"""Combine complete leg artwork with a source-preserving torso cutout.

Static calibration and recorded semantic masks precede animation. Existing
native head, arms and weapon are reused without repainting.
"""
import argparse
import json
from pathlib import Path
import shutil
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
from build_independent_mage_kit import place,clean_single_part
from build_occluded_underlays import composite,sha,solidify_interior


def split_leg(image,side,points,underlap):
    values=np.array(image);yy,xx=np.indices(values.shape[:2]);pixels=np.stack([xx,yy],axis=-1)
    knee=np.asarray(points['Shin.'+side]);ankle=np.asarray(points['Foot.'+side]);axis=(ankle-knee)/np.linalg.norm(ankle-knee)
    visible=values[:,:,3]>0;foot=visible&((pixels-ankle)@axis>-10);shin=visible&~foot&((pixels-knee)@axis>=0);thigh=visible&~foot&~shin
    parts={}
    for name,mask in [('Thigh',thigh),('Shin',shin),('Foot',foot)]:
        mask|=ndimage.binary_dilation(mask,iterations=underlap)&(values[:,:,3]==255)
        out=np.zeros_like(values);out[mask]=values[mask];parts[name+side]=Image.fromarray(out)
    if composite(list(parts.values())).tobytes()!=image.tobytes():raise ValueError('Leg split changed painted RGBA')
    return parts


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['source-kit','torso-proposal','legs','controls','recipe','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a fresh articulated leg kit')
    old=json.loads((a.source_kit/'kit.json').read_text());r=json.loads(a.recipe.read_text());controls=json.loads(a.controls.read_text());points=controls['views'][old['direction']]['frames'][0]['landmarks']
    paths=[a.recipe,a.controls,a.legs,a.source_kit/'kit.json',a.torso_proposal/'receipt.json',a.torso_proposal/'mask.png',*[a.source_kit/name/'000.png'for name in old['parts_sha256']]]
    frozen={str(f):sha(f)for f in paths};parts={}
    for name,digest in old['parts_sha256'].items():
        file=a.source_kit/name/'000.png'
        if sha(file)!=digest:raise ValueError('Base painted primitive changed')
        parts[name]=Image.open(file).convert('RGBA')
    values=np.array(parts['Torso']);yy,xx=np.indices(values.shape[:2]);mask=np.array(Image.open(a.torso_proposal/'mask.png'))>0
    mask=ndimage.binary_fill_holes(mask);mask=ndimage.binary_dilation(mask,iterations=r['hem_underlap_px'])|(yy<r['preserve_upper_torso_before_y'])
    for poly in r.get('preserved_garment_polygons',[]):
        canvas=Image.new('1',parts['Torso'].size);ImageDraw.Draw(canvas).polygon([tuple(point)for point in poly],fill=1);mask|=np.array(canvas)
    values[~mask]=0;parts['Torso'],torso_cleanup=clean_single_part(Image.fromarray(values))
    legs=Image.open(a.legs).convert('RGBA');raw=np.array(legs)
    for side,left in [('L',True),('R',False)]:
        selected=raw.copy()
        if left:selected[:,r['raw_leg_split_x']:]=0
        else:selected[:,:r['raw_leg_split_x']]=0
        image=place(Image.fromarray(selected),r['scale'],r['offset']);image,_=solidify_interior(image);image,_=clean_single_part(image)
        parts.update(split_leg(image,side,points,r['joint_underlap_px']))
    order=[*['Thigh'+s for s in ['R','L']],*['Shin'+s for s in ['R','L']],*['Foot'+s for s in ['R','L']],*old['render_order']]
    if len(order)!=len(set(order))or set(order)!=set(parts):raise ValueError('Native locomotion layer order differs')
    if any(sha(Path(k))!=v for k,v in frozen.items()):raise ValueError('Locomotion kit source changed')
    a.output.mkdir(parents=True);hashes={}
    for name,image in parts.items():
        folder=a.output/name;folder.mkdir();file=folder/'000.png';image.save(file);hashes[name]=sha(file)
    composite([parts[n]for n in order]).save(a.output/'MasterRest.png')
    result={'status':'ARTICULATED_LOCOMOTION_KIT_NOT_ADMITTED','direction':old['direction'],'render_order':order,'parts_sha256':hashes,'input_sha256':frozen,'implementation_sha256':sha(__file__),'source_controls_sha256':sha(a.controls),'torso_cleanup':torso_cleanup,'per_frame_fitting':False,'runtime_admitted':False}
    (a.output/'kit.json').write_text(json.dumps(result,indent=2)+'\n');replay=a.output/'replay';replay.mkdir()
    for name in ['build_locomotion_kit.py','build_independent_mage_kit.py','build_occluded_underlays.py','derive_bounded_hold_parts.py']:shutil.copyfile(Path(__file__).with_name(name),replay/name)
    print(json.dumps({'native_parts':len(parts),'runtime_admitted':False}))


if __name__=='__main__':main()
