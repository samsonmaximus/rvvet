"""Analysis of the simulations and the benchmark for the methods paper.

Reads sims/chunk_*.parquet and results/benchmark_features.csv; writes results/*.json, *.csv
and figures/*.pdf. Every number quoted in the paper is printed here and stored in
results/numbers.json.
"""
import glob, json, os, sys
import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score, roc_curve

import rvvet
from rvvet.ladder import FEATURES, harmonic_distances
from rvvet.learn import (calibration_table, design, grouped_bootstrap_auc, grouped_cv_predict, metrics, models)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
RES = os.path.join(ROOT, "results"); FIG = os.path.join(ROOT, "figures")
os.makedirs(RES, exist_ok=True); os.makedirs(FIG, exist_ok=True)
NUM = {}


def _jsonable(v):
    if isinstance(v, dict):
        return {(" | ".join(map(str, k)) if isinstance(k, tuple) else str(k)): _jsonable(x) for k, x in v.items()}
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, tuple):
        return [_jsonable(x) for x in v]
    return v


def say(key, val, fmt="{}"):
    val = _jsonable(val)
    NUM[key] = val
    print(f"{key:48s} {fmt.format(val) if not isinstance(val, dict) else val}")


def load_sims():
    d = pd.concat([pd.read_parquet(p) for p in sorted(glob.glob(os.path.join(ROOT, "sims", "chunk_*.parquet")))],
                  ignore_index=True)
    d = d[d.get("error").isna()] if "error" in d else d
    # harm_alias_dist was added to the ladder after the simulations ran: recompute it from the stored
    # period, rotation proxy and spectral-window peaks (identical to rvvet.ladder.harmonic_distances).
    if "harm_alias_dist" not in d or d["harm_alias_dist"].isna().all():
        vals = []
        for r in d.itertuples():
            wp = [(float(q), 0.0) for q in str(r.window_peaks).split(";") if q not in ("", "nan", "None")]
            vals.append(harmonic_distances(1.0 / r.period, r.act_period, r.act_log10_fap, r.baseline, wp))
        d["harm_dist_check"], d["harm_alias_dist"] = zip(*vals)
        ok = np.isfinite(d.harm_dist) | np.isfinite(d.harm_dist_check)
        assert np.allclose(d.harm_dist[ok].fillna(-1), d.harm_dist_check[ok].fillna(-1), atol=1e-6)
    return d


def rule_pass(df, alias_aware=False):
    """The a-priori rule of results/RULES_FROZEN.md (alias_aware adds rotation aliases, post hoc)."""
    hd = df.harm_dist if not alias_aware else np.fmin(df.harm_dist, df.harm_alias_dist)
    rot_ok = hd.isna() | (hd >= 1)
    return ((df.log10_fap < -2) & (df.alias_margin > 0) & (df.block_phase_p.fillna(1) > 0.01)
            & (df.half_phase_z.fillna(0) < 3) & (df.ind_max_dchi2 < 13.8) & rot_ok)


