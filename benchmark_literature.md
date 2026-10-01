# Literature benchmark: published RV signals in HARPS-RVBank

Labelled set of periodic radial-velocity signals that were once claimed or proposed as planets, around stars in HARPS-RVBank (Perdelwitz et al. 2024) with at least 20 nights of data. Each label records what later peer-reviewed work concluded. Built 2026-09-29; the machine-readable version is `benchmark_literature.csv` (same rows, same order).

## Counts

| Label | N | Meaning |
|---|---|---|
| REFUTED | 17 | Later peer-reviewed work attributed the signal to activity/rotation, aliasing/window function, or failed to recover it; prevailing view. |
| UPHELD_INDEPENDENT | 19 | Confirmed by evidence independent of HARPS RVs (transits, another spectrograph with an independent data set). |
| UPHELD_HARPS | 7 | Accepted and not contested, but supported mainly by HARPS RVs. |
| DISPUTED | 3 | Conflicting published conclusions, no prevailing view. Exclude from headline metrics. |
| **Total** | **46** | |

## How to read the table

- **P, K, e** are the values published for the signal as claimed. For UPHELD rows they come from the paper named in "params from" (usually the discovery paper; a later definitive paper where noted). e = 0 means the orbit was fixed circular in that fit; blank means not published or only an upper limit (see notes).
- **Other signals** are periods (days) of other accepted signals in the same system that must be removed before testing the row's signal. For refuted-signal rows they list only accepted planets.
- **nights / baseline / median error** are from `data/rvbank_all_stars.csv`. **sep** is the offset (arcmin) between the RVBank position and the NASA Exoplanet Archive position of the host; blank = matched by name only (no archive position available; see notes).
- **HARPS in discovery**: yes / no / partial (HARPS archival data used in the discovery analysis but the detection was driven by another instrument).

## REFUTED (17)

| # | Signal | Host | RVBank star (nights; sep') | P (d) | K (m/s) | e | P_rot (d) [ref] | Other signals P (d) | Discovery | Verdict | Why | HARPS in disc. | Params from | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | GJ 581 d | GJ 581 | GJ581 (243; 0.28) | 66.8 | 2.63 | 0.38 | 130 [Robertson+2014 (Halpha); 132.5 in von Stauffenberg+2024] | 5.3686; 12.9211; 3.1481 | Udry+2007 (as 83.6 d); Mayor+2009a (revised to 66.8 d) | Robertson+2014; von Stauffenberg+2024 | Period is ~half the 130-d rotation period; RVs anti-correlate with Halpha and the signal loses significance after activity correction; dismissed as activity in the CARMENES+HARPS+HIRES reanalysis. | yes | Mayor+2009a | Originally reported at 83.6 d (1-yr alias). |
| 2 | GJ 581 g | GJ 581 | GJ581 (243; 0.28) | 36.562 | 1.29 | 0 | 130 [Robertson+2014] | 5.3686; 12.9211; 3.1481 | Vogt+2010 | Robertson+2014; von Stauffenberg+2024 | No trace of the signal remains after correcting the RVs for the Halpha activity correlation; later data support only planets b, c, e. | yes | Vogt+2010 | e fixed at 0 in discovery fit; discovery combined HIRES+HARPS. |
| 3 | GJ 581 f | GJ 581 | GJ581 (243; 0.28) | 433 | 1.3 | 0 | 130 [Robertson+2014] | 5.3686; 12.9211; 3.1481 | Vogt+2010 | Robertson+2014; von Stauffenberg+2024 | Not supported by subsequent analyses (Robertson+2014: now believed not to exist); CARMENES+HARPS+HIRES reanalysis finds only three planets (b, c, e). | yes | Vogt+2010 | e fixed at 0 in discovery fit. |
| 4 | Kapteyn b | Kapteyn's star (GJ 191) | GJ191 (217; 0.34) | 48.616 | 2.25 | 0.21 | 143; 124.7 [Robertson+2015; Bortle+2021] |  | Anglada-Escude+2014 | Robertson+2015; Bortle+2021 | Period is 1/3 of the 143-d rotation period seen in Halpha (Robertson+2015); a joint GP on RVs and Halpha explains the RVs with rotation alone (Bortle+2021). | yes | Anglada-Escude+2014 | The discovery team disputed the activity interpretation (arXiv:1506.09072; journal version not verified here). |
| 5 | Kapteyn c | Kapteyn's star (GJ 191) | GJ191 (217; 0.34) | 121.54 | 2.27 | 0.23 | 124.7 [Bortle+2021] |  | Anglada-Escude+2014 | Bortle+2021 | Lies close to the 124.7-d rotation period from a joint GP on RVs and Halpha; Bortle+2021 attribute both reported planets to rotation/activity. | yes | Anglada-Escude+2014 | Weakest REFUTED case: single refuting paper; NASA Exoplanet Archive still lists Kapteyn c. |
| 6 | HD 41248 b | HD 41248 | HD41248 (164; name only) | 18.357 | 2.93 | 0.15 | ~25 [Faria+2020 (TESS 24-25 d; GP 25.6 d)] |  | Jenkins+2013 | Santos+2014; Faria+2020 | Not recovered in 162 additional HARPS RVs (Santos+2014); a GP activity model explains all RV variation in HARPS+ESPRESSO data (Faria+2020). | yes | Jenkins+2013 |  |
| 7 | HD 41248 c | HD 41248 | HD41248 (164; name only) | 25.648 | 1.84 | 0.0 | ~25 [Faria+2020 (TESS 24-25 d; GP 25.6 d)] |  | Jenkins+2013 | Santos+2014; Faria+2020 | Coincides with the ~25-d stellar rotation period (rotational modulation of active regions per Santos+2014; TESS photometry and GP per Faria+2020). | yes | Jenkins+2013 |  |
| 8 | HD 26965 b | HD 26965 (omicron2 Eri) | HD26965 (103; 0.53) | 42.38 | 1.81 | 0.04 | ~42 [Burrows+2024; Laliotis+2023] |  | Ma+2018 | Laliotis+2023; Burrows+2024 | Period matches the ~42-d rotation; NEID line-by-line RVs show amplitude depending on line depth (convective-blueshift suppression), inconsistent with a Keplerian; Laliotis+2023 also class it as activity. | yes | Ma+2018 |  |
| 9 | Barnard b (233 d) | Barnard's star (GJ 699) | GJ699 (209; 0.48) | 232.8 | 1.2 | 0.32 | 143.7 [Lubin+2021 (GP on Halpha); 140+-10 in Ribas+2018] | 3.1533; 4.1244; 2.3402; 6.7392 | Ribas+2018 | Lubin+2021; Gonzalez Hernandez+2024 | Explained as a one-year alias of the ~145-d rotation signal, transient in time (Lubin+2021); not supported by ESPRESSO RVs (Gonzalez Hernandez+2024). | yes | Ribas+2018 |  |
| 10 | GJ 832 c | GJ 832 | HD204961 (180; 0.07) | 35.68 | 1.79 | 0.18 | 37.5 [Gorrini+2022] | 3657 | Wittenmyer+2014 | Gorrini+2022 | Close to the 37.5-d rotation period from activity indicators; signal not coherent in time and Bayesian model comparison prefers no second Keplerian. | yes | Wittenmyer+2014 |  |
| 11 | AD Leo b | AD Leo (GJ 388) | GJ388 (124; name only) | 2.22579 | 19.11 | 0.015 | 2.23 [Tuomi+2018 (photometric)] |  | Tuomi+2018 | Carleo+2020 | Period equals the 2.23-d photometric rotation period; simultaneous optical+NIR (GIARPS) RVs do not confirm the signal, which is attributed to activity. | yes | Tuomi+2018 | Easy (large-K) refuted control; discovery paper already posed rotation vs. spin-orbit-resonant planet. |
| 12 | alpha Cen Bb | alpha Cen B (GJ 559 B) | GJ559B (367; 0.0) | 3.2357 | 0.51 | 0 |  |  | Dumusque+2012 | Rajpaul+2016 | Produced by the window function of the HARPS sampling: the same ~3.24-d, ~0.5 m/s "detection" is recovered from simulated data with identical time stamps and no planet. | yes | Dumusque+2012 (as quoted by Rajpaul+2016) | Circular orbit in discovery fit. Binary motion around alpha Cen A must be modelled as a long-term trend. |
| 13 | GJ 176 b (HET, 10.24 d) | GJ 176 | HD285968 (106; 0.08) | 10.2369 | 11.62 | 0 | 39 [Forveille+2009] | 8.7836 | Endl+2008 | Forveille+2009 | No signal at 10.24 d in 57 more precise HARPS RVs; the real planet is at 8.78 d and the HET detection was judged spurious. | no | Endl+2008 (circular fit) | Discovery used HET/HRS only; eccentric fit gave e=0.23. |
| 14 | GJ 667 C d | GJ 667 C | GJ667 (268; 0.05) | 91.61 | 1.52 | 0.03 | ~105 [Robertson & Mahadevan 2014 (CCF FWHM)] | 7.2004; 28.140 | Anglada-Escude+2013 | Robertson & Mahadevan 2014 | Artifact of the ~105-d rotation seen in the CCF FWHM; disappears after activity correction while b and c remain. | yes | Anglada-Escude+2013 | Not listed in the NASA Exoplanet Archive. Feroz & Hobson 2014 report only "hints" of a 91-d signal. |
| 15 | HD 20794 c (40 d; Pepe+2011) | HD 20794 | HD20794 (620; 0.11) | 40.114 | 0.56 | 0 | 38.8 [Nari+2025 (BIS; 35.0 d in FWHM)] | 18.314; 89.67; 647.5 | Pepe+2011 | Nari+2025 | Compatible with the 38.8-d rotation period seen in the bisector span; attributed to stellar activity in the HARPS+ESPRESSO reanalysis. | yes | Pepe+2011 | Naming changed: Nari+2025 call the 89.7-d planet "c" and a 647.5-d planet "d". e fixed at 0 in discovery fit. |
| 16 | HD 85512 b | HD 85512 | HD85512 (587; name only) | 58.43 | 0.769 | 0.11 | 51.2 [Laliotis+2023 (47.13+-6.98 from RHK in Pepe+2011)] |  | Pepe+2011 | Laliotis+2023 | An archival multi-instrument analysis recovers a 51.2-d signal instead of 58.4 d and attributes it to stellar rotation; NASA Exoplanet Archive now flags the planet as a false positive. | yes | Pepe+2011 |  |
| 17 | tau Ceti b (13.97 d; Tuomi+2013) | tau Ceti (HD 10700) | HD10700 (592; 0.28) | 13.965 | 0.64 | 0.16 |  | 20.00; 49.41; 636.13 | Tuomi+2013a | Feng+2017 | With more HARPS data and a wavelength-dependent noise model, the 14-d signal weakens when the 20-d signal is removed but not vice versa, indicating a non-Keplerian origin; not retained. | yes | Tuomi+2013a | Verdict paper shares authors with the discovery paper. Other periods are the Feng+2017 candidates listed by the NASA Exoplanet Archive (unconfirmed). |

