# Supplementary Methods Search Strategy

This is a curated multi-disease provenance-audit corpus. Query retrieval, sampled candidate selection, provisional paper screening, source inspection and human claim inclusion are different stages. Corpus-flow rows are stage events and must not be summed as unique publications. All records are historical; this revision performed no new composition-source search.

## Documented sequence

- 2026-10-05: PubMed E-utilities across 12 disease strata; publication window 2019-01-01 to 2026-10-05. Relevance cap 500 per stratum. Seed 20261005 for candidate-frame selection; initial screening order used SEED + 1 = 20261006 in scripts/literature_census.py, with the first 30 preserved through screen_sample_plan_initial108.tsv; 180 unique selected candidates (earlier snapshot 108). Sixty were inspected, preserving the initial 30 when extending to 60; 120 were uninspected. Do not call all query hits screened.
- 2026-10-07: initial-screen human source adjudication yielded 12 INCLUDE, 42 EXCLUDE, 6 UNCERTAIN. Six uncertain-record resolutions yielded four source inclusions and two unresolved-source records. PMID36711576 maps to published PMID38374043; it is not another paper. PMID40879186 already contributes to the 13-paper human core.
- 2026-10-07: expansion plan selected 60 previously unscreened PMID records, seed 20261007, same date window and strata, cap 500 per query. The 3,821 search-universe rows represent PMID–stratum memberships, not 3,821 unique eligible papers. Provisional outcomes were 11 INCLUDE, 43 EXCLUDE, 6 UNRESOLVED_SOURCE_UNAVAILABLE. Of potential inclusions, seven were full-text anchored and four abstract-only; all expansion screen human_decision fields were PENDING at that stage.
- The source-confirmed candidate inventory had 23 papers: 13 already represented in the 44-claim locked core, three further uncertain-resolution candidates and seven expansion candidates. Ten candidate claims from the ten further papers were human reviewed on 2026-10-08; six accepted, four rejected. Final: 44 + 6 = 50 claims, 13 + 6 = 19 papers, 18 cohorts.
- Rejected new statements conflated multiple states/directions or included an ineligible treatment contrast. Data non-publicity did not remove otherwise eligible source-supported claims.

## Decision provenance and exclusion details

The TSV preserves all 418 stage events with current final-corpus membership and historical review status. Rows with NOT_SCREENED are not exclusions. Initial exclusions are human decisions; expansion exclusions remain provisional paper-screening decisions. Human final claim decisions are a separate stage. Preserve the historical H_YES_NOT_APPENDED snapshot in the ten-candidate source table; current membership is taken from FINAL_LAYER_A_CLAIMS_v1.1.tsv. Exclusion categories include non-human studies, bulk/flow-only or ineligible modalities, absent qualifying composition contrasts, and inseparable compound statements. Row reasons are verbatim source records, without invented mutually exclusive category totals.

## Primary records

`01_literature/search_results_raw.tsv`, `search_query_counts.tsv`, `manual_screen_60.tsv`, `screening_log.md`; `01_literature/phase1_expansion/query_counts.tsv`, `search_universe.tsv`, `selected_candidates.tsv`, `agent_screen_60.tsv`, `uncertain6_resolution.tsv`, `confirmed_composition_papers.tsv`; `00_protocol/PHASE1_BOUNDED_EXPANSION_PLAN.json`; `02_claim_extraction/phase0H_human_return/HUMAN_GOLD_ADJUDICATION_44_c5625fac86114cfd.tsv`; `02_claim_extraction/gold_standard/PHASE1_NEW_CLAIMS_HUMAN_REVIEW_LOCKED.tsv`; frozen final claim table. HTTP request timestamps in `logs/http_requests.jsonl` independently locate original search_00 requests on 2026-10-05 and expansion on 2026-10-07.

Sampling used PMID deduplication, seeded within-stratum selection and round-robin allocation; publication/preprint normalization was documented during source resolution. No availability, significance or journal-prestige filter was authorized. Query-frame caps, curation, provisional screening and uneven claim counts limit literature-wide generalization.

