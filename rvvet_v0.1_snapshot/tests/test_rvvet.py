import numpy as np
import pandas as pd
import pytest

import rvvet
from rvvet.data import Series, bin_nightly, quality_mask
from rvvet.periodogram import (Frame, alias_frequencies, baluev_fap, fit_jitter, frequency_grid, label_matrix,
                               refine_peak, window_peaks)
from rvvet.ladder import _log10_fap, prewhiten, vet
from rvvet.simulate import draw_activity, inject_activity, kepler_rv, permuted_noise, qp_joint_cov
from rvvet.learn import design, grouped_cv_predict, grouped_bootstrap_auc, metrics, models


def make_series(n=120, T=3000.0, seed=0, sigma=2.0, signal=None, jitter=0.0, offsets=(0.0, 0.0), ind=True):
    rng = np.random.default_rng(seed)
    t = np.sort(rng.uniform(0, T, n)) + 2455000.0
    label = (t > t[n // 2]).astype(int)
    e = np.full(n, sigma)
    y = rng.normal(0, np.sqrt(sigma ** 2 + jitter ** 2), n) + np.array(offsets)[label]
    if signal is not None:
        y = y + signal(t)
    inds = {}
    if ind:
        for k in ("dlw", "halpha", "fwhm", "bis"):
            inds[k] = rng.normal(0, 1, n)
    return Series("TEST", t, y, e, label, ("pre", "post"), inds)


# ------------------------------------------------------------------ periodogram core
def test_projection_matches_dense():
    s = make_series()
    fr = Frame(s.t, s.e, s.label, np.array([1.0, 2.0]))
    X = np.random.default_rng(1).normal(size=(s.n, 3))
    W = np.diag(fr.w)
    L = label_matrix(s.label) * fr.w[:, None]
    P = np.eye(s.n) - L @ np.linalg.pinv(L)
    assert np.allclose(fr.project(X), P @ W @ X, atol=1e-10)


def test_dchi2_matches_direct_least_squares():
    s = make_series(signal=lambda t: 3 * np.sin(2 * np.pi * t / 7.3))
    jit = np.array([0.5, 1.5])
    fr = Frame(s.t, s.e, s.label, jit)
    sig = np.sqrt(s.e ** 2 + jit[s.label] ** 2)
    for f in (1 / 7.3, 1 / 33.0, 1 / 2.1):
        L = label_matrix(s.label)
        tc = s.t - s.t.mean()
        X1 = np.hstack([L, np.c_[np.cos(2 * np.pi * f * tc), np.sin(2 * np.pi * f * tc)]])
        chi = lambda X: np.sum(((s.y - X @ np.linalg.lstsq(X / sig[:, None], s.y / sig, rcond=None)[0]) / sig) ** 2)
        assert fr.dchi2([f], s.y)[0] == pytest.approx(chi(L) - chi(X1), rel=1e-8)


def test_offsets_do_not_change_periodogram():
    a = make_series(seed=3)
    b = a.with_y(a.y + np.array([40.0, -25.0])[a.label])
    fr = Frame(a.t, a.e, a.label, np.array([1.0, 1.0]))
    f = frequency_grid(a.baseline, 1.5, 200)
    assert np.allclose(fr.dchi2(f, a.y), fr.dchi2(f, b.y))


def test_batch_equals_loop():
    s = make_series(seed=4)
    fr = Frame(s.t, s.e, s.label, np.array([1.0, 1.0]))
    Y = np.random.default_rng(0).normal(size=(s.n, 5))
    f = frequency_grid(s.baseline, 2, 100)
    zb = fr.dchi2(f, Y)
    for j in range(5):
        assert np.allclose(zb[:, j], fr.dchi2(f, Y[:, j]))


def test_recovers_injected_period_and_amplitude():
    P, K = 7.3, 4.0
    s = make_series(n=150, signal=lambda t: K * np.sin(2 * np.pi * t / P), seed=5)
    r = vet(s)
    assert abs(1 / r["period"] - 1 / P) < 1 / s.baseline
    assert abs(r["K"] - K) < 3 * r["sK"]
    assert r["log10_fap"] < -5


def test_fit_jitter_recovers_extra_noise():
    s = make_series(n=400, sigma=1.0, jitter=3.0, seed=6)
    jit, _ = fit_jitter(s.t, s.y, s.e, s.label)
    assert np.all(np.abs(jit - 3.0) < 0.6)


def test_baluev_fap_is_conservative_on_noise():
    rng = np.random.default_rng(7)
    faps = []
    for k in range(150):
        s = make_series(n=60, seed=100 + k, ind=False)
        fr = Frame(s.t, s.e, s.label, np.zeros(2))
        f = frequency_grid(s.baseline, 1.2, 500)
        z = fr.dchi2(f, s.y).max()
        faps.append(baluev_fap(z, fr, f[0], f[-1]))
    faps = np.array(faps)
    # an upper bound: at most as many false alarms as nominal, within binomial scatter
    assert np.mean(faps < 0.1) <= 0.1 + 3 * np.sqrt(0.1 * 0.9 / len(faps))


def test_log10_fap_does_not_underflow():
    s = make_series()
    fr = Frame(s.t, s.e, s.label, np.zeros(2))
    assert np.isfinite(_log10_fap(5000.0, fr, 0.001, 0.8))
    assert _log10_fap(5000.0, fr, 0.001, 0.8) < -500


def test_alias_frequencies():
    fa = alias_frequencies(0.2)
    assert np.any(np.isclose(fa, 0.2 + 1 / 0.99726957))
    assert np.any(np.isclose(fa, abs(0.2 - 1 / 365.25)))


def test_window_peaks_find_daily_alias():
    rng = np.random.default_rng(8)
    t = 2455000 + np.sort(rng.integers(0, 2000, 200) + rng.normal(0, 0.03, 200))   # nightly sampling
    peaks = window_peaks(t)
    assert any(abs(q - 1 / 0.99726957) < 0.01 or abs(q - 1.0) < 0.01 for q, _ in peaks)


def test_refine_peak_improves_on_grid():
    s = make_series(signal=lambda t: 5 * np.sin(2 * np.pi * t / 11.11), seed=9)
    fr = Frame(s.t, s.e, s.label, np.zeros(2))
    f = frequency_grid(s.baseline, 2, 100, oversample=1.0)
    k = np.argmax(fr.dchi2(f, s.y))
    f1, z1 = refine_peak(fr, s.y, f[k], s.baseline)
    assert z1 >= fr.dchi2([f[k]], s.y)[0]


# ------------------------------------------------------------------ data handling
def test_nightly_binning_weighted_mean():
    df = pd.DataFrame(dict(bjd=[2456000.6, 2456000.7, 2456001.6], rv=[1.0, 3.0, 5.0], e=[1.0, 1.0, 2.0],
                           dlw=[1.0, 1.0, 2.0]))
    s = bin_nightly(df, "X")
    assert s.n == 2
    assert s.y[0] == pytest.approx(2.0)
    assert s.e[0] == pytest.approx(1 / np.sqrt(2))


def test_fibre_labels():
    df = pd.DataFrame(dict(bjd=[2457000.6, 2457300.6], rv=[0.0, 0.0], e=[1.0, 1.0]))
    s = bin_nightly(df, "X")
    assert list(s.label) == [0, 1] and s.labels == ("pre", "post")


def test_quality_mask():
    df = pd.DataFrame(dict(rv=[1, 1, 1, np.nan], e=[1, 1, 1, 1], flag=[0, 64, 0, 0], snr=[50, 50, 5, 50],
                           drift=[0, 0, 0, 0]))
    assert list(quality_mask(df)) == [True, False, False, False]


def test_subset_relabels():
    s = make_series()
    sub = s.subset(s.label == 1)
    assert sub.nlab == 1 and set(sub.label) == {0} and sub.labels == ("post",)


# ------------------------------------------------------------------ ladder behaviour
def test_prewhiten_removes_known_signal():
    s = make_series(signal=lambda t: 8 * np.sin(2 * np.pi * t / 5.5), seed=10)
    r, _ = prewhiten(s, [5.5])
    fr = Frame(r.t, r.e, r.label, np.zeros(2))
    before, after = fr.dchi2([1 / 5.5], s.y)[0], fr.dchi2([1 / 5.5], r.y)[0]
    assert after < 1e-3 * before


def test_stationary_versus_transient_signal():
    stat = make_series(n=160, T=4000, signal=lambda t: 5 * np.sin(2 * np.pi * t / 9.1), seed=11)
    t0 = 2455000.0
    trans = make_series(n=160, T=4000, seed=11,
                        signal=lambda t: 10 * np.sin(2 * np.pi * t / 9.1) * np.exp(-0.5 * ((t - t0 - 600) / 250) ** 2))
    a, b = vet(stat, period=9.1), vet(trans, period=9.1)
    assert a["apod_gain"] < b["apod_gain"]
    assert a["half_imbalance"] < b["half_imbalance"]


def test_given_period_is_used():
    s = make_series(signal=lambda t: 5 * np.sin(2 * np.pi * t / 9.1), seed=12)
    r = vet(s, period=9.1)
    assert abs(r["period"] - 9.1) < 0.05


def test_activity_signal_sits_on_rotation_harmonic():
    rng = np.random.default_rng(13)
    s = make_series(n=200, T=3000, seed=13)
    # long-lived spots (lambda = 40 rotations) give a coherent signal at the rotation period or a harmonic
    s = inject_activity(s, rng, P=25.0, lam=1000.0, w=0.8, rv_rms=6.0, frac_flux=0.3, ind_snr=3.0)
    r = vet(s)
    assert np.isfinite(r["harm_dist"]) and r["harm_dist"] < 3
    assert r["ind_max_dchi2"] > 10


# ------------------------------------------------------------------ simulation
def test_kepler_circular_is_sinusoid():
    t = np.linspace(0, 20, 200)
    assert np.allclose(kepler_rv(t, 5.0, 3.0, 0.0, 0.0, 0.0), 3 * np.cos(2 * np.pi * t / 5.0))


def test_qp_derivative_covariance_matches_finite_difference():
    t = np.array([0.0, 3.0, 10.0])
    h = 1e-4
    P, lam, w = 20.0, 60.0, 0.6
    k = lambda u: np.exp(-u ** 2 / (2 * lam ** 2) - np.sin(np.pi * u / P) ** 2 / (2 * w ** 2))
    C = qp_joint_cov(t, P, lam, w)
    for i in range(3):
        for j in range(3):
            num = (k(t[i] - (t[j] + h)) - k(t[i] - (t[j] - h))) / (2 * h)       # d/dt_j cov(G_i, G_j)
            assert C[i, 3 + j] == pytest.approx(num, abs=1e-6)
            num2 = (k((t[i] + h) - (t[j] + h)) - k((t[i] + h) - (t[j] - h)) - k((t[i] - h) - (t[j] + h))
                    + k((t[i] - h) - (t[j] - h))) / (4 * h * h)
            assert C[3 + i, 3 + j] == pytest.approx(num2, abs=1e-4)


def test_permuted_noise_preserves_values_within_labels():
    s = make_series(offsets=(10.0, -5.0))
    p = permuted_noise(s, np.random.default_rng(0))
    for l in (0, 1):
        a = np.sort(s.y[s.label == l] - np.median(s.y[s.label == l]))
        b = np.sort(p.y[p.label == l])
        assert np.allclose(a, b)


def test_simulation_is_deterministic():
    s = make_series()
    a = draw_activity(s.t, 20.0, 60.0, 0.5, np.random.default_rng(42))
    b = draw_activity(s.t, 20.0, 60.0, 0.5, np.random.default_rng(42))
    assert np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])


