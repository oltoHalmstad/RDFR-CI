"""Deterministic checks of experiments/run_revision_analyses.py against manuscript values."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import run_revision_analyses as ra  # noqa: E402


@pytest.fixture(scope="module")
def df():
    return ra.load_scenarios()


def test_table10_deterministic_rows(df):
    det = ra.deterministic_shifts(df)
    t = ra.table10(det, inputs_only=__import__("numpy").ones(30), jmc=ra.joint_mc(df, 50, 42))
    got = {r.perturbation: (r.provisional_value, r.final_value) for r in t.itertuples()}
    assert got["All boundaries -0.05"] == (13, 8)
    assert got["All boundaries -0.025"] == (5, 2)
    assert got["All boundaries +0.025"] == (3, 1)
    assert got["All boundaries +0.05"] == (7, 2)
    assert got["Single boundary +/-0.025 (largest of 8 settings)"] == (3, 1)
    assert got["Single boundary +/-0.05 (largest of 8 settings)"] == (6, 3)


def test_table15_counts(df):
    t = ra.table15(df, ra.policy_variants(df)).set_index("variant")
    exp = {"Fixed playbook": (12, 24, 6, -0.01, "15 / 14 / 1 / 0 / 0"),
           "Score-only": (6, 0, 0, 0.94, "1 / 9 / 12 / 8 / 0"),
           "Gates-only": (0, 16, 12, -0.25, "17 / 0 / 7 / 6 / 0"),
           "Full RDFR-CI": (0, 0, 0, 0.71, "1 / 3 / 13 / 13 / 0")}
    for v, (e, a, b, rho, lv) in exp.items():
        r = t.loc[v]
        assert (r.eligible_while_gate_unresolved, r.above_provisional, r.bounded_automation_C_ge_0_5) == (e, a, b)
        assert round(r.spearman_rci_restriction, 2) == rho
        assert r.levels_4_3_2_1_0 == lv


def test_table17(df):
    t, _ = ra.table17(df)
    t = t.set_index("method")
    exp = {"Full RDFR-CI": (30, 1.00, 0, 0, 0.25, 0.71, "1/3/13/13/0", "2, 2"),
           "AI-SOC-style score (no C)": (28, 0.95, 1, 0, 0.18, 0.69, "1/5/11/13/0", "3, 3"),
           "5 x 5 risk matrix": (17, 0.63, 1, 0, 0.19, 0.29, "3/8/12/7/0", "2, 2"),
           "Worst-dimension rule": (3, 0.30, 0, 19, 0.63, 0.73, "0/1/2/8/19", "0, 0")}
    for m, e in exp.items():
        r = t.loc[m]
        assert (r.agreement, round(r.kappa_quadratic, 2), r.eligible_C_ge_0_65, r.level0,
                round(r.rho_C, 2), round(r.rho_RCI, 2), r.levels_4_3_2_1_0, r.water_context_D0_D025) == e
    assert (t.loc["AI-SOC-style score (no C)", "higher"], t.loc["AI-SOC-style score (no C)", "lower"]) == (2, 0)
    assert (t.loc["5 x 5 risk matrix", "higher"], t.loc["Worst-dimension rule", "lower"]) == (13, 27)
    orig = t.loc["AI-SOC original weights (sensitivity)"]
    assert orig.agreement == 27 and round(orig.kappa_quadratic, 2) == 0.93


def test_tableA1(df):
    a1 = ra.tableA1(df)
    exp_changed = ["0 (0 up / 0 down)", "8 (0 up / 8 down)", "2 (2 up / 0 down)", "5 (5 up / 0 down)",
                   "1 (1 up / 0 down)", "4 (0 up / 4 down)", "3 (3 up / 0 down)", "9 (9 up / 0 down)",
                   "1 (0 up / 1 down)", "8 (0 up / 8 down)", "1 (1 up / 0 down)", "5 (5 up / 0 down)",
                   "1 (1 up / 0 down)", "9 (1 up / 8 down)", "5 (5 up / 0 down)", "7 (7 up / 0 down)",
                   "2 (2 up / 0 down)", "8 (0 up / 8 down)", "4 (4 up / 0 down)", "5 (5 up / 0 down)",
                   "1 (0 up / 1 down)", "5 (0 up / 5 down)", "5 (5 up / 0 down)", "9 (9 up / 0 down)"]
    exp_cstar = [0.80, 0.60, 1.00, 0.80, 1.00, 0.75, 1.25, 1.00, 0.57, 0.43, 0.71, 0.57,
                 1.33, 1.00, 1.67, 1.33, 0.91, 0.69, 1.14, 0.91, 0.71, 0.53, 0.89, 0.71]
    assert list(a1.final_levels_changed) == exp_changed
    assert [round(x, 2) for x in a1.C_star] == exp_cstar
    codes = list(a1.showcase_codes)
    assert codes[9] == "3 2 2 2 1 1"
    assert all(c == ("3 2 2 2 2 1" if i % 4 == 1 else "4 2 2 2 2 1") for i, c in enumerate(codes) if i != 9)
    assert (a1.eligible_while_gate_unresolved == 0).all()
    assert [x for x in a1.gated_changed_ids if x] == ["HOSP-001"]


def test_interval_columns():
    t11 = ra.table11_intervals()
    assert list(t11.interval_windows) == ["1.38-2.04%", "9.44-10.99%", "15.36-17.26%"]
    assert list(t11.interval_blocks) == ["0.86-3.26%", "7.80-13.20%", "13.27-19.84%"]
    assert list(t11.exceedance_distinguishable_blocks) == ["No", "Yes", "Yes"]
    t12 = ra.table12_intervals()
    assert list(t12.interval_events) == ["0.43-0.95", "0.00-0.38", "0.02-0.48", "0.15-0.72"]
    assert [round(x, 3) for x in t12.R_CI] == [0.478, 0.606, 0.582, 0.534]
