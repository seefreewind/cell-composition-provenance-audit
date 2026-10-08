# Reproduction instructions

Python 3.12+ with NumPy 2.3.5 and Matplotlib 3.11.0 was used for portable summary/figure checks. The inputs were audited before this packaging stage. No network access is needed for reproduction.

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/reproduce.py --output reproduction_output
.venv/bin/python scripts/figure_generation.py --output figures
```

The first command verifies frozen SHA256 values, class totals, unique papers/cohorts, marginal and nested closure, stop totals, rule consistency, and clustered-bootstrap limits against the released tables. It uses seed 20261008 and 10,000 draws. Paper and cohort bootstraps each initialize a fresh RNG with that seed, as in the historical QC. Zero-event limits remain non-informative. Summary recomputation does not rerun abundance models, source discovery, or human adjudication.

The second command draws four main figures and one supplement from frozen metadata in SVG (editable text), PNG and 600-dpi TIFF. It exports a row-key table for Figure 3. No new PDF is produced. Claimed cell counts in the four-case figure are frozen source-audit descriptions, not new third-party data analysis.

The historical scripts are preserved in `scripts/original/` for inspection. They expect the original project folder structure and are NOT the portable entry points. The builder contains paper defaults and claim overrides and writes classifications; do not run it against the frozen release. Portable reproduction deliberately reads the final classifications instead.

Reproducing the public-source adjudications themselves requires revisiting the cited publications/repository objects under the bounded protocol. Copyrighted source documents and participant datasets are excluded here. The provided summaries support numerical reproducibility of the audit, not independent certification of source interpretation. Later source changes must become a separately versioned audit.
