#!/usr/bin/env python3
from pathlib import Path
import sys,numpy as np,pandas as pd
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
sys.path.insert(0,str(ROOT/'src')); sys.path.insert(0,str(HERE))
from common import write_df
from rdfr_ci.monte_carlo import simulate_loss_channels,tail_var

PARAMS=[('digital infrastructure',.0025,.012,1.0),('manufacturing',.0030,.018,1.1),('substation',.0032,.020,1.2),('rail/traffic',.0035,.022,1.15),('hospital',.0038,.025,1.25),('water treatment',.0040,.025,1.20)]

def main(n=100000,seed=42):
    rows=[]
    for i,(sector,sp,cp,scale) in enumerate(PARAMS):
        d=simulate_loss_channels(n=n,seed=seed+i,scale=scale,safety_probability=sp,cascade_probability=cp)
        means={k:float(v.mean()) for k,v in d.items() if k!='total'}; total=float(d['total'].mean()); var,tvar=tail_var(d['total'],.95)
        idx=d['total']>=np.quantile(d['total'],.99); tail_means={k:float(d[k][idx].mean()) for k in means}
        rows.append({'sector':sector,'n':n,'expected_total_loss':total,'VaR95':var,'TailVaR95':tvar,'safety_share_expected_loss':means['safety']/total,'largest_mean_loss_channel':max(means,key=means.get),'largest_top1pct_loss_channel':max(tail_means,key=tail_means.get),'safety_share_top1pct':tail_means['safety']/sum(tail_means.values()),'evidence_class':'SYNTHETIC MONTE CARLO DEMONSTRATION'})
    df=pd.DataFrame(rows); write_df(df,ROOT/'results/tables/table_S4_loss_channel_demo.csv')
    return df
if __name__=='__main__': main()
