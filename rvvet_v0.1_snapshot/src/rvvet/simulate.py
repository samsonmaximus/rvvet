"""Simulated signals injected into real archival sampling and noise.

Noise: the star's own nightly RVs and indicators with one shared permutation within each
instrument label, so the joint RV-indicator noise distribution, the errors and the
sampling are real while any coherent signal is destroyed.

Planets: Keplerian orbits.

Activity: the FF' picture (Aigrain et al. 2012; Rajpaul et al. 2015). A latent process
G(t) with a quasi-periodic kernel and its time derivative G'(t) are drawn jointly at the
epochs; RV = a1 G + a2 G', line width and chromospheric indices = b G, bisector = c G'.
"""
from __future__ import annotations

import numpy as np

from .data import Series


# ---------------------------------------------------------------------------------- noise
def permuted_noise(series: Series, rng) -> Series:
    """Real residuals with one permutation per label shared by the RVs and indicators; the
    per-label median is removed from each series so no offset signal survives."""
    idx = np.arange(series.n)
    for l in np.unique(series.label):
        m = np.where(series.label == l)[0]
        idx[m] = rng.permutation(m)
    y = series.y[idx].copy()
    ind = {k: v[idx].copy() for k, v in series.ind.items()}
    e = series.e[idx].copy()
    for l in np.unique(series.label):
        m = series.label == l
        y[m] -= np.median(y[m])
    return Series(series.star, series.t.copy(), y, e, series.label.copy(), series.labels, ind, dict(series.meta))


# ---------------------------------------------------------------------------------- planets
def kepler_rv(t, P, K, e=0.0, omega=0.0, tp=0.0):
    """Radial velocity of a Keplerian orbit (m/s)."""
    M = 2 * np.pi * (np.asarray(t) - tp) / P
    E = M.copy()
    for _ in range(50):                                   # Newton iterations
        dE = (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
        E -= dE
        if np.max(np.abs(dE)) < 1e-10:
            break
    nu = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))
    return K * (np.cos(nu + omega) + e * np.cos(omega))


# ---------------------------------------------------------------------------------- activity
def qp_joint_cov(t, P, lam, w):
    """Joint covariance of [G, G'] at times t for k(u) = exp(-u^2/2lam^2 - sin^2(pi u/P)/2w^2)."""
    u = t[:, None] - t[None, :]
    k = np.exp(-u ** 2 / (2 * lam ** 2) - np.sin(np.pi * u / P) ** 2 / (2 * w ** 2))
    g = -u / lam ** 2 - np.pi / (2 * w ** 2 * P) * np.sin(2 * np.pi * u / P)
    gp = -1 / lam ** 2 - np.pi ** 2 / (w ** 2 * P ** 2) * np.cos(2 * np.pi * u / P)
    kp = k * g                     # dk/du
    kpp = k * (g * g + gp)         # d2k/du2
    n = len(t)
    C = np.empty((2 * n, 2 * n))
    C[:n, :n] = k
    C[:n, n:] = -kp                # cov(G(t_i), G'(t_j)) = d/dt_j k(t_i - t_j)
    C[n:, :n] = kp                 # = -cov(G(t_j), G'(t_i)) transposed
    C[n:, n:] = -kpp               # cov(G'(t_i), G'(t_j))
    return C


def draw_activity(t, P, lam, w, rng, jitter=1e-6):
    """One joint realisation of (G, G') at times t, each scaled to unit rms."""
    C = qp_joint_cov(t, P, lam, w)
    C[np.diag_indices_from(C)] += jitter * np.diag(C).mean()
    try:
        Lc = np.linalg.cholesky(C)
    except np.linalg.LinAlgError:
        vals, vecs = np.linalg.eigh(C)
        Lc = vecs * np.sqrt(np.clip(vals, 0, None))
    x = Lc @ rng.normal(size=2 * len(t))
    G, Gp = x[: len(t)], x[len(t):]
    return G / (G.std() or 1), Gp / (Gp.std() or 1)


def inject_activity(series: Series, rng, P, lam, w, rv_rms, frac_flux, ind_snr):
    """Add activity to RVs and indicators. RV = rv_rms * [sqrt(1-f^2) G + f G'] (f = frac_flux,
    the share of the flux, G', term); each indicator gets its activity term at amplitude
    ind_snr times its own robust scatter, with the sign fixed per indicator."""
    G, Gp = draw_activity(series.t, P, lam, w, rng)
    y = series.y + rv_rms * (np.sqrt(1 - frac_flux ** 2) * G + frac_flux * Gp)
    ind = {}
    for k, v in series.ind.items():
        ok = np.isfinite(v)
        scale = 1.4826 * np.median(np.abs(v[ok] - np.median(v[ok]))) if ok.sum() > 5 else 0.0
        comp = Gp if k == "bis" else G                     # bisector follows G', the others G
        sign = -1.0 if k in ("contrast", "bis") else 1.0
        ind[k] = v + sign * ind_snr * scale * comp
    out = series.with_y(y)
    out.ind = ind
    return out
