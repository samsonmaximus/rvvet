# Response to the referee report on the first draft

Every point of `REFEREE_methods_v1.md` is answered below. "Fixed" means the text, code or
data were changed; the new values are in the paper (every number there is a generated
macro, see `NUMBERS.md`) and are not repeated here, so this file cannot drift from them.
Code changes are in rvvet 0.2 (`rvvet/README.md`, "Changes in 0.2"). The frozen first-pass
outputs are kept in `results_v0.1/`, `figures_v0.1/`, `sims_v0.1/` and `paper_v0.1/`.

## A. Numbers

1. **Fixed.** Table 2 is now written by `analyze.py` from the unrounded values
   (`paper/tab_auc_rows.tex`), sorted by the value it prints.
2. **Fixed.** Every feature with an AUC is in Table 2, including `harm_missing` (defined in
   Sect. 3.2 and Table 1) and the two prior-dependent features, marked with a dagger.
3. **Fixed.** The worked example quotes only the pipeline's K and states why its epoch count
   differs from the discovery paper's.
4. **Fixed, and the finding changed.** The defect log was rebuilt from the records under a
   codebook fixed in advance, extracted by one fresh instance and coded by two blind ones
   (κ reported). It has 84 defects, not 30. The route is read from the records' own
   attributions (v13 "(R)" marks, the v14 review-pass section, the v15 referee report,
   the reference check). The paper says the first draft's count and conclusions were wrong
   (Sect. 8.2).
5. **Fixed.** The alias rung was corrected (point 7), the claimed-period window is ±0.5/T with
   an edge flag, and the per-signal narrative was replaced by a generated table of the
   features behind each verdict (Table 3).
6. **Fixed.** NUMBERS.md no longer carries typed values for anything the script produces.

## B. Code versus text

7. **Fixed in code.** Alias candidates outside the search band are not compared; each is
   refined inside the band and dropped if it refines to within 1.5/T of f0. Unit test
   `test_alias_candidates_stay_inside_the_search_band`.
8. **Fixed in code.** (i) Jitter: all jitters are rescaled by one common factor fitted with the
   candidate sinusoid; the detection statistic is the likelihood ratio (per-era refitting was
   tried and rejected because it collapses the jitter of a small era). (ii) Blocks and halves
   are compared in (a, b) space about their GLS mean, split into amplitude and phase parts,
   with n_b − 1 dof; blocks are no longer dropped. n_b − 2 for the phase was tried first and
   was anti-conservative on simulated planets; both trials are reported (Sect. 5.4). (iii) Missing
   values passing is stated in Sect. 3 and implemented explicitly in `rvvet.rules`.
   Calibration on simulated planets is now a results subsection.
9. **Fixed in text** (Sect. 3.2): maximum over ±0.5/T and indicators, per-era centring with a
   global robust scale, the 60 % coverage cut, zero without indicators. Its false-rejection
   rate on simulated planets is reported.
10. **Fixed in code and text.** The proxy searches 2.5–200 d with a Bonferroni factor for
    the number of indicators searched.
11. **Fixed in code and text.** Each indicator now has its own amplitude and phase lag, a fifth of
    activity cases leave no indicator signal, CRX is listed, eccentricities above 0.8 are
    redrawn, and the planet-alias label covers 2f, 3f, f/2 and all first-order aliases
    and precedes the rotation labels (`simulate.label_peak`, unit-tested).
12. **Fixed in code.** Simulated series get the same clip and quadratic trend as real stars.
13. **Fixed in code** (`floor(BJD − 0.196)`, La Silla local noon). The same error in the
    HD 297396 b analysis was checked and corrected there: no result about the star
    changes; two archive-wide numbers moved slightly (v15 CHANGELOG, "Post-release correction").
14. **Fixed.** The single-frequency term is included; it is called the Baluev approximation;
    χ² weights, T, N and n_era are defined.
15. **Fixed.** Docstring corrected; `figs_bench.py` removed (all figures come from `analyze.py`);
    the change logs and the referee reports are released with the defect log (`defects/sources/`);
    the star-selection text says dLW and Hα.
