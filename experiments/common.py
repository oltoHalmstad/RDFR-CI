from pathlib import Path
import json,sys
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))

def write_df(df,path_csv,index=False):
    path_csv=Path(path_csv); path_csv.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(path_csv,index=index)
    md=path_csv.with_suffix('.md')
    md.write_text(df.to_markdown(index=index),encoding='utf-8')
    return path_csv,md

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))
