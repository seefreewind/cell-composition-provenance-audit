# Claim-level provenance and reusability of cell-composition estimands in single-cell disease studies

Version 1.0.0. Audit freeze: 2026-10-08.

This resource contains frozen derived audit data and reproducible code for **50 claims, 19 papers and 18 cohorts**. It assesses whether the donor set, annotation, numerator and denominator underlying a published composition estimand can be reconstructed under a bounded public-source search.

Class totals: fully reusable 0; partially reusable 13; source-supported non-reusable 5; unresolved 32. The nested chain is 50 → 41 → 15 → 8 → 8 → 1 → 1 → 0. Unresolved evidence is distinct from confirmed absence. The audit does not evaluate biological replication or literature-wide prevalence.

## Contents

- Root TSVs: locked claims, provenance master, cohort relationships, node closure, nested attrition, first stops, reusability classes, clustered sensitivity and QC summaries.
- `Supplementary_Table_Corpus_Flow.tsv`: 418 staged screening events with historical review status and frozen final membership. Events must not be summed as unique papers.
- `docs/`: data dictionary, provenance schema, class rules, reproduction instructions, search strategy and frozen protocols.
- `scripts/reproduce.py`: read-only input-hash verification and numerical reproduction.
- `scripts/figure_generation.py`: generation of Figures 1–4 and S1 solely from frozen audit metadata.
- `scripts/original/`: historical code required by the portable checker; the builder is for inspection, not reclassification of frozen inputs.
- `figures/`: editable SVG reference figures and Figure 3 row keys. PNG and TIFF can be regenerated.
- `FROZEN_INPUT_HASHES.json`: hashes of unchanged audit TSVs; `SHA256SUMS.txt`: release-file hashes.

## Reproduce

Python 3.12+, NumPy 2.3.5 and Matplotlib 3.11.0. In an isolated environment:

```sh
python -m pip install -r requirements.txt
python scripts/reproduce.py --output reproduction_output
python scripts/figure_generation.py --output generated_figures
```

Bootstrap summaries use 10,000 draws and seed 20261008, resetting the random-number generator independently for paper and cohort clustering. Numerical checks and plotting do not modify the frozen classifications. Source re-adjudication would require a separately versioned assessment.

## Access and citation

Code and derived data: https://github.com/seefreewind/cell-composition-provenance-audit. Cite the creators and version using `CITATION.cff`. Version 1.0.0 is archived in Zenodo: https://doi.org/10.5281/zenodo.23235247.

## License and source rights

CC BY 4.0 applies to the original audit software, derived metadata and documentation, as confirmed by the authors. Original publications, quoted evidence anchors and underlying datasets retain their own terms and attribution. No copyrighted article PDFs, third-party expression matrices, raw sequencing files, participant-level objects, credentials or manuscript drafts are included.

## Persistent citation

Lin, D., Chen, Y., Liu, Y. & Zhang, Y. (2026). Claim-level provenance and reusability of cell-composition estimands in single-cell disease studies (Version 1.0.0). Zenodo. https://doi.org/10.5281/zenodo.23235247
