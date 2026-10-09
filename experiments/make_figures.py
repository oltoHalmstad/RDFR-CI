#!/usr/bin/env python3
"""Regenerate Figure 7 (HAI 21.03 held-out evaluation) and Figure A2 (retention probabilities).

    python make_figures.py --hai-json results_hai/hai_results.json --uncertainty-csv decision_uncertainty.csv --out-dir figures
"""
import argparse, json, os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'DejaVu Sans'

GREY, RED, ORANGE = '#bdbdbd', '#d62728', '#d95f02'
BLUES = ['#9ecae1', '#4292c6', '#08519c']      # ordered by time: test3 -> test4 -> test5
OPS = ['F1 comparator', 'Nominal 1%', 'Nominal 5%', 'Nominal 10%']
BUDGET = {'Nominal 1%': 1, 'Nominal 5%': 5, 'Nominal 10%': 10}


def figure7(res, out, eq_label='Eq. 15'):
    r = res['results']['training_statistics_eq14']
    parts = [('heldout_test3', 'test3 (13–14 Jul, overlap removed)'), ('heldout_test4', 'test4 (28 Jul)'), ('heldout_test5', 'test5 (30–31 Jul)')]
    fig, ax = plt.subplots(1, 3, figsize=(10, 3.8), dpi=300, gridspec_kw={'width_ratios': [1.55, 1, 1]})
    a = ax[0]; x = np.arange(len(OPS)); w = 0.19
    a.bar(x - 1.5 * w, [100 * r[o]['calibration_flag_rate'] for o in OPS], w * 0.94, color=GREY, label='Normal calibration (train1)')
    for k, (p, lab) in enumerate(parts):
        v = np.array([100 * r[o][p]['fpr'] for o in OPS])
        lo = np.array([100 * r[o][p]['fpr_wilson_block'][0] for o in OPS]); hi = np.array([100 * r[o][p]['fpr_wilson_block'][1] for o in OPS])
        a.bar(x + (k - 0.5) * w, v, w * 0.94, color=BLUES[k], label='Held-out ' + lab)
        a.errorbar(x + (k - 0.5) * w, v, yerr=[v - lo, hi - v], fmt='none', ecolor='black', elinewidth=0.9, capsize=2.5,
                   label='Wilson 95% (block basis)' if k == 2 else None)
    for i, o in enumerate(OPS):
        if o in BUDGET:
            a.plot([i - 2.2 * w, i + 2.2 * w], [BUDGET[o]] * 2, color=RED, ls='--', lw=1.2, label='Nominal budget' if i == 1 else None)
    a.set_xticks(x); a.set_xticklabels(OPS, fontsize=8); a.set_ylabel('False-positive rate (%)', fontsize=9)
    a.set_title('(a) Budget feasibility on three later periods', fontsize=9.5)
    h, l = a.get_legend_handles_labels(); order = [l.index(s) for s in ['Nominal budget', 'Normal calibration (train1)'] + ['Held-out ' + p[1] for p in parts] + ['Wilson 95% (block basis)']]
    a.set_ylim(0, 23.5); a.legend([h[i] for i in order], [l[i] for i in order], fontsize=6.3, loc='upper left', framealpha=0.95)
    a.grid(axis='y', alpha=0.3); a.set_axisbelow(True); a.tick_params(axis='y', labelsize=8)

    b = ax[1]; pooled = [r[o]['heldout_pooled'] for o in OPS]
    rec = np.array([e['episodes_detected'] / e['episodes'] for e in pooled])
    lo = np.array([e['episode_recall_cp'][0] for e in pooled]); hi = np.array([e['episode_recall_cp'][1] for e in pooled])
    b.errorbar(x, rec, yerr=[rec - lo, hi - rec], fmt='o', color=BLUES[2], capsize=4, lw=1.6, ms=6, label='Episode recall, Clopper–Pearson 95%')
    b.plot(x, [e['point_recall'] for e in pooled], 's', mfc='none', mec=BLUES[1], ms=6, mew=1.3, label='Pointwise recall')
    for i, e in enumerate(pooled):
        b.annotate(f"{e['episodes_detected']}/{e['episodes']}", (x[i], rec[i]), textcoords='offset points', xytext=(6, 2), fontsize=7.5)
    b.set_ylim(0, 1.05); b.set_xlim(-0.5, 3.95); b.set_xticks(x); b.set_xticklabels([o.replace('Nominal ', '').replace(' comparator', '') for o in OPS], fontsize=8)
    b.set_ylabel('Recall on held-out attacks (25 episodes)', fontsize=9); b.set_title('(b) Detection, pooled held-out data', fontsize=9.5)
    b.legend(fontsize=6.3, loc='lower left', framealpha=0.95); b.grid(alpha=0.3); b.set_axisbelow(True); b.tick_params(axis='y', labelsize=8)

    c = ax[2]
    c.plot(x, [e['R_CI'] for e in pooled], 'D', color=ORANGE, ms=6, label=r'$R_{CI}$ at observed recall')
    c.plot(x, [e['R_CI_at_lower_recall'] for e in pooled], 'D', mfc='none', mec=ORANGE, ms=6, mew=1.3, label=r'$R_{CI}$ at lower 95% recall limit')
    c.axhline(0.50, color='black', ls=':', lw=1.2); c.text(3.55, 0.503, 'Shadow/restricted (level 1)', fontsize=6.3, ha='right', va='bottom')
    c.text(3.55, 0.497, 'Assisted defense (level 2)', fontsize=6.3, ha='right', va='top')
    c.set_ylim(0.40, 0.56); c.set_xlim(-0.5, 3.6); c.set_xticks(x); c.set_xticklabels([o.replace('Nominal ', '').replace(' comparator', '') for o in OPS], fontsize=8)
    c.set_ylabel(r'Composite score $R_{CI}$ (%s)' % eq_label, fontsize=9); c.set_title('(c) Provisional authority', fontsize=9.5)
    c.legend(fontsize=6.3, loc='upper left', framealpha=0.95); c.grid(alpha=0.3); c.set_axisbelow(True); c.tick_params(axis='y', labelsize=8)
    fig.tight_layout(); fig.savefig(out, dpi=300); plt.close(fig)


