"""Read-only progress snapshot for a prepared or running cohort 027."""
import json
from pathlib import Path
from cohort027_prepare import BASE,jsonl


def status():
    pipeline=BASE/'pipeline_status.json'
    print('pipeline:',json.loads(pipeline.read_text()) if pipeline.exists() else 'not started')
    print('tokenizer preflight:', 'complete' if (BASE/'token_preflight.json').exists() else 'pending')
    plan=BASE/'plan.json'
    if not plan.exists():return
    models=json.loads(plan.read_text())['model_ids']
    for split,total in (('development',224),('validation',448)):
        for model in models:
            arm=BASE/'runs'/split/(model+'_F16')
            if not arm.exists():continue
            progress=arm/'progress.json'
            saved=json.loads(progress.read_text())['completed'] if progress.exists() else len(jsonl(arm/'results.jsonl')) if (arm/'results.jsonl').exists() else 0
            analysis=arm/'analysis.json'
            qualified=json.loads(analysis.read_text())['qualified'] if analysis.exists() else None
            print(f'{split} {model} F16: {saved}/{total}; qualified={qualified}')
    for arm in sorted((BASE/'runs'/'development').glob('*_*')) if (BASE/'runs'/'development').exists() else []:
        if arm.name.endswith('_F16') or not arm.is_dir():continue
        progress=arm/'progress.json'
        saved=json.loads(progress.read_text())['completed'] if progress.exists() else len(jsonl(arm/'results.jsonl')) if (arm/'results.jsonl').exists() else 0
        print(f'development {arm.name}: {saved}/224')

if __name__=='__main__':status()
