import numpy as np, pandas as pd, warnings, time, sys; warnings.filterwarnings("ignore")
import rvvet
from rvvet.rules import rule_pass, first_failed_rung
df=pd.read_parquet('data/rvbank.parquet')
b=pd.read_csv('/mnt/user-data/uploads/exoplancsv/methods_paper/archive_run_2026-09-30/archive_blind_rvvet.csv')
rng=np.random.default_rng(20261004)
sample=list(rng.choice(b.star.values,40,replace=False))+['HD297396','HD157172','GJ479','HD129642']
rows=[];t0=time.time()
for st in sample:
    s=rvvet.load_star(df,st,clip_sigma=15)
    r=rvvet.vet(s,period=None,known_periods=[],trend=2); r['star']=st
    rows.append({k:v for k,v in r.items() if not k.startswith('_')})
n=pd.DataFrame(rows); n['rule']=rule_pass(n); n['first_fail']=first_failed_rung(n)
m=n.merge(b,on='star',suffixes=('_new','_old'))
cols=['period','dchi2','log10_fap','K','alias_margin','block_phase_p','growth_rho','ind_max_dchi2','act_log10_fap']
for c in cols:
    a,o=m[c+'_new'].astype(float),m[c+'_old'].astype(float)
    ok=np.isclose(a,o,rtol=1e-6,atol=1e-8,equal_nan=True)
    print(f'{c:16s} identical {ok.sum()}/{len(m)}  max|diff| {np.nanmax(np.abs(a-o)):.3g}')
print('rule identical',(m.rule_new==m.rule_old).sum(),'/',len(m),' first_fail identical',(m.first_fail_new==m.first_fail_old).sum())
print('%.0fs'%(time.time()-t0))
m.to_csv('repro_check.csv',index=False)
