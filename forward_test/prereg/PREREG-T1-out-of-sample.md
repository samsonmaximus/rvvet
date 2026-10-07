# PREREG-T1: out-of-sample test of two archive candidates with post-RVBank spectra

Written 2026-10-04, before any velocity taken after the HARPS-RVBank cutoff was read for either star.
What had been read at this point: ESO ObsCore metadata only (instrument, observation time, product id).
No header, spectrum or velocity of these products had been opened.

## Candidates (frozen in `out/ledger_v1.csv`, SHA-256 in `MANIFEST.sha256`)

| ledger id | star | P (d) | K (m/s) | T_max (BJD) | source |
|---|---|---|---|---|---|
| RVL-006 | GJ 902 (HD 222237) | 36.0966 ± 0.0362 | 1.90 ± 0.41 | 2456214.141 ± 1.324 | rvvet 0.3.1 blind archive run, white-noise ephemeris fit |
| RVL-027 | HD 58489 | 19.5134 ± 0.0095 | 5.48 ± 1.34 | 2456990.709 ± 0.735 | same |

Why these two: they are the only open ledger candidates in the top 30 with at least 10 public
post-RVBank HARPS/ESPRESSO/NIRPS spectra in the ESO archive on 2026-10-04 (query in `power.py` inputs).

## Data rule

1. All public ESO phase-3 spectra of the star from HARPS, ESPRESSO and NIRPS with MJD > 59580,
   minus any within 0.5 d of an epoch already in HARPS-RVBank.
2. Velocity = the pipeline's drift-corrected CCF radial velocity from the product header; if no
   drift-corrected keyword exists, the CCF RV keyword. Uncertainty = the pipeline's CCF RV error
   keyword. The keyword actually used is reported.
3. Spectra are averaged per instrument per night (inverse-variance), nights from local noon.
4. No spectrum is removed for any reason other than a missing or non-finite RV/error keyword.

## Model and statistic

v_i = c_inst + b·(t_i − t̄) + A·cos(2π(t_i − T_max)/P) + noise,
with P and T_max fixed at the ledger values, one offset per instrument, one common linear trend
(the star hosts a long-period companion, HD 222237 b; the trend is kept for HD 58489 too, for one rule),
and per-instrument jitter fitted by maximum likelihood under this model.
Statistic: z = Â / σ_Â.

## Decision (fixed now)

- **Supported:** z ≥ 3 and |Â − K| < 2·sqrt(σ_Â² + σ_K²).
- **Consistent, not decisive:** 2 ≤ z < 3.
- **Refuted:** Â < K − 3·sqrt(σ_Â² + σ_K²) (the predicted amplitude is excluded).
- **Undecided:** anything else.

Secondary, reported but not decisive: a free-phase sinusoid at fixed P (phase offset from the
prediction, in cycles), and a periodogram of the new data alone.

## Power (computed from timestamps only, `power.json`)

Nominal per-epoch errors fixed before reading: ESPRESSO 0.5, HARPS 1.0 (1.5 for HD 58489), NIRPS 2.5 m/s,
each added in quadrature to the star's RVBank jitter; ephemeris uncertainty propagated by Monte Carlo.

| star | nights | σ_Â (m/s) | median expected z | P(z ≥ 3) | P(z ≥ 2) |
|---|---|---|---|---|---|
| GJ 902 | 19 ESPRESSO, 12 NIRPS, 11 HARPS | 0.49 | 3.3 | 0.61 | 0.80 |
| HD 58489 | 18 HARPS | 1.46 | 3.5 | 0.77 | 0.95 |

These assume the archive amplitude is the true amplitude. Signals selected as the strongest peak
of a noisy periodogram are biased high, so the real power is lower than shown.

## Limits stated in advance

- A "supported" result shows a coherent signal at the predicted phase in new data. It does not by
  itself separate a planet from long-lived activity at that period.
- The timestamp of this document is a local git commit, not an external timestamp. To make it
  independently verifiable, the SHA-256 in `MANIFEST.sha256` should be posted publicly
  (GitHub commit or a public post) before anyone else reads the test result.
