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
from .periodogram import (Frame, alias_frequencies, baluev_fap, fit_jitter, fit_jitter_scale,
                          frequency_grid, label_matrix, refine_peak, window_peaks)

# Features used by the classifiers. top_margin is reported but not used: it is >= 0 by
# construction for a blind search and would not transfer to vetting a given period. log_n and
# log_ncyc are computed and reported but not used either: in simulations their power to separate
# planets from impostors comes from the injection priors (how amplitudes scale with N, and the
# period distributions of planets and rotation), not from the physics of the signal.
FEATURES = ["dchi2", "log10_fap", "snr_K", "K_over_rms", "alias_margin",
            "half_phase_z", "half_amp_z", "half_imbalance", "block_phase_p", "block_amp_p",
            "block_phase_rms", "growth_rho", "apod_gain", "ind_max_dchi2", "ind_max_absr",
            "act_log10_fap", "harm_dist", "harm_alias_dist"]
PRIOR_DEPENDENT = ["log_n", "log_ncyc"]
ROTATION_BAND = (2.5, 200.0)       # search band of the rotation proxy (d)


def _log10_fap(z, frame, fmin, fmax):
    """log10 of the Baluev (2008) approximation 1 - (1 - P1) exp(-tau) (see
    ``periodogram.baluev_fap``), computed in logs so that it does not underflow."""
    w2 = frame.w ** 2
    t = frame.t
    varw = np.sum(w2 * t ** 2) / w2.sum() - (np.sum(w2 * t) / w2.sum()) ** 2
    W = (fmax - fmin) * np.sqrt(4 * np.pi * varw)
    zz = max(z / 2.0, 1e-12)
    log_tau = np.log(W) - zz + 0.5 * np.log(zz)
    log_p1 = -zz
    if max(log_tau, log_p1) > np.log(1e-8):
        tau, p1 = np.exp(log_tau), np.exp(log_p1)
        return float(np.log10(-np.expm1(-tau) + p1 * np.exp(-tau)))
    return float(np.logaddexp(log_tau, log_p1) / np.log(10))


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


INDICATOR_CLIP = 15.0          # robust sigma; the same gross-outlier level as for the velocities


def _std_indicator(v, label, t=None, trend=0, clip=INDICATOR_CLIP):
    """Remove per-label offsets (and, with ``trend`` > 0, a polynomial trend in time fitted jointly
    with them, as for the velocities) and scale to unit robust spread. Values more than ``clip``
    robust standard deviations from the fit are set to NaN and the fit is repeated without them
    (indicators have heavy tails, and a least-squares trend tilted by one gross outlier leaves a
    spurious long-period signal). Without a trend the per-label medians are removed."""
    v = np.array(v, float)
    fin = np.isfinite(v)
    labs = np.unique(label[fin]) if fin.any() else np.array([], int)

    def model(mask):
        m = np.zeros_like(v)
        if trend and t is not None and mask.sum() > len(labs) + trend + 3:
            tc = (t - t.mean()) / max(np.ptp(t), 1.0)
            X = np.hstack([(label[:, None] == labs[None, :]).astype(float),
                           np.array([tc ** d for d in range(1, trend + 1)]).T])
            coef = np.linalg.lstsq(X[mask], v[mask], rcond=None)[0]
            return X @ coef
        for l in labs:
            ml = mask & (label == l)
            if ml.sum():
                m[label == l] = np.median(v[ml])
        return m

    mask = fin.copy()
    r = v.copy()
    for _ in range(3):
        if mask.sum() < 5:
            break
        r = v - model(mask)
        med = np.median(r[mask])
        sc = 1.4826 * np.median(np.abs(r[mask] - med))
        if not sc > 0:
            break
        new = fin & (np.abs(r - med) <= clip * sc)
        if np.array_equal(new, mask):
            break
        mask = new
    out = np.where(mask, r, np.nan)
    ok = np.isfinite(out)
    if ok.sum() < 5:
        return out
    mad = 1.4826 * np.median(np.abs(out[ok] - np.median(out[ok])))
    return out / (mad if mad > 0 else (np.std(out[ok]) or 1.0))


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


