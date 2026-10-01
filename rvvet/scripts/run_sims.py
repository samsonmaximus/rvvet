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
from rvvet.data import night_index
from rvvet.periodogram import window_peaks
from rvvet.simulate import inject_activity, kepler_rv, label_peak, permuted_noise

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "..", "data")
CLASSES = [("planet", 0.35), ("planet+activity", 0.25), ("activity", 0.30), ("noise", 0.10)]


def select_stars(df, exclude, seed=1, nmax=260):
    """Stars with 40-250 nights, baseline >= 1500 d, median error <= 3 m/s, dLW and H-alpha on
    >= 80% of spectra, RV standard deviation <= 20 m/s; benchmark hosts and HD 297396 excluded."""
    d = df[rvvet.quality_mask(df)].copy()
    d["night"] = night_index(d.bjd.values)
    g = d.groupby("star").agg(nights=("night", "nunique"), t0=("bjd", "min"), t1=("bjd", "max"), me=("e", "median"),
                              cov_dlw=("dlw", lambda x: np.isfinite(x).mean()), cov_ha=("halpha", lambda x: np.isfinite(x).mean()))
    rvsd = d.groupby("star").rv.std()
    ok = (g.nights.between(40, 250) & ((g.t1 - g.t0) >= 1500) & (g.me <= 3) & (g.cov_dlw >= 0.8) & (g.cov_ha >= 0.8)
          & (rvsd.reindex(g.index) <= 20))                   # no binaries or giant planets dominating the noise
    names = sorted(set(g.index[ok]) - set(exclude))
    rng = np.random.default_rng(seed)
    return sorted(rng.choice(names, min(nmax, len(names)), replace=False).tolist())


def loguniform(rng, lo, hi):
    return float(np.exp(rng.uniform(np.log(lo), np.log(hi))))


def one_case(args):
    """One simulated case. Priors (v0.2):
    planet     P log-uniform 1.2-300 d; K/sigma log-uniform 0.15-3 (sigma = the star's nightly
               scatter), so the amplitude does not depend on the number of epochs;
               e ~ Beta(0.867, 3.03) (Kipping 2013) truncated at 0.8 by redrawing
    activity   P_rot log-uniform 3-150 d; lambda / P_rot log-uniform 1-30; w uniform 0.25-1.2;
               RV rms / sigma log-uniform 0.2-3; flux-term share uniform 0-0.9;
               indicators: with probability 0.8 coupled, base amplitude log-uniform 0.1-3 times
               each indicator's scatter, times a per-indicator factor 10^N(0, 0.3), and a phase
               lag theta ~ U(-45, 45) deg with respect to G (bisector: 90 +- 45 deg);
               otherwise no indicator signal
    The vetting uses the same preprocessing as the benchmark: 15-sigma clip, quadratic trend."""
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
        P = loguniform(rng, 1.2, 300)
        k_rel = loguniform(rng, 0.15, 3.0)
        K = k_rel * sig
        e = 1.0
        while e > 0.8:
            e = float(rng.beta(0.867, 3.03))
        om = rng.uniform(0, 2 * np.pi); tp = rng.uniform(0, P)
        y = y + kepler_rv(s.t, P, K, e, om, s.t[0] + tp)
        rec.update(P_pl=P, K_pl=K, e_pl=e, K_rel=k_rel, snr_target=K / (sig * np.sqrt(2.0 / N)))
    s = s.with_y(y)
    if "activity" in cls:
        Prot = loguniform(rng, 3, 150)
        lam = Prot * loguniform(rng, 1, 30)
        w = rng.uniform(0.25, 1.2)
        rv_rms = sig * loguniform(rng, 0.2, 3.0)
        frac = rng.uniform(0, 0.9)
        coupled = rng.random() < 0.8
        base = loguniform(rng, 0.1, 3.0) if coupled else 0.0
        amps = {k: base * 10 ** rng.normal(0, 0.3) for k in s.ind}
        angles = {k: np.radians((90.0 if k == "bis" else 0.0) + rng.uniform(-45, 45)) for k in s.ind}
        s = inject_activity(s, rng, Prot, lam, w, rv_rms, frac, amps, angles)
        rec.update(P_rot=Prot, lam=lam, lam_rot=lam / Prot, w=w, rv_rms=rv_rms, frac_flux=frac,
                   ind_coupled=bool(coupled), ind_snr=base)
    try:
        r = rvvet.vet(s, trend=2)
    except Exception as ex:                                  # keep a record of failures
        rec["error"] = repr(ex)
        return rec
    rec.update({k: v for k, v in r.items() if not k.startswith("_") and k != "star"})
    wp = window_peaks(s.t, baseline=T)
    truth, kind = label_peak(1.0 / r["period"], T, rec.get("P_pl"), rec.get("P_rot"), rec.get("lam"), wp)
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
        s = rvvet.load_star(df, st, clip_sigma=15)
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
