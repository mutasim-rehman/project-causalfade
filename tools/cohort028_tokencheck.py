"""Required tokenizer-only preflight before cohort 028 generation."""
import json,re,subprocess
from pathlib import Path
from cohort028_prepare import BASE,ROOT,rows,sha,atomic,verify
TOKENIZER=ROOT/'.tools/llama-b12176/llama-tokenize'
def run():
    verify();plan=json.loads((BASE/'plan.json').read_text());inventory={m['id']:m for m in json.loads((BASE/'inventory.json').read_text())}
    tasks=rows(BASE/'development/public_tasks.jsonl')+rows(BASE/'validation/public_tasks.jsonl')
    chosen={}
    for t in tasks:
        key=(t['form'],t['condition'],t['representation'])
        if key not in chosen or len(t['prompt'].encode())>len(chosen[key]['prompt'].encode()):chosen[key]=t
    report={'tokenizer_sha256':sha(TOKENIZER),'context':plan['runtime']['context'],'max_tokens':plan['max_tokens'],'models':{}}
    for id in plan['models']:
        m=inventory[id];counts={}
        for t in chosen.values():
            p=subprocess.run([str(TOKENIZER),'-m',m['path'],'--stdin','--show-count'],input=t['prompt'],text=True,capture_output=True,timeout=180)
            if p.returncode:raise RuntimeError('Tokenizer failed for '+id+': '+p.stderr[-400:])
            matches=re.findall(r'(?:total\s+number\s+of\s+tokens|total\s+tokens|token\s+count)\s*[:=]\s*(\d+)',p.stdout+'\n'+p.stderr,re.I)
            if not matches:raise ValueError('Tokenizer count missing for '+id)
            count=int(matches[-1]);counts[t['task_id']]=count
            if count+plan['max_tokens'][t['condition']]+256>plan['runtime']['context']:
                raise ValueError('Context headroom failed for '+id+' '+t['task_id'])
        report['models'][id]={'model_sha256':m['sha256'],'counts':counts,'maximum':max(counts.values())}
    atomic(BASE/'token_preflight.json',report)
    return report
if __name__=='__main__':print(json.dumps(run(),indent=2))
