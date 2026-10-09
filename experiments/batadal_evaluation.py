#!/usr/bin/env python3
"""BATADAL (C-Town) second-system evaluation, implementing Sections B-C of PREREGISTRATION.md.

The detector-to-authority protocol of the HAI evaluation (Sections 3.13, 3.15) adapted only for hourly sampling:
24 h trailing windows with a 1 h step, mean / standard deviation / end-to-end delta features, scaler and
detectors fitted on the first 80% of training set 1, budgets selected on its last 20%, training-referenced
Equation (14) (segment-wise form as sensitivity), Equation (15) for R_CI, and pre-specified predictions P1-P3.

Usage (from the repository root):
    python experiments/batadal_evaluation.py --data-dir data/batadal/raw --attacks data/batadal/batadal_attacks.csv --out-dir results/batadal --seeds 20
"""
from __future__ import annotations
import argparse, json, os, platform, hashlib
import numpy as np, pandas as pd, sklearn
from numpy.lib.stride_tricks import sliding_window_view
from scipy.stats import beta, norm
from sklearn.ensemble import IsolationForest
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

STEP, BUDGETS, TRAIN_FRACTION, BLOCK_H, N_BOOT = 1, (0.01, 0.05, 0.10), 0.80, 120, 10_000
BANDS = (0.20, 0.35, 0.50, 0.65)
BLOCK = 24                           # non-overlapping 24 h blocks for the Wilson interval, for every window length
FILES = {'train1': 'BATADAL_dataset03.csv', 'train2': 'BATADAL_dataset04.csv', 'test': 'BATADAL_test_dataset.csv'}


def sha256(p):
    h = hashlib.sha256(); h.update(open(p, 'rb').read()); return h.hexdigest()


def read(data_dir, name, attacks):
    df = pd.read_csv(os.path.join(data_dir, FILES[name])); df.columns = [c.strip() for c in df.columns]
    t = pd.to_datetime(df['DATETIME'], format='%d/%m/%y %H').to_numpy().astype('datetime64[h]')
    assert np.all(np.diff(t).astype(int) == 1), name + ': non-uniform sampling'
    cols = [c for c in df.columns if c not in ('DATETIME', 'ATT_FLAG')]
    lab = np.zeros(len(t), np.int8)
    for _, a in attacks[attacks.dataset == name].iterrows():                  # start inclusive, end exclusive
        lab[(t >= np.datetime64(a.start, 'h')) & (t < np.datetime64(a.end, 'h'))] = 1
    return t, lab, df[cols].to_numpy(np.float64), cols


def features(X, lab, L):
    ends = np.arange(L - 1, len(X), STEP)
    mean = np.empty((len(ends), X.shape[1])); sd = np.empty_like(mean)
    for j in range(X.shape[1]):
        w = sliding_window_view(X[:, j], L)[::STEP]; mean[:, j] = w.mean(1); sd[:, j] = w.std(1, ddof=1)
    cl = np.r_[0, np.cumsum(lab)]
    return ends, np.hstack([mean, sd, X[ends] - X[ends - L + 1]]), (cl[ends + 1] - cl[ends + 1 - L]) > 0


def episodes(lab):
    s = np.where(np.diff(np.r_[0, lab]) == 1)[0]; e = np.where(np.diff(np.r_[lab, 0]) == -1)[0]
    return list(zip(s.tolist(), e.tolist()))


def wilson(p, n, z=norm.ppf(0.975)):
    if n == 0: return (np.nan, np.nan)
    den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (float(c - h), float(c + h))


def cp(k, n):
    return (0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k)))


def mbb(flags, block, rng):
    n = len(flags)
    if n < block: return (np.nan, np.nan)
    nb = int(np.ceil(n / block)); cs = np.r_[0, np.cumsum(flags)]
    st = rng.integers(0, n - block + 1, size=(N_BOOT, nb)); m = (cs[st + block] - cs[st]).sum(1) / (nb * block)
    return (float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5)))