def figure_a2(csv, out):
    df = pd.read_csv(csv).set_index('scenario_id')
    ids = ['CDI-001', 'MFG-001', 'SUB-001', 'RAIL-001', 'HOSP-001', 'WATER-001']
    names = ['Digital', 'Manufacturing', 'Substation', 'Rail', 'Hospital', 'Water']
    sc = df.loc[ids, 'point_score'].to_numpy(); pr = df.loc[ids, 'p_point_state'].to_numpy()
    col = '#1f6f9f'
    fig, ax = plt.subplots(1, 2, figsize=(2349 / 260, 1439 / 260), dpi=260, gridspec_kw={'width_ratios': [1.4, 1]}, sharey=True)
    y = np.arange(len(ids))[::-1]
    a = ax[0]
    for bnd in (0.20, 0.35, 0.50, 0.65):
        a.axvline(bnd, color='#7f8c9a', ls='--', lw=1); a.text(bnd, 5.62, f'{bnd:.2f}', ha='center', fontsize=8.5, color='#4a5868', bbox=dict(fc='white', ec='none', pad=1.5))
    a.plot(sc, y, 'o', color=col, ms=8)
    for s, yy in zip(sc, y): a.text(s + 0.012, yy + 0.16, f'{s:.4f}', color=col, fontsize=9.5)
    a.set_yticks(y); a.set_yticklabels(names); a.set_xlim(0.1, 0.7); a.set_ylim(-0.55, 6.05)
    a.set_xlabel(r'Composite score $R_{CI}$'); a.set_title('Composite scores and\nscore-band boundaries', fontsize=11)
    a.grid(axis='x', alpha=0.2)
    b = ax[1]
    b.barh(y, pr, height=0.52, color='#2f7ba8'); b.axvline(0.90, color='#4a5868', ls=':', lw=1.6)
    for p, yy in zip(pr, y): b.text(p + 0.015, yy, f'{p:.2f}', va='center', fontsize=10)
    b.set_xlim(0, 1.15); b.set_xlabel('Retention probability of the\nprovisional authority level'); b.set_title('Retention probability\n(input perturbation, σ = 0.05)', fontsize=11)
    b.grid(axis='x', alpha=0.2)
    for s in ('top', 'right'):
        a.spines[s].set_visible(False); b.spines[s].set_visible(False)
    fig.suptitle('Six illustrative action contexts: scores and retention of the provisional level', fontsize=11.5, y=0.985)
    fig.text(0.5, 0.012, 'Frequencies over 10,000 draws per context, rounded to two decimals; the dotted line marks the 0.90 review criterion.', ha='center', fontsize=8, color='#4a5868')
    fig.tight_layout(rect=(0, 0.03, 1, 0.97)); fig.savefig(out, dpi=260); plt.close(fig)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--hai-json'); ap.add_argument('--uncertainty-csv'); ap.add_argument('--out-dir', default='figures')
    ap.add_argument('--eq-label', default='Eq. 15', help='equation label shown on the R_CI axis of Figure 7')
    args = ap.parse_args(); os.makedirs(args.out_dir, exist_ok=True)
    if args.hai_json: figure7(json.load(open(args.hai_json)), os.path.join(args.out_dir, 'figure_7_hai_heldout.png'), args.eq_label)
    if args.uncertainty_csv: figure_a2(args.uncertainty_csv, os.path.join(args.out_dir, 'figure_A2_retention_probability.png'))
