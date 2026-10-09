#!/usr/bin/env python3
"""Corrected, chronologically held-out labeled-attack evaluation on HAI 21.03.

Implements Sections 3.13 and 3.15 of the RDFR-CI manuscript (revision 3) and resolves the
two consistency-check findings on the previous revision:

  CC1  The robust logistic transform of Equation (14) now uses the median and MAD of the
       raw Isolation Forest scores of the TRAINING segment for every scored partition.
       The segment-wise variant of public release v1.3.0 (median/MAD recomputed on each
       scored array) is reported only as a sensitivity analysis.
  CC2  In the public HAI 21.03 files, the first 12 h of test3 (2020-07-13 00:00:00 to
       12:00:00, 43,201 rows) duplicate the last 12 h of train1, i.e. the calibration
       segment. Held-out evaluation therefore uses test3 from 2020-07-13 12:00:01 onwards.
       Windows are computed inside each partition, so no window support crosses a
       partition boundary. test4 and test5 are added as later held-out periods.

Usage:
    python hai_evaluation.py --data-dir /path/to/hai/hai-21.03 --out-dir results/hai

Data: https://github.com/icsdataset/hai (hai-21.03, CC BY-SA 4.0). Nothing is redistributed.
"""
from __future__ import annotations
import argparse, json, os, platform, hashlib
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
from scipy.stats import beta, norm
import sklearn
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

L, STEP = 60, 5                      # window length and step in seconds (Eq. 13)
BUDGETS = (0.01, 0.05, 0.10)
TRAIN_FRACTION = 0.80
HELD_OUT_START = np.datetime64('2020-07-13T12:00:01')   # first second after train1 ends
MERGE_GAP = 60                       # flagged attack-free windows < 60 s apart form one alarm episode
BLOCK_SECONDS = 300                  # moving-block bootstrap block length
N_BOOT = 10_000
BANDS = (0.20, 0.35, 0.50, 0.65)     # Table 6
LEVEL_NAME = {4: 'Bounded automation', 3: 'Human-approved intervention', 2: 'Assisted defense',
              1: 'Shadow/restricted', 0: 'Rollback/isolation'}


# ----------------------------------------------------------------------------- data
def read_file(data_dir, name):
    df = pd.read_csv(os.path.join(data_dir, name + '.csv.gz'))
    t = pd.to_datetime(df.iloc[:, 0]).to_numpy().astype('datetime64[s]')
    lab = df['attack'].to_numpy(dtype=np.int8)
    cols = [c for c in df.columns[1:] if not c.startswith('attack')]
    return t, lab, df[cols].to_numpy(dtype=np.float64), cols


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def window_features(X, lab):
    """Trailing windows W(t) = {t-L+1, ..., t} with end points every STEP seconds (Eq. 13)."""
    n = X.shape[0]
    ends = np.arange(L - 1, n, STEP)
    mean = np.empty((len(ends), X.shape[1])); sd = np.empty_like(mean)
    for j in range(X.shape[1]):
        w = sliding_window_view(X[:, j], L)[::STEP]
        mean[:, j] = w.mean(axis=1); sd[:, j] = w.std(axis=1, ddof=1)
    delta = X[ends] - X[ends - L + 1]
    cl = np.r_[0, np.cumsum(lab)]
    w_attack = (cl[ends + 1] - cl[ends + 1 - L]) > 0     # window contains >= 1 attack-labeled second
    return ends, np.hstack([mean, sd, delta]), w_attack


def episodes(lab):
    start = np.where(np.diff(np.r_[0, lab]) == 1)[0]
    end = np.where(np.diff(np.r_[lab, 0]) == -1)[0]
    return list(zip(start.tolist(), end.tolist()))


# ----------------------------------------------------------------------------- statistics
def wilson(p, n, conf=0.95):
    """Wilson score interval for a proportion p observed on n (effective) trials."""
    if n == 0:
        return (float('nan'), float('nan'))
    z = norm.ppf(1 - (1 - conf) / 2)
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


def clopper_pearson(k, n, conf=0.95):
    a = 1 - conf
    lo = 0.0 if k == 0 else beta.ppf(a / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - a / 2, k + 1, n - k)
    return (float(lo), float(hi))


def moving_block_bootstrap(flags, block, n_boot, rng):
    """Percentile 95% interval of the mean of a dependent 0/1 series (Kuensch, 1989)."""
    n = len(flags)
    if n < block:
        return (float('nan'), float('nan'))
    nb = int(np.ceil(n / block))
    csum = np.r_[0, np.cumsum(flags)]
    starts = rng.integers(0, n - block + 1, size=(n_boot, nb))
    means = (csum[starts + block] - csum[starts]).sum(axis=1) / (nb * block)
    return (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))


