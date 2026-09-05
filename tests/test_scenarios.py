from pathlib import Path
from rdfr_ci.scenario_loader import load_catalog
from rdfr_ci.aggregation import weighted_arithmetic,weighted_power_mean,worst_dimension_blend
from rdfr_ci.authority import authority_from_score

ROOT=Path(__file__).resolve().parents[1]

def test_catalog_count_and_sector_count():
    s=load_catalog(ROOT/'scenarios/scenario_catalog.yaml'); assert len(s)==30; assert len({x.sector for x in s})==18

def test_all_scenarios_are_explicitly_illustrative():
    assert all(x.illustrative_or_empirical=='illustrative' for x in load_catalog(ROOT/'scenarios/scenario_catalog.yaml'))

def test_aggregation_change_count_matches_manuscript_analysis():
    changed=0
    for s in load_catalog(ROOT/'scenarios/scenario_catalog.yaml'):
        v=s.values(); w=s.weights
        scores=[weighted_arithmetic(v,w),weighted_power_mean(v,w,2),weighted_power_mean(v,w,3),worst_dimension_blend(v,w)]
        if len({int(authority_from_score(x)) for x in scores})>1: changed+=1
    assert changed==21
