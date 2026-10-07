import numpy as np, pandas as pd, warnings, time, json, hashlib, subprocess; warnings.filterwarnings("ignore")
import rvvet
from rvvet.rules import rule_pass, first_failed_rung
from multiprocessing import Pool
df=pd.read_parquet('data/rvbank.parquet')
def one(st):
    try:
        s=rvvet.load_star(df,st,clip_sigma=15)
        if s.n<20 or s.baseline<100: return None
        r=rvvet.vet(s,period=None,known_periods=[],trend=2); r['star']=st
        return {k:v for k,v in r.items() if not k.startswith('_')}
    except Exception as ex: return dict(star=st,error=str(ex)[:200])
if __name__=='__main__':
    stars=sorted(df.star.unique()); t0=time.time()
    with Pool(4) as p: rows=[r for r in p.map(one,stars,chunksize=8) if r is not None]
    b=pd.DataFrame(rows); b.to_parquet('out/archive_run_raw.parquet')
    print('stars in table',len(stars),'eligible',len(b),'%.0fs'%(time.time()-t0))
