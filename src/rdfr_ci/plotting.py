"""Publication-quality figure generation for RDFR-CI supplementary materials."""
from __future__ import annotations
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from .authority import BOUNDARIES


def _save(fig, outbase):
    outbase = Path(outbase)
    outbase.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outbase.with_suffix('.png'), dpi=300, bbox_inches='tight')
    fig.savefig(outbase.with_suffix('.pdf'), bbox_inches='tight')
    plt.close(fig)


def architecture_figure(outbase):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    ax.text(.5, .95, 'RDFR-CI evidence-to-authority architecture', ha='center', fontsize=14, fontweight='bold')

    nodes = [
        ('Evidence', .08, .62, .12),
        ('Context', .23, .62, .12),
        ('AI analysis', .38, .62, .12),
        ('Composite risk', .55, .62, .13),
        ('Provisional\nauthority', .72, .62, .13),
        ('Permitted\nauthority', .88, .62, .13),
    ]
    for lbl, x, y, w in nodes:
        box = FancyBboxPatch((x-w/2, y-.065), w, .13, boxstyle='round,pad=0.01', fill=False, linewidth=1.2)
        ax.add_patch(box); ax.text(x, y, lbl, ha='center', va='center', fontsize=9)
    for a,b in zip(nodes[:-1], nodes[1:]):
        ax.add_patch(FancyArrowPatch((a[1]+a[3]/2, a[2]), (b[1]-b[3]/2, b[2]), arrowstyle='->', mutation_scale=12))

    risk = FancyBboxPatch((.31,.25),.31,.23,boxstyle='round,pad=0.015',fill=False,linewidth=1.2)
    ax.add_patch(risk)
    ax.text(.465,.445,'Five risk dimensions',ha='center',fontsize=10,fontweight='bold')
    ax.text(.465,.355,'E  Threat exposure\nD  Detection gap\nA  AI-specific risk\nF  Forensic-readiness risk\nC  Cyber-physical consequence',ha='center',va='center',fontsize=7.8,linespacing=1.25)
    ax.add_patch(FancyArrowPatch((.465,.48),(.55,.555),arrowstyle='->',mutation_scale=12))

    gates = FancyBboxPatch((.68,.25),.29,.23,boxstyle='round,pad=0.015',fill=False,linewidth=1.2)
    ax.add_patch(gates)
    ax.text(.825,.445,'Independent gates',ha='center',fontsize=10,fontweight='bold')
    ax.text(.825,.355,'G_S  Safety\nG_V  Availability\nG_FA  Forensic accountability\nG_A  AI assurance\nG_H  Human authority',ha='center',va='center',fontsize=7.8,linespacing=1.25)
    ax.add_patch(FancyArrowPatch((.825,.48),(.88,.555),arrowstyle='->',mutation_scale=12))

    action = FancyBboxPatch((.79,.76),.18,.11,boxstyle='round,pad=0.01',fill=False,linewidth=1.2)
    ax.add_patch(action); ax.text(.88,.815,'Bounded action / response',ha='center',va='center',fontsize=9)
    ax.add_patch(FancyArrowPatch((.88,.685),(.88,.76),arrowstyle='->',mutation_scale=12))

    witness = FancyBboxPatch((.13,.06),.74,.10,boxstyle='round,pad=0.015',fill=False,linewidth=1.2)
    ax.add_patch(witness)
    ax.text(.50,.11,'Independent forensic & accountability layer\npreserve evidence • witness actions • record approvals • support replay and rollback',ha='center',va='center',fontsize=8.2)
    _save(fig, outbase)


def evidence_workflow_figure(outbase):
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('off')
    labels = ['Evidence', 'Context', 'Interpretation', 'Recommendation', 'Authorization', 'Action & verification']
    x = np.linspace(.09, .91, len(labels))
    y = .64
    for xx, lbl in zip(x, labels):
        box = FancyBboxPatch((xx - .07, y - .07), .14, .14,
                             boxstyle='round,pad=0.01', fill=False)
        ax.add_patch(box)
        ax.text(xx, y, lbl, ha='center', va='center', fontsize=8)
    for a, b in zip(x[:-1], x[1:]):
        ax.add_patch(FancyArrowPatch((a + .07, y), (b - .07, y), arrowstyle='->', mutation_scale=12))
    witness = FancyBboxPatch((.18, .20), .64, .15, boxstyle='round,pad=0.015', fill=False, linewidth=1.2)
    ax.add_patch(witness)
    ax.text(.5, .275,
            'Independent forensic & accountability layer\nsource artifacts + model/tool versions + approvals + before/after state',
            ha='center', va='center', fontsize=9)
    for xx in x:
        ax.add_patch(FancyArrowPatch((xx, .57), (xx, .35), arrowstyle='->', mutation_scale=9))
    ax.text(.5, .92, 'Evidence ≠ Interpretation ≠ Recommendation ≠ Authorization ≠ Action',
            ha='center', fontsize=12, fontweight='bold')
    _save(fig, outbase)


