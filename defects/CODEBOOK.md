# Defect log: unit of analysis and codebook

Fixed 2026-09-29 before any item was coded. Sources: the records written at the time of each
revision of the HD 297396 b manuscript, in `sources/`:
`CHANGELOG_v13.md` (v12 -> v13), `CHANGELOG_v14.md` (v13 -> v14), `CHANGELOG_v15.md` (v14 -> v15),
`REFEREE_v15.md` (the independent referee report on the first v15 build) and `refcheck.md` (the
automated reference check of v15).

## Unit of analysis

A **defect** is one statement, number, figure element, reference or analysis step, present in a
version of the manuscript or its released files, that a record says was changed or removed
because it was wrong, unsupported, stale, inconsistent or ambiguous.

* One root cause = one defect, even if it appears in several places (e.g. one wrong radius
  repeated in the abstract and a table is one defect; "eight statements left on the superseded
  range" is one defect).
* Two different wrong values in one table row are two defects if they have different causes.
* NOT defects: new analyses or tests added on request; restructuring, moving or shortening text;
  added references; cosmetic LaTeX warnings that did not change content; placeholders the author
  must fill; items a reviewer marked DONE or verified.
* A defect in a draft that the record says was caught before release (e.g. "the first v15
  build said ...") counts, with `stage = draft`.
* When a reviewer raised an issue and the record says it was not acted on, it is not a defect
  (note it in `excluded.csv` with the reason).

## Fields

* `id` — stable id (use the record's own id where it has one, e.g. E7, N3, S10; otherwise
  v14-RP-3 for the third item of the v14 review pass, v15-F2 for "found, not on the list" item
  2, v13-W5 for the fifth wording bullet, etc.).
* `version` — the version in which the defect was found (v13, v14, v15).
* `stage` — `released` (present in a previous released version) or `draft` (caught in a draft
  of the same version).
* `quote` — a short verbatim quote from the record identifying the defect.
* `route` — who found it, **as the record states it**, one of:
  - `self-review` — found by the author and assistant while revising or checking against
    sources, scripts or catalogues (v13 items not marked (R); corrections the v14/v15 logs
    describe as found by checking);
  - `independent-reviewer` — found by the independent referee-style agent (v13 items marked (R);
    v14 "Independent review pass"; issues in `REFEREE_v15.md` that the v15 log says were fixed);
  - `external-report` — raised by the "Referee-Lens Report (v13)" that the v14 acceptance list
    implements;
  - `reference-check` — found by the automated reference check (`refcheck.md`);
  - `unattributed` — the record does not say (e.g. v13 section 4, "mostly from the
    referee-style check").
* `category` — one of (mutually exclusive; choose the first that applies):
  1. `transcription` — a value copied wrongly from a source (a script output, a paper, a
     catalogue) or placed in the wrong spot, or a value from one data set quoted for another.
  2. `arithmetic` — a calculation done wrongly, a wrong statistic, a rounding error.
  3. `method` — an analysis whose design or inputs were wrong (wrong scale, missing
     uncertainty term, invalid bound, a simulation that cannot test what it claims).
  4. `overclaim` — a claim stronger than the evidence supports, or a needed caveat missing.
  5. `stale` — text left inconsistent with a change made elsewhere (superseded values,
     statements contradicting the revised analysis).
  6. `reasoning` — a wrong inference or argument that is not about a number.
  7. `reference` — wrong bibliographic data, or a claim attributed to the wrong paper.
  8. `wording` — ambiguous or misleading wording, labels, captions or file metadata that
     do not change a result.
* `origin` — where the wrong content came from:
  - `code-to-text` — a number produced by the project's own scripts, carried into text/tables;
  - `literature-to-text` — a value or statement taken from a paper, catalogue or archive;
  - `analysis` — the analysis or code itself was wrong;
  - `interpretation` — prose interpretation, with no specific number at fault;
  - `revision` — introduced by revising a previous version (e.g. caveats dropped in a rewrite,
    numbers not updated after a change).

Coders assign `category` and `origin` independently; `route` and `stage` are read from the record.
Disagreements are resolved by a third reading and both codings are kept.
