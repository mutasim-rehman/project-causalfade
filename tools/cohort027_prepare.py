"""Prepare and verify cohort 027 without model inference."""
import argparse
import hashlib
import json
import os
import random
import struct
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from causalfade.cohort027 import build, validate, joint_signature

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'experiments/cohort_027'
SOURCES=('causalfade/cohort027.py','causalfade/graph_switch.py','tools/cohort027_prepare.py','tools/cohort027_run.py','tools/cohort027_analyze.py','tools/cohort027_quantize.py','tools/cohort027_report.py','tools/cohort027_tokencheck.py','tools/cohort027_status.py','tools/run_direct_pilot.py')


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda:f.read(4*1024*1024),b''):
            h.update(part)
    return h.hexdigest()


def jsonl(path):
    return [json.loads(s) for s in Path(path).read_text().splitlines() if s]


def atomic_json(path,value):
    p=Path(path);temp=p.with_name(p.name+'.tmp')
    with temp.open('w') as f:
        json.dump(value,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temp,p)


def prior_signatures():
    signatures=set()
    for name in ('input','input_v2'):
        p=ROOT/'experiments/cohort_026'/name/'worlds.jsonl'
        if p.exists():
            for w in jsonl(p):
                j={(r['w'],r['x'],r['y']):__import__('fractions').Fraction(r['p']) for r in w['joint']}
                signatures.add(joint_signature(j))
    return signatures


def gguf_metadata(path):
    """Read header metadata only; never scan tensor payload."""
    with Path(path).open('rb') as f:
        def u32():return struct.unpack('<I',f.read(4))[0]
        def u64():return struct.unpack('<Q',f.read(8))[0]
        def string():
            n=u64()
            if n>10_000_000:raise ValueError('Unreasonable GGUF string')
            return f.read(n).decode()
        sizes={0:1,1:1,2:2,3:2,4:4,5:4,6:4,7:1,10:8,11:8,12:8}
        def value(t):
            if t==8:return string()
            if t==9:
                typ=u32();count=u64()
                if count>100_000_000:raise ValueError('Unreasonable GGUF array')
                if typ in sizes:f.seek(count*sizes[typ],1);return None
                return [value(typ) for _ in range(count)]
            if t not in sizes:raise ValueError('Unsupported GGUF type')
            raw=f.read(sizes[t])
            return int.from_bytes(raw,'little') if t in (0,1,2,3,4,5,7,10,11,12) else raw
        if f.read(4)!=b'GGUF' or u32() not in (2,3):raise ValueError('Invalid GGUF header')
        u64();nkv=u64()
        if nkv>100_000:raise ValueError('Unreasonable GGUF metadata count')
        selected={}
        for _ in range(nkv):
            key=string();v=value(u32())
            if key in ('general.file_type','tokenizer.chat_template'):
                selected[key]=v
        return {'file_type':selected.get('general.file_type'),
                'chat_template_sha256':hashlib.sha256(selected['tokenizer.chat_template'].encode()).hexdigest() if isinstance(selected.get('tokenizer.chat_template'),str) else None,
                'chat_template_length':len(selected['tokenizer.chat_template']) if isinstance(selected.get('tokenizer.chat_template'),str) else None}