def progressive_authority_figure(outbase):
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.axis('off')
    labels = ['Rollback / isolation', 'Shadow / restricted', 'Assisted defense',
              'Human-approved', 'Bounded automation']
    xs = np.linspace(.1, .9, 5)
    for xx, lbl in zip(xs, labels):
        box = FancyBboxPatch((xx - .075, .46), .15, .18, boxstyle='round,pad=0.01', fill=False)
        ax.add_patch(box)
        ax.text(xx, .55, lbl, ha='center', va='center', fontsize=8)
    ax.add_patch(FancyArrowPatch((.08, .78), (.92, .78), arrowstyle='->', mutation_scale=14))
    ax.text(.5, .84, 'Promotion: risk improves AND all applicable gates pass', ha='center', fontsize=10)
    ax.add_patch(FancyArrowPatch((.92, .28), (.08, .28), arrowstyle='->', mutation_scale=14))
    ax.text(.5, .17, 'Graceful degradation after stop conditions or gate failure', ha='center', fontsize=10)
    _save(fig, outbase)


def authority_ceiling_figure(outbase, w_c=.25, scenario_points=None):
    c = np.linspace(0, 1, 401)
    r = w_c * c
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(c, r, label=r'$R_{min}=w_C C$')
    for b in BOUNDARIES:
        ax.axhline(b, linestyle='--', linewidth=.8)
    if scenario_points:
        ax.scatter([p['C'] for p in scenario_points], [w_c * p['C'] for p in scenario_points],
                   s=20, label='Scenario library')
    ax.set(xlabel='Cyber-physical consequence C', ylabel='Best achievable composite score $R_{min}$',
           xlim=(0, 1), ylim=(0, .7), title='Consequence-driven authority ceiling')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(alpha=.2)
    _save(fig, outbase)


def decision_stability_figure(outbase, rows):
    rows = sorted(rows, key=lambda r: r['point_score'])
    y = np.arange(len(rows))
    x = np.array([r['point_score'] for r in rows])
    lo = x - np.array([r['p05_R_CI'] for r in rows])
    hi = np.array([r['p95_R_CI'] for r in rows]) - x
    fig, ax = plt.subplots(figsize=(8, max(6, len(rows) * .22)))
    ax.errorbar(x, y, xerr=[lo, hi], fmt='o', markersize=3, capsize=2)
    for b in BOUNDARIES:
        ax.axvline(b, linestyle='--', linewidth=.8)
    unstable = [i for i, r in enumerate(rows) if r['p_point_state'] < .90]
    if unstable:
        ax.scatter(x[unstable], np.array(y)[unstable], facecolors='none', edgecolors='black',
                   s=55, label='P(point state) < 0.90')
    ax.set_yticks(y)
    ax.set_yticklabels([r['scenario_id'] for r in rows], fontsize=6)
    ax.set_xlabel('$R_{CI}$ with 5th-95th percentile interval')
    ax.set_title('Decision stability under one elicitation step (σ=0.05)')
    if unstable:
        ax.legend(fontsize=8)
    ax.grid(axis='x', alpha=.2)
    _save(fig, outbase)


def detection_threshold_figure(outbase, sweep_rows, baseline=0.324):
    thr = np.array([r['threshold'] for r in sweep_rows])
    f1 = np.array([r['f1'] for r in sweep_rows])
    d = np.array([r['detection_gap'] for r in sweep_rows])
    fpr = np.array([r['fpr'] for r in sweep_rows])
    rci = baseline + .20 * d
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(thr, f1, label='Global F1')
    ax.plot(thr, 1 - d, label='Criticality-weighted recall')
    ax2 = ax.twinx()
    ax2.plot(thr, rci, linestyle='--', label='$R_{CI}$')
    for b in BOUNDARIES:
        ax2.axhline(b, linestyle=':', linewidth=.7)
    feasible = fpr <= .05
    if feasible.any():
        idx = np.where(feasible)[0][np.argmin(d[feasible])]
        ax.axvline(thr[idx], linestyle='--', linewidth=1, label='Authority optimum, FPR≤0.05')
    idx2 = int(np.argmax(f1))
    ax.axvline(thr[idx2], linestyle='-.', linewidth=1, label='Global F1 optimum')
    ax.set(xlabel='Detection threshold', ylabel='Detection metric',
           title='Detection threshold versus permitted-authority inputs')
    ax2.set_ylabel('$R_{CI}$ (fixed-context demonstration)')
    ax.legend(loc='lower left', fontsize=8)
    ax.grid(alpha=.2)
    _save(fig, outbase)


def multi_agent_authority_figure(outbase):
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.axis('off')
    nodes = [('Parent agent', .16, .65), ('Search agent', .42, .82), ('Analysis agent', .42, .58),
             ('Action agent', .70, .65), ('Independent witness', .70, .28), ('Gates + policy', .42, .30)]
    for lbl, x, y in nodes:
        box = FancyBboxPatch((x - .09, y - .06), .18, .12, boxstyle='round,pad=0.01', fill=False)
        ax.add_patch(box)
        ax.text(x, y, lbl, ha='center', va='center', fontsize=9)
    edges = [((.25, .66), (.33, .80)), ((.25, .65), (.33, .59)), ((.51, .80), (.61, .69)),
             ((.51, .58), (.61, .64)), ((.51, .33), (.64, .60)), ((.70, .59), (.70, .34))]
    for a, b in edges:
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle='->', mutation_scale=12))
    ax.text(.5, .95, 'Non-transitive multi-agent authority', ha='center', fontsize=14, fontweight='bold')
    ax.text(.5, .08,
            'Child authority ≤ parent authority, child scope, action policy and every applicable gate',
            ha='center', fontsize=10)
    _save(fig, outbase)
