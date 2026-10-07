# Forward-in-time test and the discovery ledger (Sect. 6.5)

Sect. 6.5 asks how the ladder does on signals whose fate was not known when the data were taken.
Two tests: a time split of the whole archive, and a pre-registered test of two open signals
against public spectra taken after HARPS-RVBank closed.

A planet counts as known before 2022 if the NASA Exoplanet Archive dates its discovery paper
before 2022 or exoplanet.eu dates its discovery before 2022. An earlier version of the time split,
in this repository's history, used the NASA archive alone. That counted HD 134606 b, announced in
2011 and listed by the NASA archive only from its 2024 confirmation, as a later planet.
`timesplit.py` reports the NASA-only numbers as a sensitivity check (`nea_only` in
`timesplit_numbers.json`), with the 13 stars whose status depends on the exoplanet.eu dates
(`excluded_by_eu_dates`).

## Reproduce Sect. 6.5

From this folder, in the environment of `../requirements-paper.txt`:

```bash
python timesplit.py        # writes timesplit_numbers.json, timesplit_list_2022.csv,
                           # fig_timesplit.pdf/.png and ../paper/numbers_forward.tex
```

Every number in Sect. 6.5 is a macro in `../paper/numbers_forward.tex`.

## What is here

| File | What it is |
|---|---|
| `archive_run_2026-09-30/archive_blind_rvvet.csv` | The blind run of rvvet 0.3.1 on all 1198 HARPS-RVBank stars with ≥ 20 nights over ≥ 100 d (highest peak per star, 1.2–500 d), with the rule outcome and both classifier scores. Made on 30 Sept 2026 in the paper's environment. In the environment of `requirements-paper.txt`, `blind_run.py` regenerates its features to machine precision (checked on 65 stars), and `score_check.py` regenerates both classifier scores to 1e-14. |
| `nea_xmatch_2026-10-04.txt` | NASA Exoplanet Archive (pscomppars) planets within 90″ of each eligible star, with publication dates, queried 4 Oct 2026. |
| `eu_xmatch_full_2026-10-06.txt` | exoplanet.eu (full catalogue of confirmed planets, downloaded 6 Oct 2026) matched by coordinates to all 240 stars with a significant, rule-passing signal with K < 100 m/s; the header records the source and its checksum. Stars with no planet listed do not appear. It replaces a 4 Oct match that covered only the ledger stars (in the git history). |
| `timesplit.py` and its outputs | The time split of Sect. 6.5 and the collection of the T1 numbers. |
| `ledger_v1.csv`, `ledger.py`, `MANIFEST.sha256` | The discovery ledger: the 116 significant, rule-accepted signals in the planet regime that the NASA archive did not list at that period, with circular ephemerides and a literature check (`lit_status`). It was frozen at 08:13 MDT on 4 Oct 2026, before any post-RVBank velocity was read (see the git history). Two entries are planets announced in 2011 that exoplanet.eu lists: RVL-087 (HD 157172 b, noted in `lit_status`) and RVL-005 (HD 215456 b on HIP 112414, found later by the coordinate match). |
| `prereg/` | Test T1: the rule (`PREREG-T1-out-of-sample.md`), the executable test (`run_test_t1.py`), the data-handling decisions made before any fit (`T1-DEVIATIONS.md`), the velocities read from the ESO CCF products (`t1_data/`), the result (`T1-RESULT.md`) and the calibration done afterwards (`t1_data/null.py`, `t1_null.json`). |
| `archive_scored.parquet`, `score.py`, `full_run.py`, `repro.py`, `timesplit_2022_list.csv` | The 4 Oct rerun of the archive from which the ledger was built. It ran in a newer environment (scipy 1.18, scikit-learn 1.9.1). Its rule outcomes match the 30 Sept run for all 1198 stars, but its tree scores differ by up to 0.16. `timesplit_2022_list.csv` holds the 115 signals of the NASA-only list. The paper uses the 30 Sept run, which matches the paper's environment. |

## Timestamps

The git history keeps the original commit times. In order: the ledger and the T1 rule at 08:13, the
executable test at 08:17, the data decisions at 09:09, and the result at 09:12 (MDT, 4 Oct 2026).
Git times are written by the committer, so they record the order, not an independent proof of it.

Later work in the same repository, which is not part of this paper, and the working notes of that
morning were filtered out of this history. `prereg/T1-RESULT.md` is the record written on 4 Oct.
Where it differs from the paper, the paper's reading holds: under the registered model the HD 58489
test is undecided, not passed.

## ESO data used by T1

Public HARPS, ESPRESSO and NIRPS spectra from the ESO Science Archive Facility, programmes
106.21R4.001, 108.222V.001, 110.248C.001, 112.25YG.002, 112.25YG.005, 112.25YG.006,
112.25YG.007, 112.25YG.008, 112.25YG.009, 112.25YG.010 and 115.285G.001 (67 products; the
product identifiers are in `prereg/t1_data/`).

Scripts in this folder originally ran from another directory layout. Their paths were made
relative to this repository on 6 Oct 2026, and one dead line was removed from
`prereg/t1_data/null.py`. Neither change alters any output: `null.py` and `run_test_t1.py`
reproduce their stored results exactly.
