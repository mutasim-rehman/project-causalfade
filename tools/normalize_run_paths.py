"""Remove machine account names from publishable logs and configuration."""
import argparse
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    archive = args.archive.resolve()
    if archive.is_relative_to(root):
        parser.error("Place the original-file archive outside Git")
    prefix = (str(Path.home()) + "/").encode()
    for path in args.paths:
        path = path.resolve()
        if not path.is_relative_to(root):
            parser.error(f"Path must be inside the repository: {path.name}")
        files = sorted(path.rglob("*")) if path.is_dir() else [path]
        for file in files:
            if not file.is_file() or file.suffix not in {".md", ".log", ".json", ".jsonl"}:
                continue
            original = file.read_bytes()
            if prefix not in original:
                continue
            archived = archive / file.relative_to(root)
            archived.parent.mkdir(parents=True, exist_ok=True)
            if archived.exists():
                if archived.read_bytes() != original:
                    raise FileExistsError(archived)
            else:
                staging = archived.with_name(archived.name + ".tmp")
                shutil.copyfile(file, staging)
                staging.replace(archived)
            staging = file.with_name(file.name + ".normalize.tmp")
            staging.write_bytes(original.replace(prefix, b"$HOME/"))
            staging.replace(file)


if __name__ == "__main__":
    main()
