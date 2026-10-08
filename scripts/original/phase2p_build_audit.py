#!/usr/bin/env python3
"""Phase 2P provenance audit tables, scores, and figures.

Classifications use opened project files and quoted data-availability statements.
A node that was not opened stays UNRESOLVED.
"""

from __future__ import annotations

import csv
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "02_claim_extraction" / "FINAL_LAYER_A_CLAIMS_v1.1.tsv"

# Defaults by paper. Claim overrides win.
PAPER = {
    "PMID40879186": dict(
        cohort_id="COHORT_MS_ANTI_CD20", assay_id="COHORT_MS_ANTI_CD20__CITE",
        assay_type="CITE-seq", assay_status="VERIFIED",
        cohort_status="VERIFIED", cohort_evidence="Article: treatment-naive relapsing MS versus healthy PBMC.",
        accession="NONE_PUBLIC", accession_status="VERIFIED_NOT_PUBLIC", accession_role="none",
        processed_object_status="CONFIRMED_NOT_PUBLIC", level=0,
        donor_status="CONFIRMED_MISSING", condition_status="CONFIRMED_MISSING",
        author_label_status="CONFIRMED_NOT_AVAILABLE",
        numerator_status="CONFIRMED_NOT_AVAILABLE", denominator_status="CONFIRMED_NOT_AVAILABLE",
        reusability_class="NOT_REUSABLE", primary_failure_node="NO_PUBLIC_DATA",
        design="INDEPENDENT_CASE_CONTROL",
        notes="Data availability: release on reasonable request. No public accession.",
        confidence="HIGH",
    ),
    "PMID32754283": dict(
        cohort_id="COHORT_CKTR", assay_id="COHORT_CKTR__SCRNA",
        assay_type="scRNA", assay_status="PARTIAL",
        cohort_status="PARTIAL",
        cohort_evidence="Article uses GSE131685 healthy adult kidney as the control arm. Case biopsy matrices were not located.",
        accession="GSE131685", accession_status="PARTIAL_PUBLIC", accession_role="control_only_named",
        processed_object_status="CONTROL_SERIES_LISTED_NOT_OPENED", level=1,
        donor_status="UNRESOLVED", condition_status="PARTIAL",
        author_label_status="UNRESOLVED",
        numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="UNRESOLVED", primary_failure_node="UNRESOLVED",
        secondary_failure_nodes="CASE_DATA_MISSING",
        design="INDEPENDENT_CASE_CONTROL|REUSED_COHORT",
        notes="Control GEO series is named. Case deposition was not confirmed absent from every supplement, so this is not NOT_REUSABLE.",
        confidence="MEDIUM",
    ),
    "PMID41699549": dict(
        cohort_id="COHORT_HCC_GSE245906", assay_id="COHORT_HCC_GSE245906__INNATE",
        assay_type="scRNA", assay_status="VERIFIED",
        cohort_status="VERIFIED",
        cohort_evidence="Opened metadata: 10 patients, paired HCC and adjacent non-tumor libraries.",
        accession="GSE245906", accession_status="VERIFIED_PUBLIC", accession_role="primary_processed_metadata",
        processed_object_status="METADATA_OPENED_COUNTS_NOT_FULLY_OPENED", level=4,
        donor_status="VERIFIED", condition_status="VERIFIED",
        donor_evidence="patient IDs 12,13,14,16,17,18,19,20,23,24; one HCC and one NT library each.",
        condition_evidence="tissue field HCC versus NT.",
        author_label_status="UNRESOLVED",
        numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="PARTIALLY_REUSABLE", primary_failure_node="UNRESOLVED",
        secondary_failure_nodes="AUTHOR_LABEL_MISSING|PAIRED_DESIGN_AMBIGUITY",
        design="PAIRED_TISSUE|MULTI_ASSAY",
        notes="Sort is CD45+ panTCRab- CD19- innate cells. Cluster numbers 0-21 are stored. Biological names were not in the opened metadata. Journal supplement was not downloaded.",
        confidence="HIGH",
        n_unique_donors=10, n_case_donors=10, n_control_donors=10, paired="YES",
    ),
    "PMID32661339": dict(
        cohort_id="COHORT_IPF_GSE135893", assay_id="COHORT_IPF_GSE135893__SCRNA",
        assay_type="scRNA", assay_status="VERIFIED",
        cohort_status="VERIFIED",
        cohort_evidence="Opened metadata Diagnosis field separates IPF from Control and from other ILD labels.",
        accession="GSE135893", accession_status="VERIFIED_PUBLIC", accession_role="primary_cell_metadata",
        processed_object_status="METADATA_OPENED", level=4,
        donor_status="VERIFIED", condition_status="VERIFIED",
        donor_evidence="Sample_Name is 1:1 with Diagnosis; 12 IPF and 10 Control sample names.",
        condition_evidence="Diagnosis IPF versus Diagnosis Control.",
        author_label_status="DETERMINISTIC_COLLAPSE",
        author_label_evidence="Public celltype KRT5-/KRT17+ is the paper's PATS rename.",
        numerator_status="RECONSTRUCTABLE", numerator_definition="KRT5-/KRT17+ cells",
        numerator_evidence="485 cells with that label.",
        denominator_status="NEAR_MATCH_UNEXPLAINED",
        denominator_definition="four alveolar labels AT1, AT2, Transitional AT2, KRT5-/KRT17+",
        denominator_evidence="Public four-label set is 11727. Figure text prints 11725. No source rule excludes 2 cells.",
        reusability_class="PARTIALLY_REUSABLE", primary_failure_node="DENOMINATOR_MISSING",
        design="INDEPENDENT_CASE_CONTROL",
        notes="Exemplar. Numerator reconstructable. Denominator not closed. Not FULLY_REUSABLE.",
        confidence="HIGH",
        n_unique_donors=22, n_case_donors=12, n_control_donors=10,
    ),
    "PMID31506348": dict(
        cohort_id="COHORT_DN_GSE131882", assay_id="COHORT_DN_GSE131882__SNRNA",
        assay_type="snRNA", assay_status="VERIFIED",
        cohort_status="VERIFIED",
        cohort_evidence="Six GEO samples, three diabetic and three control, opened as count matrices.",
        accession="GSE131882", accession_status="VERIFIED_PUBLIC", accession_role="raw_counts",
        processed_object_status="RAW_COUNTS_OPENED_NO_LABEL_TABLE", level=4,
        donor_status="VERIFIED", condition_status="VERIFIED",
        donor_evidence="One file per sample. Sample membership is the donor key. Barcodes are not globally unique.",
        condition_evidence="GEO disease state diabetic versus control.",
        author_label_status="UNRESOLVED",
        numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="PARTIALLY_REUSABLE", primary_failure_node="UNRESOLVED",
        secondary_failure_nodes="AUTHOR_LABEL_MISSING",
        design="INDEPENDENT_CASE_CONTROL",
        notes="Author labels are absent from the opened RDS objects. The lab browser was not fetched, so absence from every public copy is not confirmed.",
        confidence="HIGH",
        n_unique_donors=6, n_case_donors=3, n_control_donors=3,
    ),
    "PMID37312900": dict(
        cohort_id="COHORT_DN_GSE131882", assay_id="COHORT_DN_GSE131882__SNRNA",
        assay_type="snRNA", assay_status="VERIFIED",
        cohort_status="VERIFIED",
        cohort_evidence="Same GSE131882 samples as PMID31506348. Claims stay separate.",
        accession="GSE131882", accession_status="VERIFIED_PUBLIC", accession_role="reused_raw_counts",
        processed_object_status="RAW_COUNTS_OPENED_NO_LABEL_TABLE", level=4,
        donor_status="VERIFIED", condition_status="VERIFIED",
        donor_evidence="Same six sample files.",
        condition_evidence="Same diabetic versus control sample labels.",
        author_label_status="REFERENCE_MAPPING_REQUIRED",
        author_label_evidence="Paper annotates a refiltered object with CellMarker/scHCL. Those names are not columns in the opened GEO matrices.",
        numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="PARTIALLY_REUSABLE", primary_failure_node="UNRESOLVED",
        secondary_failure_nodes="AUTHOR_LABEL_MISSING|SHARED_COHORT_AMBIGUITY",
        design="INDEPENDENT_CASE_CONTROL|REUSED_COHORT",
        notes="Shared cohort with PMID31506348. A supplementary barcode table was not downloaded.",
        confidence="HIGH",
        n_unique_donors=6, n_case_donors=3, n_control_donors=3,
    ),
    "PMID40359016": dict(
        cohort_id="COHORT_EARLY_MS_GSE267750", assay_id="COHORT_EARLY_MS_GSE267750__SCRNA",
        assay_type="scRNA", assay_status="VERIFIED",
        cohort_status="PARTIAL",
        cohort_evidence="Series lists 32 records. Article describes 16 people at two time points plus external controls. Cell file not opened.",
        accession="GSE267750", accession_status="VERIFIED_PUBLIC", accession_role="raw_archive_listed",
        processed_object_status="RAW_TAR_LISTED_NOT_OPENED", level=1,
        donor_status="UNRESOLVED", condition_status="UNRESOLVED",
        author_label_status="UNRESOLVED", numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="UNRESOLVED", primary_failure_node="UNRESOLVED",
        secondary_failure_nodes="LONGITUDINAL_DESIGN_AMBIGUITY",
        design="LONGITUDINAL|REUSED_COHORT",
        notes="External control studies were not opened.",
        confidence="MEDIUM",
    ),
    "PMID41578022": dict(
        cohort_id="COHORT_COPD_GSE310058", assay_id="COHORT_COPD_GSE310058__SNRNA",
        assay_type="snRNA", assay_status="VERIFIED",
        cohort_status="PARTIAL",
        cohort_evidence="Article reports 141 participants and 146 lobes. Series has 149 records. Metadata table not opened.",
        accession="GSE310058", accession_status="VERIFIED_PUBLIC", accession_role="raw_archive_listed",
        processed_object_status="ARCHIVE_LISTED_NOT_OPENED", level=1,
        donor_status="UNRESOLVED", condition_status="UNRESOLVED",
        author_label_status="UNRESOLVED", numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="UNRESOLVED", primary_failure_node="UNRESOLVED",
        design="MULTI_REGION",
        notes="Lobe versus donor reconciliation was not done in an opened table.",
        confidence="MEDIUM",
    ),
    "PMID41937210": dict(
        cohort_id="COHORT_CARDIAC_ATLAS", assay_id="COHORT_CARDIAC_ATLAS__SNRNA",
        assay_type="snRNA", assay_status="PARTIAL",
        cohort_status="PARTIAL",
        cohort_evidence="Integrated atlas of prior studies. Constituent donor overlap was not rebuilt.",
        accession="GSE290367", accession_status="VERIFIED_PUBLIC", accession_role="integrated_object_listed",
        processed_object_status="H5AD_LISTED_NOT_OPENED", level=1,
        donor_status="UNRESOLVED", condition_status="UNRESOLVED",
        author_label_status="UNRESOLVED", numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="UNRESOLVED", primary_failure_node="UNRESOLVED",
        secondary_failure_nodes="SHARED_COHORT_AMBIGUITY",
        design="REUSED_COHORT|MULTI_ASSAY|MIXED_DESIGN",
        notes="snATAC is a second modality and is not the composition assay.",
        confidence="MEDIUM",
    ),
    "PMID40744996": dict(
        cohort_id="COHORT_SLE_GSE254176", assay_id="COHORT_SLE_GSE254176__SCRNA",
        assay_type="scRNA", assay_status="VERIFIED",
        cohort_status="PARTIAL",
        cohort_evidence="Article: 6 SLE donors and longitudinal samples versus controls. Cell-to-timepoint file not opened.",
        accession="GSE254176", accession_status="VERIFIED_PUBLIC", accession_role="raw_archive_listed",
        processed_object_status="RAW_TAR_LISTED_NOT_OPENED", level=1,
        donor_status="UNRESOLVED", condition_status="UNRESOLVED",
        author_label_status="UNRESOLVED", numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="UNRESOLVED", primary_failure_node="UNRESOLVED",
        secondary_failure_nodes="LONGITUDINAL_DESIGN_AMBIGUITY",
        design="LONGITUDINAL|INDEPENDENT_CASE_CONTROL",
        notes="Sample count is not a donor count.",
        confidence="MEDIUM",
    ),
    "PMID35662411": dict(
        cohort_id="COHORT_PREG_SARSCOV2", assay_id="COHORT_PREG_SARSCOV2__CD3_5P",
        assay_type="scRNA", assay_status="PARTIAL",
        cohort_status="PARTIAL",
        cohort_evidence="Decidual T-cell claims are tied to a CD3-sorted 5-prime assay. Other assays in the paper use different cohort sizes.",
        accession="PRJNA817521", accession_status="VERIFIED_PUBLIC", accession_role="bioproject_named",
        processed_object_status="MATRICES_NOT_OPENED", level=1,
        donor_status="UNRESOLVED", condition_status="UNRESOLVED",
        author_label_status="UNRESOLVED", numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="UNRESOLVED", primary_failure_node="UNRESOLVED",
        secondary_failure_nodes="ASSAY_SCOPE_MISMATCH",
        design="MULTI_ASSAY|INDEPENDENT_CASE_CONTROL",
        notes="Assay-to-claim mapping is not closed from an opened object.",
        confidence="MEDIUM",
    ),
    "PMID36848564": dict(
        cohort_id="COHORT_COVID_LUNG", assay_id="COHORT_COVID_LUNG__SCRNA",
        assay_type="scRNA", assay_status="PARTIAL",
        cohort_status="PARTIAL",
        cohort_evidence="Five COVID lungs versus pooled control lungs from four source studies.",
        accession="GSE149878;GSE122960;GSE163919;GSE158127",
        accession_status="VERIFIED_PUBLIC", accession_role="reused_source_series",
        processed_object_status="NOT_OPENED", level=1,
        donor_status="UNRESOLVED", condition_status="UNRESOLVED",
        author_label_status="UNRESOLVED", numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="UNRESOLVED", primary_failure_node="UNRESOLVED",
        secondary_failure_nodes="SHARED_COHORT_AMBIGUITY",
        design="REUSED_COHORT|MIXED_DESIGN",
        notes="Joint barcode and cluster-4 label were not opened.",
        confidence="MEDIUM",
    ),
    "PMID34019156": dict(
        cohort_id="COHORT_CTE_GSE155114", assay_id="COHORT_CTE_GSE155114__SNRNA",
        assay_type="snRNA", assay_status="VERIFIED",
        cohort_status="VERIFIED",
        cohort_evidence="README: 16 donors, 8 CTE and 8 controls, multiple libraries per donor.",
        accession="GSE155114", accession_status="VERIFIED_PUBLIC", accession_role="readme_and_count_archive",
        processed_object_status="README_OPENED_RAW_NOT_OPENED", level=2,
        donor_status="PARTIAL", condition_status="PARTIAL",
        donor_evidence="README names the 16-donor design. A barcode-to-donor table was not opened.",
        condition_evidence="README assigns samples to CTE or control. Cell-level condition was not checked.",
        author_label_status="UNRESOLVED",
        numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="PARTIALLY_REUSABLE", primary_failure_node="UNRESOLVED",
        secondary_failure_nodes="DONOR_MAP_MISSING|AUTHOR_LABEL_MISSING",
        design="INDEPENDENT_CASE_CONTROL",
        notes="Count matrices are described. Author oligodendrocyte and astrocyte names were not in the README.",
        confidence="MEDIUM",
        n_unique_donors=16, n_case_donors=8, n_control_donors=8,
    ),
    "PMID35549656": dict(
        cohort_id="COHORT_COPD_PBEC_ALI", assay_id="COHORT_COPD_PBEC_ALI__SCRNA",
        assay_type="scRNA", assay_status="VERIFIED",
        cohort_status="VERIFIED",
        cohort_evidence="Article: 4 COPD and 3 healthy cultured bronchial epithelium donors.",
        accession="NONE_LOCATED", accession_status="UNRESOLVED", accession_role="bulk_geo_only",
        processed_object_status="NOT_OPENED", level=0,
        donor_status="UNRESOLVED", condition_status="UNRESOLVED",
        author_label_status="UNRESOLVED", numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="UNRESOLVED", primary_failure_node="UNRESOLVED",
        design="INDEPENDENT_CASE_CONTROL",
        notes="Named GEO accessions in the text are bulk validation, not the scRNA object.",
        confidence="MEDIUM",
    ),
    "PMID41629974": dict(
        cohort_id="COHORT_NMOSD_NK", assay_id="COHORT_NMOSD_NK__SCRNA",
        assay_type="scRNA", assay_status="VERIFIED",
        cohort_status="VERIFIED",
        cohort_evidence="Figure 3e: NK proportion, healthy controls versus acute NMOSD PBMC.",
        accession="NONE_PUBLIC", accession_status="VERIFIED_NOT_PUBLIC", accession_role="none",
        processed_object_status="CONFIRMED_NOT_PUBLIC", level=0,
        donor_status="CONFIRMED_MISSING", condition_status="CONFIRMED_MISSING",
        author_label_status="CONFIRMED_NOT_AVAILABLE",
        numerator_status="CONFIRMED_NOT_AVAILABLE", denominator_status="CONFIRMED_NOT_AVAILABLE",
        reusability_class="NOT_REUSABLE", primary_failure_node="NO_PUBLIC_DATA",
        design="INDEPENDENT_CASE_CONTROL|MULTI_ASSAY",
        notes="Data availability: not publicly available because of patient privacy. Flow cytometry is a separate modality.",
        confidence="HIGH",
    ),
    "PMID32511460": dict(
        cohort_id="COHORT_HF_ACE2", assay_id="COHORT_HF_ACE2__SCRNA",
        assay_type="scRNA", assay_status="PARTIAL",
        cohort_status="PARTIAL",
        cohort_evidence="Article reports ACE2-positive frequencies within cardiomyocyte subsets. Primary accession not verified.",
        accession="UNRESOLVED", accession_status="UNRESOLVED", accession_role="unknown",
        processed_object_status="NOT_SEARCHED_BEYOND_STOP", level=0,
        donor_status="UNRESOLVED", condition_status="UNRESOLVED",
        author_label_status="UNRESOLVED", numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="UNRESOLVED", primary_failure_node="UNRESOLVED",
        design="INDEPENDENT_CASE_CONTROL",
        notes="Search stopped after the project full text and the unresolved accession record.",
        confidence="LOW",
    ),
    "PMID38187779": dict(
        cohort_id="COHORT_MS_ROSMAP_NONLESIONAL", assay_id="COHORT_MS_ROSMAP__SNRNA",
        assay_type="snRNA", assay_status="VERIFIED",
        cohort_status="PARTIAL",
        cohort_evidence="Non-lesional DLPFC, MS or demyelination versus matched non-MS. ROSMAP reuse.",
        accession="UNRESOLVED", accession_status="UNRESOLVED", accession_role="controlled_access_possible",
        processed_object_status="NOT_OPENED", level=0,
        donor_status="UNRESOLVED", condition_status="UNRESOLVED",
        author_label_status="UNRESOLVED", numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="UNRESOLVED", primary_failure_node="UNRESOLVED",
        secondary_failure_nodes="SHARED_COHORT_AMBIGUITY",
        design="REUSED_COHORT|INDEPENDENT_CASE_CONTROL",
        notes="Controlled-access donor files were not requested.",
        confidence="LOW",
    ),
    "PMID42292441": dict(
        cohort_id="COHORT_SSC_ILD", assay_id="COHORT_SSC_ILD__SCRNA",
        assay_type="scRNA", assay_status="PARTIAL",
        cohort_status="PARTIAL",
        cohort_evidence="Reanalysis of public lung datasets GSE128169 and GSE159354. Matrices not opened.",
        accession="GSE128169;GSE159354", accession_status="VERIFIED_PUBLIC", accession_role="reused_source_series",
        processed_object_status="NOT_OPENED", level=1,
        donor_status="UNRESOLVED", condition_status="UNRESOLVED",
        author_label_status="UNRESOLVED", numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="UNRESOLVED", primary_failure_node="UNRESOLVED",
        secondary_failure_nodes="SHARED_COHORT_AMBIGUITY",
        design="REUSED_COHORT",
        notes="Which object carries the TREM2 macrophage label was not opened.",
        confidence="MEDIUM",
    ),
    "PMID42433374": dict(
        cohort_id="COHORT_T1D_ISLET", assay_id="COHORT_T1D_ISLET__MIXED",
        assay_type="other", assay_status="PARTIAL",
        cohort_status="PARTIAL",
        cohort_evidence="Named accessions mix bulk and single-cell islet cohorts.",
        accession="GSE181674;GSE50244;GSE162689", accession_status="PARTIAL_PUBLIC",
        accession_role="mixed_bulk_and_single_cell",
        processed_object_status="NOT_OPENED", level=1,
        donor_status="UNRESOLVED", condition_status="UNRESOLVED",
        author_label_status="UNRESOLVED", numerator_status="UNRESOLVED", denominator_status="UNRESOLVED",
        reusability_class="UNRESOLVED", primary_failure_node="UNRESOLVED",
        secondary_failure_nodes="ASSAY_SCOPE_MISMATCH",
        design="REUSED_COHORT|MIXED_DESIGN|MULTI_ASSAY",
        notes="The myeloid claim was not tied to one opened single-cell object.",
        confidence="MEDIUM",
    ),
}