## Initial exact search strings and retrieval counts

# Search strategy

Date 2026-10-05. PubMed E-utilities; no availability filter. Fixed seed 20261005. Twelve disease strata sampled in round robin; duplicates removed by PMID. Results are query candidates, not verified human composition studies. Top 500 relevance IDs per stratum cap the sampling frame and may introduce relevance bias; no complete-universe prevalence estimates.

## Alzheimer disease

Hits: 1113; IDs retrieved: 500; capped: True.

```text
("single-cell"[Title/Abstract] OR "single nucleus"[Title/Abstract] OR "single-nucleus"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR enrich*[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract] OR "cell state"[Title/Abstract] OR "cell population"[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND Alzheimer*
```

## Parkinson disease

Hits: 397; IDs retrieved: 397; capped: False.

```text
("single-cell"[Title/Abstract] OR "single nucleus"[Title/Abstract] OR "single-nucleus"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR enrich*[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract] OR "cell state"[Title/Abstract] OR "cell population"[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND Parkinson*
```

## multiple sclerosis

Hits: 275; IDs retrieved: 275; capped: False.

```text
("single-cell"[Title/Abstract] OR "single nucleus"[Title/Abstract] OR "single-nucleus"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR enrich*[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract] OR "cell state"[Title/Abstract] OR "cell population"[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND "multiple sclerosis"
```

## SLE

Hits: 291; IDs retrieved: 291; capped: False.

```text
("single-cell"[Title/Abstract] OR "single nucleus"[Title/Abstract] OR "single-nucleus"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR enrich*[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract] OR "cell state"[Title/Abstract] OR "cell population"[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND ("systemic lupus" OR SLE)
```

## rheumatoid arthritis

Hits: 364; IDs retrieved: 364; capped: False.

```text
("single-cell"[Title/Abstract] OR "single nucleus"[Title/Abstract] OR "single-nucleus"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR enrich*[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract] OR "cell state"[Title/Abstract] OR "cell population"[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND "rheumatoid arthritis"
```

## IBD

Hits: 583; IDs retrieved: 500; capped: True.

```text
("single-cell"[Title/Abstract] OR "single nucleus"[Title/Abstract] OR "single-nucleus"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR enrich*[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract] OR "cell state"[Title/Abstract] OR "cell population"[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND ("inflammatory bowel" OR "Crohn*" OR "ulcerative colitis")
```

## COVID-19

Hits: 1149; IDs retrieved: 500; capped: True.

```text
("single-cell"[Title/Abstract] OR "single nucleus"[Title/Abstract] OR "single-nucleus"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR enrich*[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract] OR "cell state"[Title/Abstract] OR "cell population"[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND (COVID-19 OR SARS-CoV-2)
```

## pulmonary fibrosis

Hits: 470; IDs retrieved: 470; capped: False.

```text
("single-cell"[Title/Abstract] OR "single nucleus"[Title/Abstract] OR "single-nucleus"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR enrich*[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract] OR "cell state"[Title/Abstract] OR "cell population"[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND ("pulmonary fibrosis" OR "lung fibrosis")
```

## chronic kidney disease

Hits: 634; IDs retrieved: 500; capped: True.

```text
("single-cell"[Title/Abstract] OR "single nucleus"[Title/Abstract] OR "single-nucleus"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR enrich*[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract] OR "cell state"[Title/Abstract] OR "cell population"[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND ("chronic kidney" OR "kidney disease" OR "diabetic nephropathy")
```

## diabetes

Hits: 1910; IDs retrieved: 500; capped: True.

```text
("single-cell"[Title/Abstract] OR "single nucleus"[Title/Abstract] OR "single-nucleus"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR enrich*[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract] OR "cell state"[Title/Abstract] OR "cell population"[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND (diabetes OR diabetic)
```

## cardiovascular disease

Hits: 3647; IDs retrieved: 500; capped: True.

