#!/usr/bin/env python3
"""Build a clean v1.0.0 source-and-results ZIP excluding private/restricted data."""
from pathlib import Path
import argparse,hashlib,zipfile
ROOT=Path(__file__).resolve().parents[1]

def excluded(rel):
    parts=rel.parts
    if '.git' in parts or '.venv' in parts or '__pycache__' in parts or '.pytest_cache' in parts: return True
    if rel.as_posix().startswith('data/private/') and rel.name!='.gitkeep': return True
    if rel.as_posix().startswith('results/swat/'): return True
    if rel.suffix in {'.pyc','.pyo'}: return True
    return False

def main(output=None):
    output=Path(output) if output else ROOT.parent/'RDFR-CI-v1.0.0.zip'
    files=[p for p in ROOT.rglob('*') if p.is_file() and not excluded(p.relative_to(ROOT))]
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(files): z.write(p,Path('RDFR-CI')/p.relative_to(ROOT))
    h=hashlib.sha256(output.read_bytes()).hexdigest()
    sums=ROOT.parent/'RDFR-CI-v1.0.0-SHA256.txt'; sums.write_text(f'{h}  {output.name}\n',encoding='utf-8')
    print(output); print('SHA256',h); return output
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--output'); a=ap.parse_args(); main(a.output)
