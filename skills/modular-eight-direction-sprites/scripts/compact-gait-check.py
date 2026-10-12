"""SHA-bound source-only checks for the authored compact-walk adapter.

Checks actual exported dense soles, a fixed vertex during authored flat stance,
and the actual baked sagittal pelvis/neck chain. Never certifies drawn anatomy.
"""
import argparse,hashlib,json,math
from pathlib import Path

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def distance(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
def inspect(contract):
 c=json.loads(Path(contract).read_text()); ground=Path(c['ground_path']);g=json.loads(ground.read_text())
 for path,expected in [(ground,c['ground_sha256']),(g['blend_path'],g['blend_sha256']),(g['motion_path'],g['motion_sha256'])]:
  if sha(path)!=expected:raise ValueError('Stale source binding: '+str(path))
 m=json.loads(Path(g['motion_path']).read_text())
 if m['schema']!='original-compact-gait-v1' or not m.get('upright_spine_from_rest'):raise ValueError('Explicit compact/upright adapter required')
 duration=m['duration_seconds'];dense=g['dense_samples'];frames=m['frames']
 if duration<=0 or len(dense)<3 or len(frames)<3:raise ValueError('Dense source samples required')
 times=[f['time_seconds'] for f in dense]
 if abs(times[0])>1e-8 or abs(times[-1]-duration)>1e-8 or any(b<=a for a,b in zip(times,times[1:])):raise ValueError('Ordered full-cycle endpoint-inclusive samples required')
 angles=[]
 for f in frames:
  p=f['in_place_joints']['pelvis'];n=f['in_place_joints']['neck_01'];dz=n[2]-p[2]
  if dz<=0:raise ValueError('Invalid pelvis/neck ordering')
  angles.append(math.degrees(math.atan2(abs(n[1]-p[1]),dz)))
 flat=[]
 for side,offset in [('left',0),('right',.5)]:
  groups=[];active=[];name='sole.'+side+'.heel'
  for f in dense:
   phase=(f['time_seconds']/duration+offset)%1
   if .07<=phase<=.50:active.append(f['soles'][name])
   elif active:groups.append(active);active=[]
  if active:groups.append(active)
  for group in groups:
   ids={v['fixed_sole_vertex_index'] for v in group}
   if len(ids)!=1:raise ValueError('Contact sample changed fixed vertex identity')
   anchor=group[0]['fixed_sole_vertex_world_traveled'];flat.append({'side':side,'samples':len(group),'vertex_index':next(iter(ids)),'drift_evaluable':len(group)>=2,'max_drift_world':max(distance(v['fixed_sole_vertex_world_traveled'],anchor) for v in group) if len(group)>=2 else None})
 measured=[x for x in flat if x['drift_evaluable']]
 if {x['side'] for x in measured}!={'left','right'}:raise ValueError('Insufficient flat-support samples on either side')
 low=min(s['minimum_mesh_z'] for f in dense for s in f['soles'].values())
 air=sum(min(s['minimum_mesh_z'] for s in f['soles'].values())>c['budgets']['airborne_height_world'] for f in dense)
 seam=max(distance(frames[0]['in_place_joints'][n],frames[-1]['in_place_joints'][n]) for n in frames[0]['in_place_joints'])
 result={'schema':'compact-source-gait-check-v1','contract_sha256':sha(contract),'ground_sha256':sha(ground),'baked_samples':len(frames),'dense_samples':len(dense),'sagittal_neck_pelvis_tilt_deg':[min(angles),max(angles)],'minimum_actual_sole_z':low,'both_feet_airborne_candidates':air,'flat_support_intervals':flat,'maximum_in_place_joint_endpoint_error_world':seam,'scope':'Source only: baked neck chain plus dense actual sole vertices. Flat support intervals are authored. Rolling contact, support force/balance, painted posture/owners, parts and runtime contact are NOT certified.','painted_posture_verified':False,'painted_anatomy_verified':False,'production_ready':False}
 b=c['budgets'];failed=[]
 if max(angles)>b['sagittal_tilt_deg']:failed.append('source posture')
 if low < -b['penetration_world']:failed.append('source sole penetration')
 if air:failed.append('both feet elevated')
 if max(x['max_drift_world'] for x in measured)>b['flat_vertex_drift_world']:failed.append('flat-support vertex drift')
 if seam>b['joint_endpoint_world']:failed.append('in-place loop endpoint')
 result['failed_source_checks']=failed;result['source_checks_passed']=not failed
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=inspect(a.contract);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n');print('COMPACT_SOURCE_CHECK',r['source_checks_passed']);raise SystemExit(0 if r['source_checks_passed'] else 2)
if __name__=='__main__':main()
