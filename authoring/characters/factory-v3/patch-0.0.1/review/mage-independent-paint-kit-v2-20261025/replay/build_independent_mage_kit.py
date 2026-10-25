"""Build a reusable rest-pose kit from separately painted complete body/arms.

Static asset placement precedes animation. Native cameras, source motion and
protected Swordsman art are untouched. No per-frame image generation or fitting.
"""
import argparse
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image
from scipy import ndimage

import derive_bounded_hold_parts as motion
from build_occluded_underlays import composite,sha,solidify_interior


def clean_single_part(image):
    pixels=np.array(image.convert('RGBA'));alpha=pixels[:,:,3]
    labels,_=ndimage.label(alpha>64,structure=np.ones((3,3)))
    counts=np.bincount(labels.ravel());counts[0]=0
    if not counts.any():raise ValueError('A complete painted part is required')
    main=labels==int(counts.argmax());distance=ndimage.distance_transform_edt(~main)
    removed=(alpha>0)&(distance>3)
    secondary=[int(c)for i,c in enumerate(counts)if i and i!=counts.argmax()]
    if max(secondary,default=0)>128:raise ValueError('Large detached component requires semantic review')
    report={'removed_pixels':int(removed.sum()),'maximum_removed_alpha':int(alpha[removed].max())if removed.any()else 0}
    pixels[removed]=0
    return Image.fromarray(pixels),report


def place(image,scale,offset):
    if len(scale)!=2 or len(offset)!=2 or not np.isfinite([*scale,*offset]).all()or min(scale)<=0:
        raise ValueError('Finite positive static asset scale required')
    yy,xx=np.mgrid[:motion.SIZE,:motion.SIZE].astype(np.float32)
    return motion.resample_rgba(image,(yy+.5-offset[1])/scale[1]-.5,(xx+.5-offset[0])/scale[0]-.5)


def fill_hidden_clothing(body,donor,occluder,region):
    """Restore only missing cloth under the recorded original weapon footprint."""
    values=np.array(body.convert('RGBA'));paint=np.array(donor.convert('RGBA'))
    if body.size!=donor.size or body.size!=occluder.size:raise ValueError('Underpaint canvases differ')
    x0,y0,x1,y1=region
    if not(0<=x0<x1<=body.width and 0<=y0<y1<=body.height):raise ValueError('Invalid underpaint region')
    allowed=np.zeros(values.shape[:2],bool);allowed[y0:y1,x0:x1]=True
    selected=allowed&(values[:,:,3]==0)&(np.array(occluder.convert('RGBA'))[:,:,3]>0)&(paint[:,:,3]>=250)
    values[selected]=paint[selected]
    return Image.fromarray(values),int(selected.sum())


