#!/usr/bin/env python3
"""Install manuscript-facing v1.3 table CSVs without regenerating stale template content."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
ALIASES={'1':'table_1_research_streams.csv','2':'table_2_ai_failure_modes.csv','3':'table_3_independent_gates.csv','4':'table_4_authority_bands.csv','5':'table_5_authority_ceilings.csv','6':'table_6_evidence_layers.csv','7':'table_7_manuscript_detection_operating_points.csv','8':'table_8_a11_threshold_transfer.csv','9':'table_9_constructed_event_challenge.csv','10':'table_10_six_sector_showcases.csv','11':'table_11_final_action_authority.csv','B1':'table_B1_swat_protocol.csv','C1':'table_C1_validation_metrics.csv','C2':'table_C2_stop_conditions.csv'}

def main():
    src=ROOT/'paper/manuscript_tables'; dst=ROOT/'results/tables'; dst.mkdir(parents=True,exist_ok=True)
    for label,name in ALIASES.items():
        p=src/f'table_{label}.csv'
        if p.exists():
            shutil.copy2(p,dst/name); shutil.copy2(p,dst/f'table_{label}.csv')
    print('Installed manuscript-facing v1.3 table CSVs. Publication figure binaries are release-package artifacts; numerical figure generators remain diagnostic.')
if __name__=='__main__': main()
