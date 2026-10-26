"""Inventory user-supplied CC0 ActionForge animation data, never app code."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import struct


def glb_json(path):
    data=path.read_bytes()
    if data[:4]!=b'glTF' or struct.unpack_from('<I',data,4)[0]!=2:raise ValueError('Expected GLB v2')
    length,kind=struct.unpack_from('<II',data,12)
    if kind!=0x4e4f534a:raise ValueError('Expected GLB JSON first chunk')
    return data,json.loads(data[20:20+length])


def classify(name):
    if name.startswith('sword_') or name.startswith('shield_'):return 'sword_and_shield'
    if name.startswith('spell_'):return 'casting'
    if name.startswith('pistol_'):return 'firearm_outside_patch'
    if name.startswith('zombie_'):return 'zombie_outside_patch'
    if name.startswith(('farm_','treechopping','fixing_','chest_','driving','dance','yes','idle_talkingphone','idle_rail','swim_')):return 'environment_social_or_special'
    if any(word in name for word in ['walk','jog','sprint','crouch','jump','slide','roll','climb']):return 'locomotion_and_parkour'
    if name.startswith(('melee_','punch_','overhandthrow')):return 'unarmed_or_throw'
    return 'general_states'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--mesh2motion',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise ValueError('Choose a fresh inventory')
    binary,data=glb_json(a.source);mb,mesh=glb_json(a.mesh2motion)
    names={clip['name']:clip for clip in data.get('animations',[])}
    declared=data.get('asset',{}).get('extras',{}).get('clips',list(names))
    if len(names)!=len(data.get('animations',[])):raise ValueError('Duplicate clip names')
    original={re.sub('[^a-z0-9]','',x['name'].lower()):x['name']for x in mesh['animations']}
    remap={'climbup_1m':'ClimbUp_1m_RM','crouch_fwd_loop':'Crouch_Walk',
           'dance_loop':'Dance_Simple','death01':'Death_D','idle_loop':'Idle_A',
           'idle_no_loop':'Idle_ShakeOff','jog_fwd_loop':'Jog','jump_loop':'Jump_air',
           'treechopping_loop':'Chop_Tree','sword_idle':'Idle_Sword',
           'zombie_walk_fwd_loop':'Zombie_Walk','shield_dash':'Shield_Dash_RM',
           'sword_dash':'Sword_Dash_RM'}
    rows=[]
    for name in declared:
        clip=names.get(name)
        row={'id':name,'has_animation':clip is not None,'category':classify(name),
             'loop_hint_from_name':(name.endswith('_loop') and not name.endswith('_no_loop'))or name=='sword_idle',
             'visual_review':'NOT_YET_REVIEWED','rig_retarget':'NOT_YET_TESTED'}
        if clip:
            samplers=clip['samplers'];times=[data['accessors'][s['input']]for s in samplers]
            if any('min'not in t or'max'not in t for t in times):raise ValueError('Missing explicit native input-time ranges')
            start=min(t['min'][0]for t in times);end=max(t['max'][0]for t in times)
            targets=sorted({data['nodes'][c['target']['node']].get('name')for c in clip['channels']})
            row.update({'duration_seconds':end-start,'start_seconds':start,'end_seconds':end,
                        'channels':len(clip['channels']),'animated_nodes':len(targets),
                        'sampler_interpolations':sorted({s.get('interpolation','LINEAR')for s in samplers}),
                        'minimum_key_count':min(t['count']for t in times),
                        'maximum_key_count':max(t['count']for t in times)})
        base=re.sub('_loop$','',name)
        candidate=remap.get(name)or original.get(re.sub('[^a-z0-9]','',base.lower()))
        row['mesh2motion_candidate_by_name']=candidate
        row['same_motion_proven']=False
        row['patch_relevance']='candidate'if row['category']in ['sword_and_shield','casting','general_states','locomotion_and_parkour']else'outside_core_or_optional'
        if name.startswith('sitting_'):row['caution']='Chair-like source posture requires floor-sit review; do not assume floor sitting.'
        if name in ['sword_regular_combo','sword_heavy_combo','sword_regular_c']:row['caution']='Review as skill/combo before considering basic attack; turning and weight transfer not yet inspected.'
        if not clip:row['caution']='Listed in export metadata but no actual animation track is present.'
        rows.append(row)
    canonical={'Hips':'pelvis','Spine':'spine_01','Chest':'spine_03','Neck':'neck_01','Head':'Head'}
    for side,lower in [('L','l'),('R','r')]:
        for target,source in [('Clavicle','clavicle'),('UpperArm','upperarm'),('Forearm','lowerarm'),('Hand','hand'),('Thigh','thigh'),('Shin','calf'),('Foot','foot'),('Toe','ball')]:canonical[target+'.'+side]=source+'_'+lower
        for digit in ['Index','Middle','Ring','Pinky','Thumb']:
            for i in [1,2,3]:canonical[f'{digit}{i}.{side}']=f'{digit.lower()}_{i:02d}_{lower}'
    node_names={n.get('name')for n in data['nodes']}
    missing={k:v for k,v in canonical.items()if v not in node_names}
    result={'status':'COMPLETE_FILE_INVENTORY_NOT_COMPLETE_VISUAL_OR_RETARGET_REVIEW',
            'source_file':str(a.source),'source_sha256':hashlib.sha256(binary).hexdigest(),
            'mesh2motion_source_sha256':hashlib.sha256(mb).hexdigest(),
            'declared_clips':len(declared),'actual_animations':len(names),
            'metadata_without_animation':sorted(set(declared)-set(names)),
            'unlisted_animations':sorted(set(names)-set(declared)),
            'clips':rows,'asset_metadata':data['asset'],
            'canonical_bone_map_candidate':canonical,'missing_candidate_bones':missing,
            'bone_name_coverage_only_not_rest_pose_compatibility':True,
            'dedicated_bow_clip_names':[name for name in names if any(t in name for t in ['bow','archer','arrow'])],
            'preferred_motion_source':'Mesh2Motion','current_factory_sources_replaced':False,
            'runtime_admitted':False}
    a.output.mkdir(parents=True)
    (a.output/'inventory.json').write_text(json.dumps(result,indent=2)+'\n')
    fields=['id','has_animation','category','duration_seconds','loop_hint_from_name','mesh2motion_candidate_by_name','visual_review','rig_retarget','caution']
    with(a.output/'inventory.csv').open('w',newline='')as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n');writer.writeheader();writer.writerows(rows)
    print(json.dumps({'declared_clips':len(declared),'actual_animations':len(names),
                      'missing_tracks':result['metadata_without_animation'],'candidate_bones':len(canonical),
                      'missing_candidate_bones':missing,'bow_clip_names':result['dedicated_bow_clip_names']}))


if __name__=='__main__':main()
