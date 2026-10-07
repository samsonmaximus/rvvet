"""Forward-in-time test of the vetting ladder (Sect. 6.5 of the paper).

The 30 September 2026 blind run of rvvet 0.3.1 on every HARPS-RVBank star with at least 20 nights
over 100 d (archive_run_2026-09-30/, one highest peak per star, 1.2-500 d) is turned into the list
the ladder would have produced when the archive closed (its last spectrum is from 2021 December 29):
significant peaks that pass the a-priori rule, with K < 100 m/s, on stars with no planet known before
2022. A planet counts as known before 2022 if the NASA Exoplanet Archive dates its discovery
publication before 2022 (pscomppars, queried 2026-10-04) or exoplanet.eu dates its discovery before
2022 (full catalogue, queried 2026-10-06). exoplanet.eu counts earlier announcements, such as the
2011 HARPS planets that the NASA archive lists only from their later confirmation. A signal is a
"hit" if the NASA archive lists a planet at the same period published from January 2022 on.
Sensitivity checks: the NASA archive alone (the definition of an earlier version), keeping stars
with earlier planets, and a period window of 1/T instead of 1.5/T.

Also collects the numbers of the prospective test T1 (prereg/), whose rule and data decisions were
committed before the velocities were fitted (see prereg/ and the git history).

Writes timesplit_numbers.json, timesplit_list_2022.csv, fig_timesplit.pdf/.png here and the LaTeX
macros of Sect. 6.5 to ../paper/numbers_forward.tex. Run from this folder in the environment of
../requirements-paper.txt:  python timesplit.py
"""
import json, re
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.ticker
from scipy.stats import hypergeom, norm
from sklearn.metrics import roc_auc_score

b = pd.read_csv("archive_run_2026-09-30/archive_blind_rvvet.csv")
cat = pd.read_csv("nea_xmatch_2026-10-04.txt", sep="|", comment="#", header=None,
                  names=["star", "pl", "host", "P", "K", "yr", "pub", "fac", "meth", "sep"])
cat = cat[(cat.sep < 60) & (cat.P > 0)].drop_duplicates(["star", "pl"])
pre, post = cat[cat.pub < "2022-01"], cat[cat.pub >= "2022-01"]

# exoplanet.eu, full catalogue matched to the 240 stars of the list below (stars without a planet are absent)
eu = {}
for line in open("eu_xmatch_full_2026-10-06.txt"):
    if line.startswith("#"):
        continue
    st, n, rest = [x.strip() for x in line.split("|")]
    pl = [re.fullmatch(r"(.+?) ~ P (\S+) ~ disc (\d+) ~ (\S+)", p.strip()).groups() for p in rest.split(";;")]
    assert len(pl) == int(n), line
    eu[st] = [(name, None if P == "null" else float(P), int(y)) for name, P, y, _ in pl]


def near(f, q, T, w):
    """Same period, a first-order alias or a low harmonic, within w/T."""
    if abs(f - 1 / q) < w / T:
        return True
    for a in (1 / 365.25, 1.0027379, 1 / 29.53):
        if abs(abs(f - 1 / q) - a) < w / T or abs(f + 1 / q - a) < w / T:
            return True
    return any(abs(f - h / q) < w / T for h in (2, 3, 0.5, 1 / 3))


s = b[b.sig & b.rule & (b.K < 100)].copy()
s["nlogfap"] = -s.log10_fap
assert set(eu) <= set(s.star)


def classify(w):
    """Catalogue flags of every signal for a period window of w/T."""
    rows = zip(s.star, s.period, s.baseline)
    c = pd.DataFrame(index=s.index)
    c["known_nea"] = [any(near(1 / P, q, T, w) for q in pre[pre.star == st].P) for st, P, T in rows]
    c["known_eu"] = [any(q is not None and y < 2022 and near(1 / P, q, T, w) for _, q, y in eu.get(st, []))
                     for st, P, T in zip(s.star, s.period, s.baseline)]
    c["host_nea"] = s.star.isin(pre.star).values
    c["host_eu"] = [any(y < 2022 for _, _, y in eu.get(st, [])) for st in s.star]
    c["hit"] = [any(abs(1 / P - 1 / q) < w / T for q in post[post.star == st].P)
                for st, P, T in zip(s.star, s.period, s.baseline)]
    c["known"], c["host"] = c.known_nea | c.known_eu, c.host_nea | c.host_eu
    return c


C, C1 = classify(1.5), classify(1.0)
s = s.join(C)

SCORES = [("p_boosting", "trees"), ("p_logistic", "logistic"), ("nlogfap", "fap"), ("snr_K", "snrK")]


