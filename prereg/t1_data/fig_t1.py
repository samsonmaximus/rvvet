import numpy as np, pandas as pd, importlib.util, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
spec=importlib.util.spec_from_file_location('t',"run_test_t1.py"); t=importlib.util.module_from_spec(spec); spec.loader.exec_module(t)
fig,axs=plt.subplots(1,2,figsize=(11,4.2))
cols={'ESPRESSO':'#2457c5','HARPS':'#c2412d','NIRPS':'#999999','HARPS_G2':'#22804f','HARPS_K5':'#c2412d'}
for ax,(star,f,title) in zip(axs,[('GJ902','rv_gj902.csv','GJ 902 (RVL-006): REFUTED'),('HD58489','rv_hd58489.csv','HD 58489 (RVL-027): SUPPORTED, weakly')]):
    e=t.EPH[star]; P,T,K=float(e['P']),float(e['Tmax']),float(e['K']); d=t.nightly(pd.read_csv(f))
    p,C,jit=t.fit(d,P,T); insts=sorted(d.inst.unique())
    off={i:p[k] for k,i in enumerate(insts)}; b=p[len(insts)]
    res=d.rv-np.array([off[i] for i in d.inst])-b*(d.bjd-d.bjd.mean())/365.25
    ph=((d.bjd-T)/P)%1
    for i in insts:
        m=d.inst==i; s=np.sqrt(d.err[m]**2+jit[i]**2)
        if i=='NIRPS': continue
        ax.errorbar(ph[m],res[m],s,fmt='o',ms=4,color=cols[i],label=f'{i} ({m.sum()} nights)',alpha=.85)
    x=np.linspace(0,1,300); ax.plot(x,K*np.cos(2*np.pi*x),'k--',lw=1.4,label=f'predicted from 2003-2021 (K={K:.1f})')
    ax.plot(x,p[-1]*np.cos(2*np.pi*x),'k-',lw=1,label=f'fitted at predicted phase (A={p[-1]:.1f}±{np.sqrt(C[-1,-1]):.1f})')
    ax.set_title(title,fontsize=11); ax.set_xlabel(f'phase at P = {P:.3f} d (0 = predicted RV maximum)'); ax.set_ylabel('RV - offsets (m/s)'); ax.legend(fontsize=7.5,loc='lower left'); ax.axhline(0,color='0.8',lw=.6)
    lim=max(3*K, np.nanpercentile(np.abs(res[d.inst!='NIRPS']),95)*1.3); ax.set_ylim(-lim,lim)
fig.suptitle('Pre-registered test T1: velocities taken 2022-2026, after the archive cutoff (NIRPS omitted from plot, jitter 9 m/s)',fontsize=10)
fig.tight_layout(); fig.savefig('fig_t1.png',dpi=140)
