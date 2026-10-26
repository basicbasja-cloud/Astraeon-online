"""Seed reviewable same-frame roles from native head motion and observed skin.

This explicit back/side auburn Mage recipe is not a general character detector.
Observed hand points prevent a cream collar from becoming the hand occluder.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from audit_staff_motion import observed_crystal
from build_occluded_underlays import sha


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['masters','guide','reference-annotations','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Preserve previous manual annotations')
    reference=json.loads(a.reference_annotations.read_text());guide=json.loads((a.guide/'pilot-receipt.json').read_text());rows=guide['views']['NE']['frames'];base=np.array(rows[0]['landmarks']['Head']);base_hand=np.array(rows[0]['landmarks']['Hand.R']);bias=np.array([700,731])-base_hand;records=[]
    for row in rows:
        i=row['index'];file=a.masters/f'{i:03}.png';image=Image.open(file).convert('RGBA');pixels=np.array(image);rgb=pixels[:,:,:3].astype(float);r,g,b=rgb.transpose(2,0,1);yy,xx=np.indices(r.shape);head=np.array(row['landmarks']['Head']);delta=head-base
        if i==0:
            if sha(file)!=reference['frames'][0]['source_sha256']:raise ValueError('Manually annotated reference changed')
            records.append(reference['frames'][0]);continue
        expected=np.array(row['landmarks']['Hand.R'])+bias
        skin=(pixels[:,:,3]>200)&(r>170)&(g>120)&(b>75)&(r-g>25)&(r-g<90)&(g-b>15)&(g-b<75)&(abs(xx-expected[0])<45)&(abs(yy-expected[1])<35)
        ys,xs=np.where(skin)
        if not len(xs):raise ValueError('Missing observed staff hand in pose '+str(i))
        k=np.argmin((xs-expected[0])**2+(ys-expected[1])**2);hand=np.array([int(xs[k]),int(ys[k])]);crystal,_=observed_crystal(image,head[1]);wood=np.rint(crystal+[0,50]).astype(int)
        hx,hy=map(float,head);sx,sy=map(int,hand);cx,cy=map(float,crystal)
        positives=(np.array(reference['frames'][0]['roles']['HeadHair']['positive'])+delta).tolist()
        roles={
            'HeadHair':{'positive':positives,'negative':[hand.tolist(),(hand+[16,13]).tolist(),(np.array([805,775])+delta).tolist(),wood.tolist()],'box':[hx-120,hy-180,hx+120,hy+10],'pixel_range':[8000,35000]},
            'Weapon':{'positive':[crystal.tolist(),wood.tolist()],'negative':[positives[0],hand.tolist(),(hand+[16,13]).tolist()],'box':[cx-50,max(0,cy-60),cx+50,min(1536,sy+350)],'pixel_range':[1000,18000]},
            'WeaponHandOccluder':{'positive':[hand.tolist()],'negative':[(np.array([750,705])+delta).tolist(),(np.array([805,775])+delta).tolist(),wood.tolist()],'box':[sx-30,sy-25,sx+55,sy+42],'pixel_range':[200,6000]}}
        records.append({'index':i,'source_sha256':sha(file),'observed_skin_seed':hand.tolist(),'roles':roles,'requires_semantic_review':True})
    result={'priority':reference['priority'],'frames':records,'status':'SEEDED_SAME_FRAME_ANNOTATIONS_REQUIRE_REVIEW','guide_receipt_sha256':sha(a.guide/'pilot-receipt.json'),'reference_annotations_sha256':sha(a.reference_annotations),'implementation_sha256':sha(__file__)}
    a.output.write_text(json.dumps(result,indent=2)+'\n');print('seeded frames',len(records))


if __name__=='__main__':main()
