# HD 297396 b: v12 → v13

Overnight pass, 2026-09-25. Every number below was computed from the public RVBank rows
(`HD297396_rvbank_full.csv`) with the scripts in `analysis/`, or read from the source paper
named. The v12 folder is untouched.

Three groups: **errors fixed** (a referee would have caught them), **new tests** (a referee
would have asked for them), and **wording** (claims that went further than the evidence).
After the first draft of v13, an independent referee-style check (a separate agent that
read the manuscript against the three source papers) found a second round of issues; those
fixes are included below and marked (R).

---

## 1. Errors fixed

| # | Where | v12 said | v13 says | Why |
|---|---|---|---|---|
| E1 | Sect. 8.1, Table 7 | HD 105779 b has "the same semi-amplitude (5.27 ± 0.45 m/s)"; K/σK 11.7. HD 103891 b K = 14.78 ± 0.30, K/σK 49, ΔlnZ +86.5 | HD 105779 b K = 10.42 ± 0.96, K/σK 10.9, ΔlnZ +35.1. HD 103891 b K = 21.12 ± 0.86, K/σK 24.6, ΔlnZ +94.3 | Checked against Sreenivas et al. 2022, Tables 3–4 (`2112.09029v1.pdf` in your folder). 5.27 ± 0.45 was our own K from v7–v11 pasted into the wrong column, and the "same semi-amplitude" argument was the centre of the comparison. +86.5 is their DRS value. Paragraph rewritten. |
| E2 | Sect. 4.2 | Baluev = 4.9e-5, "30× more optimistic than the bootstrap, so we do not use it"; 103-epoch FAP "≈3e-6, extrapolated" | Baluev = 2.2e-3 (104) and 6.7e-6 (103), agreeing with the bootstrap; 7e-6 quoted for 103 | Baluev's formula bounds the FAP from above; it cannot sit 30× below a correct bootstrap. `baluev.py`. |
| E3 | Sect. 3.2 | Noyes τc = 34.1 d, Rossby 0.84; Rossby at P0 = 0.13 | τc = 23.7 d, Rossby 1.21 (P_rot 28.6 d, unchanged); Rossby at P0 = 0.18 | Your own `phase9/kinematics/kinematics.json` has 23.6 d and 1.206. 34.1 d is 8 × P0, pasted from the harmonic list. |
| E4 | Sect. 4.5 | "R_p ≈ 2.5 R⊕ at this mass [Chen & Kipping]", 960 ppm | Chen & Kipping 3.4 R⊕ (1800 ppm); Earth-like 2.0 R⊕ (600 ppm); TOI-6263.01 130 ppm | Chen & Kipping at 11.8 M⊕ gives 3.4 R⊕. The conclusion now rests on the most conservative radius. |
| E5 | Sect. 2.3, Table 1 | C2 rejects 1 spectrum | C2 flags 2 (one also fails C4); 2 rejected | `core.py` prints `rejected C2 2`. |
| E6 | Sect. 8.3 | Out-of-sample prediction 5.5 ± 1.0 m/s, "≈1.2σ test" | 5.2 ± 2.7 m/s, ≈1σ | The ±1.0 left out the orbital-phase uncertainty, which matters because the 2024 March spectrum falls where the velocity curve is steepest. |
| E7 | Sect. 5.6 | "period held constant to about ±1 min" | "3 parts in 10⁵ … about one minute for a 30-d rotation period" | Ambiguous before. |
| E8 | Sect. 8.2, Table 8 | "semi-amplitude is four times the per-epoch error" | "four times the median formal error but only comparable to the per-epoch scatter once jitter is included (4–6 m/s)" | With jitter the scatter is 4–6 m/s; the forward simulation is the real argument. |
| E9 (R) | Sect. 5.8, Table 6 | "gap at 1.8–3 au where no probe is sensitive" | The velocities themselves exclude stellar/brown-dwarf companions there (P = 2.7–5.9 yr) | A stellar companion at 2–3 au would be a signal of hundreds of m/s in 17.9 yr of RVs. |
| E10 (R) | Sect. 8.3 | Gaia reflex 0.34 μas | 0.05 μas | Arithmetic. Conclusion unchanged. |
| E11 (R) | Sect. 5.1 | Bonferroni 0.0057 | 0.0056 | 0.05/9. |
| E12 (R) | Sect. 6 | expected largest \|z\| for 103 draws 2.59 | 2.7 | 2.59 is the once-exceeded level, not the expected maximum. |
| E13 (R) | Sect. 5.5 | "Δχ² = 44.6 before the NZP correction" | 31.9 and 44.6 for the two sets | 44.6 is the 103-epoch value. `nonzp.py`. |
| E14 (R) | Sect. 6 | 3.7 nats = "1.5 times the run-to-run scatter" | "about twice the 1.7-nat run-to-run scatter" | Arithmetic. |
| E15 (R) | Sect. 7.1 | 200.9-d evidence "+3.85 after the prior-width correction" | "+3.85 after widening that prior to 10–1000 d"; P2 prior (Jeffreys 150–260 d) added to Table A.1 | The correction was to 10–1000 d (`phase3/p3run.py`), not the 1.05–1000 d used for b. |
| E16 (R) | Table 7 | HD 22496 residual rms "…"; baseline "895 d"; HD 103891 "91 RVs", M sin i 1.44 ± 0.02, P/P_rot > 48; HD 105779 e < 0.16 unlabelled | 0.28 m/s; 895 d ESPRESSO, 17.4 yr with HARPS; 90 RVs (one removed by the authors); 1.44 +0.06/−0.05; > 47; e < 0.16 is 1σ, HD 22496's < 0.15 is 95 % | Checked against the source papers. |
| E17 (R) | Sect. 8.1 | HD 22496 "9 % semi-amplitude from 41 epochs"; "no 895-d data set could bound [the coherence]" | 8 % from ESPRESSO plus 43 HARPS points; coherence sentence rewritten | Their K comes from the joint ESPRESSO+HARPS fit, which spans 17 yr. |
| E18 (R) | Sect. 5.8, abstract | companions excluded "0.02–100 au" | "0.02 au to the edge of the speckle contrast curve (typically 1.2″, ≈55 au)" | Zorro contrast curves usually stop near 1.2″. **Check the actual curve on ExoFOP**: if it reaches further, restore the larger number. |

