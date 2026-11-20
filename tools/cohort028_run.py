"""Sequential, resumable cohort 028 runner; import does not request model output."""
import fcntl,json,os,socket,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
from urllib.error import URLError,HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from causalfade.cohort028 import parse_structured,calculate
from cohort028_prepare import ROOT,BASE,sha,rows,atomic,verify
from cohort028_analyze import analyze
from run_direct_pilot import request

def utc():return datetime.now(timezone.utc).isoformat()
def append(path,obj):
    with Path(path).open('a') as f:f.write(json.dumps(obj,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
def recover_tail(path):
    p=Path(path)
    if not p.exists():return
    b=p.read_bytes()
    if not b or b.endswith(b'\n'):return
    end=b.rfind(b'\n')+1
    p.with_name(p.name+'.partial_tail.'+str(time.time_ns())).write_bytes(b[end:])
    with p.open('r+b') as f:f.truncate(end);f.flush();os.fsync(f.fileno())
def event(out,name,**data):append(out/'events.jsonl',{'utc':utc(),'event':name,**data})
def commit_paths(paths,message,push=True):
    rel=[str(Path(p).relative_to(ROOT)) for p in paths]
    subprocess.run(['git','add','--',*rel],cwd=ROOT,check=True)
    code=subprocess.run(['git','diff','--cached','--quiet','--',*rel],cwd=ROOT).returncode
    if code==1:subprocess.run(['git','commit','-m',message,'--',*rel],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    elif code:raise RuntimeError('Git diff failed')
    if push:
        r=subprocess.run(['git','push'],cwd=ROOT,text=True,capture_output=True)
        if r.returncode:print('WARNING: push failed; local checkpoint commit remains safe: '+r.stderr[-300:],flush=True)
def checkpoint(out,arm,split,done,total,push):
    atomic(out/'progress.json',{'arm':arm,'split':split,'completed':done,'total':total,'utc':utc()})
    event(out,'checkpoint',completed=done,total=total)
    files=[out]
    if (BASE/'token_preflight.json').exists():files.append(BASE/'token_preflight.json')
    commit_paths(files,f'Checkpoint cohort 028 {split} {arm} {done}/{total}',push)
def server_start(cmd,out,port,tries):
    for attempt in range(1,tries+1):
        with (out/'server.stdout.log').open('a') as stdout,(out/'server.stderr.log').open('a') as stderr:
            proc=subprocess.Popen(cmd,stdout=stdout,stderr=stderr)
        deadline=time.monotonic()+180
        while time.monotonic()<deadline and proc.poll() is None:
            try:request(port,'/health',timeout=2);event(out,'server_ready',attempt=attempt,pid=proc.pid);return proc
            except (OSError,ValueError):time.sleep(1)
        proc.terminate()
        try:proc.wait(timeout=15)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()
        event(out,'server_start_failed',attempt=attempt,returncode=proc.returncode)
        time.sleep(min(5*attempt,20))
    raise RuntimeError('Server failed bounded startup attempts; arm can resume')
def stop(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try:proc.wait(timeout=20)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()
def derive(task,response):
    choice=response['choices'][0];raw=choice['message']['content'];finish=choice['finish_reason']
    record={'raw':raw,'finish_reason':finish,'usage':response.get('usage')}
    if task['condition']=='structured':
        parsed=parse_structured(raw,finish)
        if parsed is not None:
            selected=calculate(task['payload'],parsed['rule'])
            record['selected_rule']=parsed['rule']
            record['calculator_input']={'payload':task['payload'],'rule':parsed['rule']}
            record['calculator_output']={k:str(v) for k,v in selected.items()}
    return record
def analyze_arm(split,model):
    verify();out=BASE/'runs'/split/model
    result=analyze(rows(BASE/split/'public_tasks.jsonl'),rows(BASE/split/'oracle_truth.jsonl'),rows(out/'results.jsonl'),split)
    atomic(out/'analysis.json',result)
    return result
def run_arm(split,model,push=True):
    verify();plan=json.loads((BASE/'plan.json').read_text())
    if model not in plan['models']:raise ValueError('Model not pinned')
    if split=='validation':
        p=BASE/'runs'/'development'/model/'analysis.json'
        if not p.exists() or not json.loads(p.read_text())['qualified']:raise ValueError('Development gate not passed')
    token=BASE/'token_preflight.json'
    if not token.exists():raise ValueError('Tokenizer preflight missing')
    token_info=json.loads(token.read_text())
    if model not in token_info['models'] or token_info['context']!=plan['runtime']['context']:
        raise ValueError('Token preflight mismatch')
    inventory={m['id']:m for m in json.loads((BASE/'inventory.json').read_text())};m=inventory[model]
    if token_info['models'][model]['model_sha256']!=m['sha256'] or sha(m['path'])!=m['sha256'] or sha(plan['server'])!=plan['server_sha256']:
        raise ValueError('Model/server hash mismatch')
    tasks={t['task_id']:t for t in rows(BASE/split/'public_tasks.jsonl')}
    schedule=json.loads((BASE/split/'schedule.json').read_text())
    if len(schedule)!=len(tasks) or set(schedule)!=set(tasks):raise ValueError('Schedule mismatch')
    out=BASE/'runs'/split/model;out.mkdir(parents=True,exist_ok=True)
    lock=(out/'.lock').open('w')
    try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:raise RuntimeError('Arm already running')
    for name in ('attempts.jsonl','results.jsonl','events.jsonl'):recover_tail(out/name)
    config={'model':model,'model_sha256':m['sha256'],'manifest_sha256':sha(BASE/'manifest.json'),'plan_sha256':sha(BASE/'plan.json'),
            'schedule_sha256':sha(BASE/split/'schedule.json'),'runtime':plan['runtime'],'decoding':plan['decoding'],'max_tokens':plan['max_tokens']}
    cp=out/'config.json'
    if cp.exists() and json.loads(cp.read_text())!=config:raise ValueError('Resume config mismatch')
    if not cp.exists():atomic(cp,config)
    saved=rows(out/'results.jsonl') if (out/'results.jsonl').exists() else []
    done={r['task_id'] for r in saved}
    if len(done)!=len(saved) or not done.issubset(tasks):raise ValueError('Duplicate/corrupt result records')
    for attempt in rows(out/'attempts.jsonl') if (out/'attempts.jsonl').exists() else []:
        tid=attempt['task_id']
        if tid in done or 'response' not in attempt:continue
        if tid not in tasks:raise ValueError('Orphan attempt outside schedule')
        try:derived=derive(tasks[tid],attempt['response'])
        except (KeyError,IndexError,TypeError,ValueError) as exc:derived={'scoring_error':'Unreadable archived response: '+repr(exc)}
        append(out/'results.jsonl',{'task_id':tid,'utc':attempt['utc'],'recovered_from_attempt':True,**derived});done.add(tid)
        event(out,'recovered_completed_response',task_id=tid)
    if len(done)==len(schedule):
        if (out/'analysis.json').exists():return json.loads((out/'analysis.json').read_text())
        result=analyze_arm(split,model);checkpoint(out,model,split,len(done),len(schedule),push);return result
    with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
    run=plan['runtime'];cmd=[plan['server'],'-m',m['path'],'--host','127.0.0.1','--port',str(port),'-ngl',str(run['gpu_layers']),
                             '-c',str(run['context']),'-np',str(run['parallel']),'-t',str(run['threads']),
                             '--cache-type-k','f16','--cache-type-v','f16']
    proc=None;event(out,'arm_started' if not done else 'arm_resumed',completed=len(done),total=len(schedule))
    try:
        proc=server_start(cmd,out,port,plan['server_start_retries'])
        for tid in schedule:
            if tid in done:continue
            task=tasks[tid];record={'task_id':tid,'utc':utc()}
            for attempt_no in range(1,plan['transport_retries']+2):
                if proc.poll() is not None:
                    event(out,'server_died',task_id=tid,returncode=proc.returncode)
                    proc=server_start(cmd,out,port,plan['server_start_retries'])
                started=time.monotonic()
                try:
                    body={'model':m['path'],'messages':[{'role':'user','content':task['prompt']}],**plan['decoding'],
                          'max_tokens':plan['max_tokens'][task['condition']]}
                    response=request(port,'/v1/chat/completions',body,timeout=180)
                    append(out/'attempts.jsonl',{'task_id':tid,'attempt':attempt_no,'utc':utc(),'response':response,
                                                 'elapsed_seconds':time.monotonic()-started})
                except (URLError,HTTPError,TimeoutError,ConnectionError,OSError,KeyError,IndexError,TypeError,ValueError) as exc:
                    append(out/'attempts.jsonl',{'task_id':tid,'attempt':attempt_no,'utc':utc(),'error':repr(exc),
                                                 'elapsed_seconds':time.monotonic()-started})
                    if attempt_no>plan['transport_retries']:
                        record['infrastructure_error']=repr(exc);event(out,'task_infrastructure_failure',task_id=tid,error=repr(exc))
                    else:time.sleep(min(2**attempt_no,8))
                    continue
                # A completed response is never requested again, even if its
                # schema or local calculator replay is unusable.
                try:record.update(derive(task,response))
                except (KeyError,IndexError,TypeError,ValueError) as exc:record['scoring_error']=repr(exc)
                record['elapsed_seconds']=time.monotonic()-started
                break
            append(out/'results.jsonl',record);done.add(tid)
            event(out,'task_complete',task_id=tid,completed=len(done),total=len(schedule),condition=task['condition'],
                  infrastructure_error=bool(record.get('infrastructure_error')))
            print(f'{model} {split} {len(done)}/{len(schedule)} {tid}',flush=True)
            if len(done)%plan['checkpoint_every']==0 or len(done)==len(schedule):checkpoint(out,model,split,len(done),len(schedule),push)
        result=analyze_arm(split,model);event(out,'arm_complete',qualified=result['qualified'])
        checkpoint(out,model,split,len(done),len(schedule),push)
        return result
    except BaseException as exc:
        event(out,'arm_stopped',completed=len(done),error=repr(exc));checkpoint(out,model,split,len(done),len(schedule),push);raise
    finally:stop(proc);fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
def pipeline_checkpoint(push=True):
    files=[BASE/'pipeline_status.json']
    if (BASE/'token_preflight.json').exists():files.append(BASE/'token_preflight.json')
    commit_paths(files,'Checkpoint cohort 028 pipeline status',push)
def run_all(push=True):
    verify();plan=json.loads((BASE/'plan.json').read_text())
    if not (BASE/'token_preflight.json').exists():
        from cohort028_tokencheck import run
        print('Tokenizer preflight: no generation requests',flush=True);run()
    atomic(BASE/'pipeline_status.json',{'status':'running','utc':utc()});pipeline_checkpoint(push)
    try:
        for model in plan['models']:
            print('DEVELOPMENT '+model,flush=True);run_arm('development',model,push)
        qualified=[model for model in plan['models'] if json.loads((BASE/'runs'/'development'/model/'analysis.json').read_text())['qualified']]
        print('Development qualified:',qualified,flush=True)
        for model in qualified:
            print('VALIDATION '+model,flush=True);run_arm('validation',model,push)
        status='validation_complete' if qualified else 'stopped_by_gate'
        atomic(BASE/'pipeline_status.json',{'status':status,'utc':utc(),'development_qualified':qualified});pipeline_checkpoint(push)
        print('Cohort 028 '+status,flush=True)
    except BaseException as exc:
        atomic(BASE/'pipeline_status.json',{'status':'interrupted','utc':utc(),'error':repr(exc)});pipeline_checkpoint(push);raise
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('run-arm');a.add_argument('split',choices=('development','validation'));a.add_argument('model_id')
    sub.add_parser('run-all');p.add_argument('--no-push',action='store_true')
    args=p.parse_args()
    if args.command=='run-arm':print(json.dumps(run_arm(args.split,args.model_id,not args.no_push),indent=2))
    else:run_all(not args.no_push)
