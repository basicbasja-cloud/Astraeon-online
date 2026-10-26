"""Replace three inaccurate shoe poses with complete guide-painted foot parts.

Only the selected boot's lower shoe is removed. A fixed ankle underlap joins
the new shoe to the existing shaft; other visible body pixels stay unchanged.
"""
import argparse
import json
from pathlib import Path
import shutil
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial.transform import Rotation
from build_occluded_underlays import sha,composite
from native_bone_plane import bone_plane_matrix,proper_rotation
from render_segmented_mage_action import segment_matrix
from render_articulated_native_action import paint_affine


def transport_shoe(image,source,target,camera):
    camera_z=Rotation.from_euler('xyz',camera['rotation']).as_matrix()[:,2]
    a=proper_rotation(source['world_matrices']['Foot.R']).T@camera_z;b=proper_rotation(target['world_matrices']['Foot.R']).T@camera_z
    angle=float(np.degrees(np.arccos(np.clip(a@b,-1,1))))
    if angle>30:raise ValueError('Shoe template requires a closer anatomical view')
    matrix=bone_plane_matrix(source['world_matrices']['Foot.R'],target['world_matrices']['Foot.R'],camera,source['landmarks']['Foot.R'],target['landmarks']['Foot.R'])
    predicted=matrix@np.array([*source['landmarks']['Toe.R'],1]);correction=segment_matrix([target['landmarks']['Foot.R'],predicted],[target['landmarks']['Foot.R'],target['landmarks']['Toe.R']]);combined=(np.vstack([correction,[0,0,1]])@np.vstack([matrix,[0,0,1]]))[:2]
    return paint_affine(image,combined),{'source_pose_index':source['index'],'native_view_difference_degrees':angle,'native_joint_transform':combined.tolist()}


def complete_background_shoe(body,new_boot,shin,ankle):
    pixels=np.array(new_boot.convert('RGBA'));yy,xx=np.indices(pixels.shape[:2]);axis=np.asarray(ankle)-np.asarray(shin);axis/=np.linalg.norm(axis);along=(np.stack([xx,yy],axis=-1)-ankle)@axis;pixels[:,:,3]=np.rint(pixels[:,:,3]*np.clip((along+25)/6,0,1)).astype(np.uint8);pixels[pixels[:,:,3]==0]=0
    result=composite([Image.fromarray(pixels),body]);original=np.array(body);actual=np.array(result)
    if np.any(actual[original[:,:,3]==255]!=original[original[:,:,3]==255]):raise ValueError('Background shoe changed opaque existing body pixels')
    return result,{'mode':'complete_missing_background_shoe','opaque_existing_body_pixels_changed':0}


