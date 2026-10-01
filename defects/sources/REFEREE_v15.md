# Referee report on v15: HD 297396 b (Open Journal of Astrophysics version)

Reviewed 2026-09-29. Files: `hd297396b.tex` (v15), `hd297396b_v14_source.tex`, `make_v15.py`, `ACCEPTANCE_v15.md`, `NUMBERS.md`, `analysis/`, `ancillary/`, `hd297396b.log`.
Line numbers refer to `hd297396b.tex`.

**What I checked directly**
- Running `make_v15.py` on the v14 source (in a scratch copy) reproduces `hd297396b.tex` byte for byte, so the script lists every v14→v15 change.
- `heldout_v15.py` gives a `heldout_v15.json` identical to the shipped one. `rotcal.py` reproduces every v15 rotation number. `rot3050.json` and `fwd_qp_3050.json` match their logs and the text.
- Sign convention: a weighted fit of the archive velocities with per-label offsets puts the phase of the signal 0.003–0.017 orbit from $-K\sin[2\pi(t-T_c)/P]$ with $T_c = 2456298.34$ (SERVAL and DRS, 104 and 103 epochs). The convention in `heldout_v15.py` is therefore correct.
- The two new references were checked against the publisher pages.

---

## 1. Acceptance items (frozen list of 14)

| # | Verdict | Reason |
|---|---|---|
| 1 | **DONE** | Reported in Sect. 8.4 (the list says 8.3; "What will confirm it" is 8.4 in the PDF), in the abstract and in Summary item 2, whichever way it came out. The extra analysis is labelled "not planned before the data were read" (l. 1096). The wording "agree with the ephemeris" is too strong (see 4a). |
| 2 | **NOT DONE (small)** | Table 2 and Sect. 3.2 are updated. But Table 5 still gives the rotation signature as "Spots varying in 25--40 d" (l. 826). Numbers derived from the old range were not updated: "more than 55 rotations" (l. 613, l. 821) and the HD 181433 b "regime" (l. 944–945). See Sect. 3. |
| 3 | **DONE** | All five reruns exist over 30–50 d and match the text: bands and 90 % recovery (`rot3050.json`), coherent forward model (`rot3050.json`), short- and long-lived QP (`fwd_qp_3050.json`), and $9P_0$ (`fwd_qp_3050.json`). Whether the $9P_0$ case is a real test is a separate question (4b). |
| 4 | **DONE** | Yu et al. (2024) is cited in Sect. 3.2 (l. 295–297). |
| 5 | **DONE** | The depth of 193 ± 17 ppm, S/N 9, PC disposition, the TOI note, TFOP LCO-CTIO 2023-04-25 with 137/139 cleared, and the conditioning are all in Sects. 7.2, 8.1 and Summary item 4. However, the radius and predicted $K$ of TOI-6263.01 were not updated to match the new depth (Sect. 2/3, item S1). |
| 6 | **DONE** | Zorro 832/562 nm values come from the ExoFOP tables (l. 791–796). Nit: the outer edge is 1.175″ = 54 au, not 55 au. |
| 7 | **NOT DONE (trivial)** | There are no undefined references or citations. The log still shows: (i) a 1.8 pt overfull `\hbox` inside Table 5 (row at l. 824); (ii) `LastPage` multiply defined; (iii) three duplicate hyperref destinations `table.1`, so links to Tables A1, B1 and G1 jump to Table 1. Fix (iii) with `\usepackage[hypertexnames=false,...]{hyperref}` or `\renewcommand{\theHtable}{\thesection.\arabic{table}}`. Also cosmetic: the URL footnote (l. 122) breaks across pages 1–2. |
| 8 | **DONE** | Byline, affiliation and name-based email are in place (l. 29–31). |
| 9 | **DONE** | The statement is in the acknowledgements and includes a validation account (l. 1183–1196). Two sentences overclaim (Sect. 5, item 5). |
| 10 | **DONE for the two new entries** | `GomesdaSilva2021` matches the publisher: A&A 646, A77 (2021), doi 10.1051/0004-6361/202039765, same authors and title. `Yu2024` also matches: MNRAS 528, 5511–5527 (2024), doi 10.1093/mnras/stae137, same authors and title; the abstract states 268 targets and rotation periods for 49 stars, as the text says. Both are cited with correct `\citet`/`\citep` forms. A content issue is separate: l. 288 attributes "makes cool stars appear more active" to `Perdelwitz2024`, and I cannot confirm that from its abstract (see 4b). |
| 11 | **DONE** | Received/accepted line, CDS footnote, "available at the CDS" and `\keywords` are all gone. The remaining "CDS catalogue J/A+A/683/A125" (l. 120–122) correctly identifies the RVBank data source and should stay. |
| 12 | **DONE (at the limit)** | The abstract is 250 words counting each inline formula as one word (about 270 as rendered tokens) and 1696 characters (arXiv limit 1920). Summary covers items 1, 2, 3 and 5. The replacement abstract sentence in 4a keeps the word count. |
| 13 | **NOT DONE** | NUMBERS.md was extended, but there is no v15 CHANGELOG (only `CHANGELOG_v14.md`), so there is no "Found, not on the list" section. NUMBERS.md also lacks: the "20 %" prior power (l. 1087), the "0.98 m s⁻¹" NZP rms (l. 1092), and the photometric-plan simulation of l. 1057–1059. |
| 14 | **NOT DONE (expected)** | `ZENODODOI` and `GITHUBUSER` placeholders remain at l. 1207–1208. |

