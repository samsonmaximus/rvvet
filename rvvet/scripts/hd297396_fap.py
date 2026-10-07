"""Why the generic ladder gives HD 297396 b a much smaller false-alarm probability than the discovery
paper does (Sect. 7). Writes paper/numbers_hdfap.tex and results/hd297396_fap.json.

The generic pipeline (analyze.py) fits one offset and one jitter per era (before and after the 2015
fibre upgrade), removes a quadratic trend, and takes the Baluev (2008) FAP of the likelihood ratio
with the jitter scale refitted under the alternative. This script recomputes that FAP

  1. with the jitters held at their planet-free values (Delta chi^2 in the H0 frame), and
  2. without the discrepant night of 2009 April 1 (BJD 2454922.53) that the discovery paper
     identifies, with both statistics.

Needs data/rvbank.parquet (rvvet/scripts/load_rvbank.py). Run in the environment of
requirements-paper.txt:  python rvvet/scripts/hd297396_fap.py
"""
import json, os
import numpy as np
import pandas as pd

import rvvet
from rvvet import ladder

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
P, NIGHT_BJD = 4.26837, 2454922.53

df = pd.read_parquet(os.path.join(ROOT, "data", "rvbank.parquet"))
s = rvvet.load_star(df, "HD297396", clip_sigma=15)
k = int(np.argmin(abs(s.t - NIGHT_BJD)))
assert abs(s.t[k] - NIGHT_BJD) < 0.5, "discrepant night not found"
out = {"period": P, "discrepant_night_bjd": float(s.t[k])}
for tag, ser in (("all", s), ("without_night", s.subset(np.arange(s.n) != k))):
    r = rvvet.vet(ser, period=P, trend=2)
    w, _ = ladder.prewhiten(ser, [], trend=2)
    d = ladder.detect(w, period=P)
    assert abs(d["log10_fap"] - r["log10_fap"]) < 1e-9
    out[tag] = dict(n=int(ser.n), log10_fap_rescaled=float(r["log10_fap"]), log10_fap_planet_free=float(d["log10_fap_h0"]),
                    jitter_planet_free=dict(zip(ser.labels, np.round(d["jit0"], 2).tolist())),
                    jitter_rescaled=dict(zip(ser.labels, np.round(d["jit"], 2).tolist())))

# The discovery paper's analytic (Baluev) values with four groups of programmes, band 1.05-1000 d:
# 2.2e-3 with all 104 epochs and 6.7e-6 without the night (its Sect. 4.2; its simulated FAP is 1.4e-3).
PAPER1_ANALYTIC = {"all": 2.2e-3, "without_night": 6.7e-6}
for tag in PAPER1_ANALYTIC:
    out[tag]["paper1_analytic_over_planet_free"] = PAPER1_ANALYTIC[tag] / 10 ** out[tag]["log10_fap_planet_free"]
json.dump(out, open(os.path.join(ROOT, "results", "hd297396_fap.json"), "w"), indent=1)
A, B = out["all"], out["without_night"]
r = sorted(out[t]["paper1_analytic_over_planet_free"] for t in PAPER1_ANALYTIC)
M = {"HDfapHz": f"{A['log10_fap_planet_free']:.1f}", "HDfapNoNight": f"{B['log10_fap_rescaled']:.1f}",
     "HDfapHzNoNight": f"{B['log10_fap_planet_free']:.1f}", "HDratioLo": f"{r[0]:.0f}", "HDratioHi": f"{r[1]:.0f}"}
lines = ["% Written by rvvet/scripts/hd297396_fap.py (do not edit by hand)"]
lines += [r"\newcommand{\nm%s}{%s}" % (a, v) for a, v in M.items()]
open(os.path.join(ROOT, "paper", "numbers_hdfap.tex"), "w").write("\n".join(lines) + "\n")
print(json.dumps(out, indent=1))
print("\n".join(lines))