def main():
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.labelsize": 8, "legend.fontsize": 7,
                         "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.linewidth": 0.6, "xtick.direction": "in",
                         "ytick.direction": "in", "xtick.top": True, "ytick.right": True, "savefig.dpi": 300,
                         "savefig.bbox": "tight", "mathtext.fontset": "dejavuserif"})
    W1 = 3.4
    d = load_sims()
    say("sims_cases", int(len(d)))
    say("sims_stars", int(d.star.nunique()))
    say("sims_class_counts", d.cls.value_counts().to_dict())
    say("sims_median_nights", float(d.N.median()))

    # ---------------------------------------------------------------- FAP calibration on real noise
    nz = d[d.cls == "noise"]
    cal = {}
    for a in (0.001, 0.01, 0.05, 0.1, 0.2, 0.5):
        frac = float(np.mean(nz.log10_fap < np.log10(a)))
        ci = binomtest(int(np.sum(nz.log10_fap < np.log10(a))), len(nz)).proportion_ci()
        cal[str(a)] = dict(frac=frac, lo=float(ci.low), hi=float(ci.high))
    say("fap_calibration_noise_only", cal)
    say("noise_cases", int(len(nz)))

    # ---------------------------------------------------------------- detections and impostors
    det = d[d.log10_fap < -2].copy()
    say("detections", int(len(det)))
    say("detection_truth_fraction", float(det.truth.mean()))
    say("detections_by_kind", det.kind.value_counts().to_dict())
    say("detections_by_class", det.groupby("cls").truth.agg(["size", "mean"]).round(3).to_dict())
    # planet-only completeness vs injected S/N and period
    pl = d[d.cls == "planet"].copy()
    pl["recovered"] = (pl.truth == 1) & (pl.log10_fap < -2)
    bins = [3, 5, 7, 10, 14, 20]
    pl["snr_bin"] = pd.cut(pl.snr_target, bins)
    comp = pl.groupby("snr_bin", observed=True).recovered.agg(["mean", "size"])
    say("completeness_by_snr", {str(k): [round(v["mean"], 3), int(v["size"])] for k, v in comp.iterrows()})
    pbins = [1.2, 3, 10, 30, 100, 300]
    pl["P_bin"] = pd.cut(pl.P_pl, pbins)
    compP = pl[pl.snr_target > 7].groupby("P_bin", observed=True).recovered.agg(["mean", "size"])
    say("completeness_by_P_snr_gt7", {str(k): [round(v["mean"], 3), int(v["size"])] for k, v in compP.iterrows()})

    # ---------------------------------------------------------------- single-feature power (detections)
    y = det.truth.values.astype(int)
    groups = det.star.values
    X = design(det)
    single = {}
    for c in X.columns:
        v = X[c].values
        ok = np.isfinite(v)
        if ok.sum() < 50 or len(np.unique(y[ok])) < 2:
            continue
        auc = roc_auc_score(y[ok], v[ok])
        single[c] = dict(auc=float(max(auc, 1 - auc)), direction="+" if auc >= 0.5 else "-", n=int(ok.sum()))
    single = dict(sorted(single.items(), key=lambda kv: -kv[1]["auc"]))
    say("single_feature_auc", {k: round(v["auc"], 3) for k, v in single.items()})
    json.dump(single, open(os.path.join(RES, "single_feature_auc.json"), "w"), indent=1)

    # ---------------------------------------------------------------- classifiers, grouped CV
    preds = {}
    for name, m in models().items():
        p = grouped_cv_predict(m, X, y, groups)
        preds[name] = p
        mt = metrics(y, p)
        mt["auc_ci"] = grouped_bootstrap_auc(y, p, groups, n=500)
        say(f"cv_{name}", mt)
        calibration_table(y, p).to_csv(os.path.join(RES, f"calibration_{name}.csv"), index=False)
    # baselines: FAP alone, and FAP plus snr (the "detection-only" view)
    for name, cols in (("fap_only", ["log10_fap"]), ("detection_only", ["log10_fap", "dchi2", "snr_K", "log_n"])):
        p = grouped_cv_predict(models()["logistic"], X[cols], y, groups)
        mt = metrics(y, p); mt["auc_ci"] = grouped_bootstrap_auc(y, p, groups, n=500)
        say(f"cv_{name}", mt)
        preds[name] = p
    # rule-based ladder
    for aa in (False, True):
        rp = rule_pass(det, alias_aware=aa).values
        tpr = float(rp[y == 1].mean()); fpr = float(rp[y == 0].mean())
        say(f"rule{'_alias' if aa else ''}_tpr_fpr", dict(tpr=tpr, fpr=fpr, precision=float(y[rp].mean()) if rp.any() else None))
    # impostor-type recall at fixed operating point (boosting, threshold 0.5)
    pb = preds["boosting"]
    by_kind = det.assign(p=pb).groupby("kind").p.agg(lambda v: float(np.mean(v > 0.5)))
    say("boosting_frac_called_planet_by_kind", by_kind.round(3).to_dict())

    # robustness: a model without any activity-indicator feature; dependence on indicator S/N and on N
    noind = [c for c in X.columns if not (c.startswith("ind_") or c.startswith("act_") or c.startswith("harm"))]
    p_noind = grouped_cv_predict(models()["boosting"], X[noind], y, groups)
    mt = metrics(y, p_noind); mt["auc_ci"] = grouped_bootstrap_auc(y, p_noind, groups, n=500)
    say("cv_boosting_no_indicators", mt)
    preds["no_indicators"] = p_noind
    strata = {}
    act_imp = (det.truth == 0) & det.cls.str.contains("activity")
    planets = det.truth == 1
    for lo, hi in ((0.1, 0.3), (0.3, 1.0), (1.0, 3.0)):
        m = act_imp & det.ind_snr.between(lo, hi)
        sub = planets | m
        if m.sum() > 20:
            strata[f"{lo}-{hi}"] = dict(n_impostors=int(m.sum()),
                                        auc_boosting=float(roc_auc_score(y[sub], preds["boosting"][sub])),
                                        auc_no_indicators=float(roc_auc_score(y[sub], p_noind[sub])),
                                        rule_fpr=float(rule_pass(det[m]).mean()))
    say("activity_impostors_by_indicator_snr", strata)
    nmed = float(np.median(det.N))
    for nm, m in (("N_below_median", det.N < nmed), ("N_above_median", det.N >= nmed)):
        say(f"cv_boosting_{nm}", dict(auc=float(roc_auc_score(y[m], preds["boosting"][m])), n=int(m.sum()), N_median=nmed))
    rp0 = rule_pass(det)
    say("rule_fpr_by_kind", det.assign(r=rp0).groupby("kind").r.mean().round(3).to_dict())
    # which rung rejects each simulated impostor first (in ladder order)
    rungs = [("detection", det.log10_fap < -2), ("period", det.alias_margin > 0),
             ("phase", (det.block_phase_p.fillna(1) > 0.01) & (det.half_phase_z.fillna(0) < 3)),
             ("indicators", det.ind_max_dchi2 < 13.8), ("rotation", det.harm_dist.isna() | (det.harm_dist >= 1))]
    first = []
    for i in range(len(det)):
        f = "passes"
        for nm, ok in rungs:
            if not bool(ok.iloc[i]):
                f = nm; break
        first.append(f)
    det["first_fail"] = first
    say("first_failed_rung_impostors", det[det.truth == 0].first_fail.value_counts().to_dict())
    say("first_failed_rung_planets", det[det.truth == 1].first_fail.value_counts().to_dict())

    # permutation importance (boosting, fitted on all detections; evaluated on a held-out star split)
    rng = np.random.default_rng(0)
    ustars = np.unique(groups); test_st = set(rng.choice(ustars, len(ustars) // 4, replace=False))
    te = np.array([g in test_st for g in groups])
    mb = models()["boosting"].fit(X[~te], y[~te])
    pi = permutation_importance(mb, X[te], y[te], scoring="roc_auc", n_repeats=10, random_state=0)
    imp = pd.Series(pi.importances_mean, index=X.columns).sort_values(ascending=False)
    say("perm_importance_boosting", imp.round(4).to_dict())
    ml = models()["logistic"].fit(X, y)
    coef = pd.Series(ml[-1].coef_[0][: X.shape[1]], index=X.columns)
    say("logistic_coefficients", coef.round(3).to_dict())

    # ---------------------------------------------------------------- benchmark (external test)
    b = pd.read_csv(os.path.join(RES, "benchmark_features.csv"))
    b["detected"] = b.log10_fap < -2
    b["upheld"] = b.label.str.startswith("UPHELD").astype(int)
    b["binary"] = b.label.isin(["UPHELD_INDEPENDENT", "UPHELD_HARPS", "REFUTED"])
    fits = {name: m.fit(X, y) for name, m in models().items()}
    Xb = design(b)
    for name, m in fits.items():
        b[f"p_{name}"] = m.predict_proba(Xb[X.columns])[:, 1]
    b["rule"] = rule_pass(b); b["rule_alias"] = rule_pass(b, alias_aware=True)
    mni = models()["boosting"].fit(X[noind], y)
    b["p_no_indicators"] = mni.predict_proba(Xb[noind])[:, 1]
    ff = []
    for _, r0 in b.iterrows():
        f = "passes"
        for nm, ok in (("detection", r0.log10_fap < -2), ("period", r0.alias_margin > 0),
                       ("phase", (1 if np.isnan(r0.block_phase_p) else r0.block_phase_p) > 0.01 and
                        (0 if np.isnan(r0.half_phase_z) else r0.half_phase_z) < 3),
                       ("indicators", r0.ind_max_dchi2 < 13.8),
                       ("rotation", np.isnan(r0.harm_dist) or r0.harm_dist >= 1)):
            if not ok:
                f = nm; break
        ff.append(f)
    b["first_fail"] = ff
    bb = b[b.binary]
    say("bench_counts", bb.label.value_counts().to_dict())
    say("bench_detected_by_label", bb.groupby("label").detected.agg(["sum", "size"]).to_dict())
    for sub_name, sub in (("all", bb), ("detected", bb[bb.detected])):
        yy = sub.upheld.values
        res = {}
        if len(np.unique(yy)) == 2:
            for name in ("boosting", "logistic", "no_indicators"):
                pp = sub[f"p_{name}"].values
                auc = roc_auc_score(yy, pp)
                boots = []
                for _ in range(2000):
                    i = rng.integers(0, len(yy), len(yy))
                    if len(np.unique(yy[i])) == 2:
                        boots.append(roc_auc_score(yy[i], pp[i]))
                res[name] = dict(auc=float(auc), lo=float(np.percentile(boots, 2.5)), hi=float(np.percentile(boots, 97.5)))
            for rn in ("rule", "rule_alias"):
                r = sub[rn].values
                res[rn] = dict(tpr=float(r[yy == 1].mean()), fpr=float(r[yy == 0].mean()),
                               n_up=int((yy == 1).sum()), n_ref=int((yy == 0).sum()))
        say(f"bench_{sub_name}", res)
    cols = ["signal", "label", "P_claim", "n", "dchi2", "log10_fap", "is_top", "K", "sK", "alias_margin", "block_phase_p",
            "half_phase_z", "apod_gain", "ind_max_dchi2", "ind_argmax", "act_period", "act_log10_fap", "harm_dist",
            "harm_alias_dist", "p_logistic", "p_boosting", "p_no_indicators", "rule", "rule_alias", "first_fail", "detected"]
    b[cols].to_csv(os.path.join(RES, "benchmark_scored.csv"), index=False)

    say("bench_first_fail", b[b.binary].groupby(["label", "first_fail"]).size().to_dict())
    # ---------------------------------------------------------------- HD 297396 b, generic pipeline
    df = pd.read_parquet(os.path.join(ROOT, "data", "rvbank.parquet"))
    s = rvvet.load_star(df, "HD297396", clip_sigma=15)
    r = rvvet.vet(s, period=4.26837, trend=2)
    rr = pd.DataFrame([r])
    Xr = design(rr)
    r["p_boosting"] = float(fits["boosting"].predict_proba(Xr[X.columns])[:, 1][0])
    r["p_logistic"] = float(fits["logistic"].predict_proba(Xr[X.columns])[:, 1][0])
    r["rule"] = bool(rule_pass(rr).iloc[0]); r["rule_alias"] = bool(rule_pass(rr, True).iloc[0])
    r["p_no_indicators"] = float(mni.predict_proba(Xr[noind])[:, 1][0])
    say("hd297396b", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()
                      if not k.startswith("_") and k not in ("star",)})

    # ---------------------------------------------------------------- figures
    # Fig: FAP calibration
    fig, ax = plt.subplots(figsize=(W1, 2.4))
    a = np.logspace(-3, 0, 40)
    fr = [np.mean(nz.log10_fap < np.log10(x)) for x in a]
    ax.plot(a, fr, color="#2a78d6", label="noise-only simulations")
    ax.plot(a, a, color="#222", lw=0.7, ls="--", label="nominal")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(1e-3, 1); ax.set_ylim(1e-4, 1)
    ax.set_xlabel("Baluev FAP threshold"); ax.set_ylabel("fraction of noise series below it"); ax.legend(frameon=False)
    fig.savefig(os.path.join(FIG, "fig_fapcal.pdf")); plt.close(fig)
    # Fig: completeness
    fig, ax = plt.subplots(figsize=(W1, 2.4))
    x = np.array([np.sqrt(bins[i] * bins[i + 1]) for i in range(len(bins) - 1)])
    ax.errorbar(x, comp["mean"].values, yerr=np.sqrt(comp["mean"] * (1 - comp["mean"]) / comp["size"]).values,
                fmt="o-", color="#2a78d6", ms=3, lw=0.9, capsize=0)
    ax.set_xscale("log"); ax.set_ylim(0, 1.02)
    ax.set_xlabel(r"injected $K/\sigma_K$ (expected)"); ax.set_ylabel("recovered at the right period, FAP < 1%")
    fig.savefig(os.path.join(FIG, "fig_completeness.pdf")); plt.close(fig)
    # Fig: ROC curves on simulations
    fig, ax = plt.subplots(figsize=(W1, 2.8))
    for name, c, ls in (("boosting", "#c0392b", "-"), ("logistic", "#2a78d6", "-"), ("detection_only", "#8a8a85", "--"),
                        ("fap_only", "#8a8a85", ":")):
        fpr, tpr, _ = roc_curve(y, preds[name])
        ax.plot(fpr, tpr, color=c, ls=ls, lw=1.0, label=f"{name.replace('_', ' ')} (AUC {roc_auc_score(y, preds[name]):.2f})")
    rp = rule_pass(det).values
    ax.plot(rp[y == 0].mean(), rp[y == 1].mean(), "ks", ms=4, label="a-priori rule")
    ax.plot([0, 1], [0, 1], color="#ccc", lw=0.6)
    ax.set_xlabel("false-positive rate (impostors called planets)"); ax.set_ylabel("true-positive rate")
    ax.legend(frameon=False, loc="lower right")
    fig.savefig(os.path.join(FIG, "fig_roc.pdf")); plt.close(fig)
    # Fig: reliability
    fig, ax = plt.subplots(figsize=(W1, 2.5))
    for name, c in (("boosting", "#c0392b"), ("logistic", "#2a78d6")):
        ct = calibration_table(y, preds[name])
        ax.plot(ct.p_mean, ct.frac_pos, "o-", color=c, ms=3, lw=0.9, label=name)
    ax.plot([0, 1], [0, 1], color="#222", lw=0.6, ls="--")
    ax.set_xlabel("predicted P(planet)"); ax.set_ylabel("fraction that are planets"); ax.legend(frameon=False)
    fig.savefig(os.path.join(FIG, "fig_reliability.pdf")); plt.close(fig)
    # Fig: feature importance
    fig, ax = plt.subplots(figsize=(W1, 3.0))
    top = imp.head(12)[::-1]
    ax.barh(range(len(top)), top.values, color="#2a78d6")
    ax.set_yticks(range(len(top))); ax.set_yticklabels([t.replace("_", " ") for t in top.index])
    ax.set_xlabel("drop in AUC when permuted (held-out stars)")
    fig.savefig(os.path.join(FIG, "fig_importance.pdf")); plt.close(fig)
    # Fig: benchmark scores
    fig, ax = plt.subplots(figsize=(W1, 3.2))
    order = {"REFUTED": 0, "UPHELD_HARPS": 1, "UPHELD_INDEPENDENT": 2, "DISPUTED": 3}
    bs = b.assign(o=b.label.map(order)).sort_values(["o", "p_boosting"])
    colors = {"REFUTED": "#c0392b", "UPHELD_HARPS": "#1baf7a", "UPHELD_INDEPENDENT": "#2a78d6", "DISPUTED": "#8a8a85"}
    for i, (_, r0) in enumerate(bs.iterrows()):
        ax.plot(r0.p_boosting, i, "o" if r0.detected else "o", mfc=colors[r0.label] if r0.detected else "white",
                mec=colors[r0.label], ms=3.5)
    ax.set_yticks(range(len(bs))); ax.set_yticklabels(bs.signal, fontsize=4.5)
    ax.axvline(0.5, color="#ccc", lw=0.6); ax.set_xlim(-0.02, 1.02)
    ax.set_xlabel("P(planet), boosted trees trained on simulations")
    fig.savefig(os.path.join(FIG, "fig_benchmark.pdf")); plt.close(fig)

    json.dump(NUM, open(os.path.join(RES, "numbers.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
