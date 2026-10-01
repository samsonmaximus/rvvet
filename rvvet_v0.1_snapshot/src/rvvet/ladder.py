"""The vetting ladder: interpretable statistics of a candidate periodic RV signal.

``vet(series, period=None)`` finds the highest periodogram peak (or evaluates a given
period), and returns a flat dict of features, each answering one question a referee asks
of an archival signal:

* detection   -- how strong is it, and how often does noise do this? (dchi2, log10_fap, top_margin)
* amplitude   -- how large is it compared with the errors and the scatter? (snr_K, K_over_rms)
* period      -- is it a window alias of something else? (alias_margin)
* stationarity-- does it keep amplitude and phase in time? (half_*, block_*, growth_rho, apod_gain)
* activity    -- do the activity indicators vary at this period, and does it sit on a
                 harmonic of the rotation period they reveal? (ind_*, act_*, harm_dist)
"""
from __future__ import annotations

import numpy as np
from scipy.stats import chi2, spearmanr

from .data import INDICATORS, ACTIVITY_PROXIES, Series
from .periodogram import (Frame, alias_frequencies, baluev_fap, fit_jitter, frequency_grid,
                          label_matrix, refine_peak, window_peaks)

# Features used by the classifiers. top_margin is reported but not used: it is >= 0 by
# construction for a blind search and would not transfer to vetting a given period.
FEATURES = ["dchi2", "log10_fap", "snr_K", "K_over_rms", "log_ncyc", "alias_margin",
            "half_phase_z", "half_amp_z", "half_imbalance", "block_phase_p", "block_amp_p",
            "block_phase_rms", "growth_rho", "apod_gain", "ind_max_dchi2", "ind_max_absr",
            "act_log10_fap", "harm_dist", "harm_alias_dist", "log_n"]


def _log10_fap(z, frame, fmin, fmax):
    """log10 of the Baluev bound, computed from tau directly so that it does not underflow."""
    w2 = frame.w ** 2
    t = frame.t
    varw = np.sum(w2 * t ** 2) / w2.sum() - (np.sum(w2 * t) / w2.sum()) ** 2
    W = (fmax - fmin) * np.sqrt(4 * np.pi * varw)
    zz = max(z / 2.0, 1e-12)
    log_tau = np.log(W) - zz + 0.5 * np.log(zz)
    tau = np.exp(log_tau)
    return float(np.log10(-np.expm1(-tau))) if tau > 1e-8 else float(log_tau / np.log(10))


def _true_anomaly(t, P, e, tp):
    M = 2 * np.pi * ((t - tp) / P % 1.0)
    E = M + e * np.sin(M)
    for _ in range(40):
        dE = (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
        E -= dE
        if np.max(np.abs(dE)) < 1e-10:
            break
    return 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))