def level_of(score):
    return 4 - int(np.searchsorted(BANDS, score, side='right'))


def r_ci(D):
    """Equation (15): assumed water-treatment context E=0.55, A=0.30, F=0.25, C=0.90."""
    return 0.430 + 0.20 * D


# ----------------------------------------------------------------------------- detector
def logistic(r, m, mad):
    return 1.0 / (1.0 + np.exp(-(r - m) / (1.4826 * mad)))


def med_mad(r):
    m = float(np.median(r))
    return m, float(np.median(np.abs(r - m))) + 1e-9


def budget_threshold(a_cal, phi):
    """Smallest threshold whose calibration flag rate (a >= threshold) does not exceed phi."""
    s = np.sort(a_cal)[::-1]
    k = int(np.floor(phi * len(s) + 1e-9))          # number of windows that may be flagged
    while k > 0 and k < len(s) and s[k] == s[k - 1]:  # do not split ties
        k -= 1
    return float(s[k - 1]) if k > 0 else float(np.nextafter(s[0], np.inf))


def f1_threshold(a, y):
    """Threshold maximising pointwise F1 (window end-point labels) on the selection data."""
    order = np.argsort(-a, kind='stable')
    a_s, y_s = a[order], y[order].astype(int)
    tp = np.cumsum(y_s); fp = np.cumsum(1 - y_s)
    f1 = 2 * tp / (2 * tp + fp + (y_s.sum() - tp))
    last = np.r_[a_s[1:] != a_s[:-1], True]           # evaluate only at distinct score values
    idx = np.where(last)[0]
    best = idx[np.argmax(f1[idx])]
    return float(a_s[best]), float(f1[best])


