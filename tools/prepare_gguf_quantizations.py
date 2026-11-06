"""Prepare deterministic GGUF copies from the retained F16 baselines.

Runs the locally installed llama.cpp quantizer; writes only model files and
conversion provenance to the selected data drive. No prompts or inference runs.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess


MODELS = ('0.5b', '1.5b', '3b', '7b')
FORMATS = {'Q8_0': 'q8_0', 'Q4_K_M': 'q4_k_m', 'Q2_K': 'q2_k', 'Q1_0': 'q1_0'}
QUANTIZER_RELEASE = 'llama.cpp b12176 (Windows x64 CPU)'
QUANTIZER_ZIP_SHA256 = '5c1b4049b67d59aa13488f095e00afe823f62569e6a0d76fae8f555717886606'


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8*1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def is_gguf(path):
    with path.open('rb') as stream:
        return stream.read(4) == b'GGUF'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('H:/CAUSALFADE'))
    parser.add_argument('--quantizer', type=Path, required=True, help='Local PC path to llama-quantize.exe')
    parser.add_argument('--threads', type=int, default=max(1, min(8, os.cpu_count() or 1)))
    parser.add_argument('--rebuild-7b-q4', action='store_true',
                        help='Recreate 7B Q4_K_M with this pinned quantizer, preserving the donor copy.')
    args = parser.parse_args()
    root, quantizer = args.root.resolve(), args.quantizer.resolve()
    if not root.is_dir() or root == Path(root.anchor):
        raise ValueError(f'Invalid data root: {root}')
    if not quantizer.is_file() or quantizer.suffix.lower() != '.exe':
        raise ValueError(f'Expected a local Windows quantizer executable: {quantizer}')
    if args.threads < 1:
        raise ValueError('--threads must be positive')
    sources = {m: root/f'weights/gguf/qwen2.5-{m}-instruct-f16.gguf' for m in MODELS}
    for path in sources.values():
        if not path.is_file() or path.stat().st_size < 100_000_000 or not is_gguf(path):
            raise ValueError(f'Missing or invalid F16 source: {path}')
    source_hashes = {model: sha256(path) for model, path in sources.items()}
    outdir = root/'weights/gguf'
    records = []
    preserved = []
    for fmt, suffix in FORMATS.items():
        for model, source in sources.items():
            target = outdir/f'qwen2.5-{model}-instruct-{suffix}.gguf'
            rebuild = fmt == 'Q4_K_M' and model == '7b' and args.rebuild_7b_q4
            if target.exists() and not rebuild:
                if not is_gguf(target):
                    raise ValueError(f'Existing output has invalid header: {target}')
                records.append(dict(model=model, format=fmt, source=str(source), output=str(target),
                                    bytes=target.stat().st_size, sha256=sha256(target),
                                    status='existing_verified_gguf'))
                continue
            if target.exists():
                if not rebuild:
                    raise FileExistsError(f'Refusing to overwrite existing output: {target}')
                archive = outdir/'agere_original'/target.name
                if archive.exists():
                    raise FileExistsError(f'Refusing to overwrite donor archive: {archive}')
                archive.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, archive)
                old_hash = sha256(target)
                if sha256(archive) != old_hash:
                    raise ValueError('Read-back mismatch preserving original donor Q4 model.')
                preserved.append(dict(path=str(archive), bytes=archive.stat().st_size,
                                      sha256=old_hash, reason='Original AGERE Q4_K_M retained before pinned rebuild.'))
            partial = target.with_name(target.stem+'.partial.gguf')
            if partial.exists():
                raise FileExistsError(f'Remove or inspect prior partial before retry: {partial}')
            source_hash = source_hashes[model]
            command = [str(quantizer), str(source), str(partial), fmt, str(args.threads)]
            log = outdir/f'{target.stem}.quantize.log'
            with log.open('w', encoding='utf-8') as stream:
                stream.write(json.dumps(dict(command=command, source_sha256=source_hash,
                                             quantizer=QUANTIZER_RELEASE, started=datetime.now(timezone.utc).isoformat()))+'\n')
                stream.flush()
                result = subprocess.run(command, cwd=quantizer.parent, stdout=stream,
                                        stderr=subprocess.STDOUT, check=False)
            if result.returncode != 0:
                raise RuntimeError(f'{fmt} conversion failed ({result.returncode}); see {log}')
            if not partial.is_file() or partial.stat().st_size <= 0 or not is_gguf(partial):
                raise RuntimeError(f'Quantizer did not produce a valid GGUF; see {log}')
            if target.exists() and rebuild:
                archive = outdir/'agere_original'/target.name
                if not archive.exists() or sha256(archive) != sha256(target):
                    raise RuntimeError('Preserved Q4 donor copy failed verification; original output kept.')
                target.unlink()
            partial.rename(target)
            records.append(dict(model=model, format=fmt, source=str(source), source_sha256=source_hash,
                                output=str(target), bytes=target.stat().st_size, sha256=sha256(target),
                                log=str(log), status='quantized_and_hash_recorded'))
            report = dict(created_at=datetime.now(timezone.utc).isoformat(), quantizer=QUANTIZER_RELEASE,
                          quantizer_sha256=QUANTIZER_ZIP_SHA256, threads=args.threads, method='weight-only GGUF conversion; no imatrix supplied',
                          status='in_progress', assets=records, preserved_originals=preserved)
            (root/'manifests/quantization_preparation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
            print(json.dumps({'format': fmt, 'model': model, 'bytes': target.stat().st_size, 'sha256': records[-1]['sha256']}), flush=True)
    report = dict(created_at=datetime.now(timezone.utc).isoformat(), quantizer=QUANTIZER_RELEASE,
                  quantizer_sha256=QUANTIZER_ZIP_SHA256, threads=args.threads,
                  method='Weight-only GGUF conversion from each matched F16 GGUF; no importance matrix or study prompts used.',
                  formats=list(FORMATS), models=list(MODELS), status='complete', assets=records,
                  preserved_originals=preserved,
                  note='Preparation only. No model inference, causal tasks, evaluation, or data collection performed.')
    (root/'manifests/quantization_preparation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'status': 'complete', 'assets': len(records), 'free_bytes': shutil.disk_usage(root).free}))


if __name__ == '__main__':
    main()