def split_arm(image,side,points,underlap):
    values=np.array(image);yy,xx=np.indices(values.shape[:2]);pixels=np.stack([xx,yy],axis=-1)
    shoulder,elbow,wrist=[np.asarray(points[k+'.'+side])for k in ['UpperArm','Forearm','Hand']]
    mask=values[:,:,3]>0
    axis=(wrist-elbow)/np.linalg.norm(wrist-elbow)
    hand=mask&(((pixels-wrist)@axis)>-4)
    axis=(elbow-shoulder)/np.linalg.norm(elbow-shoulder)
    fore=mask&~hand&(((pixels-elbow)@axis)>0)
    upper=mask&~hand&~fore
    parts={}
    for name,selected in [('UpperArm',upper),('Forearm',fore),('Hand',hand)]:
        selected|=ndimage.binary_dilation(selected,iterations=underlap)&(values[:,:,3]==255)
        result=np.zeros_like(values);result[selected]=values[selected]
        parts[name+side]=Image.fromarray(result)
    if composite(list(parts.values())).tobytes()!=image.tobytes():raise ValueError('Arm split changed source RGBA')
    return parts


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['recipe','guide','output']:
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Choose a fresh independent part kit')
    recipe=json.loads(args.recipe.read_text());guide=json.loads((args.guide/'pilot-receipt.json').read_text())
    direction=recipe['direction'];row=guide['views'][direction]['frames'][0]
    if recipe['source_pose_index']!=0:raise ValueError('This kit binds source rest pose zero')
    inputs=[args.recipe,args.guide/'pilot-receipt.json',*[Path(p['image'])for p in recipe['parts'].values()]]
    repair=recipe.get('hidden_clothing')
    if repair:inputs += [Path(repair[k])for k in ['donor','original_weapon']]
    frozen={str(p):sha(p)for p in inputs};images={};normalization={}
    for name,entry in recipe['parts'].items():
        image=place(Image.open(entry['image']).convert('RGBA'),entry['scale'],entry['offset'])
        image,count=solidify_interior(image)
        images[name]=image;normalization[name]={'interior_alpha_repair_pixels':count}
    upper=np.array(images['UpperTorso']);upper[recipe['upper_torso_end_y']:]=0
    lower=np.array(images['LowerBody']);lower[:recipe['lower_body_start_y']]=0
    torso=composite([Image.fromarray(upper),Image.fromarray(lower)])
    control=recipe['torso_static_registration'];source=np.array(control['source_controls'],float);target=np.array(control['native_controls'],float)
    field,metrics,_=motion.inverse_field(source,target)
    if metrics['maximum_inverse_displacement_px']>32 or metrics['minimum_jacobian']<.75 or metrics['maximum_jacobian']>1.35:
        raise ValueError('Static torso registration exceeds bounded shape correction')
    yy,xx=np.mgrid[:motion.SIZE,:motion.SIZE].astype(np.float32)
    dx,dy=[ndimage.map_coordinates(field[:,:,i],[(yy+.5)/motion.SPACING,(xx+.5)/motion.SPACING],order=1)for i in range(2)]
    registered=np.array(motion.resample_rgba(torso,yy+dy,xx+dx));original=np.array(torso)
    registered[recipe['lower_body_start_y']:]=original[recipe['lower_body_start_y']:]
    images['Torso']=Image.fromarray(registered)
    source_parts={};cleanup={}
    for name in ['Torso','LeftArm','RightArm','HeadHair','Weapon']:
        images[name],cleanup[name]=clean_single_part(images[name])
    underpaint=0
    if repair:
        images['Torso'],underpaint=fill_hidden_clothing(images['Torso'],Image.open(repair['donor']),Image.open(repair['original_weapon']),repair['region'])
    source_parts['Torso']=images['Torso'];source_parts['HeadHair']=images['HeadHair'];source_parts['Weapon']=images['Weapon']
    for side,name in [('L','LeftArm'),('R','RightArm')]:source_parts.update(split_arm(images[name],side,row['landmarks'],recipe['joint_underlap_px']))
    order=recipe['render_order']
    if set(order)!=set(source_parts)or len(order)!=len(set(order)):raise ValueError('Independent source layer order differs')
    if any(sha(p)!=v for p,v in frozen.items()):raise ValueError('Independent source changed during kit construction')
    args.output.mkdir(parents=True)
    hashes={}
    for name,image in source_parts.items():
        folder=args.output/name;folder.mkdir();path=folder/'000.png';image.save(path);hashes[name]=sha(path)
    composite([source_parts[n]for n in order]).save(args.output/'MasterRest.png')
    kit={'status':'INDEPENDENT_PAINTED_ARM_KIT_NOT_ADMITTED','direction':direction,'source_pose_index':0,
         'canonical_guide_receipt_sha256':sha(args.guide/'pilot-receipt.json'),'render_order':order,'parts_sha256':hashes,
         'input_sha256':frozen,'implementation_sha256':sha(__file__),'normalization':normalization,'detached_cleanup':cleanup,
         'static_torso_registration':metrics,'lower_body_reused':True,'per_frame_fitting':False,'runtime_admitted':False}
    kit['hidden_clothing_repair']={'pixels':underpaint,'recipe':repair,'existing_body_pixels_changed':0}
    (args.output/'kit.json').write_text(json.dumps(kit,indent=2)+'\n')
    replay=args.output/'replay';replay.mkdir()
    for name in ['build_independent_mage_kit.py','derive_bounded_hold_parts.py','build_occluded_underlays.py']:
        shutil.copyfile(Path(__file__).with_name(name),replay/name)
    print(json.dumps({'source_parts':len(source_parts),'static_torso_registration':metrics,'runtime_admitted':False}))


if __name__=='__main__':main()
