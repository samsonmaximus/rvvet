# Response to the second referee report

As before, values are not repeated here; they are generated macros in the paper. rvvet 0.3
contains the code changes; the simulations and the benchmark were rerun with it.

**First-round points not resolved in round 2**

* 10 — **Stated.** AD Leo's rotation (2.23 d) is below the 2.5-d proxy band; Sect. 6.3 says so. We
  did not lower the band, because the only reason to do so would be this benchmark signal.
* 28 — **Fixed.** The abstract says the benchmark counts shift with the window; Sect. 6.4 lists all
  three rounds of changes, including the window; Table 4 gives the results for three windows.
* 30 — **Fixed.** "Every computed result is a macro"; design constants, literature values and
  counts typed by hand are listed in `NUMBERS.md`; the 8.5 % is now a macro.
* 32 — **Fixed.** Sect. 6.3 states the highest-peak mismatch with counts.
* 35 — **Fixed.** Sect. 6.2 distinguishes measured from expected K/σK.
* 40 — **Fixed.** Uncertainties are ε_i; e is eccentricity only; f_proxy (the proxy) and f_rot
  (the injected rotation) are distinct.

**Round-2 findings**

1. **Fixed in code and text.** The window is capped at ±0.5/T in both refinement steps
   (`detect(window=)`); the offset (in 1/T) and an edge flag are in Table A1; the benchmark was run
   at ±0.5/T, ±0.25/T and the claimed period (Table 4); the change from ±0.25/T is listed as post hoc
   in Sect. 6.4; the HD 41248 c attribution now points to the table rather than the first pass.
2. **Fixed in code, reported, and stated.** Indicators are now detrended with the same per-era
   offsets and quadratic as the velocities before the indicator rung and the proxy; the simulations
   and benchmark were rerun. The proxy rates on simulated and real stars are reported side by side,
   with a model trained without the proxy features, and the mismatch is a stated limitation.
3. **Fixed.** Stated with counts (Sect. 6.3).
4. **Fixed.** See point 30.
5. **Fixed.** "The largest category" with its percentage.
6. **Fixed.** Counts among the numerical defects by origin are generated (Sect. 8.2).
7. **Fixed.** The line/harmonic balance is given by spot lifetime, and excluding the envelope;
   Conclusion 2 rewritten.
8. **Fixed.** Both AUCs.
9. **Fixed.** Both dof trials are computed on the same planets and generated; the docstring gives
   no number.
10. **Resolved by the rerun.** The simulations now store n_b − 1 p-values directly; `analyze.py`
    asserts this instead of converting.
11. **Fixed.** "Close to nominal" applies to the phase test; the amplitude test is called
    somewhat liberal, with its interval.
12. **Stated** (see point 10).
13. **Fixed.** Both test descriptions corrected.
14. **Fixed.** The caveat is stated and the counts at the claimed period are in Table 4.
15. **Fixed.** See point 35.
16. **Fixed.** Sect. 3.3.
17. **Fixed.** The coders are described as instances of the same model; the "lessons" are
    presented as practices the log is consistent with, and the route shares' dependence on the
    records is stated.
18. **Fixed.** The dependence on the activity RV amplitude is reported (Sect. 5.8) and the
    independence of the indicator amplitudes stated (Sect. 4).
19. **Fixed**: clip wording; φ described as the share of the rotational term; README; periodogram
    docstring; `prot_first` parses "~"; the empirical thresholds have bootstrap intervals. The
    rotation-rung status of GJ 581 d is in Table 3.
20. **Fixed** (point 40).
21. **Fixed**: Fig. 6 legend below the axes, Table 3 footnote, PDF metadata. The "float stuck"
    warnings come from the class's deferred floats and every float is placed.

## Round 3 (binary re-check of the above)

The same reviewer re-checked every item: 20 of 27 RESOLVED. The seven NOT RESOLVED items and the
four new findings (`REFEREE_methods_v3.md`) were addressed in rvvet 0.3.1:

* **N1 (major) — fixed in code, simulations and benchmark rerun.** Indicators are clipped at 15
  robust σ (the velocities' level) before and during the detrending fit, so outliers cannot tilt
  it; the rotation proxy is the highest local maximum (not a band-edge value) outside 1/T of one
  and two cycles per year. On the benchmark hosts the half-year proxies are gone, and more
  proxies agree with published rotation periods (Sect. 6.3). GJ 876 b is no longer rejected on a
  half-year harmonic. Sects. 6.3–6.4 give the corrected diagnosis.
* **R2-2** — see N1; the remaining mismatch between real and simulated proxy rates is attributed to
  what it is (permutation removes the star's own activity) and stated as a limitation.
* **R2-7 / R1-28** — the abstract now says "many ... rather than", with the dependence on spot
  lifetime, and that the rule's features were revised after its thresholds were fixed.
* **R2-9, N2** — `NUMBERS.md` and `CHANGELOG.md` rewritten for 0.3.1.
* **R2-19** — the bootstrap intervals of the empirical thresholds are printed.
* **R2-21** — Table 3's footnote defines every "Fails at" entry. The blank space before the
  appendix tables and the "float stuck" warnings are the class's float handling; every float is
  placed.
* **N3** — the window table is Table 4; corrected above.
* **N4** — Sect. 6.4 says the four first-round errors were corrected in version 0.2.