---

## 2. Numbers that changed from v14 to v15

### 2.1 Verified (text = JSON/script/NUMBERS)

- **Sect. 3.2 / Table 2** (`rotcal.py`): $S_{\rm MW}$ 0.49; $\log R'_{\rm HK}$ −4.79 (median −4.787); B−V 1.12; τc 23.9 d; Ro 1.63 (1.634); $P_{\rm rot}$ 39 d (39.1); range 31–49 d (31.0–49.2); MH08 38 d (38.3); v14 input gives 28.6 d. $P_0/P_{\rm rot}$ is 0.09–0.14 (0.085–0.142). Multiples 8–11; $9P_0$ = 38.415 d. Ro(P0) 0.18 → −4.3.
- **Sect. 5.3** (`rot3050.json`): 0/20 000; p99 9.3 (9.27); max 18.0 (18.04); 0.3 % at 12 (0.275 %); 2.0 % at 15 (1.95 %).
- **Sect. 5.3** (`fwd_qp_3050.json` + v13 NUMBERS): 90 000 = v13 50 000 + v15 40 000; 0.3–0.4 % at 10 m/s (0.26, 0.30, 0.39 %); $9P_0$: 0/10 000 at each of 3.2 and 6, 0.36 % at 10.
- **Sect. 5.6** (`rot3050.json`): 13.9/13.7/11.0 vs 20.2/21.3/22.0; 0.895 recovered at 4.5 m/s. The 1.5 min figure is 1.53 min for 39.1 d.
- **Table 5**: 0.5–0.8 of 1 % levels (30–50: 0.69/0.64/0.50); 110 000 = 90 000 + 20 000.
- **Abstract / Table 6 / Summary**: 150 000 = 20 000 + 20 000 + 50 000 + 60 000.
- **Sects. 4.5 and 7.2**: 193 ± 17 ppm; "three to nine times" (600/193 = 3.1, 1800/193 = 9.3); S/N 9; 137/139; 2.5′; 0.19 ppt.
- **Sect. 5.8**: Δm 7.0 at 0.5″ = 23 au; 8.3 at the outer edge; 5.6 at 562 nm.
- **Sect. 8.4** (`heldout_v15.json`):
  - dates and programmes match the headers;
  - phases 0.80/0.52/0.80 (0.804/0.520/0.795);
  - $D_{\rm pred}$ −4.2 ± 2.9 (−4.21 ± 2.87); $D_{\rm obs}$ −12.7 (−12.71);
  - DVRMS 3.5/5.7/3.9; noise 7.9 (7.89 = √[5.71²+3.9² + ¼(3.50²+3.9²) + ¼(3.92²+3.9²)]);
  - z −1.0 (−1.01); z0 −1.6 (−1.61); power 8 % (0.083);
  - 108 spectra; "0.001 m/s" (max 0.0005); 2.2 m/s (hypot(0.98, 2.0)); 0.8:1 (0.79).

### 2.2 Mismatches or missing provenance

