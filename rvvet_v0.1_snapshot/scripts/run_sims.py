"""Labelled simulations on real HARPS-RVBank sampling and noise.

For each case: take a star's nightly series, replace it with permuted real noise, inject a
planet and/or activity (or nothing), run the ladder blind on the highest peak, and record
the features with the truth. Resume-safe: one parquet file per chunk.

Usage: python run_sims.py OUTDIR NCASES [WORKERS] [SEED]
"""
import json, os, sys, time
from multiprocessing import Pool

import numpy as np
import pandas as pd

import rvvet
from rvvet.periodogram import alias_frequencies, window_peaks
from rvvet.simulate import inject_activity, kepler_rv, permuted_noise

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data")
CLASSES = [("planet", 0.35), ("planet+activity", 0.25), ("activity", 0.30), ("noise", 0.10)]


def select_stars(df, exclude, seed=1, nmax=260):
    """Stars with 40-250 nights, baseline >= 1500 d, median error <= 3 m/s, dLW and H-alpha on
    >= 80% of spectra; benchmark hosts and HD 297396 excluded."""
    d = df[rvvet.quality_mask(df)].copy()
    d["night"] = np.floor(d.bjd - 0.5)
    g = d.groupby("star").agg(nights=("night", "nunique"), t0=("bjd", "min"), t1=("bjd", "max"), me=("e", "median"),
                              cov_dlw=("dlw", lambda x: np.isfinite(x).mean()), cov_ha=("halpha", lambda x: np.isfinite(x).mean()))
    rvsd = d.groupby("star").rv.std()
    ok = (g.nights.between(40, 250) & ((g.t1 - g.t0) >= 1500) & (g.me <= 3) & (g.cov_dlw >= 0.8) & (g.cov_ha >= 0.8)
          & (rvsd.reindex(g.index) <= 20))                   # no binaries or giant planets dominating the noise
    names = sorted(set(g.index[ok]) - set(exclude))
    rng = np.random.default_rng(seed)
    return sorted(rng.choice(names, min(nmax, len(names)), replace=False).tolist())


def one_case(args):
    case_id, star, series_dict, seed = args
    rng = np.random.default_rng(seed)
    s = rvvet.Series(**series_dict)
    s = permuted_noise(s, rng)
    N, T = s.n, s.baseline
    sig = float(np.std(s.y))                                  # effective per-epoch scatter (errors + jitter)
    u = rng.random()
    acc = 0.0
    for cls, p in CLASSES:
        acc += p
        if u < acc:
            break
    rec = dict(case=case_id, star=star, cls=cls, N=N, T=T, sigma_eff=sig)
    y = s.y.copy()
    if "planet" in cls:
        P = float(np.exp(rng.uniform(np.log(1.2), np.log(300))))
        snr = float(np.exp(rng.uniform(np.log(3), np.log(20))))
        K = snr * sig * np.sqrt(2.0 / N)
        e = float(min(rng.beta(0.867, 3.03), 0.8))
        om = rng.uniform(0, 2 * np.pi); tp = rng.uniform(0, P)
        y = y + kepler_rv(s.t, P, K, e, om, s.t[0] + tp)
        rec.update(P_pl=P, K_pl=K, e_pl=e, snr_target=snr)
    s = s.with_y(y)
    if "activity" in cls:
        Prot = float(np.exp(rng.uniform(np.log(8), np.log(60))))
        lam = Prot * float(np.exp(rng.uniform(np.log(1), np.log(10))))
        w = rng.uniform(0.25, 1.2)
        rv_rms = sig * rng.uniform(0.3, 3.0)
        frac = rng.uniform(0, 0.9)
        isnr = float(np.exp(rng.uniform(np.log(0.1), np.log(3))))
        s = inject_activity(s, rng, Prot, lam, w, rv_rms, frac, isnr)
        rec.update(P_rot=Prot, lam=lam, w=w, rv_rms=rv_rms, frac_flux=frac, ind_snr=isnr)
    try:
        r = rvvet.vet(s)
    except Exception as ex:                                  # keep a record of failures
        rec["error"] = repr(ex)
        return rec
    rec.update({k: v for k, v in r.items() if not k.startswith("_") and k != "star"})
    f = 1.0 / r["period"]
    truth, kind = 0, "noise"
    if "planet" in cls:
        fp = 1.0 / rec["P_pl"]
        if abs(f - fp) < 1.0 / T:
            truth, kind = 1, "planet"
        else:
            wp = [q for q, _ in window_peaks(s.t, baseline=T)]
            offs = list(alias_frequencies(fp)) + [abs(fp + sg * q) for q in wp for sg in (1, -1)] + [2 * fp]
            if np.any(np.abs(np.array(offs) - f) < 1.0 / T):
                kind = "planet_alias_or_harmonic"
    if truth == 0 and "activity" in cls:
        fr = 1.0 / rec["P_rot"]
        hk = [abs(f - k * fr) * T for k in range(1, 5)]
        al = [np.min(np.abs(alias_frequencies(k * fr) - f)) * T for k in range(1, 5)]
        if min(hk) < 1.0 or min(al) < 1.0:
            kind = "rotation"
        elif kind == "noise":
            kind = "activity_other"
    rec.update(truth=truth, kind=kind)
    return rec


def main():
    outdir, ncases = sys.argv[1], int(sys.argv[2])
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    seed0 = int(sys.argv[4]) if len(sys.argv) > 4 else 20260929
    os.makedirs(outdir, exist_ok=True)
    df = pd.read_parquet(os.path.join(DATA, "rvbank.parquet"))
    bench = pd.read_csv(os.path.join(DATA, "..", "benchmark_literature.csv"))
    exclude = set(bench.rvbank_star) | {"HD297396"}
    stars = select_stars(df, exclude)
    json.dump(dict(stars=stars, n=len(stars), seed=seed0), open(os.path.join(outdir, "stars.json"), "w"))
    series = {}
    for st in stars:
        s = rvvet.load_star(df, st)
        series[st] = dict(star=st, t=s.t, y=s.y, e=s.e, label=s.label, labels=s.labels, ind=s.ind)
    print(len(stars), "stars; median nights", int(np.median([len(v["t"]) for v in series.values()])), flush=True)
    rng = np.random.default_rng(seed0)
    jobs = [(i, stars[i % len(stars)], None, int(rng.integers(2 ** 31))) for i in range(ncases)]
    chunk = 500
    with Pool(workers) as pool:
        for c0 in range(0, ncases, chunk):
            path = os.path.join(outdir, f"chunk_{c0 // chunk:04d}.parquet")
            if os.path.exists(path):
                continue
            t0 = time.time()
            batch = [(i, st, series[st], sd) for i, st, _, sd in jobs[c0:c0 + chunk]]
            recs = pool.map(one_case, batch, chunksize=8)
            pd.DataFrame(recs).to_parquet(path)
            print(f"chunk {c0 // chunk}: {len(recs)} cases in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
