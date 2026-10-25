"""Correct visible ownership and add authored pixels behind opaque foreground.

Ownership transfer preserves RGBA; explicit near-opaque alpha repair changes
only alpha by at most five levels. Hidden additions then preserve that master.
This does not approve a hairstyle,
weapon family or costume swap: those must be inspected independently.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage

ROLES = ['BodyCostume','HeadHair','Weapon','WeaponHandOccluder']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def composite(parts):
    result=Image.new('RGBA',parts[0].size)
    for part in parts: result.alpha_composite(part)
    return result


def solidify_interior(image):
    values=np.array(image.convert('RGBA'))
    mask=values[:,:,3]>=250
    values[mask,3]=255
    return Image.fromarray(values),int(mask.sum())


def transfer_visible_pixels(parts,source_role,target_role,mask):
    source=np.array(parts[source_role]);target=np.array(parts[target_role])
    selected=mask & (source[:,:,3]>0)
    if np.any(selected & (target[:,:,3]>0)):
        raise ValueError('Ownership correction cannot overwrite another layer')
    target[selected]=source[selected];source[selected]=0
    parts[source_role]=Image.fromarray(source);parts[target_role]=Image.fromarray(target)
    return int(selected.sum())


def add_hidden(destination, donor, foreground, region):
    base=np.array(destination.convert('RGBA'));paint=np.array(donor.convert('RGBA'))
    cover=np.array(foreground.convert('RGBA'))[:,:,3]
    if base.shape!=paint.shape or region.shape!=base.shape[:2] or cover.shape!=region.shape:
        raise ValueError('Hidden underlays require matching canvases')
    # Exact opacity is required: fractional foreground would reveal additions.
    mask=region & (cover==255) & (base[:,:,3]==0) & (paint[:,:,3]>0)
    base[mask]=paint[mask]
    return Image.fromarray(base),int(mask.sum())


def shaft_donor(weapon, center, half_width, top, bottom):
    values=np.array(weapon.convert('RGBA'))
    height,width=values.shape[:2]
    if not all(isinstance(v,int) for v in [center,half_width,top,bottom]) or not 0<=top<bottom<=height or not 0<half_width<width//8 or not half_width<=center<width-half_width:
        raise ValueError('Invalid authored hidden shaft corridor')
    yy,xx=np.indices(values.shape[:2])
    corridor=(abs(xx-center)<=half_width)&(yy>=top)&(yy<bottom)
    opaque=corridor&(values[:,:,3]==255)
    if not opaque.any():raise ValueError('No opaque painted shaft texture in corridor')
    _,indices=ndimage.distance_transform_edt(~opaque,return_indices=True)
    donor=np.zeros_like(values)
    donor[corridor]=values[indices[0][corridor],indices[1][corridor]]
    return Image.fromarray(donor),corridor


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['parts','body-donor','recipe','output']:
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Choose a fresh underlay output')
    recipe=json.loads(args.recipe.read_text())
    if recipe['direction']!='NE' or recipe['index']!=0:raise ValueError('This authored recipe is NE template zero only')
    source={role:args.parts/role/'000.png' for role in ROLES}
    raw_parts=[Image.open(source[r]).convert('RGBA') for r in ROLES]
    original_raw=composite(raw_parts)
    owned=dict(zip(ROLES,raw_parts))
    yy,xx=np.indices((original_raw.height,original_raw.width))
    body=np.array(owned['BodyCostume']);rgb=body[:,:,:3].astype(float)
    head_region=Image.new('1',original_raw.size)
    ImageDraw.Draw(head_region).polygon(recipe['hair_ownership_polygon'],fill=1)
    auburn=(rgb[:,:,0]>rgb[:,:,1]+10)&((rgb[:,:,0]-rgb[:,:,1])>1.6*np.maximum(rgb[:,:,1]-rgb[:,:,2],1))
    hair_count=transfer_visible_pixels(owned,'BodyCostume','HeadHair',np.array(head_region)&((body[:,:,3]<64)|auburn))
    body=np.array(owned['BodyCostume'])
    shaft_recipe=recipe['shaft_corridor']
    pole_region=(abs(xx-shaft_recipe['center'])<=shaft_recipe['half_width']+3)&(yy>=recipe['staff_ownership_top'])&(yy<recipe['staff_ownership_bottom'])
    pole_count=transfer_visible_pixels(owned,'BodyCostume','Weapon',pole_region&(body[:,:,3]<64))
    returned_weapon=0
    for x0,y0,x1,y1 in recipe.get('weapon_residue_regions',[]):
        region=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
        returned_weapon+=transfer_visible_pixels(owned,'Weapon','BodyCostume',region)
    raw_parts=[owned[r]for r in ROLES]
    if composite(raw_parts).tobytes()!=original_raw.tobytes():raise ValueError('Ownership correction changed master pixels')
    normalized=[solidify_interior(p) for p in raw_parts]
    parts=[row[0] for row in normalized]
    original=composite(parts)
    donor=Image.open(args.body_donor).convert('RGBA')
    if donor.size!=original.size:raise ValueError('Calibrated donor canvas differs')
    yy,xx=np.indices((original.height,original.width))
    x0,y0,x1,y1=recipe['body_hidden_region']
    region=(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
    parts[0],body_count=add_hidden(parts[0],donor,parts[1],region)
    shaft,region=shaft_donor(parts[2],**recipe['shaft_corridor'])
    # The pole passes behind the sleeve/body as well as the gripping hand.
    # Keep hidden and visible weapon passes separate instead of drawing the
    # reconstructed pole over the original sleeve.
    foreground=composite([parts[0],parts[1],parts[3]])
    region &= np.array(parts[2])[:,:,3]==0
    back,shaft_count=add_hidden(Image.new('RGBA',original.size),shaft,foreground,region)
    if composite([back,*parts]).tobytes()!=original.tobytes():raise ValueError('Underlay changed visible master pixels')
    args.output.mkdir(parents=True)
    for role,image in zip(ROLES,parts):
        folder=args.output/role;folder.mkdir();image.save(folder/'000.png')
    (args.output/'WeaponBack').mkdir()
    back.save(args.output/'WeaponBack'/'000.png')
    composite([back,parts[2]]).save(args.output/'WeaponComplete-reference.png')
    original.save(args.output/'Master.png')
    shutil.copyfile(__file__,args.output/'renderer-source.py')
    inputs=[*source.values(),args.body_donor,args.recipe]
    receipt={'status':'OPAQUE_OCCLUDED_UNDERLAY_STUDY','direction':'NE','index':0,
             'input_sha256':{str(p):sha(p) for p in inputs},'implementation_sha256':sha(__file__),
             'added_body_pixels':body_count,'added_shaft_pixels':shaft_count,
             'hair_pixels_returned_from_body':hair_count,'staff_edge_pixels_returned_from_body':pole_count,
             'cloth_pixels_returned_from_weapon':returned_weapon,
             'render_order':['WeaponBack',*ROLES],
             'interior_alpha_250_plus_to_255_pixels':sum(row[1] for row in normalized),
             'normalization_rgb_changed_pixels':int(np.any(np.array(original_raw)[:,:,:3]!=np.array(original)[:,:,:3],axis=2).sum()),
             'maximum_normalization_alpha_change':int(np.abs(np.array(original_raw)[:,:,3].astype(int)-np.array(original)[:,:,3].astype(int)).max()),
             'visible_composition_changed_pixels':0,'whole_hidden_surface_complete':False,
             'swaps_approved':False,'runtime_admitted':False,
             'output_sha256':{r:sha(args.output/r/'000.png')for r in ROLES}}
    (args.output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k]for k in ['added_body_pixels','added_shaft_pixels','visible_composition_changed_pixels']}))


if __name__=='__main__':main()
