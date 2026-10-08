"""Figure package drawn exclusively from frozen audit metadata."""
from pathlib import Path
import csv, argparse, textwrap
from collections import Counter
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
ROOT=Path(__file__).resolve().parents[1]
def read(name):return list(csv.DictReader((ROOT/name).open(),delimiter='\t'))
PALETTE={'closed':'#328C80','partial':'#C89D42','unresolved':'#D8DADD','confirmed':'#8A5748','near':'#48768B'}
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','Helvetica','DejaVu Sans'],'font.size':8,'svg.fonttype':'none','pdf.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':0.6,'legend.frameon':False})
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='figures');args=ap.parse_args()
    out=Path(args.output);out=out if out.is_absolute() else ROOT/out;out.mkdir(parents=True,exist_ok=True)
    rows=read('PHASE2P_MASTER_CLAIM_PROVENANCE.tsv')
    def save(fig,name):
        fig.savefig(out/(name+'.svg'))
        fig.savefig(out/(name+'.png'),dpi=300)
        fig.savefig(out/(name+'.tiff'),dpi=600,pil_kwargs={'compression':'tiff_lzw'})
        plt.close(fig)
    counts=[int(r['n']) for r in read('PHASE2P_NESTED_ATTRITION.tsv')]
    labels=['Audited claims','Verified public source','Verified cohort within public source','Donor map','Condition map','Author label','Numerator','Denominator','Fully reusable']
    fig,ax=plt.subplots(figsize=(7.1,4.1));y=np.arange(9)
    ax.barh(y,counts,color=[PALETTE['unresolved']]+[PALETTE['closed']]*8,height=.65)
    ax.set_yticks(y,labels);ax.invert_yaxis();ax.set_xlim(0,55);ax.set_xticks([0,10,20,30,40,50]);ax.set_xlabel('Claims retained in the nested chain (initial n = 50)')
    for yi,n in zip(y,counts):ax.text(n+.6,yi,str(n),va='center',fontsize=8)
    ax.set_title('Public source to published composition estimand',loc='left',fontsize=10)
    fig.subplots_adjust(left=.40,right=.98,bottom=.15,top=.90);save(fig,'Figure1_Provenance_Attrition')
    stoprows=read('PHASE2P_FIRST_UNCLOSED_BY_CLAIM.tsv')
    nodes=['PUBLIC_SOURCE','COHORT','ASSAY','DONOR','CONDITION','AUTHOR_LABEL','NUMERATOR','DENOMINATOR']
    types=['unresolved','partial','confirmed','near'];lab={'unresolved':'Unresolved','partial':'Partial evidence','confirmed':'Source-supported break','near':'Opened near match'}
    def kind(r):
        l=r['stop_label']
        return 'unresolved' if l.startswith('UNRESOLVED') else 'confirmed' if l.startswith('CONFIRMED') else 'near' if l.startswith('NEAR') else 'partial'
    fig,ax=plt.subplots(figsize=(7.1,4.0));left=np.zeros(8)
    for k in types:
        vals=np.array([sum(r['first_unclosed_node']==node and kind(r)==k for r in stoprows) for node in nodes])
        ax.barh(range(8),vals,left=left,color=PALETTE[k],label=lab[k],height=.65);left+=vals
    ax.set_yticks(range(8),['Public source','Cohort','Assay','Donor','Condition','Author label','Numerator','Denominator']);ax.invert_yaxis();ax.set_xlabel('Claims at the first unclosed node (n = 50)');ax.set_xlim(0,30)
    for i,n in enumerate(left):ax.text(n+.4,i,str(int(n)),va='center')
    ax.legend(loc='lower right',fontsize=7);ax.set_title('Where the reconstruction chain first stops',loc='left',fontsize=10)
    fig.subplots_adjust(left=.18,right=.98,top=.9,bottom=.16);save(fig,'Figure2_First_Unclosed_Node')
    cols=[('cohort_status',{'VERIFIED'},{'PARTIAL'}),('assay_status',{'VERIFIED'},{'PARTIAL'}),('accession_status',{'VERIFIED_PUBLIC'},{'PARTIAL_PUBLIC'}),('donor_status',{'VERIFIED'},{'PARTIAL'}),('condition_status',{'VERIFIED'},{'PARTIAL'}),('author_label_status',{'EXACT_AUTHOR_LABEL','DETERMINISTIC_COLLAPSE'},{'REFERENCE_MAPPING_REQUIRED'}),('numerator_status',{'EXACT','RECONSTRUCTABLE'},{'AMBIGUOUS'}),('denominator_status',{'EXACT','RECONSTRUCTABLE'},set())]
    order=sorted(rows,key=lambda r:(r['reusability_class'],r['paper_id'],r['claim_id']))
    mat=np.zeros((50,8));confirmed={'VERIFIED_NOT_PUBLIC','CONFIRMED_MISSING','CONFIRMED_NOT_AVAILABLE','MISMATCH'}
    for i,r in enumerate(order):
        for j,(c,yes,mid) in enumerate(cols):
            mat[i,j]=3 if r[c] in yes else 2 if r[c] in mid else 4 if r[c]=='NEAR_MATCH_UNEXPLAINED' else 1 if r[c] in confirmed else 0
    fig,ax=plt.subplots(figsize=(7.1,10.2));colors=[PALETTE[k] for k in ['unresolved','confirmed','partial','closed','near']]
    ax.imshow(mat,cmap=ListedColormap(colors),vmin=0,vmax=4,aspect='auto',interpolation='none')
    ax.set_xticks(range(8),['Cohort','Assay','Public source','Donor','Condition','Author label','Numerator','Denominator'],rotation=45,rotation_mode='anchor',ha='right',fontsize=8)
    ax.set_yticks(range(50),[f'C{i+1:02d}' for i in range(50)],fontsize=7)
    for i in range(1,50):
        if order[i]['paper_id']!=order[i-1]['paper_id']:ax.axhline(i-.5,color='white',lw=.8)
    ax.set_title('Claim-level provenance matrix (n = 50)',loc='left',fontsize=10,pad=12)
    fig.legend(handles=[Patch(color=PALETTE[k],label=v) for k,v in [('closed','Closed'),('partial','Partial'),('unresolved','Unresolved'),('confirmed','Source-supported break'),('near','Near match')]],loc='lower center',ncol=3,fontsize=7,bbox_to_anchor=(.52,.006))
    fig.subplots_adjust(left=.10,right=.97,top=.95,bottom=.14);save(fig,'Figure3_Claim_Provenance_Matrix')
    with (out/'Figure3_ROW_KEYS.tsv').open('w') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(['row_key','claim_id','paper_id','cohort_id']);w.writerows([[f'C{i+1:02d}',r['claim_id'],r['paper_id'],r['cohort_id']] for i,r in enumerate(order)])
    cases=[
        ('a','Near-complete provenance','PATS / GSE135893','Numerator: 485 KRT5-/KRT17+ cells\nPublic denominator candidate: 11,727\nPrinted denominator: 11,725\nNo rule identifies the two excluded cells.','NEAR_MATCH_UNEXPLAINED','near'),
        ('b','Control record; case source unresolved','GSE131685','A public control source is identified.\nCase matrices were not located within\nthe bounded search.\nAbsence elsewhere is not established.','UNRESOLVED','unresolved'),
        ('c','Donor and condition without author labels','GSE131882','Six donor/sample objects were opened.\nConditions are recoverable.\nAuthor labels are absent from opened counts.\nA linked browser was not fetched.','PARTIALLY_REUSABLE','partial'),
        ('d','Claimed population outside assay scope','GSE245906','The opened object is an innate-cell sort.\nCytotoxic CD4 T cells and hepatocytes\nfall outside this assay.\nTwo claims have source-supported breaks.','NOT_REUSABLE','confirmed')]
    fig,axes=plt.subplots(2,2,figsize=(7.1,5.5))
    for ax,(panel,title,source,body,status,k) in zip(axes.ravel(),cases):
        ax.set_axis_off();ax.text(0,1,panel,fontweight='bold',fontsize=11,transform=ax.transAxes,va='top')
        ax.text(.09,.99,'\n'.join(textwrap.wrap(title,31)),fontsize=9,fontweight='bold',va='top',transform=ax.transAxes)
        ax.text(.02,.75,source,fontsize=8,color='#555555',transform=ax.transAxes)
        ax.text(.02,.63,body,fontsize=8,va='top',linespacing=1.6,transform=ax.transAxes)
        ax.text(.02,.12,status,fontsize=7,fontweight='bold',color=PALETTE[k] if k!='unresolved' else '#666666',transform=ax.transAxes)
        ax.axhline(.05,color=PALETTE[k],lw=2,xmin=.02,xmax=.96)
    fig.subplots_adjust(left=.055,right=.985,bottom=.03,top=.98,wspace=.12,hspace=.12);save(fig,'Figure4_Reconstruction_Cases')
    design={r['cohort_id']:r['design_tags'] for r in read('PHASE2P_COHORT_DESIGN.tsv')}
    groups=[('Broad cell-type label',lambda r:r['claim_granularity']=='BROAD_CELL_TYPE'),('Other state label',lambda r:r['claim_granularity']!='BROAD_CELL_TYPE')]
    for tag,name in [('REUSED_COHORT','Reused cohort'),('MULTI_ASSAY','Multi-assay'),('LONGITUDINAL','Longitudinal')]:
        groups.extend([(name+' tag',lambda r,t=tag:t in design.get(r['cohort_id'],'')),('No '+name.lower()+' tag',lambda r,t=tag:t not in design.get(r['cohort_id'],''))])
    vals=[];texts=[]
    for name,pred in groups:
        data=[float(r['provenance_closure_score']) for r in rows if pred(r)];vals.append(float(np.mean(data)) if data else 0);texts.append(f'{name} (n = {len(data)})')
    fig,ax=plt.subplots(figsize=(7.1,3.7));ax.barh(range(8),vals,color=PALETTE['near'],height=.65);ax.set_yticks(range(8),texts);ax.invert_yaxis();ax.set_xlim(0,9);ax.set_xlabel('Mean descriptive closure score (0–9)');ax.set_title('Descriptive score slices; overlapping groups, no tests',loc='left',fontsize=9)
    fig.subplots_adjust(left=.38,right=.98,bottom=.16,top=.89);save(fig,'FigureS1_Descriptive_Closure_Scores')
    print('Created four main figures and Supplementary Figure S1 in SVG/PNG/600-dpi TIFF; no PDF output')
if __name__=='__main__':main()
