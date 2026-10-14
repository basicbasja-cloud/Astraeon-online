"""Check a goal-conditioned pickup, not merely a named clip or neck trajectory."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image

def audit(data,folder):
    folder=Path(folder);f=data['frames'];checks={};p=lambda i,k:np.array(f[i]['points'][k]['world_xyz'])
    checks['eight_ordered_samples']=len(f)==8 and [x['index'] for x in f]==list(range(8)) and all(f[i+1]['time_seconds']>f[i]['time_seconds'] for i in range(7))
    rest_lengths={};errors=[]
    for name,a,b,parent in data['bone_definitions']:
        if b is None:continue
        length=float(np.linalg.norm(p(0,b)-p(0,a)));rest_lengths[name]=length;errors += [abs(float(np.linalg.norm(p(i,b)-p(i,a)))-length) for i in range(8)]
    checks['fixed_bone_lengths']=max(errors)<1e-5
    drift=max(float(np.linalg.norm(p(i,k)-p(0,k))) for i in range(8) for k in ['left.ankle','right.ankle','left.toe','right.toe'])
    checks['planted_source_feet']=drift<1e-6
    peak=data['grasp_frame'];axis=p(peak,'neck')-p(peak,'pelvis');hinge=float(np.degrees(np.arccos(axis[2]/np.linalg.norm(axis))))
    checks['real_forward_hip_hinge']=hinge>=55 and p(0,'pelvis')[2]-p(peak,'pelvis')[2]>=.30
    forward=np.array(data['forward_world']);reach=float(np.dot(p(peak,'right.grip')-p(peak,'pelvis'),forward))
    chain={name:(a,b,parent) for name,a,b,parent in data['bone_definitions']}
    ownership=(p(0,'right.hip')[0]<p(0,'left.hip')[0] and p(0,'right.shoulder')[0]<p(0,'left.shoulder')[0] and chain['right.hand']==('right.wrist','right.palm','right.lowerarm') and chain['right.lowerarm']==('right.elbow','right.wrist','right.upperarm'))
    checks['right_hand_reaches_forward']=reach>=.70 and p(0,'right.palm')[2]-p(peak,'right.palm')[2]>=.5 and ownership
    grounded=[abs(float(fr['object_center'][2])-data['object_half_height']) for fr in f[:peak+1]]
    checks['object_rests_on_ground_before_contact']=max(grounded)<1e-6
    checks['ground_object_does_not_teleport']=max(float(np.linalg.norm(np.array(fr['object_center'])-f[0]['object_center'])) for fr in f[:peak+1])<1e-6
    contact=float(np.linalg.norm(p(peak,'right.grip')-f[peak]['grasp_socket_world']))
    checks['right_grip_socket_contact']=contact<1e-5
    grip_offsets=[float(np.linalg.norm(p(i,'right.palm')+data['palm_to_grip_world']-p(i,'right.grip'))) for i in range(8)]
    checks['wrist_palm_and_grip_not_confused']=max(grip_offsets)<1e-6 and abs(data['palm_to_grip_world'][2])>.01
    carry=max(float(np.linalg.norm(p(i,'right.grip')-(np.array(f[i]['object_center'])+[0,0,data['object_half_height']]))) for i in range(peak+1,data['store_frame']))
    checks['item_follows_same_grip_after_contact']=carry<1e-5 and f[5]['object_center'][2]>f[peak]['object_center'][2]+.4 and not f[7]['object_visible']
    checks['free_left_hand_is_not_grasping']=float(np.linalg.norm(p(peak,'left.palm')-f[peak]['grasp_socket_world']))>.3
    projection=[];visibility=[];hashes=[]
    for row in f:
        for view,cam in data['cameras'].items():
            inverse=np.linalg.inv(np.array(cam['world_matrix']));scale=data['canvas'][1]/cam['ortho_scale'];w,h=data['canvas']
            for point in row['points'].values():
                v=inverse@np.array([*point['world_xyz'],1]);xy=[w/2+scale*v[0],h/2-scale*v[1]];projection.append(float(np.linalg.norm(np.array(xy)-point['xy'][view])))
            b=row['views'][view];hashes.append(hashlib.sha256((folder/b['path']).read_bytes()).hexdigest()==b['sha256'])
        b=row['owner_pass'];hashes.append(hashlib.sha256((folder/b['path']).read_bytes()).hexdigest()==b['sha256'])
        b=row['right_hand_visibility_pass'];path=folder/b['path'];hashes.append(hashlib.sha256(path.read_bytes()).hexdigest()==b['sha256']);a=np.array(Image.open(path).convert('RGBA'));blue=(a[:,:,2]>200)&(a[:,:,0]<30)&(a[:,:,1]<100)&(a[:,:,3]>=128);red=(a[:,:,0]>200)&(a[:,:,1]<30)&(a[:,:,2]<30)&(a[:,:,3]>=128)
        by,bx=np.where(blue);center_error=float(np.linalg.norm(np.array([bx.mean(),by.mean()])-row['points']['right.palm']['xy']['rear'])) if len(bx) else None
        visibility.append(dict(index=row['index'],right_palm_pixels=int(blue.sum()),object_pixels=int(red.sum()),visible_palm_centroid_to_source_center_px=center_error))
    checks['independent_projection']=max(projection)<.001
    checks['actual_capture_hashes']=all(hashes)
    checks['right_palm_and_item_visible_at_grasp']=visibility[peak]['right_palm_pixels']>=20 and visibility[peak]['object_pixels']>=20 and visibility[peak]['visible_palm_centroid_to_source_center_px']<14
    checks={k:bool(v) for k,v in checks.items()}
    return dict(checks=checks,source_action_pass=all(checks.values()),max_bone_length_error=max(errors),max_foot_world_drift=drift,hip_hinge_degrees=hinge,forward_reach_from_pelvis=reach,right_grip_error=contact,carry_socket_error=carry,max_projection_error_px=max(projection),actual_scene_visibility=visibility,scope='Original authored geometric source and actual source-camera pixels only. No mass balance/force simulation, automatic painted-side recognition, finger fit, user-art or production approval.',production_pass=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();r=audit(json.loads(a.source.read_text()),a.source.parent.parent);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='actual_scene_visibility'}));return 0 if r['source_action_pass'] else 1
if __name__=='__main__':raise SystemExit(main())