| # | Location | Problem | Fix |
|---|---|---|---|
| N1 | l. 208 (Sect. 2.4) | "$0.93 \pm 0.08\,R_\oplus$" is the radius the old 130-ppm depth was computed from: $(0.93/109.1/0.739)^2 = 133$ ppm. With the new 193 ± 17 ppm and $R_\star = 0.739 \pm 0.026\,R_\odot$, $R_p = 1.12 \pm 0.06\,R_\oplus$. | Replace with `a $1.12 \pm 0.06\,R_{\oplus}$ candidate` (depth and $R_\star$ of Table 2, no limb-darkening or impact-parameter correction). Alternatively, cite the source of 0.93 and the $R_\star$ it assumes. Add the line to NUMBERS.md. |
| N2 | l. 882 (Sect. 7.2) | "predicted semi-amplitude is 0.4 m s⁻¹" follows from 0.93 $R_\oplus$ → 0.77 $M_\oplus$ (Chen & Kipping terran branch) at 0.524 m s⁻¹ per $M_\oplus$. At 1.12 $R_\oplus$ the same relation gives ≈1.5 $M_\oplus$, so ≈0.8 m s⁻¹. | Recompute with a script and quote ≈0.8 m s⁻¹. Recheck the 9.2 mutual Hill radii (l. 885), which depends weakly on the inner mass. |
| N3 | l. 613–614 and l. 821 | "more than 55 rotations at the long edge of the candidate range": 2300/40 = 57.5 was right for v14's 25–40 d. At the adopted 50 d the value is 46 (and 2300/42 = 54.8 is not "more than 55" either). | l. 613: `more than 46 rotations at the long edge of the adopted range (50\,d) and 540 orbits`. l. 821: `$\tau > 2300$\,d, more than 46 rotations at 50\,d`. |
| N4 | l. 281–282 | "its mean activity is −4.79": −4.787 is the **median**; the weighted mean is −4.806, which gives 40.3 d (32.0–50.7 d) in `rotcal.py`. | `On the Mount Wilson scale its median activity level is $\log R'_{\rm HK} = -4.79$ (weighted mean $-4.81$; ...)`. |
| N5 | l. 793–796 | "1.2″ or 55 au": the outer edge of the table is 1.175″ = 54.2 au. | `1\farcs18 or 54\,au`, and "54 au" at l. 796 (Table 5 "about 55 au" can stay). |
| N6 | l. 1087 | "the 20 % expected before the pipeline errors were known" has no provenance. I get 0.21 with the v13 prediction (−5.2 ± 2.7, noise 4.8) and 0.17 with the v15 header-BJD prediction and 3.9-m/s-only noise (4.78). | Say "about 20 %" (or "17–21 %") and add the calculation to `heldout_v15.py` and NUMBERS.md. |
| N7 | l. 1092 | "0.98 m s⁻¹ rms" is not in NUMBERS.md. It is the standard deviation of `NZPdrs` over post-upgrade nights (0.95 over all nights). | Add it to NUMBERS.md with that definition. |
| N8 | NUMBERS.md "Evolving-spot… 30–50 d" row and l. 653–656 | The 90 000 total includes v13's `fwd_qp_long.json`, which is not in `/home/claude/v15/analysis`, so I could not check it here. | Ship it (see Sect. 5, item 7). |

---

## 3. Stale text

**Legitimate mentions (keep):**
- l. 120–122: the CDS catalogue ID of the RVBank source.
- l. 260 and 286–290: −4.64 described as the RVBank value.
- l. 649, 763 and 822: 25–40, 22–40 and 17–45 d given as robustness runs.
- l. 1416–1418: describes the ASAS-SN search that was actually run over 25–40 d.
- l. 1431: "30–50-d modulation is longer than a sector".

**Stale or inconsistent (fix):**

