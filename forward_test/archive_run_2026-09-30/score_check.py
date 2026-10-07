"""Check that the classifier scores stored in archive_blind_rvvet.csv are what the paper's classifiers give.

Trains the logistic regression and the boosted trees of rvvet.learn on all significant simulated peaks
(as analyze.py does for the benchmark) and scores the stored ladder features of the 1198 stars.
Run from this folder in the environment of ../../requirements-paper.txt: python score_check.py
"""
import glob, numpy as np, pandas as pd, warnings; warnings.filterwarnings("ignore")
from rvvet.learn import design, models

o = pd.read_csv("archive_blind_rvvet.csv")
d = pd.concat([pd.read_parquet(p) for p in sorted(glob.glob("../../sims/chunk_*.parquet"))], ignore_index=True)
if "error" in d:
    d = d[d.error.isna()]
det = d[d.log10_fap < -2]; X = design(det); y = det.truth.values.astype(int)
Xo = design(o)
for name, m in models().items():
    p = m.fit(X, y).predict_proba(Xo[X.columns])[:, 1]
    print(f"{name}: largest difference from the stored scores {np.max(np.abs(p - o['p_' + name].values)):.1e}")
