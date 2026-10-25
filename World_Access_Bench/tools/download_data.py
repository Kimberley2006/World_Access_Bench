"""Restore exact input assets from a GitHub release or local ZIPs (stdlib only)."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import urllib.error
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def checked_members(archive):
    for info in archive.infolist():
        p = PurePosixPath(info.filename)
        if (p.is_absolute() or '..' in p.parts or '\\' in info.filename
                or not p.parts or p.parts[0] != 'World_Bench_Server_Inputs'
                or stat.S_ISLNK(info.external_attr >> 16)):
            raise ValueError(f'Unsafe ZIP member: {info.filename}')
        yield info

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive-dir', type=Path)
    parser.add_argument('--output-dir', type=Path, default=ROOT)
    args = parser.parse_args()
    spec = json.loads((ROOT / 'release-assets.json').read_text())
    cache = args.archive_dir or ROOT / '.downloads'
    cache.mkdir(parents=True, exist_ok=True)
    archives = []
    for asset in spec['assets']:
        path = cache / asset['name']
        if not path.exists():
            if args.archive_dir:
                raise FileNotFoundError(path)
            url = f"https://github.com/{spec['repository']}/releases/download/{spec['tag']}/{asset['name']}"
            partial = path.with_suffix('.zip.part')
            print(f"Downloading {asset['name']}", flush=True)
            try:
                with urllib.request.urlopen(url, timeout=60) as response, partial.open('wb') as out:
                    shutil.copyfileobj(response, out, 1024 * 1024)
                if partial.stat().st_size != asset['size_bytes'] or digest(partial) != asset['sha256']:
                    raise ValueError(f'Asset checksum mismatch: {asset["name"]}')
                partial.replace(path)
            finally:
                partial.unlink(missing_ok=True)
        if path.stat().st_size != asset['size_bytes'] or digest(path) != asset['sha256']:
            raise ValueError(f'Asset checksum mismatch: {path.name}')
        archives.append(path)
        print(f'Verified {path.name}', flush=True)
    dest = args.output_dir.resolve()
    # Preflight every member before writing any extracted file.
    for path in archives:
        with zipfile.ZipFile(path) as archive:
            for info in checked_members(archive):
                target = dest / info.filename
                if not target.resolve().is_relative_to(dest):
                    raise ValueError(f'Path escapes output directory: {info.filename}')
                if target.exists() and not info.is_dir():
                    if not target.is_file():
                        raise ValueError(f'File conflicts with directory: {info.filename}')
                    with archive.open(info) as source:
                        h = hashlib.sha256()
                        for block in iter(lambda: source.read(1024 * 1024), b''):
                            h.update(block)
                    if digest(target) != h.hexdigest():
                        raise ValueError(f'Existing file differs; refusing to overwrite: {info.filename}')
    for path in archives:
        with zipfile.ZipFile(path) as archive:
            for info in checked_members(archive):
                target = dest / info.filename
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                elif not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(info) as source, target.open('xb') as out:
                        shutil.copyfileobj(source, out, 1024 * 1024)
    print(f'Restored inputs to {dest / "World_Bench_Server_Inputs"}')
    print('Run: python3 World_Bench_Server_Inputs/tools/verify_inputs.py')

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile, urllib.error.URLError) as exc:
        raise SystemExit(f'Restore failed: {exc}')
