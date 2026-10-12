"""Projection-aware actual-pixel sole review. Diagnostic, not inferred physics.

Each ROI is an independently inspected visible heel/toe patch. A changing whole
sprite bottom is never a contact point. One declared transform applies to the
entire clip; the checker never moves any artwork or fits each pose separately.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sole_pixels(path,box,canvas):
 with Image.open(path) as im:
  if list(im.size)!=canvas:raise ValueError('Wrong artwork canvas')
  a=np.array(im.convert('RGBA'))[:,:,3]
 x0,y0,x1,y1=box
 if not(0<=x0<x1<=canvas[0] and 0<=y0<y1<=canvas[1]):raise ValueError('Invalid sole ROI')
 mask=a[y0:y1,x0:x1]>128
 if mask.sum()<16:return {'status':'INCONCLUSIVE_EMPTY_OR_TINY_PATCH'}
 if mask[-1].any():return {'status':'INCONCLUSIVE_ROI_CLIPS_LOWER_CONTOUR'}
 columns=np.where(mask.any(axis=0))[0]
 bottoms=np.array([np.where(mask[:,x])[0][-1]+y0 for x in columns])
 return {'status':'VISIBLE_SOLE_CONTOUR_MEASURED','pixels':int(mask.sum()),'sampled_columns':len(columns),'lower_contour_y_px':float(np.percentile(bottoms,90)),'maximum_alpha_y_px':int(bottoms.max())}

def audit(spec):
 p=Path(spec['source_ground_path'])
 if sha(p)!=spec['source_ground_sha256']:raise ValueError('Changed source floor receipt')
 source=json.loads(p.read_text())
 if sha(source['blend_path'])!=source['blend_sha256'] or sha(source['motion_path'])!=source['motion_sha256']:raise ValueError('Changed authoritative rig/motion')
 s=spec['shared_scale'];ty=spec['shared_translation_y_px']
 if not(np.isfinite(s) and s>0 and np.isfinite(ty)):raise ValueError('Invalid shared transform')
 report={'schema':'painted-ground-review-v1','source_ground_sha256':sha(p),'shared_scale':s,'shared_translation_y_px':ty,'per_frame_fit':False,'art_modified':False,'world_support_verified':False,'anatomical_identity_verified':False,'status':'DIAGNOSTIC_REQUIRES_VISUAL_REVIEW','frames':[],
         'scope':'Projected source-floor comparison of manually selected visible sole contours; ROI/identity/scale calibration can be wrong. Not recovery of image depth, weight or world-space foot-lock.'}
 for f in spec['frames']:
  if not isinstance(f['source_key'],int) or not 0<=f['source_key']<len(source['frames']):raise ValueError('Invalid source phase key')
  if sha(f['image'])!=f['sha256']:raise ValueError('Changed artwork invalidates sole review')
  row={'source_key':f['source_key'],'image':f['image'],'observations':[]}
  row['calibration_sample_not_independent_validation']=f.get('calibration_sample_not_independent_validation',False)
  for o in f['soles']:
   if o.get('roi_xyxy') is None:row['observations'].append({'status':'UNKNOWN_VISIBLE_SOLE'});continue
   if o['side'] not in ['left','right'] or o['part'] not in ['heel','toe']:raise ValueError('Invalid anatomical source sole')
   src=source['frames'][f['source_key']]['soles'][f"sole.{o['side']}.{o['part']}"]
   measured=sole_pixels(f['image'],o['roi_xyxy'],spec['canvas'])
   measured.update(side=o['side'],part=o['part'],roi_xyxy=o['roi_xyxy'],identity_review=o.get('identity_review','unconfirmed'),source_near_plane_candidate=src['near_plane_candidate'],source_height_world=src['minimum_mesh_z'],expected_ground_y_px=s*src['same_xy_on_ground_projected'][1]+ty,expected_sole_y_px=s*src['lowest_xy'][1]+ty)
   measured['calibration_observation_not_validation']=o.get('calibration_observation',row['calibration_sample_not_independent_validation'])
   if measured['status']=='VISIBLE_SOLE_CONTOUR_MEASURED':
    uncertainty=o['uncertainty_px']
    if not np.isfinite(uncertainty) or uncertainty<0:raise ValueError('Invalid uncertainty')
    residual=measured['lower_contour_y_px']-measured['expected_sole_y_px']
    measured.update(signed_source_sole_residual_px=residual,source_ground_readability_warning=abs(residual)>spec['warning_budget_px']+uncertainty,
        contact_floor_warning=src['near_plane_candidate'] and abs(measured['lower_contour_y_px']-measured['expected_ground_y_px'])>spec['warning_budget_px']+uncertainty,
        uncertainty_px=uncertainty)
   row['observations'].append(measured)
  report['frames'].append(row)
 report['contact_warning_keys']=[r['source_key'] for r in report['frames'] if any(o.get('contact_floor_warning') for o in r['observations'])]
 report['inconclusive_keys']=[r['source_key'] for r in report['frames'] if any(o['status']!='VISIBLE_SOLE_CONTOUR_MEASURED' for o in r['observations'])]
 report['independent_contact_warning_keys']=[r['source_key'] for r in report['frames'] if any(o.get('contact_floor_warning') and not o.get('calibration_observation_not_validation') for o in r['observations'])]
 report['source_dense_summary']=source['summary'];return report

def initialize(frames_dir,source_path,scale,translation,budget):
 """Bind new pixels, starting with no sole or anatomical observations."""
 paths=sorted(Path(frames_dir).glob('*.png'));source=json.loads(Path(source_path).read_text())
 if not paths or len(paths)!=len(source['frames']):raise ValueError('New art must match the source phase count; export its own source first')
 if not all(np.isfinite(v) for v in [scale,translation,budget]) or scale<=0 or budget<0:raise ValueError('Invalid declared floor transform/budget')
 with Image.open(paths[0]) as im:canvas=list(im.size)
 rows=[]
 for k,path in enumerate(paths):
  with Image.open(path) as im:
   if list(im.size)!=canvas:raise ValueError('New frame canvases differ')
  rows.append({'source_key':k,'image':str(path),'sha256':sha(path),'soles':[{'side':side,'part':part,'roi_xyxy':None,'uncertainty_px':None,'identity_review':'unconfirmed','calibration_observation':False} for side in ['left','right'] for part in ['heel','toe']]})
 return {'schema':'painted-ground-observations-v1','source_ground_path':str(source_path),'source_ground_sha256':sha(source_path),'canvas':canvas,'shared_scale':scale,'shared_translation_y_px':translation,'warning_budget_px':budget,'frames':rows,'scope':'Unknown-first template. Declare a character-specific source/camera/scale. Inspect sole contours and proximal ownership before annotating. Unknown observations never approve contact.'}

def main():
 p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--observations',type=Path);mode.add_argument('--init-from-frames',type=Path);p.add_argument('--source',type=Path);p.add_argument('--shared-scale',type=float);p.add_argument('--shared-translation-y',type=float);p.add_argument('--warning-budget',type=float);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if a.init_from_frames:
  if a.out.exists():raise ValueError('Refusing to overwrite reviewed observations')
  if any(v is None for v in [a.source,a.shared_scale,a.shared_translation_y,a.warning_budget]):p.error('Initialization requires source, shared-scale, shared-translation-y and warning-budget')
  d=initialize(a.init_from_frames,a.source,a.shared_scale,a.shared_translation_y,a.warning_budget)
 else:d=audit(json.loads(a.observations.read_text()))
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(d,indent=2)+'\n');print('GROUND_REVIEW',d.get('status','UNKNOWN_FIRST_TEMPLATE'))
if __name__=='__main__':main()
