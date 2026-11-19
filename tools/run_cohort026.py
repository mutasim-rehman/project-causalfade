"""Resumable two-lineage cohort 026 development runner with raw append-only output."""
import argparse
import hashlib
import json
import random
import re
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from run_direct_pilot import request

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'experiments/cohort_026'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def rows(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s]

def decode(response, kind):
    try:
        content=response['choices'][0]['message']['content'].strip()
        finish=response['choices'][0]['finish_reason']
    except (KeyError,IndexError,AttributeError):
        return None,'missing'
    allowed={'graph':('upstream','downstream'),'arithmetic':('yes','no')}.get(kind,('X=1','X=0'))
    return (content if content in allowed and finish=='stop' else None),finish

def run(model_id):
    plan=json.loads((BASE/'frozen_development_plan.json').read_text())
    if sha(BASE/'input/manifest.json')!=plan['fixture_manifest_sha256']:
        raise ValueError('Fixture manifest mismatch')
    model=next(x for x in plan['models'] if x['id']==model_id)
    if sha(model['path'])!=model['sha256'] or sha(plan['server'])!=plan['server_sha256']:
        raise ValueError('Model or server hash mismatch')
    tasks=[x for x in rows(BASE/'input/public_tasks.jsonl') if x['split']==plan['split']]
    rng=random.Random(plan['seed']);rng.shuffle(tasks)
    out=BASE/'runs'/model_id;out.mkdir(parents=True,exist_ok=True)
    schedule=out/'schedule.json'
    if schedule.exists():
        if json.loads(schedule.read_text())!=tasks:raise ValueError('Schedule mismatch')
    else:schedule.write_text(json.dumps(tasks,indent=2)+'\n')
    raw=out/'raw_responses.jsonl'
    completed={x['task_id'] for x in rows(raw)} if raw.exists() else set()
    if len(completed)==len(tasks):return
    with socket.socket() as s:
        s.bind(('127.0.0.1',0));port=s.getsockname()[1]
    cmd=[plan['server'],'-m',model['path'],'--host','127.0.0.1','--port',str(port),'-ngl','0','-c',str(plan['context']),'-np','1','-t',str(plan['threads']),'--cache-type-k','f16','--cache-type-v','f16']
    (out/'config.json').write_text(json.dumps({'model':model,'plan_sha256':sha(BASE/'frozen_development_plan.json'),'command':cmd},indent=2)+'\n')
    with (out/'stdout.log').open('a') as stdout,(out/'stderr.log').open('a') as stderr:
        server=subprocess.Popen(cmd,stdout=stdout,stderr=stderr)
        try:
            deadline=time.monotonic()+180
            while True:
                if server.poll() is not None:raise RuntimeError('Server exited during startup')
                try:request(port,'/health');break
                except OSError:
                    if time.monotonic()>deadline:raise TimeoutError('Server startup')
                    time.sleep(1)
            with raw.open('a') as stream:
                for i,task in enumerate(tasks):
                    if task['task_id'] in completed:continue
                    rec={'task_id':task['task_id'],'utc':datetime.now(timezone.utc).isoformat()}
                    try:
                        response=request(port,'/v1/chat/completions',{'model':model['path'],'messages':[{'role':'user','content':task['prompt']}], 'temperature':0,'seed':plan['seed'],'max_tokens':plan['max_tokens'],'stream':False,'cache_prompt':False},timeout=180)
                        rec['response']=response
                        rec['answer'],rec['finish_reason']=decode(response,task['kind'])
                    except Exception as exc:
                        rec['error']=repr(exc);rec['answer']=None
                    stream.write(json.dumps(rec)+'\n');stream.flush()
                    if (i+1)%14==0:print(model_id,i+1,'/',len(tasks),flush=True)
        finally:
            server.terminate()
            try:server.wait(timeout=20)
            except subprocess.TimeoutExpired:server.kill();server.wait()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('model_id');run(p.parse_args().model_id)