| # | Location | Stale item | Replacement |
|---|---|---|---|
| S1 | l. 208, l. 882 | TOI-6263.01 radius and predicted $K$ still come from the 130-ppm era | See N1, N2. |
| S2 | l. 290–291 | "repeat every test that depends on it over 17–45 d". Not true for the photometric bound (25–40 d only) or the seasonal injection (l. 292–295, range not recorded). It also omits the 25–40 and 22–40 d runs. | `We adopt 30--50\,d. The velocity tests that depend on it were also run over 25--40, 22--40 and 17--45\,d with the same results; the photometric bound of Sect.~\ref{sec:phot} covers 25--40\,d only.` Check which range the injection at l. 292–295 used. |
| S3 | l. 613, l. 821 | 55 rotations | See N3. |
| S4 | l. 668–671 (Fig. 6 caption) | The figure is the v12 run with $P_{\rm rot} \sim U(25,40)$ (`fwd2.py`, l. 21), but the caption does not say so and Sect. 5.3 now leads with 30–50 d. | Regenerate from the 30–50 d run, or add to the caption: `Rotation periods are drawn from 25--40\,d; the 30--50-d run gives the same distribution (99th percentile 9.3, maximum 18.0).` |
| S5 | l. 748–752 (Sect. 5.6) | "The candidate rotation periods of Sect. 3.2 do not place a harmonic at $P_0$" contradicts l. 310–313, which now says $9P_0$ lies inside both estimates. | `The quasi-periods measured in Sect.~\ref{sec:rot} (41.4, 38.9 and 36.1\,d) do not place a harmonic at $P_0$: the nearest lie 18, 47 and 83 frequency-resolution elements away. Only $P_{\rm rot} = 38.41 \pm 0.03$\,d would put one within a single element, and that value lies inside both the activity range and the spread of the quasi-periods, so the period alone does not exclude it (Sect.~\ref{sec:forward}).` |
| S6 | l. 782–783 | Correct for the test run, but silent on 40–50 d, unlike Table 5. | `That reduction bounds any modulation in 25--40\,d below 8\,mmag; periods of 40--50\,d were not searched.` Add the same clause at l. 1417. |
| S7 | l. 826 (Table 5) | Signature "Spots varying in 25--40 d" | `Spots varying in 30--50\,d` & `ASAS-SN $g$, $< 8$\,mmag at 90\% recovery in 25--40\,d; 40--50\,d not searched` |
| S8 | l. 944–948 | "at 0.09–0.14 of the rotation period, the regime of HD 47186 b and HD 181433 b ($P/P_{\rm rot}$ ≈ 0.12 and 0.17)". 0.17 is outside 0.09–0.14. | `HD\,297396\,b lies at 0.09--0.14 of the rotation period, close to HD\,47186\,b ($P/P_{\rm rot} \approx 0.12$) and below HD\,181433\,b (0.17; \citealt{Bouchy2009}), both published from HARPS with an inferred rotation period, ...` |
| S9 | l. 1057–1059 | "25 nights … over two months measure any modulation above 5 mmag at the rotation period". Unchanged from v14, with no NUMBERS entry; probably simulated for ≤40 d. At 50 d, two months is 1.2 cycles. | Re-run for 30–50 d, or change to "three months" once re-simulated. Add it to NUMBERS.md. |
| S10 | l. 1042 (Table 7), l. 823 (Table 5), l. 1124–1125 (Summary) | "$P_{\rm rot}=9P_0$ simulated / with sharp harmonics / including a rotation period at nine times $P_0$". These are overclaims, not stale text. | See 4b for replacement text. |
| S11 | `ancillary/ReadMe`, column `logRHK` | The column holds the RVBank (PHOENIX-based) values (median −4.644), not the −4.79 now quoted as the activity level. | `log10 R'HK from HARPS-RVBank (PHOENIX-based photospheric correction; not the Mount Wilson scale, see Table 2)`. |
| S12 | `analysis/rot3050.py` header | The comment says bands 22–40/11–20/7.33–13.33 and $U(22,40)$, but the code uses 30–50. | Fix the comment before depositing. `heldout_new.py` also refers to "Sect. 8.3" and "Table 4" (now 8.4 and Table 3); leave the frozen file alone and note this in the CHANGELOG. |
| S13 | Table 6, l. 975 | HD 297396 is now on the Mount Wilson scale (−4.79). The other columns (−4.94, −5.20, −5.01) must be on the same scale. | Check the sources and add "(Mount Wilson scale)" to the row label, or footnote any that are not. |

No A&A or CDS leftovers remain in the text. "Sect." abbreviations and `\tablefoot` are harmless.

---

## 4. Scientific soundness of the two substantive v15 changes

### 4a. Held-out test (Sect. 8.4, l. 1072–1097)

**Correctness of the computation**
- `heldout_v15.py` implements the frozen rule of `heldout_new.py` exactly. It reads the same header keywords (DRS 3.8 still writes `DRS CCF RVC` and `DRS DVRMS`). Night binning and the contrast weights (−½, 1, −½) are unchanged, and the seed is the same (so the Monte Carlo is identical).
- The model $-K\sin[2\pi(t-T_c)/P]$ is right for inferior conjunction and agrees with the archive fit (phase offset < 0.02 orbit).
- $z = (D_{\rm obs}-\bar D_{\rm pred})/\sqrt{\sigma_{\rm noise}^2+{\rm Var}(D_{\rm pred})}$ and $z_0 = D_{\rm obs}/\sigma_{\rm noise}$ are the right statistics.
- The power $P(z_0<-2\mid{\rm planet}) = 0.083$ is computed correctly.

**Honesty.** The write-up states the registered test, its result, its low power, and the prior expectation, and it labels the archive-tied comparison as unplanned. That is good practice. Five points need fixing:

1. **"Agree with the ephemeris" overstates the result** (abstract l. 51–52, Summary l. 1117–1119).
   - The contrast has the predicted sign, but it comes from one spectrum. The 2024 March spectrum has the lowest S/N (SN60 = 25.1, five above the C4 cut) and lies 13 m s⁻¹ below the other two, which agree with each other to 2.5 m s⁻¹. That is three times the predicted −4.2 m s⁻¹.
   - When the offset is tied to the archive (post hoc), the planet predicts the 2022 and 2024 November points about +5 m s⁻¹ above the offset. They sit at +1.1 and −1.5 m s⁻¹, and the odds are 0.8:1, slightly **against** the planet.
   - "Consistent with, too weak to test" is the honest summary.
   - Abstract l. 51–52 (same word count): `Three later HARPS spectra are consistent with the ephemeris but cannot test it.`
   - Summary l. 1117–1119: `Three HARPS spectra taken after the archive release are consistent with the ephemeris on a test fixed before their velocities were read ($z = -1.0$), but the test had an 8\% chance of excluding zero, and the three spectra carry little weight.`
   - Sect. 8.4, after "The observed contrast is $-12.7\ms$" (l. 1082): add `, carried by the 2024 March spectrum, the one with the lowest S/N, which lies $13\ms$ below the other two`.

