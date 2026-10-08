# Where every number in the methods paper comes from

> Note for this repository: `analysis/counts.py` and `analysis/xstar.py` are in the companion
> repository `hd297396b`; `CHANGELOG.md` was a working file of the release folder and is
> summarised in the paper's Sect. 6.4 and Appendix B. `sims.log` (the per-chunk simulation
> timing behind `\nmSecPerCase`) is in the repository root. `data/rvbank.parquet` is rebuilt
> locally with `rvvet/scripts/load_rvbank.py` (see README).

**Generated numbers.** Every computed result in the text of `paper/rvvet_methods.tex` is a
LaTeX macro `\nm...` defined in `paper/numbers.tex`. That file is written by
`rvvet/scripts/analyze.py` from the analysis outputs; so are the table bodies
`paper/tab_auc_rows.tex`, `tab_bench_rows.tex`, `tab_refsig_rows.tex`, `tab_window_rows.tex`,
`tab_v01_rows.tex` and `tab_defects_rows.tex`. Design constants, literature values and counts
of items (tests, review rounds) are typed by hand and listed at the end.
`results/numbers.json` holds the full-precision values behind the macros (same script, same
run). To regenerate: see `rvvet/README.md`, "Reproduce the paper".

| Macro group | Source files | Script section |
|---|---|---|
| `\nmSim*`, `\nmN*Only`, `\nmSecPerCase` | `sims/chunk_*.parquet`, `sims.log` | simulations |
| `\nmFap*` | `results/fap_calibration.parquet` (`scripts/fap_calibration.py`) | false-alarm calibration |
| `\nmComp*`, `\nmPlWrong*` | sims, planet-only cases | completeness |
| `\nmNDet*`, `\nmImp*`, `\nmDetPlanetPct*`, `\nmNoise*` | sims, detections | impostors |
| `\nmAuc*` (single features), Table 2 rows | sims, detections | single-feature power |
| `\nmAucLog*`, `\nmAucTree*`, `\nmBrier*`, `\nmCal*`, `\nmTree*` | grouped CV on detections | classifiers |
| `\nmRule*`, `\nmRungRej*`, `\nmBPh*` (incl. `\nmBPhFiveNbTwo`, the n_b − 2 trial), `\nmBAmp*`, `\nmHPh*`, `\nmHAmp*`, `\nmIndOverPl` | sims | rule, calibration of the rungs |
| `\nmSt*`, `\nmDom*`, `\nmAmp*`, `\nmLine*`, `\nmHarm*`, `\nmImpRotLineNoEnv` | sims, activity impostors | sensitivity strata, lines vs harmonics |
| `\nmProxy*`, `\nmAucNoProxy`, `\nmBAucNoProxy*` | sims and benchmark | rotation-proxy rates, models without proxy features |
| `\nmBench*`, `\nmRef*`, `\nmUp*`, `\nmBRule*`, `\nmBAuc*`, `\nmBMis*`, `\nmBSingle*`, `\nmBTree*`, `\nmBLog*`, `\nmTop*`, `\nmBChanged`, `\nmBEasyN` | `results/benchmark_features.csv`, `benchmark_literature.csv`, `results_v0.1/benchmark_scored.csv` | benchmark |
| `\nmWin*`, `\nmNEdge`, Table 4 rows | `results/benchmark_windows.csv` | window sensitivity |
| `\nmHD*` | `data/rvbank.parquet` (HD 297396) | worked example |
| `\nmRVBank*`, `\nmBenchClipped*`, `\nmProx*` | `data/rvbank.parquet` | the archive |
| `\nmDef*` (incl. `\nmDefNum*`), Table 5 rows | `defects/defect_log.csv`, `defects/coder_A.csv`, `defects/coder_B.csv`, `defects/excluded.csv` | defect log |
| `\nmTs*`, `\nmTa*` (Sect. 6.5) | `paper/numbers_forward.tex`, written by `forward_test/timesplit.py` from `forward_test/archive_run_2026-09-30/archive_blind_rvvet.csv`, `nea_xmatch_2026-10-04.txt`, `eu_xmatch_full_2026-10-06.txt`, `ledger_v1.csv` and `prereg/t1_data/` | forward test |
| `\nmHDfapHz`, `\nmHDfapHzNoNight`, `\nmHDfapNoNight`, `\nmHDratio*` (Sect. 7) | `paper/numbers_hdfap.tex`, written by `rvvet/scripts/hd297396_fap.py` from `data/rvbank.parquet`; full precision in `results/hd297396_fap.json` | worked example: FAP comparison |
| `\nmVer*` (Sect. 8.1) | `paper/numbers_versions.tex`, written by `rvvet/scripts/version_sensitivity.py` from `results/sklearn19_sensitivity.json` | software versions |

