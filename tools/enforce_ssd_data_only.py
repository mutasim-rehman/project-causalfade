"""Remove the recorded redundant SSD source snapshot. Dry-run unless --apply.

Unknown files, symlinks, changed snapshots or missing repository originals stop
cleanup. Weights and datasets are never removed. Run from the repository.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil

from tools.reuse_ssd_assets import contained, digest


def check_snapshot(root, workspace, assets):
    root, workspace = root.resolve(), workspace.resolve()
    if root == Path(root.anchor):
        raise ValueError('Refusing a drive root.')
    target = contained(root, 'runtime/source')
    records = [a for a in assets if a['relative_destination'].startswith('runtime/source/')]
    expected = {contained(root, a['relative_destination']) for a in records}
    if len(expected) != len(records):
        raise ValueError('Duplicate snapshot paths.')
    if target.exists():
        if any(p.is_symlink() or p.is_junction() for p in [root, root/'runtime', target]):
            raise ValueError('Refusing linked snapshot directories.')
        paths = list(target.rglob('*'))
        if any(p.is_symlink() or p.is_junction() for p in paths):
            raise ValueError('Refusing links inside snapshot.')
        actual = {p.resolve() for p in paths if p.is_file()}
        if actual != expected:
            raise ValueError('Snapshot contains missing or unrecorded files; refusing removal.')
    elif records:
        raise ValueError('Snapshot is missing but still recorded; reconcile manually.')
    for a in records:
        path = contained(root, a['relative_destination'])
        original = Path(a['source']).resolve()
        if not original.is_relative_to(workspace) or not original.is_file():
            raise ValueError(f'Repository original unavailable: {original}')
        if path.stat().st_size != a['bytes'] or digest(path) != a['sha256']:
            raise ValueError(f'Snapshot changed; preserve edits before cleanup: {path}')
    return target, records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('H:/CAUSALFADE'))
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    workspace = Path(__file__).resolve().parents[1]
    root = args.root.resolve()
    manifest = contained(root, 'manifests/agere_reuse_import.json')
    result = json.loads(manifest.read_text(encoding='utf-8-sig'))
    if Path(result['destination_root']).resolve() != root:
        raise ValueError('Manifest belongs to a different SSD directory.')
    target, removed = check_snapshot(root, workspace, result['assets'])
    print(json.dumps({'target': str(target), 'redundant_files': len(removed), 'apply': args.apply}))
    if not args.apply:
        return
    report = dict(event='enforce_data_only_storage', timestamp=datetime.now(timezone.utc).isoformat(),
                  removed_files=len(removed), removed_bytes=sum(a['bytes'] for a in removed),
                  removed_assets=removed,
                  storage_policy='All code in Git repository; SSD holds data assets only.')
    # Preserve verified removal evidence before deleting this exact checked subtree.
    report_dir = workspace/'results/asset_reuse'
    report_dir.mkdir(parents=True, exist_ok=True)
    if removed:
        (report_dir/'storage_policy_migration.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        (root/'manifests/storage_policy_migration.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        # target is resolved and confined above; unknown/modified files block removal.
        shutil.rmtree(target)
        if not any(target.parent.iterdir()):
            target.parent.rmdir()
    assets = [a for a in result['assets'] if a not in removed]
    readme = root/'README.md'
    readme.write_bytes((report_dir/'SSD_README.md').read_bytes())
    for a in assets:
        if a['relative_destination'] == 'README.md':
            a.update(bytes=readme.stat().st_size, expected_hash=digest(readme), sha256=digest(readme),
                     expected_hash_algorithm='sha256', status='updated_storage_policy')
    result.update(assets=assets, verified_file_count=len(assets), total_bytes=sum(a['bytes'] for a in assets),
                  storage_policy=report['storage_policy'],
                  code_repository='https://github.com/mutasim-rehman/project-causalfade',
                  free_bytes_after=shutil.disk_usage(root).free)
    result['categories'] = {c: dict(files=sum(a['category']==c for a in assets),
                                   bytes=sum(a['bytes'] for a in assets if a['category']==c))
                            for c in sorted({a['category'] for a in assets})}
    result.pop('source_snapshot', None)
    result['supplemental_files'] = sum(a['category'] in {'model_preparation_log', 'ssd_entrypoint'} for a in assets)
    result['notes'] = [
        'Redundant source snapshot removed; all code is maintained in the Git repository.',
        'No source AGERE files were modified. No model downloads were performed.',
        'Model preparation logs are provenance, not CausalFade experimental observations.'
    ]
    encoded = json.dumps(result, indent=2)+'\n'
    manifest.write_text(encoded, encoding='utf-8')
    (report_dir/'import_result.json').write_text(encoded, encoding='utf-8')
    if removed:
        with (root/'manifests/agere_reuse_journal.jsonl').open('a', encoding='utf-8') as journal:
            journal.write(json.dumps({k:v for k,v in report.items() if k != 'removed_assets'})+'\n')
    print(json.dumps({'retained_assets': len(assets), 'source_snapshot_exists': target.exists()}))


if __name__ == '__main__':
    main()