2. **The photon-noise variant is in NUMBERS.md but not in the paper.** With the CCF photon-noise errors (1.34, 3.56, 1.62 m s⁻¹) in place of DVRMS, the noise is 6.05 m s⁻¹, $z = -1.27$ and $z_0 = -2.10$, which crosses the "excludes zero" line.
   - DVRMS is the registered choice, and RVBank uses it too: ESO `dvrms` equals RVBank `e_RVdrs` for every matched spectrum.
   - However, for the two 2021 RVBank spectra taken in the same STAR,SKY mode, DVRMS (5.27, 3.11) is 2.5–3.4 times their SERVAL errors (2.09, 0.92). For the STAR,DARK spectra the two errors are similar. So the registered errors are probably conservative.
   - Either remove the variant from NUMBERS.md or, better, report it and keep the registered result as the headline. Insert after l. 1087: `With the cross-correlation photon-noise errors (1.3, 3.6 and $1.6\ms$) instead of the registered pipeline errors, a choice not made in advance, the noise is $6.0\ms$, $z = -1.3$ and the contrast lies $2.1\sigma$ from zero. For spectra in this fibre mode the registered errors are 2.5--3.4 times the \serval\ errors of the two 2021 RVBank spectra, so the registered test is the conservative one; we report it as the result.`

3. **C3 is not "passed", it cannot be applied** (l. 1077–1079). STAR,SKY spectra have no simultaneous reference; the drift is 0 by construction, as for the two 2021 RVBank spectra. Replace with: `they pass criteria C4 and C5 of Table~\ref{tab:data}; C1 and C2 need RVBank products, and C3 cannot be applied because, like the last two RVBank spectra, they were taken without a simultaneous reference.`

4. **The freeze is attested only by the author's records** (l. 1074–1075). "fixed in the released code before their velocities were read" should match Sect. 2.2, which says the deposit postdates the analysis. Replace with: `run with a decision rule written into code on 2026 September 25, before their velocities were read (the code is released with this paper; the date is not independently time-stamped).`

5. **Minor points**
   - In the secondary test, `heldout_v15.py` treats the 0.98 m s⁻¹ nightly zero point as fully correlated across the three nights. It is nightly and belongs on the diagonal; only the 2 m s⁻¹ instrumental term is shared. The result does not move (my reruns give ln B = −0.29 with per-night NZP, −0.28 with the 4.6 m s⁻¹ DRS post-upgrade jitter of App. B, and −0.09 with photon errors). Fix the code comment or the covariance; the text can stay.
   - The frozen 3.9 m s⁻¹ is a SERVAL-fit scatter applied to DRS velocities, whose post-upgrade jitter is 4.6 m s⁻¹ (App. B, l. 1316). It was frozen, so leave it, but one clause would pre-empt the question.
   - A result now sits inside "What will confirm it". Consider moving the paragraph to Sect. 5 (for example "5.x Three post-archive spectra") and leaving a one-line pointer in 8.4.

**Verdict on 4a.** The computation is correct, and pre-registered and post-hoc parts are separated honestly. The power is disclosed. The abstract and summary claim more than the data show, and a post-hoc variant that happens to cross the threshold should be disclosed, not left only in NUMBERS.md.

### 4b. Rotation recalibration and the ninth-harmonic worst case

**The recalibration is correct in principle, and it is adverse to the planet**, which makes it credible.
- Feeding the PHOENIX-based RVBank value into relations built on Noyes/Middelkoop $R'_{\rm HK}$ was a scale error. The Mount Wilson value from GdS21 is the right input.
- `rotcal.py` reproduces the GdS21 median −4.787 from $S_{\rm MW}$ = 0.4876 (−4.799 via Middelkoop/Noyes), and the Noyes/MH08 arithmetic is right.
- The new estimate (≈39 d) agrees with the ΔLW/Hα quasi-period (36–42 d). This strengthens the case that the star rotates in 36–42 d, and it places $9P_0$ = 38.415 d inside both estimates.

**Caveats the text should state** (l. 281–291):
1. At B−V = 1.12 the star is near the red edge of both calibrations. Noyes' τc(B−V) is a linear extrapolation for B−V > 1, and the MH08 Ro–activity fit is dominated by F to early-K stars. The ±0.1 dex range is therefore a lower limit on the uncertainty. Also, the weighted-mean activity level gives 40.3 d (32.0–50.7 d), so the adopted 30–50 d slightly truncates the upper tail. A cross-check against a relation calibrated for K dwarfs (for example Suárez Mascareño et al. 2015/2016, HARPS-based) would help.
   - Insert after "gives 38 d" (l. 286): `At $B-V = 1.12$ the star lies near the red edge of the samples that calibrate both relations, so the 0.1-dex range understates the uncertainty; the weighted-mean activity level gives 40\,d (32--51\,d).`
