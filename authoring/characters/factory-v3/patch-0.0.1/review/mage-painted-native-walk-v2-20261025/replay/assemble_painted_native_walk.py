"""Combine pose-specific painted clothing with a complete rigid head and staff.

The body retains its observed packing correction. One head and one staff follow
the frozen Blender controls; no per-frame scaling or camera fitting occurs.
This is a single-view review, not a complete playable character.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
from PIL import Image
from scipy import ndimage
from build_occluded_underlays import composite,sha
from render_segmented_mage_action import rigid_head_matrix,palm_matrix,segment_matrix,remove_distant_faint_alpha
from render_articulated_native_action import paint_affine
from audit_staff_motion import project
from build_independent_mage_kit import clean_single_part


def reviewed_artifact_cleanup(image,entry):
    values=np.array(image);report=[]
    if entry:
        if hashlib.sha256(image.tobytes()).hexdigest()!=entry['source_rgba_sha256']:raise ValueError('Reviewed artifact image changed')
        labels,_=ndimage.label(values[:,:,3]>64,structure=np.ones((3,3)));counts=np.bincount(labels.ravel());counts[0]=0;main=int(counts.argmax())
        for component in entry['components']:
            x0,y0,x1,y1=component['bbox'];options=set(np.unique(labels[y0:y1,x0:x1]))-{0,main};matches=[]
            for label in options:
                yy,xx=np.where(labels==label);bounds=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]
                if bounds==component['bbox']and int(counts[label])==component['area']:matches.append(label)
            if len(matches)!=1:raise ValueError('Reviewed foreign component differs')
            values[labels==matches[0]]=0;report.append(component)
    cleaned,small=clean_single_part(Image.fromarray(values))
    return cleaned,{'reviewed_components_removed':report,'small_detached_cleanup':small}


def shaft_socket(image,guide_grip,guide_tip):
    alpha=np.array(image)[:,:,3];samples=[]
    for y in [int(round(guide_grip[1])),int(round(guide_grip[1]-70))]:
        x0=max(0,int(guide_grip[0]-40));x1=min(image.width,int(guide_grip[0]+40));line=alpha[y,x0:x1].astype(float);line[line<64]=0
        if line.sum()==0:raise ValueError('Complete staff has no observed shaft at its native socket')
        samples.append(np.array([float(np.dot(np.arange(x0,x1),line)/line.sum()),float(y)]))
    axis=samples[1]-samples[0];axis/=np.linalg.norm(axis)
    return [samples[0],samples[0]+axis*np.linalg.norm(guide_tip-guide_grip)]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['cutouts','guide','head','weapon','weapon-guide','recipe','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a fresh assembled native walk')
    implementation=sha(__file__);capture=json.loads((a.guide/'pilot-receipt.json').read_text());weapon_capture=json.loads((a.weapon_guide/'pilot-receipt.json').read_text());cutouts=json.loads((a.cutouts/'receipt.json').read_text());recipe=json.loads(a.recipe.read_text());view=capture['views']['NE'];weapon_view=weapon_capture['views']['NE'];base=view['frames'][0]
    if view['camera']!=weapon_view['camera']:raise ValueError('Staff template camera differs')
    for key in ['rig_sha256','actor_scale','leg_scale','weapon']:
        if capture[key]!=weapon_capture[key]:raise ValueError('Staff native authority differs: '+key)
    if len(cutouts['frames'])!=len(view['frames']):raise ValueError('Incomplete painted walk cutouts')
    head=Image.open(a.head).convert('RGBA');staff=Image.open(a.weapon).convert('RGBA');hand_file=a.cutouts/'WeaponHandOccluder/000.png';hand=Image.open(hand_file).convert('RGBA')
    if any(image.size!=(1536,1536)for image in [head,staff,hand]):raise ValueError('Native part canvas differs')
    paths=[a.recipe,a.head,a.weapon,hand_file,a.cutouts/'receipt.json',a.guide/'pilot-receipt.json',a.weapon_guide/'pilot-receipt.json'];frozen={str(f):sha(f)for f in paths}
    wb=weapon_view['frames'][0];source_staff=shaft_socket(staff,project(wb['grip_world'],weapon_view['camera']),project(wb['staff_tip_world'],weapon_view['camera']))
    scale=recipe.get('constant_painted_asset_scale',1.)
    if not .8<=scale<=1.2:raise ValueError('Static illustration calibration exceeds review bounds')
    def calibration(point):return np.column_stack([np.eye(2)*scale,np.asarray(point)*(1-scale)])
    head=paint_affine(head,calibration(base['landmarks']['Head']));hand=paint_affine(hand,calibration(project(base['grip_world'],view['camera'])))
    a.output.mkdir(parents=True);records=[];previews=[];order=['Weapon','BodyCostume','WeaponHandOccluder','HeadHair']
    for row,owned in zip(view['frames'],cutouts['frames'],strict=True):
        i=row['index']
        if i!=owned['index']:raise ValueError('Source pose indices differ')
        body_file=a.cutouts/'BodyCostume'/f'{i:03}.png';hand_source=a.cutouts/'WeaponHandOccluder'/f'{i:03}.png'
        for role,file in [('BodyCostume',body_file),('WeaponHandOccluder',hand_source)]:
            if sha(file)!=owned['sha256'][role]:raise ValueError('Painted same-frame role changed')
            frozen[str(file)]=sha(file)
        body=Image.open(body_file).convert('RGBA');restored=False
        if i in recipe['restore_collar_from_hand_role_frames']:
            body=composite([body,Image.open(hand_source).convert('RGBA')]);restored=True
        body,noise=remove_distant_faint_alpha(body)
        body,artifact_cleanup=reviewed_artifact_cleanup(body,recipe.get('reviewed_foreign_components',{}).get(str(i)))
        body=paint_affine(body,calibration(row['landmarks']['Head']))
        points=row['landmarks'];head_matrix=rigid_head_matrix([base['landmarks'][k]for k in ['Neck','Head']],[points[k]for k in ['Neck','Head']]);hand_matrix=palm_matrix([base['landmarks'][k+'.R']for k in ['Hand','Index1','Pinky1']],[points[k+'.R']for k in ['Hand','Index1','Pinky1']]);grip=project(row['grip_world'],view['camera']);tip=project(row['staff_tip_world'],view['camera']);staff_matrix=segment_matrix(source_staff,[grip,tip])
        parts={'Weapon':paint_affine(staff,staff_matrix),'BodyCostume':body,'WeaponHandOccluder':paint_affine(hand,hand_matrix),'HeadHair':paint_affine(head,head_matrix)}
        master=composite([parts[n]for n in order]);hashes={};distances={}
        gx,gy=np.rint(grip).astype(int)
        for role in ['Weapon','WeaponHandOccluder']:
            alpha=np.array(parts[role])[:,:,3];distance=ndimage.distance_transform_edt(alpha<64);distances[role]=float(distance[gy,gx])
        for name,image in {**parts,'Master':master}.items():
            folder=a.output/name;folder.mkdir(exist_ok=True);file=folder/f'{i:03}.png';image.save(file);hashes[name]=sha(file)
        records.append({'index':i,'source_action':row['source_action'],'source_frame':row['source_frame'],'sha256':hashes,'transforms':{'HeadHair':head_matrix.tolist(),'WeaponHandOccluder':hand_matrix.tolist(),'Weapon':staff_matrix.tolist()},'native_grip':grip.tolist(),'grip_to_opaque_part_distance_px':distances,'collar_role_restored':restored,'detached_faint_body_pixels_removed':noise,'body_artifact_cleanup':artifact_cleanup})
        bg=Image.new('RGBA',master.size,'#aaa');bg.alpha_composite(master);previews.append(bg.resize((768,768),Image.Resampling.LANCZOS).convert('RGB'))
    previews[0].save(a.output/'native-painted-walk.gif',save_all=True,append_images=previews[1:],duration=80,loop=0)
    if sha(__file__)!=implementation or any(sha(Path(k))!=v for k,v in frozen.items()):raise ValueError('Native assembled inputs or code changed')
    keys=['Hips','Head','Hand.L','Hand.R','Foot.L','Foot.R'];positions=np.array([[row['landmarks'][k]for k in keys]for row in view['frames']]);adjacent=np.sqrt(np.mean(np.sum(np.diff(positions,axis=0)**2,axis=2),axis=1));seam=float(np.sqrt(np.mean(np.sum((positions[-1]-positions[0])**2,axis=1))))
    report={'status':'LAYERED_NATIVE_ACTION_STUDY','direction':'NE','render_order':order,'frames':records,'replacement_head':str(a.head),'loop_evidence':{'native_joint_seam_rms_px':seam,'maximum_adjacent_native_joint_rms_px':float(adjacent.max()),'terminal_frame_cloned':False},'input_sha256':frozen,'implementation_sha256':implementation,'source_staff_socket':np.array(source_staff).tolist(),'constant_painted_asset_scale':scale,'per_frame_bbox_fitting':False,'hand_behind_head':True,'body_packing_proxy_only':True,'semantic_approval':False,'runtime_admitted':False}
    (a.output/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');replay=a.output/'replay';replay.mkdir()
    for name in ['assemble_painted_native_walk.py','build_independent_mage_kit.py','render_articulated_native_action.py','render_segmented_mage_action.py','native_bone_plane.py','derive_bounded_hold_parts.py','build_occluded_underlays.py','audit_staff_motion.py']:shutil.copyfile(Path(__file__).with_name(name),replay/name)
    print(json.dumps({'frames':len(records),'maximum_staff_grip_distance_native_px':max(r['grip_to_opaque_part_distance_px']['Weapon']for r in records),'maximum_hand_grip_distance_native_px':max(r['grip_to_opaque_part_distance_px']['WeaponHandOccluder']for r in records),'native_seam_rms_px':seam,'maximum_adjacent_native_rms_px':float(adjacent.max()),'runtime_admitted':False}))


if __name__=='__main__':main()