**Numbers typed by hand** (all others are macros):

| Number | Value | Source |
|---|---|---|
| Unit tests | 40 (13 against an independent calculation, 27 behavioural) | `pytest`; classification in the paper, Sect. 8.1 |
| Search band, grid | 1.2–500 d, 3 per 1/T | `ladder.vet` defaults |
| Rotation-proxy band | 2.5–200 d, excluding 1/T around 1 and 2 cycles per year | `ladder.ROTATION_BAND`, `ladder.activity_period` |
| Indicator clip | 15 robust σ | `ladder.INDICATOR_CLIP` |
| Claimed-period windows | ±0.5/T adopted; ±0.25/T and 0 for sensitivity | `ladder.detect`, `run_benchmark.WINDOWS` |
| Rule thresholds | FAP 1 %, alias margin 0, block p 0.01, half 3σ, Δχ² 13.8, harm_dist 1 | `results/RULES_FROZEN.md`, `rvvet/rules.py` |
| Simulation priors | all ranges in Sect. 4 | `scripts/run_sims.py::one_case` docstring and code |
| Star selection | 40–250 nights, ≥1500 d, ≤3 m/s, dLW and Hα ≥80 %, RV std ≤20 m/s | `run_sims.py::select_stars` |
| Class mix | 35/25/30/10 % | `run_sims.py::CLASSES` |
| Local noon at La Silla | 16:43 UT, JD fraction 0.196 | longitude 70.73° W |
| Literature rotation periods (GJ 581 130 d, etc.) | | `benchmark_literature.csv` (`prot_d`, `prot_ref`) |
| First-draft defect count 30 and its split | | `results_v0.1/defect_log.csv`, `paper_v0.1/` |
| Referee points on the first draft; review rounds | 41; three rounds | `reviews/REFEREE_methods_v1.md`, `REFEREE_methods_v2.md`, `REFEREE_methods_v3.md` |
| "Four errors" found in the first draft | night boundary, alias rung, fixed jitter, block dof | `reviews/REFEREE_methods_v1.md` points 7, 8, 13 |
| v15 post-release correction (1221→1214 stars; 612→611, 1.24→1.21, 49→54, 7.6→8.1) | | v15 `CHANGELOG.md`, `analysis/xstar.py`, `analysis/counts.py` |
| Sect. 7: discovery-analysis values for HD 297396 b (K = 5.5 ± 0.8 m/s; FAP 1.4 × 10⁻³ by simulation with all epochs; without the discrepant night no simulation exceeds the peak and the analytic Baluev bound is 7 × 10⁻⁶ (6.7 × 10⁻⁶); four groups of programmes). `hd297396_fap.py` also uses that paper's analytic values, 2.2 × 10⁻³ and 6.7 × 10⁻⁶, and the night's date, BJD 2454922.53 | | the HD 297396 b paper (Fraser 2026, doi:10.5281/zenodo.23249329), Sects. 2.1, 4.2 and 4.5 |
| Sect. 6.5: hit window 1.5/T (and 1/T, 5 % for sensitivity); K < 100 m/s; catalogue query dates | NASA archive 2026-10-04, exoplanet.eu 2026-10-06 | `forward_test/timesplit.py`, headers of `nea_xmatch_2026-10-04.txt` and `eu_xmatch_full_2026-10-06.txt` |
| Sect. 6.5: years of the planets named in the text (HD 134606, 2011; HD 137496, 2021; two TESS planets, 2019) | | `forward_test/timesplit_numbers.json` (`excluded_by_eu_dates`); `timesplit.py` stops if the list changes |
| Sect. 6.5: the ESPRESSO product of another star in the GJ 902 cone (−106 against +70 km/s) | | `forward_test/prereg/T1-DEVIATIONS.md`, item 3 |
| Sect. 6.5: period range of the HD 58489 check (2–150 d) | | `forward_test/prereg/t1_data/secondary.py` |
| Sect. 6.5: "the two of its 30 highest-ranked signals with at least ten public post-2022 spectra" | | `forward_test/prereg/PREREG-T1-out-of-sample.md` |
| Acknowledgements: ESO programme IDs of the T1 spectra (11 programmes, 67 products) | | ESO archive TAP query of the product identifiers in `forward_test/prereg/t1_data/`, 2026-10-06; listed in `forward_test/README.md` |
| Sect. 8.1: software versions (Python 3.13, numpy 2.4, scipy 1.17, pandas 3.0, scikit-learn 1.8, matplotlib 3.10) | | `requirements-paper.txt` |