def evaluate(L, hit, seed=1):
    rng = np.random.default_rng(seed)
    y = np.asarray(hit, int)
    r = {"n": int(len(L)), "hits": int(y.sum()), "base_rate": float(y.mean())}
    for col, lab in SCORES:
        sc = L[col].values
        bs = []
        for _ in range(4000):
            i = rng.integers(0, len(y), len(y))
            if 0 < y[i].sum() < len(i):
                bs.append(roc_auc_score(y[i], sc[i]))
        o = np.argsort(-sc, kind="stable")
        r[lab] = dict(auc=float(roc_auc_score(y, sc)), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)),
                      top10=int(y[o][:10].sum()), top20=int(y[o][:20].sum()))
    N, K = len(y), int(y.sum())
    for k in (10, 20):
        r[f"expected_top{k}"] = k * K / N
        r[f"p_hypergeom_trees_top{k}"] = float(hypergeom.sf(r["trees"][f"top{k}"] - 1, N, K, k))
        r[f"p_hypergeom_fap_top{k}"] = float(hypergeom.sf(r["fap"][f"top{k}"] - 1, N, K, k))
    # paired bootstrap of the difference in AUC between the trees and the false-alarm probability
    t, f, d = L.p_boosting.values, L.nlogfap.values, []
    for _ in range(4000):
        i = rng.integers(0, len(y), len(y))
        if 0 < y[i].sum() < len(i):
            d.append(roc_auc_score(y[i], t[i]) - roc_auc_score(y[i], f[i]))
    r["dauc_trees_minus_fap"] = dict(value=r["trees"]["auc"] - r["fap"]["auc"], lo=float(np.percentile(d, 2.5)),
                                     hi=float(np.percentile(d, 97.5)))
    return r


strict = s[~s.known & ~s.host].copy()
loose = s[~s.known].copy()
nea = s[~s.known_nea & ~s.host_nea].copy()
m1 = ~C1.known & ~C1.host
win = s[m1.values].copy()
# hits whose period also agrees within 5 per cent (the 1.5/T window is wide on short baselines)
strict["dP_frac"] = [min(abs(P / q - 1) for q in post[post.star == st].P) if h else np.nan
                     for st, P, h in zip(strict.star, strict.period, strict.hit)]
out = {"stars_run": int(len(b)), "stars_listed": int(len(s)),
       "definition": "known before 2022: NASA archive publication date < 2022-01 or exoplanet.eu discovery year < 2022; "
                     "hit: NASA archive planet published from 2022-01 within 1.5/T",
       "strict": evaluate(strict, strict.hit), "loose": evaluate(loose, loose.hit),
       "nea_only": evaluate(nea, nea.hit), "window_1_over_T": evaluate(win, C1.hit[m1].values),
       "period_within_5pc": evaluate(strict, strict.hit & (strict.dP_frac < 0.05))}

# signals whose status depends on the exoplanet.eu dates
eu_only = s[~s.known_nea & ~s.host_nea & (s.known_eu | s.host_eu)]
out["excluded_by_eu_dates"] = [dict(star=r.star, P=float(r.period), hit_by_nea_dates=bool(r.hit),
                                    eu_planets_before_2022=[f"{n} ({'?' if q is None else f'{q:g} d'}, {y})"
                                                            for n, q, y in eu[r.star] if y < 2022])
                               for _, r in eu_only.iterrows()]

o = np.argsort(-strict.p_boosting.values, kind="stable")
rank = np.empty(len(o), int); rank[o] = np.arange(1, len(o) + 1)
strict["rank_trees"] = rank
transit_star = set(cat[cat.meth == "Transit"].star) | {st for st, v in eu.items() if any(re.match(r"(TOI|K2)-", n) for n, _, _ in v)}
toi_star = set(cat[cat.pl.str.startswith("TOI-")].star) | {st for st, v in eu.items() if any(n.startswith("TOI-") for n, _, _ in v)}
hits = []
for _, r in strict[strict.hit].sort_values("rank_trees").iterrows():
    q = post[post.star == r.star]; q = q.iloc[np.argmin(abs(1 / q.P - 1 / r.period))]
    e = [(n, p, y) for n, p, y in eu.get(r.star, []) if p is not None and abs(1 / p - 1 / q.P) < 1.5 / r.baseline]
    hits.append(dict(star=r.star, P=float(r.period), K=float(r.K), baseline=float(r.baseline), planet=q.pl,
                     P_planet=float(q.P), dP_frac=float(r.dP_frac), pub=q.pub, facility=q.fac, method=q.meth,
                     eu_entry=f"{e[0][0]} ({e[0][2]})" if e else None, rank_trees=int(r.rank_trees),
                     within_1_over_T=bool(abs(1 / r.period - 1 / q.P) < 1 / r.baseline),
                     toi_host=r.star in toi_star, transit_host=r.star in transit_star))
