#!/usr/bin/env python3
"""Audit research-corpus bindings/clocks/exclusions; never approve anatomy/art."""
import argparse,gzip,hashlib,json,math
from pathlib import Path
from PIL import Image

def specs(catalog,taxonomy):
 errors=[];sources=catalog['sources'];motions=taxonomy['motions'];ids=[s['id'] for s in sources]
 if len(ids)!=len(set(ids)):errors.append('duplicate_source_id')
 if len({m['id'] for m in motions})!=len(motions):errors.append('duplicate_motion_id')
 if taxonomy.get('dash_policy') not in ('excluded','optional_research') or not taxonomy.get('old_attacks_excluded'):errors.append('missing_user_scope')
 for s in sources:
  if s.get('old_own_attack_reference') is not False:errors.append('old_attack_source:'+s['id'])
  if s.get('asset_admission')!='not_admitted':errors.append('unreviewed_asset_admitted:'+s['id'])
 for m in motions:
  if 'dash' in m['id'].lower():
   if taxonomy['dash_policy']=='excluded':errors.append('dash_motion:'+m['id'])
   if taxonomy['dash_policy']=='optional_research' and (m.get('scope')!='optional' or m.get('gameplay_committed') is not False):errors.append('dash_not_optional:'+m['id'])
  if not m['phase_beats'] or not m['specific_review']:errors.append('empty_recipe:'+m['id'])
  if set(m['reference_leads'])-set(ids):errors.append('dangling_source:'+m['id'])
  if m.get('production_approved') is not False:errors.append('unearned_production_approval:'+m['id'])
 return errors

def capture_errors(report):
 errors=[];frames=report['frames']
 if not frames:return ['empty_capture']
 for i,f in enumerate(frames):
  if f['index']!=i:errors.append('ordinal_order')
  if not math.isfinite(f['source_pts_ms']) or not math.isfinite(f['duration_ms']) or f['duration_ms']<=0:errors.append('invalid_native_time')
  if i and f['source_index']!=frames[i-1]['source_index']+1:errors.append('source_frame_gap')
  if i and abs(f['source_pts_ms']-(frames[i-1]['source_pts_ms']+frames[i-1]['duration_ms']))>1e-5:errors.append('native_clock_discontinuity')
  if abs(f['time_ms']-(f['source_pts_ms']-frames[0]['source_pts_ms']))>1e-5:errors.append('elapsed_clock_mismatch')
 if abs(report['duration_ms']-(frames[-1]['time_ms']+frames[-1]['duration_ms']))>1e-5:errors.append('duration_mismatch')
 return sorted(set(errors))

def safe(root,path):
 target=(root/path).resolve()
 if not target.is_relative_to(root.resolve()):raise ValueError('Path outside corpus')
 return target

def bound(root,path,expected):
 target=safe(root,path)
 if hashlib.sha256(target.read_bytes()).hexdigest()!=expected:raise ValueError('Changed file '+path)
 return target

def multiply(a,b):return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]

def matrix_residual(sample,bones):
 worst=0.0
 for name,bone in bones.items():
  world=sample['world_bone_matrices'][name];local=sample['parent_local_bone_matrices'][name]
  for matrix in (world,local,sample['object_world_matrix']):
   if len(matrix)!=4 or any(len(row)!=4 or any(not math.isfinite(v) for v in row) for row in matrix):raise ValueError('Invalid source matrix')
  parent=sample['world_bone_matrices'][bone['parent']] if bone['parent'] else sample['object_world_matrix']
  rebuilt=multiply(parent,local)
  worst=max(worst,max(abs(rebuilt[i][j]-world[i][j]) for i in range(4) for j in range(4)),max(abs(world[i][3]-sample['world_joints'][name][i]) for i in range(3)))
 return worst

