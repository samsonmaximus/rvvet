"""Run the ladder on the literature benchmark (published HARPS signals with later verdicts).

For each signal: load the host's RVBank series (15-sigma gross-outlier clip), fit and remove the
other accepted signals in the system as Keplerian orbits together with a quadratic trend, and
evaluate the ladder at the claimed period: the highest point within 0.5/T of it (adopted), and
for the sensitivity analysis within 0.25/T (the first-pass window) and at the period itself.
Writes results/benchmark_features.csv (0.5/T) and results/benchmark_windows.csv (all three).
"""
import os, sys
import numpy as np
import pandas as pd

import rvvet

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")


def parse_periods(x):
    if not isinstance(x, str) or not x.strip():
        return []
    out = []
    for tok in x.split(";"):
        try:
            out.append(float(tok))
        except ValueError:
            pass
    return out


WINDOWS = (0.5, 0.25, 0.0)       # half-width (1/T) around the claimed period: adopted, first pass, exact


def main():
    df = pd.read_parquet(os.path.join(ROOT, "data", "rvbank.parquet"))
    bench = pd.read_csv(os.path.join(ROOT, "benchmark_literature.csv"))
    rows, wrows = [], []
    cache = {}
    for _, b in bench.iterrows():
        st = b.rvbank_star
        if st not in cache:
            cache[st] = rvvet.load_star(df, st, clip_sigma=15)
        s = cache[st]
        known = parse_periods(b.other_signals_P_d)
        for w in WINDOWS:
            r = rvvet.vet(s, period=float(b.P_d), known_periods=known, trend=2, period_window=w)
            r.update(signal=b.signal, host=b.host, label=b.label, P_claim=float(b.P_d), K_claim=float(b.K_ms),
                     n_clipped=s.meta.get("n_clipped", 0), prot_lit=b.prot_d, n_known_removed=len(known),
                     is_top=bool(r["top_margin"] >= 0), window=w)
            wrows.append(r)
            if w == WINDOWS[0]:
                rows.append(r)
                print(f"{b.signal:32s} {b.label:18s} P={b.P_d:9.3f} n={r['n']:4d} dchi2={r['dchi2']:7.1f} "
                      f"logFAP={r['log10_fap']:8.2f} top={r['is_top']!s:5s} K={r['K']:.2f}+-{r['sK']:.2f} "
                      f"offset={r['period_offset']:+.2f}/T", flush=True)
    clean = lambda rs: pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in rs])
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    clean(rows).to_csv(os.path.join(ROOT, "results", "benchmark_features.csv"), index=False)
    clean(wrows).to_csv(os.path.join(ROOT, "results", "benchmark_windows.csv"), index=False)


if __name__ == "__main__":
    main()
