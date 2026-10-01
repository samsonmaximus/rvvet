# Referee report on the first draft (rvvet 0.1) of the methods paper

Independent review, 2026-09-29, by a separate instance of the model given the manuscript,
the code, the outputs and the acceptance list, but not the conversation that produced them.
It edited no files. The report is reproduced as delivered (formatting condensed); the
authors' response to each point is in `RESPONSE_methods_v1.md`.

**Recommendation: major revision.** Verified: every number in the text against numbers.json,
the CSVs and the code (most match; exceptions below); 12 simulated cases regenerated from
their seeds match their stored features exactly; `pytest` 26 passed.

## A. Numbers that do not match

1. (typo) Table 2 rounding: `growth_rho` 0.8348 printed 0.84 (0.83); `K_over_rms` 0.7546 printed 0.76 (0.75); `apod_gain` 0.6946 printed 0.70 (0.69, and it belongs below `log_ncyc` 0.695).
2. (minor) Table 2 omits `log_n` (0.67), `harm_alias_dist` (0.68) and `harm_missing` (0.67); `harm_missing` is used by the classifiers but never defined.
3. (minor) Sect. 6: "a 4.27-d, 5.5 m/s candidate" is not in NUMBERS.md; the pipeline in the same paragraph gives K = 6.59 ± 1.08.
4. (major) Sect. 7.2, Table 4, Conclusion 5: defect_log.csv contradicts itself — `how_caught` names the independent reviewer for E1, E6, E7, E8 and C3 while `route` assigns them to self-review; by `how_caught` the reviewer found 20 of 30, all 6 overclaims.
5. (major) Sect. 6.2: Barnard b's "marginally stronger alias" is the 1.002-d mirror, outside the 1.2–500 d band, and its refined period sits at the ±0.25/T window edge; AD Leo b's "stronger alias" is 1.5/T from f0, the same activity peak; GJ 581 d's "first harmonic" is k = 2, and harm_dist ≥ 1 means it passes the rotation rung (rejected on Hα).
6. (typo, NUMBERS.md) K/σK of Barnard 3.15 d 3.27, Proxima b 4.66, HD 15337 c 5.05; Barnard 233 d alias margin −0.575.

## B. Where the code contradicts the text

7. (major) Period rung: `vet` compares f0 with aliases down to 0.5 d, outside the 1.2-d band, and excludes candidates within 1.5/T before refining them by ±0.5/T, so a "window alias" can refine back onto f0's own peak. 191 of the 296 planets that fail this rung are planet-only; in 12 rebuilt, the winning alias is the ~1-d mirror of the planet.
8. (major) Stationarity p-values far from uniform for true planets (median block_phase_p 0.94): jitter fitted without the signal and held fixed; deviations measured from the global fit but tested with dof = number of blocks; blocks with σφ ≥ 120° dropped; NaN treated as a pass.
9. (minor) Indicator rung maximises over ±0.5/T and 8 indicators (not single-frequency); per-era centring with a global MAD; indicators with <60 % coverage dropped; no indicators → 0 and pass.
10. (minor) Rotation proxy: lowest FAP among four indicators with no correction; the 8–150 d band cannot find AD Leo's 2.23-d rotation.
11. (minor) Simulated activity: one ind_snr shared by all 8 indicators; CRX also receives G but is not listed; eccentricity clipped at 0.8 not truncated; planet-alias label checks only 2f_p and rotation takes precedence.
12. (minor–moderate) Simulations use `vet(s)` without trend, prewhitening or clip; benchmark and HD 297396 b use trend=2 and the 15σ clip.
13. (minor) Nightly binning uses floor(BJD − 0.5), starting a night at 0 h UT; ~4 % of spectra are taken 22–24 UT; 42 same-era epoch pairs < 0.3 d apart in the benchmark stars. Fix: floor(BJD − 0.2).
14. (minor) "Baluev bound": the code omits the single-frequency term; the w_i are whitening factors (χ² weights are w_i²); T, 1/T and N undefined.
15. (minor) run_benchmark.py docstring stale; README omits figs_bench.py, which overwrites two figures; change logs "released with the code" not in the package; star-selection text vs code (only dLW and Hα required).
16. (minor) The CV-group test does not test group separation; "26 unit tests … against independent calculations" overstates; rule_pass, harmonic_distances, alias_margin, labelling and analyze.py untested.

