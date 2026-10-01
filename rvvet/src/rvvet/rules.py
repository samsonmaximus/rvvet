"""The a-priori rule (results/RULES_FROZEN.md, frozen 2026-09-29 12:08 UTC before any benchmark
signal was run). Thresholds are fixed; features are computed by ``ladder.vet``."""
from __future__ import annotations

import numpy as np
import pandas as pd

LOG10_FAP_MAX = -2.0          # detection: global FAP below 1 %
ALIAS_MARGIN_MIN = 0.0        # period: beats every alias candidate
BLOCK_PHASE_P_MIN = 0.01      # phase: constant across blocks ...
HALF_PHASE_Z_MAX = 3.0        # ... and halves
IND_DCHI2_MAX = 13.8          # activity: no indicator with Delta chi^2 >= 13.8 near P
HARM_DIST_MIN = 1.0           # rotation: >= 1 resolution element from k f_rot, k = 1-4

RUNGS = ("detection", "period", "phase", "indicators", "rotation")


def rung_checks(df: pd.DataFrame, alias_aware: bool = False) -> pd.DataFrame:
    """Boolean pass/fail of each rung. Missing values pass (a test that cannot be computed does
    not reject): no blocks or halves -> phase passes; no rotation proxy -> rotation passes.
    ``alias_aware`` also rejects candidates within one element of a first-order alias of a
    rotation harmonic (harm_alias_dist; added after the rule was frozen)."""
    hd = df["harm_dist"] if not alias_aware else np.fmin(df["harm_dist"], df["harm_alias_dist"])
    return pd.DataFrame({
        "detection": df["log10_fap"] < LOG10_FAP_MAX,
        "period": df["alias_margin"].fillna(np.inf) > ALIAS_MARGIN_MIN,
        "phase": (df["block_phase_p"].fillna(1.0) > BLOCK_PHASE_P_MIN) & (df["half_phase_z"].fillna(0.0) < HALF_PHASE_Z_MAX),
        "indicators": df["ind_max_dchi2"].fillna(0.0) < IND_DCHI2_MAX,
        "rotation": hd.isna() | (hd >= HARM_DIST_MIN),
    }, index=df.index)


def rule_pass(df: pd.DataFrame, alias_aware: bool = False) -> pd.Series:
    return rung_checks(df, alias_aware).all(axis=1)


def first_failed_rung(df: pd.DataFrame, alias_aware: bool = False) -> pd.Series:
    """The first rung, in ladder order, that a candidate fails ("passes" if none)."""
    c = rung_checks(df, alias_aware)
    out = pd.Series("passes", index=df.index, dtype=object)
    for r in reversed(RUNGS):
        out[~c[r]] = r
    return out
