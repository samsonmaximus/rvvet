import glob, numpy as np, pandas as pd, warnings, json; warnings.filterwarnings("ignore")
from rvvet.learn import design, models
from rvvet.rules import rule_pass, first_failed_rung
b=pd.read_parquet('out/archive_run_raw.parquet'); b=b[b.error.isna()].copy()
d=pd.concat([pd.read_parquet(p) for p in sorted(glob.glob('rvvet/sims/chunk_*.parquet'))],ignore_index=True)
if 'error' in d: d=d[d.error.isna()]
det=d[d.log10_fap<-2]; X=design(det); y=det.truth.values.astype(int)
fits={n:m.fit(X,y) for n,m in models().items()}
Xb=design(b)
for n,m in fits.items(): b['p_'+n]=m.predict_proba(Xb[X.columns])[:,1]
b['rule']=rule_pass(b); b['first_fail']=first_failed_rung(b); b['sig']=b.log10_fap<-2
# compare with Sept 30 file
o=pd.read_csv('/mnt/user-data/uploads/exoplancsv/methods_paper/archive_run_2026-09-30/archive_blind_rvvet.csv').set_index('star')
bb=b.set_index('star')
print('rule identical',(bb.rule==o.rule.loc[bb.index]).mean(),' first_fail identical',(bb.first_fail==o.first_fail.loc[bb.index]).mean(),
      ' max|dp_boost|',np.abs(bb.p_boosting-o.p_boosting.loc[bb.index]).max().round(4),' max|dp_logit|',np.abs(bb.p_logistic-o.p_logistic.loc[bb.index]).max().round(4))
# catalogue
cat=pd.read_csv('nea_xmatch_2026-10-04.txt',sep='|',comment='#',header=None,
   names=['star','pl_name','host','P','K','disc_year','disc_pub','facility','method','sep'])
cat=cat[(cat.sep<60)&(cat.P>0)]
def match(st,P,T):
    g=cat[cat.star==st]
    if g.empty: return ('no_known_planet','')
    f=1/P; best=None
    for r in g.itertuples():
        q=r.P
        if abs(f-1/q)<1.5/T: return ('catalogued',f'{r.pl_name}|{r.disc_pub}|{r.facility}|{r.method}')
    for r in g.itertuples():
        q=r.P
        for a in (1/365.25,1.0027379,1/29.53):
            if abs(abs(f-1/q)-a)<1.5/T or abs(f+1/q-a)<1.5/T: return ('alias_of_catalogued',f'{r.pl_name}')
        for h in (2,3,0.5,1/3):
            if abs(f-h/q)<1.5/T: return ('harmonic_of_catalogued',f'{r.pl_name}')
    return ('other_period_on_known_host',';'.join(g.pl_name))
m=[match(s,P,T) for s,P,T in zip(b.star,b.period,b.baseline)]
b['match']=[x[0] for x in m]; b['match_detail']=[x[1] for x in m]
b.to_parquet('out/archive_scored.parquet')
