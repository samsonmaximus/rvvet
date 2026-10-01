# Parse HARPS-RVBank table4.dat (Perdelwitz et al. 2024, corrected 2026-04-20) into a parquet file.
import gzip, numpy as np, pandas as pd, sys
spec = [  # (name, first byte, last byte) from the CDS ReadMe (1-indexed, inclusive)
 ('star',1,14),('ra',16,35),('dec',37,57),('bjd',59,73),('rv',75,87),('e',89,98),('rvdrs',100,117),('e_drs',119,127),
 ('rv_raw',129,141),('crx',206,219),('e_crx',221,233),('dlw',235,246),('e_dlw',248,257),('halpha',259,267),('e_halpha',269,276),
 ('nad1',278,286),('nad2',298,306),('flag',318,322),('fwhm',324,335),('contrast',337,349),('bis',351,371),('snr',384,388),
 ('drift',426,432),('nzp',449,458),('prog',563,576),('dpr',638,660),('rhk',662,682)]
colspecs = [(a-1, b) for _, a, b in spec]; names = [s[0] for s in spec]
df = pd.read_fwf(sys.argv[1] if len(sys.argv) > 1 else 'table4.dat.gz', colspecs=colspecs, names=names, compression='gzip',
                 dtype={'star': str, 'prog': str, 'dpr': str}, na_values=['-', ''])
for c in names:
    if c not in ('star', 'prog', 'dpr'):
        df[c] = pd.to_numeric(df[c], errors='coerce')
df['star'] = df.star.str.strip()
df.to_parquet(sys.argv[2] if len(sys.argv) > 2 else 'rvbank.parquet')
print(len(df), 'rows', df.star.nunique(), 'stars')
print(df[df.star == 'HD297396'][['bjd', 'rv', 'e', 'dlw', 'halpha', 'bis', 'snr', 'prog']].head(3))
