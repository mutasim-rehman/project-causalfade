"""Audit AGERE assets and optionally copy a verified allowlist to CAUSALFADE.

Default is read-only. --apply copies without changing the donor; no network,
hardlinks, environments, adapters or AGERE experiment records are imported.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


def contained(root, relative):
    root = root.resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or path == root:
        raise ValueError(f'Path escapes the named root: {relative}')
    return path


def digest(path, algorithm='sha256'):
    h = hashlib.new('sha1' if algorithm == 'git-blob-sha1' else algorithm)
    if algorithm == 'git-blob-sha1':
        h.update(f'blob {path.stat().st_size}\0'.encode())
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def data_destination(root, relative):
    """Only import inert research assets; executable code belongs in Git."""
    path = contained(root, relative)
    allowed = {'.gguf', '.safetensors', '.json', '.jsonl', '.csv', '.tsv',
               '.txt', '.md', '.metadata', '.log', '.model', '.tiktoken', '.sha256'}
    parts = path.relative_to(root.resolve()).parts
    if parts[0] not in {'weights', 'datasets', 'runs', 'manifests'} or path.suffix.lower() not in allowed:
        raise ValueError(f'SSD data-only policy rejects destination: {relative}')
    return path


def plan_assets(source, destination, workspace):
    source, destination = source.resolve(), destination.resolve()
    if source == destination or destination.is_relative_to(source) or source.is_relative_to(destination):
        raise ValueError('Source and destination roots must be separate non-nested folders.')
    if destination == Path(destination.anchor):
        raise ValueError('Destination may not be a drive root.')
    manifest = json.loads((source/'phase2/manifests/gguf_artifacts.json').read_text())
    verification = json.loads((source/'phase2/manifests/source_verification.json').read_text())
    assets = []
    models = [f'Qwen/Qwen2.5-{size}-Instruct' for size in ('0.5B','1.5B','3B','7B')]

    def add(src, relative, category, revision=None, expected=None, algorithm='sha256'):
        src = Path(src).resolve()
        if not src.is_file() or src.is_symlink():
            raise ValueError(f'Missing or unsupported source file: {src}')
        dst = data_destination(destination, relative)
        assets.append(dict(source=str(src), destination=str(dst), relative_destination=str(relative).replace('\\','/'),
                           category=category, bytes=src.stat().st_size, revision=revision,
                           expected_hash=expected or digest(src), expected_hash_algorithm=algorithm))

    for entry in manifest['artifacts']:
        if entry['model'] in models:
            path = contained(source,entry['path'])
            if path.stat().st_size != entry['size_bytes']:
                raise ValueError(f'Source size differs from recorded GGUF artifact: {path}')
            with path.open('rb') as f:
                if f.read(4) != b'GGUF':
                    raise ValueError(f'Invalid GGUF header: {path}')
            if entry['source_revision'] != verification['revisions'][entry['model']]:
                raise ValueError('Conflicting source revision records.')
            add(path,entry['path'],'gguf_recorded_source',entry['source_revision'],entry['sha256'])
    for model in models:
        folder = source/'weights/hf'/model.replace('/','--')
        revision = verification['revisions'][model]
        files = sorted(p for p in folder.iterdir() if p.is_file())
        if any('adapter' in p.name.lower() for p in files):
            raise ValueError('An adapter was found in an original-checkpoint folder.')
        index = folder/'model.safetensors.index.json'
        if index.exists():
            required = set(json.loads(index.read_text())['weight_map'].values())
            if not required.issubset({p.name for p in files}):
                raise ValueError('Incomplete checkpoint shard set.')
        elif not (folder/'model.safetensors').exists():
            raise ValueError('No original checkpoint weights.')
        for path in files:
            metadata = folder/'.cache/huggingface/download'/f'{path.name}.metadata'
            if not metadata.exists():
                raise ValueError(f'No source download metadata: {path}')
            lines = metadata.read_text().splitlines()
            if len(lines) < 2 or lines[0] != revision:
                raise ValueError(f'Unexpected revision for {path}')
            etag = lines[1]
            algorithm = 'sha256' if len(etag) == 64 else 'git-blob-sha1'
            if len(etag) not in (40,64) or any(c not in '0123456789abcdef' for c in etag):
                raise ValueError('Unrecognized source digest.')
            add(path,path.relative_to(source),'hf_original',revision,etag,algorithm)
            add(metadata,Path('manifests/agere_source/hf')/folder.name/'download'/metadata.name,'source_metadata',revision)
        tree = folder/'.cache/huggingface/trees'/f'{revision}.json'
        if tree.exists():
            add(tree,Path('manifests/agere_source/hf')/folder.name/'trees'/tree.name,'source_metadata',revision)
    for path in sorted((source/'phase2/manifests').iterdir()):
        if path.is_file():
            add(path,Path('manifests/agere_source/phase2')/path.name,'source_metadata')
    for version in ('agere-cpu-v1','agere-cpu-v2'):
        path = source/'runtime'/version/'manifest.json'
        add(path,Path('manifests/agere_source/runtime')/f'{version}.json','runtime_evidence_only')
    # Only generated datasets go to the SSD. Source stays in the repository.
    for path in sorted((workspace/'results/design_validation').iterdir()):
        if path.is_file():
            add(path,Path('datasets/design_validation')/path.name,'causalfade_synthetic_dataset')
    total = sum(a['bytes'] for a in assets)
    categories = {c: dict(files=sum(a['category']==c for a in assets),
                          bytes=sum(a['bytes'] for a in assets if a['category']==c))
                  for c in sorted({a['category'] for a in assets})}
    return dict(source_root=str(source),destination_root=str(destination),assets=assets,
                total_bytes=total,categories=categories,
                storage_policy='Git repository: all research code. Local PC: installed environments. SSD: data, weights, logs, results and provenance only.',
                code_repository='https://github.com/mutasim-rehman/project-causalfade',
                source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=workspace,text=True).strip(),
                excludes=[
                    '14B/32B models: outside the chosen study sizes.',
                    'tier8_v2 GGUF variants: tensor/context metadata differs; provenance/parity not established.',
                    'hf-training and adapters: trained/derived assets, not untouched baselines.',
                    'AGERE datasets, labels, run logs and fitted parameters: different study; not CausalFade evidence.',
                    'All source snapshots, scripts, binaries, installers and environments: code belongs in the repository or local PC, never on the SSD.',
                    'Windows torch-2.6.0+cu124-cp312-cp312-win_amd64.whl: reusable installer candidate, not a selected runtime.'
                ])


def verified_copy(asset):
    src, dst = Path(asset['source']), Path(asset['destination'])
    expected, algorithm = asset['expected_hash'], asset['expected_hash_algorithm']
    if dst.exists():
        if dst.stat().st_size != asset['bytes'] or digest(dst,algorithm) != expected:
            raise ValueError(f'Existing destination differs; refusing overwrite: {dst}')
        return dict(asset,status='already_present_verified',sha256=digest(dst))
    dst.parent.mkdir(parents=True,exist_ok=True)
    temporary = dst.with_name(dst.name+'.causalfade-import.partial')
    initial = src.stat()
    if initial.st_size != asset['bytes']:
        raise ValueError('Source changed since planning.')
    offset = temporary.stat().st_size if temporary.exists() else 0
    if offset > initial.st_size:
        raise ValueError('Partial destination is larger than source.')
    h = hashlib.new('sha1' if algorithm == 'git-blob-sha1' else algorithm)
    sha = hashlib.sha256()
    if algorithm == 'git-blob-sha1':
        h.update(f'blob {initial.st_size}\0'.encode())
    # Resume only after byte-for-byte validation of the existing prefix.
    last = time.monotonic()
    with src.open('rb') as reader:
        if offset:
            with temporary.open('rb') as prior:
                remaining = offset
                while remaining:
                    size = min(8*1024*1024,remaining)
                    block = reader.read(size)
                    if block != prior.read(size):
                        raise ValueError('Partial destination does not match source prefix.')
                    h.update(block);sha.update(block);remaining -= len(block)
        with temporary.open('ab' if temporary.exists() else 'xb') as writer:
            copied = offset
            while block := reader.read(8*1024*1024):
                writer.write(block);h.update(block);sha.update(block);copied += len(block)
                if time.monotonic()-last > 25:
                    print(json.dumps({'progress':dst.name,'copied_gib':round(copied/2**30,2),'total_gib':round(initial.st_size/2**30,2)}),flush=True)
                    last = time.monotonic()
            writer.flush();os.fsync(writer.fileno())
    final = src.stat()
    if final.st_size != initial.st_size or final.st_mtime_ns != initial.st_mtime_ns:
        raise ValueError('Source changed while copying; staged file was not promoted.')
    if h.hexdigest() != expected:
        raise ValueError(f'Source content does not match recorded digest: {src}')
    if temporary.stat().st_size != initial.st_size or digest(temporary) != sha.hexdigest():
        raise ValueError('Destination read-back verification failed.')
    if dst.exists():
        raise ValueError('Destination appeared during import; refusing overwrite.')
    temporary.rename(dst)
    return dict(asset,status='copied_and_readback_verified',sha256=sha.hexdigest())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=Path('H:/AGERE'))
    parser.add_argument('--destination',type=Path,default=Path('H:/CAUSALFADE'))
    parser.add_argument('--report',type=Path,default=Path('results/asset_reuse/plan.json'))
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    workspace=Path(__file__).resolve().parents[1]
    plan=plan_assets(args.source,args.destination,workspace)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in plan.items() if k!='assets'},indent=2),flush=True)
    if not args.apply:
        return
    needed=sum(a['bytes'] for a in plan['assets'] if not Path(a['destination']).exists())
    free=shutil.disk_usage(args.destination).free
    if needed+10*2**30 > free:
        raise ValueError('Insufficient SSD headroom: reserve at least 10 GiB after import.')
    root=args.destination.resolve()
    for a in plan['assets']:
        data_destination(root,a['relative_destination'])
    for folder in ('weights','datasets','runs','manifests'):
        contained(root,folder).mkdir(parents=True,exist_ok=True)
    journal=root/'manifests/agere_reuse_journal.jsonl'
    records=[]
    with journal.open('a',encoding='utf-8') as log:
        for i,a in enumerate(plan['assets']):
            if a['bytes'] > 64*1024*1024:
                print(json.dumps({'starting':a['relative_destination'],'gib':round(a['bytes']/2**30,3)}),flush=True)
            record=verified_copy(a);records.append(record)
            log.write(json.dumps(record)+'\n');log.flush();os.fsync(log.fileno())
            if a['bytes'] > 64*1024*1024:
                print(json.dumps({'verified':a['relative_destination'],'files_done':i+1}),flush=True)
    result={**plan,'assets':records,'status':'complete_verified','free_bytes_after':shutil.disk_usage(root).free,
            'verification_scope':'Content hashes match locally recorded donor digests and destination read-back; no upstream re-download or inference smoke test.'}
    local=args.report.with_name('import_result.json')
    local.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (root/'manifests/agere_reuse_import.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'files':len(records),'bytes':plan['total_bytes'],
                      'free_gib':round(result['free_bytes_after']/2**30,2)}),flush=True)


if __name__=='__main__':
    main()
