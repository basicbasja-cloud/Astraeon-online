"""Propose silver-haired head ownership from observed hair and adjacent face.

A palette-specific label proposal, never a general anatomy certificate. Original
RGBA is transferred between cutouts without repainting or changing the master.
"""
import argparse,json,shutil
from pathlib import Path
import numpy as np
from PIL import Image
from refine_preserved_head_cutouts import head_prompt,transfer
from track_visible_cutouts import pin_inputs,verify_inputs


def propose(head):
    import cv2
    _,hair=head_prompt(head);a=np.array(head);rgb=a[:,:,:3].astype(float);hi=rgb.max(2);lo=rgb.min(2);sat=(hi-lo)/np.maximum(hi,1)
    yy,xx=np.where(hair);center=np.array([xx.mean(),yy.mean()]);gy,gx=np.indices(hair.shape)
    skin=(a[:,:,3]>32)&(hi>105)&(rgb[:,:,0]>rgb[:,:,1]*1.15)&(rgb[:,:,1]>rgb[:,:,2]*1.1)&(rgb[:,:,1]<rgb[:,:,2]*1.8)&(sat>.30)&(sat<.64)
    skin&=(gx>=xx.min()-8)&(gx<=xx.max()+8)&(gy>=yy.min())&(gy<=yy.max()+18)
    count,labels,stats,centroids=cv2.connectedComponentsWithStats(skin.astype('uint8'),8)
    seeds=hair.copy();chosen=None
    if count>1:
        choices=[]
        for n in range(1,count):
            sy,sx=np.where(labels==n)
            if len(sx)<6:continue
            distance=float(np.min((sx-center[0])**2+(sy-center[1])**2));choices.append((distance,n))
        if choices:
            chosen=min(choices)[1];seeds|=labels==chosen
    sy,sx=np.where(seeds);points=np.column_stack([sx,sy]).astype('int32');hull=cv2.convexHull(points);mask=np.zeros(hair.shape,'uint8');cv2.fillConvexPoly(mask,hull,1);mask=cv2.dilate(mask,np.ones((3,3),'uint8'))>0
    return mask,{'method':'observed silver-hair component plus nearest bounded warm face component convex hull, one-pixel boundary allowance','observed_hair_pixels':int(hair.sum()),'face_component_found':chosen is not None}


def build(source,output):
    if output.exists():raise ValueError('Choose a new proposal directory')
    directions=['SW','NW','NE','SE'];roles=['Master','BodyCostume','HeadHair','Weapon','WeaponHandOccluder','WeaponLightBack','WeaponLightFront'];paths=[source/d/r/f'{i:03d}.png'for d in directions for r in roles for i in range(16)];pins=pin_inputs([Path(__file__),Path(__file__).with_name('refine_preserved_head_cutouts.py'),*paths]);output.mkdir(parents=True);rows=[]
    for d in directions:
        for i in range(16):
            master=Image.open(source/d/'Master'/f'{i:03d}.png').convert('RGBA');head=Image.open(source/d/'HeadHair'/f'{i:03d}.png').convert('RGBA');body=Image.open(source/d/'BodyCostume'/f'{i:03d}.png').convert('RGBA');mask,record=propose(head);newbody,newhead,count=transfer(master,body,head,mask)
            parts={'BodyCostume':newbody,'HeadHair':newhead,'Weapon':Image.open(source/d/'Weapon'/f'{i:03d}.png').convert('RGBA'),'WeaponHandOccluder':Image.open(source/d/'WeaponHandOccluder'/f'{i:03d}.png').convert('RGBA')};composed=Image.new('RGBA',master.size)
            for im in parts.values():composed.alpha_composite(im)
            if composed.tobytes()!=master.tobytes():raise ValueError('Original master pixels changed')
            for role in roles:
                dest=output/d/role;dest.mkdir(parents=True,exist_ok=True)
                if role in ['BodyCostume','HeadHair']:parts[role].save(dest/f'{i:03d}.png')
                else:shutil.copy2(source/d/role/f'{i:03d}.png',dest/f'{i:03d}.png')
            rows.append({'direction':d,'index':i,'body_reassigned_pixels':count,'recomposition_changed_pixels':0,**record})
    verify_inputs(pins);(output/'receipt.json').write_text(json.dumps({'status':'OBSERVED_HEAD_LABEL_PROPOSAL_REQUIRES_SEMANTIC_REVIEW','input_pins':pins,'frames':rows,'source_rgba_modified':False,'runtime_admitted':False},indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.source,a.output)