## UPHELD_INDEPENDENT (19)

| # | Signal | Host | RVBank star (nights; sep') | P (d) | K (m/s) | e | P_rot (d) [ref] | Other signals P (d) | Discovery | Verdict | Why | HARPS in disc. | Params from | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | HD 136352 b | HD 136352 (nu2 Lupi) | HD136352 (244; 0.24) | 11.5824 | 1.59 | 0.14 |  | 27.5821; 107.5983 | Udry+2019 | Kane+2020 | Transits at the RV period detected by TESS. | yes | Udry+2019 |  |
| 2 | HD 136352 c | HD 136352 (nu2 Lupi) | HD136352 (244; 0.24) | 27.5821 | 2.65 | 0.04 |  | 11.5824; 107.5983 | Udry+2019 | Kane+2020 | Transits at the RV period detected by TESS. | yes | Udry+2019 |  |
| 3 | HD 136352 d | HD 136352 (nu2 Lupi) | HD136352 (244; 0.24) | 107.5983 | 1.35 | 0.09 |  | 11.5824; 27.5821 | Udry+2019 | Delrez+2021 | Transit at the RV period detected by CHEOPS. | yes | Udry+2019 |  |
| 4 | pi Men c | pi Men (HD 39091) | HD39091 (209; 0.16) | 6.2679 | 1.58 | 0 |  | 2088.8; 124.64 | Huang+2018; Gandolfi+2018 | Huang+2018; Gandolfi+2018 | TESS transits at 6.27 d; the RV signal is recovered in archival HARPS (and UCLES) data. | yes | Huang+2018 | Transit-first discovery. pi Men b (P~2089 d, K~196 m/s, e~0.64) must be removed first; d (124.6 d) as listed in the NASA Exoplanet Archive. |
| 5 | GJ 357 b | GJ 357 | GJ357 (53; 0.2) | 3.93072 | 1.52 |  | 78 [Luque+2019 (photometric GP)] | 9.1247; 55.661 | Luque+2019 | Luque+2019 | TESS transits at 3.93 d. | yes | Luque+2019 | Transit-first discovery; RVs from HIRES, UVES, HARPS (53 archival), PFS, CARMENES. c and d are RV-only. |
| 6 | GJ 1132 b | GJ 1132 | GJ1132 (125; 0.29) | 1.62893 | 2.76 | 0 |  | 8.929 | Berta-Thompson+2015 | Berta-Thompson+2015 | Transits found by MEarth-South; HARPS RVs gave the mass. | yes | Berta-Thompson+2015 | Transit-first discovery; e fixed at 0. Other period is GJ 1132 c as listed in the NASA Exoplanet Archive. |
| 7 | HD 15337 b | HD 15337 (TOI-402) | HD15337 (116; 0.11) | 4.75615 | 3.08 | 0.09 |  | 17.1784 | Gandolfi+2019; Dumusque+2019 | Gandolfi+2019; Dumusque+2019 | TESS transits at the RV period. | yes | Gandolfi+2019 | Transit-first discovery. |
| 8 | HD 15337 c | HD 15337 (TOI-402) | HD15337 (116; 0.11) | 17.1784 | 2.16 | 0.05 |  | 4.75615 | Gandolfi+2019; Dumusque+2019 | Gandolfi+2019; Dumusque+2019 | TESS transits at the RV period. | yes | Gandolfi+2019 | Transit-first discovery. |
| 9 | Proxima b | Proxima Cen (GJ 551) | GJ551 (227; 0.17) | 11.186 | 1.38 |  | 83 [Anglada-Escude+2016] | 5.122 | Anglada-Escude+2016 | Suarez Mascareno+2020; Suarez Mascareno+2025 | Detected independently in ESPRESSO data alone (and in NIRPS data alone). | yes | Anglada-Escude+2016 | e<0.35 (upper limit). Discovery used HARPS + UVES. Proxima c (~1900 d) omitted: evidence inconclusive in Suarez Mascareno+2025. |
| 10 | Proxima d | Proxima Cen (GJ 551) | GJ551 (227; 0.17) | 5.122 | 0.39 | 0.04 | 83 [Anglada-Escude+2016] | 11.186 | Faria+2022 | Faria+2022; Suarez Mascareno+2025 | Discovered in ESPRESSO data; evidence in NIRPS data and confirmed with NIRPS plus simultaneous and archival HARPS (Suarez Mascareno+2025). | no | Faria+2022 | K~0.4 m/s: effectively undetectable in HARPS alone; hard case. |
| 11 | GJ 581 b | GJ 581 | GJ581 (243; 0.28) | 5.3686 | 12.3 | 0.0342 | 130 [Robertson+2014] | 12.9211; 3.1481 | Bonfils+2005 | Rosenthal+2021; von Stauffenberg+2024 | Recovered in HIRES/APF/Lick-only data (California Legacy Survey) and in CARMENES-only data. | yes | von Stauffenberg+2024 | Easy (large-K) control. |
| 12 | GJ 581 c | GJ 581 | GJ581 (243; 0.28) | 12.9211 | 3.1 | 0.032 | 130 [Robertson+2014] | 5.3686; 3.1481 | Udry+2007 | Rosenthal+2021; von Stauffenberg+2024 | Recovered in HIRES/APF/Lick-only data (California Legacy Survey) and in CARMENES-only data. | yes | von Stauffenberg+2024 |  |
| 13 | GJ 436 b | GJ 436 | GJ436 (137; 0.17) | 2.6441 | 18.1 | 0.12 |  |  | Butler+2004 | Gillon+2007 | Discovered with Keck/HIRES; transits detected at the RV period. | no | Butler+2004 | Easy (large-K) control. |
| 14 | GJ 876 b | GJ 876 | GJ876 (250; 0.1) | 60.85 | 239 | 0.27 |  | 30.088; 1.9378; 124.26 | Marcy+1998 | Marcy+1998; Rosenthal+2021 | Discovered with Lick/Keck spectrographs, independent of HARPS; recovered in the HIRES/APF California Legacy Survey. | no | Marcy+1998 | Trivial control (K~210-240 m/s). Other periods are planets c, d, e as listed in the NASA Exoplanet Archive; b and c are in 2:1 resonance. |
| 15 | HD 1461 b | HD 1461 | HD1461 (275; 0.1) | 5.77142 | 2.32 | 0.062 |  | 13.5052 | Rivera+2010 | Rivera+2010; Rosenthal+2021 | Discovered with Keck/HIRES (independent of HARPS) and recovered in HIRES/APF-only data; also retained with HARPS (Diaz+2016). | no | Rosenthal+2021 |  |
| 16 | HD 1461 c | HD 1461 | HD1461 (275; 0.1) | 13.5052 | 1.49 | 0.305 |  | 5.77142 | Diaz+2016 | Rosenthal+2021 | Recovered in HIRES/APF/Lick-only data (California Legacy Survey, P=13.504 d). | yes | Diaz+2016 | Diaz+2016 note the period is close to the first harmonic of the estimated rotation period. |
| 17 | HD 192310 b | HD 192310 (GJ 785) | GJ785 (434; 0.04) | 74.39 | 4.07 | 0.3 |  | 525.8 | Howard+2011 (as Gl 785 b); Pepe+2011 | Howard+2011; Pepe+2011 | Detected independently with Keck/HIRES (Howard+2011) and HARPS (Pepe+2011); also recovered in the California Legacy Survey. | no | Howard+2011 | HARPS detection (Pepe+2011: P=74.72 d, K=3.00 m/s, e=0.13) was simultaneous. Other period is HD 192310 c (Pepe+2011). |
| 18 | GJ 176 b | GJ 176 | HD285968 (106; 0.08) | 8.7836 | 4.12 | 0 | 39 [Forveille+2009] |  | Forveille+2009 | Rosenthal+2021; Trifonov+2018 | Recovered in HIRES/APF/Lick-only data (California Legacy Survey, P=8.775 d); orbit updated with CARMENES RVs. | yes | Forveille+2009 | e fixed at 0 in discovery fit. |
| 19 | Barnard b (3.15 d) | Barnard's star (GJ 699) | GJ699 (209; 0.48) | 3.1533 | 0.55 | 0.16 | 143.7 [Lubin+2021] | 4.1244; 2.3402; 6.7392 | Gonzalez Hernandez+2024 | Basant+2025 | Confirmed by MAROON-X data alone. | partial | Gonzalez Hernandez+2024 (e from NASA Exoplanet Archive) | Detection driven by ESPRESSO; archival HARPS, HARPS-N and CARMENES included in the analysis. K~0.5 m/s: hard case. Other periods are Basant+2025 planets c, d, e. |

