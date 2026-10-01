"""Benchmark and completeness figures from saved outputs (results/benchmark_scored.csv, sims)."""
import glob, os
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..", "..")
plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.labelsize": 8, "legend.fontsize": 6.5,
                     "xtick.labelsize": 7, "ytick.labelsize": 7, "axes.linewidth": 0.6, "xtick.direction": "in",
                     "ytick.direction": "in", "xtick.top": True, "savefig.dpi": 300, "savefig.bbox": "tight"})
b = pd.read_csv(os.path.join(ROOT, "results", "benchmark_scored.csv"))
order = {"REFUTED": 0, "UPHELD_HARPS": 1, "UPHELD_INDEPENDENT": 2, "DISPUTED": 3}
colors = {"REFUTED": "#c0392b", "UPHELD_HARPS": "#1baf7a", "UPHELD_INDEPENDENT": "#2a78d6", "DISPUTED": "#8a8a85"}
bs = b.assign(o=b.label.map(order)).sort_values(["o", "p_boosting"], ascending=[False, True]).reset_index(drop=True)
fig, ax = plt.subplots(figsize=(3.4, 5.6))
for i, r in bs.iterrows():
    c = colors[r.label]
    ax.plot(r.p_boosting, i, "o", mfc=c if r.detected else "white", mec=c, ms=4, mew=0.9)
    if not r.rule and r.detected:
        ax.plot(r.p_boosting, i, "x", color="k", ms=3, mew=0.8)
for k in range(1, len(bs)):
    if bs.o[k] != bs.o[k - 1]:
        ax.axhline(k - 0.5, color="#ddd", lw=0.6)
ax.set_yticks(range(len(bs)))
ax.set_yticklabels([s.replace(" (40 d; Pepe+2011)", " (40 d)").replace(" (13.97 d; Tuomi+2013)", "").replace(" (HET, 10.24 d)", " (10.2 d)")
                    for s in bs.signal], fontsize=5.5)
ax.axvline(0.5, color="#bbb", lw=0.6); ax.set_xlim(-0.03, 1.03); ax.set_ylim(-0.7, len(bs) - 0.3)
ax.set_xlabel("P(planet) from boosted trees trained on simulations")
h = [Line2D([], [], marker="o", ls="", color=colors[k], label=k.replace("_", " ").lower()) for k in
     ("UPHELD_INDEPENDENT", "UPHELD_HARPS", "REFUTED", "DISPUTED")]
h += [Line2D([], [], marker="o", ls="", mfc="white", mec="k", label="not detected (FAP > 1%)"),
      Line2D([], [], marker="x", ls="", color="k", label="detected, fails the a-priori rule")]
ax.legend(handles=h, frameon=True, framealpha=0.95, edgecolor="#ddd", loc="center left", bbox_to_anchor=(0.01, 0.42), fontsize=5.5)
fig.savefig(os.path.join(ROOT, "figures", "fig_benchmark.pdf")); plt.close(fig)

d = pd.concat([pd.read_parquet(p) for p in sorted(glob.glob(os.path.join(ROOT, "sims", "chunk_*.parquet")))])
pl = d[d.cls == "planet"].copy()
pl["rec"] = (pl.truth == 1) & (pl.log10_fap < -2)
edges = np.array([3, 4, 5, 6, 7, 8.5, 10, 12, 14, 17, 20])
pl["b"] = pd.cut(pl.snr_target, edges)
g = pl.groupby("b", observed=True).rec.agg(["mean", "size"])
x = np.sqrt(edges[:-1] * edges[1:])
fig, ax = plt.subplots(figsize=(3.4, 2.3))
ax.errorbar(x, g["mean"], yerr=np.sqrt(g["mean"] * (1 - g["mean"]) / g["size"]), fmt="o-", ms=3, lw=0.9, color="#2a78d6", capsize=0)
ax.set_xscale("log"); ax.set_xticks([3, 5, 7, 10, 14, 20]); ax.set_xticklabels(["3", "5", "7", "10", "14", "20"])
ax.minorticks_off(); ax.set_ylim(0, 1.02)
ax.set_xlabel(r"injected $K/\sigma_K$ (expected, $\sigma_K=\sigma\sqrt{2/N}$)"); ax.set_ylabel("recovered at the right period")
fig.savefig(os.path.join(ROOT, "figures", "fig_completeness.pdf")); plt.close(fig)
print(g)