def indicator_frames(series, trend=0):
    """Standardised (and, with ``trend``, detrended) indicators and their frames, computed once
    per series."""
    out = {}
    for k in INDICATORS:
        if k in series.ind:
            v = _std_indicator(series.ind[k], series.label, series.t, trend)
            fr, vv = _indicator_frame(series, v)
            if fr is not None:
                out[k] = (v, fr, vv)
    return out


def activity_period(series: Series, pmin=ROTATION_BAND[0], pmax=ROTATION_BAND[1], oversample=4.0,
                    frames=None):
    """Rotation proxy: the most significant local maximum over pmin-pmax among the activity
    indicators of ACTIVITY_PROXIES, excluding frequencies within 1/T of one and two cycles per
    year (seasonal sampling puts spurious power there) and peaks at the edges of the band. Its
    log10 FAP is the Baluev value over the band multiplied by the number of indicators searched
    (Bonferroni). Returns (period, dchi2, log10_fap, indicator) or (NaN, 0, 0, "")."""
    from .periodogram import YEAR
    frames = indicator_frames(series) if frames is None else frames
    avail = [k for k in ACTIVITY_PROXIES if k in frames]
    best = (np.nan, 0.0, 0.0, "")
    if not avail:
        return best
    T = series.baseline
    f = frequency_grid(T, pmin, pmax, oversample)
    allowed = (np.abs(f - 1.0 / YEAR) > 1.0 / T) & (np.abs(f - 2.0 / YEAR) > 1.0 / T)
    for k in avail:
        _, fr, vv = frames[k]
        z = fr.dchi2(f, vv)
        peak = np.zeros(len(z), bool)
        peak[1:-1] = (z[1:-1] >= z[:-2]) & (z[1:-1] >= z[2:])
        cand = np.where(peak & allowed)[0]
        if len(cand) == 0:
            continue
        i = int(cand[np.argmax(z[cand])])
        lf = min(0.0, _log10_fap(float(z[i]), fr, f[0], f[-1]) + np.log10(len(avail)))
        if lf < best[2]:
            best = (float(1 / f[i]), float(z[i]), lf, k)
    return best


def harmonic_distances(f0, pact, lfact, T, window=()):
    """Distance (resolution elements, 1/T) from f0 to the nearest rotation harmonic k*f_rot,
    k = 1-4 (harm_dist), and to the nearest first-order alias of one (harm_alias_dist: sidereal
    day, synodic month, year and the star's spectral-window peaks). NaN when no rotation proxy
    is detected (log10 FAP of the proxy >= -2)."""
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


def _sinusoid_design(t, f):
    ph = 2 * np.pi * f * (t - t.mean())
    return np.c_[np.cos(ph), np.sin(ph)]


def _homogeneity(fits):
    """Test that sub-samples share one sinusoid. Each fit gives (a, b) with covariance C. With mu
    the generalised-least-squares mean of the (a, b), the deviations are split into the
    direction of mu (amplitude) and across it (phase); each sum of squared, standardised
    deviations is ~chi^2 with len(fits) - 1 degrees of freedom for a constant sinusoid.
    Returns (chi2_phase, chi2_amp, dof, phase deviations in degrees)."""
    V = np.array([[f["a"], f["b"]] for f in fits])
    C = [f["cov"] for f in fits]
    Ci = [np.linalg.inv(c) for c in C]
    mu = np.linalg.solve(sum(Ci), sum(ci @ v for ci, v in zip(Ci, V)))
    amp = float(np.hypot(*mu))
    u = mu / max(amp, 1e-12)
    tv = np.array([-u[1], u[0]])
    dev = V - mu
    rad, tan = dev @ u, dev @ tv
    var_r = np.array([u @ c @ u for c in C])
    var_t = np.array([tv @ c @ tv for c in C])
    dph = np.degrees(np.arctan2(tan, amp + rad))
    return float(np.sum(tan ** 2 / var_t)), float(np.sum(rad ** 2 / var_r)), len(fits) - 1, dph