## 2. New tests

(T1–T10: new analyses added at a referee's likely request; not defects. Omitted here except
where they record a correction.)

| # | Test | Result (excerpt relevant to corrections) |
|---|---|---|
| T3b | A candidate rotation period: 36–42 d | ... (A draft argument comparing a 350-d "evolution time" with the P0 coherence was dropped after the referee check: the λ of a nearly aperiodic kernel is not a spot lifetime.) |
| T7 | Eccentricity | ... the −2.93-nat "eccentric disfavoured" result with all epochs is flagged as unreliable; the circular orbit is now justified by the 103-epoch limit. |

## 3. Comparison table (Table 7)

* Sreenivas numbers corrected; rows added for log R'HK, residual rms, the period prior of
  each evidence, FAP and FIP. The footnote now says that Sreenivas et al. chose their P and K
  priors to maximise ΔlnZ, and that Lillo-Box et al. also report a wide-prior result.
* **HD 47186 b** (Bouchy et al. 2009) added as a fifth column.
* The text now says plainly how HD 297396 b differs: half to a quarter of the Sreenivas
  semi-amplitudes, a more active host, and an orbit inside the rotation period.

## 4. Wording tightened (mostly from the referee-style check)

* P_rot is "estimated", not "bounded" (it comes from activity calibrations).
* Abstract: "none of 612 other HARPS stars" (not "no other HARPS star"); "saturation-corrected
  ASAS-SN" (the aperture ASAS-SN photometry does show 11.9 mmag at P0); the forward model uses
  "the amplitude the data would detect nine times in ten" (not "the largest permitted").
* Held-out test: the two programme groups share period and phase; amplitudes agree within
  1.4σ (v12 said "same amplitude"; 6.5 ± 0.7 vs 4.9 ± 0.9).
* Sect. 6: under the full-band prior the weakest cells (DRS adopted, white noise with all
  epochs) are indecisive; v12 said "every treatment gives a detection".
* Forward model: "stronger than any spot model in its coherence, not in its harmonic content".
* Coherence: spot patterns evolve over one to a few rotations (v12: "about one").
* 200.9-d signal: added that its strength is a caution in its own right.
* Cross-star control: states it is not matched in spectral type or mask.
* "Metal-rich" → "near-solar metallicity" ([Fe/H] = +0.11 ± 0.12).
* ESPRESSO follow-up: "semi-amplitude to a few per cent" (v12: "mass below 5 %", which the
  6 % stellar-mass error forbids).
* Rotation at P0 also excluded by TESS (< 63 ppm at P0) and the activity level (Rossby 0.18
  would imply log R'HK ≈ −4.3).
* Mamajek & Hillenbrand (2008) added as a second rotation calibration (27.6 d).
* New references: Bouchy 2009, Horner 2019, Hara 2022, Mortier & Collier Cameron 2017,
  Zeng 2019 (DOIs checked).

## Conclusions rewrite (2026-09-25, after the overnight run)

(Rewrite of the abstract conclusions; not a record of defects.)

---
Note added 2026-09-29 when this copy was made for the defect-log study: sections 2 and
"Conclusions rewrite" are abridged; the full file is `claude/CHANGELOG_v13.md` in the
project. Nothing in sections 1 and 4 was abridged.
