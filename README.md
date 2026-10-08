# rvvet — which tests catch false planets in archival radial velocities?

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23249395.svg)](https://doi.org/10.5281/zenodo.23249395)

Code, simulations, benchmark and results behind

> **Fraser, S. (2026). Which tests catch false planets in archival radial velocities? An
> injection-calibrated vetting ladder tested on published signals with known fates.**
> *Preprint.*
> Preprint: [`Fraser2026_rvvet_methods.pdf`](Fraser2026_rvvet_methods.pdf) in this repository; archived at Zenodo, [doi:10.5281/zenodo.23249395](https://doi.org/10.5281/zenodo.23249395). arXiv ID to follow.

`rvvet` runs a ladder of interpretable tests on a periodic signal in a long radial-velocity time
series. The ladder covers detection, amplitude, aliasing, stationarity and stellar activity. It
returns one feature per question a referee would ask of an archival planet candidate. The paper
calibrates those features on 16 000 simulated planets and activity impostors, injected into the
real sampling and noise of 260 HARPS-RVBank stars. It then tests them on 46 published signals
whose fate is known: upheld or refuted.

**Main results** (details and caveats in the paper):

- No single test is decisive. The best single feature reaches AUC 0.78; combined classifiers reach 0.91–0.92.
- On these stars the Baluev false-alarm approximation is *liberal*: a nominal 0.44 % corresponds to a real 1 %.
- The a-priori rule rejects 5 of the 6 significant refuted signals and 2 of 21 significant upheld ones.
- Run on the archive as it stood in January 2022, the ladder ranks the 10 signals since published as planets
  near the top (6 of the top 10, against 1.0 expected), though not measurably better than the false-alarm
  probability alone. Five of those six are on stars with TESS candidates, which observers were already
  following. Of two pre-registered predictions tested with newer ESO spectra, one failed (GJ 902) and the other
  (HD 58489) is undecided under the registered model.

## Layout

| Folder / file | Contents |
|---|---|
| `rvvet/` | The Python package (`src/rvvet`), 40 unit tests, CLI and the scripts that reproduce the paper. **Start with `rvvet/README.md`.** |
| `paper/` | LaTeX source of the paper. `numbers.tex` and `tab_*.tex` are written by `rvvet/scripts/analyze.py`, `numbers_forward.tex` by `forward_test/timesplit.py`, `numbers_versions.tex` by `rvvet/scripts/version_sensitivity.py` and `numbers_hdfap.tex` by `rvvet/scripts/hd297396_fap.py`; `build.sh` builds the PDF (needs the figures from `figures/`). |
| `results/` | Outputs behind every number: `numbers.json` (full precision), false-alarm calibration, benchmark features and scores, calibration tables, reproducibility check. |
| `figures/` | The six paper figures, written by `rvvet/scripts/analyze.py`. |
| `sims/` | The 16 000 simulated cases (parquet, 500 per file) and `stars.json` (the 260 stars and the seed). |
| `benchmark_literature.csv` / `.md` | The 46 published signals, their verdicts and references. |
| `defects/` | The defect-log study of Sect. 8.2: codebook, sources, extraction, two independent codings, adjudicated log. |
| `reviews/` | The referee reports on the paper and the responses. |
| `results_v0.1/`, `figures_v0.1/`, `sims_v0.1/`, `rvvet_v0.1_snapshot/` | The frozen first pass, kept for the before/after comparison in Appendix B. |
| `forward_test/` | The forward-in-time test of Sect. 6.5: the 30 Sept archive run, catalogue cross-matches, the discovery ledger and the pre-registered test T1, with its git history. See `forward_test/README.md`. |
| `requirements-paper.txt` | The exact environment that reproduces the paper (see below). |
| `NUMBERS.md`, `ACCEPTANCE_methods.md` | Provenance of every number; the acceptance list frozen before the work. |

## Reproduce the paper

```bash
python3.13 -m venv venv && . venv/bin/activate
pip install -r requirements-paper.txt && pip install -e ./rvvet
python rvvet/scripts/load_rvbank.py table4.dat.gz data/rvbank.parquet   # see below for table4.dat.gz
python rvvet/scripts/analyze.py                                         # every macro, table and figure
python rvvet/scripts/hd297396_fap.py                                    # the FAP comparison of Sect. 7
(cd forward_test && python timesplit.py)                                # Sect. 6.5
```

In this environment the released code regenerates the paper's numbers, tables and figures exactly
(checked in a fresh virtual environment on 2026-10-06). `rvvet/README.md` lists the longer runs
that regenerate the simulations and benchmark features themselves.

## Install

```bash
pip install "git+https://github.com/samsonmaximus/rvvet#subdirectory=rvvet"
# or, from a clone:
pip install -e "./rvvet[test]" && (cd rvvet && pytest)    # 40 tests
```

The HARPS-RVBank table is not stored here. Download `table4.dat.gz` from CDS catalogue
[J/A+A/683/A125](https://cdsarc.cds.unistra.fr/viz-bin/cat/J/A+A/683/A125) and convert it with
`python rvvet/scripts/load_rvbank.py table4.dat.gz data/rvbank.parquet`.

## Use of AI tools

The code was written with the assistance of a large language model (Claude, Anthropic) under the
author's direction. The paper's verification section (Sect. 8) and `defects/` document how the
code and text were checked, including every defect found and how it was found.

## Citation and licence

Cite the paper above and this archive: Zenodo DOI 10.5281/zenodo.23249395 (see `CITATION.cff`).
Code: MIT (`LICENSE`). Data, results and documentation: CC BY 4.0 (`LICENSE-DATA.md`).
Velocities derive from HARPS-RVBank (Perdelwitz et al. 2024, A&A 683, A125); please cite it too.
