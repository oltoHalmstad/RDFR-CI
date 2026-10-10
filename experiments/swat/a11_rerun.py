#!/usr/bin/env python3
"""SWaT A11 threshold transfer and constructed-event challenge with an explicit Equation (14) reference.

Rerun of Section 4.3 of the article for release v1.4.1.

* Features (Section 3.13, Equation (13)): 82 historian variables (alarm fields encoded Active=1/Inactive=0;
  fields that are entirely "Bad Input" removed; remaining bad inputs interpolated), rolling mean, standard
  deviation and end-to-end delta over 60 s windows ending every 5 s; features constant on the training segment
  removed (173 features).
* Detector: Isolation Forest (300 trees, seed 42) on the first 80% of the 19 February capture; thresholds for
  the nominal budgets selected on the remaining 20% (calibration segment).
* Equation (14): training-referenced form (primary); the segment-wise form of release v1.3.0 is reported for
  comparison only.
* Constructed-event challenge: specification frozen in a11_constructed_events.json (SHA-256 in
  a11_constructed_events.sha256) before any perturbed copy was scored.

The raw SWaT files are restricted (iTrust) and are not redistributed. Place them in data/private/swat_a11/.

    PYTHONPATH=src python experiments/swat/a11_rerun.py --data-dir data/private/swat_a11 --out-dir results/swat_a11
"""
from __future__ import annotations
import argparse, hashlib, json, platform, sys, time
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import beta

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from train_isolation_forest import train_isolation_forest, fit_score_reference, anomaly_scores  # noqa: E402

L, STEP, TRAIN_FRAC = 60, 5, 0.80
PHIS = (0.01, 0.05, 0.10)
FILE_A = 'SWaT.A10_OTDataset_19-Feb-2026_0930_1735.csv'
FILE_B = 'SWaT.A10_OTDataset_20-Feb-2026_0905_1710.csv'
Z = 1.959963984540054


