"""Sync the repository's human-readable SSD entrypoint and its recorded hash."""
import hashlib
import json
from pathlib import Path
import shutil


def main():
    workspace = Path(__file__).resolve().parents[1]
    root = Path('H:/CAUSALFADE').resolve()
    source = workspace/'results/asset_reuse/SSD_README.md'
    destination = root/'README.md'
    shutil.copyfile(source, destination)
    h = hashlib.sha256(destination.read_bytes()).hexdigest()
    path = root/'manifests/agere_reuse_import.json'
    manifest = json.loads(path.read_text(encoding='utf-8-sig'))
    entry = next(a for a in manifest['assets'] if a['relative_destination'] == 'README.md')
    entry.update(bytes=destination.stat().st_size, expected_hash=h, sha256=h,
                 expected_hash_algorithm='sha256', status='updated_with_quantization_inventory')
    path.write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'readme': str(destination), 'sha256': h}))


if __name__ == '__main__':
    main()
