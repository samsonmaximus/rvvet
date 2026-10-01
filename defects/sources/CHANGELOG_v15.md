# v15 changelog (2026-09-29)

v15 builds on v14 (v13 and v14 are untouched in their own folders). You asked for "a v13";
v13 and v14 already existed from 25 Sept, so this is the next version and nothing was
overwritten. The frozen list is `ACCEPTANCE_v15.md`, written before the edits. An independent
referee pass (`REFEREE_v15.md`) was run on the first v15 build; everything it asked for is
fixed below except the two items that need you.

## Frozen acceptance list: done / not done

| # | Item | Status | Where / note |
|---|---|---|---|
| 1 | Held-out test on the three 2022–2024 HARPS spectra, frozen rule, reported whichever way | **Done** | New Sect. 5.2. Result: consistent (z = −1.0), 1.6σ from zero in the predicted direction, but the test had only an 8 % chance of excluding zero. The unplanned absolute comparison gives odds 0.75:1 (slightly against). Abstract and Summary say "consistent with the ephemeris but cannot test it". `analysis/heldout_v15.py`, `ancillary/heldout.dat` |
| 2 | Rotation estimate on the Mount Wilson scale | **Done** | Sect. 3.2, Table 2: log R'HK −4.79 (Gomes da Silva et al. 2021) → P_rot ≈ 39 d (31–49 d; 40 d with the weighted mean). v14 fed the PHOENIX-based RVBank value (−4.64) into the Noyes relation and got 28.6 d. `analysis/rotcal.py` |
| 3 | Rotation-dependent tests rerun over 30–50 d | **Done** | Harmonic bands, 90 % recovery, coherent forward model (new Fig. 6), evolving-spot models. The 9·P0 case is now argued from phase stability and the harmonic budget (new `comb9.py`), after the referee showed the quasi-periodic simulation could not have reproduced a ninth harmonic. |
| 4 | Cite Yu et al. (2024) | **Done** | Sect. 3.2, with the caveat that it is weak evidence either way. |
| 5 | TOI-6263.01 from ExoFOP | **Done** | Depth 193 ± 17 ppm, radius 1.12 R⊕ with our stellar radius, predicted K 0.8 m/s, 8.9 mutual Hill radii, PC disposition, "low SNR; slight depth-aperture correlation", TFOP LCO 1-m NEB check. `analysis/toi.py` |
| 6 | Zorro limits from the real curves | **Done** | Δm 7.0 at 0.5″ and 8.3 at 1.18″ (54 au) at 832 nm; 5.6 at 0.5″ at 562 nm. |
| 7 | OJAp class, clean build | **Done** | `openjournal.cls`, `aasjournal.bst`. No undefined references or citations, no overfull boxes. One harmless class warning remains ("LastPage multiply defined", from revtex4-1 inside the OJAp class). 16 pages. |
| 8 | Byline Samson Fraser | **Done** | Independent researcher, Sicamous; samsonmfraser@gmail.com. |
| 9 | Generative-AI statement per OJAp policy | **Done** | Acknowledgements: declared, with how the code and analysis were validated; wording corrected after the referee pass (no claim that every number is script-produced; both GP codes were AI-assisted). |
| 10 | Every reference checked | **Done** | `refcheck.md`: 78 entries, 76 OK, 2 fixed (Perdelwitz 2024 DOI was another paper's; Astudillo-Defru 2017 title). |
| 11 | A&A leftovers removed | **Done** | Received/accepted line, CDS footnote and CDS table statements replaced with the arXiv ancillary file (`ancillary/`). |
| 12 | Abstract ≤ 250 words, Summary updated | **Done** | 247 words. |
| 13 | NUMBERS.md and CHANGELOG | **Done** | NUMBERS.md "v15 additions" (two tables); this file. The v13 scripts and JSON files the referee found missing are now all in `analysis/`. |
| 14 | GitHub user and Zenodo DOI | **Not done: needs you** | `GITHUBUSER` and `ZENODODOI` in Data availability. See README. |

## Trade-offs (stated, not absorbed)

1. **The held-out test is weak and I said so.** With the real pipeline errors of these spectra
   (3.5–5.7 m/s; they were taken without a simultaneous reference), the noise on the contrast is
   7.9 m/s, not the 4.8 m/s expected when the rule was frozen. The paper reports the registered
   result as the headline and discloses the post-hoc photon-noise variant (which would reach 2.1σ)
   instead of promoting it.
2. **The rotation correction works against the planet, and it is in anyway.** On the right scale
   the star rotates in about 39 d, which puts 9·P0 = 38.415 d inside the estimate. The paper now
   says the period alone does not exclude a ninth harmonic and rests the case on phase stability
   (3 parts in 10⁵ over 170 rotations) and the harmonic budget (every other harmonic of 38.415 d
   is below 3 m/s at 95 %).
3. **I removed a claim a referee would have caught.** The first v15 build said simulations with
   P_rot at 9·P0 "do not reproduce the signal". The referee showed that kernel puts under 1 % of its
   variance in the ninth harmonic, so it could not have. That sentence is gone; the simulations are
   described as confirming the harmonic budget, not testing it.
4. **Fig. 6 and its numbers now come from the 30–50 d run** (`fwd2_3050.py`). A second, independent
   30–50 d run (`rot3050.py`) differs slightly (p99 9.3 vs 9.0) from Monte Carlo noise; both are in
   NUMBERS.md and the text quotes the one shown in the figure.
5. **The ASAS-SN rotation bound still covers only 25–40 d.** The photometry was not re-reduced for
   40–50 d; the paper says so in three places instead of implying coverage.
6. **The held-out paragraph moved** from "What will confirm it" to Sect. 5 (it is a result now),
   with a one-line pointer left in Sect. 8.4.
7. **`heldout_new.py` is frozen and unedited**, so its comments still say "Sect. 8.3" and "Table 4"
   (now Sect. 5.2 and Table 3).

## Found, not on the list

* The ESO HARPS radial-velocity catalogue (HARPS_RVCAT_V1) reproduces RVBank's DRS velocities to
  0.0005 m/s for all 108 spectra, which made the secondary absolute test possible.
* The TOI-6263.01 radius in v14 (0.93 R⊕) came from the TOI catalogue, which assumes a smaller star
  (0.61 R☉); with ours it is 1.12 R⊕ and the predicted K doubles to 0.8 m/s.
* The comparison table (Table 6) mixed activity scales; all log R'HK there are now Gomes da Silva
  et al. (2021) medians.
* The photometric follow-up plan was re-simulated for 30–50 d (it had been simulated at 28 d).
* No paper on HD 297396 / TOI-6263 exists in ADS full text as of 2026-09-29, so there is no scoop.
* ADS also links HD 297396 to the HWO target-list papers (Tuchow et al. 2024, 2025) as a star;
  not checked further and not used in the paper.
