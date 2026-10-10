#!/usr/bin/env python3
"""Robustness, policy-variant, alternative-method and parameterization analyses.

Regenerates, with fixed seeds, the manuscript outputs attributed to
``experiments/run_revision_analyses.py``:

* Table 10  - robustness of provisional/final levels (deterministic boundary
              shifts, inputs-only and joint Monte Carlo retention probabilities)
* Table 15  - structural properties of four policy variants
* Table 17  - comparison with three alternative decision methods
* Table A1  - 24 alternative parameterizations of weights and band boundaries
* Table 11  - interval columns (Wilson 95%, nominal n = 5821 and block n_eff = 485)
* Table 12  - interval column (Clopper-Pearson 95% for 12 held-out events)
* Figures 4, 5 and 6 (PNG + PDF)

Design source: manuscript Sections 3.13 (end), 3.14 and 3.16. The script was
re-implemented in release v1.4.1 from that description because the v1.4.0
file was not available (see experiments/REVISION_ANALYSES_NOTE.md).

Input: the archived 30-scenario catalog (scenarios/scenario_catalog.yaml).
The SWaT A11 analysis of Section 4.3 (Tables 11 and 12, Figure 5) is rerun on
the restricted captures by experiments/swat/a11_rerun.py.
Policy logic (Equation (1) score, Equation (2) weights, Table 5 gate caps,
Table 6 bands, Equation (10) minimum) is taken from the ``rdfr_ci`` package.

Usage:
    PYTHONPATH=src python3 experiments/run_revision_analyses.py \
        [--out-dir results/revision_analyses] [--seed 42] [--n-mc 10000]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta as beta_dist
from scipy.stats import norm, spearmanr
from sklearn.metrics import cohen_kappa_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "src"))

from rdfr_ci.authority import BOUNDARIES, AuthorityState, authority_from_score, boundary_margin  # noqa: E402
from rdfr_ci.gates import final_authority  # noqa: E402
from rdfr_ci.risk import DEFAULT_WEIGHTS, DIMENSIONS, composite_risk  # noqa: E402
from rdfr_ci.scenario_loader import load_catalog  # noqa: E402
from rdfr_ci.uncertainty import simulate_state_distribution  # noqa: E402

CATALOG = ROOT / "scenarios" / "scenario_catalog.yaml"
SHOWCASES = ("CDI-001", "MFG-001", "SUB-001", "RAIL-001", "HOSP-001", "WATER-001")
LEVELS_DESC = (4, 3, 2, 1, 0)

# Scores and boundaries are compared after rounding to this many decimals so
# that values lying exactly on a (shifted) boundary, e.g. WATER-001 at 0.5000,
# follow the half-open convention of Table 6 instead of floating-point noise.
_ROUND = 10

# Water-treatment context of Equation (15): E, A, F, C fixed, D varies.
WATER_CONTEXT = {"E": 0.55, "A": 0.30, "F": 0.25, "C": 0.90}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def level_from_score(score: float, bounds=BOUNDARIES) -> int:
    """Table 6 half-open bands with (possibly shifted) boundaries b1<b2<b3<b4."""
    x = round(float(score), _ROUND)
    for i, b in enumerate(bounds):
        if x < round(float(b), _ROUND):
            return 4 - i
    return 0


def levels_vec(scores: np.ndarray, bounds) -> np.ndarray:
    """Vectorised version of :func:`level_from_score`; ``bounds`` may be (n,4)."""
    s = np.round(np.asarray(scores, float), _ROUND)
    b = np.round(np.asarray(bounds, float), _ROUND)
    if b.ndim == 1:
        b = np.broadcast_to(b, (s.size, 4))
    return 4 - (s[:, None] >= b).sum(axis=1)


def score(values: dict, weights: dict) -> float:
    return float(sum(weights[k] * float(values[k]) for k in DIMENSIONS))


def rescaled(weights: dict, key: str, value: float) -> dict:
    """Set one weight and rescale the others proportionally to keep sum 1."""
    rest = sum(v for k, v in weights.items() if k != key)
    return {k: (value if k == key else v * (1.0 - value) / rest) for k, v in weights.items()}


def wilson(p: float, n: float, conf: float = 0.95):
    z = norm.ppf(0.5 + conf / 2)
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def clopper_pearson(k: int, n: int, conf: float = 0.95):
    a = 1 - conf
    lo = 0.0 if k == 0 else float(beta_dist.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta_dist.ppf(1 - a / 2, k + 1, n - k))
    return lo, hi


def counts_by_level(levels) -> str:
    levels = list(levels)
    return " / ".join(str(levels.count(v)) for v in LEVELS_DESC)


def write(df: pd.DataFrame, out: Path, name: str) -> None:
    df.to_csv(out / f"{name}.csv", index=False)


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------
def load_scenarios():
    """Point scores, provisional/final levels and gate caps (Section 3.14).

    A gate recorded as unresolved in the catalog receives its Table 5 UNKNOWN
    cap (via rdfr_ci.gates.final_authority); all other gates are PASS.
    """
    rows = []
    for s in load_catalog(CATALOG):
        vals = s.values()
        r = composite_risk(*(vals[k] for k in DIMENSIONS), weights=s.weights)
        prov = authority_from_score(r)
        final, binding = final_authority(prov, s.gate_states, s.gate_caps)
        cap, _ = final_authority(AuthorityState.BOUNDED_AUTOMATION, s.gate_states, s.gate_caps)
        rows.append(dict(
            scenario_id=s.scenario_id, reversibility=s.reversibility, weights=dict(s.weights),
            **vals, R_CI=r, provisional=int(prov), final=int(final), gate_cap=int(cap),
            binding=binding, gated=int(cap) < 4, margin=boundary_margin(r),
            unresolved_gates=",".join(k for k, v in s.gate_states.items() if v != "pass"),
        ))
    df = pd.DataFrame(rows)
    assert len(df) == 30 and int(df.gated.sum()) == 13
    return df


def final_levels(prov: np.ndarray, caps: np.ndarray) -> np.ndarray:
    """Equation (10) with declared gates: min(provisional, gate cap)."""
    return np.minimum(prov, caps)


# ---------------------------------------------------------------------------
# Table 10 / Figure 4
# ---------------------------------------------------------------------------
def deterministic_shifts(df: pd.DataFrame) -> pd.DataFrame:
    R = df.R_CI.to_numpy(); P = df.provisional.to_numpy(); F = df.final.to_numpy(); cap = df.gate_cap.to_numpy()
    rows = []
    for d in (-0.05, -0.025, 0.025, 0.05):
        settings = [("all", None, [b + d for b in BOUNDARIES])]
        for j in range(4):
            b = list(BOUNDARIES); b[j] += d
            settings.append(("single", j + 1, b))
        for kind, j, b in settings:
            p = levels_vec(R, b); f = final_levels(p, cap)
            rows.append(dict(kind=kind, boundary=j, shift=d, bounds=" ".join(f"{x:.3f}" for x in b),
                             provisional_changed=int((p != P).sum()), final_changed=int((f != F).sum()),
                             provisional_changed_ids=",".join(df.scenario_id[p != P]),
                             final_changed_ids=",".join(df.scenario_id[f != F])))
    return pd.DataFrame(rows)


def inputs_only_mc(df: pd.DataFrame, n: int, seed: int) -> np.ndarray:
    """Input-only sensitivity of Section 4.2 (rdfr_ci.uncertainty, seed+i)."""
    return np.array([
        simulate_state_distribution({k: r[k] for k in DIMENSIONS}, r.weights, sigma=0.05, n=n, seed=seed + i)["p_point_state"]
        for i, r in df.iterrows()])


def joint_mc(df: pd.DataFrame, n: int, seed: int, sigma=0.05, concentration=120.0, shift=0.025):
    """Joint Monte Carlo of Section 3.14 (inputs, Dirichlet weights, common boundary shift)."""
    out = []
    for i, r in df.iterrows():
        rng = np.random.default_rng(seed + i)
        x = np.array([r[k] for k in DIMENSIONS], float)
        w0 = np.array([r.weights[k] for k in DIMENSIONS], float)
        X = np.clip(rng.normal(x, sigma, size=(n, 5)), 0.0, 1.0)
        W = rng.dirichlet(w0 * concentration, size=n)
        u = rng.uniform(-shift, shift, size=n)
        s = (X * W).sum(axis=1)
        b = np.asarray(BOUNDARIES)[None, :] + u[:, None]
        p = levels_vec(s, b)
        f = np.minimum(p, r.gate_cap)
        out.append(dict(scenario_id=r.scenario_id, R_CI=r.R_CI, boundary_margin=r.margin,
                        gated=bool(r.gated), provisional=r.provisional, final=r.final,
                        retention_provisional=float((p == r.provisional).mean()),
                        retention_final=float((f == r.final).mean())))
    return pd.DataFrame(out)


def table10(det: pd.DataFrame, inputs_only: np.ndarray, jmc: pd.DataFrame):
    rows = []
    for d, lab in ((-0.05, "All boundaries -0.05"), (-0.025, "All boundaries -0.025"),
                   (0.025, "All boundaries +0.025"), (0.05, "All boundaries +0.05")):
        x = det[(det.kind == "all") & np.isclose(det["shift"], d)].iloc[0]
        rows.append(dict(perturbation=lab, provisional=f"{x.provisional_changed} changed", final=f"{x.final_changed} changed",
                         provisional_value=int(x.provisional_changed), final_value=int(x.final_changed)))
    for mag in (0.025, 0.05):
        x = det[(det.kind == "single") & np.isclose(det["shift"].abs(), mag)]
        rows.append(dict(perturbation=f"Single boundary +/-{mag} (largest of 8 settings)",
                         provisional=f"{x.provisional_changed.max()} changed", final=f"{x.final_changed.max()} changed",
                         provisional_value=int(x.provisional_changed.max()), final_value=int(x.final_changed.max())))
    k = int((inputs_only >= 0.90).sum())
    rows.append(dict(perturbation="Inputs only, sigma = 0.05: scenarios with retention probability >= 0.90",
                     provisional=f"{k} of 30", final="-", provisional_value=k, final_value=None))
    kp = int((jmc.retention_provisional >= 0.90).sum()); kf = int((jmc.retention_final >= 0.90).sum())
    rows.append(dict(perturbation="Joint Monte Carlo: scenarios with retention probability >= 0.90",
                     provisional=f"{kp} of 30", final=f"{kf} of 30", provisional_value=kp, final_value=kf))
    ip = jmc.retention_provisional.idxmin(); jf = jmc.retention_final.idxmin()
    rows.append(dict(perturbation="Joint Monte Carlo: lowest retention probability",
                     provisional=f"{jmc.retention_provisional[ip]:.2f} ({jmc.scenario_id[ip]})",
                     final=f"{jmc.retention_final[jf]:.2f} ({jmc.scenario_id[jf]})",
                     provisional_value=float(jmc.retention_provisional[ip]), final_value=float(jmc.retention_final[jf])))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Table 15 / Figure 6
# ---------------------------------------------------------------------------
PLAYBOOK = {"high": 4, "medium": 3, "low": 2}


def policy_variants(df: pd.DataFrame) -> dict:
    return {
        "Fixed playbook": df.reversibility.map(PLAYBOOK).to_numpy(),
        "Score-only": df.provisional.to_numpy(),
        "Gates-only": df.gate_cap.to_numpy(),
        "Full RDFR-CI": df.final.to_numpy(),
    }


def table15(df: pd.DataFrame, variants: dict) -> pd.DataFrame:
    R = df.R_CI.to_numpy(); P = df.provisional.to_numpy(); C = df.C.to_numpy(); g = df.gated.to_numpy()
    rows = []
    for name, L in variants.items():
        rows.append(dict(
            variant=name,
            eligible_while_gate_unresolved=int(((L >= 3) & g).sum()),
            above_provisional=int((L > P).sum()),
            bounded_automation_C_ge_0_5=int(((L == 4) & (C >= 0.5)).sum()),
            spearman_rci_restriction=float(spearmanr(R, 4 - L)[0]),
            levels_4_3_2_1_0=counts_by_level(L),
            eligible_while_gated_ids=",".join(df.scenario_id[(L >= 3) & g]),
        ))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Table 17
# ---------------------------------------------------------------------------
AISOC_RENORM = {k: DEFAULT_WEIGHTS[k] / (1 - DEFAULT_WEIGHTS["C"]) for k in ("E", "D", "A", "F")}  # (0.267,0.267,0.200,0.267)
AISOC_ORIGINAL = {"E": 0.30, "D": 0.30, "A": 0.20, "F": 0.20}
MATRIX_MAP = {0: 4, 1: 4, 2: 4, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 0}


def aisoc_score(v: dict, w: dict) -> float:
    return float(sum(w[k] * v[k] for k in ("E", "D", "A", "F")))


def five_class(x: float) -> int:
    """Equal-width classes [0,.2),[.2,.4),...,[.8,1] -> 0..4."""
    return min(int(math.floor(round(x, _ROUND) * 5)), 4)


def method_level(method: str, v: dict) -> int:
    """Score-based level of an alternative method, before gates."""
    if method == "Full RDFR-CI":
        return level_from_score(score(v, DEFAULT_WEIGHTS))
    if method == "AI-SOC-style score (no C)":
        return level_from_score(aisoc_score(v, AISOC_RENORM))
    if method == "AI-SOC original weights (sensitivity)":
        return level_from_score(aisoc_score(v, AISOC_ORIGINAL))
    if method == "5 x 5 risk matrix":
        return MATRIX_MAP[five_class(aisoc_score(v, AISOC_RENORM)) + five_class(v["C"])]
    if method == "Worst-dimension rule":
        return level_from_score(max(v[k] for k in DIMENSIONS))
    raise ValueError(method)


METHODS = ("Full RDFR-CI", "AI-SOC-style score (no C)", "5 x 5 risk matrix", "Worst-dimension rule",
           "AI-SOC original weights (sensitivity)")


def table17(df: pd.DataFrame):
    ref = df.final.to_numpy(); C = df.C.to_numpy(); R = df.R_CI.to_numpy(); cap = df.gate_cap.to_numpy()
    rows, per = [], {}
    for m in METHODS:
        L = final_levels(np.array([method_level(m, {k: r[k] for k in DIMENSIONS}) for _, r in df.iterrows()]), cap)
        per[m] = L
        water = [method_level(m, {**WATER_CONTEXT, "D": d}) for d in (0.0, 0.25)]
        rows.append(dict(
            method=m, agreement=int((L == ref).sum()),
            kappa_quadratic=float(cohen_kappa_score(L, ref, weights="quadratic")),
            higher=int((L > ref).sum()), lower=int((L < ref).sum()),
            eligible_C_ge_0_65=int(((L >= 3) & (C >= 0.65)).sum()),
            level0=int((L == 0).sum()),
            rho_C=float(spearmanr(C, 4 - L)[0]), rho_RCI=float(spearmanr(R, 4 - L)[0]),
            levels_4_3_2_1_0=counts_by_level(L).replace(" ", ""),
            water_context_D0_D025=f"{water[0]}, {water[1]}",
            disagreements=",".join(f"{sid}:{a}vs{b}" for sid, a, b in zip(df.scenario_id, L, ref) if a != b),
        ))
    return pd.DataFrame(rows), per


# ---------------------------------------------------------------------------
# Table A1
# ---------------------------------------------------------------------------
def parameterizations():
    w = dict(DEFAULT_WEIGHTS)
    weights = [("Baseline (Eq. (2))", w), ("Equal weights", {k: 0.2 for k in DIMENSIONS}),
               ("Consequence-heavy (wC = 0.35)", rescaled(w, "C", 0.35)),
               ("Consequence-light (wC = 0.15)", rescaled(w, "C", 0.15)),
               ("Detection-heavy (wD = 0.30)", rescaled(w, "D", 0.30)),
               ("Forensic-light (wF = 0.10)", rescaled(w, "F", 0.10))]
    bounds = [("Baseline", list(BOUNDARIES)), ("Stricter (-0.05)", [b - 0.05 for b in BOUNDARIES]),
              ("More permissive (+0.05)", [b + 0.05 for b in BOUNDARIES]), ("Equal-width", [0.20, 0.40, 0.60, 0.80])]
    return [(wn, wv, bn, bv) for wn, wv in weights for bn, bv in bounds]


def tableA1(df: pd.DataFrame) -> pd.DataFrame:
    F = df.final.to_numpy(); cap = df.gate_cap.to_numpy(); g = df.gated.to_numpy()
    idx = [int(np.flatnonzero(df.scenario_id == s)[0]) for s in SHOWCASES]
    rows = []
    for wn, wv, bn, bv in parameterizations():
        R = np.array([score({k: r[k] for k in DIMENSIONS}, wv) for _, r in df.iterrows()])
        L = final_levels(levels_vec(R, bv), cap)
        up = int((L > F).sum()); dn = int((L < F).sum())
        rows.append(dict(weights=wn, boundaries=bn, changed=up + dn, up=up, down=dn,
                         final_levels_changed=f"{up + dn} ({up} up / {dn} down)",
                         C_star=round(bv[0] / wv["C"], 10),
                         showcase_codes=" ".join(str(L[i]) for i in idx),
                         eligible_while_gate_unresolved=int(((L >= 3) & g).sum()),
                         gated_changed_ids=",".join(df.scenario_id[g & (L != F)]),
                         **{f"w{k}": wv[k] for k in DIMENSIONS}, b1=bv[0], b2=bv[1], b3=bv[2], b4=bv[3]))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
BLUE, ORANGE, INK, MUTED = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e"


def _style(plt):
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                         "ytick.color": MUTED, "axes.grid": True, "grid.color": "#e4e3df", "grid.linewidth": 0.6,
                         "axes.axisbelow": True, "legend.frameon": False})


def _save(fig, out: Path, name: str):
    for ext in ("png", "pdf"):
        fig.savefig(out / f"{name}.{ext}", dpi=300, bbox_inches="tight")


def figure4(det: pd.DataFrame, jmc: pd.DataFrame, out: Path):
    import matplotlib.pyplot as plt
    _style(plt)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1.5, 1]})
    d = pd.concat([det[det.kind == "all"], det[det.kind == "single"].sort_values(["boundary", "shift"])])
    labels = [("All " if k == "all" else f"b{int(b)} ") + f"{s:+.3f}" for k, b, s in zip(d.kind, d.boundary, d["shift"])]
    x = np.arange(len(d)); wbar = 0.38
    ax1.bar(x - wbar / 2 - 0.02, d.provisional_changed, wbar, color=BLUE, label="Provisional level")
    ax1.bar(x + wbar / 2 + 0.02, d.final_changed, wbar, color=ORANGE, label="Final level")
    ax1.axvline(3.5, color=MUTED, lw=0.8, ls=":")
    ax1.set_xticks(x, labels, rotation=60, ha="right", fontsize=7)
    ax1.set_ylabel("Scenarios with changed level (of 30)")
    ax1.set_title("(a) Deterministic band-boundary shifts", loc="left", fontsize=10)
    ax1.legend(loc="upper right")
    ax2.scatter(jmc.boundary_margin, jmc.retention_provisional, s=30, facecolors="none", edgecolors=BLUE,
                linewidths=1.2, label="Provisional level")
    ax2.scatter(jmc.boundary_margin, jmc.retention_final, s=22, color=ORANGE, label="Final level")
    ax2.axhline(0.90, color=MUTED, lw=0.8, ls="--")
    for _, r in jmc[jmc.retention_final < 0.90].iterrows():
        ax2.annotate(r.scenario_id, (r.boundary_margin, r.retention_final), xytext=(4, -3),
                     textcoords="offset points", fontsize=6.5, color=MUTED)
    ax2.set_xlabel("Distance of point score to nearest band boundary")
    ax2.set_ylabel("Retention probability")
    ax2.set_ylim(0.4, 1.02)
    ax2.set_title("(b) Joint Monte Carlo (inputs, weights, boundaries)", loc="left", fontsize=10)
    ax2.legend(loc="lower right")
    fig.tight_layout(); _save(fig, out, "figure_4_robustness"); plt.close(fig)


def figure6(df: pd.DataFrame, variants: dict, t15: pd.DataFrame, out: Path):
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    _style(plt)
    names = list(variants)
    M = np.vstack([variants[n] for n in names])
    cmap = ListedColormap(["#0d366b", "#1c5cab", "#3987e5", "#86b6ef", "#cde2fb"])  # 0..4
    fig, ax = plt.subplots(figsize=(12, 2.9))
    ax.imshow(M, cmap=cmap, vmin=-0.5, vmax=4.5, aspect="auto")
    ax.grid(False)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, str(M[i, j]), ha="center", va="center", fontsize=7,
                    color="white" if M[i, j] <= 2 else INK)
    ax.set_yticks(range(len(names)), names)
    ax.set_xticks(range(len(df)), [s + ("*" if g else "") for s, g in zip(df.scenario_id, df.gated)],
                  rotation=70, ha="right", fontsize=7)
    ax.set_xlim(-0.5, len(df) + 1.5)
    for i, n in enumerate(names):
        k = int(t15.set_index("variant").loc[n, "eligible_while_gate_unresolved"])
        ax.text(len(df) + 0.6, i, f"{k}/13", ha="left", va="center", fontsize=8, color=INK)
    ax.text(len(df) + 0.6, -0.75, "Eligible while\ngate unresolved", ha="left", va="bottom", fontsize=7, color=MUTED)
    ax.spines[:].set_visible(False)
    ax.set_title("Final authority level (4 = Bounded automation ... 0 = Rollback/isolation); * = unresolved gate",
                 loc="left", fontsize=9, color=MUTED)
    fig.tight_layout(); _save(fig, out, "figure_6_policy_variants"); plt.close(fig)


# ---------------------------------------------------------------------------
def main(out_dir: Path, seed: int = 42, n_mc: int = 10_000, figures: bool = True) -> dict:
    t0 = time.time()
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    df = load_scenarios()
    write(df.drop(columns=["weights"]), out_dir, "scenario_points")

    det = deterministic_shifts(df); write(det, out_dir, "table_10_deterministic_shifts")
    inp = inputs_only_mc(df, n_mc, seed)
    jmc = joint_mc(df, n_mc, seed); jmc["retention_inputs_only"] = inp
    write(jmc, out_dir, "table_10_joint_monte_carlo")
    t10 = table10(det, inp, jmc); write(t10, out_dir, "table_10")

    variants = policy_variants(df)
    t15 = table15(df, variants); write(t15, out_dir, "table_15")
    write(pd.DataFrame({"scenario_id": df.scenario_id, **variants}), out_dir, "table_15_levels")

    t17, per = table17(df); write(t17, out_dir, "table_17")
    write(pd.DataFrame({"scenario_id": df.scenario_id, **per}), out_dir, "table_17_levels")

    a1 = tableA1(df); write(a1, out_dir, "table_A1")

    if figures:
        import matplotlib
        matplotlib.use("Agg")
        figure4(det, jmc, out_dir); figure6(df, variants, t15, out_dir)

    summary = {
        "seed": seed, "n_mc": n_mc, "catalog": str(CATALOG.relative_to(ROOT)),
        "gated_scenarios": int(df.gated.sum()),
        "table_10": t10.to_dict(orient="records"),
        "table_15": t15.to_dict(orient="records"),
        "table_17": t17.to_dict(orient="records"),
        "table_A1": a1[["weights", "boundaries", "final_levels_changed", "C_star", "showcase_codes",
                        "eligible_while_gate_unresolved", "gated_changed_ids"]].to_dict(orient="records"),
        "table_A1_gated_pairs_changed": int(sum(len(x.split(",")) for x in a1.gated_changed_ids if x)),
        "runtime_seconds": round(time.time() - t0, 2),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=float), encoding="utf-8")
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out-dir", type=Path, default=ROOT / "results" / "revision_analyses")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n-mc", type=int, default=10_000)
    ap.add_argument("--no-figures", action="store_true")
    a = ap.parse_args()
    s = main(a.out_dir, a.seed, a.n_mc, figures=not a.no_figures)
    print(pd.DataFrame(s["table_10"])[["perturbation", "provisional", "final"]].to_string(index=False))
    print(pd.DataFrame(s["table_15"]).drop(columns=["eligible_while_gated_ids"]).to_string(index=False))
    print(pd.DataFrame(s["table_17"]).drop(columns=["disagreements"]).to_string(index=False))
    print(pd.DataFrame(s["table_A1"]).to_string(index=False))
    print(f"gated scenario-parameterization pairs changed: {s['table_A1_gated_pairs_changed']} of 312")
    print(f"runtime: {s['runtime_seconds']} s -> {a.out_dir}")