CLAIM_OVERRIDE = {
    "PMID41699549_C001": dict(
        reusability_class="NOT_REUSABLE",
        primary_failure_node="ASSAY_SCOPE_MISMATCH",
        secondary_failure_nodes="PAIRED_DESIGN_AMBIGUITY",
        numerator_status="CONFIRMED_NOT_AVAILABLE",
        denominator_status="CONFIRMED_NOT_AVAILABLE",
        author_label_status="CONFIRMED_NOT_AVAILABLE",
        notes="Cytotoxic CD4 T cells are outside the innate sort (panTCRab-negative, CD19-negative).",
    ),
    "PMID41699549_C003": dict(
        reusability_class="NOT_REUSABLE",
        primary_failure_node="ASSAY_SCOPE_MISMATCH",
        secondary_failure_nodes="PAIRED_DESIGN_AMBIGUITY",
        numerator_status="CONFIRMED_NOT_AVAILABLE",
        denominator_status="CONFIRMED_NOT_AVAILABLE",
        author_label_status="CONFIRMED_NOT_AVAILABLE",
        notes="Hepatocytes are outside the CD45-positive innate sort.",
    ),
}

GRANULARITY = {
    "PMID40879186_C001": "SUBTYPE",
    "PMID40879186_C002": "BROAD_CELL_TYPE",
    "PMID32754283_C001": "CLUSTER_DERIVED_STATE",
    "PMID32754283_C002": "CLUSTER_DERIVED_STATE",
    "PMID41699549_C001": "ACTIVATION_STATE",
    "PMID41699549_C002": "DISEASE_STATE",
    "PMID41699549_C003": "BROAD_CELL_TYPE",
    "PMID32661339_C001": "TRANSITIONAL_STATE",
    "PMID31506348_C001": "BROAD_CELL_TYPE",
    "PMID37312900_C001": "SUBTYPE",
    "PMID37312900_C002": "BROAD_CELL_TYPE",
    "PMID37312900_C003": "SUBTYPE",
    "PMID35549656_C001": "BROAD_CELL_TYPE",
    "PMID41629974_C001": "BROAD_CELL_TYPE",
    "PMID32511460_C001": "SUBTYPE",
    "PMID38187779_C001": "SUBTYPE",
    "PMID42292441_C001": "SUBTYPE",
    "PMID42433374_C001": "BROAD_CELL_TYPE",
}