def _block_dofs(nb):
    """Degrees of freedom of the block tests (phase, amplitude): nb - 1 each, the deviations
    being measured about their generalised-least-squares mean. The frequency is also fitted
    to the same data, which removes part of a linear phase trend; nb - 2 for the phase test
    was tried first and was anti-conservative on simulated planets, nb - 1 close to nominal
    (the paper, Sect. 5.4, gives both), so nb - 1 is used for both."""
    return nb - 1, nb - 1


def detect(series: Series, period: float | None = None, band=(1.2, 500.0), oversample=3.0, window=0.5):
    """Detection step of the ladder (see ``vet``). For a given ``period`` the candidate is the
    highest point within +-``window``/T of 1/period (``window`` = 0: the period itself). Returns
    a dict with the candidate frequency f0, the likelihood-ratio statistic z0 (jitter scale
    profiled), Delta chi^2 in the H1 frame (zf0) and in the H0 frame at f0 (z_h0), the H0 and H1
    jitters and frames, the periodogram z in the H1 frame, the grid, and log10 FAPs from both
    statistics."""
    T = series.baseline
    t, y = series.t, series.y
    freqs = frequency_grid(T, band[0], band[1], oversample)
    flo, fhi = 1.0 / band[1], 1.0 / band[0]
    jit0, nll0 = fit_jitter(t, y, series.e, series.label)
    fr0 = Frame(t, series.e, series.label, jit0)
    if period is None:
        fc = float(freqs[int(np.argmax(fr0.dchi2(freqs, y)))])
        wlo, whi, hw = flo, fhi, 0.5
    else:
        fc = 1.0 / period
        wlo, whi, hw = max(flo, fc - window / T), min(fhi, fc + window / T), window
    if hw > 0:
        fc, _ = refine_peak(fr0, y, fc, T, halfwidth=hw, n=41, fmin=wlo, fmax=whi)
    jit, _, _ = fit_jitter_scale(t, y, series.e, series.label, jit0, design=_sinusoid_design(t, fc))
    if hw > 0:
        f0, _ = refine_peak(Frame(t, series.e, series.label, jit), y, fc, T, halfwidth=0.1, n=21, fmin=wlo, fmax=whi)
    else:
        f0 = fc
    jit, jscale, nll1 = fit_jitter_scale(t, y, series.e, series.label, jit0, design=_sinusoid_design(t, f0))
    fr = Frame(t, series.e, series.label, jit)
    z = fr.dchi2(freqs, y)
    zf0 = float(fr.dchi2([f0], y)[0])
    z_h0 = float(fr0.dchi2([f0], y)[0])
    z0 = float(max(2.0 * (nll0 - nll1), 0.0))
    return dict(f0=f0, z0=z0, zf0=zf0, z_h0=z_h0, jit0=jit0, jit=jit, jscale=jscale, fr0=fr0, fr=fr, z=z,
                freqs=freqs, flo=flo, fhi=fhi,
                log10_fap=_log10_fap(z0, fr, freqs[0], freqs[-1]),
                log10_fap_h0=_log10_fap(z_h0, fr0, freqs[0], freqs[-1]))


