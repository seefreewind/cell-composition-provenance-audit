# PHASE 0H-R prespecified label equivalence rule

Date: 2026-10-07. Freeze this rule before reviewing/scoring the 44 records. This is a protocol amendment before biological outcome analysis. No donor-aware statistics have run.

EXACT_LABEL_MATCH and BIOLOGICAL_LABEL_EQUIVALENCE are separate metrics. Historical exact-name result ORIGINAL_EXTRACTION 41/44 =93.2% and its three mismatches are immutable. No historical score is recalculated by this policy.

## Review universe and independence

Review all 44 fixed claims from the returned human reconciliation reference. Compare original_extractor_label with human_source_label, using original paper/figure/legend/supplement/author metadata to support nonlexical equivalence. The reviewer is an independent fresh-context agent evaluating a user-supplied human reference; its output is source-supported equivalence review, not new human gold. It cannot edit the human answers, extraction output, code or claim IDs. Report YES/NO/NOT_ASSESSABLE with exact-match status, rule and source support for every row.

## Permitted rules

EXACT: Equality after the historical Unicode NFC/whitespace-only normalization. This baseline equality is biological equivalence without a semantic expansion; reference source anchors must still be retained.

RULE_1_SINGULAR_PLURAL: Singular/plural differences only, with unchanged subtype/state/cluster identity. Do not strip arbitrary ending letters or collapse biologically distinct names. Treg/Tregs is eligible only when the same source population is involved.

RULE_2_AUTHOR_ABBREVIATION: Expand abbreviations only when the author source explicitly establishes the full-name relation. Cite the source statement and location; common knowledge is insufficient. Keep state/cluster modifiers unchanged.

RULE_3_TYPOGRAPHY: Ignore only case, hyphen, underscore, Unicode typography or spacing differences that carry no population/state distinction. Do not erase meaningful symbols or cluster/state IDs.

RULE_4_SOURCE_SAME_POPULATION: Expanded wording is equivalent only with explicit source support that both names identify the same original population. Cite evidence; do not infer by similarity.

Multiple permitted rules may be recorded. If no permitted/source-supported relation exists, NO for incompatible populations and NOT_ASSESSABLE for unresolved evidence. Do not remove unresolved records from the denominator.

## Prohibited substitutions

No parent-child, state-type or ontology-neighbor substitutions: CD4 T cell/Treg, microglia/DAM, fibroblast/myofibroblast, oligodendrocyte/OPC, monocyte/macrophage are not automatically equivalent. No guessing cluster biology, broad-for-subtype replacement or harmonized naming. Preserve source-defined labels and all claim IDs.

## Metrics and selection

Exact-label accuracy stays 41/44. Biological-label equivalence accuracy = number YES /44, including NO and NOT_ASSESSABLE in the denominator. Report all decisions, source coverage and the three exact mismatches separately.

Select ORIGINAL_EXTRACTION only if frozen human-core validity >=0.90, direction >=0.95 and source-reviewed biological equivalence >=0.95. V2 is excluded from selection and retained only as a historical architecture. No tuning/re-extraction permitted.

If selected, FINAL Layer A truth comes from the returned human reference, not extractor outputs or reviewer substitutions. Future workflow: paper -> original extractor -> candidate claims -> human claim-core verification -> final Layer A. Independent agents are DISAGREEMENT_FLAGGER only, not extractors/universal verifiers; flags never overwrite human truth.

Selection authorizes Phase 1 SOURCE AUDIT only (literature, cohort/accession/assay/donor provenance, labels, denominator and data availability). No Phase 1 work is performed during this phase. PHASE2_STATISTICAL_ANALYSIS_AUTHORIZED = NO; no propeller/sccomp/scCODA or abundance testing.