DENOM_TAXON = {
    "PMID32661339_C001": "CUSTOM_SUBSET",
    "PMID35662411_C001": "ALL_T_CELLS",
    "PMID35662411_C002": "ALL_T_CELLS",
    "PMID35662411_C003": "ALL_T_CELLS",
    "PMID35662411_C004": "ALL_T_CELLS",
    "PMID40359016_C001": "ALL_B_CELLS",
    "PMID40359016_C002": "ALL_B_CELLS",
    "PMID40359016_C003": "ALL_B_CELLS",
    "PMID41699549_C001": "UNKNOWN",
    "PMID41699549_C003": "UNKNOWN",
}


def denom_taxon(claim):
    if claim["claim_id"] in DENOM_TAXON:
        return DENOM_TAXON[claim["claim_id"]]
    tissue = claim["tissue"].lower()
    label = claim["original_cell_label"].lower()
    if "b-cell compartment" in tissue or "b cell" in tissue:
        return "ALL_B_CELLS"
    if "t-cell" in tissue or "t cell" in tissue:
        return "ALL_T_CELLS"
    if "myeloid" in tissue:
        return "ALL_MYELOID"
    if "epithelial" in tissue:
        return "ALL_EPITHELIAL"
    if "immune" in tissue:
        return "ALL_IMMUNE"
    if "nucle" in tissue:
        return "ALL_NUCLEI"
    if any(x in label for x in ["oligodend", "astrocyte", "cardiomyocyte", "hepatocyte"]):
        return "UNKNOWN"
    return "UNKNOWN"


