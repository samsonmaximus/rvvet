# Referee report on the revised methods paper (rvvet 0.2), second round

Independent review, 2026-09-29, by a fresh instance of the model given the revised paper,
the first report and response, the code, the outputs and the defect-log materials, but not
the conversation that produced them. It edited no project files. Condensed from the report
as delivered; the response is in `RESPONSE_methods_v2.md`.

**Checks.** `pytest` 36 passed. `analyze.py` re-run on a scratch copy reproduces
`numbers.tex` (308 macros), `numbers.json` and all `tab_*.tex` byte for byte; ~120 macros
recomputed independently from raw files all match; 8 more simulated cases regenerated from
their seeds match exactly. Text/code consistency verified for the likelihood-ratio statistic,
the Baluev formula, the dof, the labels, every simulation prior, the class mix and star
selection, except the period window and the clip wording.

**First-round points:** 35 RESOLVED, 6 NOT RESOLVED (10, 28, 30, 32, 35, 40).

## Findings

1. (major) The claimed-period window was changed after the first pass (±0.25/T → ±0.5/T),
   is effectively ±0.6/T because of a second refinement, and drives 3 of the 7 changes of
   Table B1 (Kapteyn c, HD 41248 c, GJ 176 b); with ±0.25/T the headline becomes 4 of 5 refuted
   and 2 of 21 upheld rejected; at the exact period Kapteyn c, Barnard 233 d and GJ 176 b are
   not significant and HD 192310 b fails on phase. List the change, cap or state the window,
   add the offset and edge flag to Table A1, give headline numbers for ±0.25/T and the exact
   period, and correct the attribution of the HD 41248 c flip.
2. (major) The rotation proxy is significant for 0.26 % of simulated planets but for 18 of 28
   benchmark hosts and 13 of 21 significant upheld signals, often at 100–200 d (cycles or
   trends: indicators are only median-centred); 6 of 10 hosts with published P_rot disagree by
   more than 20 %. Masking the proxy features changes benchmark AUCs (trees 0.90 → 0.94,
   logistic 0.98 → 0.94) and individual scores. Detrend the indicators or cap the band, compare
   feature distributions, report results without proxy features, state the mismatch.
3. (minor) Trained on highest peaks, applied at claimed periods: 3 of 6 significant refuted
   signals are not the highest peak, all 21 upheld are.
4. (minor) "Every number generated" is false (8.5 %, test counts, 30, 16:43 UT, design
   constants); reword to computed results and generate the 8.5 %.
5. (minor) "Most were overclaims": 39 of 84 is the largest category, not a majority.
6. (minor) The numerical-error sentence uses origin totals over all categories; among the 19
   numerical defects: literature 8, analysis 5, code 4, revision 2.
7. (minor) Conclusion 2 overgeneralises: line/harmonic balance depends on λ (short: 267 vs 72;
   long: 141 vs 403) and includes the k = 0 envelope.
8. (minor) Conclusion 4 quotes only the logistic AUC; give both.
9. (minor) dof-trial numbers from different samples (8.5 % on 7000 cases vs 4.4 % on all);
   docstring says 4.8 %.
10. (minor) The dof conversion of the stored simulations is not disclosed.
11. (minor) "Close to nominal" does not hold for the amplitude test (7.4 % below 0.05, ~4σ).
12. (minor) AD Leo's 2.23-d rotation is below the 2.5-d proxy band; state it.
13. (minor) Two test descriptions overstate (homogeneity test checks the mean only; the FAP
    conservatism test uses the known-variance statistic).
14. (minor) The single-frequency counts depend on the window and use the liberal statistic.
15. (minor) Measured and expected K/σK compared directly.
16. (minor) The missing-values-pass rule is not in the paper.
17. (minor) Coders are instances of the same model; "two lessons" are descriptive, and route
    shares follow which record exists per version.
18. (minor) Unreported dependence on the activity RV amplitude; indicator amplitude drawn
    independently of A not stated.
19. (typo) Clip applied before injection; φ multiplies the rotational term; README dof wording;
    stale periodogram docstring; `prot_first` drops "~"; GJ 581 d also fails the rotation rung;
    the 0.1 % empirical threshold needs an interval.
20. (typo) e for eccentricity and uncertainties; f_rot for proxy and truth.
21. (typo) Float-stuck warnings; blank appendix page; Fig. 6 legend over the separator; Table 3
    footnote lacks "Fails at"; empty PDF metadata.

**Recommendation:** major revision, narrowly scoped; no new simulations required for 3–21.
