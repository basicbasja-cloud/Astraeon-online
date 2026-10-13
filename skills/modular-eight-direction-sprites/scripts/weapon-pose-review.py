"""Review independently drawn weapon poses, never animate a flat master by rotation."""
import json,argparse,hashlib,math
from pathlib import Path
import numpy as np
from PIL import Image

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit(case,root):
 sp=root/case['source']['path']
 if sha(sp)!=case['source']['sha256']:raise ValueError('Source binding changed')
 source=json.loads(sp.read_text());issues=[];rows=[];ratios=[];paths=[]
 for f in case['frames']:
  p=root/f['path'];paths.append((f['key'],f['sha256']))
  if sha(p)!=f['sha256']:raise ValueError('Weapon pixels changed')
  if abs(f.get('runtime_rotation_degrees',0))>1e-8:issues.append('flat_weapon_runtime_rotation_forbidden')
  if abs(f['shared_scale']-case['shared_scale'])>1e-8:issues.append('per_pose_weapon_rescaling_forbidden')
  if f.get('cell_edge_touched'):issues.append('weapon_cell_clipped_or_spilled')
  points=f.get('observations')
  if not points or any(v is None for v in points.values()):issues.append('weapon_pose_points_unknown');continue
  im=Image.open(p).convert('RGBA')
  for name,xy in points.items():
   x,y=map(round,xy)
   if not(0<=x<im.width and 0<=y<im.height) or im.getpixel((x,y))[3]<100:issues.append('weapon_'+name+'_not_on_visible_pixels')
  rec=source['records'][f['key']];expected=np.subtract(rec['blade_tip_xy'],rec['right_grip_xy']);actual=np.subtract(points['tip'],points['grip']);dot=float(actual@expected/(np.linalg.norm(actual)*np.linalg.norm(expected)));ratio=float(np.linalg.norm(actual)/np.linalg.norm(expected));ratios.append(ratio)
  if dot<.85:issues.append('weapon_angle_disagrees_with_projected_pose')
  rows.append({'key':f['key'],'direction_dot':dot,'drawn_grip_to_tip_length_px':float(np.linalg.norm(actual)),'source_grip_to_tip_length_px':float(np.linalg.norm(expected)),'apparent_scale_ratio':ratio})
 if len({sha for k,sha in paths if k!=7})<=1:issues.append('single_flat_master_reused_across_changing_views')
 if ratios:
  med=float(np.median(ratios));error=max(abs(x/med-1) for x in ratios)
  if error>.20:issues.append('drawn_foreshortening_disagrees_with_common_source_scale')
 else:error=None
 if not case.get('painted_grip_and_occlusion_verified'):issues.append('painted_grip_and_occlusion_unverified')
 return {'schema':'weapon-pose-review-v1','issues':sorted(set(issues)),'status':'INCOMPLETE' if issues else 'REVIEW_REQUIRED','measurements':rows,'maximum_relative_foreshortening_scale_deviation':error,'production_pass':False,'scope':'Different bound projected weapon drawings plus manually observed tip/grip pixels. Angle agreement does not verify blade-face perspective, finger wrap, visibility ordering or complete replacement parts.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=audit(json.loads(a.case.read_text()),a.root);a.out.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['issues'])
if __name__=='__main__':main()