# ------------------------------------------------------------------ learning
def test_grouped_cv_never_splits_a_group():
    rng = np.random.default_rng(0)
    n = 400
    df = pd.DataFrame({f: rng.normal(size=n) for f in rvvet.FEATURES})
    y = (df["dchi2"] + 0.5 * rng.normal(size=n) > 0).astype(int).values
    groups = np.repeat(np.arange(40), 10)
    X = design(df)
    p = grouped_cv_predict(models()["logistic"], X, y, groups)
    assert np.all(np.isfinite(p))
    assert metrics(y, p)["auc"] > 0.75
    lo, hi = grouped_bootstrap_auc(y, p, groups, n=200)
    assert lo < metrics(y, p)["auc"] < hi


def test_keplerian_prewhitening_removes_eccentric_orbit():
    P, K, e = 150.0, 40.0, 0.6
    s = make_series(n=200, T=4000, sigma=1.5, seed=21,
                    signal=lambda t: kepler_rv(t, P, K, e, 1.0, 2455000.0 + 30.0) + 5e-7 * (t - 2455000.0) ** 2)
    r, model = prewhiten(s, [P], trend=2)
    resid = r.y - np.array([np.median(r.y[r.label == l]) for l in r.label])
    assert np.std(resid) < 2.5                    # back to the 1.5 m/s noise, not the 40 m/s orbit
    r2, _ = prewhiten(s, [P], trend=2, kepler=False)
    resid2 = r2.y - np.array([np.median(r2.y[r2.label == l]) for l in r2.label])
    assert np.std(resid) < np.std(resid2)         # a two-harmonic Fourier fit does worse at e = 0.6


def test_cli_runs(tmp_path):
    import json, subprocess, sys
    s = make_series(n=80, signal=lambda t: 6 * np.sin(2 * np.pi * t / 6.1), seed=30)
    rows = []
    for t, y, e, l in zip(s.t, s.y, s.e, s.label):
        rows.append(dict(star="TEST", bjd=t, rv=y, e=e, flag=0, snr=50.0, drift=0.0, dlw=np.nan))
    p = tmp_path / "rv.parquet"
    pd.DataFrame(rows).to_parquet(p)
    out = subprocess.run([sys.executable, "-m", "rvvet.cli", "vet", "--rvbank", str(p), "--star", "TEST"],
                         capture_output=True, text=True, check=True).stdout
    r = json.loads(out)
    assert abs(r["period"] - 6.1) < 0.05 and "provenance" in r
