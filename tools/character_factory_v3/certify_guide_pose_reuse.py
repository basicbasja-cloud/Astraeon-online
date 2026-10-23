"""Certify exact source-render pose reuse across action timelines.

Source controls, camera, landmarks, rotations, prop coordinates and every visible
RGBA pixel must agree. This does not approve painted art or copy effect timing.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def certify(source,target,offset=None,pairs=None):
    a=json.loads((source/'manifest.json').read_text());b=json.loads((target/'manifest.json').read_text())
    for key in ['source_sha256','renderer_sha256','render_pose_freeze_sha256']:
        if a['job'].get(key)!=b['job'].get(key):raise ValueError('Different source/render implementation: '+key)
    if set(a['views'])!=set(b['views']):raise ValueError('Source views differ')
    if pairs is None:
        if type(offset)is not int or offset<0 or offset+a['frame_count']>b['frame_count']:raise ValueError('Invalid target frame offset')
        pairs=[(i,i+offset)for i in range(a['frame_count'])]
    if not pairs or any(type(i)is not int or type(j)is not int or not 0<=i<a['frame_count']or not 0<=j<b['frame_count']for i,j in pairs)or len({j for _,j in pairs})!=len(pairs):raise ValueError('Invalid or duplicate source/target frame mappings')
    rows=[]
    for direction in a['views']:
        av=a['views'][direction];bv=b['views'][direction]
        if av['camera']!=bv['camera']:raise ValueError('Camera differs')
        for i,j in pairs:
            s=av['frames'][i];t=bv['frames'][j]
            for key in ['action','source_frame','transition_from','transition_frame','transition_weight']:
                if s.get(key)!=t.get(key):raise ValueError('Source pose controls differ')
            errors=[]
            for field in ['world_landmarks','bone_rotations','weapon_guide']:
                if set(s[field])!=set(t[field]):raise ValueError('Pose fields differ')
                for key,value in s[field].items():
                    if isinstance(value,list):
                        left=np.asarray(value,dtype=float);right=np.asarray(t[field][key],dtype=float)
                        if left.shape!=right.shape or not np.isfinite(left).all()or not np.isfinite(right).all():raise ValueError('Invalid pose coordinates: '+field+'/'+key)
                        error=float(np.max(np.abs(left-right)))
                        if error>(.0002 if field=='weapon_guide'else 2e-6):raise ValueError('Pose coordinates differ: '+field+'/'+key)
                        errors.append(error)
                    elif value!=t[field][key]:raise ValueError('Prop state differs')
            sp=source/direction/f'{i:03d}.png';tp=target/direction/f'{j:03d}.png'
            x=np.array(Image.open(sp).convert('RGBA'));y=np.array(Image.open(tp).convert('RGBA'))
            if x.shape!=y.shape:raise ValueError('Source canvas differs')
            visible=(x[:,:,3]>0)|(y[:,:,3]>0)
            changed=int((np.any(x!=y,axis=2)&visible).sum())
            if changed:raise ValueError(f'Source render differs: {direction}/{i} -> {j}: {changed} visible pixels')
            rows.append({'direction':direction,'source_index':i,'target_index':j,
                         'source_action':s['action'],'source_frame':s['source_frame'],
                         'source_png_sha256':sha(sp),'target_png_sha256':sha(tp),'visible_pixel_changes':0,
                         'max_recorded_coordinate_component_error':max(errors,default=0)})
    return {'status':'EXACT_SOURCE_RENDER_POSE_REUSE_CERTIFIED','source_guide_job':a['job']['id'],
            'target_guide_job':b['job']['id'],'source_manifest_sha256':sha(source/'manifest.json'),
            'target_manifest_sha256':sha(target/'manifest.json'),'mappings':rows,
            'eligible_art_roles':['BodyCostume','HeadHair','Weapon','WeaponHandOccluder','BackAccessory','Headgear'],
            'painted_art_imported':False,'same_character_and_fit_required':True,
            'target_action_timings_and_events_must_remain_explicit':True,'effect_timing_copied':False,
            'owner_approved':False,'runtime_admitted':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True)
    p.add_argument('--target',type=Path,required=True);mapping=p.add_mutually_exclusive_group(required=True)
    mapping.add_argument('--offset',type=int);mapping.add_argument('--pair',nargs=2,type=int,action='append')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=certify(a.source,a.target,a.offset,a.pair)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'status':r['status'],'certified_mappings':len(r['mappings'])}))