2. l. 286–289 attributes "makes cool stars appear more active" to Perdelwitz et al. (2024). The RVBank paper's abstract says nothing of this. Unless the body of that paper shows it, cite the paper that introduced and compared the PHOENIX-based correction (Mittag et al. 2013, A&A 549, A117), or state only what is shown for this star. Replacement: `HARPS-RVBank lists $\log R'_{\rm HK} = -4.64$ for the star, 0.15\,dex higher; its values use a PHOENIX-based photospheric correction \citep{Perdelwitz2024} rather than the $B-V$-based one for which these relations were calibrated, and used as input they would give 28.6\,d.`
3. Table 2 footnote *a* is attached to the B−V row but describes the $S$-index conversion. Give B−V its own note, or change the source column to "GdS21 (Hipparcos)".

**The ninth-harmonic "worst case" cannot reproduce the signal by construction, so it does not test the scenario it is presented as testing** (l. 656–661, Table 5 l. 823, Table 7 l. 1042, Summary l. 1124–1125).

1. **Harmonic budget of the kernel.** In `fwd_qp_3050.py` the kernel is $\exp[-\tau^2/2\lambda^2-\sin^2(\pi\tau/P)/2w^2]$. Its periodic factor expands in modified Bessel functions: harmonic $n$ carries a variance fraction $2I_n(\kappa)e^{-\kappa}$ with $\kappa = 1/4w^2$.

   | w | variance beyond 3rd harmonic | variance in 9th harmonic | equivalent $K_9$ at 6 m/s rms | at 10 m/s rms |
   |---|---|---|---|---|
   | 0.15 | 29 % | 0.65 % | 0.69 m/s | 1.14 m/s |
   | 0.20 | 16 % | 0.08 % | 0.24 | 0.39 |
   | 0.25 | 8 % | 0.008 % | 0.07 | 0.12 |
   | 0.30 | 4 % | 8e-6 | 0.02 | 0.04 |
   | 0.40 | 1 % | 1e-7 | 0.00 | 0.01 |

   The planet has $K$ = 5.5 m s⁻¹. Even at the sharpest end ($w$ = 0.15) the ninth harmonic is 5–8 times too weak **before** any decoherence. Over most of the drawn range $w$ = 0.15–0.4 it is negligible. "Puts much of their power beyond the third harmonic" holds only near $w$ = 0.15, and "sharp harmonics" (Table 5) is not accurate.

2. **The outputs show no ninth-harmonic effect.** The Δχ² percentiles at $P_0$ for the 9P0 set match the generic 30–50 d set: p99 8.3/12.8/25.1 against 8.1/13.6/25.1 at 3.2/6/10 m s⁻¹. The 0.36 % at 10 m s⁻¹ is the generic QP rate (0.26–0.39 %), not a harmonic effect.

3. **The ±1 % window is mostly off target.** A ±1 % window on $P_{\rm rot}$ puts the ninth harmonic up to ±15 frequency-resolution elements from $P_0$. For the long-lived realisations (λ up to 10 rotations; line σ ≈ 2.7 elements), only the roughly 7 % of draws within ±0.025 d of 38.415 d are on target.

4. **The model cannot represent the dangerous case.** The dangerous case is a long-lived, phase-stable spot pattern whose ninth harmonic dominates. A QP GP with λ ≤ 10 rotations (≤ 384 d, against a 6536-d baseline and τ > 2300 d) is not that. The coherent forward model uses harmonics 1–3 only, so it cannot represent it either.

**What does argue against $P_{\rm rot} = 9P_0$** is already in the data and should be stated directly:
- (i) **Phase stability.** 15° over 170 rotations requires a period stable to 2.7 × 10⁻⁵ (l. 752–756).
- (ii) **Harmonic budget.** A strictly periodic signal at 38.415 d would need its ninth harmonic to carry 5.5 m s⁻¹ while all the others are small. A quick check (white-noise frame, planet removed, per-label jitters refitted, single-frequency fits at $k/38.415$ d) gives:
  - Δχ² ≤ 3.8 and $K$ ≤ 1.6 ± 0.8 m s⁻¹ at every harmonic $k$ = 1–8, 10, 11;
  - 2σ upper limits ≲ 3 m s⁻¹; the fundamental is 0.46 ± 0.79 m s⁻¹.

  So the ninth harmonic would have to exceed the fundamental by more than a factor of about 3. In the QP kernel, $K_9$ = 5.5 m s⁻¹ would need ≈50 m s⁻¹ rms of rotational signal, about 8 times the velocity scatter.

  These are my numbers, not the author's. The author must reproduce them with a released script (for example `analysis/comb9.py`, below) and add them to NUMBERS.md before using them.

Replacement for l. 652–663 (keep the α Cen B sentence at the end):

```latex
Evolving spots do no better. Realisations of a quasi-periodic Gaussian process,
$k(\tau) = A^2\exp[-\tau^2/2\lambda^2 - \sin^2(\pi\tau/P_{\rm rot})/2w^2]$, with
rotation period 17--45 or 30--50\,d, evolution time $\lambda$ of one to ten
rotations and harmonic complexity $w$ spanning that fitted to $\Delta$LW, never
reach the observed value: none of 90\,000 at $3.2$ or $6\ms$ rms. At $10\ms$ rms,
almost twice the total velocity scatter of the star, 0.3--0.4\% do.

