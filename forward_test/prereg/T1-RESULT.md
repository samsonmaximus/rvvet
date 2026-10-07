# PREREG-T1 result (run 2026-10-04, overnight)

Rule frozen in commit `0fba0be` (08:13 MDT); data decisions in `2b5a4b0` (09:09 MDT), before any fit.
Velocities: ESO phase-3 CCF products of 2022–2026, read anonymously from the ESO archive
(`t1_all_velocities.csv`, one row per exposure, file name included).

| | GJ 902 (RVL-006) | HD 58489 (RVL-027) |
|---|---|---|
| Prediction (from 2003–2021 HARPS) | P = 36.097 d, K = 1.90 ± 0.41 m/s | P = 19.513 d, K = 5.48 ± 1.34 m/s |
| New data | 41 nights: 19 ESPRESSO, 11 HARPS, 11 NIRPS | 18 nights HARPS (10 G2-mask, 8 K5-mask) |
| Amplitude at the predicted phase | **0.20 ± 0.37 m/s** | **4.02 ± 1.02 m/s** |
| z | 0.54 | 3.96 |
| **Pre-registered verdict** | **REFUTED** | **SUPPORTED** (with deviation 5) |
| Literal model (one HARPS offset) | same | UNDECIDED (z = 0.33; the mask offset is absorbed as 8.5 m/s jitter) |

Figure: `fig_t1.png`.

## Calibration (computed after the verdicts; not part of the rule)

- The formal z is overconfident: in white-noise simulations with the same dates, errors and fitted
  jitters, z has a standard deviation of 1.4, not 1. Future tests should calibrate z this way.
- **GJ 902:** if the predicted signal were real, 0 of 1000 simulations give z as low as observed
  (median 6.1). Without a signal, 34% give z ≥ 0.54. The new data are consistent with no signal at
  36.1 d. The archival signal did not persist as a stable orbit.
- **HD 58489:** without a signal, 0.6% of simulations give z ≥ 3.96 (about 2.5σ, not 4σ). With the
  predicted signal, 5% give z this low or lower, so the amplitude is on the low side, as expected for
  a signal selected as a periodogram maximum. A template at a random phase does as well in 17% of
  phases. The K5 spectra alone (no deviation needed) give 5.2 ± 2.0 m/s at the predicted phase.
  The new data alone do not single out 19.5 d: 13% of periods between 2 and 150 d fit them better.

## Reading

- **GJ 902 b at 36.1 d is not a planet at the archived amplitude.** The ladder passed it (trees 0.87);
  the prospective test removed it. This is the first ledger signal closed by new data, and it is a
  ladder false positive worth stating in the methods paper.
- **HD 58489 at 19.5 d passed its first prospective test, weakly.** Ten nights in February 2023 trace
  the predicted descending half of the curve, and the scattered 2022–2024 nights agree. It is not yet
  a detection: about 2.5σ after calibration, one instrument, and a declared deviation. It is now the
  ledger's best-supported open signal after HD 297396 and should get a dossier and follow-up.

## Stated limits

- Deviation 5 (separate offsets for the two CCF masks) was decided after the velocities were displayed
  but before any fit; it is the standard treatment and the literal model is reported.
- HARPS DRS 3.8 velocities from ESO are not nightly zero-point corrected like RVBank; this adds about
  1 m/s of night-to-night noise, absorbed by the fitted jitter.
- The test was run by the same agent that built the ledger; the frozen code and data allow anyone to
  rerun it: `python run_test_t1.py HD58489 rv_hd58489.csv`.
