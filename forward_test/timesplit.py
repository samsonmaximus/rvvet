"""Forward-in-time test of the vetting ladder (Sect. 6.5 of the paper).

The 30 September 2026 blind run of rvvet 0.3.1 on every HARPS-RVBank star with at least 20 nights
over 100 d (archive_run_2026-09-30/, one highest peak per star, 1.2-500 d) is turned into the list
the ladder would have produced when the archive closed in January 2022: significant peaks that pass
the a-priori rule, with K < 100 m/s, on stars with no planet published before 2022. A signal is a
"hit" if a planet at the same period was published from January 2022 on. Planet lists: the NASA
Exoplanet Archive (pscomppars, queried 2026-10-04) and, as a sensitivity check, exoplanet.eu.

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


def near(f, q, T):
    """Same period, a first-order alias or a low harmonic, within 1.5/T."""
    if abs(f - 1 / q) < 1.5 / T:
        return True
    for a in (1 / 365.25, 1.0027379, 1 / 29.53):
        if abs(abs(f - 1 / q) - a) < 1.5 / T or abs(f + 1 / q - a) < 1.5 / T:
            return True
    return any(abs(f - h / q) < 1.5 / T for h in (2, 3, 0.5, 1 / 3))


s = b[b.sig & b.rule & (b.K < 100)].copy()
s["known2022"] = [any(near(1 / P, q, T) for q in pre[pre.star == st].P) for st, P, T in zip(s.star, s.period, s.baseline)]
s["host2022"] = s.star.isin(pre.star)
s["hit"] = [any(abs(1 / P - 1 / q) < 1.5 / T for q in post[post.star == st].P) for st, P, T in zip(s.star, s.period, s.baseline)]
s["nlogfap"] = -s.log10_fap

# exoplanet.eu: planets listed before 2022 at the same period (coordinate match, ledger stars)
eu = {}
for line in open("eu_xmatch_2026-10-04.txt"):
    if line.startswith("#"):
        continue
    st, n, rest = [x.strip() for x in line.split("|")]
    for p in rest.split(";;"):
        m = re.match(r"\s*(.+?) ~ P (\S+) ~ msini \S+ ~ disc (\d+)", p)
        if m and m.group(2) != "null":
            eu.setdefault(st, []).append((m.group(1), float(m.group(2)), int(m.group(3))))
s["eu_known2022"] = [any(near(1 / P, q, T) and y < 2022 for _, q, y in eu.get(st, [])) for st, P, T in zip(s.star, s.period, s.baseline)]

SCORES = [("p_boosting", "trees"), ("p_logistic", "logistic"), ("nlogfap", "fap"), ("snr_K", "snrK")]


def evaluate(L, seed=1):
    rng = np.random.default_rng(seed)
    y = L.hit.values.astype(int)
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
    return r


strict = s[~s.known2022 & ~s.host2022].copy()
loose = s[~s.known2022].copy()
out = {"stars_run": int(len(b)), "strict": evaluate(strict), "loose": evaluate(loose)}
out["strict_excluding_eu_known"] = evaluate(strict[~strict.eu_known2022])
s2 = strict.copy(); s2.loc[s2.eu_known2022, "hit"] = True
out["strict_counting_eu_known_as_hits"] = evaluate(s2)
out["eu_flagged"] = strict[strict.eu_known2022].star.tolist()
# the exoplanet.eu query covered the 116 stars of ledger_v1.csv by coordinates (stars without a listed planet
# do not appear in eu_xmatch); every open signal of the strict list should be one of them
out["eu_query_covers_open_strict_signals"] = float(strict[~strict.hit].star.isin(pd.read_csv("ledger_v1.csv").star).mean())

o = np.argsort(-strict.p_boosting.values, kind="stable")
rank = np.empty(len(o), int); rank[o] = np.arange(1, len(o) + 1)
strict["rank_trees"] = rank
hits = []
for _, r in strict[strict.hit].sort_values("rank_trees").iterrows():
    q = post[post.star == r.star]; q = q.iloc[np.argmin(abs(1 / q.P - 1 / r.period))]
    hits.append(dict(star=r.star, P=float(r.period), K=float(r.K), planet=q.pl, pub=q.pub, facility=q.fac,
                     method=q.meth, rank_trees=int(r.rank_trees), toi_host=bool(q.meth == "Transit" or "TOI" in q.pl)))
out["hits"] = hits
out["n_hits_toi_host"] = int(sum(h["toi_host"] for h in hits))
out["n_hits_toi_host_trees_top10"] = int(sum(h["toi_host"] for h in hits if h["rank_trees"] <= 10))

# Prospective test T1 (pre-registered; prereg/)
eph = pd.read_csv("ledger_v1.csv").set_index("star")
t1 = {}
for star, files in (("GJ902", ["result_t1_GJ902.json"]), ("HD58489", ["result_t1_HD58489_masksplit.json", "result_t1_HD58489_literal.json"])):
    res = [json.load(open("prereg/t1_data/" + f)) for f in files]
    t1[star] = dict(results=res)
t1_null = json.load(open("prereg/t1_data/t1_null.json"))
t1_sec = json.load(open("prereg/t1_data/t1_secondary.json"))
out["T1"] = dict(results=t1, null=t1_null, secondary=t1_sec,
                 trees_score_30sep={st: float(b.set_index("star").p_boosting[st]) for st in ("GJ902", "HD58489")})
json.dump(out, open("timesplit_numbers.json", "w"), indent=1)

cols = ["star", "period", "K", "snr_K", "log10_fap", "p_boosting", "p_logistic", "rank_trees", "host2022", "hit", "eu_known2022"]
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
S, L, X, H = out["strict"], out["loose"], out["strict_excluding_eu_known"], out["strict_counting_eu_known_as_hits"]
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
    "TsLooseN": L["n"], "TsLooseHits": L["hits"], "TsLooseTreeTen": L["trees"]["top10"],
    "TsEuN": len(out["eu_flagged"]), "TsEuExTreeTen": X["trees"]["top10"], "TsEuExAucTree": f"{X['trees']['auc']:.2f}",
    "TsEuHitTreeTen": H["trees"]["top10"], "TsEuHitTreeTwenty": H["trees"]["top20"],
    "TsToi": out["n_hits_toi_host"], "TsToiTopTen": out["n_hits_toi_host_trees_top10"],
    "TaGjP": f"{float(eph.loc['GJ902', 'P']):.2f}", "TaGjK": f"{gj['K_pred']:.2f}", "TaGjsK": f"{float(eph.loc['GJ902', 'sK']):.2f}",
    "TaGjA": f"{gj['A']:.2f}", "TaGjsA": f"{gj['sigma_A']:.2f}", "TaGjNights": gj["n_nights"],
    "TaGjEsp": nights_gj["ESPRESSO"], "TaGjHarps": nights_gj["HARPS"], "TaGjNirps": nights_gj["NIRPS"],
    "TaGjTree": f"{out['T1']['trees_score_30sep']['GJ902']:.2f}",
    "TaHdP": f"{float(eph.loc['HD58489', 'P']):.2f}", "TaHdK": f"{hd_split['K_pred']:.1f}", "TaHdsK": f"{float(eph.loc['HD58489', 'sK']):.1f}",
    "TaHdA": f"{hd_split['A']:.1f}", "TaHdsA": f"{hd_split['sigma_A']:.1f}", "TaHdNights": hd_split["n_nights"],
    "TaHdSigma": f"{norm.isf(t1_null['HD58489']['null_P_z_ge_obs']):.1f}",
    "TaHdLitA": f"{hd_lit['A']:.1f}", "TaHdLitsA": f"{hd_lit['sigma_A']:.1f}",
}
lines = ["% Written by forward_test/timesplit.py from the files in forward_test/ (do not edit by hand)"]
lines += [r"\newcommand{\nm%s}{%s}" % (k, v) for k, v in M.items()]
open("../paper/numbers_forward.tex", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
print(json.dumps({k: out[k] for k in ("strict", "loose", "eu_flagged", "eu_query_covers_open_strict_signals", "n_hits_toi_host", "n_hits_toi_host_trees_top10")}, indent=1))