out["hits"] = hits
out["n_hits_toi_host"] = int(sum(h["toi_host"] for h in hits))
out["n_hits_toi_host_trees_top10"] = int(sum(h["toi_host"] for h in hits if h["rank_trees"] <= 10))
out["n_hits_transit_host"] = int(sum(h["transit_host"] for h in hits))
out["n_hits_transit_host_trees_top10"] = int(sum(h["transit_host"] for h in hits if h["rank_trees"] <= 10))

# Prospective test T1 (pre-registered; prereg/)
eph = pd.read_csv("ledger_v1.csv").set_index("star")
t1 = {}
for star, files in (("GJ902", ["result_t1_GJ902.json"]), ("HD58489", ["result_t1_HD58489_masksplit.json", "result_t1_HD58489_literal.json"])):
    res = [json.load(open("prereg/t1_data/" + f)) for f in files]
    t1[star] = dict(results=res)
t1_null = json.load(open("prereg/t1_data/t1_null.json"))
t1_sec = json.load(open("prereg/t1_data/t1_secondary.json"))
# distinct nights (run_test_t1.py averages per instrument per night, so a night with two instruments counts twice there)
distinct_nights = {st: int(np.floor(pd.read_csv(f"prereg/t1_data/{fn}").bjd - 0.2).nunique())
                   for st, fn in (("GJ902", "rv_gj902.csv"), ("HD58489", "rv_hd58489.csv"))}
out["T1"] = dict(results=t1, null=t1_null, secondary=t1_sec, distinct_nights=distinct_nights,
                 trees_score_30sep={st: float(b.set_index("star").p_boosting[st]) for st in ("GJ902", "HD58489")})
json.dump(out, open("timesplit_numbers.json", "w"), indent=1)

cols = ["star", "period", "K", "snr_K", "log10_fap", "p_boosting", "p_logistic", "rank_trees", "hit"]
strict.sort_values("rank_trees")[cols].to_csv("timesplit_list_2022.csv", index=False)

# Figure: cumulative later-published planets against rank
plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.labelsize": 8, "legend.fontsize": 6.5,
                     "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.linewidth": 0.6,
                     "xtick.direction": "in", "ytick.direction": "in"})
fig, ax = plt.subplots(figsize=(3.4, 2.7))
y = strict.hit.values
for col, lab, c, ls in [("p_boosting", "boosted trees", "#c2412d", "-"), ("p_logistic", "logistic regression", "#2457c5", "-"),
                        ("nlogfap", "FAP alone", "0.35", "--")]:
    oo = np.argsort(-strict[col].values, kind="stable")
    ax.step(np.arange(1, len(y) + 1), np.cumsum(y[oo]), where="post", color=c, ls=ls, lw=1.2, label=lab)
ax.plot([0, len(y)], [0, y.sum()], color="0.6", lw=0.8, ls=":", label="random order")
ax.set_xlabel(f"rank in the January 2022 list ({len(y)} signals)")
ax.set_ylabel("published as planets since 2022")
ax.set_xlim(0, len(y)); ax.set_ylim(0, y.sum() + 0.5)
ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
ax.legend(frameon=False, loc="lower right")
fig.tight_layout(); fig.savefig("fig_timesplit.pdf"); fig.savefig("fig_timesplit.png", dpi=160)

# LaTeX macros
S, L, A, W, F = out["strict"], out["loose"], out["nea_only"], out["window_1_over_T"], out["period_within_5pc"]
wide = [h for h in hits if h["dP_frac"] >= 0.05]
# the text says that a window of 1/T changes nothing; stop if that is no longer true
assert all(W[k] == S[k] for k in ("n", "hits")) and all(W[c][t] == S[c][t] for c in ("trees", "logistic", "fap", "snrK")
                                                          for t in ("top10", "top20", "auc")), "1/T window changes the result"
# the text names the stars that the NASA archive alone would keep
assert sorted(e["star"] for e in out["excluded_by_eu_dates"] if e["hit_by_nea_dates"]) == ["CD-415929", "GJ1246", "HD134606", "HD137496"]
gj, hd = t1["GJ902"]["results"][0], t1["HD58489"]["results"]
hd_split, hd_lit = hd[0], hd[1]
nights_gj = {k.replace("only_", ""): v["n"] for k, v in t1_sec["GJ902"].items() if k.startswith("only_")}
def pexp(x):
    m, e = f"{x:.1e}".split("e")
    return rf"{m}\times10^{{{int(e)}}}"
