# Reusability class rules

Preserve the frozen classifications. The implementation is `scripts/original/phase2p_build_audit.py::rule_class`; the source audit remains necessary to interpret each status.

1. `NOT_REUSABLE`: the frozen primary reason is ASSAY_SCOPE_MISMATCH with a verified public accession, or accession status is VERIFIED_NOT_PUBLIC. In this corpus these rules identify five source-supported claims. The broader protocol reserves the class for confirmed non-public or missing required information; unfound objects do not qualify.
2. `FULLY_REUSABLE`: verified cohort, assay, public source, donor and condition; author label EXACT_AUTHOR_LABEL or DETERMINISTIC_COLLAPSE; numerator and denominator EXACT or RECONSTRUCTABLE.
3. `PARTIALLY_REUSABLE`: cohort and assay each VERIFIED or PARTIAL, public source VERIFIED_PUBLIC or PARTIAL_PUBLIC, and at least one recovered-tail status. The actual tail accepts donor VERIFIED/PARTIAL, author label EXACT_AUTHOR_LABEL/DETERMINISTIC_COLLAPSE/REFERENCE_MAPPING_REQUIRED, numerator EXACT/RECONSTRUCTABLE, or denominator EXACT/RECONSTRUCTABLE/NEAR_MATCH_UNEXPLAINED. This is partial evidence, not closure of those nodes. It explains the seven white-matter claims with partial donor design.
4. Otherwise `UNRESOLVED`.

The order above matters. No private information is inferred. UNRESOLVED is a search-boundary outcome, not UNAVAILABLE. Missing-like legacy failure flags cannot override node evidence. No biological-validity or replication verdict is attached to any class.

The closure score is descriptive. EXACT_AUTHOR_LABEL, DETERMINISTIC_COLLAPSE, VERIFIED, VERIFIED_PUBLIC, EXACT and RECONSTRUCTABLE receive 1; PARTIAL, PARTIAL_PUBLIC, REFERENCE_MAPPING_REQUIRED, AMBIGUOUS and NEAR_MATCH_UNEXPLAINED receive 0.5; other statuses receive 0. The total does not replace the categorical criteria.
