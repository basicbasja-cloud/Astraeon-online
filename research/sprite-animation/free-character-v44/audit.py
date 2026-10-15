"""Bounded evidence gates. --source-only may pass; production remains blocked.
This is not a general image/anatomy classifier or an approval generator.
"""
from pathlib import Path
import json,hashlib,math,argparse
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def valid_number(x):return isinstance(x,(int,float)) and math.isfinite(x)
def inspect_gate(r):
 c={}
 c['no_missing_real_deform_modifiers']=r.get('missing_armature_modifiers')==[]
 c['normalized_nonnegative_weights']=r.get('unweighted_vertices')==0 and r.get('invalid_weights')==0 and valid_number(r.get('maximum_weight_sum_error')) and r['maximum_weight_sum_error']<1e-6
 c['actual_bind_vertices_unchanged']=bool(r.get('actual_bind_vertex_errors')) and all(valid_number(v) and v<1e-5 for v in r['actual_bind_vertex_errors'].values())
 c['all_eight_source_keys']=len(r.get('source_key_errors',[]))==8 and all(valid_number(f.get('max_error')) and f['max_error']<1e-5 for f in r['source_key_errors'])
 c['dense_157_actual_evaluations']=r.get('dense_sample_count')==157 and len(r.get('frames',[]))==157
 for name,key,limit in [('feet_fixed','max_dense_foot_vertex_drift',1e-5),('bone_lengths_fixed','max_dense_bone_length_error',1e-5),('right_grasp_fixed','max_dense_right_grasp_socket_error',1e-5),('shared_hinge_frames','max_dense_hinge_axis_error',1e-5)]:c[name]=valid_number(r.get(key)) and r[key]<limit
 c['no_sole_floor_penetration']=valid_number(r.get('min_dense_sole_world_z')) and 0<=r['min_dense_sole_world_z']<.002
 limits=r.get('dense_limb_ring_area_ratio_range',[]);c['sampled_ring_areas']=len(limits)==2 and all(valid_number(x) for x in limits) and .95<=limits[0]<=limits[1]<=1.05
 c['all_four_limb_surfaces_closed']=len(r.get('closed_limb_topology',{}))==4 and all(v.get('nonmanifold_edges')==0 for v in r['closed_limb_topology'].values())
 c['two_authoring_slots']=r.get('runtime_slots')==['body_outfit','complete_head']
 return c

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source-only',action='store_true');args=ap.parse_args();r=json.loads((P/'receipt.json').read_text());g=json.loads((P/'saved-rig-inspection.json').read_text());c=inspect_gate(g);c['blend_binding']=sha(P/'original-character.blend')==g['blend_sha256'];c['inspection_binding']=sha(P/'inspect-saved-rig.py')==g['inspection_script_sha256'];c['authoring_binding']=sha(P/'build-character.py')==r['script_sha256'];c['source_binding']=sha(P.parent/'continuous-arm-v43/source/source.json')==r['source_sha256']==g['source_sha256'];c['no_credit_provider']=r['provider_calls']==r['credits']==0
 views=['S','SE','E','NE','N','NW','W','SW'];c['all_35_poses_eight_views']=len(r['frames'])==35 and all(list(f['views'])==views for f in r['frames']);bad=[];images=0
 for f in r['frames']:
  for item in list(f['views'].values())+list(f['ownership_images'].values()):
   path=P/item['path'];images+=1
   if not path.is_file() or sha(path)!=item['sha256']:bad.append(item['path']);continue
   im=Image.open(path)
   if im.size!=(384,512) or im.mode!='RGBA' or np.max(np.asarray(im)[:,:,3])==0:bad.append(item['path'])
 c['all_actual_capture_bytes']=images==344 and not bad
 source=json.loads((P.parent/'continuous-arm-v43/source/source.json').read_text());projection=0
 for f in r['frames']:
  for v in views:
   inv=np.linalg.inv(np.array(source['cameras'][v]['world_matrix']));ortho=source['cameras'][v]['ortho_scale']
   for k,p in f['world_points'].items():
    a=inv@np.array(p+[1]);xy=np.array([(a[0]/(ortho*.75)+.5)*384,(.5-a[1]/ortho)*512]);projection=max(projection,float(np.linalg.norm(xy-f['projected_points'][v][k])))
 c['independent_camera_projection']=projection<.001
 # A current-image mask observation catches the actual old frozen-render failure.
 image_motion={}
 for v in views:
  centers=[]
  for i in [0,3]:
   a=np.asarray(Image.open(P/f'renders/ownership/{v}/{i:02}.png'));mask=(a[:,:,1]>240)&(a[:,:,0]<10)&(a[:,:,2]<10)&(a[:,:,3]>240);ys,xs=np.where(mask);centers.append(None if not len(xs) else [float(xs.mean()),float(ys.mean())])
  image_motion[v]=None if None in centers else float(np.linalg.norm(np.subtract(*centers)))
 c['actual_head_surface_moves_all_views']=all(v is not None and v>20 for v in image_motion.values())
 # Preserve previous published research bytes and the accepted W art.
 frozen=[]
 for f in (ROOT/'research/sprite-animation').glob('*/evidence-manifest.json'):
  if f.parent==P:continue
  m=json.loads(f.read_text())
  for leaf in m.get('files',[]):
   p=ROOT/leaf['path']
   if not p.is_file() or sha(p)!=leaf['sha256']:frozen.append(leaf['path'])
 c['all_prior_manifest_leaves_unchanged']=not frozen
 w=json.loads((ROOT/'research/sprite-animation/joint-tracking-ro-v30/protected-W.json').read_text());c['accepted_W_unchanged']=all(sha(ROOT/f['path'])==f['expected_sha256'] for f in w['files'])
 x=json.loads((P/'corrective-glb-roundtrip.json').read_text());ex=json.loads((P/'corrective-export-receipt.json').read_text());gx=json.loads((P/'corrective-glb-inspection.json').read_text())
 c['corrective_export_bytes_bound']=sha(P/'original-character-corrected.glb')==x['glb_sha256']==ex['glb_sha256']==gx['sha256'] and ex['source_blend_sha256']==g['blend_sha256'] and ex['script_sha256']==sha(P/'export-corrective-character.py')
 c['actual_40_sample_glb_roundtrip']=len(x['frames'])==40 and x['roundtrip_surface_pass'] and all(valid_number(f['max_surface_vertex_distance']) and f['max_surface_vertex_distance']<.0001 for f in x['frames'])
 c['one_synchronized_corrective_clip']=gx['animation_count']==1 and gx['pass_all']
 c['baseline_export_failure_preserved']=not json.loads((P/'glb-roundtrip.json').read_text())['roundtrip_surface_pass'] and not json.loads((P/'corrective-split-actions-REJECTED/corrective-glb-roundtrip.json').read_text())['roundtrip_surface_pass']
 result=dict(checks=c,bounded_source_and_current_capture_pass=all(c.values()),capture_count=images,independent_projection_max_px=projection,current_head_id_surface_displacement_px=image_motion,missing_or_changed_captures=bad,changed_frozen=frozen,source_scope='Saved full weighted rig and direct renderer captures; green mask is visible head surface centroid, not a detected anatomical joint. No painted-image tracking, dense surface collision or human acting proof.',visual_quality_pass=False,production_pass=False)
 (P/'audit.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(dict(checks=c,projection_max_px=projection,source_pass=all(c.values()),production_pass=False),indent=2));return 0 if args.source_only and all(c.values()) else 1
if __name__=='__main__':raise SystemExit(main())