A rotation period at $9P_0 = 38.415$\,d, inside both rotation estimates, needs
no leakage: the ninth harmonic of a strictly periodic signal falls on $P_0$. Two
properties of the data argue against it. The phase would have to hold to
$15\degr$ over 170 rotations, which requires a rotation period constant to 3
parts in $10^5$ (Sect.~\ref{sec:harm}); and the ninth harmonic would have to
carry $K \approx 5.5\ms$ while the fundamental and the other harmonics of
38.415\,d, up to the eleventh, each carry less than about $3\ms$ ($2\sigma$).
Spot models do not distribute power this way: in the kernel above even
$w = 0.15$ puts less than 1\% of the variance into the ninth harmonic, so
$K = 5.5\ms$ there would need a rotational signal of about $50\ms$ rms.
Realisations with $P_{\rm rot}$ within 1\% of $9P_0$ and $w = 0.15$--0.4 behave
like the rest of the band (none of 20\,000 at 3.2 or $6\ms$ rms, 0.4\% at
$10\ms$), which confirms this budget rather than testing a coherent ninth
harmonic.
```

Other places:
- Table 5 l. 823: replace ", including $P_{\rm rot} = 9P_0$ with sharp harmonics" with `; at $P_{\rm rot} = 9P_0$ the ninth harmonic would have to exceed the fundamental and every other harmonic ($K < 3\ms$)`.
- Table 7 l. 1042: replace "$P_{\rm rot} = 9P_0$ simulated" with `at $P_{\rm rot} = 9P_0$ the ninth harmonic would have to dominate`.
- Summary l. 1123–1125: `... reproduces it. A rotation period of exactly nine times $P_0$ is not excluded by period alone; it would need a ninth harmonic stronger than the fundamental, held in phase for 170 rotations.`

Sketch of the check (in the style of `rot3050.py`, run in `analysis/`):

```python
exec(open('split.py').read().split('subsets={')[0])
df=S; t=df.t.values; X=np.c_[np.cos(2*np.pi*t/P0),np.sin(2*np.pi*t/P0)]
jj,_,idx,L,labs=jitter_fit(df,design=X); w=1/(df.e.values**2+jj[idx]**2)
XX=np.hstack([L,X]); p=np.linalg.solve(XX.T@(XX*w[:,None]),XX.T@(w*df.y.values))
R=df.copy(); R['y']=df.y.values-X@p[-2:]; jn,_,iR,_,_=jitter_fit(R); wR=1/(R.e.values**2+jn[iR]**2)
for k in [1,2,3,4,5,6,7,8,10,11]:
    f=k/(9*P0); A=np.hstack([L,np.c_[np.cos(2*np.pi*t*f),np.sin(2*np.pi*t*f)]])
    M=A.T@(A*wR[:,None]); c=np.linalg.solve(M,A.T@(wR*R.y.values)); C=np.linalg.inv(M)
    print(k, periodogram(R,np.array([f]),jit=jn)[0][0], np.hypot(*c[-2:]), np.sqrt(np.diag(C)[-2:].mean()))
