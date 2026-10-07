# PREREG-T1: data-handling decisions made after the archive headers were read, before any model was fitted

Written 2026-10-04 (overnight run). The velocities had been extracted and displayed as header values,
but no fit, periodogram, phase fold or comparison with the ephemeris had been made.

1. **Source of the velocities.** ESO phase-3 ancillary CCF products, read anonymously from the ESO
   archive: ESPRESSO and NIRPS `HIERARCH ESO QC CCF RV` / `QC CCF RV ERROR`; HARPS `HIERARCH ESO
   DRS CCF RVC` (drift-corrected) / `DRS CCF NOISE` from the CCF file inside the HARPS ancillary tar.
2. **ESPRESSO product choice.** 2023–2024 products have only `CCF_A`; 2025 products have `CCF_A` and
   `CCF_TELL_CORR_A`. `CCF_A` is used for every ESPRESSO epoch so one product type spans the series.
   NIRPS products have only `CCF_TELL_CORR_A`, which is used.
3. **A different object.** One ESPRESSO product in the search cone (ADP.2024-07-05T16:02:51.937, two
   exposures) has RV = −106.3 km/s with a G2 mask, against +69.87 km/s for GJ 902. It is another star,
   not a spectrum of the target. Rule: drop spectra more than 1 km/s from the target's median RV.
4. **Not yet public.** Two NIRPS products of 2026-05-22 returned no header; excluded under data rule 4
   (missing keyword).
5. **HD 58489 mask change.** Ten 2023 February HARPS spectra were reduced with the G2 mask and the rest
   with K5. A CCF mask change shifts the velocity zero point, so `HARPS_G2` and `HARPS_K5` get separate
   offsets. The literal pre-registered model (one HARPS offset) is also run and reported.
6. **Times.** ESPRESSO and NIRPS give `QC BJD`. The HARPS CCF header gives no BJD, so BJD_TDB is computed
   from MJD-OBS + EXPTIME/2 with an astropy barycentric correction for La Silla.
7. **Overlap with RVBank.** Spectra within 0.5 d of an RVBank epoch are dropped (data rule 1).