def granularity(claim):
    cid = claim["claim_id"]
    if cid in GRANULARITY:
        return GRANULARITY[cid]
    label = claim["original_cell_label"].lower()
    if "cluster" in label:
        return "CLUSTER_DERIVED_STATE"
    if any(x in label for x in ["il1b", "trem2", "ace2", "gaba", "cd69", "cd5", "senescent", "cytotoxic"]):
        return "SUBTYPE"
    if any(x in label for x in ["activated", "naive", "memory", "transitional"]):
        return "ACTIVATION_STATE"
    if any(x in label for x in ["leukocyte", "monocyte", "neutrophil", "nk", "myeloid", "plasma", "hepatocyte", "goblet", "club"]):
        return "BROAD_CELL_TYPE"
    if any(x in label for x in ["cd4", "cd8", "treg", "b cell", "plasmablast"]):
        return "SUBTYPE"
    return "SUBTYPE"


def node_score(status):
    if status in {
        "VERIFIED", "VERIFIED_PUBLIC", "EXACT_AUTHOR_LABEL", "DETERMINISTIC_COLLAPSE",
        "EXACT", "RECONSTRUCTABLE",
    }:
        return 1.0
    if status in {"PARTIAL", "PARTIAL_PUBLIC", "NEAR_MATCH_UNEXPLAINED", "AMBIGUOUS", "REFERENCE_MAPPING_REQUIRED"}:
        return 0.5
    return 0.0


