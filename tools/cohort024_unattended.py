"""One-command cohort 024 preparation, freeze, full run and live monitoring."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from cohort024 import check_plan,load,model_inventory
from causalfade.sensitivity import digest,write_json

REV_META='0e9e39f249a16976918f6564b8830bc894c89659'
SOURCES=(
 ('mistral7b','second-state/Mistral-7B-Instruct-v0.3-GGUF','1b61eaebc05628c996532ffb676c6f209824216a','Mistral-7B-Instruct-v0.3-f16.gguf',14497337344,'afd9070b42b8788becde8959d2924489cc1226e3104272f93ae8403e98e9be30','apache-2.0'),
 ('llama8b','second-state/Meta-Llama-3.1-8B-Instruct-GGUF','6d6118a261564da05fd7e651f4bc069eb7c38c20','Llama-3.1-8B-Instruct-f16.gguf',16068896128,'031c5d9ae1ad8cf676f8498ef539418c0d1f2b1b9c9d33c8f9207b83218c89b3','llama3.1'))
DATA=ROOT/'experiments/cohort_024'
WEIGHTS=Path.home()/'Desktop/CAUSALFADE/weights'


def token():
    value=os.environ.get('HF_TOKEN','').strip()
    if value:return value
    for line in (ROOT/'.env').read_text().splitlines():
        if '=' in line and line.split('=',1)[0].strip()=='HF_TOKEN':
            return line.split('=',1)[1].strip().strip('"').strip("'")
    raise ValueError('HF_TOKEN missing from environment or ignored .env')


def meta_access(secret):
    url=f'https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct/resolve/{REV_META}/config.json'
    req=urllib.request.Request(url,headers={'Authorization':'Bearer '+secret})
    with urllib.request.urlopen(req,timeout=30) as response:
        if response.status!=200:raise ValueError('Authorized Meta Llama access failed')
        response.read()
    print('AUTHORIZED Meta Llama 3.1 Instruct file access verified',flush=True)


def download(repo,rev,name,size,expected_sha,destination):
    destination.parent.mkdir(parents=True,exist_ok=True)
    partial=destination.with_suffix(destination.suffix+'.part')
    if destination.exists():
        if destination.stat().st_size!=size:raise ValueError('Existing F16 has unexpected size: '+str(destination))
        if digest(destination)!=expected_sha:raise ValueError('Existing F16 hash mismatch: '+str(destination))
        return destination
    offset=partial.stat().st_size if partial.exists() else 0
    if offset>size:raise ValueError('Oversized partial F16: '+str(partial))
    url=f'https://huggingface.co/{repo}/resolve/{rev}/{name}'
    headers={'Range':f'bytes={offset}-'} if offset else {}
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=180) as response:
        if offset and response.status!=206:raise ValueError('Server refused safe resume for '+name)
        with partial.open('ab') as out:
            while True:
                chunk=response.read(8*1024*1024)
                if not chunk:break
                out.write(chunk)
                if out.tell()%(512*1024*1024)<len(chunk):print('DOWNLOAD',name,out.tell(),size,flush=True)
            out.flush();os.fsync(out.fileno())
    if partial.stat().st_size!=size:raise ValueError('Incomplete F16 retained: '+str(partial))
    if digest(partial)!=expected_sha:raise ValueError('Downloaded F16 hash mismatch; partial retained: '+str(partial))
    partial.rename(destination)
    print('SOURCE',name,size,digest(destination),flush=True)
    return destination


def command(argv):
    print('COMMAND',' '.join(argv),flush=True)
    subprocess.run(argv,cwd=ROOT,check=True)


def freeze_checkpoint(plan):
    command(['git','add','--',str(plan)])
    staged=subprocess.run(['git','diff','--cached','--name-only'],cwd=ROOT,text=True,capture_output=True,check=True).stdout.splitlines()
    if staged!=['experiments/cohort_024/frozen_lab_plan.json']:
        raise ValueError('Unrelated staged content blocks plan checkpoint: '+repr(staged))
    command(['git','commit','-m','protocol: freeze cohort 024 lab model matrix'])
    command(['git','push','origin','main'])


def start(args):
    secret=token();meta_access(secret)
    qwen=WEIGHTS/'gguf/qwen2.5-7b-instruct-f16.gguf'
    qhash='389d79c70a7c78b7b5190a3d6c3cd1146aa8b1350ab3a3e981804b8a2600de9a'
    if digest(qwen)!=qhash:raise ValueError('Archived Qwen F16 hash mismatch')
    sources=[{'lineage':'qwen7b','path':str(qwen),'source_repo':'Qwen/Qwen2.5-7B-Instruct',
              'source_revision':'a09a35458c702b33eeacc393d103063234e8bc28','license':'apache-2.0',
              'conversion':'existing F16 GGUF; CAUSALFADE agere_source/phase2 manifest; llama.cpp 7fe450e19305b828c199d602c23a8337aaa1f03b',
              'sha256':qhash}]
    for lineage,repo,rev,name,size,expected_sha,license_name in SOURCES:
        if lineage=='llama8b':meta_access(secret)
        path=download(repo,rev,name,size,expected_sha,WEIGHTS/'cohort_024_sources'/lineage/name)
        sources.append({'lineage':lineage,'path':str(path),'source_repo':repo,'source_revision':rev,
                        'license':license_name,'conversion':('published F16 GGUF; original '+('meta-llama/Llama-3.1-8B-Instruct@'+REV_META if lineage=='llama8b' else 'mistralai/Mistral-7B-Instruct-v0.3')+'; publisher conversion command not independently verified'),
                        'sha256':digest(path)})
    source_path=DATA/'sources.local.json';write_json(source_path,sources)
    models=DATA/'models.local.json';plan=DATA/'frozen_lab_plan.json'
    if not models.exists():
        command([sys.executable,'tools/cohort024.py','build-models','--sources',str(source_path),
                 '--quantizer',str(ROOT/'.tools/llama-b12176/llama-quantize'),'--out',str(WEIGHTS/'cohort_024_quantized'),
                 '--models-out',str(models)])
    inventory=model_inventory(models)
    if len(inventory)!=21:raise ValueError('Incomplete model inventory')
    if not plan.exists():
        command([sys.executable,'tools/cohort024.py','freeze','--dataset',str(DATA/'input'),
                 '--models',str(models),'--server',str(ROOT/'.tools/llama-b12176/llama-server'),
                 '--plan',str(plan),'--threads','8'])
        freeze_checkpoint(plan)
    else:check_plan(load(plan))
    runs=DATA/'runs';runs.mkdir(exist_ok=True)
    log=DATA/'live.log'
    while True:
        with log.open('a',encoding='utf-8') as stream:
            proc=subprocess.Popen([sys.executable,'-u','tools/cohort024.py','run-all','--plan',str(plan),
                                   '--out',str(runs),'--max-seconds','7200','--progress-every','20','--checkpoint-after-arm'],
                                  cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
            for line in proc.stdout:
                print(line,end='',flush=True);stream.write(line);stream.flush()
            rc=proc.wait()
        if rc==0:print('COMPLETE all 21 arms',flush=True);return
        if rc!=2:raise RuntimeError('run-all failed; inspect live.log and statuses')
        statuses=[(m['id'],load(runs/m['id']/'status.json')['status']) for m in inventory if (runs/m['id']/'status.json').exists()]
        if not statuses or statuses[-1][1]!='paused_budget':
            raise RuntimeError('Arm failed or interrupted; inspect and resume manually')
        print('RESUME after clean budget pause',statuses[-1],flush=True)


def progress(args):
    plan=DATA/'frozen_lab_plan.json';runs=DATA/'runs'
    while True:
        if plan.exists():
            models=load(plan)['models'];total=len(models)*1472;completed=0;states=[]
            for m in models:
                p=runs/m['id']/'status.json';s=load(p) if p.exists() else {'status':'pending','completed':0}
                completed+=s['completed'];states.append((m['id'],s['status'],s['completed']))
            active=[x for x in states if x[1] not in ('success','pending')]
            print(f'OVERALL {completed}/{total} ({completed/total:.1%}); successful arms {sum(x[1]=="success" for x in states)}/{len(states)}; active {active[-1] if active else "none"}',flush=True)
        else:print('PREPARING sources, quantizations or frozen plan; see start terminal',flush=True)
        if args.once:break
        time.sleep(args.interval)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('start');p=sub.add_parser('progress');p.add_argument('--interval',type=int,default=20);p.add_argument('--once',action='store_true')
    a=parser.parse_args()
    if a.command=='start':start(a)
    else:progress(a)
