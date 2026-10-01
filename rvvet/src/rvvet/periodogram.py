"""Maximum-likelihood periodogram with one offset and one jitter per instrument label.

The statistic is the chi-square improvement of adding a sinusoid at frequency f to a
model of per-label offsets, with the per-label jitters held fixed. (``ladder.detect`` finds the
candidate with the planet-free jitters, then rescales them with the sinusoid in the model and
uses the likelihood ratio as its detection statistic.)

    Delta chi^2(f) = chi^2(offsets) - chi^2(offsets + a cos 2 pi f t + b sin 2 pi f t).

Offsets are removed by projecting the whitened basis onto the complement of the whitened
label indicators, which costs O(N * n_labels) per frequency instead of O(N^2).
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize

SIDEREAL_DAY = 0.99726957
YEAR = 365.25
SYNODIC_MONTH = 29.530589


def label_matrix(label: np.ndarray, nlab: int | None = None) -> np.ndarray:
    nlab = int(label.max()) + 1 if nlab is None else nlab
    return (label[:, None] == np.arange(nlab)[None, :]).astype(float)


def fit_jitter(t, y, e, label, design=None, bounds=(-5.0, 7.0)):
    """Maximum-likelihood per-label jitters (m/s) with per-label offsets and an optional
    linear design (columns) profiled out. Returns (jitters, -lnL)."""
    L = label_matrix(label)
    X = L if design is None else np.hstack([L, design])
    nlab = L.shape[1]

    def nll(lj):
        s2 = e ** 2 + np.exp(lj)[label] ** 2
        w = 1.0 / s2
        A = X.T @ (X * w[:, None])
        p = np.linalg.solve(A, X.T @ (w * y))
        r = y - X @ p
        return 0.5 * np.sum(r * r * w + np.log(s2))

    # start from the per-label excess scatter, then refine
    x0 = np.empty(nlab)
    for l in range(nlab):
        m = label == l
        ex = np.var(y[m]) - np.mean(e[m] ** 2) if m.sum() > 1 else 0.0
        x0[l] = np.clip(0.5 * np.log(max(ex, 1e-4)), bounds[0], bounds[1])
    best = minimize(nll, x0, method="L-BFGS-B", bounds=[bounds] * nlab)
    alt = minimize(nll, np.full(nlab, 0.5), method="L-BFGS-B", bounds=[bounds] * nlab)
    if alt.fun < best.fun:
        best = alt
    return np.exp(best.x), float(best.fun)


def fit_jitter_scale(t, y, e, label, jitter0, design=None, bounds=(-4.0, 2.0)):
    """Rescale fixed per-label jitters by one common factor s, fitted by maximum likelihood with
    per-label offsets and a linear design profiled out: sigma_i^2 = e_i^2 + (s * jitter0_l)^2.
    Used to re-estimate the jitter with a candidate sinusoid in the model. One shared factor
    cannot collapse the jitter of a label with few epochs onto a sinusoid that happens to fit
    them, which per-label refitting can. Returns (s * jitter0, s, -lnL), with -lnL defined as in
    ``fit_jitter`` (so that 2 * (nll_0 - nll_1) is a likelihood ratio)."""
    L = label_matrix(label, len(jitter0))
    X = L if design is None else np.hstack([L, design])
    X = X[:, np.abs(X).sum(0) > 0]
    j0 = np.asarray(jitter0, float)[label]

    def nll(ls):
        s2 = e ** 2 + (np.exp(ls) * j0) ** 2
        w = 1.0 / s2
        A = X.T @ (X * w[:, None])
        p = np.linalg.solve(A, X.T @ (w * y))
        r = y - X @ p
        return 0.5 * np.sum(r * r * w + np.log(s2))

    from scipy.optimize import minimize_scalar
    res = minimize_scalar(nll, bounds=bounds, method="bounded", options=dict(xatol=1e-4))
    sc = float(np.exp(res.x))
    return np.asarray(jitter0, float) * sc, sc, float(res.fun)


class Frame:
    """Whitening and offset projection for fixed per-label jitters.

    ``Frame(t, e, label, jitter)`` precomputes the weights and an orthonormal basis Q of the
    whitened label indicators; ``project(X)`` returns (I - Q Q^T) diag(w) X. Phases are
    measured from ``t_ref`` (default: the mean time), so frames built on subsets of one series
    must share ``t_ref`` for their phases to be comparable.
    """

    def __init__(self, t, e, label, jitter, t_ref=None):
        self.t = np.asarray(t, float)
        self.t_ref = float(self.t.mean()) if t_ref is None else float(t_ref)
        self.tc = self.t - self.t_ref
        self.label = np.asarray(label, int)
        self.jitter = np.asarray(jitter, float)
        self.s = np.sqrt(np.asarray(e, float) ** 2 + self.jitter[self.label] ** 2)
        self.w = 1.0 / self.s
        L = label_matrix(self.label, len(self.jitter))
        L = L[:, L.sum(0) > 0]
        self.Q, _ = np.linalg.qr(L * self.w[:, None])

    def project(self, X):
        Xw = X * (self.w[:, None] if X.ndim == 2 else self.w)
        return Xw - self.Q @ (self.Q.T @ Xw)

    def dchi2(self, freqs, Y, chunk=4000):
        """Delta chi^2 at each frequency; Y is (N,) or (N, M). Returns (F,) or (F, M)."""
        freqs = np.atleast_1d(np.asarray(freqs, float))
        yp = self.project(np.asarray(Y, float))
        out = []
        for i in range(0, len(freqs), chunk):
            f = freqs[i:i + chunk]
            ph = 2 * np.pi * np.outer(self.tc, f)
            C = self.project(np.cos(ph))
            S = self.project(np.sin(ph))
            cc = np.einsum("ij,ij->j", C, C)
            ss = np.einsum("ij,ij->j", S, S)
            cs = np.einsum("ij,ij->j", C, S)
            det = cc * ss - cs * cs
            a = C.T @ yp
            b = S.T @ yp
            if yp.ndim == 1:
                z = (ss * a * a - 2 * cs * a * b + cc * b * b) / det
            else:
                z = (ss[:, None] * a * a - 2 * cs[:, None] * a * b + cc[:, None] * b * b) / det[:, None]
            out.append(z)
        return np.concatenate(out)

    def fit_sinusoid(self, f, y, envelope=None):
        """Least-squares sinusoid (times an optional envelope) at frequency f with per-label
        offsets. Returns dict(K, sK, phase_deg, sphase_deg, a, b, cov, dchi2)."""
        ph = 2 * np.pi * f * self.tc
        X = np.c_[np.cos(ph), np.sin(ph)]
        if envelope is not None:
            X = X * envelope[:, None]
        Xp = self.project(X)
        yp = self.project(np.asarray(y, float))
        F = Xp.T @ Xp
        cov = np.linalg.inv(F)
        a, b = cov @ (Xp.T @ yp)
        K = float(np.hypot(a, b))
        J = np.array([a, b]) / max(K, 1e-12)
        sK = float(np.sqrt(J @ cov @ J))
        Jp = np.array([-b, a]) / max(K, 1e-12) ** 2
        sph = float(np.degrees(np.sqrt(Jp @ cov @ Jp)))
        return dict(K=K, sK=sK, phase_deg=float(np.degrees(np.arctan2(b, a))), sphase_deg=sph,
                    a=float(a), b=float(b), cov=cov, dchi2=float(np.array([a, b]) @ F @ np.array([a, b])))


def frequency_grid(baseline, pmin=1.2, pmax=500.0, oversample=3.0):
    """Uniform frequency grid from 1/pmax to 1/pmin with `oversample` points per 1/baseline."""
    return np.arange(1.0 / pmax, 1.0 / pmin, 1.0 / (oversample * baseline))


def refine_peak(frame, y, f0, baseline, halfwidth=0.5, n=41, fmin=0.0, fmax=np.inf):
    """Maximise Delta chi^2 on a fine grid within +-halfwidth/baseline of f0, restricted to
    [fmin, fmax] (the search band) when given."""
    g = f0 + np.linspace(-halfwidth, halfwidth, n) / baseline
    g = g[(g > 0) & (g >= fmin) & (g <= fmax)]
    if len(g) == 0:
        g = np.array([min(max(f0, fmin), fmax)])
    z = frame.dchi2(g, y)
    k = int(np.argmax(z))
    return float(g[k]), float(z[k])


def baluev_fap(z, frame, fmin, fmax):
    """Baluev (2008) approximation to the global false-alarm probability of a Delta chi^2 peak z
    over [fmin, fmax] for known noise variances (two sinusoid parameters):
    FAP = 1 - (1 - P1) exp(-tau), P1 = exp(-z/2) (single frequency), tau = W e^{-z/2} sqrt(z/2),
    W = (fmax - fmin) sqrt(4 pi Var_w(t)) with Var_w the weighted variance of the epochs. It is
    an upper bound in the small-FAP limit."""
    w2 = frame.w ** 2
    t = frame.t
    varw = np.sum(w2 * t ** 2) / w2.sum() - (np.sum(w2 * t) / w2.sum()) ** 2
    W = (fmax - fmin) * np.sqrt(4 * np.pi * varw)
    zz = np.asarray(z, float) / 2.0
    tau = W * np.exp(-zz) * np.sqrt(np.maximum(zz, 0))
    p1 = np.exp(-np.maximum(zz, 0))
    return 1.0 - (1.0 - p1) * np.exp(-tau)


def alias_frequencies(f):
    """Aliases of f through the sidereal day, the synodic month and the year (first order)."""
    out = []
    for D in (SIDEREAL_DAY, SYNODIC_MONTH, YEAR):
        for s in (+1, -1):
            fa = abs(f + s / D)
            if fa > 0:
                out.append(fa)
    return np.array(out)


_WINDOW_CACHE = {}


def window_peaks(t, weights=None, fmax=1.1, n_peaks=3, baseline=None):
    """Frequencies of the strongest peaks of the spectral window |sum w exp(2 pi i f t)|^2 / (sum w)^2
    over (1.5/T, fmax], one per resolution element. These are the sampling-specific alias offsets.
    Unweighted windows (weights=None) are cached per set of epochs."""
    t = np.asarray(t, float)
    key = None
    if weights is None:
        key = (t.tobytes(), fmax, n_peaks, baseline)
        if key in _WINDOW_CACHE:
            return _WINDOW_CACHE[key]
    w = np.ones_like(t) if weights is None else np.asarray(weights, float)
    T = baseline or (t.max() - t.min())
    f = np.arange(1.5 / T, fmax, 1.0 / (5 * T))
    tc = t - t.mean()
    W = np.zeros(len(f))
    for i in range(0, len(f), 20000):
        ph = 2 * np.pi * np.outer(tc, f[i:i + 20000])
        W[i:i + 20000] = ((w @ np.cos(ph)) ** 2 + (w @ np.sin(ph)) ** 2) / w.sum() ** 2
    peaks = []
    order = np.argsort(W)[::-1]
    for k in order:
        if all(abs(f[k] - q) > 1.5 / T for q, _ in peaks):
            peaks.append((float(f[k]), float(W[k])))
        if len(peaks) >= n_peaks:
            break
    if key is not None:
        if len(_WINDOW_CACHE) > 2000:
            _WINDOW_CACHE.clear()
        _WINDOW_CACHE[key] = peaks
    return peaks
