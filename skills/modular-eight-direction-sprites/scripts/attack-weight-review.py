"""Bound source motion proxies and independent visible body observations.

No inferred mass, damage, anatomical wrist flexion or automatic owner detection.
"""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bound(root,b):
 p=root/b['path']
 if sha(p)!=b['sha256']:raise ValueError('Changed evidence binding: '+str(p))
 return json.loads(p.read_text())
def audit(case,root):
 s=bound(root,case['source_index']);rows=s['dense_bake'];keys=s['records'];issues=[];m={}
 # These values are authored/source-recorded pelvis positions, not COM or force.
 hips=np.asarray([r['hip'] for r in rows]);m['source_hip_forward_range_world']=float(np.ptp(hips[:,1]));m['source_hip_vertical_range_world']=float(np.ptp(hips[:,2]))
 coil=next(r for r in rows if r['time_ms']==keys[2]['time_ms']);follow=next(r for r in rows if r['time_ms']==keys[4]['time_ms']);m['source_coil_to_follow_hip_forward_travel_world']=float(coil['hip'][1]-follow['hip'][1]);m['source_authored_lean_range_degrees']=math.degrees(max(r['lean'] for r in rows)-min(r['lean'] for r in rows))
 if m['source_coil_to_follow_hip_forward_travel_world']<case['contract']['minimum_hip_travel_world']:issues.append('source_transfer_below_declared_family_target')
 if m['source_authored_lean_range_degrees']<case['contract']['minimum_lean_range_degrees']:issues.append('source_trunk_acting_below_declared_family_target')
 u=np.array([-.5,0,.8660254]);u/=np.linalg.norm(u);v=np.array([0,-1,0]);angles=[]
 for r in rows:
  axis=np.subtract(r['blade_tip'],r['right_grip']);angles.append(math.degrees(math.atan2(axis@v,axis@u)))
 angles=np.degrees(np.unwrap(np.radians(angles)));times=np.array([r['time_ms'] for r in rows]);t=keys[3]['time_ms'];h=5
 near=float((np.interp(t+h,times,angles)-np.interp(t-h,times,angles))/(2*h)*1000)
 mean=float((np.interp(t,times,angles)-np.interp(keys[2]['time_ms'],times,angles))/(t-keys[2]['time_ms'])*1000)
 m['source_mid_cut_angular_speed_deg_s']=near;m['source_coil_to_mid_mean_speed_deg_s']=mean;m['source_mid_cut_speed_ratio']=abs(near/mean)
 if abs(near/mean)<case['contract']['minimum_mid_cut_speed_ratio']:issues.append('source_stops_or_slows_at_intermediate_cut_key')
 if case.get('wrist_audit'):
  w=bound(root,case['wrist_audit']);m['actual_source_rest_relative_hand_frame_degrees']=[r['hand_relative_forearm_rotation_from_rest_degrees'] for r in w['own_v27']['rows']]
  # Values include roll; explicit comparison only, no universal joint-limit threshold.
 else:issues.append('source_rest_relative_hand_frame_observations_unknown')
 art=case.get('art');obs=[]
 if art is None:issues.append('painted_weight_and_wrist_observations_unknown')
 else:
  for f in art['frames']:
   p=root/f['path']
   if sha(p)!=f['sha256']:raise ValueError('Painted binding changed')
   points=f['points'];im=Image.open(p).convert('RGBA')
   for name,xy in points.items():
    if xy is None:issues.append('painted_'+name+'_unknown');continue
    x,y=map(round,xy)
    if not(0<=x<im.width and 0<=y<im.height) or im.getpixel((x,y))[3]<100:issues.append('painted_'+name+'_not_on_visible_pixels')
   if points.get('pelvis') and points.get('shoulder'):
    delta=np.subtract(points['shoulder'],points['pelvis']);obs.append({'key':f['key'],'visible_shoulder_to_belt_vector_xy':delta.tolist(),'screen_lean_to_vertical_degrees':math.degrees(math.atan2(delta[0],-delta[1]))})
   if not f.get('anatomical_right_chain_verified'):issues.append('painted_right_chain_identity_unverified')
  if not art.get('acting_accepted_by_user'):issues.append('painted_acting_acceptance_pending')
 return {'schema':'attack-weight-review-v1','status':'REVIEW_REQUIRED' if not issues else 'INCOMPLETE','issues':sorted(set(issues)),'measurements':m,'painted_observations':obs,'production_pass':False,'scope':'Source hip/lean/spacing and manually marked visible surfaces only. No mass/inertia/contact force/damage estimate; no hidden painted skeleton or wrist flexion recovery. Thresholds are this authored family contract.'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();result=audit(json.loads(a.case.read_text()),a.root);result['case_sha256']=sha(a.case);a.out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['issues'],result['measurements'])
if __name__=='__main__':main()
