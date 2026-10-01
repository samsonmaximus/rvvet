# v14 changelog

v14 implements the frozen 16-item acceptance list of the *Referee-Lens Report (v13)*, rewrites
the paper so it states what was done and found instead of arguing with a referee, and rebuilds
it in the real A&A class. v13 is untouched in its own folder.

## Frozen acceptance list: done / not done

| # | Item | Status | Where / note |
|---|---|---|---|
| 1 | Abstract and Summary give the full FAP/FIP range | **Done, one deviation** | Abstract and Summary 1 give FAP 1.4e-3 (all epochs), 1.7 expected archive false alarms, 7e-6 without the night, FIP of order 1e-4 / 0.17. The fixed-jitter value 0.45 is in Sect. 4.3 and Summary item 1 with its reason, **not** in the abstract (see trade-offs). |
| 2 | Summary orders the reasons: significance, one instrument, rotation | Done | Summary item 5 |
| 3 | Pre-registration language cut to one sentence stating the deposit postdates the runs | Done | Sect. 2.2, last sentence. "Written down before" removed from Sects. 2.3, 5.6, 7.1 and Table 1. |
| 4 | Sect. 4.4 has the window-percentile contrast with the 200.9-d signal | Done | Sect. 4.4, first paragraph |
| 5 | Held-out test opens Sect. 5; its figure is Fig. 2 | Done | Sect. 5.1; Fig. 2 (placed in Sect. 4.2, where the detection first needs it) |
| 6 | Quasi-periodic GP named in the main text as the primary alternative | Done | Sect. 4.1, second paragraph: ΔlnZ +9.71, K = 5.63 ± 0.99 m/s (new number, see below) |
| 7 | Model ladder and ASAS-SN detail in appendices, two sentences each in the text | Done | Appendix B (ladder, Table B.1), Appendix E (ASAS-SN); Sect. 4.1/4.3 and 5.7 keep two sentences each |
| 8 | "The planet in context" rewritten: ridge, TOI-6263.01 architecture, follow-up prediction | Done | Sect. 8.1, now the first Discussion section |
| 9 | Corner plot of the adopted-model posterior | Done | Fig. 4, from a new nested-sampling run of the adopted model (`figs_corner.py`) |
| 10 | Hara et al. (2022, A&A 658, A177) cited for the Gaussian-envelope test | Done | Sect. 5.2 (`Hara2022b`) |
| 11 | Rebuilt in aa.cls with aa.bst and A&A citations; no half-empty float pages | Done | aa.cls v9.2 (2024-08-08), aa.bst. 14 pages. |
| 12 | Title has no "strong", says "Neptune-mass" | Done | |
| 13 | Abstract ≤ 250 words | Done | 236 words (each math expression counted as one) |
| 14 | Placeholders filled (Zenodo DOI, GitHub user); Shappee note removed | **Not done: needs you** | Shappee note removed. `ZENODODOI` and `GITHUBUSER` need a Zenodo deposit and a GitHub repository that only you can create (see README). |
| 15 | Acknowledgements: all ESO programme IDs, Gemini/Zorro, TFOP, MAST texts; Zorro observers contacted | **Text done; contact needs you** | All 18 programme IDs; verbatim NOIRLab/Zorro, ExoFOP, MAST texts. Emailing the Zorro team is yours to do; name them in the acknowledgements after they reply. |
| 16 | RV table prepared for CDS; RVBank version cited with URL | Done | `cds/ReadMe`, `cds/rv.dat` (104 epochs, DRS and nine indicators); Appendix G sample table; title footnote; Sect. 2.1 cites CDS J/A+A/683/A125 (table4 corrected 2026-04-20) and GitHub Ver.02 with URLs |

## Trade-offs (stated, not absorbed)

1. **FIP 0.45 kept out of the abstract.** The report asked for "FIP from 1e-4 to 0.45 depending on
   the noise frame". The 0.45 is not a different noise frame: it is the FIP with the jitters fixed at
   their planet-free values, which lets the jitters absorb the signal and is not how Hara et al. define
   the FIP. Quoting it as a bound would mislead a referee in the other direction. The abstract gives
   the properly marginalised range (1e-4 to 0.17); Sect. 4.3 gives 0.45 with the reason, and says the
   white-noise frame is disfavoured by 24.7 nats against the GP on the planet-free model.
