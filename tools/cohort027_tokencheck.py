"""Mandatory no-generation tokenizer preflight before cohort 027 inference."""
import json
import re
import subprocess
from pathlib import Path
from cohort027_prepare import BASE,sha,jsonl,atomic_json,verify

TOKENIZER=Path('/home/i242514/Desktop/project-causalfade/.tools/llama-b12176/llama-tokenize')

def run():
    verify()
    plan=json.loads((BASE/'plan.json').read_text())
    inventory={m['id']:m for m in json.loads((BASE/'inventory.json').read_text())}
    prompts=jsonl(BASE/'development'/'public_tasks.jsonl')+jsonl(BASE/'validation'/'public_tasks.jsonl')
    # Longest rendered item in every form/kind; all prompts share the same template.
    chosen={}
    for t in prompts:
        key=(t['form'],t['kind'])
        if key not in chosen or len(t['prompt'].encode())>len(chosen[key]['prompt'].encode()):chosen[key]=t
    result={'tokenizer_sha256':sha(TOKENIZER),'context':plan['runtime']['context'],'max_tokens':plan['decoding']['max_tokens'],
            'checked_prompt_ids':[t['task_id'] for t in chosen.values()],'models':{}}
    for model_id in plan['model_ids']:
        m=inventory[model_id]
        counts={}
        for key,t in chosen.items():
            command=[str(TOKENIZER),'-m',m['path'],'--stdin','--show-count']
            p=subprocess.run(command,input=t['prompt'],text=True,capture_output=True,timeout=180)
            if p.returncode:raise RuntimeError(f'Tokenizer failed for {model_id}: {p.stderr[-400:]}')
            matches=re.findall(r'(?:total\s+number\s+of\s+tokens|total\s+tokens|token\s+count)\s*[:=]\s*(\d+)',p.stdout+'\n'+p.stderr,re.I)
            if not matches:raise ValueError(f'Could not parse tokenizer count for {model_id}: {(p.stdout+p.stderr)[-400:]}')
            counts[t['task_id']]=int(matches[-1])
        maximum=max(counts.values())
        if maximum+plan['decoding']['max_tokens']+256>plan['runtime']['context']:
            raise ValueError(f'Context budget exceeded for {model_id}')
        result['models'][model_id]={'model_sha256':m['sha256'],'counts':counts,'max_count':maximum}
    atomic_json(BASE/'token_preflight.json',result)
    return result

if __name__=='__main__':print(json.dumps(run(),indent=2))
