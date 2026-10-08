#!/usr/bin/env python3
"""Phase 2P-QC. Does not edit the frozen provenance master."""

from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "03_data_availability" / "PHASE2P_MASTER_CLAIM_PROVENANCE.tsv"
FROZEN_SHA = "9b59a9b963499b68aba265726d006fa8f2a084b04a29405ea091482aba7d6d9b"
SEED = 20261008
N_BOOT = 10000
CLASSES = ["FULLY_REUSABLE", "PARTIALLY_REUSABLE", "NOT_REUSABLE", "UNRESOLVED"]

NODE_ORDER = [
    ("PUBLIC_SOURCE", "accession_status", {"VERIFIED_PUBLIC"}, {"VERIFIED_NOT_PUBLIC"}, {"PARTIAL_PUBLIC"}),
    ("COHORT", "cohort_status", {"VERIFIED"}, set(), {"PARTIAL"}),
    ("ASSAY", "assay_status", {"VERIFIED"}, set(), {"PARTIAL"}),
    ("DONOR", "donor_status", {"VERIFIED"}, {"CONFIRMED_MISSING"}, {"PARTIAL"}),
    ("CONDITION", "condition_status", {"VERIFIED"}, {"CONFIRMED_MISSING"}, {"PARTIAL"}),
    ("AUTHOR_LABEL", "author_label_status", {"EXACT_AUTHOR_LABEL", "DETERMINISTIC_COLLAPSE"}, {"CONFIRMED_NOT_AVAILABLE"}, {"REFERENCE_MAPPING_REQUIRED"}),
    ("NUMERATOR", "numerator_status", {"EXACT", "RECONSTRUCTABLE"}, {"CONFIRMED_NOT_AVAILABLE"}, {"AMBIGUOUS"}),
    ("DENOMINATOR", "denominator_status", {"EXACT", "RECONSTRUCTABLE"}, {"CONFIRMED_NOT_AVAILABLE", "MISMATCH"}, {"NEAR_MATCH_UNEXPLAINED"}),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stop_label(row):
    for node, col, closed, confirmed, partial in NODE_ORDER:
        status = row[col]
        if status in closed:
            continue
        if status in confirmed:
            return node, f"CONFIRMED_BREAK_AT_{node}", status
        if status in partial or status == "NEAR_MATCH_UNEXPLAINED":
            if status == "NEAR_MATCH_UNEXPLAINED":
                return node, f"NEAR_MATCH_AT_{node}", status
            return node, f"PARTIAL_AT_{node}", status
        if status == "UNRESOLVED":
            return node, f"UNRESOLVED_AT_{node}", status
        raise SystemExit(f"UNMAPPED_STATUS {row['claim_id']} {col}={status}")
    raise SystemExit(f"ALL_NODES_CLOSED {row['claim_id']}")


def bootstrap(rows, key, rng):
    groups = defaultdict(list)
    for r in rows:
        groups[r[key]].append(r)
    ids = sorted(groups)
    out = {k: [] for k in CLASSES}
    for _ in range(N_BOOT):
        draw = rng.choice(ids, size=len(ids), replace=True)
        sample = [r for i in draw for r in groups[i]]
        n = len(sample)
        for k in CLASSES:
            out[k].append(100.0 * sum(r["reusability_class"] == k for r in sample) / n)
    summary = {}
    for k in CLASSES:
        lo, hi = np.percentile(out[k], [2.5, 97.5])
        summary[k] = (round(float(lo), 1), round(float(hi), 1))
    return summary


def cascade_flags(row):
    public = row["accession_status"] == "VERIFIED_PUBLIC"
    cohort = public and row["cohort_status"] == "VERIFIED"
    donor = cohort and row["donor_status"] == "VERIFIED"
    condition = donor and row["condition_status"] == "VERIFIED"
    label = condition and row["author_label_status"] in {"EXACT_AUTHOR_LABEL", "DETERMINISTIC_COLLAPSE"}
    numerator = label and row["numerator_status"] in {"EXACT", "RECONSTRUCTABLE"}
    denominator = numerator and row["denominator_status"] in {"EXACT", "RECONSTRUCTABLE"}
    full = denominator and row["reusability_class"] == "FULLY_REUSABLE"
    return [True, public, cohort, donor, condition, label, numerator, denominator, full]


def main():
    digest = sha256(MASTER)
    if digest != FROZEN_SHA:
        raise SystemExit("SOURCE_CLASSIFICATION_ERROR_FOUND")
    rows = list(csv.DictReader(MASTER.open(), delimiter="\t"))
    if len(rows) != 50:
        raise SystemExit("SOURCE_CLASSIFICATION_ERROR_FOUND")
    counts = Counter(r["reusability_class"] for r in rows)
    if counts["FULLY_REUSABLE"] != 0 or counts["PARTIALLY_REUSABLE"] != 13 or counts["NOT_REUSABLE"] != 5 or counts["UNRESOLVED"] != 32:
        raise SystemExit("SOURCE_CLASSIFICATION_ERROR_FOUND")
    if len({r["paper_id"] for r in rows}) != 19:
        raise SystemExit("SOURCE_CLASSIFICATION_ERROR_FOUND")

    by_claim = []
    for r in rows:
        node, label, status = stop_label(r)
        by_claim.append({
            "claim_id": r["claim_id"],
            "paper_id": r["paper_id"],
            "cohort_id": r["cohort_id"],
            "reusability_class": r["reusability_class"],
            "frozen_primary_failure_node": r["primary_failure_node"],
            "first_unclosed_node": node,
            "stop_label": label,
            "node_status": status,
        })
    if len(by_claim) != 50:
        raise SystemExit("FIRST_UNCLOSED_INCOMPLETE")

    with (ROOT / "07_results" / "PHASE2P_FIRST_UNCLOSED_BY_CLAIM.tsv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, list(by_claim[0]), delimiter="\t")
        w.writeheader()
        w.writerows(by_claim)

    agg = Counter((r["first_unclosed_node"], r["stop_label"]) for r in by_claim)
    order_nodes = [n for n, *_ in NODE_ORDER]
    with (ROOT / "07_results" / "PHASE2P_FIRST_UNCLOSED_NODE.tsv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, ["node", "stop_label", "kind", "n", "percent"], delimiter="\t")
        w.writeheader()
        for node in order_nodes:
            items = [(lab, n) for (nd, lab), n in agg.items() if nd == node]
            items.sort(key=lambda x: -x[1])
            for lab, n in items:
                if lab.startswith("UNRESOLVED_AT_"):
                    kind = "unresolved"
                elif lab.startswith("CONFIRMED_BREAK_AT_"):
                    kind = "confirmed_absent_or_mismatch"
                elif lab.startswith("NEAR_MATCH_AT_"):
                    kind = "opened_but_not_closed"
                else:
                    kind = "partial"
                w.writerow({"node": node, "stop_label": lab, "kind": kind, "n": n, "percent": round(100 * n / 50, 1)})

    point = {k: round(100 * counts[k] / 50, 1) for k in CLASSES}
    paper_iv = bootstrap(rows, "paper_id", np.random.default_rng(SEED))
    cohort_iv = bootstrap(rows, "cohort_id", np.random.default_rng(SEED))
    with (ROOT / "07_results" / "PHASE2P_CLUSTER_SENSITIVITY.tsv").open("w", newline="") as fh:
        fields = [
            "analysis", "cluster_unit", "class", "n", "percent",
            "stability_interval_low", "stability_interval_high",
            "interval_status", "replicates", "seed", "role",
        ]
        w = csv.DictWriter(fh, fields, delimiter="\t")
        w.writeheader()
        for analysis, unit, iv, role in [
            ("A", "paper_id", paper_iv, "primary_reporting_unit"),
            ("B", "cohort_id", cohort_iv, "dependence_sensitivity"),
        ]:
            for k in CLASSES:
                lo, hi = iv[k]
                status = "NOT_INFORMATIVE_FOR_ZERO_EVENT" if counts[k] == 0 else "CLUSTERED_BOOTSTRAP_STABILITY_INTERVAL"
                w.writerow({
                    "analysis": analysis,
                    "cluster_unit": unit,
                    "class": k,
                    "n": counts[k],
                    "percent": point[k],
                    "stability_interval_low": "" if counts[k] == 0 else lo,
                    "stability_interval_high": "" if counts[k] == 0 else hi,
                    "interval_status": status,
                    "replicates": N_BOOT,
                    "seed": SEED,
                    "role": role,
                })

    # Supersede the 4,000-replicate summary so a 0.0-0.0 interval is not the reported result.
    with (ROOT / "07_results" / "PHASE2P_REUSABILITY_SUMMARY.tsv").open("w", newline="") as fh:
        fields = ["class", "n", "percent", "stability_interval_low", "stability_interval_high", "interval_status", "bootstrap"]
        w = csv.DictWriter(fh, fields, delimiter="\t")
        w.writeheader()
        for k in CLASSES:
            lo, hi = paper_iv[k]
            status = "NOT_INFORMATIVE_FOR_ZERO_EVENT" if counts[k] == 0 else "PAPER_CLUSTERED_BOOTSTRAP_STABILITY_INTERVAL"
            w.writerow({
                "class": k, "n": counts[k], "percent": point[k],
                "stability_interval_low": "" if counts[k] == 0 else lo,
                "stability_interval_high": "" if counts[k] == 0 else hi,
                "interval_status": status,
                "bootstrap": f"paper_id_{N_BOOT}_seed_{SEED}",
            })

    steps = cascade_flags
    step_names = [
        "human_locked_claims", "verified_public_source", "verified_cohort_within_public_source",
        "verified_donor_mapping", "verified_condition_mapping", "recovered_author_label",
        "reconstructed_numerator", "reconstructed_denominator", "fully_reusable",
    ]
    step_n = []
    flags = [steps(r) for r in rows]
    for i in range(9):
        step_n.append(sum(f[i] for f in flags))
    nested_ok = all(step_n[i + 1] <= step_n[i] for i in range(8))
    if not nested_ok:
        raise SystemExit("NESTED_ATTRITION_FAIL")
    with (ROOT / "07_results" / "PHASE2P_NESTED_ATTRITION.tsv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, ["step", "n", "prior_n", "nested"], delimiter="\t")
        w.writeheader()
        for i, name in enumerate(step_names):
            w.writerow({"step": name, "n": step_n[i], "prior_n": "" if i == 0 else step_n[i - 1], "nested": "PASS"})

    # Descriptive basis. Does not alter frozen taxonomy values.
    source_denom_ids = {r["claim_id"] for r in rows if r["denominator_taxonomy"] in {"ALL_B_CELLS", "ALL_T_CELLS"}}
    with (ROOT / "07_results" / "PHASE2P_DESCRIPTIVE_BASIS.tsv").open("w", newline="") as fh:
        fields = ["claim_id", "claim_granularity", "claim_granularity_basis", "denominator_taxonomy", "denominator_taxonomy_basis"]
        w = csv.DictWriter(fh, fields, delimiter="\t")
        w.writeheader()
        for r in rows:
            denom_basis = "SOURCE_VERIFIED" if r["claim_id"] in source_denom_ids else "HEURISTIC_DESCRIPTIVE"
            w.writerow({
                "claim_id": r["claim_id"],
                "claim_granularity": r["claim_granularity"],
                "claim_granularity_basis": "RULE_DERIVED",
                "denominator_taxonomy": r["denominator_taxonomy"],
                "denominator_taxonomy_basis": denom_basis,
            })

    papers = defaultdict(list)
    for r in rows:
        papers[r["paper_id"]].append(r["reusability_class"])
    any_partial = sum("PARTIALLY_REUSABLE" in set(v) for v in papers.values())
    any_not = sum("NOT_REUSABLE" in set(v) for v in papers.values())
    any_full = sum("FULLY_REUSABLE" in set(v) for v in papers.values())
    all_unresolved = sum(set(v) == {"UNRESOLVED"} for v in papers.values())

    endpoint_shift = []
    for k in CLASSES:
        if counts[k] == 0:
            continue
        for a, b in zip(paper_iv[k], cohort_iv[k]):
            endpoint_shift.append(abs(a - b))
    material = "results were materially unchanged" if max(endpoint_shift, default=0) < 5 and all(
        abs(point[k] - point[k]) < 5 for k in CLASSES
    ) else "interval endpoints moved"

    # Point estimates are identical by construction. Material if every reported endpoint moves by <5 pp.
    max_shift = max(endpoint_shift) if endpoint_shift else 0
    material_flag = "results were materially unchanged" if max_shift < 5 else "INTERVAL_SHIFT_REPORTED"

    write_figures(rows, by_claim, step_n, step_names)
    if sha256(MASTER) != FROZEN_SHA:
        raise SystemExit("SOURCE_CLASSIFICATION_ERROR_FOUND")

    manifest = ROOT / "07_results" / "PHASE2P_QC_NUMBERS.txt"
    lines = [
        f"sha {digest}",
        f"steps {step_n}",
        f"paper {paper_iv}",
        f"cohort {cohort_iv}",
        f"max_endpoint_shift {max_shift}",
        f"material {material_flag}",
        f"papers any_full {any_full} any_partial {any_partial} any_not {any_not} all_unresolved {all_unresolved}",
        f"cohorts {len({r['cohort_id'] for r in rows})}",
        "stops",
    ]
    for node in order_nodes:
        for (nd, lab), n in sorted(agg.items()):
            if nd == node:
                lines.append(f"  {lab} {n}")
    manifest.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


def write_figures(rows, by_claim, step_n, step_names):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig_dir = ROOT / "08_figures"
    labels = [
        "Human-locked claims",
        "Verified public source",
        "Verified cohort",
        "Verified donor map",
        "Verified condition map",
        "Recovered author label",
        "Reconstructed numerator",
        "Reconstructed denominator",
        "Fully reusable",
    ]
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    ax.barh(range(len(step_n))[::-1], step_n, color="#3C6E71")
    ax.set_yticks(range(len(step_n))[::-1])
    ax.set_yticklabels(labels)
    ax.set_xlabel("Claims remaining")
    ax.set_xlim(0, 58)
    for i, v in enumerate(step_n):
        ax.text(v + 0.6, len(step_n) - 1 - i, str(v), va="center", fontsize=9)
    ax.set_title("From published claim to reconstructable evidence")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure1_Provenance_Attrition_FINAL.pdf")
    plt.close()

    nodes = ["PUBLIC_SOURCE", "COHORT", "ASSAY", "DONOR", "CONDITION", "AUTHOR_LABEL", "NUMERATOR", "DENOMINATOR"]
    kinds = ["unresolved", "partial", "confirmed_absent_or_mismatch", "opened_but_not_closed"]
    colors = {
        "unresolved": "#BDBDBD",
        "partial": "#E0A106",
        "confirmed_absent_or_mismatch": "#6B3A2A",
        "opened_but_not_closed": "#3C6E71",
    }
    kind_of = {}
    for r in by_claim:
        lab = r["stop_label"]
        if lab.startswith("UNRESOLVED_AT_"):
            kind_of[r["claim_id"]] = "unresolved"
        elif lab.startswith("CONFIRMED_BREAK_AT_"):
            kind_of[r["claim_id"]] = "confirmed_absent_or_mismatch"
        elif lab.startswith("NEAR_MATCH_AT_"):
            kind_of[r["claim_id"]] = "opened_but_not_closed"
        else:
            kind_of[r["claim_id"]] = "partial"
    mat = {k: [] for k in kinds}
    for node in nodes:
        for k in kinds:
            mat[k].append(sum(1 for r in by_claim if r["first_unclosed_node"] == node and kind_of[r["claim_id"]] == k))
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    y = np.arange(len(nodes))
    left = np.zeros(len(nodes))
    pretty = {
        "unresolved": "Unresolved at this node",
        "partial": "Partial record at this node",
        "confirmed_absent_or_mismatch": "Source-supported break",
        "opened_but_not_closed": "Opened, numerator/denominator not closed",
    }
    for k in kinds:
        vals = np.array(mat[k], dtype=float)
        if vals.sum() == 0:
            continue
        ax.barh(y, vals, left=left, color=colors[k], label=pretty[k])
        left += vals
    ax.set_yticks(y)
    ax.set_yticklabels(nodes)
    ax.invert_yaxis()
    ax.set_xlabel("Claims")
    ax.set_title("Where the reconstruction chain first stops")
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure2_First_Unclosed_Node_FINAL.pdf")
    plt.close()

    # Supplementary confirmed taxonomy only. UNRESOLVED is excluded.
    confirmed = Counter(r["frozen_primary_failure_node"] for r in by_claim if r["reusability_class"] == "NOT_REUSABLE" or r["frozen_primary_failure_node"] == "DENOMINATOR_MISSING")
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    names = list(confirmed.keys())
    vals = [confirmed[n] for n in names]
    ax.barh(range(len(names))[::-1], vals, color="#6B3A2A")
    ax.set_yticks(range(len(names))[::-1])
    ax.set_yticklabels(names)
    ax.set_xlabel("Claims")
    ax.set_title("Source-supported breaks (supplement)")
    fig.tight_layout()
    fig.savefig(fig_dir / "FigureS_Confirmed_Failure_Taxonomy.pdf")
    plt.close()

    cols = [
        ("cohort_status", {"VERIFIED"}, {"PARTIAL"}),
        ("assay_status", {"VERIFIED"}, {"PARTIAL"}),
        ("accession_status", {"VERIFIED_PUBLIC"}, {"PARTIAL_PUBLIC"}),
        ("donor_status", {"VERIFIED"}, {"PARTIAL"}),
        ("condition_status", {"VERIFIED"}, {"PARTIAL"}),
        ("author_label_status", {"EXACT_AUTHOR_LABEL", "DETERMINISTIC_COLLAPSE"}, {"REFERENCE_MAPPING_REQUIRED"}),
        ("numerator_status", {"EXACT", "RECONSTRUCTABLE"}, {"AMBIGUOUS"}),
        ("denominator_status", {"EXACT", "RECONSTRUCTABLE"}, {"NEAR_MATCH_UNEXPLAINED"}),
    ]
    # Confirmed-absent statuses are drawn separately from unresolved so the matrix does not equate them.
    order = sorted(rows, key=lambda r: (r["reusability_class"], r["paper_id"], r["claim_id"]))
    matx = np.zeros((len(order), len(cols)))
    confirmed_status = {
        "VERIFIED_NOT_PUBLIC", "CONFIRMED_MISSING", "CONFIRMED_NOT_AVAILABLE", "MISMATCH",
    }
    for i, r in enumerate(order):
        for j, (col, good, mid) in enumerate(cols):
            if r[col] in good:
                matx[i, j] = 3
            elif r[col] in mid:
                matx[i, j] = 2
            elif r[col] in confirmed_status:
                matx[i, j] = 1
            else:
                matx[i, j] = 0
    fig, ax = plt.subplots(figsize=(8.4, 10))
    cmap = matplotlib.colors.ListedColormap(["#D9D9D9", "#6B3A2A", "#E0A106", "#2A9D8F"])
    ax.imshow(matx, aspect="auto", cmap=cmap, vmin=0, vmax=3)
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(["cohort", "assay", "public", "donor", "condition", "label", "numerator", "denominator"], rotation=45, ha="right")
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([r["claim_id"] for r in order], fontsize=5)
    ax.set_title("Claim-level provenance matrix")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure3_Claim_Provenance_Matrix_FINAL.pdf")
    plt.close()

    def mean_score(pred):
        sel = [float(r["provenance_closure_score"]) for r in rows if pred(r)]
        return len(sel), (float(np.mean(sel)) if sel else 0.0)
    # Design flags are not columns of the frozen master. Rebuild slices from frozen cohort/assay fields only.
    design = {}
    for r in csv.DictReader((ROOT / "03_data_availability" / "PHASE2P_COHORT_DESIGN.tsv").open(), delimiter="\t"):
        design[r["cohort_id"]] = r["design_tags"]
    groups = [
        ("Broad state label", lambda r: r["broad_vs_fine_state"] == "BROAD" if "broad_vs_fine_state" in r else r["claim_granularity"] == "BROAD_CELL_TYPE"),
        ("Other state label", lambda r: r["claim_granularity"] != "BROAD_CELL_TYPE"),
        ("Reused cohort tag", lambda r: "REUSED_COHORT" in design.get(r["cohort_id"], "")),
        ("No reused-cohort tag", lambda r: "REUSED_COHORT" not in design.get(r["cohort_id"], "")),
        ("Multi-assay tag", lambda r: "MULTI_ASSAY" in design.get(r["cohort_id"], "")),
        ("No multi-assay tag", lambda r: "MULTI_ASSAY" not in design.get(r["cohort_id"], "")),
        ("Longitudinal tag", lambda r: "LONGITUDINAL" in design.get(r["cohort_id"], "")),
        ("No longitudinal tag", lambda r: "LONGITUDINAL" not in design.get(r["cohort_id"], "")),
    ]
    # broad_vs_fine is not in the frozen master. Use claim_granularity only.
    groups[0] = ("Broad cell-type label", lambda r: r["claim_granularity"] == "BROAD_CELL_TYPE")
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    stats = [mean_score(fn) for _, fn in groups]
    ax.barh(range(len(groups))[::-1], [s[1] for s in stats], color="#457B9D")
    ax.set_yticks(range(len(groups))[::-1])
    ax.set_yticklabels([f"{name} (n={n})" for (name, _), (n, _) in zip(groups, stats)])
    ax.set_xlabel("Mean provenance closure score (0–9)")
    ax.set_xlim(0, 9)
    ax.set_title("Descriptive provenance-closure scores across study characteristics")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure4_Descriptive_Closure_Scores_FINAL.pdf")
    plt.close()

    fig, axes = plt.subplots(2, 2, figsize=(8.6, 6.4))
    cases = [
        ("A  PATS denominator", "Numerator recovered: 485 KRT5-/KRT17+ cells.\nPublic four-label set: 11,727.\nPrinted count: 11,725.\nThe two-cell gap has no source rule."),
        ("B  Control series only", "GSE131685 is a public control series.\nCase matrices were not located.\nAbsence was not confirmed, so the claims stay unresolved."),
        ("C  Donor without a label", "GSE131882: six donors and conditions were opened.\nThe author cell-state column was not in those matrices.\nA linked browser was not fetched."),
        ("D  Assay scope", "GSE245906 is an innate-cell sort.\nCytotoxic CD4 T cells and hepatocytes\nare outside that assay."),
    ]
    for ax, (title, text) in zip(axes.ravel(), cases):
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(True)
        ax.set_title(title, loc="left", fontsize=10)
        ax.text(0.05, 0.5, text, va="center", fontsize=9, transform=ax.transAxes)
    fig.suptitle("Representative reconstruction cases")
    fig.tight_layout()
    fig.savefig(fig_dir / "Figure5_Reconstruction_Cases_FINAL.pdf")
    plt.close()


if __name__ == "__main__":
    main()
