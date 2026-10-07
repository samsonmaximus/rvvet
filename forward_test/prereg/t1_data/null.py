import numpy as np, pandas as pd, importlib.util, json
spec=importlib.util.spec_from_file_location('t',"run_test_t1.py"); t=importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
rng=np.random.default_rng(42); out={}
for star,f,zobs in [('HD58489','rv_hd58489.csv',3.960),('GJ902','rv_gj902.csv',0.545)]:
    e=t.EPH[star]; d=t.nightly(pd.read_csv(f)); P,T=float(e['P']),float(e['Tmax'])
    _,_,jit=t.fit(d,P,T)
    zs=[];zp=[]
    for k in range(1000):
        dd=d.copy(); dd['rv']=rng.normal(0,np.sqrt(dd.err**2+np.array([jit[i] for i in dd.inst])**2))
        p,C,_=t.fit(dd,P,T); zs.append(p[-1]/np.sqrt(C[-1,-1]))
    zs=np.array(zs); out[star]=dict(null_P_z_ge_obs=float((zs>=zobs).mean()),null_z_sd=float(zs.std()))
    # planet-at-predicted-K simulation: inject predicted signal into white noise
    zi=[]
    for k in range(1000):
        dd=d.copy(); dd['rv']=float(e['K'])*np.cos(2*np.pi*(dd.bjd-T)/P)+rng.normal(0,np.sqrt(dd.err**2+np.array([jit[i] for i in dd.inst])**2))
        p,C,_=t.fit(dd,P,T); zi.append(p[-1]/np.sqrt(C[-1,-1]))
    zi=np.array(zi); out[star].update(planet_P_z_le_obs=float((zi<=zobs).mean()),planet_median_z=float(np.median(zi)))
print(json.dumps(out,indent=1))
json.dump(out,open('t1_null.json','w'),indent=1)
