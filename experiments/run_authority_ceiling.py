#!/usr/bin/env python3
from pathlib import Path
import sys,pandas as pd
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'src')); sys.path.insert(0,str(HERE))
from common import write_df
from rdfr_ci.authority import authority_ceiling,label
from rdfr_ci.plotting import authority_ceiling_figure
from rdfr_ci.scenario_loader import load_catalog

def main():
    rows=[]
    interpretation={.25:'Full range of deployment states available',.50:'Ceiling not yet binding',.75:'Ceiling approaching; small margin remains',.80:'Threshold at which bounded automation is lost',.90:'Autonomous action permanently excluded',.95:'Assurance investment cannot change the band'}
    for c in [.25,.50,.75,.80,.90,.95]:
        r,s=authority_ceiling(c,.25); rows.append({'C':c,'R_min = w_C*C':r,'Best reachable state':label(s),'Interpretation':interpretation[c]})
    write_df(pd.DataFrame(rows),ROOT/'results/tables/table_5_authority_ceilings.csv')
    sc=load_catalog(ROOT/'scenarios/scenario_catalog.yaml')
    authority_ceiling_figure(ROOT/'results/figures/figure_A1_authority_ceiling',.25,[s.values() for s in sc])
    return rows
if __name__=='__main__': main()
