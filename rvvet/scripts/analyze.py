"""Analysis of the simulations, the false-alarm calibration, the benchmark and the defect log.

Reads sims/chunk_*.parquet, results/fap_calibration.parquet, results/benchmark_features.csv,
results_v0.1/benchmark_scored.csv (the first, frozen-pipeline pass) and defects/*.csv. Writes
results/numbers.json, results/*.csv, figures/*.pdf, and the LaTeX files the paper inputs:
paper/numbers.tex (one macro per number quoted in the text) and paper/tab_*.tex (tables).
No number in the paper is typed by hand except literature values.
"""
import glob, json, os, re, sys
import numpy as np
import pandas as pd
from scipy.stats import beta as _beta
from sklearn.inspection import permutation_importance
from sklearn.metrics import cohen_kappa_score, roc_auc_score, roc_curve

import rvvet
from rvvet.ladder import FEATURES, PRIOR_DEPENDENT
from rvvet.learn import (calibration_table, design, grouped_bootstrap_auc, grouped_cv_predict, metrics, models)
from rvvet.rules import first_failed_rung, rule_pass, rung_checks

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RES = os.path.join(ROOT, "results"); FIG = os.path.join(ROOT, "figures"); PAP = os.path.join(ROOT, "paper")
for d_ in (RES, FIG, PAP):
    os.makedirs(d_, exist_ok=True)
NUM, MAC = {}, {}
HD297396_P = 4.26837


# ----------------------------------------------------------------------------- helpers
def _jsonable(v):
    if isinstance(v, dict):
        return {(" | ".join(map(str, k)) if isinstance(k, tuple) else str(k)): _jsonable(x) for k, x in v.items()}
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    if isinstance(v, (tuple, list)):
        return [_jsonable(x) for x in v]
    return v


def say(key, val):
    val = _jsonable(val)
    NUM[key] = val
    print(f"{key:44s} {val}")


def mac(name, s):
    assert re.fullmatch(r"[A-Za-z]+", name), name
    assert name not in MAC, f"macro {name} defined twice"
    MAC[name] = str(s)


def thou(n):
    n = int(round(n))
    return f"{n:,}".replace(",", r"\,") if abs(n) >= 10000 else str(n)


def pc(x, nd=0):
    return f"{100 * x:.{nd}f}"


def f2(x, nd=2):
    return f"{x:.{nd}f}"


