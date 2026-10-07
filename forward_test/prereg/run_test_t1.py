"""Execute PREREG-T1 exactly as written. Do not edit the decision rule.

Input: a CSV per star with columns  inst,bjd,rv,err  (m/s; BJD_TDB), holding the pipeline
CCF velocities of the public post-RVBank spectra listed in ts_<star>.csv (e.g. exported from
DACE or read from the ESO CCF product headers). Usage:

    python run_test_t1.py GJ902 rv_gj902.csv
    python run_test_t1.py HD58489 rv_hd58489.csv
"""
import sys, json, hashlib, numpy as np, pandas as pd
from scipy.optimize import minimize

EPH = {  # copied from ledger_v1.csv (sha256 0d3f84df...); do not edit
    "GJ902":   dict(P=np.float64(36.0966341809), Tmax=np.float64(2456214.14075), K=np.float64(1.89863716905), sK=np.float64(0.406372439916)),
    "HD58489": dict(P=np.float64(19.5133582075), Tmax=np.float64(2456990.70857), K=np.float64(5.47530249534), sK=np.float64(1.34121993016)),
}


def nightly(d):
    d = d.copy()
    d["night"] = np.floor(d.bjd - 0.2).astype(int)
    out = []
    for (inst, n), g in d.groupby(["inst", "night"]):
        w = 1 / g.err ** 2
        out.append(dict(inst=inst, bjd=np.sum(w * g.bjd) / w.sum(), rv=np.sum(w * g.rv) / w.sum(), err=1 / np.sqrt(w.sum())))
    return pd.DataFrame(out)


def fit(d, P, T, free_phase=False):
    insts = sorted(d.inst.unique()); lab = np.array([insts.index(i) for i in d.inst])
    t, y, e = d.bjd.values, d.rv.values, d.err.values
    cols = [(lab == k).astype(float) for k in range(len(insts))] + [(t - t.mean()) / 365.25]
    cols.append(np.cos(2 * np.pi * (t - T) / P))
    if free_phase:
        cols.append(np.sin(2 * np.pi * (t - T) / P))
    X = np.column_stack(cols)

    def nll(lj):
        s2 = e ** 2 + np.exp(lj)[lab] ** 2; w = 1 / s2
        A = (X * w[:, None]).T @ X; p = np.linalg.solve(A, (X * w[:, None]).T @ y); r = y - X @ p
        return 0.5 * np.sum(r * r * w + np.log(s2))
    best = minimize(nll, np.zeros(len(insts)), method="L-BFGS-B", bounds=[(-6, 4)] * len(insts))
    s2 = e ** 2 + np.exp(best.x)[lab] ** 2; w = 1 / s2
    C = np.linalg.inv((X * w[:, None]).T @ X); p = C @ (X * w[:, None]).T @ y
    return p, C, dict(zip(insts, np.exp(best.x).round(3).tolist()))


def main(star, path):
    eph = EPH[star]; raw = pd.read_csv(path)
    raw = raw[np.isfinite(raw.rv) & np.isfinite(raw.err) & (raw.err > 0)]
    d = nightly(raw)
    p, C, jit = fit(d, eph["P"], eph["Tmax"])
    A, sA = p[-1], np.sqrt(C[-1, -1]); z = A / sA; comb = np.hypot(sA, eph["sK"])
    if z >= 3 and abs(A - eph["K"]) < 2 * comb: verdict = "SUPPORTED"
    elif 2 <= z < 3: verdict = "CONSISTENT, NOT DECISIVE"
    elif A < eph["K"] - 3 * comb: verdict = "REFUTED"
    else: verdict = "UNDECIDED"
    pf, Cf, _ = fit(d, eph["P"], eph["Tmax"], free_phase=True)
    a, b = pf[-2], pf[-1]; dphi = np.arctan2(b, a) / (2 * np.pi)
    res = dict(star=star, n_spectra=int(len(raw)), n_nights=int(len(d)), A=float(A), sigma_A=float(sA), z=float(z),
               K_pred=eph["K"], verdict=verdict, jitter=jit, free_phase_offset_cycles=float(dphi),
               free_phase_amp=float(np.hypot(a, b)),
               input_sha256=hashlib.sha256(open(path, "rb").read()).hexdigest())
    print(json.dumps(res, indent=1))
    json.dump(res, open(f"result_t1_{star}.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
