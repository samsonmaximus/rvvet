"""Classifiers on ladder features, validated with cross-validation grouped by host star."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .ladder import FEATURES

# Transforms that make heavy-tailed features closer to linear in the log-odds.
def design(df: pd.DataFrame, features=FEATURES) -> pd.DataFrame:
    X = df[list(features)].astype(float).copy()
    for c in ("dchi2", "snr_K", "apod_gain", "ind_max_dchi2", "harm_dist", "harm_alias_dist", "half_phase_z", "half_amp_z"):
        if c in X:
            X[c] = np.log1p(np.clip(X[c], 0, None))
    for c in ("alias_margin",):
        if c in X:
            X[c] = np.sign(X[c]) * np.log1p(np.abs(X[c]))
    for c in ("block_phase_p", "block_amp_p"):
        if c in X:
            X[c] = np.log10(np.clip(X[c], 1e-12, 1))
    if "log10_fap" in X:
        X["log10_fap"] = np.clip(X["log10_fap"], -30, 0)
    if "act_log10_fap" in X:
        X["act_log10_fap"] = np.clip(X["act_log10_fap"], -30, 0)
    if "harm_dist" in X:                  # missing = no rotation proxy detected: far from any harmonic
        X["harm_missing"] = X["harm_dist"].isna().astype(float)
        X["harm_dist"] = X["harm_dist"].fillna(np.log1p(1e3))
    if "harm_alias_dist" in X:
        X["harm_alias_dist"] = X["harm_alias_dist"].fillna(np.log1p(1e3))
    return X


def models(seed=0):
    return {
        "logistic": make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler(),
                                  LogisticRegression(C=0.5, max_iter=5000)),
        "boosting": HistGradientBoostingClassifier(max_iter=400, learning_rate=0.04, max_leaf_nodes=15,
                                                   l2_regularization=1.0, min_samples_leaf=40, random_state=seed),
    }


def grouped_cv_predict(model, X, y, groups, n_splits=5):
    """Out-of-fold probabilities with folds that never split a host star."""
    p = np.full(len(y), np.nan)
    for tr, te in GroupKFold(n_splits=n_splits).split(X, y, groups):
        m = _clone(model)
        m.fit(X.iloc[tr], y[tr])
        p[te] = m.predict_proba(X.iloc[te])[:, 1]
    return p


def _clone(model):
    from sklearn.base import clone
    return clone(model)


def metrics(y, p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return dict(auc=float(roc_auc_score(y, p)), brier=float(brier_score_loss(y, p)), logloss=float(log_loss(y, p)),
                n=int(len(y)), prevalence=float(np.mean(y)))


def grouped_bootstrap_auc(y, p, groups, n=1000, seed=0):
    """AUC with a bootstrap over host stars (resampling groups, not cases)."""
    rng = np.random.default_rng(seed)
    g = np.asarray(groups)
    ug = np.unique(g)
    idx_by = {k: np.where(g == k)[0] for k in ug}
    vals = []
    for _ in range(n):
        pick = rng.choice(ug, len(ug), replace=True)
        idx = np.concatenate([idx_by[k] for k in pick])
        if len(np.unique(y[idx])) < 2:
            continue
        vals.append(roc_auc_score(y[idx], p[idx]))
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def calibration_table(y, p, bins=10):
    edges = np.linspace(0, 1, bins + 1)
    k = np.clip(np.digitize(p, edges) - 1, 0, bins - 1)
    rows = []
    for b in range(bins):
        m = k == b
        if m.sum():
            rows.append(dict(bin=b, p_mean=float(p[m].mean()), frac_pos=float(y[m].mean()), n=int(m.sum())))
    return pd.DataFrame(rows)