def prewhiten(series: Series, periods, jitter=None, trend=0, kepler=True, n_iter=3, harmonics=2):
    """Fit and subtract known signals, jointly with per-label offsets and an optional polynomial
    trend of degree ``trend``. With ``kepler=True`` each known period gets a Keplerian orbit
    (eccentricity and periastron time by grid search and refinement; the orbit is linear in
    K cos w and K sin w for fixed e and t_p), fitted by backfitting; otherwise a Fourier series
    with ``harmonics`` terms. Returns the residual Series and the subtracted model."""
    from scipy.optimize import minimize as _minimize
    periods = [float(p) for p in (periods or []) if np.isfinite(p) and p > 0]
    if not periods and trend == 0:
        return series, np.zeros(series.n)
    t = series.t
    tc = (t - t.mean()) / max(series.baseline, 1.0)
    Tr = np.array([tc ** d for d in range(1, trend + 1)]).T if trend > 0 else np.zeros((series.n, 0))
    four = []
    for P in periods:
        for h in range(1, harmonics + 1):
            four += [np.cos(2 * np.pi * h * t / P), np.sin(2 * np.pi * h * t / P)]
    X0 = np.hstack([Tr, np.array(four).T]) if four else Tr
    if jitter is None:
        jitter, _ = fit_jitter(series.t, series.y, series.e, series.label, design=X0 if X0.shape[1] else None)
    fr = Frame(series.t, series.e, series.label, jitter)
    yp = fr.project(series.y)
    if not kepler or not periods:
        coef = np.linalg.lstsq(fr.project(X0), yp, rcond=None)[0]
        model = X0 @ coef
        return series.with_y(series.y - model), model
    comps = {P: np.zeros(series.n) for P in periods}
    trend_model = np.zeros(series.n)
    nT = Tr.shape[1]

    def fit_one(r, P, e, tp):
        """Keplerian at fixed (P, e, tp) fitted jointly with the trend and the offsets."""
        nu = _true_anomaly(t, P, e, tp)
        B = np.hstack([np.c_[np.cos(nu), np.sin(nu)], Tr])
        Bp = fr.project(B)
        rp = fr.project(r)
        c = np.linalg.lstsq(Bp, rp, rcond=None)[0]
        res = rp - Bp @ c
        return float(res @ res), B[:, :2] @ c[:2], (Tr @ c[2:] if nT else np.zeros(series.n))

    for it in range(n_iter):
        for P in periods:
            r = series.y - sum(v for k, v in comps.items() if k != P)
            best = (np.inf, None, None)
            for e in (0.0, 0.1, 0.2, 0.3, 0.45, 0.6, 0.75, 0.9):
                for tp in np.linspace(0, P, 24, endpoint=False) + t[0]:
                    chi = fit_one(r, P, e, tp)[0]
                    if chi < best[0]:
                        best = (chi, e, tp)
            obj = lambda x: fit_one(r, P, float(np.clip(x[0], 0, 0.95)), x[1])[0]
            sol = _minimize(obj, [best[1], best[2]], method="Nelder-Mead",
                            options=dict(xatol=1e-4, fatol=1e-6, maxiter=400))
            _, comps[P], trend_model = fit_one(r, P, float(np.clip(sol.x[0], 0, 0.95)), sol.x[1])
    model = trend_model + sum(comps.values())
    return series.with_y(series.y - model), model


def _std_indicator(v, label):
    """Remove per-label medians and scale an indicator to unit robust spread; NaN kept."""
    v = np.array(v, float)
    for l in np.unique(label):
        m = (label == l) & np.isfinite(v)
        if m.sum():
            v[label == l] -= np.median(v[m])
    ok = np.isfinite(v)
    if ok.sum() < 5:
        return v
    mad = 1.4826 * np.median(np.abs(v[ok] - np.median(v[ok])))
    return v / (mad if mad > 0 else (np.std(v[ok]) or 1.0))


def _indicator_frame(series, v):
    """Frame for a standardised indicator. Indicators carry no usable errors, so the per-label
    maximum-likelihood jitter with offsets only is the per-label standard deviation (closed form)."""
    ok = np.isfinite(v)
    if ok.sum() < max(15, 0.6 * series.n):
        return None, None
    sub = series.subset(ok)
    vv = v[ok]
    e = np.full(sub.n, 1e-3)
    jit = np.array([max(np.std(vv[sub.label == l]), 1e-3) for l in range(sub.nlab)])
    return Frame(sub.t, e, sub.label, jit), vv


def indicator_frames(series):
    """Standardised indicators and their frames, computed once per series."""
    out = {}
    for k in INDICATORS:
        if k in series.ind:
            v = _std_indicator(series.ind[k], series.label)
            fr, vv = _indicator_frame(series, v)
            if fr is not None:
                out[k] = (v, fr, vv)
    return out


def activity_period(series: Series, pmin=8.0, pmax=150.0, oversample=4.0, frames=None):
    """Rotation proxy: highest peak over pmin-pmax among the activity indicators.
    Returns (period, dchi2, log10_fap, indicator name) or NaNs."""
    frames = indicator_frames(series) if frames is None else frames
    best = (np.nan, 0.0, 0.0, "")
    f = frequency_grid(series.baseline, pmin, pmax, oversample)
    for k in ACTIVITY_PROXIES:
        if k not in frames:
            continue
        _, fr, vv = frames[k]
        z = fr.dchi2(f, vv)
        i = int(np.argmax(z))
        lf = _log10_fap(float(z[i]), fr, f[0], f[-1])
        if lf < best[2]:
            best = (float(1 / f[i]), float(z[i]), lf, k)
    return best


