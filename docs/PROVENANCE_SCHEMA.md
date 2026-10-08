# Provenance schema

Paper → claim → cohort → assay → accession/public object → donor → condition → author cell state → numerator → denominator.

This conceptual trace is not a one-to-one relational chain. `claim_id` is the master key; `paper_id`, `cohort_id`, and `assay_id` retain different units. One paper can contain several claims and assays. One biological cohort can appear in several papers, as for GSE131882. Reannotation in a later paper creates a new claim-specific annotation requirement without creating a new biological cohort. An accession can contain multiple assays or only one contrast arm. An assay may not cover every population named elsewhere in a paper.

Donor, sample, library and visit are distinct objects. A paired study can have the same donors in both conditions; unique donors are not the sum of case and control donor counts. Barcode identities need an accession/sample namespace when they repeat across sample files. The resource contains assessments of these mappings, not redistributed participant-level metadata.

The numerator and denominator are claim-specific selections of cells. A parent cell universe can differ from all retained cells. A denominator candidate is not accepted unless its identity and selection rule match the published proportion. The PATS candidate 11,727 versus printed 11,725 remains NEAR_MATCH_UNEXPLAINED. No numeric tolerance or guessed two-cell exclusion is applied.

Node closure is stored as status plus evidence, with missing and unresolved distinguished. The analytical cascade intentionally starts at public source then tests cohort identity; this ordering differs from the conceptual entity trace. `PHASE2P_NODE_CLOSURE.tsv` reports marginal counts (19 cohorts identified). `PHASE2P_NESTED_ATTRITION.tsv` reports nested counts (15 cohorts within 41 verified public sources). Claim source is closed for all 50 claims and assay identity is tracked separately.

This is a domain-specific schema description, not a claim of W3C PROV conformance. The flat master does not encode every accession-to-file or donor-to-cell edge as a separate relational row.