def shoe_patch(body,old_boot,new_boot,shin,ankle,front):
    original=np.array(body.convert('RGBA'));alpha=np.array(old_boot.convert('RGBA'))[:,:,3]
    labels,_=ndimage.label(alpha>64,structure=np.ones((3,3)));counts=np.bincount(labels.ravel());counts[0]=0
    if not counts.any():raise ValueError('Missing observed original boot')
    selected=labels==int(counts.argmax());selected=ndimage.binary_dilation(selected,iterations=2)&(original[:,:,3]>0)
    yy,xx=np.indices(alpha.shape);points=np.stack([xx,yy],axis=-1);ankle=np.asarray(ankle);axis=ankle-np.asarray(shin);axis/=np.linalg.norm(axis);along=(points-ankle)@axis
    removed=selected&(along>=-15);remaining=original.copy();remaining[removed]=0
    patch=np.array(new_boot.convert('RGBA'));weight=np.clip((along+25)/6,0,1);patch[:,:,3]=np.rint(patch[:,:,3]*weight).astype(np.uint8);patch[patch[:,:,3]==0]=0
    patch_image=Image.fromarray(patch);remaining_image=Image.fromarray(remaining)
    result=composite([remaining_image,patch_image]if front else[patch_image,remaining_image]);changed=np.any(np.array(result)!=original,axis=2)&((original[:,:,3]>0)|(np.array(result)[:,:,3]>0));allowed=removed|(patch[:,:,3]>0)
    if np.any(changed&~allowed):raise ValueError('Shoe patch changed unrelated visible body pixels')
    return result,{'removed_original_shoe_pixels':int(removed.sum()),'new_shoe_pixels':int((patch[:,:,3]>0).sum()),'visible_changes_outside_patch':0,'foreground_shoe':bool(front)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['source','guide','controls','masks','templates','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--template-pose-map',type=Path)
    p.add_argument('--background-completion-indices',type=int,nargs='*',default=[])
    a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a fresh foot-corrected action')
    implementation=sha(__file__);source=json.loads((a.source/'receipt.json').read_text());guide=json.loads((a.guide/'pilot-receipt.json').read_text());controls=json.loads(a.controls.read_text());masks=json.loads((a.masks/'receipt.json').read_text());selected={r['index']:r for r in masks['frames']};view=guide['views']['NE'];camera_z=Rotation.from_euler('xyz',view['camera']['rotation']).as_matrix()[:,2]
    frozen={str(f):sha(f)for f in [a.source/'receipt.json',a.guide/'pilot-receipt.json',a.controls,a.masks/'receipt.json']};a.output.mkdir(parents=True);rows=[];previews=[]
    pose_map=json.loads(a.template_pose_map.read_text())if a.template_pose_map else{}
    if a.template_pose_map:frozen[str(a.template_pose_map)]=sha(a.template_pose_map)
    for row,native,numeric in zip(source['frames'],view['frames'],controls['views']['NE']['frames'],strict=True):
        i=row['index'];parts={};patch_report=None
        if i!=native['index']or i!=numeric['index']:raise ValueError('Native shoe pose indices differ')
        for role in source['render_order']:
            file=a.source/role/f'{i:03}.png'
            if sha(file)!=row['sha256'][role]:raise ValueError('Original native sprite role changed')
            frozen[str(file)]=sha(file);parts[role]=Image.open(file).convert('RGBA')
        if i in selected or i in a.background_completion_indices:
            template_index=int(pose_map.get(str(i),i));new=a.templates/f'{template_index:03}.png';frozen[str(new)]=sha(new)
            new_shoe,transport=transport_shoe(Image.open(new).convert('RGBA'),controls['views']['NE']['frames'][template_index],numeric,view['camera'])
            for name in ['Foot.R','Foot.L','Shin.R']:
                if not np.allclose(native['landmarks'][name],numeric['landmarks'][name],atol=1e-5):raise ValueError('Shoe depth controls differ from image guide')
            depth={s:float(camera_z@np.array(numeric['world_matrices']['Foot.'+s])[:3,3])for s in ['L','R']}
            if i in selected:
                old=a.masks/'BootR'/f'{i:03}.png'
                if sha(old)!=selected[i]['sha256']['BootR']:raise ValueError('Reviewed boot ownership changed')
                frozen[str(old)]=sha(old);parts['BodyCostume'],patch_report=shoe_patch(parts['BodyCostume'],Image.open(old),new_shoe,native['landmarks']['Shin.R'],native['landmarks']['Foot.R'],depth['R']>depth['L'])
            else:parts['BodyCostume'],patch_report=complete_background_shoe(parts['BodyCostume'],new_shoe,native['landmarks']['Shin.R'],native['landmarks']['Foot.R'])
            patch_report['template_transport']=transport
        master=composite([parts[n]for n in source['render_order']]);hashes={}
        for role,image in {**parts,'Master':master}.items():
            folder=a.output/role;folder.mkdir(exist_ok=True);file=folder/f'{i:03}.png';image.save(file);hashes[role]=sha(file)
        distance=ndimage.distance_transform_edt(np.array(parts['BodyCostume'])[:,:,3]<64);coverage={k:float(distance[int(round(native['landmarks'][k][1])),int(round(native['landmarks'][k][0]))])for k in ['Foot.L','Toe.L','Foot.R','Toe.R']}
        rows.append({**row,'sha256':hashes,'shoe_patch':patch_report,'native_foot_to_body_alpha_distance_px':coverage})
        bg=Image.new('RGBA',master.size,'#aaa');bg.alpha_composite(master);previews.append(bg.resize((768,768),Image.Resampling.LANCZOS).convert('RGB'))
    previews[0].save(a.output/'native-painted-walk.gif',save_all=True,append_images=previews[1:],duration=80,loop=0)
    if sha(__file__)!=implementation or any(sha(Path(k))!=v for k,v in frozen.items()):raise ValueError('Shoe patch inputs or implementation changed')
    result={**source,'frames':rows,'source_receipt_sha256':sha(a.source/'receipt.json'),'input_sha256':frozen,'implementation_sha256':implementation,'replaced_shoe_poses':sorted(selected),'background_shoe_completion_poses':a.background_completion_indices,'body_pose_generated_again':False,'runtime_admitted':False};(a.output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');replay=a.output/'replay';replay.mkdir()
    for name in ['replace_native_shoe_patches.py','build_occluded_underlays.py','native_bone_plane.py','render_segmented_mage_action.py','render_articulated_native_action.py','derive_bounded_hold_parts.py']:shutil.copyfile(Path(__file__).with_name(name),replay/name)
    print(json.dumps({'frames':len(rows),'replaced_shoe_poses':sorted(selected),'maximum_native_foot_to_painted_body_distance_px':max(v for r in rows for v in r['native_foot_to_body_alpha_distance_px'].values()),'runtime_admitted':False}))


if __name__=='__main__':main()