def prepare():
    if any((BASE/s).exists() for s in ('development','validation','manifest.json','plan.json')):
        raise FileExistsError('Prepared files exist; refuse to overwrite frozen fixture')
    worlds,tasks,truth=build()
    audit=validate(worlds,tasks,truth,prior_signatures())
    candidates=json.loads((BASE/'model_candidates.json').read_text())
    inventory=[]
    for m in candidates:
        p=Path(m['path'])
        actual=sha(p) if p.is_file() else None
        metadata=gguf_metadata(p) if p.is_file() else None
        inventory.append({**m,'available':p.is_file(),'bytes':p.stat().st_size if p.is_file() else None,
                          'actual_sha256':actual,'hash_ok':actual==m['sha256'] and metadata['file_type']==1 if metadata else False,
                          'gguf_metadata':metadata})
    for split in ('development','validation'):
        target=BASE/split;target.mkdir()
        for name,arr in (('worlds.jsonl',worlds),('public_tasks.jsonl',tasks),('oracle_truth.jsonl',truth)):
            with (target/name).open('x') as f:
                for row in arr:
                    if row['split']==split if 'split' in row else row['task_id'].startswith(split+'_'):
                        f.write(json.dumps(row,sort_keys=True)+'\n')
        ordered=[t['task_id'] for t in tasks if t['split']==split]
        random.Random(20261119+(0 if split=='development' else 1)).shuffle(ordered)
        atomic_json(target/'schedule.json',ordered)
    atomic_json(BASE/'inventory.json',inventory)
    plan={'classification':'frozen staged development and descriptive precision; no confirmation',
          'source_commit':__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'model_ids':[m['id'] for m in inventory if m['hash_ok'] and not m.get('excluded_before_outcomes')],
          'server':'/home/i242514/Desktop/project-causalfade/.tools/llama-b12176/llama-server',
          'server_sha256':'6d3d7416bf83500c5adda80ee4bb076f6877e38ff0a53ddc81c0b278108b2f24',
          'quantizer':'/home/i242514/Desktop/project-causalfade/.tools/llama-b12176/llama-quantize',
          'quantizer_sha256':'ea836b715dd96e67099d2b7052e9d20be7f8f315a510fa94e12599ecb0f9fbc9',
          'precision_levels':['Q8_0','Q6_K','Q5_K_M','Q4_K_M','Q3_K_M','Q2_K'],
          'decoding':{'temperature':0,'seed':20261119,'max_tokens':64,'cache_prompt':False,'stream':False},
          'runtime':{'threads':8,'context':4096,'parallel':1,'gpu_layers':0,'execution_mode':'sequential'},
          'checkpoint_every':14,'transport_retries':2,'server_start_retries':3,
          'development_families':8,'validation_families':16,'prompts_per_family':28,
          'source_hashes':{s:sha(ROOT/s) for s in SOURCES}}
    plan['development_order']=plan['model_ids'][:]
    random.Random(27027).shuffle(plan['development_order'])
    plan['validation_order']=plan['model_ids'][:]
    random.Random(27028).shuffle(plan['validation_order'])
    plan['precision_order_by_model']={m:random.Random(27029+i).sample(plan['precision_levels'],len(plan['precision_levels']))
                                      for i,m in enumerate(plan['model_ids'])}
    atomic_json(BASE/'plan.json',plan)
    from cohort027_analyze import shortcut_audit
    atomic_json(BASE/'preflight.json',{'fixture_audit':audit,'shortcut_audit':shortcut_audit()})
    files=[BASE/'plan.json',BASE/'inventory.json',BASE/'model_candidates.json',BASE/'preflight.json']
    for split in ('development','validation'):
        files.extend((BASE/split/n for n in ('worlds.jsonl','public_tasks.jsonl','oracle_truth.jsonl','schedule.json')))
    manifest={'files':{str(p.relative_to(BASE)):sha(p) for p in files},'audit':audit,
              'source_hashes':plan['source_hashes']}
    atomic_json(BASE/'manifest.json',manifest)
    return manifest


def verify():
    manifest=json.loads((BASE/'manifest.json').read_text())
    for name,expected in manifest['files'].items():
        if sha(BASE/name)!=expected:raise ValueError('File hash mismatch: '+name)
    for name,expected in manifest['source_hashes'].items():
        if sha(ROOT/name)!=expected:raise ValueError('Source hash mismatch: '+name)
    worlds=[];tasks=[];truth=[]
    for split in ('development','validation'):
        worlds+=jsonl(BASE/split/'worlds.jsonl');tasks+=jsonl(BASE/split/'public_tasks.jsonl');truth+=jsonl(BASE/split/'oracle_truth.jsonl')
    audit=validate(worlds,tasks,truth,prior_signatures())
    if audit!=manifest['audit']:raise ValueError('Audit mismatch')
    return {'ok':True,'audit':audit}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=('prepare','verify'));a=p.parse_args()
    print(json.dumps(prepare() if a.command=='prepare' else verify(),indent=2))
