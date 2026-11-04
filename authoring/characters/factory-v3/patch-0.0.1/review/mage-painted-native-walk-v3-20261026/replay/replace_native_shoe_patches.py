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
    a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a fresh foot-corrected action')
    implementation=sha(__file__);source=json.loads((a.source/'receipt.json').read_text());guide=json.loads((a.guide/'pilot-receipt.json').read_text());controls=json.loads(a.controls.read_text());masks=json.loads((a.masks/'receipt.json').read_text());selected={r['index']:r for r in masks['frames']};view=guide['views']['NE'];camera_z=Rotation.from_euler('xyz',view['camera']['rotation']).as_matrix()[:,2]
    frozen={str(f):sha(f)for f in [a.source/'receipt.json',a.guide/'pilot-receipt.json',a.controls,a.masks/'receipt.json']};a.output.mkdir(parents=True);rows=[];previews=[]
    for row,native,numeric in zip(source['frames'],view['frames'],controls['views']['NE']['frames'],strict=True):
        i=row['index'];parts={};patch_report=None
        if i!=native['index']or i!=numeric['index']:raise ValueError('Native shoe pose indices differ')
        for role in source['render_order']:
            file=a.source/role/f'{i:03}.png'
            if sha(file)!=row['sha256'][role]:raise ValueError('Original native sprite role changed')
            frozen[str(file)]=sha(file);parts[role]=Image.open(file).convert('RGBA')
        if i in selected:
            old=a.masks/'BootR'/f'{i:03}.png';new=a.templates/f'{i:03}.png'
            if sha(old)!=selected[i]['sha256']['BootR']:raise ValueError('Reviewed boot ownership changed')
            frozen[str(old)]=sha(old);frozen[str(new)]=sha(new)
            for name in ['Foot.R','Foot.L','Shin.R']:
                if not np.allclose(native['landmarks'][name],numeric['landmarks'][name],atol=1e-5):raise ValueError('Shoe depth controls differ from image guide')
            depth={s:float(camera_z@np.array(numeric['world_matrices']['Foot.'+s])[:3,3])for s in ['L','R']}
            parts['BodyCostume'],patch_report=shoe_patch(parts['BodyCostume'],Image.open(old),Image.open(new),native['landmarks']['Shin.R'],native['landmarks']['Foot.R'],depth['R']>depth['L'])
        master=composite([parts[n]for n in source['render_order']]);hashes={}
        for role,image in {**parts,'Master':master}.items():
            folder=a.output/role;folder.mkdir(exist_ok=True);file=folder/f'{i:03}.png';image.save(file);hashes[role]=sha(file)
        distance=ndimage.distance_transform_edt(np.array(parts['BodyCostume'])[:,:,3]<64);coverage={k:float(distance[int(round(native['landmarks'][k][1])),int(round(native['landmarks'][k][0]))])for k in ['Foot.L','Toe.L','Foot.R','Toe.R']}
        rows.append({**row,'sha256':hashes,'shoe_patch':patch_report,'native_foot_to_body_alpha_distance_px':coverage})
        bg=Image.new('RGBA',master.size,'#aaa');bg.alpha_composite(master);previews.append(bg.resize((768,768),Image.Resampling.LANCZOS).convert('RGB'))
    previews[0].save(a.output/'native-painted-walk.gif',save_all=True,append_images=previews[1:],duration=80,loop=0)
    if sha(__file__)!=implementation or any(sha(Path(k))!=v for k,v in frozen.items()):raise ValueError('Shoe patch inputs or implementation changed')
    result={**source,'frames':rows,'source_receipt_sha256':sha(a.source/'receipt.json'),'input_sha256':frozen,'implementation_sha256':implementation,'replaced_shoe_poses':sorted(selected),'body_pose_generated_again':False,'runtime_admitted':False};(a.output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');replay=a.output/'replay';replay.mkdir()
    for name in ['replace_native_shoe_patches.py','build_occluded_underlays.py']:shutil.copyfile(Path(__file__).with_name(name),replay/name)
    print(json.dumps({'frames':len(rows),'replaced_shoe_poses':sorted(selected),'maximum_native_foot_to_painted_body_distance_px':max(v for r in rows for v in r['native_foot_to_body_alpha_distance_px'].values()),'runtime_admitted':False}))


if __name__=='__main__':main()
