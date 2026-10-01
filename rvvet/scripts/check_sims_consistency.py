"""Regenerate simulated cases from their seeds with the current package and compare every
feature with the stored run (after the degrees-of-freedom recomputation that analyze.py
applies). Writes results/sims_consistency.json.

Usage: python check_sims_consistency.py [N_CASES] [SEED]
"""
import glob, json, os, sys
import numpy as np
import pandas as pd

import rvvet
import run_sims as R
from scipy.stats import chi2
from rvvet.ladder import _block_dofs

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed0 = 20260929
    stored = pd.concat([pd.read_parquet(p) for p in sorted(glob.glob(os.path.join(ROOT, "sims", "chunk_*.parquet")))],
                       ignore_index=True).set_index("case")
    ok = stored.n_blocks_used >= 3
    dofs = np.array([_block_dofs(int(k)) for k in stored.loc[ok, "n_blocks_used"]])
    stored.loc[ok, "block_phase_p"] = chi2.sf(stored.loc[ok, "block_phase_chi2"], dofs[:, 0])
    stars = json.load(open(os.path.join(ROOT, "sims", "stars.json")))["stars"]
    rng = np.random.default_rng(seed0)
    seeds = [int(rng.integers(2 ** 31)) for _ in range(len(stored))]
    df = pd.read_parquet(os.path.join(ROOT, "data", "rvbank.parquet"))
    pick = np.random.default_rng(1).choice(stored.index.values, n, replace=False)
    worst, rows = 0.0, []
    for case in sorted(int(c) for c in pick):
        st = stars[case % len(stars)]
        s = rvvet.load_star(df, st, clip_sigma=15)
        sd = dict(star=st, t=s.t, y=s.y, e=s.e, label=s.label, labels=s.labels, ind=s.ind)
        rec = R.one_case((case, st, sd, seeds[case]))
        ref = stored.loc[case]
        diffs = {}
        for k, v in rec.items():
            if k in ref.index and isinstance(v, (float, int, np.floating)) and not isinstance(v, bool):
                a, b = float(v), float(ref[k])
                if np.isfinite(a) or np.isfinite(b):
                    d = abs(a - b) / max(1.0, abs(b))
                    diffs[k] = d
        m = max(diffs.values())
        worst = max(worst, m)
        rows.append(dict(case=case, star=st, kind=rec["kind"], kind_stored=ref["kind"], max_rel_diff=m,
                         worst_feature=max(diffs, key=diffs.get)))
        print(rows[-1], flush=True)
    out = dict(n=len(rows), max_rel_diff=worst, identical_kind=all(r["kind"] == r["kind_stored"] for r in rows), rows=rows)
    json.dump(out, open(os.path.join(ROOT, "results", "sims_consistency.json"), "w"), indent=1)
    print("max relative difference", worst)


if __name__ == "__main__":
    main()