## UPHELD_HARPS (7)

| # | Signal | Host | RVBank star (nights; sep') | P (d) | K (m/s) | e | P_rot (d) [ref] | Other signals P (d) | Discovery | Verdict | Why | HARPS in disc. | Params from | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | HD 10180 d | HD 10180 | HD10180 (269; 0.04) | 16.3579 | 2.86 | 0.088 |  | 5.75979; 49.745; 122.76; 601.2; 2222 | Lovis+2011 | Lovis+2011 | Member of the HARPS HD 10180 multi-planet system; accepted and not contested, no independent detection. | yes | Lovis+2011 |  |
| 2 | HD 47186 b | HD 47186 | HD47186 (145; 0.09) | 4.0845 | 9.12 | 0.038 |  | 1353.6 | Bouchy+2009 | Bouchy+2009 | HARPS hot Neptune; accepted and not contested, no independent detection. | yes | Bouchy+2009 | Easy-ish control (K~9 m/s). |
| 3 | HD 181433 b | HD 181433 | HD181433 (189; 0.09) | 9.3743 | 2.94 | 0.396 |  | 1014.5; 7012 | Bouchy+2009 | Horner+2019 | Retained in the later re-analysis and new orbital solution of the system (P=9.3745 d, K=2.70 m/s). | yes | Bouchy+2009 | Other periods are Horner+2019 values for c and d. |
| 4 | GJ 163 c | GJ 163 | GJ163 (205; 0.09) | 25.63058 | 2.75 | 0.099 |  | 8.63182; 603.95 | Bonfils+2013 | Bonfils+2013 | Member of the HARPS GJ 163 system; accepted and not contested, no independent detection. | yes | Bonfils+2013 |  |
| 5 | HD 40307 b | HD 40307 | GJ2046 (260; 0.06) | 4.3115 | 1.79 | 0.168 |  | 9.6207; 20.4185; 51.56 | Mayor+2009b | Diaz+2016 | Confirmed in an 8-yr Bayesian re-analysis of more HARPS data including activity terms. | yes | Diaz+2016 | RVBank lists HD 40307 as GJ2046 (same position to 3 arcsec). |
| 6 | GJ 581 e | GJ 581 | GJ581 (243; 0.28) | 3.1481 | 1.8 | 0.012 | 130 [Robertson+2014] | 5.3686; 12.9211 | Mayor+2009a | von Stauffenberg+2024 | Retained as one of the three GJ 581 planets; in CARMENES-only data it appears only as an insignificant 3.15-d residual, so support is mainly HARPS. | yes | von Stauffenberg+2024 |  |
| 7 | HD 20794 b | HD 20794 | HD20794 (620; 0.11) | 18.314 | 0.614 | 0.064 | 38.8 [Nari+2025 (BIS)] | 89.67; 647.5 | Pepe+2011 | Nari+2025 | Confirmed with HARPS+ESPRESSO, but ESPRESSO alone is insufficient (Delta lnZ=+1.7), so support is mainly HARPS. | yes | Nari+2025 | K~0.6 m/s: hard case. |

## DISPUTED (3)

| # | Signal | Host | RVBank star (nights; sep') | P (d) | K (m/s) | e | P_rot (d) [ref] | Other signals P (d) | Discovery | Verdict | Why | HARPS in disc. | Params from | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | GJ 667 C e | GJ 667 C | GJ667 (268; 0.05) | 62.24 | 0.92 | 0.02 | ~105 [Robertson & Mahadevan 2014] | 7.2004; 28.140 | Anglada-Escude+2013 | Feroz & Hobson 2014; Robertson & Mahadevan 2014 | Claimed in a HARPS+HIRES+PFS Bayesian analysis but not supported by a correlated-noise model (only b and c) or after activity correction; still listed as confirmed by the NASA Exoplanet Archive. | yes | Anglada-Escude+2013 |  |
| 2 | GJ 667 C f | GJ 667 C | GJ667 (268; 0.05) | 39.026 | 1.08 | 0.03 | ~105 [Robertson & Mahadevan 2014] | 7.2004; 28.140 | Anglada-Escude+2013 | Feroz & Hobson 2014; Robertson & Mahadevan 2014 | Claimed in a HARPS+HIRES+PFS Bayesian analysis but not supported by a correlated-noise model (only b and c) or after activity correction; still listed as confirmed by the NASA Exoplanet Archive. | yes | Anglada-Escude+2013 |  |
| 3 | HD 40307 g | HD 40307 | GJ2046 (260; 0.06) | 197.8 | 0.95 | 0.29 |  | 4.3115; 9.6207; 20.4185; 51.56 | Tuomi+2013b | Diaz+2016 | Diaz+2016 find the HARPS data not conclusive for g (and for e); the NASA Exoplanet Archive still lists g. | yes | Tuomi+2013b |  |

