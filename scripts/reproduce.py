"""Read frozen inputs, verify summaries and bootstrap; never reclassify inputs."""
from pathlib import Path
import csv, json, hashlib, argparse, importlib.util
from collections import Counter
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    return list(csv.DictReader((ROOT/name).open(),delimiter='\t'))
def module(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts/original'/f'{name}.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='reproduction_output');args=ap.parse_args()
    out=Path(args.output);out=out if out.is_absolute() else ROOT/out;out.mkdir(parents=True,exist_ok=True)
    rows=read('PHASE2P_MASTER_CLAIM_PROVENANCE.tsv');claims=read('FINAL_LAYER_A_CLAIMS_v1.1.tsv')
    expected=json.loads((ROOT/'FROZEN_INPUT_HASHES.json').read_text())
    for name,sha in expected.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
    assert len(rows)==len(claims)==50
    assert len({r['claim_id'] for r in rows})==50
    assert {r['claim_id'] for r in rows}=={r['claim_id'] for r in claims}
    assert len({r['paper_id'] for r in rows})==19
    assert len({r['cohort_id'] for r in rows})==18
    count=dict(Counter(r['reusability_class'] for r in rows));count.setdefault('FULLY_REUSABLE',0)
    assert count=={'FULLY_REUSABLE':0,'PARTIALLY_REUSABLE':13,'NOT_REUSABLE':5,'UNRESOLVED':32}
    qc=module('phase2p_qc');builder=module('phase2p_build_audit')
    assert all(builder.rule_class(r)==r['reusability_class'] for r in rows)
    flags=[qc.cascade_flags(r) for r in rows]
    cascade=[sum(f[i] for f in flags) for i in range(len(flags[0]))]
    assert cascade==[50,41,15,8,8,1,1,0,0],cascade
    stops=dict(Counter(qc.stop_label(r)[1] for r in rows))
    recorded=read('PHASE2P_FIRST_UNCLOSED_NODE.tsv')
    # Summary table retains both stop label and node; compare count by label.
    key=next(k for k in recorded[0] if k in {'stop_label','first_unclosed_status','stop'})
    nkey=next(k for k in recorded[0] if k in {'n','n_claims','count'})
    assert stops=={r[key]:int(r[nkey]) for r in recorded},(stops,recorded)
    marginal={
        'cohort_identified':sum(r['cohort_status']=='VERIFIED' for r in rows),
        'assay_identified':sum(r['assay_status']=='VERIFIED' for r in rows),
        'public_data_available':sum(r['accession_status']=='VERIFIED_PUBLIC' for r in rows),
        'donor_mapped':sum(r['donor_status']=='VERIFIED' for r in rows),
        'condition_mapped':sum(r['condition_status']=='VERIFIED' for r in rows),
        'author_label_recovered':sum(r['author_label_status'] in {'EXACT_AUTHOR_LABEL','DETERMINISTIC_COLLAPSE'} for r in rows),
        'numerator_recovered':sum(r['numerator_status'] in {'EXACT','RECONSTRUCTABLE'} for r in rows),
        'denominator_recovered':sum(r['denominator_status'] in {'EXACT','RECONSTRUCTABLE'} for r in rows)}
    assert marginal=={r['node']:int(r['n_closed']) for r in read('PHASE2P_NODE_CLOSURE.tsv')}
    rng=np.random.default_rng(20261008)
    a=qc.bootstrap(rows,'paper_id',rng);b=qc.bootstrap(rows,'cohort_id',np.random.default_rng(20261008))
    for r in read('PHASE2P_CLUSTER_SENSITIVITY.tsv'):
        if r['class']=='FULLY_REUSABLE':
            assert r['interval_status']=='NOT_INFORMATIVE_FOR_ZERO_EVENT' and not r['stability_interval_low']
        else:
            got=(a if r['analysis']=='A' else b)[r['class']]
            assert got==(float(r['stability_interval_low']),float(r['stability_interval_high'])),(r,got)
    result={'status':'PASS','claims':50,'papers':19,'cohorts':18,'classes':count,'cascade':cascade,'marginal_closure':marginal,'first_stops':stops,'paper_bootstrap':a,'cohort_bootstrap':b,'seed':20261008,'replicates':10000,'class_rule_matches':50,'frozen_hashes':'PASS','biological_models':'NOT_RUN'}
    (out/'NUMERIC_QC.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: frozen hashes, 50 class rules, cascade, marginal closure, stops and clustered bootstrap')
if __name__=='__main__':main()
