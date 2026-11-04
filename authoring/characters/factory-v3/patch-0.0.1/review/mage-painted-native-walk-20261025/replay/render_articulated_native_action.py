"""Render a fixed-camera 15-part painted kit from canonical numeric poses.

Feet use full Blender bone rotations, avoiding unstable near-zero toe vectors.
This is an action study; no absent character actions or views are substituted.
"""
import argparse
import json
from pathlib import Path
import shutil
import numpy as np
from PIL import Image
from build_occluded_underlays import composite,sha
from native_bone_plane import bone_plane_matrix
from render_segmented_mage_action import segment_matrix,palm_matrix,rigid_head_matrix
from audit_staff_motion import project
from scipy import ndimage
import derive_bounded_hold_parts as motion


def paint_affine(image,matrix):
    inverse=np.linalg.inv(np.vstack([matrix,[0,0,1]]))[:2].ravel()
    return image.convert('RGBa').transform(image.size,Image.Transform.AFFINE,tuple(inverse),resample=Image.Resampling.BICUBIC).convert('RGBA')


def torso_joint_transport(image,matrix,source_points,target_points):
    """Keep the chest plane, then align its shoulder/hip seams to native joints."""
    keys=['UpperArm.L','UpperArm.R','Chest','Hips','Neck']
    start=np.array([matrix@np.array([*source_points[k],1])for k in keys])
    end=np.array([target_points[k]for k in keys])
    boundary=np.array([[0,0],[768,0],[1536,0],[0,768],[1536,768],[0,1536],[768,1536],[1536,1536]])
    field,metrics,_=motion.inverse_field(np.vstack([start,boundary]),np.vstack([end,boundary]))
    if metrics['maximum_inverse_displacement_px']>64 or metrics['minimum_jacobian']<.65 or metrics['maximum_jacobian']>1.5:
        raise ValueError('Torso joint correction exceeds bounded native transport')
    yy,xx=np.mgrid[:1536,:1536].astype(np.float32)
    dx,dy=[ndimage.map_coordinates(field[:,:,i],[(yy+.5)/motion.SPACING,(xx+.5)/motion.SPACING],order=1,prefilter=False)for i in range(2)]
    inverse=np.linalg.inv(np.vstack([matrix,[0,0,1]]))
    sx=inverse[0,0]*(xx+dx)+inverse[0,1]*(yy+dy)+inverse[0,2]
    sy=inverse[1,0]*(xx+dx)+inverse[1,1]*(yy+dy)+inverse[1,2]
    return motion.resample_rgba(image,sy,sx),metrics


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['kit','base-controls','target-controls','output']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a fresh native articulated study')
    implementation=sha(__file__)
    kit=json.loads((a.kit/'kit.json').read_text());base=json.loads(a.base_controls.read_text());target=json.loads(a.target_controls.read_text())
    if any(c.get('status')!='NUMERIC_CANONICAL_POSES_NOT_IMAGE_CAPTURE'or c.get('image_captures')!=0 for c in [base,target]):raise ValueError('Canonical numeric controls required')
    if kit['status']!='ARTICULATED_LOCOMOTION_KIT_NOT_ADMITTED'or kit['source_controls_sha256']!=sha(a.base_controls):raise ValueError('Native source kit controls differ')
    for key in ['rig_sha256','actor_scale','leg_scale','weapon','canonical_implementation_sha256']:
        if base[key]!=target[key]:raise ValueError('Canonical pose authority differs: '+key)
    direction=kit['direction'];source_view=base['views'][direction];target_view=target['views'][direction]
    if source_view['camera']!=target_view['camera']:raise ValueError('Fixed native camera changed')
    camera=source_view['camera'];rest=source_view['frames'][0];points=rest['landmarks'];parts={};paths=[a.kit/'kit.json',a.base_controls,a.target_controls]
    for name,digest in kit['parts_sha256'].items():
        path=a.kit/name/'000.png'
        if sha(path)!=digest:raise ValueError('Painted source part changed')
        parts[name]=Image.open(path).convert('RGBA');paths.append(path)
    frozen={str(f):sha(f)for f in paths};a.output.mkdir(parents=True);rows=[];previews=[]
    for row in target_view['frames']:
        i=row['index'];q=row['landmarks'];matrices={}
        matrices['Torso']=bone_plane_matrix(rest['world_matrices']['Chest'],row['world_matrices']['Chest'],camera,points['Chest'],q['Chest'])
        matrices['HeadHair']=rigid_head_matrix([points[k]for k in ['Neck','Head']],[q[k]for k in ['Neck','Head']])
        for side in ['L','R']:
            for name,joints in [('UpperArm',['UpperArm','Forearm']),('Forearm',['Forearm','Hand']),('Hand',['Hand','Index1','Pinky1']),('Thigh',['Thigh','Shin']),('Shin',['Shin','Foot'])]:
                start=[points[k+'.'+side]for k in joints];end=[q[k+'.'+side]for k in joints]
                matrices[name+side]=palm_matrix(start,end)if name=='Hand'else segment_matrix(start,end)
            bone='Foot.'+side;matrices['Foot'+side]=bone_plane_matrix(rest['world_matrices'][bone],row['world_matrices'][bone],camera,points[bone],q[bone])
        matrices['Weapon']=segment_matrix([project(rest[k],camera)for k in ['grip_world','staff_tip_world']],[project(row[k],camera)for k in ['grip_world','staff_tip_world']])
        derived={name:paint_affine(image,matrices[name])for name,image in parts.items()if name!='Torso'}
        derived['Torso'],torso_metrics=torso_joint_transport(parts['Torso'],matrices['Torso'],points,q)
        derived['Master']=composite([derived[n]for n in kit['render_order']]);hashes={}
        for name,image in derived.items():
            folder=a.output/name;folder.mkdir(exist_ok=True);path=folder/f'{i:03}.png';image.save(path);hashes[name]=sha(path)
        rows.append({'index':i,'source_action':row['source_action'],'source_frame':row['source_frame'],'transforms':{n:m.tolist()for n,m in matrices.items()},'torso_joint_transport':torso_metrics,'sha256':hashes})
        image=derived['Master'];bg=Image.new('RGBA',image.size,'#aaa');bg.alpha_composite(image);previews.append(bg.resize((768,768),Image.Resampling.LANCZOS).convert('RGB'))
        print('ARTICULATED_NATIVE_POSE',i,flush=True)
    previews[0].save(a.output/'native-action.gif',save_all=True,append_images=previews[1:],duration=80,loop=0)
    if sha(__file__)!=implementation or any(sha(Path(k))!=v for k,v in frozen.items()):raise ValueError('Native action code or inputs changed')
    result={'status':'ARTICULATED_NATIVE_ACTION_STUDY_NOT_ADMITTED','direction':direction,'render_order':kit['render_order'],'frames':rows,'input_sha256':frozen,'implementation_sha256':implementation,'foot_transport':'canonical-world-rotation-projected-to-fixed-camera','head_transport':'rigid-neck-axis','per_frame_generation':False,'camera_changed':False,'image_guide_captures_created':0,'runtime_admitted':False}
    (a.output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');replay=a.output/'replay';replay.mkdir()
    for name in ['render_articulated_native_action.py','native_bone_plane.py','render_segmented_mage_action.py','derive_bounded_hold_parts.py','build_occluded_underlays.py','audit_staff_motion.py']:shutil.copyfile(Path(__file__).with_name(name),replay/name)


if __name__=='__main__':main()
