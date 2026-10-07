import numpy as np, pandas as pd, json, hashlib, warnings, datetime as dt, sklearn, platform
warnings.filterwarnings("ignore")
import rvvet
from rvvet.periodogram import fit_jitter
from scipy.optimize import least_squares
df=pd.read_parquet('data/rvbank.parquet'); b=pd.read_parquet('out/archive_scored.parquet')
s=b[b.sig&b.rule&(b.K<100)&b.match.isin(['no_known_planet','other_period_on_known_host'])].copy()
LIT={ # source-checked literature status (2026-10-04)
 'HD157172':('known_planet','HD 157172 b, P=104.84 d, Mayor et al. 2011 (arXiv:1109.2497); in exoplanet.eu, absent from NASA pscomppars'),
 'GJ654':('known_planet','GJ 654 b, P=15.35 d (2024) in exoplanet.eu'),
 'HD4308':('known_planet','HD 4308 b, P=15.56-15.61 d (2005); missed by the 1.5/T period tolerance'),
 'HD183579':('harmonic_of_known','P = half of transiting HD 183579 b (17.47 d)'),
 'GJ17':('activity_in_literature','HD 1581: 15.653 d classed ACT-R (rotation) by Laliotis et al. 2023 (arXiv:2302.10310)'),
 'HD26965':('activity_in_literature','42.3 d classed activity by Laliotis et al. 2023; refuted in the rvvet benchmark'),
 'GJ479':('activity_in_literature','P = Prot/2; photometric Prot 23.1 d (Mignon et al. 2024, A&A, Table 9)'),
 'GJ358':('activity_in_literature','photometric Prot 25.0 d (Mignon et al. 2024, Table 9); signal 26.0 d'),
 'GJ3218':('near_rotation','activity-based Prot 22.3 d (Mignon et al. 2024, Table 12); signal 20.8 d'),
 'GJ3018':('near_rotation','activity-based Prot 27.0 d (Mignon et al. 2024, Table 12); signal 24.5 d'),
 'GJ361':('alias_of_published_candidate','Mignon et al. 2024 candidate at 28.94 d; ladder top peak 26.81 d with alias at 28.91 d'),
}
def ephem(st,P0):
    S=rvvet.load_star(df,st,clip_sigma=15); t,y,e,lab=S.t,S.y,S.e,S.label
    t0=np.round(np.median(t)); tt=(t-t0)/(t.max()-t.min())
    D=np.column_stack([tt,tt**2]); jit,_=fit_jitter(t,y,e,lab,design=D)
    sig=np.sqrt(e**2+jit[lab]**2); L=(lab[:,None]==np.arange(lab.max()+1)).astype(float)
    def res(p):
        P,a,c=p[:3]; off=p[3:3+L.shape[1]]; q=p[3+L.shape[1]:]
        m=a*np.cos(2*np.pi*(t-t0)/P)+c*np.sin(2*np.pi*(t-t0)/P)+L@off+D@q
        return (y-m)/sig
    X=np.column_stack([np.cos(2*np.pi*(t-t0)/P0),np.sin(2*np.pi*(t-t0)/P0),L,D]); w=1/sig
    lin=np.linalg.lstsq(X*w[:,None],y*w,rcond=None)[0]
    p0=np.r_[P0,lin[0],lin[1],lin[2:2+L.shape[1]],lin[2+L.shape[1]:]]
    r=least_squares(res,p0,x_scale='jac'); J=r.jac; chi2=np.sum(r.fun**2); dof=len(y)-len(p0)
    cov=np.linalg.pinv(J.T@J)*max(1,chi2/dof)
    P,a,c=r.x[:3]; K=np.hypot(a,c); phi=np.arctan2(c,a)  # model = K cos(2pi(t-t0)/P - phi)
    # time of max RV nearest t0: 2pi(T-t0)/P = phi
    Tmax=t0+phi/(2*np.pi)*P
    g=np.zeros(len(r.x)); g[1]=-c/(a*a+c*c)*P/(2*np.pi); g[2]=a/(a*a+c*c)*P/(2*np.pi); g[0]=phi/(2*np.pi)
    sT=np.sqrt(g@cov@g); sP=np.sqrt(cov[0,0]); gk=np.zeros(len(r.x)); gk[1]=a/K; gk[2]=c/K; sK=np.sqrt(gk@cov@gk)
    tref=2461557.5  # 2027-07-01
    n=np.round((tref-Tmax)/P); Tn=Tmax+n*P; sTn=np.sqrt(sT**2+(n*sP)**2+2*n*(g@cov[:,0]))
    return dict(P=P,sP=sP,K=K,sK=sK,Tmax_bjd=Tmax,sTmax=sT,T2027_bjd=Tn,sT2027=sTn,phase_unc_2027=sTn/P,n_ep=len(y),jit_med=float(np.median(jit[lab])),rchi2=chi2/dof)
