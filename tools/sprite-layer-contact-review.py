"""Verify a rigid planted painted sole through known, independently rendered occluders.

Requires explicit source owners/foot windows. Never infers anatomy from colors.
Visible composite pixels and isolated sole pixels must both agree with neutral.
"""
from pathlib import Path
from PIL import Image
import numpy as np,hashlib,json,argparse
def evaluate(d,base):
 errors=[];rows=[];refs={};frames=d.get('frames',[]);windows=d.get('foot_windows',{});occluders=d.get('occluders',[])
 if not isinstance(frames,list) or len(frames)<3 or not isinstance(windows,dict) or not windows or not isinstance(occluders,list) or not occluders:return {'layer_contact_pass':False,'failures':['empty_contract']}
 if type(d.get('distal_band_px'))is not int or not 1<=d['distal_band_px']<=64:return {'layer_contact_pass':False,'failures':['invalid_distal_band']}
 if not all(isinstance(b,list) and len(b)==4 and all(type(v)is int for v in b) for b in windows.values()):return {'layer_contact_pass':False,'failures':['invalid_windows']}
 tolerance=d.get('rgba_rounding_budget',2)
 if type(tolerance)is not int or not 0<=tolerance<=2:return {'layer_contact_pass':False,'failures':['invalid_rounding_budget']}
 if not all(type(d.get(k)) in [int,float] and .5<=d[k]<=1 for k in ['min_visible_distal_fraction','min_visible_baseline_fraction']):return {'layer_contact_pass':False,'failures':['invalid_visibility_budget']}
 def read(f):
  p=base/f['path'];assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'],'stale_or_missing_input';im=Image.open(p);assert im.mode=='RGBA';return np.array(im).astype('int16')
 try:
  for i,r in enumerate(frames):
   whole=read(r['composite']);layers={n:read(f) for n,f in r['layers'].items()};assert all(a.shape==whole.shape for a in layers.values()),'canvas_mismatch'
   occ=np.maximum.reduce([layers[n][:,:,3] for n in occluders])>0
   for owner,box in windows.items():
    x0,y0,x1,y1=box;assert all(type(v)is int for v in box) and 0<=x0<x1<=whole.shape[1] and 0<=y0<y1<=whole.shape[0],'invalid_window';own=layers[owner][y0:y1,x0:x1];com=whole[y0:y1,x0:x1];obstructed=occ[y0:y1,x0:x1]
    if i==0:
     mask=own[:,:,3]>=128;yy,xx=np.where(mask);assert len(yy)>40 and yy.max()<mask.shape[0]-1 and xx.min()>0 and xx.max()<mask.shape[1]-1,'unknown_initial_sole';bottom=int(yy.max());distal=mask&(np.indices(mask.shape)[0]>=bottom-d['distal_band_px']+1);baseline=mask&(np.indices(mask.shape)[0]==bottom);refs[owner]=(own.copy(),distal,baseline)
    neutral,distal,baseline=refs[owner];assert own.shape==neutral.shape,'shape_mismatch';same=np.array_equal(own,neutral);visible=distal&~obstructed;floor=baseline&~obstructed;fraction=float(visible.sum()/distal.sum());floorfraction=float(floor.sum()/baseline.sum());pixel_ok=bool(np.max(np.abs(com[visible]-neutral[visible]),initial=0)<=tolerance);visible_ok=fraction>=d['min_visible_distal_fraction'] and floorfraction>=d['min_visible_baseline_fraction'];passed=bool(same and pixel_ok and visible_ok);rows.append({'frame':i,'owner':owner,'isolated_sole_pixels_exactly_neutral':same,'visible_composite_matches_neutral':pixel_ok,'visible_distal_fraction':fraction,'visible_baseline_fraction':floorfraction,'full_distal_sole_visible':bool(fraction==1),'pass':passed})
    if not passed:errors.append({'frame':i,'owner':owner,'kind':'sole_or_visible_contact_mismatch'})
 except (AssertionError,KeyError,ValueError,OSError,TypeError,IndexError) as e:errors.append(str(e))
 return {'layer_contact_pass':not errors,'observations':rows,'failures':errors,'production_pass':False,'scope':d.get('scope'),'hidden_anatomy_pass':None}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('case',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();r=evaluate(json.loads(a.case.read_text()),a.case.parent)
 if a.output:a.output.write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps({'layer_contact_pass':r['layer_contact_pass'],'failures':r['failures'],'min_visible_distal_fraction':min((x['visible_distal_fraction'] for x in r.get('observations',[])),default=None)}));raise SystemExit(not r['layer_contact_pass'])