def harmonic_distances(f0, pact, lfact, T, window=()):
    """Distance (resolution elements) from f0 to the nearest rotation harmonic k*f_rot, k = 1-4
    (harm_dist), and to the nearest first-order alias of one (harm_alias_dist: day, synodic
    month, year and the star's spectral-window peaks). NaN when no rotation proxy is detected
    (log10 FAP of the proxy >= -2)."""
    if not (np.isfinite(pact) and lfact < -2):
        return np.nan, np.nan
    fr = 1.0 / pact
    harm = [k * fr for k in range(1, 5)]
    d1 = min(abs(f0 - h) * T for h in harm)
    als = []
    for h in harm:
        als += list(alias_frequencies(h)) + [abs(h + s * q) for q, _ in window for s in (+1, -1)]
    d2 = min(abs(f0 - a) * T for a in als) if als else np.nan
    return float(d1), float(d2)


def vet(series: Series, period: float | None = None, band=(1.2, 500.0), oversample=3.0,
        known_periods=(), trend=0, n_blocks=4, want_periodogram=False) -> dict:
    """Run the ladder. If ``period`` is None the highest peak over ``band`` is vetted.
    ``known_periods`` (other planets in the system, fitted as Keplerians) and a polynomial
    trend of degree ``trend`` are fitted and removed first."""
    if known_periods or trend:
        series, _ = prewhiten(series, list(known_periods), trend=trend)
    T = series.baseline
    jit, _ = fit_jitter(series.t, series.y, series.e, series.label)
    fr = Frame(series.t, series.e, series.label, jit)
    freqs = frequency_grid(T, band[0], band[1], oversample)
    z = fr.dchi2(freqs, series.y)
    ktop = int(np.argmax(z))
    if period is None:
        f0, z0 = refine_peak(fr, series.y, freqs[ktop], T)
    else:
        f0, z0 = refine_peak(fr, series.y, 1.0 / period, T, halfwidth=0.25)
    out = dict(star=series.star, n=series.n, baseline=T, period=1.0 / f0, dchi2=z0,
               log10_fap=_log10_fap(z0, fr, freqs[0], freqs[-1]),
               log_n=float(np.log10(series.n)), log_ncyc=float(np.log10(T * f0)))
    far = np.abs(freqs - f0) > 1.5 / T
    out["top_margin"] = float(z0 - z[far].max()) if far.any() else np.nan
    out["top_period"] = float(1.0 / freqs[ktop])

    # amplitude
    L = label_matrix(series.label)
    yres = series.y - L @ np.linalg.lstsq(L * fr.w[:, None], series.y * fr.w, rcond=None)[0]
    fit = fr.fit_sinusoid(f0, series.y)
    out.update(K=fit["K"], sK=fit["sK"], snr_K=fit["K"] / fit["sK"])
    out["K_over_rms"] = fit["K"] / float(np.sqrt(np.mean(yres ** 2)))

    # aliases: the standard day/month/year aliases and the three strongest peaks of this
    # star's spectral window
    wp = window_peaks(series.t, baseline=T)
    cands = list(alias_frequencies(f0)) + [abs(f0 + s * q) for q, _ in wp for s in (+1, -1)]
    cands = [fa for fa in cands if 1.0 / band[1] <= fa <= 1.0 / 0.5 and abs(fa - f0) > 1.5 / T]
    za = [refine_peak(fr, series.y, fa, T, halfwidth=0.5, n=21)[1] for fa in cands]
    out["window_peaks"] = ";".join(f"{q:.5f}" for q, _ in wp)
    out["alias_margin"] = float(z0 - max(za)) if za else np.nan

    # stationarity: halves (equal counts), blocks, growth, apodisation
    tref = fr.t_ref
    def sub_fit(mask):
        sub = series.subset(mask)
        if sub.n < 8:
            return None
        frs = Frame(sub.t, sub.e, sub.label, jit[np.unique(series.label[mask])], t_ref=tref)
        try:
            return frs.fit_sinusoid(f0, sub.y), sub.n
        except np.linalg.LinAlgError:
            return None
    order = np.argsort(series.t)
    half = np.zeros(series.n, bool); half[order[: series.n // 2]] = True
    h1, h2 = sub_fit(half), sub_fit(~half)
    if h1 and h2:
        (f1, n1), (f2, n2) = h1, h2
        dph = (f1["phase_deg"] - f2["phase_deg"] + 180) % 360 - 180
        out["half_phase_z"] = abs(dph) / np.hypot(f1["sphase_deg"], f2["sphase_deg"])
        out["half_amp_z"] = abs(f1["K"] - f2["K"]) / np.hypot(f1["sK"], f2["sK"])
        d1, d2 = max(f1["dchi2"], 0), max(f2["dchi2"], 0)
        out["half_imbalance"] = abs(d1 / (d1 + d2 + 1e-12) - n1 / (n1 + n2))
    else:
        out.update(half_phase_z=np.nan, half_amp_z=np.nan, half_imbalance=np.nan)

    edges = np.array_split(order, n_blocks)
    rows = []
    for idx in edges:
        m = np.zeros(series.n, bool); m[idx] = True
        r = sub_fit(m)
        if r and np.isfinite(r[0]["sphase_deg"]) and r[0]["sphase_deg"] < 120:
            rows.append(r[0])
    if len(rows) >= 3:
        dph = np.array([(r["phase_deg"] - fit["phase_deg"] + 180) % 360 - 180 for r in rows])
        sph = np.array([r["sphase_deg"] for r in rows])
        Ks = np.array([r["K"] for r in rows]); sKs = np.array([r["sK"] for r in rows])
        out["block_phase_p"] = float(chi2.sf(np.sum((dph / sph) ** 2), len(rows)))
        out["block_amp_p"] = float(chi2.sf(np.sum(((Ks - fit["K"]) / sKs) ** 2), len(rows)))
        out["block_phase_rms"] = float(np.sqrt(np.mean(dph ** 2)))
    else:
        out.update(block_phase_p=np.nan, block_amp_p=np.nan, block_phase_rms=np.nan)

    ns = np.unique(np.linspace(max(10, series.n // 5), series.n, 15).astype(int))
    g = []
    for n in ns:
        m = np.zeros(series.n, bool); m[order[:n]] = True
        r = sub_fit(m)
        g.append(r[0]["dchi2"] if r else np.nan)
    g = np.array(g)
    ok = np.isfinite(g)
    out["growth_rho"] = float(spearmanr(ns[ok], g[ok]).correlation) if ok.sum() >= 5 else np.nan

    t0, t1 = series.t.min(), series.t.max()
    best = fit["dchi2"]
    for ta in np.linspace(t0, t1, 7):
        for tau in T * np.array([0.1, 0.2, 0.35, 0.5]):
            env = np.exp(-0.5 * ((series.t - ta) / tau) ** 2)
            if env.sum() < 3:
                continue
            try:
                best = max(best, fr.fit_sinusoid(f0, series.y, envelope=env)["dchi2"])
            except np.linalg.LinAlgError:
                pass
    out["apod_gain"] = float(best - fit["dchi2"])

    # activity indicators at f0, and correlation with the RVs
    dmax, rmax, which = 0.0, 0.0, ""
    frames = indicator_frames(series)
    for k, (v, fri, vv) in frames.items():
        zi = refine_peak(fri, vv, f0, T, halfwidth=0.5, n=11)[1]
        if zi > dmax:
            dmax, which = zi, k
        ok = np.isfinite(v)
        r = np.corrcoef(yres[ok], v[ok])[0, 1]
        rmax = max(rmax, abs(r))
    out.update(ind_max_dchi2=float(dmax), ind_argmax=which, ind_max_absr=float(rmax))

    pact, zact, lfact, kact = activity_period(series, frames=frames)
    out.update(act_period=pact, act_dchi2=zact, act_log10_fap=lfact, act_indicator=kact)
    out["harm_dist"], out["harm_alias_dist"] = harmonic_distances(f0, pact, lfact, T, wp)
    if want_periodogram:
        out["_freqs"], out["_z"] = freqs, z
    return out