rows=[]
for r in s.itertuples():
    eph=ephem(r.star,r.period)
    lit=LIT.get(r.star,('none_found','no match in NASA pscomppars (coord), exoplanet.eu (name), Laliotis+2023 Table 4, Mignon+2024 Tables 5/9/12' if r.star.startswith('GJ') else 'no match in NASA pscomppars (coord), exoplanet.eu (name), Laliotis+2023 Table 4'))
    flags=[]
    if r.snr_K<3: flags.append('K poorly constrained (snr_K<3) despite low FAP: fit degenerate')
    if r.n<30: flags.append('fewer than 30 nights')
    if r.alias_margin<5: flags.append(f'alias margin {r.alias_margin:.1f} (alias {r.alias_period:.3f} d)')
    if r.match=='other_period_on_known_host': flags.append('host has catalogued planet(s) at other periods')
    rows.append(dict(star=r.star,category=r.match,lit_status=lit[0],lit_note=lit[1],p_trees=r.p_boosting,p_logistic=r.p_logistic,
       log10_fap=r.log10_fap,snr_K=r.snr_K,alias_margin=r.alias_margin,alias_period=r.alias_period,block_phase_p=r.block_phase_p,
       growth_rho=r.growth_rho,ind_max_dchi2=r.ind_max_dchi2,act_period=r.act_period,baseline=r.baseline,flags='; '.join(flags),**eph))
L=pd.DataFrame(rows)
L['open']=L.lit_status.isin(['none_found'])&(L.snr_K>=3)
L=L.sort_values(['open','p_trees'],ascending=[False,False]).reset_index(drop=True)
L.insert(0,'ledger_id',[f'RVL-{i+1:03d}' for i in range(len(L))])
L.to_csv('out/ledger_v1.csv',index=False,float_format='%.12g')
prov=dict(created_utc=dt.datetime.utcnow().isoformat()+'Z',rvvet_version=rvvet.__version__,rvvet_commit='7ae430ed68c85586f4af812a5b5586c3dadce766',
  table4_sha256='ce3d41c54fd213d2ac6292eff8786e2facfc4f73723672d386d8208bac7c30e5',sklearn=sklearn.__version__,python=platform.python_version(),
  catalogue='NASA Exoplanet Archive pscomppars dec<35 fetched 2026-10-04 (nea_xmatch_2026-10-04.txt)',
  selection='top peak per star, 1.2-500 d, Baluev FAP<1%, frozen a-priori rule passes, K<100 m/s, no NASA-catalogued planet at that period',
  ranking='open candidates first (no literature match, snr_K>=3), then by boosted-trees score trained on the released simulations',
  prediction='circular sinusoid; T2027 = time of maximum RV nearest 2027-07-01 with propagated 1-sigma')
json.dump(prov,open('out/ledger_v1_provenance.json','w'),indent=1)
print(L.open.sum(),'open of',len(L)); print(L.lit_status.value_counts())
print(L[['ledger_id','star','P','sP','K','sK','n_ep','p_trees','p_logistic','log10_fap','phase_unc_2027','lit_status','flags']].head(30).round(4).to_string())
