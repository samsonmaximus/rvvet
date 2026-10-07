# rvvet — vetting radial-velocity planet signals in long archival time series

`rvvet` runs a ladder of interpretable tests on a periodic signal in a radial-velocity (RV)
time series and returns one feature per question a referee asks of an archival planet
candidate:

| Rung | Question | Features |
|---|---|---|
| Detection | Is the peak significant for this sampling? | `dchi2` (likelihood ratio, jitter profiled), `log10_fap` (Baluev 2008 approximation), `log10_p_single` |
| Amplitude | Is the semi-amplitude large compared with errors and scatter? | `snr_K`, `K_over_rms` |
| Period | Is it a window alias of another peak in the search band? | `alias_margin`, `alias_period` (day, month, year and the star's own window peaks) |
| Stationarity | Does it keep amplitude and phase? | `half_phase_z`, `half_amp_z`, `half_imbalance`, `block_phase_p`, `block_amp_p`, `block_phase_rms`, `growth_rho`, `apod_gain` |
| Activity | Do indicators vary at this period, or does it sit on a rotation harmonic? | `ind_max_dchi2`, `ind_max_absr`, `act_log10_fap`, `harm_dist`, `harm_alias_dist` |

The a-priori rule of the paper (`results/RULES_FROZEN.md`) is in `rvvet.rules`.

It was built for HARPS-RVBank (Perdelwitz et al. 2024) but works on any nightly RV series
with instrument labels. It also contains a simulation engine (planets and FF′ activity
injected into real sampling and noise) and classifiers trained on those simulations.

## Install and test

```bash
pip install -e ".[test]"
pytest              # 40 tests (see the paper, Sect. 8.1, for which compare with an independent calculation)
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
print(rvvet.rule_pass(pd.DataFrame([r])).iloc[0])
```

## Reproduce the paper (about four hours on two cores)

Use the pinned environment in `../requirements-paper.txt` (Python 3.13). In it, the steps below
regenerate the simulated cases, the benchmark features and every number, table and figure of
the paper exactly. Newer library versions give slightly different numbers: scikit-learn 1.9
changes the classifier outputs (`results/sklearn19_sensitivity.json`), and scipy 1.18 changes
recomputed features in the fifth decimal place for simulated cases and by a few per cent for HD 10180 d.
To skip the four-hour runs, `python analyze.py` alone rebuilds everything from the stored
simulations and features (about a minute).

```bash
cd scripts
python run_sims.py ../../sims 16000 2 20260929                       # labelled simulations on 260 RVBank stars
python fap_calibration.py ../../results/fap_calibration.parquet 40 2 # noise-only series, two noise models
python check_sims_consistency.py 20                                  # regenerate 20 cases, compare
python run_benchmark.py                                              # 46 published signals, three period windows
python analyze.py                                                    # numbers.json, figures, and the paper's
                                                                     # numbers.tex (macros) and tab_*.tex (tables)
```

Every number in the text of the paper is a macro in `paper/numbers.tex`, written by
`analyze.py`; every table except the feature definitions is written by it too. The numbers
of Sect. 6.5 are in `paper/numbers_forward.tex`, written by `../forward_test/timesplit.py`, and
those on software versions in `paper/numbers_versions.tex`, written by
`version_sensitivity.py`. Every run is
seeded; `rvvet vet` writes a provenance block (version, source hash, input file).

## Changes in 0.3.1 (after a third review)

* Indicators are clipped at 15 robust σ before and during the detrending fit (a least-squares
  trend tilted by one gross outlier left a spurious long-period signal).
* The rotation proxy is the highest local maximum of the band, excluding 1/T around one and two
  cycles per year (seasonal sampling put spurious power at half a year).

## Changes in 0.3 (after a second review)

* The window around a claimed period is capped at ±0.5/T (0.2 let a second refinement reach
  ±0.6/T); `vet(..., period_window=)` sets it, and the offset and an edge flag are reported.
* Indicators are detrended with the same per-era offsets and polynomial trend as the
  velocities before the indicator rung and the rotation proxy (0.2 removed only per-era medians,
  so the proxy fired on slow variations such as magnetic cycles).

## Changes in 0.2 (after an independent review of 0.1)

* Nights run from local noon at La Silla (0.1 started them at 0 h UT, which split some nights
  and merged the morning of one night with the evening of the next).
* Detection statistic: the likelihood ratio with the jitter rescaled under the signal model
  (0.1 held the jitter at its planet-free value, which deflates real signals and made the
  Baluev approximation look conservative by a factor of several).
* Alias rung: candidates outside the search band are no longer compared, and a candidate that
  refines onto the peak itself is dropped (0.1 compared planets with their ~1-d mirrors).
* Stationarity: blocks and halves are compared in (a, b) space against their generalised
  least-squares mean, split into phase and amplitude parts, each with n_b − 1 degrees of freedom.
* Rotation proxy: 2.5–200 d, Bonferroni-corrected for the number of indicators searched.
* Simulations: planet and activity amplitudes both scale with the star's scatter (not with the
  number of epochs); rotation 3–150 d, spot evolution 1–30 rotations; each indicator has its own
  amplitude and phase lag, and a fifth of activity cases leave no trace in the indicators; the
  simulated series get the same trend removal and outlier clip as real stars.
* `log_n` and `log_ncyc` are reported but no longer used by the classifiers.

## Design notes

* The periodogram removes per-label offsets by projecting onto the complement of the
  whitened label indicators, so each frequency costs O(N · labels), and it evaluates many
  simulated data sets in one matrix product.
* Known companions are removed with Keplerian fits (eccentricity and periastron by grid and
  refinement; the orbit is linear in K cos ω and K sin ω at fixed e and t_p).
* Classifiers are validated with folds grouped by host star (`rvvet.learn.grouped_folds`), so
  no star is in both training and test data; a unit test checks it.

MIT licence.