## RVBank matching

| RVBank star | Host | nights | baseline (d) | median error (m/s) | sep (arcmin) |
|---|---|---|---|---|---|
| GJ581 | GJ 581 | 243 | 2909 | 1.05 | 0.28 |
| GJ191 | Kapteyn's star (GJ 191) | 217 | 6592 | 1.29 | 0.34 |
| HD41248 | HD 41248 | 164 | 5175 | 1.32 | name only |
| HD26965 | HD 26965 (omicron2 Eri) | 103 | 4536 | 0.89 | 0.53 |
| GJ699 | Barnard's star (GJ 699) | 209 | 4569 | 0.95 | 0.48 |
| HD204961 | GJ 832 | 180 | 5864 | 1.05 | 0.07 |
| GJ388 | AD Leo (GJ 388) | 124 | 6294 | 1.39 | name only |
| GJ559B | alpha Cen B (GJ 559 B) | 367 | 5102 | 0.81 | 0.0 |
| HD285968 | GJ 176 | 106 | 5163 | 1.17 | 0.08 |
| GJ667 | GJ 667 C | 268 | 5572 | 1.24 | 0.05 |
| HD20794 | HD 20794 | 620 | 6630 | 0.86 | 0.11 |
| HD85512 | HD 85512 | 587 | 6553 | 0.79 | name only |
| HD10700 | tau Ceti (HD 10700) | 592 | 6628 | 0.9 | 0.28 |
| HD136352 | HD 136352 (nu2 Lupi) | 244 | 4817 | 0.9 | 0.24 |
| HD39091 | pi Men (HD 39091) | 209 | 6184 | 1.29 | 0.16 |
| GJ357 | GJ 357 | 53 | 3350 | 1.24 | 0.2 |
| GJ1132 | GJ 1132 | 125 | 745 | 1.95 | 0.29 |
| HD15337 | HD 15337 (TOI-402) | 116 | 5750 | 1.04 | 0.11 |
| GJ551 | Proxima Cen (GJ 551) | 227 | 5576 | 1.3 | 0.17 |
| GJ436 | GJ 436 | 137 | 5170 | 1.33 | 0.17 |
| GJ876 | GJ 876 | 250 | 5730 | 0.99 | 0.1 |
| HD1461 | HD 1461 | 275 | 6507 | 0.91 | 0.1 |
| GJ785 | HD 192310 (GJ 785) | 434 | 4717 | 0.81 | 0.04 |
| HD10180 | HD 10180 | 269 | 5048 | 0.96 | 0.04 |
| HD47186 | HD 47186 | 145 | 5029 | 0.9 | 0.09 |
| HD181433 | HD 181433 | 189 | 5029 | 0.92 | 0.09 |
| GJ163 | GJ 163 | 205 | 6630 | 1.56 | 0.09 |
| GJ2046 | HD 40307 | 260 | 5640 | 0.89 | 0.06 |

