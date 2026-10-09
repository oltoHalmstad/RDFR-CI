#!/usr/bin/env python3
"""Same-testbed replication of the HAI 21.03 evaluation (Sections 3.15 and 4.6) on HAI 22.04 and HAI 23.05.

The protocol is identical to experiments/hai_evaluation.py: Isolation Forest (300 trees) on 60 s windows with
a 5 s step, rolling mean / standard deviation / end-to-end delta features, a scaler fitted on the training
segment only, the training-referenced robust logistic transform of Equation (14), thresholds for nominal budgets
of 1%, 5% and 10% selected on a normal calibration segment, and held-out evaluation strictly after all training
and calibration data. Only the file roles differ, because the files of each release interleave in time:

  HAI 22.04  training/calibration: train1 (first 80% / last 20%; 11-12 July 2021)
             F1 selection: test1 (10 July 2021, precedes training)
             labeled held-out: test2, test3, test4 (13-17 July 2021)
             later attack-free periods: train2-train6 (17 July - 9 August 2021)
  HAI 23.05  training/calibration: hai-train1 (first 80% / last 20%; 4-8 August 2022)
             no labeled file precedes training, so the F1 comparator is selected on hai-test1 and
             evaluated on hai-test2 only; budget thresholds are evaluated on hai-test1 and hai-test2
             later attack-free periods: hai-train2, hai-train3, hai-train4 (13-25 August 2022)
             labels: label-test1/2 aligned by row (label-test2 timestamps are stored at minute resolution)

Usage: python hai_replication.py --version 22.04 --data-dir DIR --out-dir DIR [--seeds 20]
Data: https://github.com/icsdataset/hai (Git LFS files; CC BY-SA 4.0). Nothing is redistributed.
"""
from __future__ import annotations
import argparse, json, os, platform, sys
import numpy as np, pandas as pd, sklearn
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hai_evaluation as H

DESIGN = {
 '22.04': dict(train='train1', f1sel=['test1'], held=['test2', 'test3', 'test4'], f1_eval=['test2', 'test3', 'test4'],
               later=['train2', 'train3', 'train4', 'train5', 'train6'], files=lambda n: n + '.csv', labels=None),
 '23.05': dict(train='hai-train1', f1sel=['hai-test1'], held=['hai-test1', 'hai-test2'], f1_eval=['hai-test2'],
               later=['hai-train2', 'hai-train3', 'hai-train4'], files=lambda n: n + '.csv',
               labels={'hai-test1': 'label-test1.csv', 'hai-test2': 'label-test2.csv'}),
}


def read(data_dir, version, name):
    df = pd.read_csv(os.path.join(data_dir, DESIGN[version]['files'](name)))
    t = pd.to_datetime(df.iloc[:, 0]).to_numpy().astype('datetime64[s]')
    lab_col = [c for c in df.columns if c.lower() == 'attack']
    labels = DESIGN[version]['labels']
    if lab_col:
        lab = df[lab_col[0]].to_numpy(np.int8)
    elif labels and name in labels:
        lf = pd.read_csv(os.path.join(data_dir, labels[name]))
        assert len(lf) == len(df), (name, len(lf), len(df))
        lab = lf['label'].to_numpy(np.int8)
    else:
        lab = np.zeros(len(df), np.int8)            # training files of 23.05 carry no label column: normal operation
    cols = [c for c in df.columns[1:] if c.lower() not in ('attack', 'label') and not c.lower().startswith('attack_')]
    assert np.all(np.diff(t.astype('int64')) == 1), name + ': non-uniform sampling'
    return t, lab, df[cols].to_numpy(np.float64), cols