2. **"Neptunian ridge" claimed in period only.** Castro-González et al. (2024) mapped the ridge for
   planets of 4–10 R⊕ (the overdensity itself at 5.5–8.5 R⊕). Chen & Kipping put HD 297396 b at
   3.4–3.8 R⊕, just below that. The paper says "in the period range of the Neptunian ridge" and
   "at the low-mass edge of the ridge population", not "a ridge Neptune".
3. **The migration argument is ours, not Castro-González et al. (2026).** That paper does not discuss
   inner companions (checked). The argument that high-eccentricity migration destroys inner planets
   is cited to Mustill et al. (2015), who show it for migrating giants; the paper says so.
4. **Follow-up promise scaled down.** The report said one ESPRESSO season would take K/σK to about 20,
   give a mass to a few per cent and reach the 0.4 m/s of TOI-6263.01. With the 3–4 m/s stellar jitter
   fitted here, 40 epochs give 6–8σ (σK ≈ σ√(2/N)); v13's "a few per cent" was also wrong and is gone.
   TOI-6263.01 at 0.4 m/s is out of reach of one season, so it is not promised.
5. **Sreenivas prior footnote corrected.** v13 called U(18, 25) and U(5, 15) period priors; they are
   the K priors (checked against the paper's Table 2).
6. **Rotation section shortened.** Details that defended the 36–42-d estimate were cut to two
   sentences (weaker in the second half of the baseline; programme groups differ by 5 d).
7. **Some caveats moved, none deleted.** The 5.1975-d peak in the 57-epoch group, the selection
   dependence of the programme split, the third sinusoid, the eccentric mode, the DRS evidence gap and
   the discrepant-night leverage are all still in the paper; most now sit in one sentence or in an
   appendix instead of interrupting the argument.

## New numbers in v14 (provenance in NUMBERS.md)

* QP GP semi-amplitude at its maximum-likelihood covariance: 5.63 ± 0.99 m/s (104), 5.47 ± 0.83 (103).
* Transit geometry: TOI-6263.01 transits only for i > 84.7°; b escapes transit only for i < 85.7°;
  for 1–2° mutual inclination, sin i > 0.99.
* Follow-up estimate: 40 epochs at 3–4 m/s give K/σK = 6.2–8.2.
* Corner-plot posterior (Fig. 4), repeat run of the adopted model (`gpns.py 1p in 7`, lnZ = −738.17 ± 0.26):
  P = 4.268371 ± 0.00026 d, K = 5.40 ± 0.79 m/s (0.15σ from Table 3), T_conj = 6298.35 ± 0.10,
  A_RV = 2.9 (+2.2/−1.6) m/s, log10 ℓ = 2.84 (+0.23/−0.32).
* Ephemeris from that posterior: phase uncertainty (1σ) 0.069 of an orbit in 2024 March and 0.088 at the
  end of 2028. **Correction to v13:** v13's CHANGELOG said P and T_conj were anti-correlated so the
  0.09 bound was conservative; the posterior shows a correlation of +0.34, and the direct propagation
  gives 0.088–0.092. v14 says "to within 0.1 of an orbit (1σ) through 2028".

## Structure

Sect. 4.1 now names the QP GP; 4.3 gives evidence and FIP in plain terms; Sect. 5 opens with the
programme split; Sect. 6 is one paragraph; Discussion opens with "The planet in context", then the
comparison, the failure screens and "What will confirm it". Appendices: A priors/sampler/FIP,
B noise-model ladder (old Table 3), C one-outlier mixture, D discrepant night, E ASAS-SN, F TESS,
G velocities (CDS).

## Independent review pass

A second reviewer compared v14 with v13 line by line. Everything it found was fixed:

* Restored caveats: every analysis choice came after the signal was found (Sect. 2.2); the full-band
  cells that are indecisive (Sect. 6); "at amplitudes the data allow" for the 70 000 simulations
  (abstract, Summary); the correlated-noise qualifier on "least favourable"; the cross-star sample is
  not matched in spectral type or mask; Nava et al. (2020) on non-harmonic activity peaks; K is
  comparable to the per-epoch scatter; the screens describe past failures, not every failure; the
  block-activity test is weak; HD 47186 b and HD 181433 b were loud signals around quieter stars; 36–42 d
  is a candidate rotation period, not a measurement.
* Fixed: "phases agree to within 1°" (now the two measured phases); "the window cannot make P0"
  (now what separates the two signals); Table 5 "Noise fluctuation" verdict is now "disfavoured";
  the order of the >100 / >47 ratios; the corner caption; the FIP-frame agreement (1 nat same code,
  about 2 nats juliet); "written rule" wording; the Table B.1 overflow; the CDS footnote ("in full").
