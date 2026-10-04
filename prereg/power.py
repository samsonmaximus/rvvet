import numpy as np, pandas as pd, json
L=pd.read_csv('out/ledger_v1.csv').set_index('star'); df=pd.read_parquet('data/rvbank.parquet')
SIG={'ESPRESSO':0.5,'HARPS':1.0,'NIRPS':2.5}   # nominal per-epoch errors (m/s), fixed before any velocity is read
out={}
for st,f,sig_h in [('GJ902','prereg/ts_gj902.csv',1.0),('HD58489','prereg/ts_hd58489.csv',1.5)]:
    r=L.loc[st]; ts=pd.read_csv(f); ts['bjd']=ts.mjd+2400000.5
    rvb=df[df.star==st].bjd.values
    ts=ts[[np.min(np.abs(rvb-b))>0.5 for b in ts.bjd]]
    ts['night']=np.floor(ts.bjd-0.2).astype(int)   # nights from local noon at La Silla/Paranal (~16:43 UT)
    g=ts.groupby(['inst','night']).bjd.mean().reset_index()
    sig={**SIG,'HARPS':sig_h}; e=np.array([np.hypot(sig[i],r.jit_med) for i in g.inst])
    t=g.bjd.values; insts=sorted(g.inst.unique())
    X0=np.column_stack([(g.inst==i).astype(float) for i in insts]+[(t-t.mean())/365.25])
    rng=np.random.default_rng(0); zs=[]
    for k in range(4000):
        P=rng.normal(r.P,r.sP); T=rng.normal(r.Tmax_bjd,r.sTmax)
        c_true=np.cos(2*np.pi*(t-T)/P); c_pred=np.cos(2*np.pi*(t-r.Tmax_bjd)/r.P)
        W=1/e**2; X=np.column_stack([X0,c_pred])
        A=np.linalg.solve((X*W[:,None]).T@X,(X*W[:,None]).T@(r.K*c_true))[-1]
        sA=np.sqrt(np.linalg.inv((X*W[:,None]).T@X)[-1,-1]); zs.append(A/sA)
    zs=np.array(zs)
    out[st]=dict(n_spectra=int(len(ts)),n_nights_by_inst=g.inst.value_counts().to_dict(),sigma_A=float(sA),K_pred=float(r.K),sK=float(r.sK),
       expected_z_median=float(np.median(zs)),P_z_ge_3=float((zs>=3).mean()),P_z_ge_2=float((zs>=2).mean()),
       phase_unc_cycles_mid=float(np.hypot(r.sTmax,np.median(np.round((t-r.Tmax_bjd)/r.P))*r.sP)/r.P))
print(json.dumps(out,indent=1)); json.dump(out,open('prereg/power.json','w'),indent=1)