16. **Fixed.** A real fold-disjointness test (`test_grouped_folds_are_disjoint_by_star`), plus
    tests of the rule, the harmonic distances, the alias rung and the labels. The paper says
    which tests compare with an independent calculation and which check behaviour.

## C. Overclaims

17. **Fixed.** The impostor fraction is presented as a property of the priors, with its range
    across N quartiles.
18. **Fixed, with a new label.** A "rotation line" label (within the ±2σ width of a line of the
    QP spectrum, k = 0–4) now separates peaks inside the broad lines from exact harmonics;
    the text says what this means for harmonic-distance tests.
19. **Fixed at the source.** Planet and activity amplitudes both scale with the star's
    scatter, not with N; log N and log(T f0) are no longer classifier features; the detection
    baseline no longer includes N; the effect of adding them back is reported.
20. **Fixed, and the finding changed.** A dedicated calibration run (40 series per star, two
    noise models) with binomial intervals. The "four to eight" factor was the price of the
    fixed jitter: with the jitter treated as in 0.2 the approximation is close to nominal. The
    white-noise caveat is stated.
21. **Fixed.** Exact intervals; UI and UH reported separately; the "no false positives"
    wording is gone.
22. **Fixed.** Both the global FAP (blind search) and the single-frequency probability (known
    period) are reported, with what each answers; "the simplest test" wording removed; the
    single-feature AUCs on the benchmark are reported.
23. **Fixed.** Calibration is tested per bin with z-scores; the output on real candidates is
    called a score; the prior dependence is stated.
24. **Fixed in the simulations.** P_rot now spans 3–150 d and spot lifetimes 1–30 rotations; the
    long-P_rot, long-λ regime is reported separately; the number of refuted hosts outside the
    simulated range is reported; "more robust" is gone.
25. **Fixed.** `rule_alias` and the indicator-free model are reported on the benchmark.
26. **Fixed.** "Signals around HARPS-RVBank stars"; the number not discovered with HARPS is given.
27. **Fixed.** AUC without the easy controls (K/σK > 20) is reported.
28. **Fixed.** Limitations and Sect. 6.4 list both rounds of post-hoc changes; the frozen-pipeline
    results are released and the changed signals tabulated (Appendix B); the circularity of
    the HD 297396 b thresholds is stated in Sects. 3.3 and 7.
29. **Fixed, and the finding reversed.** The rebuilt log has an origin field: only 5 of 84 were
    code-to-text. The paper now says so.
30. **Fixed.** Every number in the text is a generated macro; literature values are listed; the
    tests are described accurately; the referee report and this response are released.

## D. Statistics

31. **Addressed in the simulations** (independent amplitudes and lags, indicator-free cases) and
    the sensitivity subsection.
32. **Fixed.** Operating points (TPR at 5 % and 1 % FPR), precision at stated prevalences,
    acceptance by impostor kind; the training/application mismatch is stated.
33. **Fixed.** Stratified bootstrap within each class and the number of misordered pairs; the
    simulation intervals are described as holding the fitted models fixed.
34. **Fixed.** Thresholds described as nominal levels whose error rates are measured on
    simulations (Sect. 5.4).
35. **Fixed in code** (point 8). Measured and expected K/σK are distinguished in the text.

## E–F. Consistency, citations, format

36. **Fixed.**
37. **Fixed.** The acceptance list's "v12–v15" is corrected to v13–v15 in the done/not-done
    review (the v12 → v13 change log is the earliest record); the review is in `CHANGELOG.md`.
38. **Fixed.** The appendix table has a note for log FAP 0.0 and for single references, and is
    placed after its heading.
39. **Fixed.** The withdrawal clause cites Rajpaul et al. (2016) and Lubin et al. (2021).
40. **Fixed.** Symbols defined; e is used only for uncertainties (eccentricity is e in the
    simulation paragraph only, where no uncertainty appears); classifier hyperparameters and
    transforms are given in Sect. 5.6.
41. **Fixed.** `\texorpdfstring` used; the draft date replaced by a preprint date;
    placeholders remain for the author.
