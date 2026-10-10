import hashlib, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'experiments' / 'swat'))
import a11_rerun as A


def test_event_spec_hash_frozen():
    spec = ROOT / 'experiments/swat/a11_constructed_events.json'
    recorded = (ROOT / 'experiments/swat/a11_constructed_events.sha256').read_text().split()[0]
    assert hashlib.sha256(spec.read_bytes()).hexdigest() == recorded
    ev = json.loads(spec.read_text())['events']
    assert sum(e['set'] == 'calibration' for e in ev) == 12 and sum(e['set'] == 'heldout' for e in ev) == 12


def test_threshold_and_intervals():
    cal = np.arange(1167, dtype=float)
    thr = A.select_threshold(cal, 0.05)
    assert (cal >= thr).sum() == 58
    lo, hi = A.wilson(0.1055, 485)
    assert round(100 * lo, 2) == 8.12 and round(100 * hi, 2) == 13.60
    assert A.level_eq15(0.463) == 2 and A.level_eq15(0.547) == 1


def test_reported_results_consistent():
    r = json.loads((ROOT / 'results/swat_a11/a11_results.json').read_text())
    assert [round(100 * x['tgt_rate'], 2) for x in r['transfer_training']] == [1.96, 10.55, 17.92]
    assert [round(100 * x['cal_rate'], 2) for x in r['transfer_training']] == [0.94, 4.97, 9.94]
    assert r['meta']['variables'] == 82 and r['meta']['features'] == 173


def test_missing_data_guard(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['a11_rerun.py', '--data-dir', str(tmp_path), '--out-dir', str(tmp_path / 'o')])
    assert A.main() == 2
