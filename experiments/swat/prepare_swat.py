#!/usr/bin/env python3
"""Load and partition an authorized local SWaT copy without redistributing it."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np

LABEL_CANDIDATES = ['Normal/Attack','Normal_Attack','label','Label','attack','Attack']
TIME_CANDIDATES = ['Timestamp','timestamp','Time','time','DateTime','datetime']


def _find_col(columns, candidates):
    lower={str(c).strip().lower():c for c in columns}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


def _to_binary_label(series):
    if pd.api.types.is_numeric_dtype(series):
        x=pd.to_numeric(series,errors='coerce').fillna(0).astype(float)
        unique=set(x.unique().tolist())
        if unique.issubset({0.0,1.0}):
            return x.astype(int)
        return (x!=0).astype(int)
    s=series.astype(str).str.strip().str.lower()
    normal_tokens={'normal','0','false','benign','no','none'}
    return (~s.isin(normal_tokens)).astype(int)


def discover_csvs(data_dir: Path):
    files=sorted(Path(data_dir).glob('*.csv'))
    if len(files)<2:
        raise FileNotFoundError('At least two CSV files (normal and attack) are required in the SWaT data directory.')
    normal=[p for p in files if 'normal' in p.name.lower()]
    attack=[p for p in files if any(t in p.name.lower() for t in ['attack','abnormal'])]
    if normal and attack:
        return normal[0], attack[0]
    # Fallback: inspect labels and choose the file with the smallest attack fraction as normal.
    stats=[]
    for p in files:
        df=pd.read_csv(p,nrows=5000)
        col=_find_col(df.columns,LABEL_CANDIDATES)
        frac=0.0 if col is None else float(_to_binary_label(df[col]).mean())
        stats.append((frac,p))
    stats.sort(key=lambda x:x[0])
    return stats[0][1], stats[-1][1]


def load_swat(normal_file, attack_file, label_column=None, timestamp_column=None):
    ndf=pd.read_csv(normal_file)
    adf=pd.read_csv(attack_file)
    label_column=label_column or _find_col(adf.columns,LABEL_CANDIDATES)
    timestamp_column=timestamp_column or _find_col(adf.columns,TIME_CANDIDATES)
    if label_column is None:
        raise ValueError('Could not infer SWaT label column. Pass --label-column explicitly.')
    # Harmonize columns; feature set is the intersection, excluding labels/timestamps and non-numeric columns.
    common=[c for c in ndf.columns if c in adf.columns]
    exclude={label_column}
    if timestamp_column: exclude.add(timestamp_column)
    feature_cols=[]
    for c in common:
        if c in exclude: continue
        n=pd.to_numeric(ndf[c],errors='coerce')
        a=pd.to_numeric(adf[c],errors='coerce')
        if n.notna().mean()>.98 and a.notna().mean()>.98:
            feature_cols.append(c)
    if not feature_cols:
        raise ValueError('No shared numeric process features were found in the SWaT files.')
    Xn=ndf[feature_cols].apply(pd.to_numeric,errors='coerce').interpolate(limit_direction='both').ffill().bfill()
    Xa=adf[feature_cols].apply(pd.to_numeric,errors='coerce').interpolate(limit_direction='both').ffill().bfill()
    yn=np.zeros(len(ndf),dtype=int)
    ya=_to_binary_label(adf[label_column]).to_numpy(dtype=int)
    return Xn,Xa,yn,ya,feature_cols,timestamp_column,adf


def chronological_normal_split(Xn, train_fraction=.80):
    cut=max(1,min(len(Xn)-1,int(len(Xn)*train_fraction)))
    return Xn.iloc[:cut].copy(),Xn.iloc[cut:].copy()