def level_of(r): return 4 - int(np.searchsorted(BANDS, r, side='right'))
def r_ci(D): return 0.430 + 0.20 * D
def logistic(r, m, mad): return 1 / (1 + np.exp(-(r - m) / (1.4826 * mad)))
def med_mad(r):
    m = float(np.median(r)); return m, float(np.median(np.abs(r - m))) + 1e-12


def budget_threshold(a, phi):
    s = np.sort(a)[::-1]; k = int(np.floor(phi * len(s) + 1e-9))
    while 0 < k < len(s) and s[k] == s[k - 1]: k -= 1
    return float(s[k - 1]) if k > 0 else float(np.nextafter(s[0], np.inf))


def f1_threshold(a, y):
    o = np.argsort(-a, kind='stable'); a_s, y_s = a[o], y[o].astype(int)
    tp = np.cumsum(y_s); fp = np.cumsum(1 - y_s); f1 = 2 * tp / (2 * tp + fp + (y_s.sum() - tp))
    idx = np.where(np.r_[a_s[1:] != a_s[:-1], True])[0]; b = idx[np.argmax(f1[idx])]
    return float(a_s[b]), float(f1[b])


def free_rate(a, part, thr, L, rng):
    free = ~part['w_attack']; fl = (a >= thr)[free]
    n = int(free.sum()); neff = n // BLOCK; p = float(fl.mean())
    return dict(attack_free_windows=n, n_eff=neff, hours=n * STEP, rate=p, wilson_block=wilson(p, neff), mbb=mbb(fl.astype(float), BLOCK_H, rng))


def evaluate(a, part, thr, L, rng):
    ends, lab = part['ends'], part['lab']; flag = a >= thr
    out = free_rate(a, part, thr, L, rng)
    det, delay = [], []
    for s, e in episodes(lab):
        hit = np.where((ends >= s) & (ends <= e) & flag)[0]; det.append(bool(len(hit)))
        if len(hit): delay.append(float(ends[hit[0]] - s))
    n, k = len(det), int(sum(det)); D = 1 - k / n; c = cp(k, n)
    d = np.asarray(det, float); rec = d[rng.integers(0, n, size=(N_BOOT, n))].mean(1)
    freq = {}
    for u in np.unique(rec): freq[level_of(r_ci(1 - u))] = freq.get(level_of(r_ci(1 - u)), 0) + float((rec == u).mean())
    out.update(episodes=n, detected=k, detected_flags=det, recall_cp=c, median_delay_h=float(np.median(delay)) if delay else np.nan,
               delays_h=delay, D=D, R_CI=r_ci(D), level=level_of(r_ci(D)), R_CI_at_lower_recall=r_ci(1 - c[0]), level_at_lower_recall=level_of(r_ci(1 - c[0])),
               boot_level_freq=freq)
    return out


def build(data_dir, attacks, L):
    raw = {n: read(data_dir, n, attacks) for n in FILES}
    assert raw['train1'][3] == raw['train2'][3] == raw['test'][3]
    t1, l1, X1, cols = raw['train1']; cut = int(len(X1) * TRAIN_FRACTION)
    seg = {'training': (t1[:cut], l1[:cut], X1[:cut]), 'calibration': (t1[cut:], l1[cut:], X1[cut:]),
           'train2': raw['train2'][:3], 'test': raw['test'][:3]}
    def keys(X): return set(pd.util.hash_pandas_object(pd.DataFrame(X), index=False).tolist())
    k1 = keys(X1); table = []
    for n, (t, lab, X) in seg.items():
        nw = len(t) - L + 1
        table.append(dict(partition=n, first=str(t[0]), last=str(t[-1]), records=len(t), windows=nw,
                          first_window_end=str(t[L - 1]), last_window_end=str(t[-1]), attack_hours=int(lab.sum()), attacks=len(episodes(lab)),
                          identical_value_rows_shared_with_train1=(None if n in ('training', 'calibration') else
                                                                   int(len(keys(X) & k1))),
                          timestamps_shared_with_train1=(None if n in ('training', 'calibration') else int(np.isin(t, t1).sum()))))
    feats = {}
    for n, (t, lab, X) in seg.items():
        e, F, wa = features(X, lab, L); feats[n] = dict(ends=e, F=F, w_attack=wa, lab=lab, t=t)
    return feats, table, cols


