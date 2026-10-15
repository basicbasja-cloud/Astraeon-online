"""Bounded source/actual-capture checks; no general image anatomy approval."""
from pathlib import Path
import json,math,hashlib,argparse
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2];OLD=P.parent/'free-character-v44'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def finite(x):return isinstance(x,(int,float)) and math.isfinite(x)
def arm_gate(data):
 policy=json.loads((P/'arm-contract.json').read_text());s=data.get('summary',{});c={};lim=lambda k,lo,hi:finite(s.get(k)) and lo<=s[k]<=hi
 c['relaxed_arm_abduction']=lim('max_abduction_degrees',0,policy['maximum_upperarm_lateral_abduction_degrees'])
 c['body_relative_elbow_plane']=lim('max_plane_deviation_degrees',0,policy['maximum_elbow_plane_deviation_from_body_lateral_degrees'])
 c['limited_flexion']=lim('min_flexion_degrees',policy['minimum_flexion_degrees'],policy['maximum_flexion_degrees']) and lim('max_flexion_degrees',policy['minimum_flexion_degrees'],policy['maximum_flexion_degrees'])
 c['no_normal_flip']=lim('max_normal_step_degrees',0,10)
 c['dense_between_bake_evaluations']=len(data.get('frames',[]))==313
 c['current_enabled_skin']=data.get('missing_actual_modifiers')==[] and data.get('mesh_count')==115
 c['weights_valid']=finite(data.get('maximum_weight_sum_error')) and data['maximum_weight_sum_error']<1e-6 and data.get('invalid_weights')==0
 c['actual_neutral_bind']=finite(data.get('actual_bind_vertex_error')) and data['actual_bind_vertex_error']<1e-5
 c['source_keys_exact']=len(data.get('source_key_errors',[]))==8 and all(finite(f.get('max_error')) and f['max_error']<1e-5 for f in data['source_key_errors'])
 c['deformed_sections_preserved']=lim('min_ring_area_ratio',.95,1.05) and lim('max_ring_area_ratio',.95,1.05)
 c['longitudinal_rings_not_collapsed']=lim('min_ring_spacing_ratio',.5,1.5)
 c['subpixel_between_key_support']=lim('max_foot_vertex_drift',0,policy['maximum_bake_gap_foot_drift_world']) and lim('max_right_socket_error',0,policy['maximum_bake_gap_foot_drift_world'])
 c['closed_current_arm_surface']=data.get('arm_nonmanifold_edges')==0
 c['fixed_bone_lengths']=lim('max_bone_length_error',0,1e-5)
 return c

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-only',action='store_true');args=ap.parse_args();i=json.loads((P/'arm-inspection.json').read_text());r=json.loads((P/'receipt.json').read_text());v=json.loads((P/'arm-visibility-receipt.json').read_text());oldvis=json.loads((P/'before-arm-visibility-receipt.json').read_text());c=arm_gate(i['after']);c['real_rejected_v44_arm_now_fails']=not all(arm_gate(i['before']).values());c['saved_rigs_bound']=sha(P/'original-character.blend')==i['after']['blend_sha256']==v['blend_sha256'] and sha(OLD/'original-character.blend')==i['before']['blend_sha256'];c['scripts_contract_bound']=sha(P/'inspect-arm.py')==i['script_sha256'] and sha(P/'arm-contract.json')==i['contract_sha256'] and sha(P/'build-character.py')==r['script_sha256'] and sha(P/'render-arm-visibility.py')==v['script_sha256'];views=['S','SE','E','NE','N','NW','W','SW'];c['all_eight_physical_views']=len(r['frames'])==35 and all(list(f['views'])==views for f in r['frames']);bindings=[]
 for f in r['frames']:bindings+=list(f['views'].values())+list(f['ownership_images'].values())
 for f in v['frames']+oldvis['frames']:bindings+=list(f['images'].values())
 c['actual_536_capture_bytes']=len(bindings)==536 and all((P/x['path']).is_file() and sha(P/x['path'])==x['sha256'] for x in bindings)
 visibility=[]
 for f in v['frames']:
  counts={}
  for k,x in f['images'].items():
   a=np.asarray(Image.open(P/x['path']).convert('RGBA'));counts[k]=int(((a[:,:,0]>240)&(a[:,:,1]>60)&(a[:,:,1]<200)&(a[:,:,2]<80)&(a[:,:,3]>128)).sum())
  frac=counts['depth_tested']/counts['isolated'] if counts['isolated'] else None
  visibility.append(dict(index=f['index'],view=f['view'],counts=counts,visible_fraction=frac,observation='IMAGE_ANATOMY_UNKNOWN_OCCLUDED' if frac is None or frac<.2 else 'PARTIAL_SOURCE_SURFACE_VISIBLE_NOT_IMAGE_ANATOMY_APPROVAL'))
 nonarm_isolated=0
 for f in v['frames']+oldvis['frames']:
  a=np.asarray(Image.open(P/f['images']['isolated']['path']).convert('RGBA'));orange=(a[:,:,0]>240)&(a[:,:,1]>60)&(a[:,:,1]<200)&(a[:,:,2]<80);nonarm_isolated+=int(((a[:,:,3]>128)&~orange).sum())
 c['isolated_pass_contains_only_arm_surface']=nonarm_isolated==0
 c['isolated_arm_has_real_surface_all_keys']=all(f['counts']['isolated']>100 for f in visibility)
 c['depth_surface_never_added_over_occluders']=all(f['visible_fraction'] is not None and f['visible_fraction']<=1.01 for f in visibility)
 source=json.loads((P.parent/'continuous-arm-v43/source/source.json').read_text());err=0
 for f in r['frames']:
  for view in views:
   inv=np.linalg.inv(source['cameras'][view]['world_matrix']);scale=512/source['cameras'][view]['ortho_scale']
   for k,world in f['world_points'].items():
    q=inv@np.array(world+[1]);pred=np.array([192+q[0]*scale,256-q[1]*scale]);err=max(err,float(np.linalg.norm(pred-f['projected_points'][view][k])))
 c['independent_world_projection']=err<.001
 b=json.loads((P/'display-bind.json').read_text());c['exact_prior_display_matrix']=b['matrix']==json.loads((OLD/'display-bind.json').read_text())['matrix'] and b['baseline_display_sha256']==sha(OLD/'display-bind.json')
 # Frozen prior evidence, including the rejected v44 drawings, remains unchanged.
 changes=[]
 for m in (ROOT/'research/sprite-animation').glob('*/evidence-manifest.json'):
  if m.parent==P:continue
  for leaf in json.loads(m.read_text()).get('files',[]):
   if not (ROOT/leaf['path']).is_file() or sha(ROOT/leaf['path'])!=leaf['sha256']:changes.append(leaf['path'])
 c['all_prior_frozen_leaves_unchanged']=not changes
 w=json.loads((ROOT/'research/sprite-animation/joint-tracking-ro-v30/protected-W.json').read_text());c['accepted_W_unchanged']=all(sha(ROOT/f['path'])==f['expected_sha256'] for f in w['files'])
 c['before_isolation_bound']=oldvis['blend_sha256']==i['before']['blend_sha256'] and oldvis['script_sha256']==sha(P/'render-before-arm.py')
 c['free_only']=r['provider_calls']==r['credits']==0
 result=dict(checks=c,bounded_arm_source_pass=all(c.values()),before=i['before']['summary'],after=i['after']['summary'],projection_max_px=err,isolated_nonarm_pixel_count=nonarm_isolated,arm_visibility=visibility,changed_frozen=changes,scope='Relaxed free LEFT arm pickup source+direct geometry captures. Numeric limits are authored action guards, not universal human anatomy. Orange visibility is actual known-mesh surface, not an arbitrary-image classifier. Full acting/artwork/collisions/user approval remain unproved.',production_pass=False);(P/'audit.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(dict(checks=c,bounded_arm_source_pass=all(c.values()),production_pass=False),indent=2));return 0 if args.source_only and all(c.values()) else 1
if __name__=='__main__':raise SystemExit(main())
