"""Apply reviewed same-frame head boundaries without changing master pixels."""
import argparse,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from track_visible_cutouts import partition_visible,pin_inputs,verify_inputs,sha


def apply(masters,previous,annotations,output):
    if output.exists():raise ValueError('Preserve previous masks; use a new destination')
    data=json.loads(annotations.read_text());items=data['frames'];size=tuple(data['canvas'])
    if not items or len({r['index']for r in items})!=len(items):raise ValueError('Empty or duplicate annotations')
    def source(r,role):return (annotations.parent/r[role+'_source']).resolve()if role+'_source'in r else previous/role/f"{r['index']:03d}.png"
    paths=[annotations,Path(__file__)]+[p for r in items for p in [masters/f"{r['index']:03d}.png",source(r,'Weapon')]+([source(r,'HeadHair')]if r.get('mode')=='patch'else [])]
    pinned=pin_inputs(paths);output.mkdir(parents=True);records=[]
    has_hand=any(r.get('hand_occluder')for r in items)
    roles=['BodyCostume','HeadHair','Weapon']+(['WeaponHandOccluder']if has_hand else [])
    sheets={role:Image.new('RGBA',(size[0]*4,size[1]*math.ceil(len(items)/4)))for role in roles}
    for slot,r in enumerate(items):
        i=r['index'];master=Image.open(masters/f'{i:03d}.png')
        if master.mode!='RGBA' or master.size!=size or sha(masters/f'{i:03d}.png')!=r['master_sha256']:raise ValueError('Stale painted source')
        origin=np.asarray(r['crop_origin'],float)
        def polygon_mask(points):
            polygon=np.asarray(points,float)+origin
            if polygon.ndim!=2 or polygon.shape[1]!=2 or len(polygon)<3 or not np.isfinite(polygon).all() or polygon.min()<0 or np.any(polygon>=np.array(size)):raise ValueError('Invalid canonical polygon')
            mask=Image.new('L',size);ImageDraw.Draw(mask).polygon([tuple(p)for p in polygon],fill=255);return np.array(mask)>0
        original=np.array(master)
        def subset(path):
            image=Image.open(path)
            if image.mode!='RGBA' or image.size!=size:raise ValueError('Part canvas or mode differs')
            pixels=np.array(image);visible=pixels[:,:,3]>0
            if not np.array_equal(pixels[visible],original[visible]):raise ValueError('Part is not an unchanged same-frame source subset')
            return visible
        if r.get('mode')=='patch':h=subset(source(r,'HeadHair'))
        else:h=polygon_mask(r['polygon'])
        included=np.zeros_like(h)
        for points in r.get('include',[]):included|=polygon_mask(points)
        h|=included
        for points in r.get('exclude',[]):h&=~polygon_mask(points)
        hsv=np.array(master.convert('RGB').convert('HSV'))/255.
        for exclusion in r.get('exclude_material',[]):
            region=polygon_mask(exclusion['polygon']);lo,hi=exclusion['hue']
            if not 0<=lo<hi<=1 or not 0<=exclusion['minimum_saturation']<=1:raise ValueError('Invalid material exclusion')
            h&=~(region&(hsv[:,:,0]>=lo)&(hsv[:,:,0]<=hi)&(hsv[:,:,1]>=exclusion['minimum_saturation']))
        weapon=Image.open(source(r,'Weapon')).convert('RGBA')
        if weapon.size!=size:raise ValueError('Weapon canvas differs')
        w=subset(source(r,'Weapon'));w&=~included;h&=~w
        hand=np.zeros_like(h)
        for points in r.get('hand_occluder',[]):hand|=polygon_mask(points)
        if r.get('hand_from_body_only'):
            # Optional ownership restriction for same-frame palm/cuff proposals.
            # Existing head and weapon ownership is preserved, not certified.
            hand&=~h;hand&=~w
        if r.get('protect_gold_weapon_in_hand'):
            gold=(hsv[:,:,0]>.08)&(hsv[:,:,0]<.16)&(hsv[:,:,1]>.35)&(hsv[:,:,2]>.3)
            hand&=~(gold&w)
        h&=~hand;w&=~hand
        masks=[h,w]+([hand]if has_hand else [])
        parts=partition_visible(master,np.where(np.stack(masks),1.,-1.),['HeadHair','Weapon']+(['WeaponHandOccluder']if has_hand else []))
        ids=np.zeros((size[1],size[0]),np.uint8)
        for label,role in [(1,'BodyCostume'),(2,'HeadHair'),(3,'Weapon')]+([(6,'WeaponHandOccluder')]if has_hand else []):
            part=parts[role];folder=output/role;folder.mkdir(exist_ok=True);part.save(folder/f'{i:03d}.png')
            ids[np.array(part)[:,:,3]>0]=label;sheets[role].paste(part,((slot%4)*size[0],(slot//4)*size[1]))
        folder=output/'labels';folder.mkdir(exist_ok=True);Image.fromarray(ids).save(folder/f'{i:03d}.png')
        records.append({'index':i,'master_sha256':r['master_sha256'],'labels_sha256':sha(folder/f'{i:03d}.png'),'part_sha256':{role:sha(output/role/f'{i:03d}.png')for role in parts},'recomposition_mismatch_pixels':0})
    for role,sheet in sheets.items():sheet.save(output/(role+'-sheet.png'))
    verify_inputs(pinned)
    result={'status':'MANUAL_HEAD_BOUNDARY_VISIBLE_PART_REVIEW','canvas':list(size),'frames':records,
            'input_hashes':pinned,'head_boundaries':'explicit same-frame masks and polygons; annotation mode is recorded',
            'source_pixels_changed':False,'hidden_surfaces_authored':False,'weapon_and_hand_boundary_review_required':True,
            'runtime_admitted':False}
    (output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['masters','previous','annotations','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();r=apply(a.masters,a.previous,a.annotations,a.output);print(json.dumps({'frames':len(r['frames']),'recomposition_mismatches':0}))