```text
("single-cell"[Title/Abstract] OR "single nucleus"[Title/Abstract] OR "single-nucleus"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR enrich*[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract] OR "cell state"[Title/Abstract] OR "cell population"[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND (cardiovascular OR "heart failure" OR atherosclerosis OR "myocardial infarction")
```

## cancer

Hits: 20662; IDs retrieved: 500; capped: True.

```text
("single-cell"[Title/Abstract] OR "single nucleus"[Title/Abstract] OR "single-nucleus"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR enrich*[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract] OR "cell state"[Title/Abstract] OR "cell population"[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND (cancer OR carcinoma OR tumor OR tumour)
```

API documentation: [NCBI](https://www.nlm.nih.gov/dataguide/eutilities/utilities.html); [Europe PMC](https://europepmc.org/RestfulWebService).

## Expansion exact queries

### Alzheimer disease

Hits: 445; retrieved: 445; cap: 500.

```text
("single-cell RNA"[Title/Abstract] OR "single cell RNA"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract] OR "single nucleus RNA"[Title/Abstract] OR "single-nucleus RNA"[Title/Abstract]) AND (patient*[Title/Abstract] OR disease[Title/Abstract] OR case[Title/Abstract] OR control[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR frequency[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR enrich*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract]) AND (humans[MeSH Terms] OR human[Title/Abstract] OR patients[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND Alzheimer*
```

### Parkinson disease

Hits: 144; retrieved: 144; cap: 500.

```text
("single-cell RNA"[Title/Abstract] OR "single cell RNA"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract] OR "single nucleus RNA"[Title/Abstract] OR "single-nucleus RNA"[Title/Abstract]) AND (patient*[Title/Abstract] OR disease[Title/Abstract] OR case[Title/Abstract] OR control[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR frequency[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR enrich*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract]) AND (humans[MeSH Terms] OR human[Title/Abstract] OR patients[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND Parkinson*
```

### multiple sclerosis

Hits: 114; retrieved: 114; cap: 500.

```text
("single-cell RNA"[Title/Abstract] OR "single cell RNA"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract] OR "single nucleus RNA"[Title/Abstract] OR "single-nucleus RNA"[Title/Abstract]) AND (patient*[Title/Abstract] OR disease[Title/Abstract] OR case[Title/Abstract] OR control[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR frequency[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR enrich*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract]) AND (humans[MeSH Terms] OR human[Title/Abstract] OR patients[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND "multiple sclerosis"
```

### SLE

Hits: 162; retrieved: 162; cap: 500.

```text
("single-cell RNA"[Title/Abstract] OR "single cell RNA"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract] OR "single nucleus RNA"[Title/Abstract] OR "single-nucleus RNA"[Title/Abstract]) AND (patient*[Title/Abstract] OR disease[Title/Abstract] OR case[Title/Abstract] OR control[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR frequency[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR enrich*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract]) AND (humans[MeSH Terms] OR human[Title/Abstract] OR patients[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND ("systemic lupus" OR SLE)
```

### rheumatoid arthritis

Hits: 157; retrieved: 157; cap: 500.

```text
("single-cell RNA"[Title/Abstract] OR "single cell RNA"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract] OR "single nucleus RNA"[Title/Abstract] OR "single-nucleus RNA"[Title/Abstract]) AND (patient*[Title/Abstract] OR disease[Title/Abstract] OR case[Title/Abstract] OR control[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR frequency[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR enrich*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract]) AND (humans[MeSH Terms] OR human[Title/Abstract] OR patients[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND "rheumatoid arthritis"
```

### IBD

Hits: 266; retrieved: 266; cap: 500.

```text
("single-cell RNA"[Title/Abstract] OR "single cell RNA"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract] OR "single nucleus RNA"[Title/Abstract] OR "single-nucleus RNA"[Title/Abstract]) AND (patient*[Title/Abstract] OR disease[Title/Abstract] OR case[Title/Abstract] OR control[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR frequency[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR enrich*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract]) AND (humans[MeSH Terms] OR human[Title/Abstract] OR patients[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND ("inflammatory bowel" OR "Crohn*" OR "ulcerative colitis")
```

### COVID-19

Hits: 497; retrieved: 497; cap: 500.

```text
("single-cell RNA"[Title/Abstract] OR "single cell RNA"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract] OR "single nucleus RNA"[Title/Abstract] OR "single-nucleus RNA"[Title/Abstract]) AND (patient*[Title/Abstract] OR disease[Title/Abstract] OR case[Title/Abstract] OR control[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR frequency[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR enrich*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract]) AND (humans[MeSH Terms] OR human[Title/Abstract] OR patients[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND (COVID-19 OR SARS-CoV-2)
```

### pulmonary fibrosis

Hits: 248; retrieved: 248; cap: 500.

```text
("single-cell RNA"[Title/Abstract] OR "single cell RNA"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract] OR "single nucleus RNA"[Title/Abstract] OR "single-nucleus RNA"[Title/Abstract]) AND (patient*[Title/Abstract] OR disease[Title/Abstract] OR case[Title/Abstract] OR control[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR frequency[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR enrich*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract]) AND (humans[MeSH Terms] OR human[Title/Abstract] OR patients[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND ("pulmonary fibrosis" OR "lung fibrosis")
```

### chronic kidney disease

Hits: 288; retrieved: 288; cap: 500.

```text
("single-cell RNA"[Title/Abstract] OR "single cell RNA"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract] OR "single nucleus RNA"[Title/Abstract] OR "single-nucleus RNA"[Title/Abstract]) AND (patient*[Title/Abstract] OR disease[Title/Abstract] OR case[Title/Abstract] OR control[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR frequency[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR enrich*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract]) AND (humans[MeSH Terms] OR human[Title/Abstract] OR patients[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND ("chronic kidney" OR "kidney disease" OR "diabetic nephropathy")
```

### diabetes

Hits: 567; retrieved: 500; cap: 500.

```text
("single-cell RNA"[Title/Abstract] OR "single cell RNA"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract] OR "single nucleus RNA"[Title/Abstract] OR "single-nucleus RNA"[Title/Abstract]) AND (patient*[Title/Abstract] OR disease[Title/Abstract] OR case[Title/Abstract] OR control[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR frequency[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR enrich*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract]) AND (humans[MeSH Terms] OR human[Title/Abstract] OR patients[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND (diabetes OR diabetic)
```

### cardiovascular disease

Hits: 1140; retrieved: 500; cap: 500.

```text
("single-cell RNA"[Title/Abstract] OR "single cell RNA"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract] OR "single nucleus RNA"[Title/Abstract] OR "single-nucleus RNA"[Title/Abstract]) AND (patient*[Title/Abstract] OR disease[Title/Abstract] OR case[Title/Abstract] OR control[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR frequency[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR enrich*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract]) AND (humans[MeSH Terms] OR human[Title/Abstract] OR patients[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND (cardiovascular OR "heart failure" OR atherosclerosis OR "myocardial infarction")
```

### cancer

Hits: 6722; retrieved: 500; cap: 500.

```text
("single-cell RNA"[Title/Abstract] OR "single cell RNA"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR snRNA-seq[Title/Abstract] OR "single nucleus RNA"[Title/Abstract] OR "single-nucleus RNA"[Title/Abstract]) AND (patient*[Title/Abstract] OR disease[Title/Abstract] OR case[Title/Abstract] OR control[Title/Abstract]) AND (proportion*[Title/Abstract] OR abundance[Title/Abstract] OR composition[Title/Abstract] OR frequency[Title/Abstract] OR expand*[Title/Abstract] OR deplet*[Title/Abstract] OR enrich*[Title/Abstract] OR increas*[Title/Abstract] OR decreas*[Title/Abstract]) AND (humans[MeSH Terms] OR human[Title/Abstract] OR patients[Title/Abstract]) AND ("2019/01/01"[Date - Publication] : "2026/10/05"[Date - Publication]) AND (cancer OR carcinoma OR tumor OR tumour)
```