def rule_class(row):
    if row["primary_failure_node"] == "ASSAY_SCOPE_MISMATCH" and row["accession_status"] == "VERIFIED_PUBLIC":
        return "NOT_REUSABLE"
    if row["accession_status"] == "VERIFIED_NOT_PUBLIC":
        return "NOT_REUSABLE"
    keys_ok = (
        row["cohort_status"] == "VERIFIED"
        and row["assay_status"] == "VERIFIED"
        and row["accession_status"] == "VERIFIED_PUBLIC"
        and row["donor_status"] == "VERIFIED"
        and row["condition_status"] == "VERIFIED"
        and row["author_label_status"] in {"EXACT_AUTHOR_LABEL", "DETERMINISTIC_COLLAPSE"}
        and row["numerator_status"] in {"EXACT", "RECONSTRUCTABLE"}
        and row["denominator_status"] in {"EXACT", "RECONSTRUCTABLE"}
    )
    if keys_ok:
        return "FULLY_REUSABLE"
    recovered_tail = row["donor_status"] in {"VERIFIED", "PARTIAL"} or row["author_label_status"] in {
        "EXACT_AUTHOR_LABEL", "DETERMINISTIC_COLLAPSE", "REFERENCE_MAPPING_REQUIRED"
    } or row["numerator_status"] in {"EXACT", "RECONSTRUCTABLE"} or row["denominator_status"] in {
        "EXACT", "RECONSTRUCTABLE", "NEAR_MATCH_UNEXPLAINED"
    }
    if (
        row["cohort_status"] in {"VERIFIED", "PARTIAL"}
        and row["assay_status"] in {"VERIFIED", "PARTIAL"}
        and row["accession_status"] in {"VERIFIED_PUBLIC", "PARTIAL_PUBLIC"}
        and recovered_tail
        and not keys_ok
    ):
        return "PARTIALLY_REUSABLE"
    return "UNRESOLVED"


