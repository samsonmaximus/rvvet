# Where every number in the methods paper comes from

> Note for this repository: `analysis/counts.py` and `analysis/xstar.py` are in the companion
> repository `hd297396b`; `CHANGELOG.md` and `sims.log` were working files of the release folder
> and are summarised in the paper's Sect. 6.4 and Appendix B. `data/rvbank.parquet` is rebuilt
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
