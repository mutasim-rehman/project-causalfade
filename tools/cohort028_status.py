"""Read-only cohort 028 pipeline snapshot."""
import json
from pathlib import Path
from cohort028_prepare import BASE,rows

def status():
    p=BASE/'pipeline_status.json';print('pipeline:',json.loads(p.read_text()) if p.exists() else 'not started')
    print('tokenizer preflight:', 'complete' if (BASE/'token_preflight.json').exists() else 'pending')
    plan=BASE/'plan.json'
    if not plan.exists():return
    for split,total in (('development',1280),('validation',2560)):
        for id in json.loads(plan.read_text())['models']:
            out=BASE/'runs'/split/id
            if not out.exists():continue
            progress=out/'progress.json'
            n=json.loads(progress.read_text())['completed'] if progress.exists() else len(rows(out/'results.jsonl')) if (out/'results.jsonl').exists() else 0
            analysis=out/'analysis.json'
            q=json.loads(analysis.read_text())['qualified'] if analysis.exists() else None
            print(f'{split} {id}: {n}/{total}; qualified={q}')
if __name__=='__main__':status()