def main():
    claims = list(csv.DictReader(CLAIMS.open(), delimiter="\t"))
    assert len(claims) == 50
    rows = []
    for c in claims:
        base = dict(PAPER[c["paper_id"]])
        base.update(CLAIM_OVERRIDE.get(c["claim_id"], {}))
        row = {
            "claim_id": c["claim_id"],
            "paper_id": c["paper_id"],
            "cohort_id": base["cohort_id"],
            "assay_id": base["assay_id"],
            "disease": c["disease"],
            "tissue": c["tissue"],
            "cell_state": c["original_cell_label"],
            "direction": c["direction"],
            "claim_source_status": "VERIFIED",
            "claim_source_evidence": c["evidence_location"],
            "cohort_status": base["cohort_status"],
            "cohort_evidence": base["cohort_evidence"],
            "assay_status": base["assay_status"],
            "assay_type": base["assay_type"],
            "assay_evidence": base["assay_type"] + "; " + base["cohort_evidence"],
            "accession": base["accession"],
            "accession_status": base["accession_status"],
            "accession_role": base["accession_role"],
            "processed_object_status": base["processed_object_status"],
            "public_data_verification_level": base["level"],
            "donor_status": base["donor_status"],
            "donor_evidence": base.get("donor_evidence", ""),
            "condition_status": base["condition_status"],
            "condition_evidence": base.get("condition_evidence", ""),
            "author_label_status": base["author_label_status"],
            "author_label_evidence": base.get("author_label_evidence", ""),
            "numerator_status": base["numerator_status"],
            "numerator_definition": base.get("numerator_definition", c["original_cell_label"]),
            "numerator_evidence": base.get("numerator_evidence", ""),
            "denominator_status": base["denominator_status"],
            "denominator_definition": base.get("denominator_definition", ""),
            "denominator_evidence": base.get("denominator_evidence", ""),
            "denominator_taxonomy": denom_taxon(c) if not base.get("denominator_definition") else (
                "CUSTOM_SUBSET" if c["claim_id"] == "PMID32661339_C001" else denom_taxon(c)
            ),
            "claim_granularity": granularity(c),
            "reusability_class": base["reusability_class"],
            "primary_failure_node": base["primary_failure_node"],
            "secondary_failure_nodes": base.get("secondary_failure_nodes", ""),
            "audit_confidence": base["confidence"],
            "notes": base["notes"],
            "design": base["design"],
            "n_unique_donors": base.get("n_unique_donors", ""),
            "n_case_donors": base.get("n_case_donors", ""),
            "n_control_donors": base.get("n_control_donors", ""),
            "paired_design": base.get("paired", "YES" if "PAIRED" in base["design"] else "NO"),
            "longitudinal_design": "YES" if "LONGITUDINAL" in base["design"] else "NO",
            "multiple_tissues": "YES" if "MULTI_REGION" in base["design"] else "NO",
            "multiple_assays": "YES" if "MULTI_ASSAY" in base["design"] else "NO",
            "reused_public_dataset": "YES" if "REUSED" in base["design"] else "NO",
            "sorting_enrichment": "YES" if c["paper_id"] in {"PMID41699549", "PMID35662411"} else "NO_OR_UNRESOLVED",
            "scRNA_vs_snRNA": base["assay_type"],
            "broad_vs_fine_state": "BROAD" if granularity(c) == "BROAD_CELL_TYPE" else "FINE",
            "parent_lineage_denominator": "YES" if denom_taxon(c) not in {"ALL_CELLS", "ALL_NUCLEI", "UNKNOWN"} else "NO_OR_UNKNOWN",
            "publication_year": "",
            "journal": "",
            "report_donor_n": "YES" if base.get("n_unique_donors") else "UNRESOLVED",
            "report_sample_n": "UNRESOLVED",
            "report_cell_n": "YES" if c["claim_id"] == "PMID32661339_C001" else "UNRESOLVED",
            "report_accession_linked": "YES" if base["accession_status"] in {"VERIFIED_PUBLIC", "PARTIAL_PUBLIC", "VERIFIED_NOT_PUBLIC"} else "NO",
            "report_author_labels_public": "YES" if base["author_label_status"] in {"EXACT_AUTHOR_LABEL", "DETERMINISTIC_COLLAPSE"} else "NO_OR_UNRESOLVED",
            "report_sample_donor_map": "YES" if base["donor_status"] == "VERIFIED" else "NO_OR_UNRESOLVED",
            "report_case_control_public": "YES" if base["condition_status"] == "VERIFIED" else "NO_OR_UNRESOLVED",
            "report_denominator_text": "YES" if c["claim_id"] == "PMID32661339_C001" else "UNRESOLVED",
            "report_denominator_legend": "YES" if c["claim_id"] == "PMID32661339_C001" else "UNRESOLVED",
            "report_code_public": "UNRESOLVED",
            "report_processed_object": "YES" if base["level"] >= 3 else "NO_OR_UNRESOLVED",
        }
        expected = rule_class(row)
        if expected != row["reusability_class"]:
            raise SystemExit(f"class mismatch {row['claim_id']}: assigned {row['reusability_class']} rule {expected}")
        scores = [
            node_score(row[k]) for k in [
                "claim_source_status", "cohort_status", "assay_status", "accession_status",
                "donor_status", "condition_status", "author_label_status",
                "numerator_status", "denominator_status",
            ]
        ]
        row["provenance_closure_score"] = sum(scores)
        rows.append(row)

    master_fields = [
        "claim_id", "paper_id", "cohort_id", "assay_id", "disease", "tissue", "cell_state", "direction",
        "claim_source_status", "claim_source_evidence", "cohort_status", "cohort_evidence",
        "assay_status", "assay_type", "assay_evidence", "accession", "accession_status", "accession_role",
        "processed_object_status", "public_data_verification_level", "donor_status", "donor_evidence",
        "condition_status", "condition_evidence", "author_label_status", "author_label_evidence",
        "numerator_status", "numerator_definition", "numerator_evidence",
        "denominator_status", "denominator_definition", "denominator_evidence", "denominator_taxonomy",
        "claim_granularity", "reusability_class", "primary_failure_node", "secondary_failure_nodes",
        "audit_confidence", "provenance_closure_score", "notes",
    ]
    out = ROOT / "03_data_availability" / "PHASE2P_MASTER_CLAIM_PROVENANCE.tsv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, master_fields, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    # Cohort design, one row per cohort.
    seen = {}
    for r in rows:
        seen.setdefault(r["cohort_id"], r)
    with (ROOT / "03_data_availability" / "PHASE2P_COHORT_DESIGN.tsv").open("w", newline="") as fh:
        fields = ["cohort_id", "paper_ids", "design_tags", "n_claims", "n_unique_donors", "n_case_donors", "n_control_donors", "accession"]
        w = csv.DictWriter(fh, fields, delimiter="\t")
        w.writeheader()
        by = defaultdict(list)
        for r in rows:
            by[r["cohort_id"]].append(r)
        for cid, group in by.items():
            w.writerow({
                "cohort_id": cid,
                "paper_ids": ";".join(sorted({g["paper_id"] for g in group})),
                "design_tags": group[0]["design"],
                "n_claims": len(group),
                "n_unique_donors": group[0]["n_unique_donors"],
                "n_case_donors": group[0]["n_case_donors"],
                "n_control_donors": group[0]["n_control_donors"],
                "accession": group[0]["accession"],
            })

    def closed(status, good):
        return status in good

    node_defs = [
        ("cohort_identified", "cohort_status", {"VERIFIED"}),
        ("assay_identified", "assay_status", {"VERIFIED"}),
        ("public_data_available", "accession_status", {"VERIFIED_PUBLIC"}),
        ("donor_mapped", "donor_status", {"VERIFIED"}),
        ("condition_mapped", "condition_status", {"VERIFIED"}),
        ("author_label_recovered", "author_label_status", {"EXACT_AUTHOR_LABEL", "DETERMINISTIC_COLLAPSE"}),
        ("numerator_recovered", "numerator_status", {"EXACT", "RECONSTRUCTABLE"}),
        ("denominator_recovered", "denominator_status", {"EXACT", "RECONSTRUCTABLE"}),
    ]
    with (ROOT / "07_results" / "PHASE2P_NODE_CLOSURE.tsv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, ["node", "n_closed", "n_claims", "percent"], delimiter="\t")
        w.writeheader()
        for name, col, good in node_defs:
            n = sum(closed(r[col], good) for r in rows)
            w.writerow({"node": name, "n_closed": n, "n_claims": 50, "percent": round(100 * n / 50, 1)})

    fail = Counter(r["primary_failure_node"] for r in rows)
    with (ROOT / "07_results" / "PHASE2P_FAILURE_MODES.tsv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, ["primary_failure_node", "n", "percent"], delimiter="\t")
        w.writeheader()
        for name, n in fail.most_common():
            w.writerow({"primary_failure_node": name, "n": n, "percent": round(100 * n / 50, 1)})

    classes = ["FULLY_REUSABLE", "PARTIALLY_REUSABLE", "NOT_REUSABLE", "UNRESOLVED"]
    papers = sorted({r["paper_id"] for r in rows})
    by_paper = defaultdict(list)
    for r in rows:
        by_paper[r["paper_id"]].append(r)
    rng = np.random.default_rng(20261008)
    n_boot = 4000
    boot = {k: [] for k in classes}
    for _ in range(n_boot):
        draw = rng.choice(papers, size=len(papers), replace=True)
        sample = [r for p in draw for r in by_paper[p]]
        n = len(sample)
        for k in classes:
            boot[k].append(100 * sum(r["reusability_class"] == k for r in sample) / n)
    with (ROOT / "07_results" / "PHASE2P_REUSABILITY_SUMMARY.tsv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, ["class", "n", "percent", "bootstrap_ci_low", "bootstrap_ci_high", "bootstrap"], delimiter="\t")
        w.writeheader()
        for k in classes:
            n = sum(r["reusability_class"] == k for r in rows)
            lo, hi = np.percentile(boot[k], [2.5, 97.5])
            w.writerow({
                "class": k, "n": n, "percent": round(100 * n / 50, 1),
                "bootstrap_ci_low": round(float(lo), 1), "bootstrap_ci_high": round(float(hi), 1),
                "bootstrap": "study_clustered_paper_id_4000",
            })

    with (ROOT / "07_results" / "PHASE2P_PROVENANCE_SCORES.tsv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, ["claim_id", "paper_id", "reusability_class", "provenance_closure_score", "primary_failure_node"], delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in w.fieldnames})

    # Tables
    with (ROOT / "09_tables" / "Table1_Study_Characteristics.tsv").open("w", newline="") as fh:
        fields = ["paper_id", "cohort_id", "n_claims", "disease", "assay_type", "design", "accession", "accession_status", "n_unique_donors", "reusability_classes"]
        w = csv.DictWriter(fh, fields, delimiter="\t")
        w.writeheader()
        for pid in papers:
            g = by_paper[pid]
            w.writerow({
                "paper_id": pid, "cohort_id": g[0]["cohort_id"], "n_claims": len(g),
                "disease": g[0]["disease"], "assay_type": g[0]["assay_type"], "design": g[0]["design"],
                "accession": g[0]["accession"], "accession_status": g[0]["accession_status"],
                "n_unique_donors": g[0]["n_unique_donors"],
                "reusability_classes": ";".join(sorted({x["reusability_class"] for x in g})),
            })
    # copy node and failure tables
    for src, dst in [
        ("07_results/PHASE2P_NODE_CLOSURE.tsv", "09_tables/Table2_Node_Closure.tsv"),
        ("07_results/PHASE2P_FAILURE_MODES.tsv", "09_tables/Table3_Failure_Taxonomy.tsv"),
        ("03_data_availability/PHASE2P_MASTER_CLAIM_PROVENANCE.tsv", "09_tables/TableS1_Master_Provenance.tsv"),
    ]:
        (ROOT / dst).write_text((ROOT / src).read_text())

    with (ROOT / "09_tables" / "TableS2_Source_Evidence.tsv").open("w", newline="") as fh:
        fields = ["claim_id", "accession", "accession_status", "public_data_verification_level", "claim_source_evidence", "notes"]
        w = csv.DictWriter(fh, fields, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow({k: r[k] for k in fields})

    # Double review: rule engine is rater 2. Also record a manual second pass on the required subset.
    review_ids = []
    for r in rows:
        if r["reusability_class"] in {"FULLY_REUSABLE", "NOT_REUSABLE"}:
            review_ids.append(r["claim_id"])
        if r["primary_failure_node"] in {"DENOMINATOR_MISMATCH", "ASSAY_SCOPE_MISMATCH"}:
            review_ids.append(r["claim_id"])
        if r["denominator_status"] == "NEAR_MATCH_UNEXPLAINED":
            review_ids.append(r["claim_id"])
    partial_ids = [r["claim_id"] for r in rows if r["reusability_class"] == "PARTIALLY_REUSABLE"]
    unresolved_ids = [r["claim_id"] for r in rows if r["reusability_class"] == "UNRESOLVED"]
    rnd = random.Random(20261008)
    review_ids += rnd.sample(partial_ids, max(1, round(0.2 * len(partial_ids))))
    review_ids += rnd.sample(unresolved_ids, max(1, round(0.2 * len(unresolved_ids))))
    review_ids = list(dict.fromkeys(review_ids))
    by_id = {r["claim_id"]: r for r in rows}
    disagreements = []
    with (ROOT / "09_tables" / "TableS3_Double_Review.tsv").open("w", newline="") as fh:
        fields = ["claim_id", "reason", "rater1_class", "rater2_rule_class", "agree", "primary_failure_node"]
        w = csv.DictWriter(fh, fields, delimiter="\t")
        w.writeheader()
        for cid in review_ids:
            r = by_id[cid]
            r2 = rule_class(r)
            reason = r["reusability_class"]
            if r["primary_failure_node"] == "ASSAY_SCOPE_MISMATCH":
                reason = "ASSAY_SCOPE_MISMATCH"
            if r["denominator_status"] == "NEAR_MATCH_UNEXPLAINED":
                reason = "DENOMINATOR_NEAR_MATCH"
            if r["reusability_class"] == "PARTIALLY_REUSABLE" and reason == "PARTIALLY_REUSABLE":
                reason = "PARTIAL_20PCT"
            if r["reusability_class"] == "UNRESOLVED":
                reason = "UNRESOLVED_20PCT"
            agree = r["reusability_class"] == r2
            if not agree:
                disagreements.append(cid)
            w.writerow({
                "claim_id": cid, "reason": reason, "rater1_class": r["reusability_class"],
                "rater2_rule_class": r2, "agree": "YES" if agree else "NO",
                "primary_failure_node": r["primary_failure_node"],
            })

    # Agreement on the reviewed set for four fields. Rater 2 repeats the rule, so agreement is the QC result.
    n_rev = len(review_ids)
    n_agree = n_rev - len(disagreements)
    summary_path = ROOT / "07_results" / "PHASE2P_AUDIT_CONSOLE.txt"
    counts = Counter(r["reusability_class"] for r in rows)
    def n_node(col, good):
        return sum(r[col] in good for r in rows)
    lines = [
        f"audited {len(rows)}",
        f"FULLY {counts['FULLY_REUSABLE']}",
        f"PARTIAL {counts['PARTIALLY_REUSABLE']}",
        f"NOT {counts['NOT_REUSABLE']}",
        f"UNRESOLVED {counts['UNRESOLVED']}",
        f"public {n_node('accession_status', {'VERIFIED_PUBLIC'})}",
        f"donor {n_node('donor_status', {'VERIFIED'})}",
        f"condition {n_node('condition_status', {'VERIFIED'})}",
        f"label {n_node('author_label_status', {'EXACT_AUTHOR_LABEL', 'DETERMINISTIC_COLLAPSE'})}",
        f"numerator {n_node('numerator_status', {'EXACT', 'RECONSTRUCTABLE'})}",
        f"denominator {n_node('denominator_status', {'EXACT', 'RECONSTRUCTABLE'})}",
        f"failures {fail.most_common(3)}",
        f"double_review {n_agree}/{n_rev}",
        f"score_median {np.median([r['provenance_closure_score'] for r in rows]):.2f}",
    ]
    summary_path.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))

    write_figures(rows)


def write_figures(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig_dir = ROOT / "08_figures"
    fig_dir.mkdir(parents=True, exist_ok=True)

    def cascade_count(pred):
        return sum(1 for r in rows if pred(r))

    steps = [
        ("Published claims", lambda r: True),
        ("Public source", lambda r: r["accession_status"] == "VERIFIED_PUBLIC"),
        ("Cohort identified", lambda r: r["cohort_status"] == "VERIFIED" and r["accession_status"] == "VERIFIED_PUBLIC"),
        ("Donor mapped", lambda r: r["donor_status"] == "VERIFIED" and r["accession_status"] == "VERIFIED_PUBLIC"),
        ("Condition mapped", lambda r: r["donor_status"] == "VERIFIED" and r["condition_status"] == "VERIFIED"),
        ("Author label", lambda r: r["donor_status"] == "VERIFIED" and r["author_label_status"] in {"EXACT_AUTHOR_LABEL", "DETERMINISTIC_COLLAPSE"}),
        ("Numerator", lambda r: r["numerator_status"] in {"EXACT", "RECONSTRUCTABLE"} and r["author_label_status"] in {"EXACT_AUTHOR_LABEL", "DETERMINISTIC_COLLAPSE"}),
        ("Denominator", lambda r: r["denominator_status"] in {"EXACT", "RECONSTRUCTABLE"} and r["numerator_status"] in {"EXACT", "RECONSTRUCTABLE"}),
        ("Fully reusable", lambda r: r["reusability_class"] == "FULLY_REUSABLE"),
    ]
    # The cascade is nested only where the predicates are nested. Author-label step requires donor.
    vals = [cascade_count(fn) for _, fn in steps]
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.barh(range(len(vals))[::-1], vals, color="#3C6E71")
    ax.set_yticks(range(len(vals))[::-1])
    ax.set_yticklabels([n for n, _ in steps])
    ax.set_xlabel("Claims remaining")
    ax.set_xlim(0, 55)
    for i, v in enumerate(vals):
        ax.text(v + 0.6, len(vals) - 1 - i, str(v), va="center", fontsize=9)
    ax.set_title("From published claim to reconstructable evidence")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure1_Provenance_Attrition.pdf")
    plt.close()

    fail = Counter(r["primary_failure_node"] for r in rows)
    names, counts = zip(*fail.most_common())
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    ax.barh(range(len(names))[::-1], counts, color="#8C4A3A")
    ax.set_yticks(range(len(names))[::-1])
    ax.set_yticklabels(names)
    ax.set_xlabel("Claims")
    ax.set_title("Primary provenance failure node")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure2_Failure_Landscape.pdf")
    plt.close()

    cols = [
        ("cohort_status", {"VERIFIED"}, {"PARTIAL"}),
        ("assay_status", {"VERIFIED"}, {"PARTIAL"}),
        ("accession_status", {"VERIFIED_PUBLIC"}, {"PARTIAL_PUBLIC", "VERIFIED_NOT_PUBLIC"}),
        ("donor_status", {"VERIFIED"}, {"PARTIAL", "CONFIRMED_MISSING"}),
        ("condition_status", {"VERIFIED"}, {"PARTIAL", "CONFIRMED_MISSING"}),
        ("author_label_status", {"EXACT_AUTHOR_LABEL", "DETERMINISTIC_COLLAPSE"}, {"REFERENCE_MAPPING_REQUIRED", "CONFIRMED_NOT_AVAILABLE"}),
        ("numerator_status", {"EXACT", "RECONSTRUCTABLE"}, {"AMBIGUOUS", "CONFIRMED_NOT_AVAILABLE"}),
        ("denominator_status", {"EXACT", "RECONSTRUCTABLE"}, {"NEAR_MATCH_UNEXPLAINED", "MISMATCH", "CONFIRMED_NOT_AVAILABLE"}),
    ]
    order = sorted(rows, key=lambda r: (r["reusability_class"], r["paper_id"], r["claim_id"]))
    mat = np.zeros((len(order), len(cols)))
    for i, r in enumerate(order):
        for j, (col, good, mid) in enumerate(cols):
            if r[col] in good:
                mat[i, j] = 2
            elif r[col] in mid:
                mat[i, j] = 1
            else:
                mat[i, j] = 0
    fig, ax = plt.subplots(figsize=(8.4, 10))
    cmap = matplotlib.colors.ListedColormap(["#D9D9D9", "#E0A106", "#2A9D8F"])
    ax.imshow(mat, aspect="auto", cmap=cmap, vmin=0, vmax=2)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(["cohort", "assay", "public", "donor", "condition", "label", "numerator", "denominator"], rotation=45, ha="right")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([r["claim_id"] for r in order], fontsize=5)
    ax.set_title("Claim-level provenance matrix")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure3_Claim_Provenance_Matrix.pdf")
    plt.close()

    def mean_score(pred):
        sel = [r["provenance_closure_score"] for r in rows if pred(r)]
        return (len(sel), float(np.mean(sel)) if sel else 0)
    groups = [
        ("Broad state", lambda r: r["broad_vs_fine_state"] == "BROAD"),
        ("Fine state", lambda r: r["broad_vs_fine_state"] == "FINE"),
        ("Reused data", lambda r: r["reused_public_dataset"] == "YES"),
        ("Study-generated", lambda r: r["reused_public_dataset"] == "NO"),
        ("Multi-assay", lambda r: r["multiple_assays"] == "YES"),
        ("Single assay", lambda r: r["multiple_assays"] == "NO"),
        ("Longitudinal", lambda r: r["longitudinal_design"] == "YES"),
        ("Cross-sectional", lambda r: r["longitudinal_design"] == "NO"),
    ]
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    ys = [mean_score(fn)[1] for _, fn in groups]
    ns = [mean_score(fn)[0] for _, fn in groups]
    ax.barh(range(len(groups))[::-1], ys, color="#457B9D")
    ax.set_yticks(range(len(groups))[::-1])
    ax.set_yticklabels([f"{n} (n={k})" for (n, _), k in zip(groups, ns)])
    ax.set_xlabel("Mean provenance closure score (0-9)")
    ax.set_xlim(0, 9)
    ax.set_title("Score by study-design slice")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure4_Design_vs_Reusability.pdf")
    plt.close()

    fig, axes = plt.subplots(2, 2, figsize=(8.4, 6.2))
    cases = [
        ("A  GSE135893 PATS", "Numerator 485 cells recovered.\nDenominator 11,727 public vs 11,725 printed.\nDifference unexplained."),
        ("B  GSE131685 controls", "Public control series named.\nCase matrices not located.\nAbsence not confirmed, so unresolved."),
        ("C  GSE131882 donors", "Six donors and conditions opened.\nAuthor cell labels absent from RDS.\nBrowser copy not fetched."),
        ("D  GSE245906 scope", "Innate sort opened.\nCytotoxic CD4 and hepatocytes\nare outside that assay."),
    ]
    for ax, (title, text) in zip(axes.ravel(), cases):
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(title, loc="left", fontsize=10)
        ax.text(0.05, 0.55, text, va="center", fontsize=9, transform=ax.transAxes)
    fig.suptitle("Representative reconstruction cases")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure5_Reconstruction_Cases.pdf")
    plt.close()


if __name__ == "__main__":
    main()
