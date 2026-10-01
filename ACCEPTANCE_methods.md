# Methods paper: frozen acceptance list (written 2026-09-29, before the results were in)

| # | Item |
|---|---|
| 1 | Installable, tested Python package (`rvvet`): ladder, simulation, learning, CLI; at least 20 unit tests passing; seeded runs; provenance block in CLI output. |
| 2 | False-alarm calibration of the detection statistic on real archival noise (noise-only simulations on real sampling). |
| 3 | Injection–recovery on real sampling and noise of at least 200 RVBank stars (at least 10 000 simulated cases in total). |
| 4 | Labelled simulation set with planets, activity impostors, window aliases and noise; single-test power (AUC) for every ladder feature. |
| 5 | Classifiers (logistic regression and gradient-boosted trees) with cross-validation grouped by host star; calibration and permutation importance; comparison with a detection-only baseline and with the a-priori rule (`results/RULES_FROZEN.md`). |
| 6 | External test on the literature benchmark (46 published HARPS signals with later verdicts): per-signal table, headline metrics on upheld vs refuted with bootstrap intervals, explicit discussion of small numbers and of labels that depend on the same tests. |
| 7 | HD 297396 b as a worked example through the generic pipeline. |
| 8 | Verification section with the documented defect log of the HD 297396 b analysis (v12–v15). |
| 9 | Paper in OJAp format; figures; every reference verified; AI statement per OJAp policy; code and data availability. |
| 10 | NUMBERS (provenance of every number), README, and a done / not-done review of this list. |
