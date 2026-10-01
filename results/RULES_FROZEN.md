# A-priori ladder rule (frozen 2026-09-29, before any benchmark signal was run through the pipeline)

A candidate PASSES the rule-based ladder if all of the following hold. The thresholds come
from the HD 297396 b analysis and standard significance levels, not from the benchmark.

| Rung | Condition | Reason |
|---|---|---|
| Detection | log10_fap < -2 (Baluev bound, band 1.2-500 d) | 1 % global false-alarm level |
| Period | alias_margin > 0 | the period beats its day/month/year and spectral-window aliases |
| Phase coherence | block_phase_p > 0.01 and half_phase_z < 3 | phase constant across four blocks and two halves |
| Activity, spectroscopic | ind_max_dchi2 < 13.8 | no indicator has power at P with single-frequency p < 0.001 (chi2, 2 dof) |
| Activity, rotation | harm_dist >= 1 or no rotation proxy (act_log10_fap >= -2) | not within one resolution element of k*f_rot, k = 1-4 |

Benchmark labels are never used to set or change these thresholds. The machine-learned
classifiers are trained only on simulations; the benchmark is an external test.
Tue Sep 29 12:08:22 UTC 2026
