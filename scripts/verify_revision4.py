#!/usr/bin/env python3
"""Rerun the SWaT A11 and HAI 21.03 analyses and compare them with the archived results.

Intended for the authors' own verification before submission. Each analysis is rerun into a
temporary directory with the archived scripts, and every CSV output is compared with the copy
in results/ (numeric columns with a relative tolerance, text columns exactly).

    python scripts/verify_revision4.py --a11-dir data/private/swat_a11 --hai-dir DATA/hai-21.03

Either argument may be omitted to skip that analysis. Runtime: A11 about 1 min; HAI 21.03 with
20 seed repeats roughly 10-30 min depending on the machine (use --hai-seeds 0 for a quick check).
"""
from __future__ import annotations
import argparse, os, subprocess, sys, tempfile
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def compare_csv(new: Path, ref: Path, rtol=1e-9, atol=1e-12):
    a, b = pd.read_csv(new), pd.read_csv(ref)
    if a.shape != b.shape or list(a.columns) != list(b.columns):
        return False, f'shape/columns differ: {a.shape} vs {b.shape}'
    worst = 0.0
    for c in a.columns:
        x, y = a[c], b[c]
        if pd.api.types.is_numeric_dtype(x) and pd.api.types.is_numeric_dtype(y):
            if not np.allclose(x.to_numpy(float), y.to_numpy(float), rtol=rtol, atol=atol, equal_nan=True):
                d = np.nanmax(np.abs(x.to_numpy(float) - y.to_numpy(float)))
                return False, f'column {c}: max abs difference {d:.3g}'
        elif not (x.astype(str) == y.astype(str)).all():
            return False, f'column {c}: text differs'
    return True, 'identical within tolerance'


def run(cmd, env):
    print('  $', ' '.join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:])
    return r.returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--a11-dir', help='folder with the two SWaT A11 CSV files')
    ap.add_argument('--hai-dir', help='folder with the HAI 21.03 files (train1..3, test1..5)')
    ap.add_argument('--hai-seeds', type=int, default=20, help='seed repeats for HAI (0 = primary seed only)')
    a = ap.parse_args()
    env = dict(os.environ, PYTHONPATH=str(ROOT / 'src') + os.pathsep + os.environ.get('PYTHONPATH', ''))
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        if a.a11_dir:
            print('SWaT A11 rerun ...')
            rc = run([sys.executable, 'experiments/swat/a11_rerun.py', '--data-dir', a.a11_dir, '--out-dir', str(tmp / 'a11')], env)
            for f in ('table_11.csv', 'table_12.csv', 'a11_seed_sensitivity.csv'):
                ok, msg = (False, 'script failed') if rc else compare_csv(tmp / 'a11' / f, ROOT / 'results/swat_a11' / f)
                rows.append(('A11', f, ok, msg))
        if a.hai_dir:
            print('HAI 21.03 evaluation ...')
            cmd = [sys.executable, 'experiments/hai_evaluation.py', '--data-dir', a.hai_dir, '--out-dir', str(tmp / 'hai')]
            if a.hai_seeds: cmd += ['--seed-sensitivity', str(a.hai_seeds)]
            rc = run(cmd, env)
            files = ['hai_operating_points.csv', 'hai_partitions.csv'] + (['hai_seed_sensitivity.csv'] if a.hai_seeds else [])
            for f in files:
                ok, msg = (False, 'script failed') if rc else compare_csv(tmp / 'hai' / f, ROOT / 'results/hai/hai21.03' / f, rtol=1e-6)
                rows.append(('HAI 21.03', f, ok, msg))
    if not rows:
        ap.error('give --a11-dir and/or --hai-dir')
    print('\nResult')
    for an, f, ok, msg in rows:
        print(f"  {'PASS' if ok else 'FAIL'}  {an:10s} {f:28s} {msg}")
    print('\nIf a file differs only in the last digits, check the library versions against README.md '
          '("Environment of the reported runs"); Isolation Forest results can change slightly across scikit-learn versions.')
    return 0 if all(r[2] for r in rows) else 1


if __name__ == '__main__':
    raise SystemExit(main())