def evaluate(a, part, thr, rng):
    ends, w_attack, lab = part['ends'], part['w_attack'], part['lab']
    flag = a >= thr
    free = ~w_attack
    n_free = int(free.sum()); k_free = int(flag[free].sum())
    n_eff = n_free // (L // STEP)
    fpr = k_free / n_free
    det, delays = [], []
    for s, e in episodes(lab):
        hit = np.where((ends >= s) & (ends <= e) & flag)[0]
        det.append(bool(len(hit)))
        if len(hit):
            delays.append(float(ends[hit[0]] - s))
    n_ep, k_ep = len(det), int(sum(det))
    end_attack = lab[ends] == 1
    point_recall = float(flag[end_attack].mean()) if end_attack.any() else float('nan')
    ft = ends[free & flag]
    alarms = 0 if len(ft) == 0 else 1 + int((np.diff(ft) >= MERGE_GAP).sum())
    hours = n_free * STEP / 3600.0
    D = 1 - k_ep / n_ep if n_ep else float('nan')
    cp = clopper_pearson(k_ep, n_ep) if n_ep else (float('nan'), float('nan'))
    out = dict(windows=int(len(a)), attack_free_windows=n_free, n_eff_blocks=int(n_eff), attack_free_hours=hours,
               fpr=fpr, fpr_wilson_block=wilson(fpr, n_eff), fpr_wilson_window=wilson(fpr, n_free),
               fpr_mbb=moving_block_bootstrap(flag[free].astype(float), BLOCK_SECONDS // STEP, N_BOOT, rng),
               episodes=n_ep, episodes_detected=k_ep, episode_recall_cp=cp, episode_detected_flags=det,
               point_recall=point_recall, median_delay_s=float(np.median(delays)) if delays else float('nan'),
               false_alarm_episodes=alarms, alarms_per_hour=alarms / hours, D=D, R_CI=r_ci(D),
               level=level_of(r_ci(D)), R_CI_at_lower_recall=r_ci(1 - cp[0]), level_at_lower_recall=level_of(r_ci(1 - cp[0])))
    if n_ep:
        d = np.asarray(det, float)
        rec = d[rng.integers(0, n_ep, size=(N_BOOT, n_ep))].mean(axis=1)
        lv = np.array([level_of(r_ci(1 - x)) for x in np.unique(rec)])
        freq = {}
        for u, l in zip(np.unique(rec), lv):
            freq[int(l)] = freq.get(int(l), 0.0) + float((rec == u).mean())
        out['episode_bootstrap_level_freq'] = freq
    return out


def pool(parts_a, parts, thr, rng):
    """Pool several held-out partitions (concatenated in time order, episodes kept intact)."""
    off = 0; ends, wa, labs, aa = [], [], [], []
    for a, p in zip(parts_a, parts):
        ends.append(p['ends'] + off); wa.append(p['w_attack']); labs.append(np.r_[p['lab'], np.zeros(MERGE_GAP + L, np.int8)])
        aa.append(a); off += len(p['lab']) + MERGE_GAP + L      # gap keeps alarms/episodes from merging across files
    part = dict(ends=np.concatenate(ends), w_attack=np.concatenate(wa), lab=np.concatenate(labs))
    return evaluate(np.concatenate(aa), part, thr, rng)


# ----------------------------------------------------------------------------- main
def run(data_dir, seed=42, verbose=True):
    rng = np.random.default_rng(seed)
    raw_files = {n: read_file(data_dir, n) for n in ['train1', 'test1', 'test2', 'test3', 'test4', 'test5']}
    t1, lab1, X1, cols = raw_files['train1']
    cut = int(len(X1) * TRAIN_FRACTION)

    # --- partitions -----------------------------------------------------------------
    seg = {'training': (t1[:cut], lab1[:cut], X1[:cut]), 'calibration': (t1[cut:], lab1[cut:], X1[cut:])}
    t3, lab3, X3, _ = raw_files['test3']
    keep3 = t3 >= HELD_OUT_START
    seg['test3_overlap_excluded'] = (t3[~keep3], lab3[~keep3], X3[~keep3])
    seg['heldout_test3'] = (t3[keep3], lab3[keep3], X3[keep3])
    for n in ['test1', 'test2', 'test4', 'test5']:
        t, lab, X, _ = raw_files[n]
        if n == 'test2':                 # its last row (2020-07-11 00:00:00) is also the first row of train1
            dup = t >= t1[0]
            t, lab, X = t[~dup], lab[~dup], X[~dup]
        seg[('f1sel_' if n in ('test1', 'test2') else 'heldout_') + n] = (t, lab, X)
    seg['test3_full_uncorrected'] = (t3, lab3, X3)

    # --- duplicate-observation check against training + calibration (all of train1) --
    def row_keys(t, X):
        return pd.util.hash_pandas_object(pd.DataFrame(np.column_stack([t.astype('int64'), X])), index=False).to_numpy()
    ref_t = set(t1.astype('int64').tolist()); ref_rows = set(row_keys(t1, X1).tolist())
    table = []
    for name, (t, lab, X) in seg.items():
        n_win = max(0, (len(t) - L) // STEP + 1)
        shared_t = int(np.isin(t.astype('int64'), list(ref_t)).sum()) if name not in ('training', 'calibration') else None
        shared_r = int(np.isin(row_keys(t, X), list(ref_rows)).sum()) if name not in ('training', 'calibration') else None
        table.append(dict(partition=name, first=str(t[0]), last=str(t[-1]), rows=int(len(t)), hours=len(t) / 3600.0,
                          windows=int(n_win), first_window_end=str(t[L - 1]), last_window_end=str(t[L - 1 + (n_win - 1) * STEP]),
                          attack_seconds=int(lab.sum()), attack_episodes=len(episodes(lab)),
                          timestamps_shared_with_train1=shared_t, identical_rows_shared_with_train1=shared_r))

    # --- features, scaler, detector --------------------------------------------------
    feats = {}
    for name, (t, lab, X) in seg.items():
        ends, F, wa = window_features(X, lab)
        feats[name] = dict(ends=ends, F=F, w_attack=wa, lab=lab, t=t)
    Ftr = feats['training']['F']
    keep = (Ftr.max(axis=0) - Ftr.min(axis=0)) > 0          # drop features constant on the training segment
    scaler = StandardScaler().fit(Ftr[:, keep])
    model = IsolationForest(n_estimators=300, contamination='auto', random_state=seed, n_jobs=-1).fit(scaler.transform(Ftr[:, keep]))
    raw = {name: -model.score_samples(scaler.transform(f['F'][:, keep])) for name, f in feats.items()}

    m_tr, mad_tr = med_mad(raw['training'])
    res = dict(meta=dict(seed=seed, variables=len(cols), features=int(keep.sum()), window_s=L, step_s=STEP,
                         training_windows=int(len(raw['training'])), calibration_windows=int(len(raw['calibration'])),
                         median_train=m_tr, mad_train=mad_tr, held_out_start=str(HELD_OUT_START),
                         python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__, sklearn=sklearn.__version__),
               partitions=table, results={})

    held = ['heldout_test3', 'heldout_test4', 'heldout_test5']
    for variant in ['training_statistics_eq14', 'segment_wise_v1_3_0']:
        if variant == 'training_statistics_eq14':
            a = {k: logistic(v, m_tr, mad_tr) for k, v in raw.items()}
        else:                                               # sensitivity: statistics of the scored array (release v1.3.0)
            a = {k: logistic(v, *med_mad(v)) for k, v in raw.items()}
        a_sel = np.concatenate([a['f1sel_test1'], a['f1sel_test2']])
        y_sel = np.concatenate([feats[n]['lab'][feats[n]['ends']] == 1 for n in ('f1sel_test1', 'f1sel_test2')])  # end-point labels
        thr_f1, f1_val = f1_threshold(a_sel, y_sel)
        ops = {'F1 comparator': thr_f1}
        ops.update({f'Nominal {int(100 * phi)}%': budget_threshold(a['calibration'], phi) for phi in BUDGETS})
        vres = {}
        for op, thr in ops.items():
            r = dict(threshold=thr, calibration_flag_rate=float((a['calibration'] >= thr).mean()))
            if op == 'F1 comparator':
                r['selection_f1'] = f1_val
            for name in held + ['f1sel_test1', 'f1sel_test2', 'test3_full_uncorrected', 'test3_overlap_excluded']:
                if name == 'test3_overlap_excluded':
                    r[name] = dict(flag_rate=float((a[name] >= thr).mean()), windows=int(len(a[name])))
                else:
                    r[name] = evaluate(a[name], feats[name], thr, rng)
            r['heldout_pooled'] = pool([a[n] for n in held], [feats[n] for n in held], thr, rng)
            r['f1sel_pooled'] = pool([a[n] for n in ['f1sel_test1', 'f1sel_test2']], [feats[n] for n in ['f1sel_test1', 'f1sel_test2']], thr, rng)
            vres[op] = r
        res['results'][variant] = vres
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--data-dir', required=True); ap.add_argument('--out-dir', default='results/hai')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--seed-sensitivity', type=int, default=0, help='number of additional detector seeds (0 = skip)')
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    res = run(args.data_dir, args.seed)
    res['meta']['file_sha256'] = {n: sha256(os.path.join(args.data_dir, n + '.csv.gz')) for n in ['train1', 'test1', 'test2', 'test3', 'test4', 'test5']}
    json.dump(res, open(os.path.join(args.out_dir, 'hai_results.json'), 'w'), indent=1, default=float)
    pd.DataFrame(res['partitions']).to_csv(os.path.join(args.out_dir, 'hai_partitions.csv'), index=False)
    rows = []
    for variant, vres in res['results'].items():
        for op, r in vres.items():
            for part in ['heldout_test3', 'heldout_test4', 'heldout_test5', 'heldout_pooled', 'f1sel_pooled', 'test3_full_uncorrected']:
                e = r[part]
                rows.append(dict(variant=variant, operating_point=op, partition=part, threshold=r['threshold'],
                                 cal_rate_pct=100 * r['calibration_flag_rate'], attack_free_windows=e['attack_free_windows'],
                                 n_eff=e['n_eff_blocks'], attack_free_hours=e['attack_free_hours'], fpr_pct=100 * e['fpr'],
                                 wilson_lo=100 * e['fpr_wilson_block'][0], wilson_hi=100 * e['fpr_wilson_block'][1],
                                 mbb_lo=100 * e['fpr_mbb'][0], mbb_hi=100 * e['fpr_mbb'][1],
                                 episodes=f"{e['episodes_detected']}/{e['episodes']}", cp_lo=e['episode_recall_cp'][0], cp_hi=e['episode_recall_cp'][1],
                                 point_recall=e['point_recall'], median_delay_s=e['median_delay_s'],
                                 false_alarm_episodes=e['false_alarm_episodes'], alarms_per_hour=e['alarms_per_hour'],
                                 D=e['D'], R_CI=e['R_CI'], level=e['level'], R_CI_at_lower_recall=e['R_CI_at_lower_recall'],
                                 level_at_lower_recall=e['level_at_lower_recall'],
                                 boot_level_freq=json.dumps(e.get('episode_bootstrap_level_freq', {}))))
    pd.DataFrame(rows).to_csv(os.path.join(args.out_dir, 'hai_operating_points.csv'), index=False)
    if args.seed_sensitivity:
        srows = []
        for s in range(1, args.seed_sensitivity + 1):
            r = run(args.data_dir, s, verbose=False)['results']['training_statistics_eq14']
            for op, v in r.items():
                for part in ['heldout_test3', 'heldout_test4', 'heldout_test5', 'heldout_pooled']:
                    e = v[part]
                    srows.append(dict(seed=s, operating_point=op, partition=part, fpr_pct=100 * e['fpr'],
                                      wilson_lo=100 * e['fpr_wilson_block'][0], episodes_detected=e['episodes_detected'], episodes=e['episodes']))
            print('seed', s, 'done', flush=True)
        pd.DataFrame(srows).to_csv(os.path.join(args.out_dir, 'hai_seed_sensitivity.csv'), index=False)
    print(pd.DataFrame(res['partitions']).to_string())
    print(pd.DataFrame(rows).drop(columns=['boot_level_freq']).round(3).to_string())


if __name__ == '__main__':
    main()
