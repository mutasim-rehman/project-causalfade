"""Freeze cohort 028 fixtures and inventory without generation requests."""
import hashlib,json,os,random,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fractions import Fraction as F
from causalfade.cohort028 import build,validate,signature

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'experiments/cohort_028'
SOURCE_FILES=('causalfade/cohort028.py','causalfade/graph_switch.py','tools/cohort028_prepare.py','tools/cohort028_run.py','tools/cohort028_analyze.py','tools/cohort028_tokencheck.py','tools/cohort028_status.py','tools/run_direct_pilot.py')

def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def rows(path):return [json.loads(s) for s in Path(path).read_text().splitlines() if s]

def atomic(path,value):
    p=Path(path);tmp=p.with_name(p.name+'.tmp')
    with tmp.open('w') as f:
        json.dump(value,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,p)

def prior_signatures():
    seen=set()
    for base in (ROOT/'experiments/cohort_026',ROOT/'experiments/cohort_027'):
        for p in base.glob('*/worlds.jsonl'):
            for w in rows(p):
                j={(v['w'],v['x'],v['y']):F(v['p']) for v in w['joint']}
                seen.add(signature(j))
    return seen

def schedule(tasks,split):
    sub=[t for t in tasks if t['split']==split]
    by_stem={}
    for t in sub:by_stem.setdefault(t['stem_id'],{})[t['condition']]=t['task_id']
    if any(set(v)!={'bare','structured'} for v in by_stem.values()):raise ValueError('Unpaired A/B stem')
    stems=list(by_stem);random.Random(28028+(split=='validation')).shuffle(stems)
    order=[]
    for i,stem in enumerate(stems):
        conditions=('bare','structured') if i%2==0 else ('structured','bare')
        order.extend(by_stem[stem][c] for c in conditions)
    return order

def prepare():
    if any((BASE/x).exists() for x in ('development','validation','plan.json','manifest.json')):
        raise FileExistsError('Prepared fixture exists; refusing to overwrite')
    worlds,tasks,truth=build();audit=validate(worlds,tasks,truth,prior_signatures())
    prior=json.loads((ROOT/'experiments/cohort_027/inventory.json').read_text())
    chosen=[]
    for id in ('qwen7b','llama8b'):
        m=next(x for x in prior if x['id']==id)
        actual=sha(m['path'])
        if actual!=m['sha256'] or not m['hash_ok']:raise ValueError('Pinned model hash mismatch: '+id)
        chosen.append({k:m[k] for k in ('id','lineage','path','sha256','bytes','source_revision','source_repo','license','gguf_metadata')})
    atomic(BASE/'inventory.json',chosen)
    for split in ('development','validation'):
        dest=BASE/split;dest.mkdir()
        for name,arr in (('worlds.jsonl',worlds),('public_tasks.jsonl',tasks),('oracle_truth.jsonl',truth)):
            with (dest/name).open('x') as f:
                for x in arr:
                    belongs=x['split'] if 'split' in x else x['task_id'].split('_')[0]
                    if belongs==split:f.write(json.dumps(x,sort_keys=True)+'\n')
        atomic(dest/'schedule.json',schedule(tasks,split))
    ids=[m['id'] for m in chosen];random.Random(28031).shuffle(ids)
    plan={'classification':'bounded development and conditional validation, no quantization or confirmation',
          'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
          'models':ids,'server':str(ROOT/'.tools/llama-b12176/llama-server'),
          'server_sha256':'6d3d7416bf83500c5adda80ee4bb076f6877e38ff0a53ddc81c0b278108b2f24',
          'decoding':{'temperature':0,'seed':20261120,'cache_prompt':False,'stream':False},
          'max_tokens':{'bare':64,'structured':192},'runtime':{'threads':8,'context':4096,'parallel':1,'gpu_layers':0},
          'checkpoint_every':20,'transport_retries':2,'server_start_retries':3,
          'source_hashes':{name:sha(ROOT/name) for name in SOURCE_FILES}}
    atomic(BASE/'plan.json',plan)
    from cohort028_analyze import analyze,shortcut_audit
    oracle_records=[]
    truth_map={v['task_id']:v for v in truth}
    for t in tasks:
        x=truth_map[t['task_id']]
        raw=x['expected_action'] if t['condition']=='bare' else json.dumps({'rule':x['expected_rule'],'score_x0':float(x['score_x0']),
              'score_x1':float(x['score_x1']),'action':x['expected_action']})
        oracle_records.append({'task_id':t['task_id'],'raw':raw,'finish_reason':'stop'})
    controls={}
    for split in ('development','validation'):
        ts=[t for t in tasks if t['split']==split];ys=[y for y in truth if y['task_id'].startswith(split+'_')];rs=[r for r in oracle_records if r['task_id'].startswith(split+'_')]
        result=analyze(ts,ys,rs,split)
        if not result['qualified']:raise ValueError('Oracle responder failed gates')
        controls[split]={'oracle_qualified':True,'primary_gain_pp':result['primary_gain_pp']['mean'],
                         'shortcut_audit':shortcut_audit(ts,ys,split)}
    atomic(BASE/'preflight.json',{'audit':audit,'oracle_controls':controls,'max_prompt_bytes':max(len(t['prompt'].encode()) for t in tasks)})
    files=[BASE/n for n in ('plan.json','inventory.json','preflight.json')]
    for split in ('development','validation'):
        files += [BASE/split/n for n in ('worlds.jsonl','public_tasks.jsonl','oracle_truth.jsonl','schedule.json')]
    atomic(BASE/'manifest.json',{'files':{str(p.relative_to(BASE)):sha(p) for p in files},'source_hashes':plan['source_hashes']})
    return audit

def verify():
    manifest=json.loads((BASE/'manifest.json').read_text())
    for name,want in manifest['files'].items():
        if sha(BASE/name)!=want:raise ValueError('File hash mismatch '+name)
    for name,want in manifest['source_hashes'].items():
        if sha(ROOT/name)!=want:raise ValueError('Source hash mismatch '+name)
    worlds=[];tasks=[];truth=[]
    for split in ('development','validation'):
        worlds+=rows(BASE/split/'worlds.jsonl');tasks+=rows(BASE/split/'public_tasks.jsonl');truth+=rows(BASE/split/'oracle_truth.jsonl')
    audit=validate(worlds,tasks,truth,prior_signatures())
    if audit!=json.loads((BASE/'preflight.json').read_text())['audit']:raise ValueError('Audit mismatch')
    for split in ('development','validation'):
        actual=json.loads((BASE/split/'schedule.json').read_text())
        if actual!=schedule(tasks,split):raise ValueError('Schedule mismatch')
    return audit

if __name__=='__main__':
    command=sys.argv[1] if len(sys.argv)>1 else None
    if command not in ('prepare','verify'):raise SystemExit('usage: cohort028_prepare.py prepare|verify')
    print(json.dumps(prepare() if command=='prepare' else verify(),indent=2))
