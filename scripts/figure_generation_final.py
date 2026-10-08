"""Redraw frozen provenance displays and assemble the V9 visual revision."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import csv, json, re, hashlib, argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Patch
from matplotlib.colors import to_rgb

ap=argparse.ArgumentParser(description='Reproduce final manuscript visuals from the frozen public data; no classifications are changed.')
ap.add_argument('--source',type=Path,default=Path(__file__).resolve().parents[1],help='Frozen release directory')
ap.add_argument('--output',type=Path,required=True,help='New output directory')
args=ap.parse_args()
SOURCE=args.source.resolve()
OUT=args.output.resolve()
FIG=OUT;QA=OUT/'_qc'
FIG.mkdir(parents=True,exist_ok=True);QA.mkdir(parents=True,exist_ok=True)
PALETTE={'closed':'#328C80','partial':'#C89D42','unresolved':'#D8DADD','break':'#8A5748','near':'#48768B'}
SYMBOL={'closed':'+','partial':'/','unresolved':'?','break':'×','near':'≈'}
HATCH={'closed':'','partial':'///','unresolved':'..','break':'xx','near':'--'}
STATE_LABEL={'closed':'Closed','partial':'Partial','unresolved':'Unresolved','break':'Source-supported break','near':'Near match'}
CLASS_ORDER=['PARTIALLY_REUSABLE','NOT_REUSABLE','UNRESOLVED']
NODES=['PUBLIC_SOURCE','COHORT','ASSAY','DONOR','CONDITION','AUTHOR_LABEL','NUMERATOR','DENOMINATOR']
DISPLAY=['Public source','Cohort','Assay','Donor','Condition','Author label','Numerator','Denominator']
COLS=['cohort_status','assay_status','accession_status','donor_status','condition_status','author_label_status','numerator_status','denominator_status']
CLASS_COLOR={'FULLY_REUSABLE':'closed','PARTIALLY_REUSABLE':'partial','NOT_REUSABLE':'break','UNRESOLVED':'unresolved'}
plt.rcParams.update({'font.family':'sans-serif','font.sans-serif':['Arial','Helvetica','DejaVu Sans'],'font.size':8,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.6,'legend.frameon':False,'hatch.linewidth':.4})
def read(name):
    return list(csv.DictReader((SOURCE/name).open(),delimiter='\t'))
rows=read('PHASE2P_MASTER_CLAIM_PROVENANCE.tsv')
locked=read('FINAL_LAYER_A_CLAIMS_v1.1.tsv')
stops=read('PHASE2P_FIRST_UNCLOSED_BY_CLAIM.tsv')
stopmap={r['claim_id']:r for r in stops}
citations={r['paper_id']:r for r in read('SOURCE_STUDY_CITATIONS.tsv')}
design={r['cohort_id']:r['design_tags'] for r in read('PHASE2P_COHORT_DESIGN.tsv')}
def state(status):
    if status in {'VERIFIED','VERIFIED_PUBLIC','EXACT_AUTHOR_LABEL','DETERMINISTIC_COLLAPSE','EXACT','RECONSTRUCTABLE'}: return 'closed'
    if status in {'PARTIAL','PARTIAL_PUBLIC','REFERENCE_MAPPING_REQUIRED','AMBIGUOUS'}:return 'partial'
    if status in {'VERIFIED_NOT_PUBLIC','CONFIRMED_MISSING','CONFIRMED_NOT_AVAILABLE','MISMATCH'}:return 'break'
    if status=='NEAR_MATCH_UNEXPLAINED':return 'near'
    assert status=='UNRESOLVED',status
    return 'unresolved'
order=sorted(rows,key=lambda r:(CLASS_ORDER.index(r['reusability_class']),NODES.index(stopmap[r['claim_id']]['first_unclosed_node']),r['cohort_id'],r['paper_id'],r['claim_id']))
keys={r['claim_id']:f'C{i+1:02d}' for i,r in enumerate(order)}
def tsv(path,fields,data):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t');w.writeheader();w.writerows(data)
def export(fig,name):
    # Keep exact physical canvas dimensions; do not crop/rescale publication text.
    fig.savefig(FIG/(name+'.pdf'))
    fig.savefig(FIG/(name+'.svg'))
    fig.savefig(FIG/(name+'.png'),dpi=600)
    fig.savefig(QA/(name+'_preview.png'),dpi=300)
    plt.close(fig)
def figure1():
    fig=plt.figure(figsize=(7.2,6.5))
    ax=fig.add_axes([.035,.675,.94,.27]);ax.set(xlim=(0,100),ylim=(0,100));ax.axis('off')
    ax.text(0,106,'a',weight='bold',fontsize=11)
    ax.text(4,106,'Claim-to-estimand provenance framework',fontsize=10,weight='bold')
    groups=[(12,32.5,'Dataset / study identity'),(45,21.5,'Biological-unit\nprovenance'),(67,32.6,'Claim / estimand\nprovenance')]
    for x,w,label in groups:
        ax.add_patch(Rectangle((x,10),w,81,facecolor='none',edgecolor='#909090',lw=.6))
        ax.text(x+w/2,80,label,ha='center',va='center',fontsize=8)
    titles=['Published\nclaim','Public\nsource','Cohort','Assay','Donor','Condition','Author\nlabel','Numerator','Denominator']
    xs=[.2]+[12.5+11*i for i in range(8)]
    for i,(x,title) in enumerate(zip(xs,titles)):
        ax.add_patch(Rectangle((x,43),9.5,25,facecolor='white',edgecolor='#454545',lw=.7))
        ax.text(x+4.75,55.5,title,ha='center',va='center',fontsize=7.4)
        if i<8:ax.add_patch(FancyArrowPatch((x+9.5,55.5),(xs[i+1],55.5),arrowstyle='->',mutation_scale=7,lw=.7,color='#454545'))
    for x,text in [(xs[6],'Published\nstate identity'),(xs[7],'Cells counted\nas the state'),(xs[8],'Reference\ncell universe')]:ax.text(x+4.75,27,text,ha='center',va='center',fontsize=7.1)
    ax.text(12.5,-1,'Dataset-level reuse',fontsize=8)
    ax.text(98,-1,'Claim-level estimand reconstruction',ha='right',fontsize=8)
    ax.add_patch(FancyArrowPatch((40,1),(64,1),arrowstyle='->',mutation_scale=8,color='#454545',lw=.8))
    ax=fig.add_axes([.375,.09,.585,.535])
    counts=[int(r['n']) for r in read('PHASE2P_NESTED_ATTRITION.tsv')]
    labels=['Audited claims','Verified public source','Verified cohort within public source','Donor map','Condition map','Author label','Numerator','Denominator','Fully reusable']
    ax.barh(range(9),counts,height=.61,color=['white']+[PALETTE['closed']]*8,edgecolor=['#454545']+[PALETTE['closed']]*8,lw=.8)
    ax.set_yticks(range(9),labels,fontsize=8);ax.invert_yaxis();ax.set_xlim(0,60);ax.set_xticks([0,10,20,30,40,50]);ax.set_xlabel('Claims retained (initial n = 50)',fontsize=8)
    for i,n in enumerate(counts):ax.text(n+.8,i,'50' if i==0 else f'{n} ({n*2}%)' if n else '0',va='center',fontsize=8)
    fig.text(.035,.645,'b',weight='bold',fontsize=11)
    fig.text(.073,.645,'Attrition from public source to published composition estimand',fontsize=9.5,weight='bold')
    export(fig,'Figure1_Framework_Attrition_FINAL')
def figure2():
    fig,ax=plt.subplots(figsize=(7.2,4.2))
    left=np.zeros(8)
    for k in ['unresolved','partial','break','near']:
        values=np.array([sum(r['first_unclosed_node']==node and state(r['node_status'])==k for r in stops) for node in NODES])
        ax.barh(range(8),values,left=left,height=.64,color=PALETTE[k],edgecolor='#454545',lw=.5,hatch=HATCH[k],label=STATE_LABEL[k]);left+=values
    ax.set_yticks(range(8),DISPLAY,fontsize=8);ax.invert_yaxis();ax.set_xlim(0,30);ax.set_xticks([0,5,10,15,20,25,30]);ax.set_xlabel('Claims at first incomplete node (n = 50)',fontsize=8)
    for i,n in enumerate(left):
        if n:ax.text(n+.45,i,str(int(n)),va='center',fontsize=8)
    fig.text(.04,.94,'Where the reconstruction chain first becomes incomplete',fontsize=10,weight='bold')
    fig.legend(loc='lower center',ncol=2,bbox_to_anchor=(.54,.006),fontsize=8)
    fig.subplots_adjust(left=.19,right=.97,top=.865,bottom=.26)
    export(fig,'Figure2_First_Incomplete_Node_FINAL')
def figure3():
    fig=plt.figure(figsize=(10.0,6.9))
    ax=fig.add_axes([.155,.13,.82,.785]);ax.axis('off');ax.set(xlim=(-.85,8),ylim=(51.3,-2.4))
    groups=[(0,3,'Dataset identity'),(3,5,'Biological-unit provenance'),(5,8,'Claim-definition provenance')]
    for a,b,label in groups:
        ax.add_patch(Rectangle((a,-2.35),b-a,1.15,facecolor='#F4F4F4',edgecolor='#707070',lw=.6))
        ax.text((a+b)/2,-1.76,label,ha='center',va='center',fontsize=9)
    for j,label in enumerate(['Cohort','Assay','Public source','Donor','Condition','Author label','Numerator','Denominator']):ax.text(j+.5,-.67,label,ha='center',va='center',fontsize=8)
    ax.text(-.4,-.67,'Class',ha='center',va='center',fontsize=8)
    for i,r in enumerate(order):
        ck=CLASS_COLOR[r['reusability_class']]
        ax.add_patch(Rectangle((-.67,i),.43,1,facecolor=PALETTE[ck],edgecolor='white',lw=.3))
        ax.text(-.455,i+.5,SYMBOL[ck],ha='center',va='center',fontsize=7.5,color='white' if ck=='break' else '#252525')
        ax.text(-.88,i+.5,keys[r['claim_id']],ha='right',va='center',fontsize=8)
        for j,col in enumerate(COLS):
            k=state(r[col]);ax.add_patch(Rectangle((j,i),1,1,facecolor=PALETTE[k],edgecolor='white',lw=.3))
            ax.text(j+.5,i+.5,SYMBOL[k],ha='center',va='center',fontsize=7.7,color='white' if k in {'closed','break','near'} else '#252525')
        if i and r['reusability_class']!=order[i-1]['reusability_class']:
            ax.plot([-.7,8],[i,i],color='#222222',lw=1.3)
        elif i and (r['cohort_id'],r['paper_id'])!=(order[i-1]['cohort_id'],order[i-1]['paper_id']):
            ax.plot([-.7,8],[i,i],color='#707070',lw=.7)
    for j in [0,3,5,8]:ax.plot([j,j],[0,50],color='#707070',lw=.7)
    # Class labels use the same status semantics; brace connects each contiguous block.
    for cls,label in [('PARTIALLY_REUSABLE','Partially\nreusable'),('NOT_REUSABLE','Not\nreusable'),('UNRESOLVED','Unresolved')]:
        indices=[i for i,r in enumerate(order) if r['reusability_class']==cls];lo=min(indices);hi=max(indices)+1
        ax.plot([-1.35,-1.25,-1.25,-1.35],[lo,lo,hi,hi],color='#454545',lw=.8,clip_on=False)
        ax.text(-1.5,(lo+hi)/2,label,ha='right',va='center',fontsize=8,clip_on=False)
    fig.text(.035,.968,'Claim-level provenance matrix (n = 50)',fontsize=11,weight='bold')
    handles=[Patch(facecolor=PALETTE[k],edgecolor='#454545',label=f'{SYMBOL[k]}  {STATE_LABEL[k]}') for k in PALETTE]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.54,.041),ncol=5,fontsize=8)
    fig.text(.035,.018,'Row keys C01–C50 map to claim, paper and cohort identifiers in Figure3_ROW_ORDER.tsv and Supplementary Table S3.',fontsize=8)
    export(fig,'Figure3_Claim_Provenance_Matrix_FINAL')
    tsv(FIG/'Figure3_ROW_ORDER.tsv',['display_order','row_key','claim_id','reusability_class','first_unclosed_node','cohort_id','paper_id'],[dict(display_order=i+1,row_key=keys[r['claim_id']],claim_id=r['claim_id'],reusability_class=r['reusability_class'],first_unclosed_node=stopmap[r['claim_id']]['first_unclosed_node'],cohort_id=r['cohort_id'],paper_id=r['paper_id']) for i,r in enumerate(order)])
def box(ax,y,text,k=None,height=.105,fs=8):
    ax.add_patch(Rectangle((.03,y-height),.94,height,facecolor='white',edgecolor='#676767',lw=.65))
    if k:
        ax.add_patch(Rectangle((.03,y-height),.08,height,facecolor=PALETTE[k],edgecolor='#676767',lw=.5))
        ax.text(.07,y-height/2,SYMBOL[k],ha='center',va='center',fontsize=9,color='white' if k in {'closed','break','near'} else '#252525')
    ax.text(.54 if k else .5,y-height/2,text,ha='center',va='center',fontsize=fs)
def arrow(ax,top,bottom):ax.add_patch(FancyArrowPatch((.5,top),(.5,bottom),arrowstyle='->',mutation_scale=8,lw=.7,color='#454545'))
def figure4():
    fig,axes=plt.subplots(2,2,figsize=(7.2,6.8))
    for ax in axes.ravel():ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
    titles=['a  PATS / GSE135893','b  Transplant / GSE131685','c  Diabetic kidney / GSE131882','d  HCC / GSE245906']
    for ax,title in zip(axes.ravel(),titles):ax.text(.03,.99,title,fontsize=9,weight='bold',va='top')
    a,b,c,d=axes.ravel()
    for y,text,k,h in [(.88,'Public author label\nKRT5-/KRT17+','closed',.12),(.72,'Numerator: 485 cells','closed',.09),(.59,'Candidate public denominator\n11,727 cells',None,.12),(.43,'Published denominator\n11,725 cells',None,.12),(.27,'Two-cell provenance gap\nNEAR_MATCH_UNEXPLAINED\nClaim class: PARTIALLY_REUSABLE','near',.16)]:box(a,y,text,k,h,7.2 if k=='near' else 7.7)
    for top,bottom in [(.76,.72),(.63,.59),(.47,.43),(.31,.27)]:arrow(a,top,bottom)
    a.text(.03,.08,'No source-supported rule identified\ntwo cells to exclude.',fontsize=7.2,va='top')
    for y,text,k in [(.86,'Public control source','closed'),(.63,'Case source: not located\nwithin bounded search','unresolved'),(.38,'UNRESOLVED','unresolved')]:box(b,y,text,k,.14,8)
    arrow(b,.72,.63);arrow(b,.49,.38)
    b.text(.03,.145,'Non-location within bounded search\n≠ confirmed absence.',fontsize=8,va='top')
    for y,text,k in [(.86,'Donor mapping','closed'),(.64,'Condition mapping','closed'),(.42,'Author label in opened objects\nNot recovered','unresolved'),(.18,'PARTIALLY_REUSABLE','partial')]:box(c,y,text,k,.14,8)
    for top,bottom in [(.72,.64),(.50,.42),(.28,.18)]:arrow(c,top,bottom)
    # The opened counts did not recover the annotation; availability elsewhere remains unresolved.
    for y,text,k in [(.86,'Public assay','closed'),(.64,'Innate-cell sort',None),(.42,'Cytotoxic CD4 T cells / hepatocytes\nOutside assay scope','break'),(.18,'SOURCE-SUPPORTED BREAK\nClaim class: NOT_REUSABLE','break')]:box(d,y,text,k,.14,7.7)
    for top,bottom in [(.72,.64),(.50,.42),(.28,.18)]:arrow(d,top,bottom)
    fig.subplots_adjust(left=.025,right=.975,top=.965,bottom=.04,wspace=.12,hspace=.14)
    fig.text(.04,.014,'Symbols: + Closed   / Partial   ? Unresolved   × Source-supported break   ≈ Near match',fontsize=7.7)
    export(fig,'Figure4_Reconstruction_Cases_FINAL')
def figureS1():
    groups=[('Broad cell-type label',lambda r:r['claim_granularity']=='BROAD_CELL_TYPE'),('Other state label',lambda r:r['claim_granularity']!='BROAD_CELL_TYPE')]
    for tag,name in [('REUSED_COHORT','Reused cohort'),('MULTI_ASSAY','Multi-assay'),('LONGITUDINAL','Longitudinal')]:
        groups.extend([(name+' tag',lambda r,t=tag:t in design[r['cohort_id']]),('No '+name.lower()+' tag',lambda r,t=tag:t not in design[r['cohort_id']])])
    values=[];labels=[];records=[]
    for name,pred in groups:
        data=[float(r['provenance_closure_score']) for r in rows if pred(r)]
        value=float(np.mean(data));values.append(value);labels.append(f'{name} (n = {len(data)})');records.append({'slice':name,'n_claims':len(data),'mean_closure_score':value})
    fig,ax=plt.subplots(figsize=(7.2,3.8))
    ax.barh(range(8),values,height=.62,color='#454545');ax.set_yticks(range(8),labels,fontsize=8);ax.invert_yaxis();ax.set_xlim(0,9);ax.set_xticks(range(10));ax.set_xlabel('Mean descriptive closure score (0–9)',fontsize=8)
    fig.text(.04,.95,'Descriptive provenance-closure scores across study characteristics',fontsize=9.5,weight='bold')
    fig.text(.04,.015,'Descriptive only; overlapping strata; no inferential tests or predictor interpretation.',fontsize=8)
    fig.subplots_adjust(left=.38,right=.97,top=.87,bottom=.17)
    export(fig,'Supplementary_Figure_S1_Closure_Scores_FINAL')
    tsv(QA/'S1_display_values.tsv',list(records[0]),records)

figure1();figure2();figure3();figure4();figureS1()
print("Created final manuscript figure layouts from frozen public metadata")