def vet(series: Series, period: float | None = None, band=(1.2, 500.0), oversample=3.0,
        known_periods=(), trend=0, n_blocks=4, want_periodogram=False, period_window=0.5) -> dict:
    """Run the ladder. If ``period`` is None the highest peak over ``band`` is vetted; otherwise
    the highest point within ``period_window``/T (default 0.5/T, half a resolution element) of
    the given period; ``period_window`` = 0 evaluates the period itself.
    ``known_periods`` (other planets in the system, fitted as Keplerians) and a polynomial trend
    of degree ``trend`` are fitted and removed first.

    Indicators are detrended with the same polynomial degree ``trend`` as the velocities.

    Jitter and detection statistic: the per-label jitters are fitted with offsets only (H0), and
    the candidate is the highest peak of the periodogram with these jitters (or the highest point
    within 0.5/T of the given period). All jitters are then rescaled by one common factor fitted
    with a sinusoid at the candidate in the model (H1), so that a real signal is not absorbed
    into the jitter. ``dchi2`` is the likelihood ratio 2 (ln L1 - ln L0) with the jitter scale
    profiled; every other statistic uses the H1 jitters (``dchi2_frame`` is Delta chi^2 in that
    frame, the reference for the alias comparison)."""
    if known_periods or trend:
        series, _ = prewhiten(series, list(known_periods), trend=trend)
    T = series.baseline
    t, y = series.t, series.y
    D = detect(series, period, band, oversample, window=period_window)
    f0, z0, zf0, jit, jscale, fr, z, freqs = D["f0"], D["z0"], D["zf0"], D["jit"], D["jscale"], D["fr"], D["z"], D["freqs"]
    flo, fhi, jit0 = D["flo"], D["fhi"], D["jit0"]
    offset = float((f0 - 1.0 / period) * T) if period is not None else np.nan
    at_edge = bool(period is not None and period_window > 0 and abs(offset) > 0.98 * period_window)
    ktop = int(np.argmax(z))
    out = dict(star=series.star, n=series.n, baseline=T, period=1.0 / f0, dchi2=z0, dchi2_frame=zf0,
               log10_fap=D["log10_fap"], log10_fap_h0=D["log10_fap_h0"], dchi2_h0=D["z_h0"],
               log10_p_single=float(-z0 / 2.0 / np.log(10)),
               log_n=float(np.log10(series.n)), log_ncyc=float(np.log10(T * f0)),
               period_at_window_edge=at_edge, period_offset=offset,
               jitter_h0_rms=float(np.sqrt(np.mean(jit0 ** 2))), jitter_scale=float(jscale))
    far = np.abs(freqs - f0) > 1.5 / T
    out["top_margin"] = float(zf0 - z[far].max()) if far.any() else np.nan
    out["top_period"] = float(1.0 / freqs[ktop])

    # amplitude
    L = label_matrix(series.label)
    yres = y - L @ np.linalg.lstsq(L * fr.w[:, None], y * fr.w, rcond=None)[0]
    fit = fr.fit_sinusoid(f0, y)
    out.update(K=fit["K"], sK=fit["sK"], snr_K=fit["K"] / fit["sK"])
    out["K_over_rms"] = fit["K"] / float(np.sqrt(np.mean(yres ** 2)))

    # period: the day/month/year aliases and the three strongest peaks of this star's spectral
    # window, kept only inside the search band; each is refined within +-0.5/T (inside the band)
    # and dropped if it refines to within 1.5/T of f0 (i.e. onto the candidate's own peak)
    wp = window_peaks(t, baseline=T)
    cands = list(alias_frequencies(f0)) + [abs(f0 + sg * q) for q, _ in wp for sg in (+1, -1)]
    za, fa_best = [], np.nan
    for fa in cands:
        if not (flo <= fa <= fhi) or abs(fa - f0) <= 1.5 / T:
            continue
        fr_a, zr = refine_peak(fr, y, fa, T, halfwidth=0.5, n=21, fmin=flo, fmax=fhi)
        if abs(fr_a - f0) > 1.5 / T:
            za.append(zr)
            if zr >= max(za):
                fa_best = fr_a
    out["window_peaks"] = ";".join(f"{q:.5f}" for q, _ in wp)
    out["alias_margin"] = float(zf0 - max(za)) if za else np.nan
    out["alias_period"] = float(1.0 / fa_best) if np.isfinite(fa_best) else np.nan

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
    order = np.argsort(t)
    half = np.zeros(series.n, bool); half[order[: series.n // 2]] = True
    h1, h2 = sub_fit(half), sub_fit(~half)
    if h1 and h2:
        (f1, n1), (f2, n2) = h1, h2
        cph, camp, _, _ = _homogeneity([f1, f2])
        out["half_phase_z"] = float(np.sqrt(cph))
        out["half_amp_z"] = float(np.sqrt(camp))
        d1, d2 = max(f1["dchi2"], 0), max(f2["dchi2"], 0)
        out["half_imbalance"] = abs(d1 / (d1 + d2 + 1e-12) - n1 / (n1 + n2))
    else:
        out.update(half_phase_z=np.nan, half_amp_z=np.nan, half_imbalance=np.nan)

    rows = []
    for idx in np.array_split(order, n_blocks):          # equal numbers of epochs
        m = np.zeros(series.n, bool); m[idx] = True
        r = sub_fit(m)
        if r:
            rows.append(r[0])
    if len(rows) >= 3:
        cph, camp, _, dph = _homogeneity(rows)
        dof_ph, dof_amp = _block_dofs(len(rows))
        out["block_phase_p"] = float(chi2.sf(cph, dof_ph))
        out["block_amp_p"] = float(chi2.sf(camp, dof_amp))
        out["block_phase_chi2"], out["block_amp_chi2"], out["n_blocks_used"] = cph, camp, len(rows)
        out["block_phase_rms"] = float(np.sqrt(np.mean(dph ** 2)))
    else:
        out.update(block_phase_p=np.nan, block_amp_p=np.nan, block_phase_rms=np.nan, n_blocks_used=len(rows))

    ns = np.unique(np.linspace(max(10, series.n // 5), series.n, 15).astype(int))
    g = []
    for n in ns:
        m = np.zeros(series.n, bool); m[order[:n]] = True
        r = sub_fit(m)
        g.append(r[0]["dchi2"] if r else np.nan)
    g = np.array(g)
    ok = np.isfinite(g)
    out["growth_rho"] = float(spearmanr(ns[ok], g[ok]).correlation) if ok.sum() >= 5 else np.nan

    t0, t1 = t.min(), t.max()
    best = fit["dchi2"]
    for ta in np.linspace(t0, t1, 7):
        for tau in T * np.array([0.1, 0.2, 0.35, 0.5]):
            env = np.exp(-0.5 * ((t - ta) / tau) ** 2)
            if env.sum() < 3:
                continue
            try:
                best = max(best, fr.fit_sinusoid(f0, y, envelope=env)["dchi2"])
            except np.linalg.LinAlgError:
                pass
    out["apod_gain"] = float(best - fit["dchi2"])

    # activity indicators: the largest Delta chi^2 of any indicator within +-0.5/T of f0, and the
    # largest |correlation| of an indicator with the RVs
    dmax, rmax, which = 0.0, 0.0, ""
    frames = indicator_frames(series, trend=trend)
    for k, (v, fri, vv) in frames.items():
        zi = refine_peak(fri, vv, f0, T, halfwidth=0.5, n=11)[1]
        if zi > dmax:
            dmax, which = zi, k
        ok = np.isfinite(v)
        r = np.corrcoef(yres[ok], v[ok])[0, 1]
        rmax = max(rmax, abs(r))
    out.update(ind_max_dchi2=float(dmax), ind_argmax=which, ind_max_absr=float(rmax), n_indicators=len(frames))

    pact, zact, lfact, kact = activity_period(series, frames=frames)
    out.update(act_period=pact, act_dchi2=zact, act_log10_fap=lfact, act_indicator=kact)
    out["harm_dist"], out["harm_alias_dist"] = harmonic_distances(f0, pact, lfact, T, wp)
    if want_periodogram:
        out["_freqs"], out["_z"] = freqs, z
    return out
