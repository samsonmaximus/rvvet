import numpy as np, pandas as pd, json, importlib.util
spec=importlib.util.spec_from_file_location('t',"run_test_t1.py"); t=importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
def z_of(d,P,T):
    p,C,j=t.fit(d,P,T); return p[-1],np.sqrt(C[-1,-1]),j
def freeamp(d,P):
    p,C,j=t.fit(d,P,2457000.0,free_phase=True); a,b=p[-2],p[-1]; cov=C[-2:,-2:]; v=np.array([a,b]); chi=v@np.linalg.solve(cov,v); return np.hypot(a,b),chi
out={}
for star,f in [('GJ902','rv_gj902.csv'),('HD58489','rv_hd58489.csv')]:
    e=t.EPH[star]; d=t.nightly(pd.read_csv(f)); P,T=float(e['P']),float(e['Tmax'])
    res={}
    for inst in sorted(d.inst.unique()):
        sub=d[d.inst==inst]
        if len(sub)>=5:
            A,s,_=z_of(sub,P,T); res[f'only_{inst}']=dict(n=len(sub),A=A,sA=s,z=A/s)
    # specificity of period: free-phase chi2 (2 dof) across periods
    Ps=np.exp(np.linspace(np.log(2),np.log(150),3000)); chis=[]
    for q in Ps:
        try: chis.append(freeamp(d,q)[1])
        except Exception: chis.append(np.nan)
    chis=np.array(chis); c0=freeamp(d,P)[1]
    res['freephase_chi2_at_P']=c0; res['frac_periods_2_150d_with_higher_chi2']=float(np.nanmean(chis>=c0)); res['best_period_new_data']=float(Ps[np.nanargmax(chis)]); res['best_chi2']=float(np.nanmax(chis))
    # phase specificity: fraction of template phases giving z >= observed
    zs=[]
    for ph in np.linspace(0,1,200,endpoint=False):
        A,s,_=z_of(d,P,T+ph*P); zs.append(A/s)
    z0=z_of(d,P,T)[0]/z_of(d,P,T)[1]; res['z_pred']=z0; res['frac_phases_z_ge_obs']=float(np.mean(np.array(zs)>=z0-1e-9))
    out[star]=res
print(json.dumps(out,indent=1,default=float)); json.dump(out,open('t1_secondary.json','w'),indent=1,default=float)
