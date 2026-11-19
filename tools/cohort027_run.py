"""Sequential, resumable cohort 027 runner. Importing this module never starts inference."""
import argparse
import fcntl
import hashlib
import json
import os
import random
import signal
import socket
import subprocess
import sys
import time
from datetime import datetime,timezone
from pathlib import Path
from urllib.error import URLError, HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from causalfade.cohort027 import decode
from cohort027_prepare import ROOT,BASE,sha,jsonl,atomic_json,verify
from cohort027_analyze import analyze_arm
from run_direct_pilot import request


def utc():return datetime.now(timezone.utc).isoformat()

def append(path,record):
    with Path(path).open('a') as f:
        f.write(json.dumps(record,sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())


def recover_incomplete_tail(path):
    """Preserve a torn final write, then restore the last complete JSONL boundary."""
    p=Path(path)
    if not p.exists():return
    data=p.read_bytes()
    if not data or data.endswith(b'\n'):return
    end=data.rfind(b'\n')+1
    tail=data[end:]
    archive=p.with_name(p.name+'.partial_tail.'+str(time.time_ns()))
    archive.write_bytes(tail)
    with p.open('r+b') as f:f.truncate(end);f.flush();os.fsync(f.fileno())

def event(out,kind,**data):
    append(out/'events.jsonl',{'utc':utc(),'event':kind,**data})

def checkpoint(out,model_id,split,completed,total,push=True,extra_paths=()):
    atomic_json(out/'progress.json',{'arm':model_id,'split':split,'completed':completed,'total':total,'utc':utc()})
    event(out,'checkpoint',completed=completed,total=total)
    paths=[str(out.relative_to(ROOT))]+[str(Path(p).relative_to(ROOT)) for p in extra_paths]
    if (BASE/'token_preflight.json').exists():paths.append('experiments/cohort_027/token_preflight.json')
    subprocess.run(['git','add','--',*paths],cwd=ROOT,check=True)
    staged=subprocess.run(['git','diff','--cached','--quiet','--',*paths],cwd=ROOT)
    if staged.returncode==1:
        subprocess.run(['git','commit','-m',f'Checkpoint cohort 027 {split} {model_id} {completed}/{total}','--',*paths],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    elif staged.returncode!=0:raise RuntimeError('git diff failed')
    if push:
        result=subprocess.run(['git','push'],cwd=ROOT,text=True,capture_output=True)
        if result.returncode:
            event(out,'push_failed',returncode=result.returncode,stderr=result.stderr[-1000:])
            print(f'WARNING: git push failed; local checkpoint is safe: {result.stderr[-300:]}',flush=True)


def pipeline_checkpoint(push=True):
    rel='experiments/cohort_027/pipeline_status.json'
    paths=[rel]
    if (BASE/'token_preflight.json').exists():paths.append('experiments/cohort_027/token_preflight.json')
    subprocess.run(['git','add','--',*paths],cwd=ROOT,check=True)
    if subprocess.run(['git','diff','--cached','--quiet','--',*paths],cwd=ROOT).returncode==1:
        subprocess.run(['git','commit','-m','Checkpoint cohort 027 pipeline status','--',*paths],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
    if push:
        result=subprocess.run(['git','push'],cwd=ROOT,text=True,capture_output=True)
        if result.returncode:print('WARNING: pipeline status push failed; local commit remains safe',flush=True)

def candidate(model_id):
    models=json.loads((BASE/'inventory.json').read_text())
    try:return next(m for m in models if m['id']==model_id)
    except StopIteration:raise ValueError('Unknown model ID '+model_id)

def resolve_model(model_id,precision,plan):
    m=candidate(model_id)
    if not m['available'] or not m['hash_ok'] or m.get('excluded_before_outcomes'):
        raise ValueError('F16 reference unavailable or excluded')
    if precision=='F16':
        path=Path(m['path']);expected=m['sha256']
    else:
        side=BASE/'quantized'/model_id/(precision+'.provenance.json')
        if not side.is_file():raise FileNotFoundError('Quantized provenance missing: '+str(side))
        prov=json.loads(side.read_text())
        if prov['source_sha256']!=m['sha256'] or prov['quantizer_sha256']!=plan['quantizer_sha256']:
            raise ValueError('Quantized provenance mismatch')
        path=Path(prov['output']);expected=prov['output_sha256']
    if not path.is_file() or sha(path)!=expected:
        raise ValueError('Model missing or SHA-256 mismatch: '+str(path))
    return path,expected

def ensure_allowed(split,model_id,precision):
    plan=json.loads((BASE/'plan.json').read_text())
    if model_id not in plan['model_ids']:raise ValueError('Model not predeclared')
    if split=='development' and precision=='F16':return
    if split=='validation' and precision=='F16':
        prior=BASE/'runs'/'development'/(model_id+'_F16')/'analysis.json'
        if not prior.is_file() or not json.loads(prior.read_text())['qualified']:
            raise ValueError('Reference did not qualify on development')
        return
    if split=='development' and precision in plan['precision_levels']:
        prior=BASE/'runs'/'validation'/(model_id+'_F16')/'analysis.json'
        if not prior.is_file() or not json.loads(prior.read_text())['qualified']:
            raise ValueError('Reference did not qualify on validation')
        return
    raise ValueError('Stage/format combination not allowed')

def server_start(command,out,port,retries):
    for attempt in range(1,retries+1):
        stdout=(out/'server.stdout.log').open('a');stderr=(out/'server.stderr.log').open('a')
        process=subprocess.Popen(command,stdout=stdout,stderr=stderr)
        stdout.close();stderr.close()
        deadline=time.monotonic()+180
        while time.monotonic()<deadline and process.poll() is None:
            try:
                health=request(port,'/health',timeout=2)
                event(out,'server_ready',pid=process.pid,attempt=attempt)
                return process
            except (OSError,ValueError):time.sleep(1)
        process.terminate()
        try:process.wait(timeout=15)
        except subprocess.TimeoutExpired:process.kill();process.wait()
        event(out,'server_start_failed',attempt=attempt,returncode=process.returncode)
        time.sleep(min(5*attempt,20))
    raise RuntimeError('Server failed to start after bounded retries; arm remains resumable')

def stop(process):
    if process is not None and process.poll() is None:
        process.terminate()
        try:process.wait(timeout=20)
        except subprocess.TimeoutExpired:process.kill();process.wait()

def run_arm(split,model_id,precision='F16',push=True):
    verify();ensure_allowed(split,model_id,precision)
    plan=json.loads((BASE/'plan.json').read_text())
    token_report=BASE/'token_preflight.json'
    if not token_report.exists():raise ValueError('Mandatory tokenizer preflight missing; run cohort027_tokencheck.py')
    token_data=json.loads(token_report.read_text())
    if token_data['context']!=plan['runtime']['context'] or token_data['max_tokens']!=plan['decoding']['max_tokens'] or model_id not in token_data['models'] or token_data['models'][model_id]['model_sha256']!=candidate(model_id)['sha256']:
        raise ValueError('Tokenizer preflight does not match the frozen plan/model')
    path,model_hash=resolve_model(model_id,precision,plan)
    if sha(plan['server'])!=plan['server_sha256']:raise ValueError('Server hash mismatch')
    tasks={x['task_id']:x for x in jsonl(BASE/split/'public_tasks.jsonl')}
    schedule=json.loads((BASE/split/'schedule.json').read_text())
    if len(schedule)!=len(tasks) or set(schedule)!=set(tasks):raise ValueError('Schedule mismatch')
    arm_id=model_id+'_'+precision
    out=BASE/'runs'/split/arm_id;out.mkdir(parents=True,exist_ok=True)
    lock=(out/'.lock').open('w')
    try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:raise RuntimeError('Arm is already running')
    for name in ('events.jsonl','attempts.jsonl','results.jsonl'):
        recover_incomplete_tail(out/name)
    config={'plan_sha256':sha(BASE/'plan.json'),'manifest_sha256':sha(BASE/'manifest.json'),
            'model_sha256':model_hash,'model_path':str(path),'split':split,'arm_id':arm_id,
            'decoding':plan['decoding'],'runtime':plan['runtime'],'schedule_sha256':sha(BASE/split/'schedule.json')}
    config_path=out/'config.json'
    if config_path.exists() and json.loads(config_path.read_text())!=config:raise ValueError('Resume config mismatch')
    if not config_path.exists():atomic_json(config_path,config)
    side=BASE/'quantized'/model_id/(precision+'.provenance.json')
    extra_paths=() if precision=='F16' else (side,side.with_suffix('.quantize.log'))
    completed_rows=jsonl(out/'results.jsonl') if (out/'results.jsonl').exists() else []
    completed={r['task_id'] for r in completed_rows}
    if len(completed)!=len(completed_rows) or not completed.issubset(tasks):raise ValueError('Corrupt/duplicate completed records')
    # A crash can land after a response is durably appended but before its
    # result row. Recover it instead of querying the model a second time.
    for attempt in jsonl(out/'attempts.jsonl') if (out/'attempts.jsonl').exists() else []:
        task_id=attempt['task_id']
        if task_id in completed or 'response' not in attempt:continue
        if task_id not in tasks:raise ValueError('Orphan attempt outside frozen schedule')
        response=attempt['response']
        try:
            choice=response['choices'][0];raw=choice['message']['content'];finish=choice['finish_reason']
            strict,sensitivity=decode(raw,tasks[task_id]['kind'],finish)
            record={'task_id':task_id,'utc':attempt['utc'],'raw':raw,'finish_reason':finish,
                    'strict_answer':strict,'sensitivity_answer':sensitivity,
                    'usage':response.get('usage'),'elapsed_seconds':attempt.get('elapsed_seconds'),
                    'recovered_from_attempt':True}
        except (KeyError,IndexError,TypeError) as exc:
            record={'task_id':task_id,'utc':attempt['utc'],'strict_answer':None,'sensitivity_answer':None,
                    'infrastructure_error':'unreadable archived response: '+repr(exc),'recovered_from_attempt':True}
        append(out/'results.jsonl',record);completed.add(task_id)
        event(out,'recovered_completed_response',task_id=task_id)
    if len(completed)==len(schedule):
        saved=out/'analysis.json'
        if saved.exists():return json.loads(saved.read_text())
        result=analyze_arm(split,arm_id)
        checkpoint(out,arm_id,split,len(completed),len(schedule),push,extra_paths)
        return result
    with socket.socket() as s:
        s.bind(('127.0.0.1',0));port=s.getsockname()[1]
    runtime=plan['runtime'];cmd=[plan['server'],'-m',str(path),'--host','127.0.0.1','--port',str(port),'-ngl',str(runtime['gpu_layers']),
                               '-c',str(runtime['context']),'-np',str(runtime['parallel']),'-t',str(runtime['threads']),
                               '--cache-type-k','f16','--cache-type-v','f16']
    process=None
    event(out,'arm_resumed' if completed else 'arm_started',completed=len(completed),total=len(schedule))
    try:
        process=server_start(cmd,out,port,plan['server_start_retries'])
        for task_id in schedule:
            if task_id in completed:continue
            task=tasks[task_id]
            record={'task_id':task_id,'utc':utc(),'strict_answer':None,'sensitivity_answer':None}
            for attempt_no in range(1,plan['transport_retries']+2):
                if process.poll() is not None:
                    event(out,'server_died',returncode=process.returncode,task_id=task_id)
                    process=server_start(cmd,out,port,plan['server_start_retries'])
                started=time.monotonic()
                try:
                    response=request(port,'/v1/chat/completions',{'model':str(path),'messages':[{'role':'user','content':task['prompt']}],
                              **plan['decoding']},timeout=180)
                    choice=response['choices'][0]
                    raw=choice['message']['content'];finish=choice['finish_reason']
                    strict,sensitivity=decode(raw,task['kind'],finish)
                    attempt={'task_id':task_id,'attempt':attempt_no,'utc':utc(),'response':response,
                             'elapsed_seconds':time.monotonic()-started}
                    append(out/'attempts.jsonl',attempt)
                    record.update({'raw':raw,'finish_reason':finish,'strict_answer':strict,'sensitivity_answer':sensitivity,
                                   'usage':response.get('usage'),'elapsed_seconds':attempt['elapsed_seconds']})
                    break
                except (URLError,HTTPError,TimeoutError,ConnectionError,OSError,KeyError,IndexError,TypeError,ValueError) as exc:
                    append(out/'attempts.jsonl',{'task_id':task_id,'attempt':attempt_no,'utc':utc(),
                                                  'transport_error':repr(exc),'elapsed_seconds':time.monotonic()-started})
                    if attempt_no>plan['transport_retries']:
                        record['infrastructure_error']=repr(exc)
                        event(out,'task_infrastructure_failure',task_id=task_id,error=repr(exc))
                    else:time.sleep(min(2**attempt_no,8))
            append(out/'results.jsonl',record);completed.add(task_id)
            event(out,'task_complete',task_id=task_id,completed=len(completed),total=len(schedule),
                  strict_valid=record['strict_answer'] is not None,
                  infrastructure_error=bool(record.get('infrastructure_error')))
            print(f'{arm_id} {split}: {len(completed)}/{len(schedule)} {task_id} valid={record["strict_answer"] is not None}',flush=True)
            if len(completed)%plan['checkpoint_every']==0 or len(completed)==len(schedule):
                checkpoint(out,arm_id,split,len(completed),len(schedule),push,extra_paths)
                print(f'{arm_id} {split}: {len(completed)}/{len(schedule)}',flush=True)
        result=analyze_arm(split,arm_id)
        checkpoint(out,arm_id,split,len(completed),len(schedule),push,extra_paths)
        event(out,'arm_complete',qualified=result['qualified'])
        return result
    except BaseException as exc:
        event(out,'arm_stopped',error=repr(exc),completed=len(completed))
        checkpoint(out,arm_id,split,len(completed),len(schedule),push,extra_paths)
        raise
    finally:
        stop(process);fcntl.flock(lock,fcntl.LOCK_UN);lock.close()


def orchestrate(push=True):
    verify();plan=json.loads((BASE/'plan.json').read_text())
    if not (BASE/'token_preflight.json').exists():
        from cohort027_tokencheck import run as tokencheck
        print('Running mandatory tokenizer preflight; no generation requests.',flush=True)
        tokencheck()
    atomic_json(BASE/'pipeline_status.json',{'status':'running','utc':utc()})
    pipeline_checkpoint(push)
    try:
        for model_id in plan['development_order']:
            print(f'STAGE B development {model_id} F16',flush=True)
            run_arm('development',model_id,'F16',push)
        qualified=[]
        for model_id in plan['model_ids']:
            x=json.loads((BASE/'runs'/'development'/(model_id+'_F16')/'analysis.json').read_text())
            if x['qualified']:qualified.append(model_id)
        print('Development qualified:',qualified,flush=True)
        for model_id in plan['validation_order']:
            if model_id not in qualified:continue
            print(f'STAGE B validation {model_id} F16',flush=True)
            run_arm('validation',model_id,'F16',push)
        expanded=[]
        for model_id in qualified:
            x=json.loads((BASE/'runs'/'validation'/(model_id+'_F16')/'analysis.json').read_text())
            if x['qualified']:expanded.append(model_id)
        print('Validation qualified:',expanded,flush=True)
        if not expanded:
            atomic_json(BASE/'pipeline_status.json',{'status':'stopped_by_gate','utc':utc(),'development_qualified':qualified})
            pipeline_checkpoint(push)
            print('Cohort 027 stopped: no reference passed both gates.',flush=True)
            return
        for model_id in expanded:
            for precision in plan['precision_order_by_model'][model_id]:
                from cohort027_quantize import build
                print(f'STAGE C {model_id} {precision}: preparing precision',flush=True)
                build(model_id,precision)
                run_arm('development',model_id,precision,push)
        atomic_json(BASE/'pipeline_status.json',{'status':'collection_complete','utc':utc(),'expanded':expanded})
        pipeline_checkpoint(push)
        print('Cohort 027 staged collection complete. Run descriptive analysis.',flush=True)
    except BaseException as exc:
        atomic_json(BASE/'pipeline_status.json',{'status':'interrupted','utc':utc(),'error':repr(exc)})
        pipeline_checkpoint(push)
        raise

if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    arm=sub.add_parser('run-arm');arm.add_argument('split',choices=('development','validation'));arm.add_argument('model_id');arm.add_argument('--precision',default='F16')
    sub.add_parser('run-all');p.add_argument('--no-push',action='store_true')
    a=p.parse_args()
    if a.command=='run-arm':print(json.dumps(run_arm(a.split,a.model_id,a.precision,not a.no_push),indent=2))
    else:orchestrate(not a.no_push)