```

**Verdict on 4b.** The recalibration is right and honestly reported. The conclusion "the ninth-harmonic worst case does not reproduce the signal" is stronger than the evidence, because that simulation could not have reproduced it. The argument against $9P_0$ should rest on phase stability and the harmonic budget, which the data do support.

---

## 5. Other referee-level problems (prioritised, max 8)

1. **The "150 000 simulated rotational signals" headline mixes sets with little power to fail.** The number sums coherent sets that use harmonics 1–3 only and QP sets that are short-lived by construction; none can reproduce a coherent signal at $P_0$ except by chance leakage. This is fine as a leakage test, but the abstract and summary imply broader coverage. Keep the number but do not attach "including a rotation period at nine times $P_0$" to it (Summary l. 1124–1125; see 4b).
2. **Undefined model parameters.** Sect. 5.3 (l. 652–660) uses "evolution time" and "harmonic complexity $w$" without defining the kernel. Give the formula once, as in the replacement above.
3. **Yu et al. (2024) is weak evidence either way** (l. 295–297). They recovered periods for 49 of 268 stars, and their Table 3 entry for this star covers data to 2015 May only. Add: `(their data end in 2015, and periods were recovered for 49 of the 268 stars, so this is weak evidence either way)`.
4. **Fig. 6 does not show the adopted range.** It is still the 25–40 d run; regenerate it from the 30–50 d run or caption it (S4).
5. **The generative-AI statement overclaims** (l. 1186–1190).
   - "Every number in the paper is produced by a released script" is contradicted by NUMBERS.md, which uses a pipeline (P), literature values, arithmetic and inline checks. Replace with `Every number in the paper is traced, in a provenance table distributed with the code, to the released script, pipeline output or published source that produced it.`
   - "implemented twice, in independent code" should say that both implementations were written with the same AI assistance: `implemented twice, in separate code bases (both written with AI assistance), and the two agree...`.
6. **Build hygiene (item 7).**
   - Fix the duplicate `table.1` anchors (links to Tables A1/B1/G1 go to Table 1), the multiply-defined `LastPage`, and the 1.8 pt overfull row in Table 5 (for example, break "(instrument-wide)" or widen the Verdict column by 1 mm).
   - "Version September 29, 2026" prints twice (running head and after the affiliation); set `\date{}` or accept the class default.
7. **The reproducibility package is incomplete.** Eleven scripts and about 14 JSON files cited in NUMBERS.md are not in `/home/claude/v15/analysis`: `fwd_qp_long.py`, `rot1745.py`, `rot2240.json`, `fip_seed.py`, `fip_extra.py`, `gpfap.py`, `gp_typical.py`, `qp_split.py`, `semian2.py`, `aliasband.py`, `ecc_check2.py`, `fastcheck.py`, and others. `fwd_qp_long.json` and `rot2240.json` underpin the 90 000 and 150 000 totals. Assemble one self-contained folder for Zenodo, and write the missing v15 CHANGELOG with its "Found, not on the list" section (item 13).
8. **The held-out result is in a future-work section.** Moving the paragraph to Sect. 5 (as a test) with a one-line pointer in 8.4 would make the paper's logic clearer (see 4a, point 5).

---

## Must fix before submission (priority order)

1. **Ninth-harmonic overclaim.** Sect. 5.3 l. 656–663, Table 5 l. 823, Table 7 l. 1042, Summary l. 1124–1125. The simulation puts ≤0.65 % of its variance in the ninth harmonic, so it cannot reproduce the signal. Replace it with the phase-stability and harmonic-budget argument, backed by a released harmonic-comb script (4b).
2. **Held-out wording and disclosure.**
   - Abstract l. 51–52 and Summary l. 1117–1119: "agree with" → "consistent with, cannot test".
   - Sect. 8.4: say the contrast is carried by the S/N-25 spectrum; say C3 cannot be applied; say the freeze date is not independently time-stamped; report or remove the post-hoc photon-noise variant ($z_0$ = −2.1).
3. **TOI-6263.01 inconsistency.** The radius 0.93 $R_\oplus$ (l. 208) and predicted $K$ 0.4 m s⁻¹ (l. 882) contradict the new 193 ppm depth. With $R_\star$ = 0.739 they become ≈1.12 ± 0.06 $R_\oplus$ and ≈0.8 m s⁻¹. Recheck the Hill separation.
4. **Stale rotation remnants.**
   - "more than 55 rotations" → 46 (l. 613, l. 821);
   - Table 5 signature "25–40 d" (l. 826);
   - HD 181433 b "regime" (l. 944–945);
   - "candidate rotation periods do not place a harmonic" (l. 748–752);
   - "repeat every test … over 17–45 d" (l. 290–291);
   - ASAS-SN 40–50 d gap in the text (l. 782, l. 1417);
   - photometric plan "two months" (l. 1057–1059);
   - Fig. 6 caption (l. 668–671).
5. **Rotation-calibration caveats.** "mean" → "median" (l. 281); note the calibration edge at B−V = 1.12 and the weighted-mean 40 d (32–51 d); fix or re-source the Perdelwitz2024 attribution (l. 286–289); split Table 2 footnote *a*.
6. **Provenance (item 13).** Write the v15 CHANGELOG. Add the "20 %" prior power, the 0.98 m s⁻¹ NZP rms, the TOI radius/K and the photometric-plan simulation to NUMBERS.md. Ship the missing v13 scripts and JSON files with the deposit.
7. **Generative-AI statement.** Make the "every number … released script" and "independent code" sentences accurate (l. 1186–1190).
8. **Build (item 7).** Fix the duplicate hyperref anchors, `LastPage`, the 1.8 pt overfull row in Table 5, and "55 au" → 54 au (l. 795–796).
9. **Item 14 (needs the author).** Create the GitHub user and Zenodo DOI and fill l. 1207–1208.