def raw_scores(feats, detector, seed):
    Ftr = feats['training']['F']; keep = (Ftr.max(0) - Ftr.min(0)) > 0
    sc = StandardScaler().fit(Ftr[:, keep]); Z = {n: sc.transform(f['F'][:, keep]) for n, f in feats.items()}
    if detector == 'isolation_forest':
        m = IsolationForest(n_estimators=300, contamination='auto', random_state=seed, n_jobs=-1).fit(Z['training'])
        return {n: -m.score_samples(z) for n, z in Z.items()}, int(keep.sum())
    m = MLPRegressor(hidden_layer_sizes=(64, 16, 64), activation='relu', solver='adam', max_iter=500, early_stopping=True,
                     random_state=seed).fit(Z['training'], Z['training'])
    return {n: ((m.predict(z) - z) ** 2).mean(1) for n, z in Z.items()}, int(keep.sum())


def run(feats, detector, seed, L, variants=('training_referenced', 'segment_wise')):
    rng = np.random.default_rng(seed); raw, nf = raw_scores(feats, detector, seed); m0, s0 = med_mad(raw['training'])
    res = {}
    for v in variants:
        a = {k: logistic(r, m0, s0) for k, r in raw.items()} if v == 'training_referenced' else {k: logistic(r, *med_mad(r)) for k, r in raw.items()}
        y2 = feats['train2']['lab'][feats['train2']['ends']] == 1
        thr_f1, f1v = f1_threshold(a['train2'], y2)
        ops = {'F1 comparator': thr_f1} | {f'Nominal {int(100 * p)}%': budget_threshold(a['calibration'], p) for p in BUDGETS}
        vr = {}
        for op, thr in ops.items():
            r = dict(threshold=thr, calibration_rate=float((a['calibration'] >= thr).mean()))
            r['test'] = evaluate(a['test'], feats['test'], thr, L, rng)
            r['later1_train2'] = free_rate(a['train2'], feats['train2'], thr, L, rng)
            r['later2_test'] = {k: r['test'][k] for k in ('attack_free_windows', 'n_eff', 'hours', 'rate', 'wilson_block', 'mbb')}
            fl = np.r_[(a['train2'] >= thr)[~feats['train2']['w_attack']], (a['test'] >= thr)[~feats['test']['w_attack']]]
            r['later_pooled'] = dict(hours=len(fl), rate=float(fl.mean()), wilson_block=wilson(float(fl.mean()), len(fl) // BLOCK))
            if op == 'F1 comparator': r['selection_f1'] = f1v
            vr[op] = r
        res[v] = vr
    return res, nf


def predictions(res, budgets=BUDGETS):
    tr, sw = res['training_referenced'], res['segment_wise']; out = {}
    for p in budgets:
        op = f'Nominal {int(100 * p)}%'; r = tr[op]
        exc = {k: bool(r[k]['rate'] > p and r[k]['wilson_block'][0] > p) for k in ('later1_train2', 'later2_test')}
        score_mech = r['test']['level'] <= 1
        out[op] = dict(P1_exceedance=exc, P1=any(exc.values()), P2_score_mechanism=score_mech, P2_gate_mechanism=any(exc.values()),
                       P2=bool(score_mech or any(exc.values())), final_level=min(r['test']['level'], 1) if any(exc.values()) else r['test']['level'],
                       P3=(bool(sw[op]['later_pooled']['rate'] < r['later_pooled']['rate']) if p in (0.05, 0.10) else None),
                       later_rate_trref=r['later_pooled']['rate'], later_rate_segwise=sw[op]['later_pooled']['rate'])
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--data-dir', required=True); ap.add_argument('--attacks', required=True)
    ap.add_argument('--out-dir', required=True); ap.add_argument('--seeds', type=int, default=0)
    ap.add_argument('--prereg', default='preregistration/batadal_ctown/PREREGISTRATION.md', help='pre-specified protocol (its SHA-256 is stored in the results)')
    a = ap.parse_args(); os.makedirs(a.out_dir, exist_ok=True)
    attacks = pd.read_csv(a.attacks)
    prereg = a.prereg
    meta = dict(prereg_sha256=sha256(prereg), python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__,
                sklearn=sklearn.__version__, files={n: sha256(os.path.join(a.data_dir, f)) for n, f in FILES.items()}, window_h=24, step_h=STEP)
    feats, table, cols = build(a.data_dir, attacks, 24)
    out = dict(meta=meta | dict(variables=len(cols)), partitions=table, primary={}, predictions={}, window_sensitivity={})
    for det in ('isolation_forest', 'autoencoder'):
        res, nf = run(feats, det, 42, 24); out['primary'][det] = res; out['predictions'][det] = predictions(res); out['meta'][f'features_{det}'] = nf
    for L in (12, 48):
        fL, _, _ = build(a.data_dir, attacks, L); res, _ = run(fL, 'isolation_forest', 42, L)
        out['window_sensitivity'][f'{L}h'] = dict(results=res, predictions=predictions(res))
    json.dump(out, open(os.path.join(a.out_dir, 'batadal_results.json'), 'w'), indent=1, default=float)
    pd.DataFrame(table).to_csv(os.path.join(a.out_dir, 'batadal_partitions.csv'), index=False)
    if a.seeds:
        rows = []
        for det in ('isolation_forest', 'autoencoder'):
            for s in range(1, a.seeds + 1):
                res, _ = run(feats, det, s, 24); pr = predictions(res)
                for op, r in res['training_referenced'].items():
                    e = r['test']; row = dict(detector=det, seed=s, operating_point=op, test_fpr=e['rate'], detected=e['detected'], attacks=e['episodes'],
                                              R_CI=e['R_CI'], level=e['level'], later1=r['later1_train2']['rate'], later1_lo=r['later1_train2']['wilson_block'][0],
                                              later2=r['later2_test']['rate'], later2_lo=r['later2_test']['wilson_block'][0],
                                              later_pooled_segwise=res['segment_wise'][op]['later_pooled']['rate'], later_pooled=r['later_pooled']['rate'])
                    if op in pr: row |= dict(P1=pr[op]['P1'], P2=pr[op]['P2'], P3=pr[op]['P3'], score_mech=pr[op]['P2_score_mechanism'], gate_mech=pr[op]['P2_gate_mechanism'])
                    rows.append(row)
                print(det, 'seed', s, flush=True)
        pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, 'batadal_seed_sensitivity.csv'), index=False)
    print(pd.DataFrame(table).to_string())
    for det in out['primary']:
        for v, vr in out['primary'][det].items():
            for op, r in vr.items():
                e = r['test']
                print(f"{det[:6]} {v[:8]} {op:14s} cal={100*r['calibration_rate']:.2f} testFPR={100*e['rate']:.2f}[{100*e['wilson_block'][0]:.2f}-{100*e['wilson_block'][1]:.2f}] "
                      f"det={e['detected']}/{e['episodes']} CP={e['recall_cp'][0]:.2f}-{e['recall_cp'][1]:.2f} delay={e['median_delay_h']}h RCI={e['R_CI']:.3f} L{e['level']} "
                      f"later1={100*r['later1_train2']['rate']:.2f}[{100*r['later1_train2']['wilson_block'][0]:.2f}] later2={100*r['later2_test']['rate']:.2f}[{100*r['later2_test']['wilson_block'][0]:.2f}]")
    print(json.dumps(out['predictions'], indent=1, default=float))


if __name__ == '__main__':
    main()
