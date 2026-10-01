"""Run the ladder on the literature benchmark (published HARPS signals with later verdicts).

For each signal: load the host's RVBank series, fit and remove the other accepted signals in
the system (fundamental + first harmonic), and evaluate the ladder at the claimed period.
Writes results/benchmark_features.csv.
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


def main():
    df = pd.read_parquet(os.path.join(ROOT, "data", "rvbank.parquet"))
    bench = pd.read_csv(os.path.join(ROOT, "benchmark_literature.csv"))
    rows = []
    cache = {}
    for _, b in bench.iterrows():
        st = b.rvbank_star
        if st not in cache:
            cache[st] = rvvet.load_star(df, st, clip_sigma=15)
        s = cache[st]
        known = parse_periods(b.other_signals_P_d)
        r = rvvet.vet(s, period=float(b.P_d), known_periods=known, trend=2)
        r.update(signal=b.signal, host=b.host, label=b.label, P_claim=float(b.P_d), K_claim=float(b.K_ms),
                 n_clipped=s.meta.get("n_clipped", 0),
                 prot_lit=b.prot_d, n_known_removed=len(known), is_top=bool(r["top_margin"] >= 0))
        rows.append(r)
        print(f"{b.signal:32s} {b.label:18s} P={b.P_d:9.3f} n={r['n']:4d} dchi2={r['dchi2']:7.1f} "
              f"logFAP={r['log10_fap']:8.2f} top={r['is_top']!s:5s} K={r['K']:.2f}+-{r['sK']:.2f}", flush=True)
    out = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in rows])
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    out.to_csv(os.path.join(ROOT, "results", "benchmark_features.csv"), index=False)


if __name__ == "__main__":
    main()
