"""Loading, quality cuts and nightly binning of HARPS-RVBank time series.

A :class:`Series` is the unit every other module works on: nightly-binned radial
velocities of one star, an integer instrument label per epoch (one per fibre era by
default), and the activity indicators binned the same way.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

FIBRE_UPGRADE_BJD = 2457170.0          # HARPS fibre change, 2015 June (Lo Curto et al. 2015)
INDICATORS = ("dlw", "halpha", "fwhm", "bis", "contrast", "crx", "nad1", "rhk")
ACTIVITY_PROXIES = ("dlw", "halpha", "fwhm", "rhk")   # used to estimate a rotation period


@dataclass
class Series:
    """Nightly-binned RV time series of one star."""

    star: str
    t: np.ndarray                      # BJD (TDB)
    y: np.ndarray                      # RV (m/s)
    e: np.ndarray                      # RV uncertainty (m/s)
    label: np.ndarray                  # integer label per epoch, 0..nlab-1
    labels: tuple = ("pre", "post")
    ind: dict = field(default_factory=dict)      # indicator -> values (NaN where missing)
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        o = np.argsort(self.t)
        self.t, self.y, self.e, self.label = (np.asarray(a, float)[o] if k < 3 else np.asarray(a, int)[o]
                                              for k, a in enumerate((self.t, self.y, self.e, self.label)))
        self.ind = {k: np.asarray(v, float)[o] for k, v in self.ind.items()}

    @property
    def n(self) -> int:
        return len(self.t)

    @property
    def baseline(self) -> float:
        return float(self.t[-1] - self.t[0])

    @property
    def nlab(self) -> int:
        return int(self.label.max()) + 1

    def subset(self, mask) -> "Series":
        """Return the epochs selected by a boolean mask, relabelled so labels stay contiguous."""
        mask = np.asarray(mask, bool)
        lab = self.label[mask]
        present = np.unique(lab)
        remap = {old: new for new, old in enumerate(present)}
        return Series(self.star, self.t[mask], self.y[mask], self.e[mask],
                      np.array([remap[v] for v in lab], int),
                      tuple(self.labels[i] for i in present),
                      {k: v[mask] for k, v in self.ind.items()}, dict(self.meta))

    def with_y(self, y) -> "Series":
        s = Series(self.star, self.t.copy(), np.asarray(y, float).copy(), self.e.copy(), self.label.copy(),
                   self.labels, {k: v.copy() for k, v in self.ind.items()}, dict(self.meta))
        return s


def load_rvbank(path: str) -> pd.DataFrame:
    """Read the parquet file written by ``scripts/load_rvbank.py`` (full HARPS-RVBank table)."""
    return pd.read_parquet(path)


def quality_mask(df: pd.DataFrame, snr_min: float = 10.0, drift_max: float = 3.0, emax: float = 20.0) -> np.ndarray:
    """Instrumental cuts that do not depend on model residuals (cf. criteria C1, C3, C4 of the
    HD 297396 b paper): RVBank flag 0, S/N >= 10 in order 55 (the paper used 20 for a K dwarf;
    10 keeps the red-dominated spectra of M dwarfs), |drift| <= 3 m/s, finite RV and error."""
    m = np.isfinite(df.rv.values) & np.isfinite(df.e.values) & (df.e.values > 0) & (df.e.values < emax)
    if "flag" in df:
        m &= (df.flag.fillna(0).values == 0)
    if "snr" in df:
        m &= ~(df.snr.values < snr_min)
    if "drift" in df:
        m &= ~(np.abs(df.drift.values) > drift_max)
    return m


def bin_nightly(df: pd.DataFrame, star: str = "", rv: str = "rv", err: str = "e",
                split_bjd: float = FIBRE_UPGRADE_BJD) -> Series:
    """Weighted nightly means within each fibre era; indicators averaged with the same weights."""
    d = df.copy()
    d["lab"] = (d.bjd.values > split_bjd).astype(int)
    d["night"] = np.floor(d.bjd.values - 0.5).astype(int)      # La Silla: noon-to-noon
    d["w"] = 1.0 / d[err].values ** 2
    rows = []
    for (night, lab), g in d.groupby(["night", "lab"], sort=True):
        w = g.w.values
        r = dict(t=np.sum(w * g.bjd.values) / w.sum(), y=np.sum(w * g[rv].values) / w.sum(),
                 e=1.0 / np.sqrt(w.sum()), lab=lab)
        for k in INDICATORS:
            if k in g:
                v = g[k].values.astype(float)
                ok = np.isfinite(v)
                r[k] = np.sum(w[ok] * v[ok]) / w[ok].sum() if ok.any() else np.nan
        rows.append(r)
    b = pd.DataFrame(rows).sort_values("t")
    present = sorted(b.lab.unique())
    remap = {v: i for i, v in enumerate(present)}
    names = tuple(("pre", "post")[v] for v in present)
    ind = {k: b[k].values for k in INDICATORS if k in b}
    return Series(star, b.t.values, b.y.values, b.e.values, b.lab.map(remap).values, names, ind,
                  dict(n_spectra=int(len(d))))


def gross_outliers(s: Series, clip_sigma: float = 15.0) -> np.ndarray:
    """Epochs more than ``clip_sigma`` robust standard deviations from a quadratic fitted to
    each label (two passes). Meant only for gross errors (misidentified spectra), not for
    discrepant nights: 15 sigma keeps, e.g., the 9.5-sigma night of HD 297396."""
    bad = np.zeros(s.n, bool)
    for l in range(s.nlab):
        m = np.where(s.label == l)[0]
        if len(m) < 8:
            continue
        keep = np.ones(len(m), bool)
        x = (s.t[m] - s.t[m].mean()) / max(np.ptp(s.t[m]), 1.0)
        for _ in range(2):
            c = np.polyfit(x[keep], s.y[m][keep], 2 if keep.sum() > 10 else 0)
            r = s.y[m] - np.polyval(c, x)
            mad = 1.4826 * np.median(np.abs(r[keep] - np.median(r[keep])))
            keep = np.abs(r - np.median(r[keep])) <= clip_sigma * max(mad, 1e-6)
        bad[m[~keep]] = True
    return bad


def load_star(df: pd.DataFrame, star: str, clip_sigma: float | None = None, **kw) -> Series:
    """Quality-cut and nightly-bin one star of the RVBank table; optionally drop gross outliers."""
    g = df[df.star == star]
    g = g[quality_mask(g, **kw)]
    if len(g) == 0:
        raise ValueError(f"no usable spectra for {star}")
    s = bin_nightly(g, star)
    if clip_sigma:
        bad = gross_outliers(s, clip_sigma)
        s = s.subset(~bad)
        s.meta["n_clipped"] = int(bad.sum())
    return s