M = {
    "TsStars": out["stars_run"], "TsN": S["n"], "TsHits": S["hits"], "TsBase": f"{100 * S['base_rate']:.0f}",
    "TsTreeTen": S["trees"]["top10"], "TsTreeTwenty": S["trees"]["top20"],
    "TsExpTen": f"{S['expected_top10']:.1f}", "TsExpTwenty": f"{S['expected_top20']:.1f}",
    "TsPTen": pexp(S["p_hypergeom_trees_top10"]), "TsPTwenty": pexp(S["p_hypergeom_trees_top20"]),
    "TsFapTen": S["fap"]["top10"], "TsFapTwenty": S["fap"]["top20"],
    "TsLogTen": S["logistic"]["top10"], "TsLogTwenty": S["logistic"]["top20"],
    "TsAucTree": f"{S['trees']['auc']:.2f}", "TsAucTreeLo": f"{S['trees']['lo']:.2f}", "TsAucTreeHi": f"{S['trees']['hi']:.2f}",
    "TsAucLog": f"{S['logistic']['auc']:.2f}", "TsAucLogLo": f"{S['logistic']['lo']:.2f}", "TsAucLogHi": f"{S['logistic']['hi']:.2f}",
    "TsAucFap": f"{S['fap']['auc']:.2f}", "TsAucFapLo": f"{S['fap']['lo']:.2f}", "TsAucFapHi": f"{S['fap']['hi']:.2f}",
    "TsAucSnr": f"{S['snrK']['auc']:.2f}",
    "TsDauc": f"{S['dauc_trees_minus_fap']['value']:.2f}".replace("-", "$-$"),
    "TsDaucLo": f"{S['dauc_trees_minus_fap']['lo']:.2f}".replace("-", "$-$"),
    "TsDaucHi": f"{S['dauc_trees_minus_fap']['hi']:.2f}".replace("-", "$-$"),
    "TsLooseN": L["n"], "TsLooseHits": L["hits"], "TsLooseTreeTen": L["trees"]["top10"],
    "TsEuOnlyN": len(out["excluded_by_eu_dates"]),
    "TsNeaN": A["n"], "TsNeaHits": A["hits"], "TsNeaTreeTen": A["trees"]["top10"],
    "TsWideN": len(wide), "TsWideMin": f"{100 * min(h['dP_frac'] for h in wide):.0f}",
    "TsWideMax": f"{100 * max(h['dP_frac'] for h in wide):.0f}",
    "TsFiveHits": F["hits"], "TsFiveTreeTen": F["trees"]["top10"], "TsFiveExpTen": f"{F['expected_top10']:.1f}",
    "TsFiveFapTen": F["fap"]["top10"], "TsFivePTen": pexp(F["p_hypergeom_trees_top10"]),
    "TsToi": out["n_hits_toi_host"], "TsToiTopTen": out["n_hits_toi_host_trees_top10"],
    "TsNonToi": S["hits"] - out["n_hits_toi_host"],
    "TaGjP": f"{float(eph.loc['GJ902', 'P']):.2f}", "TaGjK": f"{gj['K_pred']:.2f}", "TaGjsK": f"{float(eph.loc['GJ902', 'sK']):.2f}",
    "TaGjA": f"{gj['A']:.2f}", "TaGjsA": f"{gj['sigma_A']:.2f}", "TaGjNights": distinct_nights["GJ902"], "TaGjVel": gj["n_nights"],
    "TaGjEsp": nights_gj["ESPRESSO"], "TaGjHarps": nights_gj["HARPS"], "TaGjNirps": nights_gj["NIRPS"],
    "TaGjTree": f"{out['T1']['trees_score_30sep']['GJ902']:.2f}",
    "TaHdP": f"{float(eph.loc['HD58489', 'P']):.2f}", "TaHdK": f"{hd_split['K_pred']:.1f}", "TaHdsK": f"{float(eph.loc['HD58489', 'sK']):.1f}",
    "TaHdA": f"{hd_split['A']:.1f}", "TaHdsA": f"{hd_split['sigma_A']:.1f}", "TaHdNights": distinct_nights["HD58489"],
    "TaHdSigma": f"{norm.isf(t1_null['HD58489']['null_P_z_ge_obs']):.1f}",
    "TaHdLitA": f"{hd_lit['A']:.1f}", "TaHdLitsA": f"{hd_lit['sigma_A']:.1f}",
    "TaHdPhase": f"{100 * t1_sec['HD58489']['frac_phases_z_ge_obs']:.0f}",
    "TaHdPer": f"{100 * t1_sec['HD58489']['frac_periods_2_150d_with_higher_chi2']:.0f}",
}
assert hd_split["n_nights"] == distinct_nights["HD58489"]
lines = ["% Written by forward_test/timesplit.py from the files in forward_test/ (do not edit by hand)"]
lines += [r"\newcommand{\nm%s}{%s}" % (k, v) for k, v in M.items()]
open("../paper/numbers_forward.tex", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
print(json.dumps({k: out[k] for k in ("strict", "loose", "nea_only", "window_1_over_T", "excluded_by_eu_dates", "hits",
                                      "n_hits_toi_host", "n_hits_toi_host_trees_top10", "n_hits_transit_host",
                                      "n_hits_transit_host_trees_top10")}, indent=1))
