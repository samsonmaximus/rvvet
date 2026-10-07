import numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
import rvvet
from rvvet.rules import rule_pass, first_failed_rung
df=pd.read_parquet('data/rvbank.parquet'); L=pd.read_csv('out/ledger_v1.csv')
cat=pd.read_csv('nea_xmatch_2026-10-04.txt',sep='|',comment='#',header=None,names=['star','pl','host','P','K','y','pub','fac','m','sep'])
cat=cat[(cat.sep<60)&(cat.P>0)]
eu={'HD143361':[1057],'HD107148':[48.056,18.3267],'HD183263':[626.5,4971.3],'HD190647':[1038.1],'HD224538':[1202.1],'HD38283':[363.2],'HIP17157':[22315.6],'HIP54597':[3274],'GJ393':[7.02679],'GJ740':[2.37756],'HD48265':[789.6,10418],'GJ9827':[1.2089765,3.648086,6.20183]}
out=[]
for r in L[L.category=='other_period_on_known_host'].itertuples():
    S=rvvet.load_star(df,r.star,clip_sigma=15)
    kp=sorted(set(cat[cat.star==r.star].P.round(4).tolist()+eu.get(r.star,[])))
    kp=[p for p in kp if p<3*S.baseline]
    try:
        v=rvvet.vet(S,period=None,known_periods=kp,trend=2); v['star']=r.star
        out.append(dict(star=r.star,P_blind=r.P,known=kp,P_after=v['period'],log10_fap_after=v['log10_fap'],K_after=v['K'],same=abs(1/v['period']-1/r.P)<1.5/S.baseline,rule=bool(rule_pass(pd.DataFrame([v])).iloc[0]),ff=first_failed_rung(pd.DataFrame([v])).iloc[0]))
    except Exception as ex: out.append(dict(star=r.star,err=str(ex)[:80]))
o=pd.DataFrame(out); print(o.round(3).to_string()); o.to_csv('out/known_host_recheck.csv',index=False)