def build(version, data_dir):
    D = DESIGN[version]
    names = [D['train']] + D['f1sel'] + [h for h in D['held'] if h not in D['f1sel']] + D['later']
    raw = {n: read(data_dir, version, n) for n in dict.fromkeys(names)}
    cols0 = raw[D['train']][3]
    for n, r in raw.items(): assert r[3] == cols0, n + ': column mismatch'
    t1, lab1, X1, _ = raw[D['train']]
    cut = int(len(X1) * H.TRAIN_FRACTION)
    seg = {'training': (t1[:cut], lab1[:cut], X1[:cut]), 'calibration': (t1[cut:], lab1[cut:], X1[cut:])}
    for n in names[1:]: seg[n] = raw[n][:3]
    # duplicate-observation check against the training file (timestamps and identical rows)
    def keys(t, X): return pd.util.hash_pandas_object(pd.DataFrame(np.column_stack([t.astype('int64'), X])), index=False).to_numpy()
    def vkeys(X): return pd.util.hash_pandas_object(pd.DataFrame(X), index=False).to_numpy()
    ref_t = set(t1.astype('int64').tolist()); ref_r = set(keys(t1, X1).tolist()); ref_v = set(vkeys(X1).tolist())
    table = []
    for n, (t, lab, X) in seg.items():
        role = ('training' if n == 'training' else 'calibration' if n == 'calibration' else
                'F1 selection' if n in D['f1sel'] and n not in D['held'] else
                'held-out (F1 selection for comparator)' if n in D['f1sel'] else
                'labeled held-out' if n in D['held'] else 'later attack-free')
        nw = max(0, (len(t) - H.L) // H.STEP + 1)
        other = n not in ('training', 'calibration')
        table.append(dict(partition=n, role=role, first=str(t[0]), last=str(t[-1]), rows=int(len(t)), hours=len(t) / 3600,
                          windows=int(nw), first_window_end=str(t[H.L - 1]), last_window_end=str(t[H.L - 1 + (nw - 1) * H.STEP]),
                          attack_seconds=int(lab.sum()), attack_episodes=len(H.episodes(lab)),
                          timestamps_shared_with_train=int(np.isin(t.astype('int64'), list(ref_t)).sum()) if other else None,
                          identical_rows_shared_with_train=int(np.isin(keys(t, X), list(ref_r)).sum()) if other else None,
                          identical_values_shared_with_train=int(np.isin(vkeys(X), list(ref_v)).sum()) if other else None))
    feats = {}
    for n, (t, lab, X) in seg.items():
        ends, F, wa = H.window_features(X, lab)
        feats[n] = dict(ends=ends, F=F, w_attack=wa, lab=lab, t=t)
    return D, seg, feats, table, cols0


def score(feats, seed):
    Ftr = feats['training']['F']
    keep = (Ftr.max(axis=0) - Ftr.min(axis=0)) > 0
    sc = StandardScaler().fit(Ftr[:, keep])
    m = IsolationForest(n_estimators=300, contamination='auto', random_state=seed, n_jobs=-1).fit(sc.transform(Ftr[:, keep]))
    return {n: -m.score_samples(sc.transform(f['F'][:, keep])) for n, f in feats.items()}, int(keep.sum())


def evaluate_all(D, feats, raw, seed, variants=('training_statistics_eq14', 'segment_wise_v1_3_0')):
    rng = np.random.default_rng(seed)
    m_tr, mad_tr = H.med_mad(raw['training'])
    out = {}
    for variant in variants:
        a = ({k: H.logistic(v, m_tr, mad_tr) for k, v in raw.items()} if variant == 'training_statistics_eq14'
             else {k: H.logistic(v, *H.med_mad(v)) for k, v in raw.items()})
        a_sel = np.concatenate([a[n] for n in D['f1sel']])
        y_sel = np.concatenate([feats[n]['lab'][feats[n]['ends']] == 1 for n in D['f1sel']])
        thr_f1, f1v = H.f1_threshold(a_sel, y_sel)
        ops = {'F1 comparator': thr_f1}
        ops.update({f'Nominal {int(100 * p)}%': H.budget_threshold(a['calibration'], p) for p in H.BUDGETS})
        vres = {}
        for op, thr in ops.items():
            held = D['f1_eval'] if op == 'F1 comparator' else D['held']
            r = dict(threshold=thr, calibration_flag_rate=float((a['calibration'] >= thr).mean()), evaluated_on=held)
            for n in D['held']:
                r[n] = H.evaluate(a[n], feats[n], thr, rng)
            r['heldout_pooled'] = H.pool([a[n] for n in held], [feats[n] for n in held], thr, rng)
            for n in D['later']:
                fl = a[n] >= thr
                lo, hi = H.wilson(fl.mean(), len(fl) // (H.L // H.STEP))
                r[n] = dict(flag_rate=float(fl.mean()), wilson_block=(lo, hi), windows=int(len(fl)), hours=len(fl) * H.STEP / 3600)
            fl = np.concatenate([a[n] >= thr for n in D['later']])
            r['later_pooled'] = dict(flag_rate=float(fl.mean()), wilson_block=H.wilson(fl.mean(), len(fl) // (H.L // H.STEP)),
                                     windows=int(len(fl)), hours=len(fl) * H.STEP / 3600)
            vres[op] = r
        out[variant] = vres
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--version', required=True, choices=sorted(DESIGN)); ap.add_argument('--data-dir', required=True)
    ap.add_argument('--out-dir', required=True); ap.add_argument('--seed', type=int, default=42); ap.add_argument('--seeds', type=int, default=0)
    a = ap.parse_args(); os.makedirs(a.out_dir, exist_ok=True)
    D, seg, feats, table, cols = build(a.version, a.data_dir)
    raw, nfeat = score(feats, a.seed)
    res = dict(meta=dict(version=a.version, seed=a.seed, variables=len(cols), features=nfeat, window_s=H.L, step_s=H.STEP,
                         design={k: v for k, v in D.items() if k not in ('files',) and not callable(v)},
                         python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__, sklearn=sklearn.__version__,
                         file_sha256={n: H.sha256(os.path.join(a.data_dir, D['files'](n))) for n in seg if n not in ('training', 'calibration')} |
                                     {D['train']: H.sha256(os.path.join(a.data_dir, D['files'](D['train'])))}),
               partitions=table, results=evaluate_all(D, feats, raw, a.seed))
    json.dump(res, open(os.path.join(a.out_dir, f'hai{a.version}_results.json'), 'w'), indent=1, default=float)
    pd.DataFrame(table).to_csv(os.path.join(a.out_dir, f'hai{a.version}_partitions.csv'), index=False)
    if a.seeds:
        rows = []
        for s in range(1, a.seeds + 1):
            r, _ = score(feats, s)
            ev = evaluate_all(D, feats, r, s, variants=('training_statistics_eq14',))['training_statistics_eq14']
            for op, v in ev.items():
                for part in D['held'] + ['heldout_pooled', 'later_pooled'] + D['later']:
                    e = v[part]
                    if 'fpr' in e:
                        rows.append(dict(seed=s, operating_point=op, partition=part, fpr_pct=100 * e['fpr'], wilson_lo=100 * e['fpr_wilson_block'][0],
                                         episodes_detected=e['episodes_detected'], episodes=e['episodes']))
                    else:
                        rows.append(dict(seed=s, operating_point=op, partition=part, fpr_pct=100 * e['flag_rate'], wilson_lo=100 * e['wilson_block'][0],
                                         episodes_detected=None, episodes=None))
            print('seed', s, flush=True)
        pd.DataFrame(rows).to_csv(os.path.join(a.out_dir, f'hai{a.version}_seed_sensitivity.csv'), index=False)
    print(pd.DataFrame(table).to_string())
    for variant, vres in res['results'].items():
        for op, r in vres.items():
            e = r['heldout_pooled']; l = r['later_pooled']
            print(f"{variant[:8]} {op:14s} cal={100*r['calibration_flag_rate']:.2f}% FPR={100*e['fpr']:.2f}% "
                  f"[{100*e['fpr_wilson_block'][0]:.2f}-{100*e['fpr_wilson_block'][1]:.2f}] ep={e['episodes_detected']}/{e['episodes']} "
                  f"CP={e['episode_recall_cp'][0]:.2f}-{e['episode_recall_cp'][1]:.2f} RCI={e['R_CI']:.3f} L{e['level']} "
                  f"later={100*l['flag_rate']:.2f}% [{100*l['wilson_block'][0]:.2f}-{100*l['wilson_block'][1]:.2f}] ({l['hours']:.0f} h)")


if __name__ == '__main__':
    main()
