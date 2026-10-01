# rvvet — which tests catch false planets in archival radial velocities?

Code, simulations, benchmark and results behind

> **Fraser, S. (2026). Which tests catch false planets in archival radial velocities? An
> injection-calibrated vetting ladder tested on published signals with known fates.**
> *Submitted to the Open Journal of Astrophysics.* arXiv: ARXIVID

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

## Layout

| Folder / file | Contents |
|---|---|
| `rvvet/` | The Python package (`src/rvvet`), 40 unit tests, CLI and the scripts that reproduce the paper. **Start with `rvvet/README.md`.** |
| `results/` | Outputs behind every number: `numbers.json` (full precision), false-alarm calibration, benchmark features and scores, calibration tables, reproducibility check. |
| `figures/` | The six paper figures, written by `rvvet/scripts/analyze.py`. |
| `sims/` | The 16 000 simulated cases (parquet, 500 per file) and `stars.json` (the 260 stars and the seed). |
| `benchmark_literature.csv` / `.md` | The 46 published signals, their verdicts and references. |
| `defects/` | The defect-log study of Sect. 8.2: codebook, sources, extraction, two independent codings, adjudicated log. |
| `reviews/` | The referee reports on the paper and the responses. |
| `results_v0.1/`, `figures_v0.1/`, `sims_v0.1/`, `rvvet_v0.1_snapshot/` | The frozen first pass, kept for the before/after comparison in Appendix B. |
| `NUMBERS.md`, `ACCEPTANCE_methods.md` | Provenance of every number; the acceptance list frozen before the work. |

## Install

```bash
pip install "git+https://github.com/GITHUBUSER/rvvet#subdirectory=rvvet"
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

Cite the paper above and this archive: Zenodo DOI ZENODODOI (see `CITATION.cff`).
Code: MIT (`LICENSE`). Data, results and documentation: CC BY 4.0 (`LICENSE-DATA.md`).
Velocities derive from HARPS-RVBank (Perdelwitz et al. 2024, A&A 683, A125); please cite it too.
