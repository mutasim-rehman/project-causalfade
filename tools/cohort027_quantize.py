"""Provision a qualified cohort 027 precision arm from its pinned F16 source."""
import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path
from cohort027_prepare import BASE,sha,atomic_json,verify,gguf_metadata
from cohort027_run import candidate

DEST=Path('/home/i242514/Desktop/CAUSALFADE/weights/cohort_027_quantized')


def build(model_id,precision):
    verify();plan=json.loads((BASE/'plan.json').read_text())
    if precision not in plan['precision_levels']:raise ValueError('Undeclared precision')
    m=candidate(model_id)
    if m.get('excluded_before_outcomes') or not m['hash_ok']:raise ValueError('F16 source unavailable')
    quant=Path(plan['quantizer'])
    if sha(quant)!=plan['quantizer_sha256'] or sha(m['path'])!=m['sha256']:
        raise ValueError('Quantizer/source hash mismatch')
    target=DEST/model_id;target.mkdir(parents=True,exist_ok=True)
    output=target/(precision+'.gguf')
    side=BASE/'quantized'/model_id/(precision+'.provenance.json')
    side.parent.mkdir(parents=True,exist_ok=True)
    if side.exists():
        info=json.loads(side.read_text())
        if info['source_sha256']!=m['sha256'] or info['quantizer_sha256']!=plan['quantizer_sha256'] or sha(info['output'])!=info['output_sha256']:
            raise ValueError('Existing quantized provenance invalid')
        return info
    legacy_prefix={'qwen7b':'qwen7b','mistral7b':'mistral7b','llama8b':'llama8b'}.get(model_id)
    if legacy_prefix:
        legacy=Path('/home/i242514/Desktop/CAUSALFADE/weights/cohort_024_quantized')/(legacy_prefix+'_'+precision+'.gguf')
        legacy_side=legacy.with_suffix('.provenance.json')
        if legacy.is_file() and legacy_side.is_file():
            previous=json.loads(legacy_side.read_text())
            if previous.get('source_sha256')==m['sha256'] and previous.get('quantizer_sha256')==plan['quantizer_sha256'] and previous.get('precision')==precision and sha(legacy)==previous.get('output_sha256'):
                meta=gguf_metadata(legacy)
                expected_type={'Q8_0':7,'Q6_K':18,'Q5_K_M':17,'Q4_K_M':15,'Q3_K_M':12,'Q2_K':10}[precision]
                if meta['file_type']!=expected_type or meta['chat_template_sha256']!=m['gguf_metadata']['chat_template_sha256']:
                    raise ValueError('Legacy GGUF metadata mismatch')
                info={'model_id':model_id,'precision':precision,'source':m['path'],'source_sha256':m['sha256'],
                      'quantizer':str(quant),'quantizer_sha256':plan['quantizer_sha256'],
                      'output':str(legacy),'output_sha256':previous['output_sha256'],'bytes':legacy.stat().st_size,
                      'calibration':'none; verified cohort 024 same-source weight-only quantization',
                      'reused_provenance_sha256':sha(legacy_side)}
                atomic_json(side,info)
                side.with_suffix('.quantize.log').write_text('Reused verified cohort 024 GGUF and provenance: '+str(legacy)+'\n')
                return info
    if output.exists():raise FileExistsError('Unprovenanced quantized file; refusing overwrite')
    if shutil.disk_usage(target).free < int(Path(m['path']).stat().st_size*0.7)+4_000_000_000:
        raise OSError('Insufficient disk reserve')
    partial=output.with_suffix('.partial.gguf')
    if partial.exists():raise FileExistsError('Previous partial quantization; inspect before retry')
    command=[str(quant),m['path'],str(partial),precision]
    log=side.with_suffix('.quantize.log')
    with log.open('x') as f:
        result=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'Quantizer failed ({result.returncode}); partial and log retained')
    if not partial.is_file() or partial.stat().st_size==0:raise ValueError('Empty quantized output')
    expected_type={'Q8_0':7,'Q6_K':18,'Q5_K_M':17,'Q4_K_M':15,'Q3_K_M':12,'Q2_K':10}[precision]
    output_meta=gguf_metadata(partial)
    if output_meta['file_type']!=expected_type or output_meta['chat_template_sha256']!=m['gguf_metadata']['chat_template_sha256']:
        raise ValueError('Quantized GGUF format or chat template differs from F16')
    os.replace(partial,output)
    info={'model_id':model_id,'precision':precision,'source':m['path'],'source_sha256':m['sha256'],
          'quantizer':str(quant),'quantizer_sha256':plan['quantizer_sha256'],'command':command,
          'output':str(output),'output_sha256':sha(output),'bytes':output.stat().st_size,
          'calibration':'none; llama.cpp weight-only quantization'}
    atomic_json(side,info)
    return info

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('model_id');p.add_argument('precision');a=p.parse_args()
    print(json.dumps(build(a.model_id,a.precision),indent=2))
