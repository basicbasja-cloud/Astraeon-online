"""Reassign a bounded warm-colored head fringe; do not redraw or move pixels.

This identity-specific proposal excludes the lower neckline band and neutral
bowstring colors. Review quiver/weapon boundaries before using the proposal.
"""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter,ImageDraw

def components(mask):
    todo=set(map(tuple,np.argwhere(mask)));groups=[]
    while todo:
        seed=todo.pop();stack=[seed];group=[seed]
        while stack:
            y,x=stack.pop()
            for point in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
                if point in todo:todo.remove(point);stack.append(point);group.append(point)
        groups.append(group)
    return groups

def refine(head,body,radius=2,neckline_band=4,right_profile=None,neutral_weapon_overlap=False):
    if head.size!=body.size:raise ValueError('Cutout canvases differ')
    if not 1<=radius<=3 or neckline_band<radius:raise ValueError('Unbounded cutout edge refinement')
    h=np.array(head.convert('RGBA'));b=np.array(body.convert('RGBA'));mask=h[:,:,3]>0
    if not mask.any():raise ValueError('Empty head cutout')
    if np.any(mask&(b[:,:,3]>0)):raise ValueError('Expected exclusive visible cutouts')
    original=np.array(Image.alpha_composite(Image.fromarray(b),Image.fromarray(h)))
    allowed=np.ones(mask.shape,dtype=bool);manual_to_body=np.zeros(mask.shape,dtype=bool)
    if right_profile:
        clip=Image.new('L',head.size);polygon=[(0,0),(right_profile[0][0],0),*[tuple(p)for p in right_profile],(right_profile[-1][0],head.height),(0,head.height)];ImageDraw.Draw(clip).polygon(polygon,fill=255);allowed=np.array(clip)>0;manual_to_body=mask&~allowed;b[manual_to_body]=h[manual_to_body];h[manual_to_body]=0;mask=h[:,:,3]>0
    # Thin neutral bowstring pixels can be mistakenly included at the face edge.
    # Restrict this identity-specific correction to the one-pixel outer boundary;
    # do not strip bright pixels from inside the face or hair.
    inner=np.array(Image.fromarray(mask.astype(np.uint8)*255).filter(ImageFilter.MinFilter(3)))>0
    rgb=h[:,:,:3].astype(int);neutral=((rgb.max(2)-rgb.min(2)<22)&(rgb.min(2)>125))|((rgb.min(2)>145)&(rgb[:,:,0]-rgb[:,:,1]<40)&(rgb[:,:,1]-rgb[:,:,2]<40));to_body=np.zeros(mask.shape,dtype=bool)
    for group in components(mask&neutral):
        if any(not inner[y,x] for y,x in group):
            for y,x in group:to_body[y,x]=True
    if neutral_weapon_overlap:to_body|=mask&neutral
    weapon_guard=np.array(Image.fromarray(to_body.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(3)))>0
    groups=components(h[:,:,3]>8);isolated=np.zeros(mask.shape,dtype=bool)
    if groups:
        largest=max(groups,key=len);main_bottom=max(y for y,x in largest);main_top=min(y for y,x in largest);main_left=min(x for y,x in largest);main_right=max(x for y,x in largest)
        for group in groups:
            if group is largest or len(group)>32:continue
            if min(y for y,x in group)>(main_top+main_bottom)/2 and(max(x for y,x in group)<main_left-2 or min(x for y,x in group)>main_right+2):
                for y,x in group:isolated[y,x]=True
                continue
            if min(y for y,x in group)<=main_bottom:continue
            values=np.array([h[y,x,:3]for y,x in group],dtype=float).mean(0)
            if values[0]>140 and values[0]>values[1]*1.10 and values[1]>values[2]*1.05:
                for y,x in group:isolated[y,x]=True
    to_body|=isolated;b[to_body]=h[to_body];h[to_body]=0;mask=h[:,:,3]>0
    if not mask.any():raise ValueError('Head rules removed all artwork; manual ownership needed')
    dilated=np.array(Image.fromarray(mask.astype(np.uint8)*255).filter(ImageFilter.MaxFilter(radius*2+1)))>0
    r,g,blue=b[:,:,:3].astype(float).transpose(2,0,1);warm=(r>g*1.10)&(g>blue*1.05);yy=np.indices(mask.shape)[0];lowest=np.nonzero(mask)[0].max()
    claim=dilated&~mask&allowed&~weapon_guard&(b[:,:,3]>0)&warm&(yy<lowest-neckline_band)
    h[claim]=b[claim];b[claim]=0;merged=np.array(Image.alpha_composite(Image.fromarray(b),Image.fromarray(h)))
    if not np.array_equal(original,merged):raise ValueError('Head/body ownership changed the complete master')
    return Image.fromarray(h),Image.fromarray(b),{'reassigned_pixels':int(claim.sum()+to_body.sum()+manual_to_body.sum()),'body_to_head_fringe_pixels':int(claim.sum()),'head_to_body_weapon_or_neck_pixels':int(to_body.sum()),'manual_hand_weapon_exclusion_pixels':int(manual_to_body.sum()),'isolated_neck_pixels':int(isolated.sum()),'master_pixel_changes':0,'pixel_translation':False,'redrawn_pixels':False,'radius_authoring_pixels':radius,'protected_neckline_band':neckline_band,'manually_marked_weapon_overlap':neutral_weapon_overlap}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--profiles',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);rows=[];profiles=json.loads(a.profiles.read_text())if a.profiles else{}
    for path in sorted((a.source/'HeadHair').glob('*.png')):
        body_path=a.source/'BodyCostume'/path.name;head,body,report=refine(Image.open(path),Image.open(body_path),right_profile=profiles.get(path.stem),neutral_weapon_overlap=path.stem in profiles)
        for role,im in [('HeadHair',head),('BodyCostume',body)]:target=a.output/role;target.mkdir(exist_ok=True);im.save(target/path.name)
        rows.append({'frame':path.stem,'head_source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'body_source_sha256':hashlib.sha256(body_path.read_bytes()).hexdigest(),**report})
    if not rows:raise ValueError('No actual cutouts found')
    receipt={'status':'EDGE_OWNERSHIP_PROPOSAL_REQUIRES_SEMANTIC_REVIEW','frames':rows,'source_parts':str(a.source),'manual_profiles_sha256':hashlib.sha256(a.profiles.read_bytes()).hexdigest()if a.profiles else None,'weapon_separated':False,'source_pose_registered':False,'owner_approved':False,'runtime_admitted':False,'limitations':['This color prior is specific to the chestnut-haired identity.','No hidden neckline/body surfaces are invented.','Quiver/wood/skin near the head boundary must be reviewed.']};(a.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'frames':len(rows),'reassigned_pixels':sum(r['reassigned_pixels']for r in rows),'master_pixel_changes':0}))
