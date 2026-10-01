# rvvet — vetting radial-velocity planet signals in long archival time series

`rvvet` runs a ladder of interpretable tests on a periodic signal in a radial-velocity (RV)
time series and returns one feature per question a referee asks of an archival planet
candidate:

| Rung | Question | Features |
|---|---|---|
| Detection | Is the peak significant for this sampling? | `dchi2`, `log10_fap` (Baluev 2008 bound), `top_margin` |
| Amplitude | Is the semi-amplitude large compared with errors and scatter? | `snr_K`, `K_over_rms` |
| Period | Is it a window alias of another peak? | `alias_margin` (day, month, year and the star's own window peaks) |
| Stationarity | Does it keep amplitude and phase? | `half_phase_z`, `half_amp_z`, `half_imbalance`, `block_phase_p`, `block_amp_p`, `growth_rho`, `apod_gain` |
| Activity | Do indicators vary at this period, or does it sit on a rotation harmonic? | `ind_max_dchi2`, `ind_max_absr`, `act_log10_fap`, `harm_dist`, `harm_alias_dist` |

It was built for HARPS-RVBank (Perdelwitz et al. 2024) but works on any nightly RV series
with instrument labels. It also contains a simulation engine (planets and FF′ activity
injected into real sampling and noise) and classifiers trained on those simulations.

## Install and test

```bash
pip install -e ".[test]"
pytest              # 26 tests: periodogram algebra, FAP calibration, Keplerian prewhitening,
                    # GP derivative covariance, grouped cross-validation, CLI
```

## Use

```bash
python scripts/load_rvbank.py table4.dat.gz rvbank.parquet     # CDS J/A+A/683/A125
rvvet vet --rvbank rvbank.parquet --star HD297396 --period 4.26837 --trend 2
```

```python
import pandas as pd, rvvet
df = pd.read_parquet("rvbank.parquet")
s = rvvet.load_star(df, "GJ581", clip_sigma=15)
r = rvvet.vet(s, period=66.8, known_periods=[5.3686, 12.9211, 3.1481], trend=2)
print(r["log10_fap"], r["ind_max_dchi2"], r["harm_dist"])
```

## Reproduce the paper

```bash
python scripts/run_sims.py sims 16000 2 20260929      # labelled simulations on 260 RVBank stars
python scripts/run_benchmark.py                        # 46 published signals (benchmark_literature.csv)
python scripts/analyze.py                              # numbers.json, tables and figures
```

Every run is seeded; `rvvet vet` writes a provenance block (version, source hash, input file).

## Design notes

* The periodogram removes per-label offsets by projecting onto the complement of the
  whitened label indicators, so each frequency costs O(N · labels), and it evaluates many
  simulated data sets in one matrix product.
* Known companions are removed with Keplerian fits (eccentricity and periastron by grid and
  refinement; the orbit is linear in K cos ω and K sin ω at fixed e and t_p).
* Classifiers are validated with folds grouped by host star, so no star is in both training
  and test data.

MIT licence.
