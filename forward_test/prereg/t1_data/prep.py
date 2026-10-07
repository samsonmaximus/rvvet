from astropy.utils import iers; iers.conf.auto_download=False; iers.conf.auto_max_age=None
import pandas as pd, numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
df=pd.read_parquet('../../../data/rvbank.parquet')
coord={s:SkyCoord(df[df.star==s].ra.iloc[0]*u.deg, df[df.star==s].dec.iloc[0]*u.deg) for s in ['GJ902','HD58489']}
ls=EarthLocation.from_geodetic(lon=-70.7375*u.deg, lat=-29.2584*u.deg, height=2400*u.m)  # La Silla 3.6m
h=pd.read_csv('harps_raw.csv')
t=Time(h.mjd.values+h.exptime.values/2/86400,format='mjd',scale='utc',location=ls)
bjd=[]
for i,r in h.iterrows():
    tt=t[i]; bjd.append((tt.tdb+tt.light_travel_time(coord[r.star])).jd)
H=pd.DataFrame(dict(star=h.star,inst=np.where(h.star=='HD58489','HARPS_'+h['mask'],'HARPS'),bjd=bjd,rv=h.rvc_kms*1000,err=h.noise_kms*1000,file=h.file))
cols=['star','inst','adp','file','ncards','mjd','bjd','rv_kms','err_kms','mask','fwhm','catg','drift']
e=pd.concat([pd.read_csv('espnirps_raw_part1.csv'),pd.read_csv('espnirps_raw_part2.csv',header=None,names=cols)])
e=e.drop_duplicates('file')
e=e[((e.inst=='ESPRESSO')&(e.catg=='CCF_A'))|((e.inst=='NIRPS')&(e.catg=='CCF_TELL_CORR_A'))]
E2=pd.DataFrame(dict(star=e.star,inst=e.inst,bjd=e.bjd,rv=e.rv_kms*1000,err=e.err_kms*1000,file=e.file))
A=pd.concat([H,E2],ignore_index=True)
log=[]
n0=len(A); A=A[np.isfinite(A.rv)&np.isfinite(A.err)&(A.err>0)]; log.append(f'missing keywords: {n0-len(A)}')
for s in A.star.unique():
    m=A.star==s; med=A.loc[m,'rv'].median(); bad=m&(abs(A.rv-med)>1000); log.append(f'{s}: other object (>1 km/s from median) dropped {bad.sum()}'); A=A[~bad]
for s in A.star.unique():
    rvb=df[df.star==s].bjd.values; m=A.star==s
    near=m & A.bjd.apply(lambda b: np.min(np.abs(rvb-b))<0.5); log.append(f'{s}: within 0.5 d of RVBank dropped {near.sum()}'); A=A[~near]
print('\n'.join(log))
for s,g in A.groupby('star'):
    print(s, g.inst.value_counts().to_dict())
    g[['inst','bjd','rv','err']].to_csv(f'rv_{s.lower()}.csv',index=False)
    if s=='HD58489':
        g2=g.copy(); g2['inst']='HARPS'; g2[['inst','bjd','rv','err']].to_csv('rv_hd58489_literal.csv',index=False)
A.to_csv('t1_all_velocities.csv',index=False)