## C. Overclaims

17. (major) "35 % are impostors" is set by the class mix and amplitude priors (planet fraction 83 % → 49 % from the lowest to the highest quartile of N).
18. (major) "Mostly activity at periods unrelated to rotation" is a labelling artefact: 93 % of the 1552 "other activity" peaks lie within 1/λ of k·f_rot, k = 0–4.
19. (major) The 0.66 → 0.82 gain of the "detection-only" baseline comes entirely from N (N alone 0.664; without N 0.665), an artefact of K ∝ σ√(2/N) against activity ∝ σ; `log_n` is third in importance.
20. (major) "Conservative by four to eight" rests on 2, 15 and 36 events (1 %: interval ~2–65) under a white permuted null; factors 3.7 and 2.7 at 20 % and 50 %.
21. (major) "No false positives and no false negatives": 0/4 gives an upper limit of 60 %, 0/19 of 18 %; 7 of 19 are HARPS-only; report UI separately.
22. (major) "The most informative test is the simplest": on the benchmark, growth_rho 0.89, alias_margin 0.87, block_phase_rms 0.87, ind 0.85, −log FAP 0.80; the 13-of-17 result depends on a global FAP for a known period (single-frequency p < 0.01: 5 of 17 refuted and 2 of 26 upheld non-significant).
23. (minor–major) "Both well calibrated": Brier does not measure calibration; trees are overconfident (e.g. 0.980 vs 0.969, z = −3.6); calibration is to the simulated prior; call the benchmark output a score.
24. (major) GJ 581 d: its P_rot (130 d) is outside the simulated 8–60 d; 3 of 4 significant refuted hosts (and 8 of 17 refuted) are outside that range; "more robust" rests on one case.
25. (major) Unreported: `rule_alias` rejects the upheld HD 10180 d and does not catch Barnard b 233 d; the indicator-free model's benchmark AUC is 0.80 (0.32–1.0), 0.99 for GJ 581 d, 0.34 for HD 192310 b.
26. (minor) Six signals were not discovered with HARPS; say "signals around HARPS-RVBank stars".
27. (minor) Easy controls (GJ 876 b, GJ 436 b, GJ 581 b) inflate the benchmark AUC.
28. (minor) Limitations: harm_alias_dist cannot change significance; first-pass benchmark results unreported; the abstract should mention post-hoc changes; thresholds partly from HD 297396 b (circular).
29. (minor–major) "Most … where numbers passed from code into text" unsupported (no origin field; transcriptions include literature values); self-review is not independent; "two practices would have prevented most" is speculation.
30. (major) AI statement: "numbers printed by the analysis script" false; "26 unit tests … independent calculations" overstated; no record of the independent review in the materials.

## D. Statistical concerns

31. (major) Indicator power separable by construction (same G, no lag, one amplitude, planets never imprint).
32. (minor) Trained on highest peaks, applied at claimed periods; the 0.5 threshold is arbitrary (report operating points, precision at stated prevalences); trees accept 70 % of planet aliases and 73 % of noise impostors.
33. (minor) Benchmark bootstrap with 4 negatives unreliable (report the 76 pairs); simulation AUC intervals omit training variability.
34. (minor) Multiple testing in the rule; present thresholds as empirically calibrated.
35. (minor) No-signal jitter absorbs real signals (Proxima b K/σK 4.7 but FAP 0.22) and pushes 50 % completeness to K/σK ≈ 7.5; measured vs expected K/σK are different quantities.

## E. Internal consistency and citations

36. (typo) Window aliases "injected"; growth_rho called phase stability; "equal size" blocks → equal numbers of epochs.
37. (minor) Acceptance item 8 says v12–v15 but the log covers v13–v15; the done/not-done review is missing.
38. (typo) Table A1 floats before its heading; log FAP 0.0 means FAP ≈ 1; some upheld rows lack a verdict reference.
39. (minor) Dumusque2012 and Ribas2018 are discovery papers cited as evidence of withdrawal.

## F. Language and format

40. (minor) Undefined or reused symbols (T, N, n_era, f_rot; e for errors and eccentricity; φ, w); classifier hyperparameters and transforms not given.
41. (minor) `\texorpdfstring` for the section title; remove "Draft version \today"; placeholders noted.