def audit(root):
 root=root.resolve();issues=[]
 catalog=json.loads((root/'sources.json').read_text());taxonomy=json.loads((root/'motions.json').read_text())
 issues.extend(specs(catalog,taxonomy))
 inventory=json.loads((root/'clip-inventory.json').read_text());samples=json.loads(gzip.decompress((root/'preset-samples.json.gz').read_bytes()))
 clip_counts={'serialized_animations':0,'dash_included':0,'rest_poses_excluded':0,'motion_candidates':0};poses=0;matrix_error=0.0
 for f in inventory['files']:
  bound(root,f['path'],f['sha256']);bound(root,f['license_path'],f['license_sha256'])
  if not f['path'].startswith('open-data/'):issues.append('non_external_motion_source')
  sample=next(s for s in samples['files'] if s['source_id']==f['source_id'])
  if sample['source_sha256']!=f['sha256']:issues.append('stale_source_evaluation')
  allowed={c['name'] for c in f['clips'] if c['exclusion'] is None}
  if {c['name'] for c in sample['clips']}!=allowed:issues.append('included_clip_bank_mismatch')
  for clip in f['clips']:
   clip_counts['serialized_animations']+=1
   label=clip['exclusion']
   if 'dash' in clip['name'].lower() and label is None:clip_counts['dash_included']+=1
   clip_counts[{'rest_pose_not_motion':'rest_poses_excluded',None:'motion_candidates'}[label]]+=1
   if label is not None:continue
   selected=next(c for c in sample['clips'] if c['name']==clip['name'])
   for s in selected['samples']:
    t=clip['native_key_times_seconds'][s['native_key_index']]
    if abs(t-s['source_time_seconds'])>1e-8:issues.append('sample_not_native_key')
    if set(s['world_joints'])!=set(sample['bones']):issues.append('incomplete_source_joint_bank')
    if any(not math.isfinite(v) for p in s['world_joints'].values() for v in p):issues.append('invalid_source_joint')
    residual=matrix_residual(s,sample['bones']);matrix_error=max(matrix_error,residual)
    if residual>2e-5:issues.append('source_matrix_head_inconsistency')
    poses+=1
  if sample['source_id']=='kay-oga' and len(sample['bones'])!=6:issues.append('legacy_rig_count_changed')
 if clip_counts!=inventory['counts']:issues.append('advertised_count_used_in_inventory')
 captures=[];frames_total=0
 for directory in sorted((root/'captures').glob('kaykit-preview-*')):
  report=json.loads((directory/'capture.json').read_text());issues.extend(capture_errors(report))
  for f in report['frames']:
   p=bound(directory,f['file'],f['sha256'])
   with Image.open(p) as im:
    if list(im.size)!=list(report['canvas']):issues.append('capture_canvas_drift')
    if hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()!=f['rgba_pixels_sha256']:issues.append('lossless_pixel_drift')
  for name in report['review_boards']:
   if not safe(directory,name).exists():issues.append('missing_contact_sheet')
  frames_total+=len(report['frames']);captures.append({'id':directory.name,'frames':len(report['frames']),'duration_ms':report['duration_ms']})
 for filename,field in [('preset-board-manifest.json','boards'),('sprite-board-manifest.json','boards')]:
  for b in json.loads((root/filename).read_text())[field]:bound(root,b.get('file',b.get('board_file')),b.get('sha256',b.get('board_sha256')))
 return {'schema':'rpg-reference-corpus-audit-v1','corpus_integrity_pass':not issues,'production_pass':False,'art_anatomy_accuracy':None,'issues':sorted(set(issues)),'max_source_matrix_head_residual':matrix_error,'counts':{'sources':len(catalog['sources']),'motion_specifications':len(taxonomy['motions']),**clip_counts,'source_sampled_poses':poses,'native_gif_frames':frames_total},'captures':captures,'scope':'Provenance/timing/actual-RGBA/structure/exclusion audit only; phase meaning, contact, limb identity, acting and modular production remain independently unapproved.'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--study',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 result=audit(a.study);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));raise SystemExit(0 if result['corpus_integrity_pass'] else 2)
if __name__=='__main__':main()
