# Round-3 re-check of the methods paper (rvvet 0.3.0)

Binary re-check by the second-round reviewer (same instance), 2026-09-29. It edited no project
files. Condensed from the report as delivered; the response is at the end of
`RESPONSE_methods_v2.md`.

**Checks.** `pytest` 38 passed; `analyze.py` re-run on a scratch copy reproduces `numbers.tex`
(356 macros), `numbers.json` and all six `tab_*.tex` byte for byte; over 40 new or changed macros
recomputed from raw files, all match; 4 simulated cases regenerated exactly; the window cap
verified (largest offset 0.500/T).

**Verdicts: 20 of 27 RESOLVED.** NOT RESOLVED: R2-2 (rotation proxy: disclosed, but the fix does not
work and the cause is misstated — see N1); R2-7 (abstract still says "as often inside the lines
as on harmonics", true only with the k = 0 envelope); R2-9 (NUMBERS.md stale); R2-19 (empirical
threshold intervals computed but not printed); R2-21 (Table 3 footnote incomplete; blank space;
float warnings); R1-28 (abstract presents the rule as written in advance without saying its
features were revised).

**New findings**

* N1 (major). Least-squares detrending of heavy-tailed indicators (robust |z| up to ~4000) tilts
  the fitted trend: the proxy rate for simulated planets rose from 0.26 % to 1.4 %, 39 of 72
  proxies in activity-free simulations sit at the 200-d band edge, and for two stars the permuted,
  detrended series reproduce the unpermuted star's proxy exactly. On real stars detrending did not
  reduce the proxy count (17 → 19 of 28); 7 of 19 proxies lie at 180–185 d (half a year), and
  GJ 876 b is rejected because 60.85 d ≈ 183.9/3. Fix: clip before detrending or fit robustly;
  exclude 1-yr and ½-yr aliases and band-edge peaks; rerun; correct the diagnosis.
* N2 (minor). `NUMBERS.md` and `CHANGELOG.md` not updated for 0.3.0.
* N3 (minor). The response cites "Table 5" for the window table; it is Table 4.
* N4 (typo). Sect. 6.4 attributes the round-1 fixes to version 0.3.0.
