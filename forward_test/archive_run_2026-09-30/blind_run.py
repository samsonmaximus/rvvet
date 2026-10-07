import sys, numpy as np, pandas as pd, warnings, time; warnings.filterwarnings("ignore")
import rvvet
k,K=int(sys.argv[1]),int(sys.argv[2])
df=pd.read_parquet('data/rvbank.parquet')
stars=sorted(df.star.unique())[k::K]; rows=[]; t0=time.time()
for st in stars:
    try:
        s=rvvet.load_star(df,st,clip_sigma=15)
        if s.n<20 or s.baseline<100: continue
        r=rvvet.vet(s,period=None,known_periods=[],trend=2)
        r['star']=st; rows.append({a:v for a,v in r.items() if not a.startswith('_')})
    except Exception as ex: rows.append(dict(star=st,error=str(ex)[:200]))
pd.DataFrame(rows).to_parquet(f'blind_{k}.parquet'); print(k,len(rows),'%.0fs'%(time.time()-t0))