- HD 40307 is present in RVBank as **GJ2046** (3 arcsec from the archive position of HD 40307; GJ 2046 is an alias of HD 40307).
- alpha Cen B is present as **GJ559B** (the archive's nearby-star table lists HD 128621 = GJ 559B at the same position to <0.01 arcmin).
- GJ 832 = **HD204961**, GJ 176 = **HD285968**, HD 192310 = **GJ785**, Kapteyn's star = **GJ191**, Barnard's star = **GJ699**, Proxima = **GJ551**, AD Leo = **GJ388**; `GJ667` is at the position of GJ 667 C (0.05 arcmin).
- HD 41248, GJ388 (AD Leo) and HD 85512 were matched by exact name only: SIMBAD, VizieR and the Gaia archive refused automated access (robots.txt), and these stars have no NASA Exoplanet Archive host entry.
- Offsets up to ~0.5 arcmin are for high-proper-motion stars (Barnard, HD 26965, Kapteyn), consistent with epoch differences.

## Caveats

- **Weakest labels.** Kapteyn c (REFUTED) rests on a single paper (Bortle et al. 2021) and is still listed by the NASA Exoplanet Archive. The Kapteyn discovery team disputed the activity interpretation of Kapteyn b (arXiv:1506.09072; journal version not verified here, so it is not in the BibTeX). tau Ceti b (REFUTED) rests on Feng et al. 2017, which shares authors with the discovery paper.
- **Transit-first planets.** pi Men c, GJ 357 b, GJ 1132 b and HD 15337 b/c were found by transit surveys and then measured in RVs. They are valid "real signal present in HARPS" cases but were not RV-first claims.
- **Sub-m/s cases.** Proxima d (K~0.4 m/s), Barnard b 3.15 d (K~0.55), alpha Cen Bb (0.51), tau Ceti b (0.64), HD 20794 b/c (0.6/0.56) and HD 85512 b (0.77) are near or below the HARPS noise floor. Consider reporting them separately.
- **Naming.** HD 20794: Nari et al. 2025 renamed the 89.7-d planet "c" and added a 647.5-d "d"; the refuted row is the 40.1-d "c" of Pepe et al. 2011. GJ 176: the refuted row is the 10.24-d HET signal of Endl et al. 2008; the upheld row is the 8.78-d HARPS planet.
- **Rotation periods** are given only where a cited paper states one.

## BibTeX

Each entry was checked against the publisher page (A&A, MNRAS/OUP, Nature), Crossref or OpenAlex metadata for the DOI, and the paper content was checked on arXiv or the publisher page. Long author lists are truncated with `and others` after the names that were verified.

```bibtex
@article{Bonfils2005,
  author  = {Bonfils, X. and Forveille, T. and Delfosse, X. and Udry, S. and Mayor, M. and Perrier, C. and Bouchy, F. and Pepe, F. and Queloz, D. and Bertaux, J.-L.},
  title   = {The {HARPS} search for southern extra-solar planets. {VI}. A {Neptune}-mass planet around the nearby {M} dwarf {Gl} 581},
  journal = {Astronomy \& Astrophysics}, year = {2005}, volume = {443}, pages = {L15--L18},
  doi     = {10.1051/0004-6361:200500193}}

@article{Udry2007,
  author  = {Udry, S. and Bonfils, X. and Delfosse, X. and Forveille, T. and Mayor, M. and Perrier, C. and Bouchy, F. and Lovis, C. and Pepe, F. and Queloz, D. and Bertaux, J.-L.},
  title   = {The {HARPS} search for southern extra-solar planets. {XI}. Super-{Earths} (5 and 8 {M$_\oplus$}) in a 3-planet system},
  journal = {Astronomy \& Astrophysics}, year = {2007}, volume = {469}, pages = {L43--L47},
  doi     = {10.1051/0004-6361:20077612}}

@article{Mayor2009a,
  author  = {Mayor, M. and Bonfils, X. and Forveille, T. and Delfosse, X. and Udry, S. and Bertaux, J.-L. and Beust, H. and Bouchy, F. and Lovis, C. and Pepe, F. and Perrier, C. and Queloz, D. and Santos, N. C.},
  title   = {The {HARPS} search for southern extra-solar planets. {XVIII}. An {Earth}-mass planet in the {GJ} 581 planetary system},
  journal = {Astronomy \& Astrophysics}, year = {2009}, volume = {507}, pages = {487--494},
  doi     = {10.1051/0004-6361/200912172}}

@article{Mayor2009b,
  author  = {Mayor, M. and Udry, S. and Lovis, C. and Pepe, F. and Queloz, D. and Benz, W. and Bertaux, J.-L. and Bouchy, F. and Mordasini, C. and Segransan, D.},
  title   = {The {HARPS} search for southern extra-solar planets. {XIII}. A planetary system with 3 super-{Earths} (4.2, 6.9, and 9.2 {M$_\oplus$})},
  journal = {Astronomy \& Astrophysics}, year = {2009}, volume = {493}, pages = {639--644},
  doi     = {10.1051/0004-6361:200810451}}

@article{Vogt2010,
  author  = {Vogt, S. S. and Butler, R. P. and Rivera, E. J. and Haghighipour, N. and Henry, G. W. and Williamson, M. H.},
  title   = {The {Lick-Carnegie} Exoplanet Survey: A 3.1 {M$_\oplus$} Planet in the Habitable Zone of the Nearby {M3V} Star {Gliese} 581},
  journal = {The Astrophysical Journal}, year = {2010}, volume = {723}, number = {1}, pages = {954--965},
  doi     = {10.1088/0004-637X/723/1/954}}

@article{Robertson2014,
  author  = {Robertson, P. and Mahadevan, S. and Endl, M. and Roy, A.},
  title   = {Stellar activity masquerading as planets in the habitable zone of the {M} dwarf {Gliese} 581},
  journal = {Science}, year = {2014}, volume = {345}, number = {6195}, pages = {440--444},
  doi     = {10.1126/science.1253253}}

@article{vonStauffenberg2024,
  author  = {von Stauffenberg, A. and Trifonov, T. and Quirrenbach, A. and Reffert, S. and Kaminski, A. and Dreizler, S. and Ribas, I. and Reiners, A. and K{\"u}rster, M. and Twicken, J. D. and Rapetti, D. and Caballero, J. A. and Amado, P. J. and B{\'e}jar, V. J. S. and Cifuentes, C. and G{\'o}ngora, S. and Hatzes, A. P. and Henning, Th. and Montes, D. and Morales, J. C. and Schweitzer, A.},
  title   = {The {CARMENES} search for exoplanets around {M} dwarfs. Revisiting the {GJ} 581 multi-planetary system with new {Doppler} measurements from {CARMENES}, {HARPS}, and {HIRES}},
  journal = {Astronomy \& Astrophysics}, year = {2024}, volume = {688}, pages = {A112},
  doi     = {10.1051/0004-6361/202449375}}

@article{AngladaEscude2014,
  author  = {Anglada-Escud{\'e}, G. and Arriagada, P. and Tuomi, M. and Zechmeister, M. and Jenkins, J. S. and Ofir, A. and Dreizler, S. and Gerlach, E. and Marvin, C. J. and Reiners, A. and Jeffers, S. V. and Butler, R. P. and Vogt, S. S. and Amado, P. J. and Rodr{\'i}guez-L{\'o}pez, C. and Berdi{\~n}as, Z. M. and Morin, J. and Crane, J. D. and Shectman, S. A. and Thompson, I. B. and D{\'i}az, M. and Rivera, E. and Sarmiento, L. F. and Jones, H. R. A.},
  title   = {Two planets around {Kapteyn's} star: a cold and a temperate super-{Earth} orbiting the nearest halo red dwarf},
  journal = {Monthly Notices of the Royal Astronomical Society: Letters}, year = {2014}, volume = {443}, number = {1}, pages = {L89--L93},
  doi     = {10.1093/mnrasl/slu076}}

@article{Robertson2015,
  author  = {Robertson, P. and Roy, A. and Mahadevan, S.},
  title   = {Stellar Activity Mimics a Habitable-zone Planet around {Kapteyn's} Star},
  journal = {The Astrophysical Journal Letters}, year = {2015}, volume = {805}, number = {2}, pages = {L22},
  doi     = {10.1088/2041-8205/805/2/L22}}

@article{Bortle2021,
  author  = {Bortle, A. and Fausey, H. and Ji, J. and Dodson-Robinson, S. and Ramirez Delgado, V. and Gizis, J.},
  title   = {A {Gaussian} Process Regression Reveals No Evidence for Planets Orbiting {Kapteyn's} Star},
  journal = {The Astronomical Journal}, year = {2021}, volume = {161}, number = {5}, pages = {230},
  doi     = {10.3847/1538-3881/abec89}}

@article{Jenkins2013,
  author  = {Jenkins, J. S. and Tuomi, M. and Brasser, R. and Ivanyuk, O. and Murgas, F.},
  title   = {Two Super-{Earths} Orbiting the Solar Analog {HD} 41248 on the Edge of a 7:5 Mean Motion Resonance},
  journal = {The Astrophysical Journal}, year = {2013}, volume = {771}, number = {1}, pages = {41},
  doi     = {10.1088/0004-637X/771/1/41}}

@article{Santos2014,
  author  = {Santos, N. C. and Mortier, A. and Faria, J. P. and Dumusque, X. and Adibekyan, V. Zh. and Delgado-Mena, E. and Figueira, P. and Benamati, L. and Boisse, I. and Cunha, D. and Gomes da Silva, J. and Lo Curto, G. and Lovis, C. and Martins, J. H. C. and Mayor, M. and Melo, C. and Oshagh, M. and Pepe, F. and Queloz, D. and Santerne, A. and S{\'e}gransan, D. and Sozzetti, A. and Sousa, S. G. and Udry, S.},
  title   = {The {HARPS} search for southern extra-solar planets. {XXXV}. The interesting case of {HD} 41248: stellar activity, no planets?},
  journal = {Astronomy \& Astrophysics}, year = {2014}, volume = {566}, pages = {A35},
  doi     = {10.1051/0004-6361/201423808}}

@article{Faria2020,
  author  = {Faria, J. P. and Adibekyan, V. and Amazo-G{\'o}mez, E. M. and Barros, S. C. C. and Camacho, J. D. and Demangeon, O. and Figueira, P. and Mortier, A. and Oshagh, M. and Pepe, F. and Santos, N. C. and Gomes da Silva, J. and Costa Silva, A. R. and Sousa, S. G. and Ulmer-Moll, S. and Viana, P. T. P.},
  title   = {Decoding the radial velocity variations of {HD} 41248 with {ESPRESSO}},
  journal = {Astronomy \& Astrophysics}, year = {2020}, volume = {635}, pages = {A13},
  doi     = {10.1051/0004-6361/201936389}}

@article{Ma2018,
  author  = {Ma, B. and Ge, J. and Muterspaugh, M. and Singer, M. A. and Henry, G. W. and Gonz{\'a}lez Hern{\'a}ndez, J. I. and Sithajan, S. and Jeram, S. and others},
  title   = {The first super-{Earth} detection from the high cadence and high radial velocity precision {Dharma} Planet Survey},
  journal = {Monthly Notices of the Royal Astronomical Society}, year = {2018}, volume = {480}, number = {2}, pages = {2411--2422},
  doi     = {10.1093/mnras/sty1933}}

@article{Laliotis2023,
  author  = {Laliotis, K. and Burt, J. A. and Mamajek, E. E. and Li, Z. and Perdelwitz, V. and Zhao, J. and Butler, R. P. and Holden, B. and Rosenthal, L. and Fulton, B. J. and Feng, F. and Kane, S. R. and Bailey, J. and Carter, B. and Crane, J. D. and Furlan, E. and Gnilka, C. L. and Howell, S. B. and Laughlin, G. and Shectman, S. A. and Teske, J. K. and Tinney, C. G. and Vogt, S. S. and Wang, S. X. and Wittenmyer, R. A.},
  title   = {Doppler Constraints on Planetary Companions to Nearby Sun-like Stars: An Archival Radial Velocity Survey of Southern Targets for Proposed {NASA} Direct Imaging Missions},
  journal = {The Astronomical Journal}, year = {2023}, volume = {165}, pages = {176},
  doi     = {10.3847/1538-3881/acc067}}

@article{Burrows2024,
  author  = {Burrows, A. and Halverson, S. and Siegel, J. C. and Gilbertson, C. and Luhn, J. and Burt, J. and Bender, C. F. and Roy, A. and Terrien, R. C. and Vangstein, S. and Mahadevan, S. and Wright, J. T. and Robertson, P. and Ford, E. B. and Stef{\'a}nsson, G. and Ninan, J. P. and Blake, C. H. and McElwain, M. W. and Schwab, C. and Zhao, J.},
  title   = {The Death of {Vulcan}: {NEID} Reveals That the Planet Candidate Orbiting {HD} 26965 Is Stellar Activity},
  journal = {The Astronomical Journal}, year = {2024}, volume = {167}, number = {5}, pages = {243},
  doi     = {10.3847/1538-3881/ad34d5}}

@article{Ribas2018,
  author  = {Ribas, I. and Tuomi, M. and Reiners, A. and Butler, R. P. and Morales, J. C. and Perger, M. and Dreizler, S. and Rodr{\'i}guez-L{\'o}pez, C. and Gonz{\'a}lez Hern{\'a}ndez, J. I. and Rosich, A. and others},
  title   = {A candidate super-{Earth} planet orbiting near the snow line of {Barnard's} star},
  journal = {Nature}, year = {2018}, volume = {563}, number = {7731}, pages = {365--368},
  doi     = {10.1038/s41586-018-0677-y}}

@article{Lubin2021,
  author  = {Lubin, J. and Robertson, P. and Stef{\'a}nsson, G. and Ninan, J. and Mahadevan, S. and Endl, M. and Ford, E. and Wright, J. T. and Beard, C. and Bender, C. and Cochran, W. D. and Diddams, S. A. and Fredrick, C. and Halverson, S. and Kanodia, S. and Metcalf, A. J. and Ramsey, L. and Roy, A. and Schwab, C. and Terrien, R.},
  title   = {Stellar Activity Manifesting at a One-year Alias Explains {Barnard} b as a False Positive},
  journal = {The Astronomical Journal}, year = {2021}, volume = {162}, number = {2}, pages = {61},
  doi     = {10.3847/1538-3881/ac0057}}

@article{GonzalezHernandez2024,
  author  = {Gonz{\'a}lez Hern{\'a}ndez, J. I. and Su{\'a}rez Mascare{\~n}o, A. and Silva, A. M. and Stefanov, A. K. and Faria, J. P. and Tabernero, H. M. and Sozzetti, A. and Rebolo, R. and others},
  title   = {A sub-{Earth}-mass planet orbiting {Barnard's} star},
  journal = {Astronomy \& Astrophysics}, year = {2024}, volume = {690}, pages = {A79},
  doi     = {10.1051/0004-6361/202451311}}

@article{Basant2025,
  author  = {Basant, R. and Luque, R. and Bean, J. L. and Seifahrt, A. and Brady, M. and Zhao, L. and Brown, N. M. and Das, T. and others},
  title   = {Four Sub-{Earth} Planets Orbiting {Barnard's} Star from {MAROON-X} and {ESPRESSO}},
  journal = {The Astrophysical Journal Letters}, year = {2025}, volume = {982}, number = {1}, pages = {L1},
  doi     = {10.3847/2041-8213/adb8d5}}

@article{Wittenmyer2014,
  author  = {Wittenmyer, R. A. and Tuomi, M. and Butler, R. P. and Jones, H. R. A. and Anglada-Escud{\'e}, G. and Horner, J. and Tinney, C. G. and Marshall, J. P. and others},
  title   = {{GJ} 832c: A Super-{Earth} in the Habitable Zone},
  journal = {The Astrophysical Journal}, year = {2014}, volume = {791}, number = {2}, pages = {114},
  doi     = {10.1088/0004-637X/791/2/114}}

@article{Gorrini2022,
  author  = {Gorrini, P. and Astudillo-Defru, N. and Dreizler, S. and Damasso, M. and D{\'i}az, R. F. and Bonfils, X. and Jeffers, S. V. and Barnes, J. R. and Del Sordo, F. and Almenara, J.-M. and others},
  title   = {Detailed stellar activity analysis and modelling of {GJ} 832. Reassessment of the putative habitable zone planet {GJ} 832c},
  journal = {Astronomy \& Astrophysics}, year = {2022}, volume = {664}, pages = {A64},
  doi     = {10.1051/0004-6361/202243063}}

@article{Tuomi2018,
  author  = {Tuomi, M. and Jones, H. R. A. and Barnes, J. R. and Anglada-Escud{\'e}, G. and Butler, R. P. and Kiraga, M. and Vogt, S. S.},
  title   = {{AD Leonis}: Radial Velocity Signal of Stellar Rotation or Spin--Orbit Resonance?},
  journal = {The Astronomical Journal}, year = {2018}, volume = {155}, number = {5}, pages = {192},
  doi     = {10.3847/1538-3881/aab09c}}

@article{Carleo2020,
  author  = {Carleo, I. and Malavolta, L. and Lanza, A. F. and Damasso, M. and Desidera, S. and Borsa, F. and Mallonn, M. and Pinamonti, M. and Gratton, R. and Alei, E. and others},
  title   = {The {GAPS} Programme at {TNG}. {XXI}. A {GIARPS} case-study of known young planetary candidates: confirmation of {HD} 285507 b and refutation of {AD Leonis} b},
  journal = {Astronomy \& Astrophysics}, year = {2020}, volume = {638}, pages = {A5},
  doi     = {10.1051/0004-6361/201937369}}

@article{Dumusque2012,
  author  = {Dumusque, X. and Pepe, F. and Lovis, C. and S{\'e}gransan, D. and Sahlmann, J. and Benz, W. and Bouchy, F. and Mayor, M. and Queloz, D. and Santos, N. and Udry, S.},
  title   = {An {Earth}-mass planet orbiting $\alpha$ {Centauri} {B}},
  journal = {Nature}, year = {2012}, volume = {491}, number = {7423}, pages = {207--211},
  doi     = {10.1038/nature11572}}

@article{Rajpaul2016,
  author  = {Rajpaul, V. and Aigrain, S. and Roberts, S.},
  title   = {Ghost in the time series: no planet for {Alpha Cen B}},
  journal = {Monthly Notices of the Royal Astronomical Society: Letters}, year = {2016}, volume = {456}, number = {1}, pages = {L6--L10},
  doi     = {10.1093/mnrasl/slv164}}

@article{Endl2008,
  author  = {Endl, M. and Cochran, W. D. and Wittenmyer, R. A. and Boss, A. P.},
  title   = {An $m \sin i$ = 24 {M$_\oplus$} Planetary Companion to the Nearby {M} Dwarf {GJ} 176},
  journal = {The Astrophysical Journal}, year = {2008}, volume = {673}, number = {2}, pages = {1165--1168},
  doi     = {10.1086/524703}}

@article{Forveille2009,
  author  = {Forveille, T. and Bonfils, X. and Delfosse, X. and Gillon, M. and Udry, S. and Bouchy, F. and Lovis, C. and Mayor, M. and Pepe, F. and Perrier, C. and Queloz, D. and Santos, N. and Bertaux, J.-L.},
  title   = {The {HARPS} search for southern extra-solar planets. {XIV}. {Gl} 176b, a super-{Earth} rather than a {Neptune}, and at a different period},
  journal = {Astronomy \& Astrophysics}, year = {2009}, volume = {493}, pages = {645--650},
  doi     = {10.1051/0004-6361:200810557}}

@article{AngladaEscude2013,
  author  = {Anglada-Escud{\'e}, G. and Tuomi, M. and Gerlach, E. and Barnes, R. and Heller, R. and Jenkins, J. S. and Wende, S. and Vogt, S. S. and Butler, R. P. and Reiners, A. and Jones, H. R. A.},
  title   = {A dynamically-packed planetary system around {GJ} 667{C} with three super-{Earths} in its habitable zone},
  journal = {Astronomy \& Astrophysics}, year = {2013}, volume = {556}, pages = {A126},
  doi     = {10.1051/0004-6361/201321331}}

@article{RobertsonMahadevan2014,
  author  = {Robertson, P. and Mahadevan, S.},
  title   = {Disentangling Planets and Stellar Activity for {Gliese} 667{C}},
  journal = {The Astrophysical Journal Letters}, year = {2014}, volume = {793}, number = {2}, pages = {L24},
  doi     = {10.1088/2041-8205/793/2/L24}}

@article{FerozHobson2014,
  author  = {Feroz, F. and Hobson, M. P.},
  title   = {Bayesian analysis of radial velocity data of {GJ}667{C} with correlated noise: evidence for only two planets},
  journal = {Monthly Notices of the Royal Astronomical Society}, year = {2014}, volume = {437}, number = {4}, pages = {3540--3549},
  doi     = {10.1093/mnras/stt2148}}

@article{Pepe2011,
  author  = {Pepe, F. and Lovis, C. and S{\'e}gransan, D. and Benz, W. and Bouchy, F. and Dumusque, X. and Mayor, M. and Queloz, D. and Santos, N. C. and Udry, S.},
  title   = {The {HARPS} search for {Earth}-like planets in the habitable zone. {I}. Very low-mass planets around {HD} 20794, {HD} 85512, and {HD} 192310},
  journal = {Astronomy \& Astrophysics}, year = {2011}, volume = {534}, pages = {A58},
  doi     = {10.1051/0004-6361/201117055}}

@article{Nari2025,
  author  = {Nari, N. and Dumusque, X. and Hara, N. C. and Su{\'a}rez Mascare{\~n}o, A. and Cretignier, M. and Gonz{\'a}lez Hern{\'a}ndez, J. I. and Stefanov, A. K. and Passegger, V. M. and Rebolo, R. and Pepe, F. and others},
  title   = {Revisiting the multi-planetary system of the nearby star {HD} 20794. Confirmation of a low-mass planet in the habitable zone of a nearby {G}-dwarf},
  journal = {Astronomy \& Astrophysics}, year = {2025}, volume = {693}, pages = {A297},
  doi     = {10.1051/0004-6361/202451769}}

@article{Tuomi2013a,
  author  = {Tuomi, M. and Jones, H. R. A. and Jenkins, J. S. and Tinney, C. G. and Butler, R. P. and Vogt, S. S. and Barnes, J. R. and Wittenmyer, R. A. and O'Toole, S. and Horner, J. and Bailey, J. and Carter, B. D. and Wright, D. J. and Salter, G. S. and Pinfield, D.},
  title   = {Signals embedded in the radial velocity noise. Periodic variations in the $\tau$ {Ceti} velocities},
  journal = {Astronomy \& Astrophysics}, year = {2013}, volume = {551}, pages = {A79},
  doi     = {10.1051/0004-6361/201220509}}

@article{Feng2017,
  author  = {Feng, F. and Tuomi, M. and Jones, H. R. A. and Barnes, J. and Anglada-Escud{\'e}, G. and Vogt, S. S. and Butler, R. P.},
  title   = {Color Difference Makes a Difference: Four Planet Candidates around $\tau$ {Ceti}},
  journal = {The Astronomical Journal}, year = {2017}, volume = {154}, number = {4}, pages = {135},
  doi     = {10.3847/1538-3881/aa83b4}}

@article{Tuomi2013b,
  author  = {Tuomi, M. and Anglada-Escud{\'e}, G. and Gerlach, E. and Jones, H. R. A. and Reiners, A. and Rivera, E. J. and Vogt, S. S. and Butler, R. P.},
  title   = {Habitable-zone super-{Earth} candidate in a six-planet system around the {K2.5V} star {HD} 40307},
  journal = {Astronomy \& Astrophysics}, year = {2013}, volume = {549}, pages = {A48},
  doi     = {10.1051/0004-6361/201220268}}

@article{Diaz2016,
  author  = {D{\'i}az, R. F. and S{\'e}gransan, D. and Udry, S. and Lovis, C. and Pepe, F. and Dumusque, X. and Marmier, M. and Alonso, R. and Benz, W. and Bouchy, F. and others},
  title   = {The {HARPS} search for southern extra-solar planets. {XXXVIII}. {Bayesian} re-analysis of three systems. New super-{Earths}, unconfirmed signals, and magnetic cycles},
  journal = {Astronomy \& Astrophysics}, year = {2016}, volume = {585}, pages = {A134},
  doi     = {10.1051/0004-6361/201526729}}

@article{Udry2019,
  author  = {Udry, S. and Dumusque, X. and Lovis, C. and S{\'e}gransan, D. and Diaz, R. F. and Benz, W. and Bouchy, F. and Coffinet, A. and Lo Curto, G. and Mayor, M. and others},
  title   = {The {HARPS} search for southern extra-solar planets. {XLIV}. Eight {HARPS} multi-planet systems hosting 20 super-{Earth} and {Neptune}-mass companions},
  journal = {Astronomy \& Astrophysics}, year = {2019}, volume = {622}, pages = {A37},
  doi     = {10.1051/0004-6361/201731173}}

@article{Kane2020,
  author  = {Kane, S. R. and Yal{\c{c}}inkaya, S. and Osborn, H. P. and Dalba, P. A. and Nielsen, L. D. and Vanderburg, A. and Mo{\v{c}}nik, T. and Hinkel, N. R. and Ostberg, C. and Esmer, E. M. and others},
  title   = {Transits of Known Planets Orbiting a Naked-eye Star},
  journal = {The Astronomical Journal}, year = {2020}, volume = {160}, number = {3}, pages = {129},
  doi     = {10.3847/1538-3881/aba835}}

@article{Delrez2021,
  author  = {Delrez, L. and Ehrenreich, D. and Alibert, Y. and Bonfanti, A. and Borsato, L. and Fossati, L. and Hooton, M. J. and Hoyer, S. and others},
  title   = {Transit detection of the long-period volatile-rich super-{Earth} $\nu^2$ {Lupi} d with {CHEOPS}},
  journal = {Nature Astronomy}, year = {2021}, volume = {5}, pages = {775--787},
  doi     = {10.1038/s41550-021-01381-5}}

@article{Huang2018,
  author  = {Huang, C. X. and Burt, J. and Vanderburg, A. and G{\"u}nther, M. N. and Shporer, A. and Dittmann, J. A. and Winn, J. N. and Wittenmyer, R. and others},
  title   = {{TESS} Discovery of a Transiting Super-{Earth} in the pi {Mensae} System},
  journal = {The Astrophysical Journal Letters}, year = {2018}, volume = {868}, number = {2}, pages = {L39},
  doi     = {10.3847/2041-8213/aaef91}}

@article{Gandolfi2018,
  author  = {Gandolfi, D. and Barrag{\'a}n, O. and Livingston, J. H. and Fridlund, M. and Justesen, A. B. and Redfield, S. and Fossati, L. and Mathur, S. and Grziwa, S. and Cabrera, J. and others},
  title   = {{TESS's} first planet. A super-{Earth} transiting the naked-eye star $\pi$ {Mensae}},
  journal = {Astronomy \& Astrophysics}, year = {2018}, volume = {619}, pages = {L10},
  doi     = {10.1051/0004-6361/201834289}}

@article{Luque2019,
  author  = {Luque, R. and Pall{\'e}, E. and Kossakowski, D. and Dreizler, S. and Kemmer, J. and Espinoza, N. and Burt, J. and Anglada-Escud{\'e}, G. and B{\'e}jar, V. J. S. and Caballero, J. A. and others},
  title   = {Planetary system around the nearby {M} dwarf {GJ} 357 including a transiting, hot, {Earth}-sized planet optimal for atmospheric characterization},
  journal = {Astronomy \& Astrophysics}, year = {2019}, volume = {628}, pages = {A39},
  doi     = {10.1051/0004-6361/201935801}}

@article{BertaThompson2015,
  author  = {Berta-Thompson, Z. K. and Irwin, J. and Charbonneau, D. and Newton, E. R. and Dittmann, J. A. and Astudillo-Defru, N. and Bonfils, X. and Gillon, M. and others},
  title   = {A rocky planet transiting a nearby low-mass star},
  journal = {Nature}, year = {2015}, volume = {527}, pages = {204--207},
  doi     = {10.1038/nature15762}}

@article{Gandolfi2019,
  author  = {Gandolfi, D. and Fossati, L. and Livingston, J. H. and Stassun, K. G. and Grziwa, S. and Barrag{\'a}n, O. and Fridlund, M. and Kubyshkina, D. and others},
  title   = {The Transiting Multi-planet System {HD} 15337: Two Nearly Equal-mass Planets Straddling the Radius Gap},
  journal = {The Astrophysical Journal Letters}, year = {2019}, volume = {876}, number = {2}, pages = {L24},
  doi     = {10.3847/2041-8213/ab17d9}}

@article{Dumusque2019,
  author  = {Dumusque, X. and Turner, O. and Dorn, C. and Eastman, J. D. and Allart, R. and Adibekyan, V. and Sousa, S. and Santos, N. C. and others},
  title   = {Hot, rocky and warm, puffy super-{Earths} orbiting {TOI}-402 ({HD} 15337)},
  journal = {Astronomy \& Astrophysics}, year = {2019}, volume = {627}, pages = {A43},
  doi     = {10.1051/0004-6361/201935457}}

@article{AngladaEscude2016,
  author  = {Anglada-Escud{\'e}, G. and Amado, P. J. and Barnes, J. and Berdi{\~n}as, Z. M. and Butler, R. P. and Coleman, G. A. L. and de la Cueva, I. and Dreizler, S. and others},
  title   = {A terrestrial planet candidate in a temperate orbit around {Proxima Centauri}},
  journal = {Nature}, year = {2016}, volume = {536}, pages = {437--440},
  doi     = {10.1038/nature19106}}

@article{SuarezMascareno2020,
  author  = {Su{\'a}rez Mascare{\~n}o, A. and Faria, J. P. and Figueira, P. and Lovis, C. and Damasso, M. and Gonz{\'a}lez Hern{\'a}ndez, J. I. and Rebolo, R. and Cristiani, S. and others},
  title   = {Revisiting {Proxima} with {ESPRESSO}},
  journal = {Astronomy \& Astrophysics}, year = {2020}, volume = {639}, pages = {A77},
  doi     = {10.1051/0004-6361/202037745}}

@article{Faria2022,
  author  = {Faria, J. P. and Su{\'a}rez Mascare{\~n}o, A. and Figueira, P. and Silva, A. M. and Damasso, M. and Demangeon, O. and Pepe, F. and Santos, N. C. and others},
  title   = {A candidate short-period sub-{Earth} orbiting {Proxima Centauri}},
  journal = {Astronomy \& Astrophysics}, year = {2022}, volume = {658}, pages = {A115},
  doi     = {10.1051/0004-6361/202142337}}

@article{SuarezMascareno2025,
  author  = {Su{\'a}rez Mascare{\~n}o, A. and Artigau, {\'E}. and Mignon, L. and Delfosse, X. and Cook, N. J. and Bouchy, F. and Doyon, R. and Gonz{\'a}lez Hern{\'a}ndez, J. I. and others},
  title   = {Diving into the planetary system of {Proxima} with {NIRPS}. Breaking the metre per second barrier in the infrared},
  journal = {Astronomy \& Astrophysics}, year = {2025}, volume = {700}, pages = {A11},
  doi     = {10.1051/0004-6361/202553728}}

@article{Rosenthal2021,
  author  = {Rosenthal, L. J. and Fulton, B. J. and Hirsch, L. A. and Isaacson, H. T. and Howard, A. W. and Dedrick, C. M. and Sherstyuk, I. A. and Blunt, S. C. and Petigura, E. A. and Knutson, H. A. and others},
  title   = {The {California} Legacy Survey. {I}. A Catalog of 178 Planets from Precision Radial Velocity Monitoring of 719 Nearby Stars over Three Decades},
  journal = {The Astrophysical Journal Supplement Series}, year = {2021}, volume = {255}, number = {1}, pages = {8},
  doi     = {10.3847/1538-4365/abe23c}}

@article{Butler2004,
  author  = {Butler, R. P. and Vogt, S. S. and Marcy, G. W. and Fischer, D. A. and Wright, J. T. and Henry, G. W. and Laughlin, G. and Lissauer, J. J.},
  title   = {A {Neptune}-Mass Planet Orbiting the Nearby {M} Dwarf {GJ} 436},
  journal = {The Astrophysical Journal}, year = {2004}, volume = {617}, number = {1}, pages = {580--588},
  doi     = {10.1086/425173}}

@article{Gillon2007,
  author  = {Gillon, M. and Pont, F. and Demory, B.-O. and Mallmann, F. and Mayor, M. and Mazeh, T. and Queloz, D. and Shporer, A. and others},
  title   = {Detection of transits of the nearby hot {Neptune} {GJ} 436 b},
  journal = {Astronomy \& Astrophysics}, year = {2007}, volume = {472}, pages = {L13--L16},
  doi     = {10.1051/0004-6361:20077799}}

@article{Marcy1998,
  author  = {Marcy, G. W. and Butler, R. P. and Vogt, S. S. and Fischer, D. and Lissauer, J. J.},
  title   = {A Planetary Companion to a Nearby {M4} Dwarf, {Gliese} 876},
  journal = {The Astrophysical Journal Letters}, year = {1998}, volume = {505}, number = {2}, pages = {L147--L149},
  doi     = {10.1086/311623}}

@article{Rivera2010,
  author  = {Rivera, E. J. and Butler, R. P. and Vogt, S. S. and Laughlin, G. and Henry, G. W. and Meschiari, S.},
  title   = {A Super-{Earth} Orbiting the Nearby Sun-Like Star {HD} 1461},
  journal = {The Astrophysical Journal}, year = {2010}, volume = {708}, number = {2}, pages = {1492--1499},
  doi     = {10.1088/0004-637X/708/2/1492}}

@article{Howard2011,
  author  = {Howard, A. W. and Johnson, J. A. and Marcy, G. W. and Fischer, D. A. and Wright, J. T. and Henry, G. W. and Isaacson, H. and Valenti, J. A. and Anderson, J. and Piskunov, N. E.},
  title   = {The {NASA-UC} Eta-{Earth} Program. {III}. A Super-{Earth} Orbiting {HD} 97658 and a {Neptune}-mass Planet Orbiting {Gl} 785},
  journal = {The Astrophysical Journal}, year = {2011}, volume = {730}, number = {1}, pages = {10},
  doi     = {10.1088/0004-637X/730/1/10}}

@article{Trifonov2018,
  author  = {Trifonov, T. and K{\"u}rster, M. and Zechmeister, M. and Tal-Or, L. and Caballero, J. A. and Quirrenbach, A. and Amado, P. J. and Ribas, I. and others},
  title   = {The {CARMENES} search for exoplanets around {M} dwarfs. First visual-channel radial-velocity measurements and orbital parameter updates of seven {M}-dwarf planetary systems},
  journal = {Astronomy \& Astrophysics}, year = {2018}, volume = {609}, pages = {A117},
  doi     = {10.1051/0004-6361/201731442}}

@article{Lovis2011,
  author  = {Lovis, C. and S{\'e}gransan, D. and Mayor, M. and Udry, S. and Benz, W. and Bertaux, J.-L. and Bouchy, F. and Correia, A. C. M. and others},
  title   = {The {HARPS} search for southern extra-solar planets. {XXVIII}. Up to seven planets orbiting {HD} 10180: probing the architecture of low-mass planetary systems},
  journal = {Astronomy \& Astrophysics}, year = {2011}, volume = {528}, pages = {A112},
  doi     = {10.1051/0004-6361/201015577}}

@article{Bouchy2009,
  author  = {Bouchy, F. and Mayor, M. and Lovis, C. and Udry, S. and Benz, W. and Bertaux, J.-L. and Delfosse, X. and Mordasini, C. and others},
  title   = {The {HARPS} search for southern extra-solar planets. {XVII}. Super-{Earth} and {Neptune}-mass planets in multiple planet systems {HD} 47 186 and {HD} 181 433},
  journal = {Astronomy \& Astrophysics}, year = {2009}, volume = {496}, pages = {527--531},
  doi     = {10.1051/0004-6361:200810669}}

@article{Horner2019,
  author  = {Horner, J. and Wittenmyer, R. A. and Wright, D. J. and Hinse, T. C. and Marshall, J. P. and Kane, S. R. and Clark, J. T. and Mengel, M. and Agnew, M. T. and Johns, D.},
  title   = {The {HD} 181433 Planetary System: Dynamics and a New Orbital Solution},
  journal = {The Astronomical Journal}, year = {2019}, volume = {158}, number = {3}, pages = {100},
  doi     = {10.3847/1538-3881/ab2e78}}

@article{Bonfils2013,
  author  = {Bonfils, X. and Lo Curto, G. and Correia, A. C. M. and Laskar, J. and Udry, S. and Delfosse, X. and Forveille, T. and Astudillo-Defru, N. and others},
  title   = {The {HARPS} search for southern extra-solar planets. {XXXIV}. A planetary system around the nearby {M} dwarf {GJ} 163, with a super-{Earth} possibly in the habitable zone},
  journal = {Astronomy \& Astrophysics}, year = {2013}, volume = {556}, pages = {A110},
  doi     = {10.1051/0004-6361/201220237}}
```
