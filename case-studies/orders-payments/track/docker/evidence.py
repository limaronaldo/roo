"""Export an allowlist of synthetic receipts/logs, never database data or env."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path('/workspace')
CASE = ROOT / 'case-studies/orders-payments'
DEST = ROOT / 'evidence'


def identity():
    excluded = {'target', 'build', '.runtime', '.deps', '__pycache__'}
    hashes = {}
    for path in sorted(CASE.rglob('*')):
        if path.is_file() and not excluded.intersection(path.relative_to(CASE).parts):
            hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    (DEST / 'source-identity.json').write_text(json.dumps(hashes, indent=2) + '\n')


def collect():
    receipts = {'last-run.json', 'starter-last-run.json', 'solution-last-run.json',
                'e6-independent-last-run.json'}
    for directory in (CASE / 'track/.runtime', CASE / 'postgres/.runtime', CASE / 'http/.runtime'):
        if not directory.exists():
            continue
        for path in sorted(directory.iterdir()):
            if path.is_file() and (path.name in receipts or path.name.endswith('.log')):
                target = DEST / directory.parent.name / path.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)


DEST.mkdir(exist_ok=True)
if sys.argv[1] == 'identity':
    identity()
else:
    collect()