# ----------------------------------------------------------------------------------------------- data
def load(path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df.pop('t_stamp')
    out = {}
    for c in df.columns:
        s = df[c].str.strip().replace({'Active': '1', 'Inactive': '0', 'Bad Input': np.nan, '': np.nan})
        out[c] = pd.to_numeric(s, errors='coerce')
    return pd.DataFrame(out)


def prepare(data_dir):
    Xa, Xb = load(data_dir / FILE_A), load(data_dir / FILE_B)
    var = [c for c in Xa.columns if Xa[c].isna().mean() <= 0.5 and Xb[c].isna().mean() <= 0.5]
    fill = lambda X: X[var].interpolate(limit_direction='both').ffill().bfill()
    return fill(Xa), fill(Xb), var


def features(X):
    F = pd.concat([X.rolling(L).mean().add_suffix('_mean'), X.rolling(L).std().add_suffix('_std'),
                   (X - X.shift(L - 1)).add_suffix('_delta')], axis=1)
    ends = np.arange(L - 1, len(X), STEP)
    return F.iloc[ends].reset_index(drop=True), ends


# ----------------------------------------------------------------------------------------------- statistics
def wilson(p, n):
    den = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / den
    h = Z * np.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / den
    return c - h, c + h


def clopper_pearson(k, n):
    lo = 0.0 if k == 0 else beta.ppf(0.025, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(0.975, k + 1, n - k)
    return float(lo), float(hi)


def select_threshold(cal, phi):
    """Smallest threshold whose calibration flag rate (score >= threshold) does not exceed phi."""
    s = np.sort(cal)[::-1]
    k = int(np.floor(phi * len(cal) + 1e-12))
    thr = s[k - 1] if k >= 1 else np.inf
    while (cal >= thr).mean() > phi + 1e-12:
        thr = np.nextafter(thr, np.inf)
    return float(thr)


def level_eq15(rci):
    """Provisional level of the water-treatment context (Equation (15); Table 6 half-open bands)."""
    if rci < 0.35: return 3
    if rci < 0.50: return 2
    if rci < 0.65: return 1
    return 0


LEVEL_NAME = {3: 'Human-approved intervention', 2: 'Assisted defense', 1: 'Shadow/restricted', 0: 'Rollback/isolation'}


# ----------------------------------------------------------------------------------------------- analyses
class Detector:
    def __init__(self, Ftrain, seed, form):
        self.sc, self.model = train_isolation_forest(Ftrain, seed)
        self.form = form
        self.ref = fit_score_reference(self.sc, self.model, Ftrain) if form == 'training' else 'segment'

    def score(self, F):
        return anomaly_scores(self.sc, self.model, F, reference=self.ref)


def transfer(det, Fcal, Ftgt, n_blocks):
    acal, atgt = det.score(Fcal), det.score(Ftgt)
    rows = []
    for phi in PHIS:
        thr = select_threshold(acal, phi)
        k = int((atgt >= thr).sum()); n = len(atgt); p = k / n
        lo_w, hi_w = wilson(p, n); lo_b, hi_b = wilson(p, n_blocks)
        rows.append(dict(phi=phi, threshold=thr, cal_rate=float((acal >= thr).mean()), tgt_flags=k, tgt_windows=n,
                         tgt_rate=p, ci_windows=[lo_w, hi_w], ci_blocks=[lo_b, hi_b],
                         exceedance_distinguishable_blocks=bool(lo_b > phi)))
    return rows, acal, atgt


def perturb(Xb, ev, sd):
    X = Xb.copy()
    v, s, dur = ev['variable'], ev['start_s'], ev['duration_s']
    idx = np.arange(s, s + dur)
    if ev['type'] == 'offset':
        X.loc[idx, v] = X.loc[idx, v] + 2 * sd[v]
    elif ev['type'] == 'ramp':
        X.loc[idx, v] = X.loc[idx, v] + np.linspace(0, 4 * sd[v], dur)
    elif ev['type'] == 'freeze':
        X.loc[idx, v] = X.loc[s, v]
    elif ev['type'] == 'zero':
        X.loc[idx, v] = 0.0
    else:
        raise ValueError(ev['type'])
    return X


def window_labels(ends, ev):
    s, dur = ev['start_s'], ev['duration_s']
    return (ends >= s) & (ends <= s + dur - 1 + (L - 1))


def challenge(det, copies, ends, events, keep, thresholds, tgt_scores, n_boot, seed):
    """Constructed-event challenge: F1 comparator from calibration events, evaluation on held-out events."""
    scores = {ev['id']: det.score(copies[ev['id']][keep].to_numpy()) for ev in events}
    cal = [e for e in events if e['set'] == 'calibration']; held = [e for e in events if e['set'] == 'heldout']
    # F1 comparator on calibration copies
    s_all = np.concatenate([scores[e['id']] for e in cal]); y_all = np.concatenate([window_labels(ends, e) for e in cal])
    cand = np.unique(np.quantile(s_all, np.linspace(0.5, 0.9999, 2000)))
    best = (-1, None)
    for t in cand:
        pr = s_all >= t; tp = (pr & y_all).sum(); fp = (pr & ~y_all).sum(); fn = (~pr & y_all).sum()
        f1 = 2 * tp / (2 * tp + fp + fn) if tp else 0.0
        if f1 > best[0]: best = (f1, float(t))
    sel = {'F1 comparator': best[1], **{f'Nominal {int(100 * p)}%': thresholds[p] for p in PHIS}}
    q = {'analyzer': 1, 'flow_pressure': 2, 'level_state': 3}
    rng = np.random.default_rng(seed)
    out = []
    for name, thr in sel.items():
        det_held = np.array([bool((scores[e['id']][window_labels(ends, e)] >= thr).any()) for e in held])
        w = np.array([q[e['class']] for e in held], float)
        wr = float((w * det_held).sum() / w.sum()); D = 1 - wr; rci = 0.430 + 0.20 * D
        k = int(det_held.sum())
        # event-level bootstrap of the provisional level
        idx = rng.integers(0, len(held), size=(n_boot, len(held)))
        wr_b = (w[idx] * det_held[idx]).sum(1) / w[idx].sum(1)
        lv = np.array([level_eq15(0.430 + 0.20 * (1 - x)) for x in wr_b])
        freq = {LEVEL_NAME[l]: float((lv == l).mean()) for l in sorted(set(lv.tolist()), reverse=True)}
        out.append(dict(selection=name, threshold=thr, detected=k, events=len(held), weighted_recall=wr, D=D, R_CI=rci,
                        provisional_level=LEVEL_NAME[level_eq15(rci)], cp95=clopper_pearson(k, len(held)),
                        untouched_target_flag_rate=float((tgt_scores >= thr).mean()), bootstrap_level_freq=freq,
                        detected_ids=[e['id'] for e, d in zip(held, det_held) if d],
                        f1_calibration=best[0] if name == 'F1 comparator' else None))
    return out


# ----------------------------------------------------------------------------------------------- figure
def figure5(rows, seg_rows, path):
    """Figure 5: calibration and target flag rates (training-referenced), block-basis Wilson intervals,
    with the segment-wise target rates of the same detector for comparison."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    x = np.arange(len(rows)); w = 0.36
    cal = [100 * r['cal_rate'] for r in rows]; tgt = [100 * r['tgt_rate'] for r in rows]
    lo = [100 * (r['tgt_rate'] - r['ci_blocks'][0]) for r in rows]; hi = [100 * (r['ci_blocks'][1] - r['tgt_rate']) for r in rows]
    ax.bar(x - w / 2 - 0.02, cal, w, color='#bfbfbf', zorder=2)
    ax.bar(x + w / 2 + 0.02, tgt, w, color='#3182bd', zorder=2)
    ax.errorbar(x + w / 2 + 0.02, tgt, yerr=[lo, hi], fmt='none', ecolor='black', capsize=6, lw=1.2, zorder=3)
    ax.scatter(x + w / 2 + 0.02, [100 * r['tgt_rate'] for r in seg_rows], marker='D', s=36, facecolors='white',
               edgecolors='black', zorder=4)
    for i, r in enumerate(rows):
        ax.hlines(100 * r['phi'], i - 0.45, i + 0.45, colors='#d62728', linestyles='dashed', lw=1.5, zorder=3)
    ax.set_xticks(x); ax.set_xticklabels([f"Nominal {int(100 * r['phi'])}%" for r in rows], fontsize=11)
    ax.set_ylabel('Window-level flag rate (%)', fontsize=11)
    ax.set_ylim(0, max(100 * r['ci_blocks'][1] for r in rows) * 1.08)
    ax.grid(axis='y', color='#e5e5e5', zorder=0)
    handles = [Line2D([0], [0], color='#d62728', ls='--', lw=1.5), Patch(color='#bfbfbf'), Patch(color='#3182bd'),
               Line2D([0], [0], color='black', marker='_', ms=10, lw=1.2),
               Line2D([0], [0], marker='D', color='w', markerfacecolor='white', markeredgecolor='black', ms=6)]
    ax.legend(handles, ['Nominal budget', '19 Feb calibration', '20 Feb target', f'Wilson 95% (n_eff = 485)',
                        '20 Feb target, segment-wise form'], fontsize=8.5, loc='upper left')
    fig.tight_layout()
    for ext in ('png', 'pdf'):
        fig.savefig(f'{path}.{ext}', dpi=300)
    plt.close(fig)


# ----------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', default=str(ROOT / 'data/private/swat_a11'))
    ap.add_argument('--out-dir', default=str(ROOT / 'results/swat_a11'))
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--seeds', type=int, default=20, help='additional detector seeds 1..N for sensitivity')
    ap.add_argument('--bootstrap', type=int, default=10000)
    a = ap.parse_args()
    t0 = time.time()
    data_dir, out = Path(a.data_dir), Path(a.out_dir)
    if not (data_dir / FILE_A).exists():
        print('SWaT A11 files not found in', data_dir, '- the data are restricted and are not redistributed.', file=sys.stderr)
        return 2
    out.mkdir(parents=True, exist_ok=True)
    spec_path = HERE / 'a11_constructed_events.json'
    spec = json.loads(spec_path.read_text())
    Xa, Xb, var = prepare(data_dir)
    Fa, ea = features(Xa); Fb, eb = features(Xb)
    cut = int(len(Xa) * TRAIN_FRAC); tr = ea < cut
    keep = [c for c in Fa.columns if Fa.loc[tr, c].nunique() > 1]
    Ftrain, Fcal, Ftgt = Fa.loc[tr, keep].to_numpy(), Fa.loc[~tr, keep].to_numpy(), Fb[keep].to_numpy()
    n_blocks = len(Ftgt) // (L // STEP)   # non-overlapping 60 s blocks: 5821 // 12 = 485 (Section 3.13)
    sd = Xa.iloc[:cut].std()
    # perturbed copies (features only)
    events = [dict(e, duration_s=spec['duration_s']) for e in spec['events']]
    copies = {e['id']: features(perturb(Xb, e, sd))[0] for e in events}

    res = dict(meta=dict(
        inputs={f: hashlib.sha256((data_dir / f).read_bytes()).hexdigest() for f in (FILE_A, FILE_B)},
        event_spec_sha256=hashlib.sha256(spec_path.read_bytes()).hexdigest(),
        python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__,
        sklearn=__import__('sklearn').__version__, seed=a.seed,
        variables=len(var), features=len(keep), records=[len(Xa), len(Xb)],
        windows=dict(train=int(tr.sum()), calibration=int((~tr).sum()), target=len(Ftgt)), blocks=n_blocks))

    for form in ('training', 'segment'):
        det = Detector(Ftrain, a.seed, form)
        rows, acal, atgt = transfer(det, Fcal, Ftgt, n_blocks)
        res[f'transfer_{form}'] = rows
        if form == 'training':
            thr = {r['phi']: r['threshold'] for r in rows}
            res['challenge_training'] = challenge(det, copies, eb, events, keep, thr, atgt, a.bootstrap, a.seed)
    figure5(res['transfer_training'], res['transfer_segment'], str(out / 'figure_5_a11_flag_rates'))

    # detector-seed sensitivity
    sens = []
    for s in range(1, a.seeds + 1):
        for form in ('training', 'segment'):
            det = Detector(Ftrain, s, form)
            rows, acal, atgt = transfer(det, Fcal, Ftgt, n_blocks)
            rec = dict(seed=s, form=form, **{f'tgt_rate_{int(100 * r["phi"])}': r['tgt_rate'] for r in rows},
                       **{f'distinguishable_{int(100 * r["phi"])}': r['exceedance_distinguishable_blocks'] for r in rows})
            if form == 'training':
                thr = {r['phi']: r['threshold'] for r in rows}
                ch = challenge(det, copies, eb, events, keep, thr, atgt, 1, s)
                for c in ch:
                    rec[f"detected_{c['selection'].replace(' ', '_').replace('%', '')}"] = c['detected']
            sens.append(rec)
    pd.DataFrame(sens).to_csv(out / 'a11_seed_sensitivity.csv', index=False)
    res['runtime_s'] = round(time.time() - t0, 1)
    (out / 'a11_results.json').write_text(json.dumps(res, indent=2))
    tab11 = pd.DataFrame([dict(form=f, budget=f"{int(100 * r['phi'])}%", cal_rate=round(100 * r['cal_rate'], 2),
                               tgt_rate=round(100 * r['tgt_rate'], 2), ci_windows='%.2f–%.2f' % tuple(100 * np.array(r['ci_windows'])),
                               ci_blocks='%.2f–%.2f' % tuple(100 * np.array(r['ci_blocks'])),
                               distinguishable=r['exceedance_distinguishable_blocks'])
                          for f in ('training', 'segment') for r in res[f'transfer_{f}']])
    tab11.to_csv(out / 'table_11.csv', index=False)
    tab12 = pd.DataFrame([dict(selection=c['selection'], events=f"{c['detected']}/{c['events']}",
                               weighted_recall=round(c['weighted_recall'], 2), D=round(c['D'], 2), R_CI=round(c['R_CI'], 3),
                               level=c['provisional_level'], cp95='%.2f–%.2f' % tuple(c['cp95']),
                               target_flag_rate=round(100 * c['untouched_target_flag_rate'], 2))
                          for c in res['challenge_training']])
    tab12.to_csv(out / 'table_12.csv', index=False)
    print(tab11.to_string(index=False)); print(tab12.to_string(index=False))
    print(json.dumps(res['meta'], indent=1)); print('runtime', res['runtime_s'], 's')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
