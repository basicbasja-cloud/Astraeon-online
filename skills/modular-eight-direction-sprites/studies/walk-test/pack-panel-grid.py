"""Explicit shared-row registration of a nonuniform generated panel sheet.

One source pixel scale; one translation per authoring row; no per-frame fit or
anatomy painting. Panel boundaries and sole anchors must be inspected first.
Anchor observations cannot independently validate their own correction.
"""
import argparse,hashlib,importlib.util,json
from pathlib import Path
import numpy as np
from PIL import Image

def validate_panel_cuts(alpha,spec):
 width=spec['source_cell_width'];scale=spec['global_pixel_scale'];bounds=spec['raw_row_panel_bounds'];h,w=alpha.shape
 if not all(np.isfinite(v) for v in [width,scale]) or min(width,scale)<=0:raise ValueError('Invalid shared scale or panel width')
 if abs(width*4-w)>1e-6 or len(bounds)!=5 or bounds[0]!=0 or bounds[-1]!=h or any(not isinstance(v,int) for v in bounds) or any(b<=a for a,b in zip(bounds,bounds[1:])):raise ValueError('Panel boundaries do not cover this 4x4 sheet')
 cuts=[int(alpha[y-1:y+1].max()) for y in bounds[1:-1]]+[int(alpha[:,round(i*width)-1:round(i*width)+1].max()) for i in range(1,4)]
 if max(cuts)>64:raise ValueError('Panel cut crosses foreground; cannot recover by deleting content')
 if sorted(a['row'] for a in spec['anchors'])!=list(range(4)):raise ValueError('Exactly one common registration anchor per row is required')
 return cuts

def main():
 p=argparse.ArgumentParser();p.add_argument('--spec',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--grid',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
 if a.grid.exists() or a.receipt.exists():raise ValueError('Fresh outputs required')
 spec=json.loads(a.spec.read_text());source=json.loads(a.source.read_text());loader=importlib.util.spec_from_file_location('ground',Path(__file__).parents[2]/'scripts/ground-contact.py');ground=importlib.util.module_from_spec(loader);loader.loader.exec_module(ground)
 with Image.open(spec['raw']) as opened:raw=opened.convert('RGBA')
 cut_alpha=validate_panel_cuts(np.array(raw)[:,:,3],spec)
 scale=spec['global_pixel_scale'];width=spec['source_cell_width'];xpad=(512-width*scale)/2
 source_scale,source_ty=spec['source_floor_display_transform']
 if not all(np.isfinite(v) for v in [source_scale,source_ty]) or source_scale<=0:raise ValueError('Invalid declared source display transform')
 board=Image.new('RGBA',(2048,2048));rows=[]
 for anchor in spec['anchors']:
  observed=ground.sole_pixels(spec['raw'],anchor['roi_xyxy'],list(raw.size))
  if observed['status']!='VISIBLE_SOLE_CONTOUR_MEASURED':raise ValueError('Unusable row sole anchor')
  src=source['frames'][anchor['source_key']]['soles'][f"sole.{anchor['side']}.{anchor['part']}"]
  if not src['near_plane_candidate']:raise ValueError('Anchor is a released source sole, not a ground candidate')
  expected=source_scale*src['lowest_xy'][1]+source_ty;origin=observed['lower_contour_y_px']-expected/scale
  row=anchor['row'];start,end=spec['raw_row_panel_bounds'][row:row+2]
  rows.append({'row':row,'raw_y_origin':origin,'source_key':anchor['source_key'],'observed_anchor_y':observed['lower_contour_y_px'],'target_anchor_y':expected,'calibration_sample_not_validation':True})
  for col in range(4):
   # Isolate a complete panel before the common row transform, so a neighboring
   # row cannot leak into the expanded logical canvas. No foreground deletion.
   bounds=(round(col*width),start,round((col+1)*width),end);panel=raw.crop(bounds)
   transform=(1/scale,0,-xpad/scale,0,1/scale,origin-start)
   frame=panel.transform((512,512),Image.Transform.AFFINE,transform,resample=Image.Resampling.BICUBIC)
   alpha=np.array(frame)[:,:,3]
   if max(alpha[0].max(),alpha[-1].max(),alpha[:,0].max(),alpha[:,-1].max())>64:raise ValueError('Registration clips a figure')
   board.alpha_composite(frame,(col*512,row*512))
 a.grid.parent.mkdir(parents=True,exist_ok=True);board.save(a.grid)
 receipt={'schema':'shared-panel-row-registration-v1','spec_sha256':ground.sha(a.spec),'raw_sha256':ground.sha(spec['raw']),'source_ground_sha256':ground.sha(a.source),'output_grid_sha256':ground.sha(a.grid),'global_pixel_scale':scale,'shared_x_padding':xpad,'source_floor_display_transform':[source_scale,source_ty],'panel_cut_max_alpha':cut_alpha,'rows':rows,'per_frame_fit':False,'anatomy_painted':False,'world_contact_verified':False,'scope':'Row registration study only. Individual pose proportions, identities and holdout contact observations require fresh review.'}
 a.receipt.write_text(json.dumps(receipt,indent=2)+'\n');print('PANEL_GRID 16 frames / shared scale / four explicitly calibrated row translations')
if __name__=='__main__':main()
