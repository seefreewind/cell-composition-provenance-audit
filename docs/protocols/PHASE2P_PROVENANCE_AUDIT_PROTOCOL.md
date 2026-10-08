# Phase 2P provenance and reusability audit protocol

Frozen: 2026-10-08

Claim table: `FINAL_LAYER_A_CLAIMS_v1.1.tsv`, 50 human-locked claims. Direction, cell-state label, and claim validity are not edited because a public file is incomplete.

This audit asks whether a third party can rebuild the published composition estimand from public materials. It does not ask whether the biological statement is true.

## Units

The row unit is `claim_id`. `paper_id`, `cohort_id`, and `assay_id` are retained. One paper may contain several claims. One cohort may underlie several papers.

## Nine nodes

P1 claim source is `VERIFIED` or `UNRESOLVED`.

P2 cohort identity, P3 assay identity, P5 donor identity, and P6 condition identity are `VERIFIED`, `PARTIAL`, `UNRESOLVED`, or, for P5 and P6, `CONFIRMED_MISSING`.

P4 public source is `VERIFIED_PUBLIC`, `VERIFIED_NOT_PUBLIC`, `PARTIAL_PUBLIC`, or `UNRESOLVED`.

P7 author cell state is `EXACT_AUTHOR_LABEL`, `DETERMINISTIC_COLLAPSE`, `REFERENCE_MAPPING_REQUIRED`, `CONFIRMED_NOT_AVAILABLE`, or `UNRESOLVED`.

P8 numerator is `EXACT`, `RECONSTRUCTABLE`, `AMBIGUOUS`, `CONFIRMED_NOT_AVAILABLE`, or `UNRESOLVED`.

P9 denominator is `EXACT`, `RECONSTRUCTABLE`, `NEAR_MATCH_UNEXPLAINED`, `MISMATCH`, `CONFIRMED_NOT_AVAILABLE`, or `UNRESOLVED`. A denominator is not inferred from a plausible cell universe. A two-cell gap without a source rule remains `NEAR_MATCH_UNEXPLAINED`.

## Reusability

`FULLY_REUSABLE` requires a verified cohort and assay, a public source, verified donor and condition, an exact or deterministic label, and an exact or reconstructable numerator and denominator.

`PARTIALLY_REUSABLE` requires cohort, assay, and a public source, plus at least one recovered donor, label, numerator, or denominator node, with at least one key node still open.

`NOT_REUSABLE` requires a source-supported confirmed absence: data not public, case data absent, labels confirmed absent, the claimed population outside the assay, or donor mapping confirmed absent. Failure to find a file is not this class.

`UNRESOLVED` is used when the search stops without confirming presence or absence.

These four classes are reported separately.

## Search stop

Stop after the main article, its supplement when already in the project, the primary repository record, an author code link when the paper gives one, and the source paper when the dataset is reused. Do not continue into an open-ended search.

## Verification levels

0, the paper says data were deposited. 1, an accession exists. 2, a relevant file exists. 3, a file was opened. 4, a required metadata field was checked. 5, the claim-specific numerator and denominator were both reconstructed.

## Out of primary scope

GSE250498 has no human-locked disease-versus-control claim. Treatment contrasts are not provenance failures and are not in the 50.

## Statistics

Study-clustered bootstrap intervals describe the audit classes. No abundance model is part of this protocol.
