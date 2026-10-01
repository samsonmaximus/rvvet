"""False-alarm calibration of the detection statistic on noise-only series.

For every simulation star, draw M noise-only series of two kinds on the star's real nightly
sampling: (a) the star's own RVs permuted within each instrument label (real, heavy-tailed noise
with the real error bars), and (b) Gaussian noise with the star's error bars and its per-label
maximum-likelihood jitter. Each series goes through the detection step of the ladder with the
same preprocessing as the simulations (15-sigma clip at loading, quadratic trend). Both
statistics are recorded: the likelihood ratio with the jitter profiled (``log10_fap``, used by
the ladder) and Delta chi^2 with the jitter fixed at its planet-free value (``log10_fap_h0``,
used by rvvet 0.1).

Usage: python fap_calibration.py OUT.parquet [M] [WORKERS] [SEED]
"""
import json, os, sys, time
from multiprocessing import Pool

import numpy as np
import pandas as pd

import rvvet
from rvvet.ladder import detect, prewhiten
from rvvet.periodogram import fit_jitter
from rvvet.simulate import permuted_noise

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")


def one(args):
    star, sd, kind, seed = args
    rng = np.random.default_rng(seed)
    s = rvvet.Series(**sd)
    if kind == "permuted":
        s = permuted_noise(s, rng)
    else:
        jit, _ = fit_jitter(s.t, s.y, s.e, s.label)
        s = s.with_y(rng.normal(0.0, np.sqrt(s.e ** 2 + jit[s.label] ** 2)))
    s, _ = prewhiten(s, [], trend=2)
    D = detect(s)
    return dict(star=star, kind=kind, seed=seed, n=s.n, period=1 / D["f0"], z0=D["z0"], z_h0=D["z_h0"],
                log10_fap=D["log10_fap"], log10_fap_h0=D["log10_fap_h0"], jitter_scale=D["jscale"])


def main():
    out = sys.argv[1]
    M = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    seed0 = int(sys.argv[4]) if len(sys.argv) > 4 else 20260930
    stars = json.load(open(os.path.join(ROOT, "sims", "stars.json")))["stars"]
    df = pd.read_parquet(os.path.join(ROOT, "data", "rvbank.parquet"))
    ser = {}
    for st in stars:
        s = rvvet.load_star(df, st, clip_sigma=15)
        ser[st] = dict(star=st, t=s.t, y=s.y, e=s.e, label=s.label, labels=s.labels, ind={})
    rng = np.random.default_rng(seed0)
    jobs = [(st, ser[st], kind, int(rng.integers(2 ** 31))) for kind in ("permuted", "gaussian")
            for st in stars for _ in range(M)]
    t0 = time.time()
    with Pool(workers) as p:
        recs = p.map(one, jobs, chunksize=20)
    pd.DataFrame(recs).to_parquet(out)
    print(f"{len(recs)} series in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