def cp(k, n, a=0.05):
    """Clopper-Pearson interval for k successes in n trials."""
    lo = 0.0 if k == 0 else float(_beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(_beta.ppf(1 - a / 2, k + 1, n - k))
    return lo, hi


def auc(y, p):
    return float(roc_auc_score(y, p))


def boot_auc_stratified(y, p, n=4000, seed=0):
    """Bootstrap resampling each class separately (keeps both classes present)."""
    rng = np.random.default_rng(seed)
    i1, i0 = np.where(y == 1)[0], np.where(y == 0)[0]
    vals = []
    for _ in range(n):
        a = rng.choice(i1, len(i1)); b = rng.choice(i0, len(i0))
        vals.append(roc_auc_score(np.r_[np.ones(len(a)), np.zeros(len(b))], np.r_[p[a], p[b]]))
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def misordered_pairs(y, p):
    pos, neg = p[y == 1], p[y == 0]
    bad = sum(float(np.sum(neg > q) + 0.5 * np.sum(neg == q)) for q in pos)
    return bad, len(pos) * len(neg)


def load_sims():
    d = pd.concat([pd.read_parquet(p) for p in sorted(glob.glob(os.path.join(ROOT, "sims", "chunk_*.parquet")))],
                  ignore_index=True)
    n_err = int(d["error"].notna().sum()) if "error" in d else 0
    if "error" in d:
        d = d[d["error"].isna()].copy()
    # check that the stored block p-values use the package's degrees of freedom
    from scipy.stats import chi2 as _chi2
    from rvvet.ladder import _block_dofs
    ok = d.n_blocks_used >= 3
    dofs = np.array([_block_dofs(int(k)) for k in d.loc[ok, "n_blocks_used"]])
    assert np.allclose(d.loc[ok, "block_phase_p"], _chi2.sf(d.loc[ok, "block_phase_chi2"], dofs[:, 0]))
    assert np.allclose(d.loc[ok, "block_amp_p"], _chi2.sf(d.loc[ok, "block_amp_chi2"], dofs[:, 1]))
    return d, n_err


# ----------------------------------------------------------------------------- main
def main():
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.labelsize": 8, "legend.fontsize": 6.5,
                         "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.linewidth": 0.6, "xtick.direction": "in",
                         "ytick.direction": "in", "xtick.top": True, "ytick.right": True, "savefig.dpi": 300,
                         "savefig.bbox": "tight", "mathtext.fontset": "dejavuserif"})
    W1 = 3.4
    mac("rvvetVersion", rvvet.__version__)

    # ======================================================================= simulations
    d, n_err = load_sims()
    say("sims_cases", len(d)); say("sims_errors", n_err)
    say("sims_stars", d.star.nunique())
    cc = d.cls.value_counts().to_dict(); say("sims_class_counts", cc)
    say("sims_median_nights", float(d.N.median()))
    mac("SimCases", thou(len(d))); mac("SimStars", d.star.nunique()); mac("SimMedianN", int(d.N.median()))
    mac("SimErrors", n_err)
    sc = json.load(open(os.path.join(RES, "sims_consistency.json")))
    say("sims_consistency", dict(n=sc["n"], max_rel_diff=sc["max_rel_diff"], identical_kind=sc["identical_kind"]))
    mac("ConsistN", sc["n"]); mac("ConsistDiff", "identical" if sc["max_rel_diff"] == 0 else f"{sc['max_rel_diff']:.1e}")
    # cost per case on one core: median chunk wall time (500 cases, two workers) from the run log
    try:
        tt = [float(m_.group(1)) for m_ in re.finditer(r"500 cases in (\d+) s", open(os.path.join(ROOT, "sims.log")).read())]
        say("sim_chunk_seconds_median", float(np.median(tt)))
        mac("SecPerCase", f"{np.median(tt) * 2 / 500:.1f}")
    except OSError:
        pass
    mac("NPlanetOnly", thou(cc["planet"])); mac("NPlanetAct", thou(cc["planet+activity"]))
    mac("NActOnly", thou(cc["activity"])); mac("NNoiseOnly", thou(cc["noise"]))

    # ------------------------------------------------------------ false-alarm calibration
    fc = pd.read_parquet(os.path.join(RES, "fap_calibration.parquet"))
    alphas = (0.001, 0.003, 0.01, 0.03, 0.1, 0.3)
    cal = {}
    for kind in ("permuted", "gaussian"):
        for stat, col in (("lr", "log10_fap"), ("h0", "log10_fap_h0")):
            v = fc.loc[fc.kind == kind, col].values
            rows = {}
            for a in alphas:
                k = int(np.sum(v < np.log10(a))); n = len(v); lo, hi = cp(k, n)
                rows[str(a)] = dict(k=k, n=n, frac=k / n, lo=lo, hi=hi)
            cal[f"{kind}_{stat}"] = rows
    say("fap_calibration", cal)
    nser = int((fc.kind == "permuted").sum())
    mac("FapSeries", thou(nser)); mac("FapPerStar", nser // d.star.nunique())
    for kind, K in (("permuted", "Perm"), ("gaussian", "Gauss")):
        for stat, S in (("lr", "LR"), ("h0", "Fix")):
            for a, A in ((0.01, "One"), (0.1, "Ten"), (0.001, "Tenth")):
                r = cal[f"{kind}_{stat}"][str(a)]
                nd = 2 if r["frac"] < 0.01 else (1 if r["frac"] < 0.1 else 0)
                mac(f"Fap{K}{S}{A}", pc(r["frac"], nd))
                mac(f"Fap{K}{S}{A}Lo", pc(r["lo"], nd)); mac(f"Fap{K}{S}{A}Hi", pc(r["hi"], nd))
    # nominal Baluev FAP that gives an actual 1 % (and 0.1 %) false-alarm rate on real noise
    vv = np.sort(fc.loc[fc.kind == "permuted", "log10_fap"].values)
    rng_b = np.random.default_rng(3)
    for q_, nm in ((0.01, "One"), (0.001, "Tenth")):
        thr = float(np.quantile(vv, q_))
        bs_ = [np.quantile(rng_b.choice(vv, len(vv)), q_) for _ in range(1000)]
        lo_t, hi_t = np.percentile(bs_, [2.5, 97.5])
        say(f"fap_empirical_nominal_for_{q_}", [10 ** thr, 10 ** lo_t, 10 ** hi_t])
        mac(f"FapEmp{nm}", f"{100 * 10 ** thr:.2g}"); mac(f"FapEmp{nm}Lo", f"{100 * 10 ** lo_t:.2g}")
        mac(f"FapEmp{nm}Hi", f"{100 * 10 ** hi_t:.2g}")
    for kind, K in (("permuted", "Perm"), ("gaussian", "Gauss")):
        r = cal[f"{kind}_lr"]["0.01"]
        mac(f"FapLiberal{K}", f"{r['frac'] / 0.01:.1f}")
    mac("FapLiberalPermTenth", f"{cal['permuted_lr']['0.001']['frac'] / 0.001:.1f}")
    rfix = [a / cal["permuted_h0"][str(a)]["frac"] for a in (0.01, 0.03, 0.1)]
    mac("FapFixFactorLo", f"{min(rfix):.0f}"); mac("FapFixFactorHi", f"{max(rfix):.0f}")
    say("fap_fixed_jitter_conservatism_factor_1_3_10pct", rfix)
    say("fap_median_jitter_scale_permuted", float(fc.loc[fc.kind == "permuted", "jitter_scale"].median()))
    mac("JitScaleNoise", f2(float(fc.loc[fc.kind == "permuted", "jitter_scale"].median())))

    # ------------------------------------------------------------ completeness (planets alone)
    pl = d[d.cls == "planet"].copy()
    pl["recovered"] = (pl.truth == 1) & (pl.log10_fap < -2)
    edges = np.array([1, 2, 3, 4, 5, 6, 7, 8.5, 10, 12, 14, 17, 20, 30])
    pl["b"] = pd.cut(pl.snr_target, edges)
    comp = pl.groupby("b", observed=True).recovered.agg(["mean", "size"])
    say("completeness_by_expected_snr", {str(k): [round(v["mean"], 3), int(v["size"])] for k, v in comp.iterrows()})
    xc = np.sqrt(edges[:-1] * edges[1:])[: len(comp)]
    yc = comp["mean"].values
    k50 = float(np.interp(0.5, yc, xc)) if yc.max() > 0.5 else np.nan
    k90 = float(np.interp(0.9, yc, xc)) if yc.max() > 0.9 else np.nan
    say("completeness_50_90_expected_snr", [k50, k90])
    mac("CompFifty", f"{k50:.1f}"); mac("CompNinety", f"{k90:.0f}")
    for lo_, hi_, nm in ((3, 4, "ThreeFour"), (6, 7, "SixSeven"), (10, 12, "TenTwelve"), (14, 17, "FourteenSeventeen")):
        m = (pl.snr_target > lo_) & (pl.snr_target <= hi_)
        mac(f"Comp{nm}", pc(pl.recovered[m].mean()))
    pbins = [1.2, 3, 10, 30, 100, 300]
    pl["P_bin"] = pd.cut(pl.P_pl, pbins)
    compP = pl[pl.snr_target > 10].groupby("P_bin", observed=True).recovered.agg(["mean", "size"])
    say("completeness_by_P_snr_gt10", {str(k): [round(v["mean"], 3), int(v["size"])] for k, v in compP.iterrows()})
    mac("CompPLo", pc(compP["mean"].min())); mac("CompPHi", pc(compP["mean"].max()))
    pdet = pl[pl.log10_fap < -2]
    wrong = pdet[pdet.truth == 0]
    say("planet_only_detected_wrong_period", dict(n_det=len(pdet), n_wrong=len(wrong), kinds=wrong.kind.value_counts().to_dict()))
    mac("PlWrongPct", pc(len(wrong) / len(pdet), 1)); mac("PlWrongN", len(wrong)); mac("PlDetN", thou(len(pdet)))
    mac("PlWrongAliasN", int((wrong.kind == "planet_alias").sum()))

    # ------------------------------------------------------------ detections and impostors
    det = d[d.log10_fap < -2].copy()
    y = det.truth.values.astype(int)
    groups = det.star.values
    kinds = det.kind.value_counts().to_dict()
    say("detections", len(det)); say("detections_by_kind", kinds)
    mac("NDet", thou(len(det))); mac("NDetPlanet", thou(int(y.sum()))); mac("NDetImp", thou(int((1 - y).sum())))
    mac("DetPlanetPct", pc(y.mean())); mac("DetImpPct", pc(1 - y.mean()))
    for k, nm in (("rotation_harmonic", "RotHarm"), ("rotation_line", "RotLine"), ("activity_other", "ActOther"),
                  ("planet_alias", "PlAlias"), ("noise", "Noise")):
        mac(f"Imp{nm}", thou(kinds.get(k, 0)))
    act_imp_all = det[(det.truth == 0) & det.kind.isin(["rotation_harmonic", "rotation_line", "activity_other"])]
    mac("ImpActTotal", thou(len(act_imp_all)))
    mac("ImpRotLinePctAct", pc(kinds.get("rotation_line", 0) / len(act_imp_all)))
    k0 = act_imp_all[act_imp_all.kind == "rotation_line"]
    env = (1.0 / k0.period) < (1.0 / (np.pi * k0.lam))
    mac("ImpEnvelopeN", thou(int(env.sum())))
    say("rotation_line_envelope_k0", int(env.sum()))
    nz = d[d.cls == "noise"]
    mac("NoiseSigN", int((nz.log10_fap < -2).sum())); mac("NoiseN", thou(len(nz)))
    # dependence on the priors: planet fraction among detections by N quartile and by class mix
    q = pd.qcut(det.N, 4)
    byq = det.groupby(q, observed=True).truth.mean()
    say("detected_planet_fraction_by_N_quartile", {str(k): round(v, 3) for k, v in byq.items()})
    mac("DetPlanetPctNLo", pc(byq.iloc[0])); mac("DetPlanetPctNHi", pc(byq.iloc[-1]))

    # ------------------------------------------------------------ single-feature power
    X = design(det)
    Xall = X.copy()
    for c in PRIOR_DEPENDENT:
        Xall[c] = det[c].values
    single = {}
    for c in Xall.columns:
        v = Xall[c].values.astype(float)
        ok = np.isfinite(v)
        if ok.sum() < 50 or len(np.unique(y[ok])) < 2:
            continue
        a = roc_auc_score(y[ok], v[ok])
        single[c] = dict(auc=float(max(a, 1 - a)), direction="+" if a >= 0.5 else "-", n=int(ok.sum()),
                         prior_dependent=c in PRIOR_DEPENDENT)
    single = dict(sorted(single.items(), key=lambda kv: -kv[1]["auc"]))
    json.dump(single, open(os.path.join(RES, "single_feature_auc.json"), "w"), indent=1)
    say("single_feature_auc", {k: round(v["auc"], 4) for k, v in single.items()})
    # table (two columns of features)
    items = list(single.items())
    half = (len(items) + 1) // 2
    L, R = items[:half], items[half:]
    lines = []
    for i in range(half):
        def cell(it):
            if it is None:
                return "& "
            k, v = it
            nm = r"\code{" + k.replace("_", r"\_") + "}" + (r"$^\dagger$" if v["prior_dependent"] else "")
            return f"{nm} & {v['auc']:.2f}"
        lines.append(cell(L[i]) + " & " + cell(R[i] if i < len(R) else None) + r" \\")
    open(os.path.join(PAP, "tab_auc_rows.tex"), "w").write("\n".join(lines) + "\n")
    mac("NFeatTable", len(items))
    hd_ok = np.isfinite(det.harm_dist.values)
    a_ = roc_auc_score(y[hd_ok], det.harm_dist.values[hd_ok])
    say("harm_dist_auc_where_defined", dict(n=int(hd_ok.sum()), auc=float(max(a_, 1 - a_))))
    mac("HarmDefinedN", thou(int(hd_ok.sum()))); mac("AucHarmDefined", f2(max(a_, 1 - a_)))
    for k, nm in (("ind_max_dchi2", "AucInd"), ("log10_fap", "AucFap"), ("dchi2", "AucDchi"), ("block_phase_rms", "AucBlockRms"),
                  ("growth_rho", "AucGrowth"), ("alias_margin", "AucAlias"), ("log_n", "AucLogN"), ("log_ncyc", "AucLogNcyc"),
                  ("block_phase_p", "AucBlockP"), ("harm_dist", "AucHarm"), ("K_over_rms", "AucKrms")):
        if k in single:
            mac(nm, f2(single[k]["auc"]))

    # ------------------------------------------------------------ classifiers, grouped CV
    preds, cvm = {}, {}
    for name, m in models().items():
        p = grouped_cv_predict(m, X, y, groups)
        preds[name] = p
        mt = metrics(y, p); mt["auc_ci"] = grouped_bootstrap_auc(y, p, groups, n=500)
        cvm[name] = mt
        say(f"cv_{name}", mt)
        ct = calibration_table(y, p)
        ct["z"] = (ct.frac_pos - ct.p_mean) / np.sqrt(np.clip(ct.p_mean * (1 - ct.p_mean), 1e-6, None) / ct.n)
        ct.to_csv(os.path.join(RES, f"calibration_{name}.csv"), index=False)
        say(f"calibration_{name}_max_abs_z", float(ct.z.abs().max()))
        say(f"calibration_{name}_bins_abs_z_gt2", ct[ct.z.abs() > 2][["p_mean", "frac_pos", "n", "z"]].round(3).to_dict("records"))
    mac("AucLog", f"{cvm['logistic']['auc']:.3f}"); mac("AucLogLo", f"{cvm['logistic']['auc_ci'][0]:.3f}")
    mac("AucLogHi", f"{cvm['logistic']['auc_ci'][1]:.3f}")
    mac("AucTree", f"{cvm['boosting']['auc']:.3f}"); mac("AucTreeLo", f"{cvm['boosting']['auc_ci'][0]:.3f}")
    mac("AucTreeHi", f"{cvm['boosting']['auc_ci'][1]:.3f}")
    mac("BrierLog", f"{cvm['logistic']['brier']:.3f}"); mac("BrierTree", f"{cvm['boosting']['brier']:.3f}")
    for name, N_ in (("logistic", "Log"), ("boosting", "Tree")):
        ct = pd.read_csv(os.path.join(RES, f"calibration_{name}.csv"))
        mac(f"CalMaxZ{N_}", f"{ct.z.abs().max():.1f}"); mac(f"CalNBad{N_}", int((ct.z.abs() > 2).sum()))
        mac(f"CalNBins{N_}", len(ct))
    for name, cols in (("fap_only", ["log10_fap"]), ("detection_only", ["log10_fap", "dchi2", "snr_K"]),
                       ("n_only", ["log_n"])):
        Xb = X[[c for c in cols if c in X]].copy()
        if "log_n" in cols:
            Xb["log_n"] = det.log_n.values
        p = grouped_cv_predict(models()["logistic"], Xb, y, groups)
        mt = metrics(y, p); mt["auc_ci"] = grouped_bootstrap_auc(y, p, groups, n=300)
        say(f"cv_{name}", mt); preds[name] = p
    mac("AucFapOnly", f2(NUM["cv_fap_only"]["auc"])); mac("AucDetOnly", f2(NUM["cv_detection_only"]["auc"]))
    mac("AucNOnly", f2(NUM["cv_n_only"]["auc"]))
    p_prior = grouped_cv_predict(models()["boosting"], Xall, y, groups)
    say("cv_boosting_with_prior_features", metrics(y, p_prior)); mac("AucTreePrior", f"{auc(y, p_prior):.3f}")
    noind = [c for c in X.columns if not (c.startswith("ind_") or c.startswith("act_") or c.startswith("harm"))]
    p_noind = grouped_cv_predict(models()["boosting"], X[noind], y, groups)
    mt = metrics(y, p_noind); mt["auc_ci"] = grouped_bootstrap_auc(y, p_noind, groups, n=300)
    say("cv_boosting_no_indicators", mt); preds["no_indicators"] = p_noind
    mac("AucNoInd", f"{mt['auc']:.2f}")
    say("features_classifier", list(X.columns)); say("features_no_indicators", noind)
    # operating points of the trees
    pb = preds["boosting"]
    acc = det.assign(p=pb).groupby("kind").p.agg(lambda v: float(np.mean(v > 0.5)))
    say("boosting_frac_accepted_by_kind", acc.round(3).to_dict())
    tpr5 = float(np.mean(pb[y == 1] > 0.5)); fpr5 = float(np.mean(pb[y == 0] > 0.5))
    say("boosting_tpr_fpr_at_0.5", [tpr5, fpr5])
    mac("TreeTPR", pc(tpr5)); mac("TreeFPR", pc(fpr5))
    for k, nm in (("rotation_harmonic", "RotHarm"), ("rotation_line", "RotLine"), ("activity_other", "ActOther"),
                  ("planet_alias", "PlAlias"), ("noise", "Noise")):
        if k in acc:
            mac(f"TreeAcc{nm}", pc(acc[k]))
    fpr_c, tpr_c, thr = roc_curve(y, pb)
    t_at5 = float(np.interp(0.05, fpr_c, tpr_c)); t_at1 = float(np.interp(0.01, fpr_c, tpr_c))
    say("boosting_tpr_at_fpr_5_1", [t_at5, t_at1]); mac("TreeTPRatFiveFPR", pc(t_at5)); mac("TreeTPRatOneFPR", pc(t_at1))
    for prev, nm in ((0.1, "Ten"), (0.5, "Fifty")):
        ppv = tpr5 * prev / (tpr5 * prev + fpr5 * (1 - prev))
        say(f"boosting_precision_at_prevalence_{prev}", ppv); mac(f"TreePPV{nm}", pc(ppv))

    # ------------------------------------------------------------ a-priori rule on simulations
    rp = rule_pass(det).values
    tpr, fpr = float(rp[y == 1].mean()), float(rp[y == 0].mean())
    say("rule_tpr_fpr", dict(tpr=tpr, fpr=fpr, precision=float(y[rp].mean())))
    mac("RuleTPR", pc(tpr)); mac("RuleFPR", pc(fpr))
    rk = det.assign(r=rp).groupby("kind").r.mean()
    say("rule_accept_by_kind", rk.round(3).to_dict())
    for k, nm in (("rotation_harmonic", "RotHarm"), ("rotation_line", "RotLine"), ("activity_other", "ActOther"),
                  ("planet_alias", "PlAlias"), ("noise", "Noise")):
        if k in rk:
            mac(f"RuleAcc{nm}", pc(rk[k]))
    rpa = rule_pass(det, alias_aware=True).values
    say("rule_alias_tpr_fpr", dict(tpr=float(rpa[y == 1].mean()), fpr=float(rpa[y == 0].mean())))
    ff = first_failed_rung(det)
    say("first_failed_rung_planets", ff[y == 1].value_counts().to_dict())
    say("first_failed_rung_impostors", ff[y == 0].value_counts().to_dict())
    chk = rung_checks(det)
    # false rejection of real planets by each rung on its own, on planets alone (no activity)
    plo = (det.cls == "planet") & (det.truth == 1)
    fr_rung = {r: float((~chk.loc[plo, r]).mean()) for r in chk.columns}
    say("rung_false_rejection_planet_only", fr_rung)
    for r, nm in (("period", "Period"), ("phase", "Phase"), ("indicators", "Ind"), ("rotation", "Rot")):
        mac(f"RungRej{nm}", pc(fr_rung[r], 1))
    mac("NPlanetOnlyDet", thou(int(plo.sum())))
    # calibration of the stationarity p-values on planets alone
    stat = det.loc[plo]
    sp = dict(block_phase_p_median=float(stat.block_phase_p.median()), block_phase_p_lt01=float((stat.block_phase_p < 0.01).mean()),
              block_phase_p_lt05=float((stat.block_phase_p < 0.05).mean()), block_amp_p_median=float(stat.block_amp_p.median()),
              block_amp_p_lt01=float((stat.block_amp_p < 0.01).mean()), block_amp_p_lt05=float((stat.block_amp_p < 0.05).mean()),
              half_phase_z_gt196=float((stat.half_phase_z > 1.96).mean()), half_phase_z_gt3=float((stat.half_phase_z > 3).mean()),
              half_amp_z_gt196=float((stat.half_amp_z > 1.96).mean()), ind_gt138=float((stat.ind_max_dchi2 > 13.8).mean()))
    say("stationarity_calibration_planet_only", sp)
    mac("BPhMed", f2(sp["block_phase_p_median"])); mac("BPhFive", pc(sp["block_phase_p_lt05"], 1))
    mac("BAmpMed", f2(sp["block_amp_p_median"])); mac("BAmpFive", pc(sp["block_amp_p_lt05"], 1))
    mac("HPhOver", pc(sp["half_phase_z_gt196"], 1)); mac("HAmpOver", pc(sp["half_amp_z_gt196"], 1))
    mac("IndOverPl", pc(sp["ind_gt138"], 1))
    from scipy.stats import chi2 as _chi2
    p_nb2 = _chi2.sf(stat.block_phase_chi2, stat.n_blocks_used - 2)
    say("block_phase_p_lt05_with_nb_minus_2", float(np.mean(p_nb2 < 0.05)))
    mac("BPhFiveNbTwo", pc(float(np.mean(p_nb2 < 0.05)), 1))
    k_amp = int((stat.block_amp_p < 0.05).sum()); lo_a, hi_a = cp(k_amp, len(stat))
    mac("BAmpFiveLo", pc(lo_a, 1)); mac("BAmpFiveHi", pc(hi_a, 1))

    # ------------------------------------------------------------ strata: indicator coupling, rotation domain
    imp = (det.truth == 0) & det.kind.isin(["rotation_harmonic", "rotation_line", "activity_other"])
    planets = det.truth == 1
    strata = {}
    for nm, m in (("uncoupled", imp & (det.ind_coupled == False)),
                  ("0.1-0.3", imp & det.ind_snr.between(0.1, 0.3)), ("0.3-1", imp & det.ind_snr.between(0.3, 1.0)),
                  ("1-3", imp & det.ind_snr.between(1.0, 3.0))):
        sub = (planets | m).values
        strata[nm] = dict(n=int(m.sum()), rule_accept=float(rp[m.values].mean()), trees_accept=float((pb[m.values] > 0.5).mean()),
                          auc_trees=auc(y[sub], pb[sub]), auc_noind=auc(y[sub], p_noind[sub]))
    say("activity_impostors_by_indicator_coupling", strata)
    for nm, N_ in (("uncoupled", "Unc"), ("0.1-0.3", "Weak"), ("1-3", "Strong")):
        mac(f"StRule{N_}", pc(strata[nm]["rule_accept"])); mac(f"StTree{N_}", pc(strata[nm]["trees_accept"]))
        mac(f"StAuc{N_}", f2(strata[nm]["auc_trees"])); mac(f"StN{N_}", thou(strata[nm]["n"]))
    dom = {}
    for nm, m in (("Prot_3_10", imp & (det.P_rot < 10)), ("Prot_10_40", imp & det.P_rot.between(10, 40)),
                  ("Prot_40_150", imp & (det.P_rot > 40)), ("lam_1_3", imp & (det.lam_rot < 3)),
                  ("lam_3_10", imp & det.lam_rot.between(3, 10)), ("lam_10_30", imp & (det.lam_rot > 10))):
        sub = (planets | m).values
        dom[nm] = dict(n=int(m.sum()), rule_accept=float(rp[m.values].mean()), trees_accept=float((pb[m.values] > 0.5).mean()),
                       auc_trees=auc(y[sub], pb[sub]))
    say("activity_impostors_by_rotation_domain", dom)
    for nm, N_ in (("Prot_40_150", "ProtLong"), ("Prot_3_10", "ProtShort"), ("lam_10_30", "LamLong"), ("lam_1_3", "LamShort")):
        mac(f"Dom{N_}Rule", pc(dom[nm]["rule_accept"])); mac(f"Dom{N_}Tree", pc(dom[nm]["trees_accept"]))
        mac(f"Dom{N_}N", thou(dom[nm]["n"]))
    mac("RuleAccAct", pc(rp[imp.values].mean())); mac("TreeAccAct", pc((pb[imp.values] > 0.5).mean()))
    fpr_c2, tpr_c2, _ = roc_curve(y, pb)
    mac("TreeFPRatRuleTPR", pc(float(np.interp(tpr, tpr_c2, fpr_c2))))
    say("trees_fpr_at_rule_tpr", float(np.interp(tpr, tpr_c2, fpr_c2)))
    arel = det.rv_rms / det.sigma_eff
    amp = {}
    for nm, m in (("0.2-0.5", imp & (arel < 0.5)), ("0.5-1", imp & arel.between(0.5, 1.0)), ("1-3", imp & (arel > 1.0))):
        amp[nm] = dict(n=int(m.sum()), rule_accept=float(rp[m.values].mean()), trees_accept=float((pb[m.values] > 0.5).mean()))
    say("activity_impostors_by_rv_amplitude", amp)
    for nm, N_ in (("0.2-0.5", "Lo"), ("1-3", "Hi")):
        mac(f"Amp{N_}N", amp[nm]["n"]); mac(f"Amp{N_}Rule", pc(amp[nm]["rule_accept"])); mac(f"Amp{N_}Tree", pc(amp[nm]["trees_accept"]))
    lam_split = {}
    for nm, m in (("short", det.lam_rot < 3), ("long", det.lam_rot > 10)):
        line_k1 = (det.kind == "rotation_line") & m & ((1.0 / det.period) >= (1.0 / (np.pi * det.lam)))
        lam_split[nm] = dict(line_k1to4=int(line_k1.sum()), harmonic=int(((det.kind == "rotation_harmonic") & m).sum()))
    say("line_vs_harmonic_by_lambda_excluding_k0", lam_split)
    mac("LineShort", lam_split["short"]["line_k1to4"]); mac("HarmShort", lam_split["short"]["harmonic"])
    mac("LineLong", lam_split["long"]["line_k1to4"]); mac("HarmLong", lam_split["long"]["harmonic"])
    mac("ImpRotLineNoEnv", thou(int(kinds.get("rotation_line", 0)) - int(env.sum())))
    lp = imp & (det.P_rot > 40) & (det.lam_rot > 10)
    say("long_prot_long_lambda", dict(n=int(lp.sum()), rule=float(rp[lp.values].mean()), trees=float((pb[lp.values] > 0.5).mean())))
    mac("DomBothN", int(lp.sum())); mac("DomBothRule", pc(rp[lp.values].mean())); mac("DomBothTree", pc((pb[lp.values] > 0.5).mean()))

    # ------------------------------------------------------------ how often a rotation proxy is found
    prox = {}
    for nm, m in (("planet_only_detected", plo), ("activity_impostors", imp),
                  ("activity_series_all", d.cls.str.contains("activity")), ("noise_series_all", d.cls == "noise")):
        src = det if nm in ("planet_only_detected", "activity_impostors") else d
        prox[nm] = float((src.loc[m, "act_log10_fap"] < -2).mean())
    say("rotation_proxy_rate_sims", prox)
    mac("ProxyPlanetPct", pc(prox["planet_only_detected"], 1)); mac("ProxyActPct", pc(prox["activity_impostors"]))
    noproxy = [c for c in X.columns if not (c.startswith("act_") or c.startswith("harm"))]
    p_noproxy = grouped_cv_predict(models()["boosting"], X[noproxy], y, groups)
    say("cv_boosting_no_proxy", metrics(y, p_noproxy)); mac("AucNoProxy", f"{auc(y, p_noproxy):.3f}")

    # ------------------------------------------------------------ permutation importance
    rng = np.random.default_rng(0)
    ustars = np.unique(groups); test_st = set(rng.choice(ustars, len(ustars) // 4, replace=False))
    te = np.array([g in test_st for g in groups])
    mb = models()["boosting"].fit(X[~te], y[~te])
    pi = permutation_importance(mb, X[te], y[te], scoring="roc_auc", n_repeats=10, random_state=0)
    imp_s = pd.Series(pi.importances_mean, index=X.columns).sort_values(ascending=False)
    say("perm_importance_boosting", imp_s.round(4).to_dict())
    mac("ImpTopFeat", r"\code{" + imp_s.index[0].replace("_", r"\_") + "}")
    mac("ImpTopVal", f"{imp_s.iloc[0]:.2f}"); mac("ImpSecondVal", f"{imp_s.iloc[1]:.3f}")
    mac("ImpSecondFeat", r"\code{" + imp_s.index[1].replace("_", r"\_") + "}")

    # ======================================================================= benchmark
    lit = pd.read_csv(os.path.join(ROOT, "benchmark_literature.csv"))
    b = pd.read_csv(os.path.join(RES, "benchmark_features.csv"))
    refs = json.load(open(os.path.join(PAP, "bench_refs.json")))
    b = b.merge(lit[["signal", "harps_in_discovery", "prot_d", "rvbank_star"]], on="signal", how="left")
    b["detected"] = b.log10_fap < -2
    b["detected_single"] = b.log10_p_single < -2
    b["upheld"] = b.label.str.startswith("UPHELD").astype(int)
    b["binary"] = b.label.isin(["UPHELD_INDEPENDENT", "UPHELD_HARPS", "REFUTED"])
    fits = {name: m.fit(X, y) for name, m in models().items()}
    mni = models()["boosting"].fit(X[noind], y)
    Xb = design(b)
    for name, m in fits.items():
        b[f"p_{name}"] = m.predict_proba(Xb[X.columns])[:, 1]
    b["p_no_indicators"] = mni.predict_proba(Xb[noind])[:, 1]
    mnp = models()["boosting"].fit(X[noproxy], y)
    b["p_no_proxy"] = mnp.predict_proba(Xb[noproxy])[:, 1]
    b["rule"] = rule_pass(b); b["rule_alias"] = rule_pass(b, alias_aware=True)
    b["first_fail"] = first_failed_rung(b)
    bb = b[b.binary].copy()
    cnt = bb.label.value_counts().to_dict()
    say("bench_counts", cnt)
    mac("BenchN", len(b)); mac("BenchUI", cnt.get("UPHELD_INDEPENDENT", 0)); mac("BenchUH", cnt.get("UPHELD_HARPS", 0))
    mac("BenchR", cnt.get("REFUTED", 0)); mac("BenchD", int((b.label == "DISPUTED").sum())); mac("BenchBinary", len(bb))
    mac("BenchNotHarps", int((b.harps_in_discovery == "no").sum()))
    dl = bb.groupby("label").agg(det=("detected", "sum"), det1=("detected_single", "sum"), n=("detected", "size"))
    say("bench_detected_by_label", dl.to_dict())
    ref = bb[bb.upheld == 0]; up = bb[bb.upheld == 1]
    mac("RefDet", int(ref.detected.sum())); mac("RefNotDet", int((~ref.detected).sum()))
    mac("UpDet", int(up.detected.sum())); mac("UpN", len(up)); mac("UpNotDet", int((~up.detected).sum()))
    mac("RefDetSingle", int(ref.detected_single.sum())); mac("RefNotDetSingle", int((~ref.detected_single).sum()))
    mac("UpNotDetSingle", int((~up.detected_single).sum()))
    say("bench_first_fail", bb.groupby(["label", "first_fail"]).size().to_dict())
    rff = ref.first_fail.value_counts().to_dict()
    say("bench_refuted_first_fail", rff)
    for k, nm in (("detection", "Det"), ("period", "Period"), ("phase", "Phase"), ("indicators", "Ind"), ("rotation", "Rot"), ("passes", "Pass")):
        mac(f"RefFF{nm}", rff.get(k, 0))
    # rule among significant signals: exact intervals
    rd, ud = ref[ref.detected], up[up.detected]
    k_acc_ref = int(rd.rule.sum()); n_ref = len(rd); k_rej_up = int((~ud.rule).sum()); n_up = len(ud)
    say("bench_rule_detected", dict(refuted_accepted=k_acc_ref, n_refuted=n_ref, upheld_rejected=k_rej_up, n_upheld=n_up,
                                    fpr_ci=cp(k_acc_ref, n_ref), fnr_ci=cp(k_rej_up, n_up)))
    mac("BRuleRefAcc", k_acc_ref); mac("RuleRejRef", n_ref - k_acc_ref); mac("BRuleRefN", n_ref); mac("BRuleUpRej", k_rej_up); mac("BRuleUpN", n_up)
    mac("BRuleFPRHi", pc(cp(k_acc_ref, n_ref)[1])); mac("BRuleFNRHi", pc(cp(k_rej_up, n_up)[1]))
    mac("BRuleFPRLo", pc(cp(k_acc_ref, n_ref)[0])); mac("BRuleFNRLo", pc(cp(k_rej_up, n_up)[0]))
    ui_d = ud[ud.label == "UPHELD_INDEPENDENT"]
    mac("BRuleUIRej", int((~ui_d.rule).sum())); mac("BRuleUIN", len(ui_d))
    mac("BRuleUHRej", int((~ud[ud.label == "UPHELD_HARPS"].rule).sum())); mac("BRuleUHN", int((ud.label == "UPHELD_HARPS").sum()))
    ra = dict(refuted_accepted=int(rd.rule_alias.sum()), upheld_rejected=int((~ud.rule_alias).sum()),
              upheld_rejected_names=ud.loc[~ud.rule_alias, "signal"].tolist(), refuted_accepted_names=rd.loc[rd.rule_alias, "signal"].tolist())
    say("bench_rule_alias_detected", ra)
    mac("BRuleAliasUpRej", ra["upheld_rejected"]); mac("BRuleAliasRefAcc", ra["refuted_accepted"])
    same = bool((sig_rule := bb.loc[bb.detected, "rule"]).equals(bb.loc[bb.detected, "rule_alias"]))
    mac("BRuleAliasEffect", "changes none of these outcomes" if same else
        f"rejects {ra['upheld_rejected']} significant upheld and accepts {ra['refuted_accepted']} significant refuted signals")
    # classifiers among significant signals
    sig = bb[bb.detected]
    ys = sig.upheld.values
    bres = {}
    for name in ("boosting", "logistic", "no_indicators", "no_proxy"):
        pp = sig[f"p_{name}"].values
        a = auc(ys, pp); lo, hi = boot_auc_stratified(ys, pp)
        bad, tot = misordered_pairs(ys, pp)
        ui = sig.label != "UPHELD_HARPS"
        bres[name] = dict(auc=a, lo=lo, hi=hi, misordered=bad, pairs=tot, auc_UI_only=auc(ys[ui.values], pp[ui.values]))
    say("bench_classifiers_detected", bres)
    for name, N_ in (("boosting", "Tree"), ("logistic", "Log"), ("no_indicators", "NoInd"), ("no_proxy", "NoProxy")):
        r = bres[name]
        mac(f"BAuc{N_}", f2(r["auc"])); mac(f"BAuc{N_}Lo", f2(r["lo"])); mac(f"BAuc{N_}Hi", f2(r["hi"]))
        mac(f"BMis{N_}", f"{r['misordered']:g}"); mac(f"BAuc{N_}UI", f2(r["auc_UI_only"]))
    mac("BPairs", int(bres["boosting"]["pairs"]))
    for name, N_ in (("boosting", "Tree"), ("logistic", "Log"), ("no_indicators", "NoInd")):
        acc_ = sig[f"p_{name}"] > 0.5
        mac(f"B{N_}RefAcc", int((acc_ & (sig.upheld == 0)).sum())); mac(f"B{N_}UpRej", int((~acc_ & (sig.upheld == 1)).sum()))
        say(f"bench_{name}_at_0.5", dict(refuted_accepted=sig.loc[acc_ & (sig.upheld == 0), "signal"].tolist(),
                                          upheld_rejected=sig.loc[~acc_ & (sig.upheld == 1), "signal"].tolist()))
    hosts = b.drop_duplicates("rvbank_star") if "rvbank_star" in b else b.drop_duplicates("host")
    say("rotation_proxy_rate_benchmark", dict(hosts=float((hosts.act_log10_fap < -2).mean()), n_hosts=len(hosts),
                                              upheld_significant=float((sig.loc[sig.upheld == 1, "act_log10_fap"] < -2).mean())))
    mac("ProxyHostsN", int((hosts.act_log10_fap < -2).sum())); mac("NHosts", len(hosts))
    mac("ProxyUpSigN", int((sig.loc[sig.upheld == 1, "act_log10_fap"] < -2).sum()))
    hp = hosts.copy()
    hp["prot_lit"] = hp.prot_d.map(lambda x: (lambda m_: float(m_.group(0)) if m_ else np.nan)(re.search(r"\d+(\.\d+)?", str(x).split(";")[0])))
    cmpp = hp[np.isfinite(hp.prot_lit) & (hp.act_log10_fap < -2)]
    agree = (np.abs(cmpp.act_period / cmpp.prot_lit - 1) < 0.2)
    say("proxy_vs_published_prot", dict(n=len(cmpp), agree_20pct=int(agree.sum()),
                                        rows=cmpp[["rvbank_star", "act_period", "prot_lit"]].round(1).to_dict("records")))
    mac("ProxyCmpN", len(cmpp)); mac("ProxyAgreeN", int(agree.sum()))
    top_ref = int(sig.loc[sig.upheld == 0, "is_top"].sum()); top_up = int(sig.loc[sig.upheld == 1, "is_top"].sum())
    say("bench_is_highest_peak", dict(refuted=top_ref, upheld=top_up))
    mac("TopRef", top_ref); mac("TopUp", top_up)
    easy = sig.snr_K > 20
    say("bench_easy_controls", sig.loc[easy & (sig.upheld == 1), "signal"].tolist())
    mac("BEasyN", int((easy & (sig.upheld == 1)).sum()))
    if (~easy).sum() and len(np.unique(ys[~easy.values])) == 2:
        mac("BAucTreeNoEasy", f2(auc(ys[~easy.values], sig.p_boosting.values[~easy.values])))
    ba = {}
    for c in ["log10_fap", "dchi2", "snr_K", "alias_margin", "growth_rho", "block_phase_rms", "block_phase_p", "ind_max_dchi2",
              "apod_gain", "half_phase_z"]:
        v = sig[c].values.astype(float); ok = np.isfinite(v)
        a = roc_auc_score(ys[ok], v[ok]); ba[c] = max(a, 1 - a)
    say("bench_single_feature_auc_detected", {k: round(v, 3) for k, v in sorted(ba.items(), key=lambda kv: -kv[1])})
    for k, nm in (("log10_fap", "Fap"), ("growth_rho", "Growth"), ("alias_margin", "Alias"), ("ind_max_dchi2", "Ind"),
                  ("block_phase_rms", "BlockRms")):
        mac(f"BSingle{nm}", f2(ba[k]))
    # significant refuted and non-significant upheld details
    gj = b.set_index("signal")
    rows_ref = []
    for s_ in rd.signal:
        r = gj.loc[s_]
        rows_ref.append(dict(signal=s_, log10_fap=r.log10_fap, alias_margin=r.alias_margin, alias_period=r.alias_period,
                             ind=r.ind_max_dchi2, ind_which=r.ind_argmax, act_period=r.act_period, act_lfap=r.act_log10_fap,
                             harm_dist=r.harm_dist, first_fail=r.first_fail, p_trees=r.p_boosting, p_log=r.p_logistic,
                             p_noind=r.p_no_indicators, edge=r.period_at_window_edge, rule_alias=r.rule_alias))
    say("bench_refuted_detected_details", rows_ref)
    ind_names = {"dlw": r"$\Delta$LW", "halpha": r"H$\alpha$", "fwhm": "FWHM", "bis": "BIS", "contrast": "contrast",
                 "crx": "CRX", "nad1": r"Na\,D1", "rhk": r"$R'_{\rm HK}$", "": "--"}
    ffs0 = {"detection": "det.", "period": "period", "phase": "phase", "indicators": "ind.", "rotation": "rot.", "passes": "--"}
    lines = []
    for r_ in rows_ref + [dict(signal=s_, **{k: gj.loc[s_][v] for k, v in (("log10_fap", "log10_fap"), ("alias_margin", "alias_margin"),
                                  ("alias_period", "alias_period"), ("ind", "ind_max_dchi2"), ("ind_which", "ind_argmax"),
                                  ("act_period", "act_period"), ("harm_dist", "harm_dist"), ("first_fail", "first_fail"),
                                  ("p_trees", "p_boosting"), ("p_log", "p_logistic"), ("p_noind", "p_no_indicators"))})
                          for s_ in ud.loc[~ud.rule, "signal"]]:
        hd_ = "--" if not np.isfinite(r_["harm_dist"]) else f"{r_['harm_dist']:.1f}"
        lfa = gj.loc[r_["signal"]].act_log10_fap
        pa = f"{r_['act_period']:.0f}" if (np.isfinite(r_["act_period"]) and lfa < -2) else "--"
        wh = r_["ind_which"] if isinstance(r_["ind_which"], str) else ""
        vv = {"REFUTED": "R", "UPHELD_INDEPENDENT": "UI", "UPHELD_HARPS": "UH"}[gj.loc[r_["signal"]].label]
        lines.append(f"{refs[r_['signal']]['tabname']} & {vv} & ${r_['log10_fap']:.1f}$ & ${r_['alias_margin']:.1f}$ & "
                     f"{r_['ind']:.2f} ({ind_names.get(wh, wh)}) & {pa} & {hd_} & {ffs0[r_['first_fail']]} & "
                     f"{r_['p_trees']:.2f} & {r_['p_log']:.2f} & {r_['p_noind']:.2f} \\\\")
    open(os.path.join(PAP, "tab_refsig_rows.tex"), "w").write("\n".join(lines) + "\n")
    und = up[~up.detected]
    say("bench_upheld_not_detected", und[["signal", "snr_K", "log10_fap", "log10_p_single"]].round(2).to_dict("records"))
    mac("UpNotDetSnrLo", f"{und.snr_K.min():.1f}"); mac("UpNotDetSnrHi", f"{und.snr_K.max():.1f}")
    # the rotation periods of the refuted hosts against the simulated range
    def prot_first(x):
        m_ = re.search(r"[-+]?\d+(\.\d+)?", str(x).split(";")[0])
        return float(m_.group(0)) if m_ else np.nan
    b["prot_lit"] = b.prot_d.map(prot_first)
    outside = b[(b.label == "REFUTED") & ((b.prot_lit < 3) | (b.prot_lit > 150))]
    say("refuted_hosts_prot_outside_sim_range", outside[["signal", "prot_lit"]].to_dict("records"))
    mac("RefOutsideProt", len(outside))
    b.to_csv(os.path.join(RES, "benchmark_scored.csv"), index=False)

    # ------------------------------------------------------------ frozen (v0.1) pass against this one
    old = pd.read_csv(os.path.join(ROOT, "results_v0.1", "benchmark_scored.csv"))
    cmp_ = old[["signal", "label", "detected", "rule", "first_fail", "log10_fap", "p_boosting"]].merge(
        b[["signal", "detected", "rule", "first_fail", "log10_fap", "p_boosting"]], on="signal", suffixes=("_v01", "_v02"))
    cmp_["changed"] = (cmp_.detected_v01 != cmp_.detected_v02) | (cmp_.rule_v01 != cmp_.rule_v02) | \
                      (cmp_.first_fail_v01.replace({"passes": "passes"}) != cmp_.first_fail_v02)
    cmp_.to_csv(os.path.join(RES, "benchmark_v01_vs_v02.csv"), index=False)
    ch = cmp_[cmp_.changed]
    say("bench_changed_v01_to_v02", ch[["signal", "label", "detected_v01", "detected_v02", "rule_v01", "rule_v02", "first_fail_v01",
                                         "first_fail_v02"]].to_dict("records"))
    mac("BChanged", len(ch))
    lab = {"UPHELD_INDEPENDENT": "UI", "UPHELD_HARPS": "UH", "REFUTED": "R", "DISPUTED": "D"}
    ffs = {"detection": "det.", "period": "period", "phase": "phase", "indicators": "ind.", "rotation": "rot.", "passes": "--"}
    lines = []
    for _, r in ch.sort_values(["label", "signal"]).iterrows():
        lines.append(f"{_tex_signal(r.signal)} & {lab[r.label]} & ${r.log10_fap_v01:.1f}$ & {ffs[r.first_fail_v01]} & "
                     f"${r.log10_fap_v02:.1f}$ & {ffs[r.first_fail_v02]} \\\\")
    open(os.path.join(PAP, "tab_v01_rows.tex"), "w").write("\n".join(lines) + "\n")
    # sensitivity to the claimed-period window
    bw = pd.read_csv(os.path.join(RES, "benchmark_windows.csv"))
    bw = bw[bw.label.isin(["UPHELD_INDEPENDENT", "UPHELD_HARPS", "REFUTED"])].copy()
    bw["upheld"] = bw.label.str.startswith("UPHELD").astype(int)
    bw["detected"] = bw.log10_fap < -2
    bw["rule"] = rule_pass(bw)
    Xw = design(bw)
    bw["p_boosting"] = fits["boosting"].predict_proba(Xw[X.columns])[:, 1]
    bw["p_logistic"] = fits["logistic"].predict_proba(Xw[X.columns])[:, 1]
    wl = []
    for w, g in bw.groupby("window", sort=False):
        sg = g[g.detected]; rs, us = sg[sg.upheld == 0], sg[sg.upheld == 1]
        ys_ = sg.upheld.values
        row = dict(window=w, ref_sig=len(rs), ref_rejected=int((~rs.rule).sum()), up_sig=len(us), up_rejected=int((~us.rule).sum()),
                   ref_not_single=int((g[g.upheld == 0].log10_p_single >= -2).sum()),
                   up_not_single=int((g[g.upheld == 1].log10_p_single >= -2).sum()),
                   auc_trees=auc(ys_, sg.p_boosting.values) if len(np.unique(ys_)) == 2 else np.nan,
                   auc_log=auc(ys_, sg.p_logistic.values) if len(np.unique(ys_)) == 2 else np.nan,
                   changed_from_adopted=[])
        wl.append(row)
    base = bw[bw.window == 0.5].set_index("signal")
    for row in wl:
        g = bw[bw.window == row["window"]].set_index("signal")
        ch_ = [s_ for s_ in g.index if (g.loc[s_, "detected"] != base.loc[s_, "detected"]) or
               (g.loc[s_, "detected"] and g.loc[s_, "rule"] != base.loc[s_, "rule"])]
        row["changed_from_adopted"] = ch_
    say("bench_window_sensitivity", wl)
    lines = []
    wname = {0.5: r"$\pm0.5/T$ (adopted)", 0.25: r"$\pm0.25/T$ (first pass)", 0.0: "claimed period"}
    for row in wl:
        lines.append(f"{wname[row['window']]} & {row['ref_sig']} & {row['ref_rejected']} & {row['up_sig']} & {row['up_rejected']} & "
                     f"{row['auc_trees']:.2f} & {row['auc_log']:.2f} & {row['ref_not_single']} & {row['up_not_single']} \\\\")
    open(os.path.join(PAP, "tab_window_rows.tex"), "w").write("\n".join(lines) + "\n")
    wq = {row["window"]: row for row in wl}
    mac("WinQRefSig", wq[0.25]["ref_sig"]); mac("WinQRefRej", wq[0.25]["ref_rejected"]); mac("WinQUpRej", wq[0.25]["up_rejected"])
    mac("WinZRefSig", wq[0.0]["ref_sig"]); mac("WinZRefRej", wq[0.0]["ref_rejected"]); mac("WinZUpRej", wq[0.0]["up_rejected"])
    mac("WinZUpSig", wq[0.0]["up_sig"]); mac("WinQUpSig", wq[0.25]["up_sig"])
    mac("NEdge", int(b.period_at_window_edge.sum()))
    # appendix table
    order = {"UPHELD_INDEPENDENT": 0, "UPHELD_HARPS": 1, "REFUTED": 2, "DISPUTED": 3}
    bt = b.assign(o=b.label.map(order)).sort_values(["o", "signal"])
    lines = []
    for _, r in bt.iterrows():
        rf = refs[r.signal]
        pt = f"{r.p_boosting:.2f}" if r.detected else f"({r.p_boosting:.2f})"
        off = f"${r.period_offset:+.2f}$" + ("$^e$" if r.period_at_window_edge else "")
        lines.append(f"{rf['tabname']} & {_fmt_p(r.P_claim)} & {_fmt_k(r.K_claim)} & {lab[r.label]} & {int(r.n)} & {off} & "
                     f"${r.log10_fap:.1f}$ & {r.snr_K:.1f} & {ffs[r.first_fail]} & {pt} & {rf['refs']} \\\\")
    open(os.path.join(PAP, "tab_bench_rows.tex"), "w").write("\n".join(lines) + "\n")

    # ======================================================================= the archive
    df = pd.read_parquet(os.path.join(ROOT, "data", "rvbank.parquet"))
    say("rvbank_spectra_stars", [len(df), int(df.star.nunique()), float(df.bjd.max())])
    mac("RVBankSpectra", thou(len(df))); mac("RVBankStars", thou(df.star.nunique()))
    qm = rvvet.quality_mask(df)
    mac("RVBankKeptPct", pc(qm.mean()))
    bench_clip = {}
    for st in sorted(set(lit.rvbank_star)):
        ss = rvvet.load_star(df, st, clip_sigma=15)
        bench_clip[st] = int(ss.meta.get("n_clipped", 0))
    say("benchmark_clipped_epochs", {k: v for k, v in bench_clip.items() if v})
    mac("BenchClipped", sum(bench_clip.values())); mac("BenchClippedStars", sum(v > 0 for v in bench_clip.values()))
    prox = df[df.star == "GJ551"]
    if len(prox):
        mac("ProxSpec", len(prox)); mac("ProxLossTwenty", pc(float((prox.snr < 20).mean())))

    # ======================================================================= HD 297396 b
    s = rvvet.load_star(df, "HD297396", clip_sigma=15)
    r = rvvet.vet(s, period=HD297396_P, trend=2)
    rr = pd.DataFrame([r]); Xr = design(rr)
    r["p_boosting"] = float(fits["boosting"].predict_proba(Xr[X.columns])[:, 1][0])
    r["p_logistic"] = float(fits["logistic"].predict_proba(Xr[X.columns])[:, 1][0])
    r["p_no_indicators"] = float(mni.predict_proba(Xr[noind])[:, 1][0])
    r["rule"] = bool(rule_pass(rr).iloc[0]); r["rule_alias"] = bool(rule_pass(rr, True).iloc[0])
    say("hd297396b", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if not k.startswith("_") and k != "star"})
    mac("HDn", int(r["n"])); mac("HDbase", f"{r['baseline'] / 365.25:.1f}"); mac("HDfap", f"{r['log10_fap']:.1f}")
    mac("HDsnr", f"{r['snr_K']:.1f}"); mac("HDK", f"{r['K']:.1f}"); mac("HDsK", f"{r['sK']:.1f}")
    mac("HDalias", f"{r['alias_margin']:.1f}"); mac("HDhalf", f"{r['half_phase_z']:.1f}"); mac("HDblockp", f2(r["block_phase_p"]))
    mac("HDrho", f2(r["growth_rho"])); mac("HDapod", f"{r['apod_gain']:.1f}"); mac("HDind", f"{r['ind_max_dchi2']:.1f}")
    mac("HDact", f"{r['act_log10_fap']:.1f}"); mac("HDpTree", f2(r["p_boosting"])); mac("HDpLog", f2(r["p_logistic"]))
    mac("HDpNoInd", f2(r["p_no_indicators"])); mac("HDrule", "passes" if r["rule"] else "fails")
    mac("HDnspec", int(s.meta.get("n_spectra", 0)))

    # ======================================================================= defect log
    dl_ = pd.read_csv(os.path.join(ROOT, "defects", "defect_log.csv"))
    A = pd.read_csv(os.path.join(ROOT, "defects", "coder_A.csv")); B = pd.read_csv(os.path.join(ROOT, "defects", "coder_B.csv"))
    mm = A.merge(B, on="id", suffixes=("_A", "_B"))
    kap = {f: (float((mm[f + "_A"] == mm[f + "_B"]).mean()), float(cohen_kappa_score(mm[f + "_A"], mm[f + "_B"])))
           for f in ("category", "origin")}
    say("defects_agreement_kappa", kap)
    mac("DefExcluded", len(pd.read_csv(os.path.join(ROOT, "defects", "excluded.csv"))))
    mac("DefN", len(dl_)); mac("DefKappaCat", f2(kap["category"][1])); mac("DefKappaOri", f2(kap["origin"][1]))
    mac("DefAgreeCat", pc(kap["category"][0])); mac("DefAgreeOri", pc(kap["origin"][0]))
    mac("DefDisagree", int(((mm.category_A != mm.category_B) | (mm.origin_A != mm.origin_B)).sum()))
    for f in ("route", "category", "origin", "stage", "version"):
        say(f"defects_by_{f}", dl_[f].value_counts().to_dict())
    rt = dl_.route.value_counts().to_dict(); ct_ = dl_.category.value_counts().to_dict(); og = dl_.origin.value_counts().to_dict()
    for k, nm in (("independent-reviewer", "Rev"), ("self-review", "Self"), ("unattributed", "Unatt"), ("external-report", "Ext"),
                  ("reference-check", "Ref")):
        mac(f"DefRoute{nm}", rt.get(k, 0))
    for k in ("transcription", "arithmetic", "method", "overclaim", "stale", "reasoning", "reference", "wording"):
        mac("DefCat" + k.capitalize(), ct_.get(k, 0))
    for k, nm in (("code-to-text", "Code"), ("literature-to-text", "Lit"), ("analysis", "Ana"), ("interpretation", "Interp"),
                  ("revision", "Rev")):
        mac(f"DefOri{nm}", og.get(k, 0))
    stg = dl_.stage.value_counts().to_dict(); mac("DefDraft", stg.get("draft", 0)); mac("DefReleased", stg.get("released", 0))
    ovr = dl_[dl_.category == "overclaim"].route.value_counts().to_dict()
    mac("DefOverRev", ovr.get("independent-reviewer", 0))
    say("defects_overclaim_by_route", ovr)
    # table: category x route
    cats = ["overclaim", "transcription", "method", "arithmetic", "wording", "stale", "reference", "reasoning"]
    routes = ["self-review", "independent-reviewer", "external-report", "reference-check", "unattributed"]
    tab = pd.crosstab(dl_.category, dl_.route).reindex(index=cats, columns=routes, fill_value=0)
    lines = [f"{c.capitalize()} & " + " & ".join(str(int(v)) for v in tab.loc[c].values) + f" & {int(tab.loc[c].sum())} \\\\"
             for c in cats]
    lines.append(r"\hline")
    lines.append("Total & " + " & ".join(str(int(v)) for v in tab.sum().values) + f" & {int(tab.values.sum())} \\\\")
    open(os.path.join(PAP, "tab_defects_rows.tex"), "w").write("\n".join(lines) + "\n")
    tab2 = pd.crosstab(dl_.origin, dl_.category).reindex(index=["code-to-text", "literature-to-text", "analysis", "interpretation", "revision"],
                                                        columns=cats, fill_value=0)
    tab2.to_csv(os.path.join(RES, "defects_origin_by_category.csv"))
    say("defects_origin_by_category", tab2.to_dict())
    mac("DefRevOver", int(tab2.loc["revision", "overclaim"]))
    numd = dl_[dl_.category.isin(["transcription", "arithmetic"])]
    no = numd.origin.value_counts().to_dict()
    say("defects_numerical_by_origin", no)
    mac("DefNumN", len(numd)); mac("DefNumLit", no.get("literature-to-text", 0)); mac("DefNumAna", no.get("analysis", 0))
    mac("DefNumCode", no.get("code-to-text", 0)); mac("DefNumRev", no.get("revision", 0))
    mac("DefOverPct", pc(ct_.get("overclaim", 0) / len(dl_)))

    # ======================================================================= figures
    # FAP calibration
    fig, ax = plt.subplots(figsize=(W1, 2.6))
    a = np.logspace(-3, 0, 60)
    for kind, stat, col, ls, lab_ in (("permuted", "log10_fap", "#2a78d6", "-", "real noise, jitter profiled (ladder)"),
                                      ("gaussian", "log10_fap", "#2a78d6", ":", "Gaussian noise, jitter profiled"),
                                      ("permuted", "log10_fap_h0", "#c0392b", "-", "real noise, jitter fixed (v0.1)"),
                                      ("gaussian", "log10_fap_h0", "#c0392b", ":", "Gaussian noise, jitter fixed")):
        v = fc.loc[fc.kind == kind, stat].values
        fr = np.array([np.mean(v < np.log10(x)) for x in a])
        k_ = np.array([np.sum(v < np.log10(x)) for x in a]); n_ = len(v)
        ci = np.array([cp(int(kk), n_) for kk in k_])
        ax.plot(a, fr, color=col, ls=ls, lw=1.0, label=lab_)
        if ls == "-":
            ax.fill_between(a, np.clip(ci[:, 0], 1e-5, 1), ci[:, 1], color=col, alpha=0.15, lw=0)
    ax.plot(a, a, color="#222", lw=0.7, ls="--", label="nominal")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(1e-3, 1); ax.set_ylim(1e-4, 1)
    ax.set_xlabel("Baluev FAP threshold"); ax.set_ylabel("fraction of noise-only series below it")
    ax.legend(frameon=False, loc="lower right")
    fig.savefig(os.path.join(FIG, "fig_fapcal.pdf")); plt.close(fig)
    # completeness
    fig, ax = plt.subplots(figsize=(W1, 2.3))
    ax.errorbar(xc, yc, yerr=np.sqrt(yc * (1 - yc) / comp["size"].values), fmt="o-", ms=3, lw=0.9, color="#2a78d6", capsize=0)
    ax.set_xscale("log"); ax.set_xticks([1, 2, 3, 5, 7, 10, 20]); ax.set_xticklabels(["1", "2", "3", "5", "7", "10", "20"])
    ax.minorticks_off(); ax.set_ylim(0, 1.02)
    ax.set_xlabel(r"expected $K/\sigma_K$ ($\sigma_K=\sigma\sqrt{2/N}$)"); ax.set_ylabel("recovered at the right period")
    fig.savefig(os.path.join(FIG, "fig_completeness.pdf")); plt.close(fig)
    # ROC
    fig, ax = plt.subplots(figsize=(W1, 2.8))
    for name, c, ls, lab_ in (("boosting", "#c0392b", "-", "boosted trees"), ("logistic", "#2a78d6", "-", "logistic regression"),
                              ("no_indicators", "#c0392b", ":", "trees, no indicator features"),
                              ("detection_only", "#8a8a85", "--", "detection statistics only"),
                              ("fap_only", "#8a8a85", ":", "FAP only")):
        fpr_, tpr_, _ = roc_curve(y, preds[name])
        ax.plot(fpr_, tpr_, color=c, ls=ls, lw=1.0, label=f"{lab_} ({auc(y, preds[name]):.2f})")
    ax.plot(fpr, tpr, "ks", ms=4, label="a-priori rule")
    ax.plot([0, 1], [0, 1], color="#ccc", lw=0.6)
    ax.set_xlabel("false-positive rate (impostors accepted)"); ax.set_ylabel("true-positive rate (planets accepted)")
    ax.legend(frameon=False, loc="lower right")
    fig.savefig(os.path.join(FIG, "fig_roc.pdf")); plt.close(fig)
    # reliability
    fig, ax = plt.subplots(figsize=(W1, 2.5))
    for name, c in (("boosting", "#c0392b"), ("logistic", "#2a78d6")):
        ct = pd.read_csv(os.path.join(RES, f"calibration_{name}.csv"))
        ax.errorbar(ct.p_mean, ct.frac_pos, yerr=np.sqrt(ct.p_mean * (1 - ct.p_mean) / ct.n), fmt="o-", color=c, ms=3, lw=0.9,
                    capsize=0, label={"boosting": "boosted trees", "logistic": "logistic regression"}[name])
    ax.plot([0, 1], [0, 1], color="#222", lw=0.6, ls="--")
    ax.set_xlabel("predicted probability of a planet"); ax.set_ylabel("fraction that are planets"); ax.legend(frameon=False)
    fig.savefig(os.path.join(FIG, "fig_reliability.pdf")); plt.close(fig)
    # importance
    fig, ax = plt.subplots(figsize=(W1, 3.0))
    top = imp_s.head(12)[::-1]
    ax.barh(range(len(top)), top.values, color="#2a78d6")
    ax.set_yticks(range(len(top))); ax.set_yticklabels([t.replace("_", " ") for t in top.index])
    ax.set_xscale("symlog", linthresh=0.005); ax.set_xlabel("drop in AUC when permuted (held-out stars)")
    fig.savefig(os.path.join(FIG, "fig_importance.pdf")); plt.close(fig)
    # benchmark
    colors = {"REFUTED": "#c0392b", "UPHELD_HARPS": "#1baf7a", "UPHELD_INDEPENDENT": "#2a78d6", "DISPUTED": "#8a8a85"}
    order2 = {"REFUTED": 0, "UPHELD_HARPS": 1, "UPHELD_INDEPENDENT": 2, "DISPUTED": 3}
    bs = b.assign(o=b.label.map(order2)).sort_values(["o", "p_boosting"], ascending=[False, True]).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(W1, 5.6))
    for i, r0 in bs.iterrows():
        c = colors[r0.label]
        ax.plot(r0.p_boosting, i, "o", mfc=c if r0.detected else "white", mec=c, ms=4, mew=0.9)
        if (not r0.rule) and r0.detected:
            ax.plot(r0.p_boosting, i, "x", color="k", ms=3, mew=0.8)
    for k in range(1, len(bs)):
        if bs.o[k] != bs.o[k - 1]:
            ax.axhline(k - 0.5, color="#ddd", lw=0.6)
    ax.set_yticks(range(len(bs)))
    ax.set_yticklabels([refs[s_]["tabname"].replace("$\\alpha$", r"$\alpha$") for s_ in bs.signal], fontsize=5.5)
    ax.axvline(0.5, color="#bbb", lw=0.6); ax.set_xlim(-0.03, 1.03); ax.set_ylim(-0.7, len(bs) - 0.3)
    ax.set_xlabel("score from boosted trees trained on simulations")
    h = [Line2D([], [], marker="o", ls="", color=colors[k], label=k.replace("_", " ").lower()) for k in
         ("UPHELD_INDEPENDENT", "UPHELD_HARPS", "REFUTED", "DISPUTED")]
    h += [Line2D([], [], marker="o", ls="", mfc="white", mec="k", label="not significant (FAP > 1%)"),
          Line2D([], [], marker="x", ls="", color="k", label="significant, fails the a-priori rule")]
    ax.legend(handles=h, frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.07), ncol=2, fontsize=5.5)
    fig.savefig(os.path.join(FIG, "fig_benchmark.pdf")); plt.close(fig)

    # ======================================================================= outputs
    json.dump(NUM, open(os.path.join(RES, "numbers.json"), "w"), indent=1, default=str)
    with open(os.path.join(PAP, "numbers.tex"), "w") as fh:
        fh.write("% Generated by rvvet/scripts/analyze.py -- do not edit. One macro per number in the text.\n")
        for k in sorted(MAC):
            fh.write(f"\\newcommand{{\\nm{k}}}{{{MAC[k]}}}\n")
    print(f"{len(MAC)} macros written")


def _tex_signal(s):
    return s.replace("alpha", r"$\alpha$").replace("tau", r"$\tau$").replace("pi Men", r"$\pi$ Men")


def _fmt_p(P):
    return f"{P:.4g}" if P < 100 else f"{P:.1f}" if P < 1000 else f"{P:.0f}"


def _fmt_k(K):
    return f"{K:.3g}"


if __name__ == "__main__":
    main()
