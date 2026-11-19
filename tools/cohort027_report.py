"""Compile completed cohort 027 gate results and descriptive paired precision effects."""
import json
from pathlib import Path
from cohort027_prepare import BASE,atomic_json,verify


def report():
    verify();plan=json.loads((BASE/'plan.json').read_text())
    output={'classification':'development and validation gates; descriptive precision only','models':{},'precision':{}}
    for model_id in plan['model_ids']:
        model={}
        for split in ('development','validation'):
            p=BASE/'runs'/split/(model_id+'_F16')/'analysis.json'
            if p.exists():model[split]=json.loads(p.read_text())
        output['models'][model_id]=model
        if not model.get('validation',{}).get('qualified'):continue
        ref=model['development']
        formats={}
        for precision in plan['precision_levels']:
            p=BASE/'runs'/'development'/(model_id+'_'+precision)/'analysis.json'
            if not p.exists():continue
            other=json.loads(p.read_text())
            families=[]
            for fid in ref['forms']['direct']['family_paired']:
                base=sum(ref['forms'][form]['family_paired'][fid] for form in ('direct','decision'))/2
                quant=sum(other['forms'][form]['family_paired'][fid] for form in ('direct','decision'))/2
                families.append({'family_id':fid,'f16':base,'quantized':quant,'difference':quant-base})
            formats[precision]={'paired_family_differences':families,
                                'mean_difference':sum(x['difference'] for x in families)/len(families),
                                'exploratory':True}
        output['precision'][model_id]=formats
    atomic_json(BASE/'descriptive_report.json',output)
    return output

if __name__=='__main__':
    print(json.dumps(report(),indent=2))
