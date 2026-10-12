"""SHA-bound integer capture registration; no limb editing or pose fitting.

Source-assisted head mode is a surface calibration, never a recovered root.
Contact mode requires separately reviewed actual-pixel support landmarks.
Always preserves known issues and keeps calibration separate from validation.
"""
import hashlib, json, math
from pathlib import Path
import numpy as np
from PIL import Image

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def integer_translate(image,dy,alpha_noise_floor=1,dx=0):
 if not isinstance(dy,int) or not isinstance(dx,int):raise ValueError('Integer displacement required; no resampling')
 a=np.array(image.convert('RGBA'));solid=a[:,:,3]>alpha_noise_floor
 ys,xs=np.where(solid)
 if len(ys)==0:raise ValueError('No measured foreground')
 if ys.min()+dy<0 or ys.max()+dy>=a.shape[0] or xs.min()+dx<0 or xs.max()+dx>=a.shape[1]:raise ValueError('Registration would clip foreground; enlarge shared canvas first')
 # Provider leaves faint alpha=1 noise across empty gutters; explicit matte only.
 a[a[:,:,3]<=alpha_noise_floor]=0
 out=np.zeros_like(a)
 h,w=a.shape[:2];x0=max(0,-dx);x1=min(w,w-dx);y0=max(0,-dy);y1=min(h,h-dy)
 out[y0+dy:y1+dy,x0+dx:x1+dx]=a[y0:y1,x0:x1]
 return Image.fromarray(out),int((solid).sum())

def offsets(observed_y,expected_y):
 if len(observed_y)!=len(expected_y) or len(observed_y)<3:raise ValueError('Observation/source coverage differs')
 if not all(math.isfinite(v) for v in observed_y+expected_y):raise ValueError('Finite bound points required')
 # Calibrate constant feature-to-joint offset at first exposure; expected delta
 # follows actual source acting, rather than setting all heads to one height.
 target=[observed_y[0]+y-expected_y[0] for y in expected_y]
 delta=[round(y-o) for o,y in zip(observed_y,target)]
 return delta,target

def register(case,source_records,report,outdir):
 if report['case_sha256']!=sha(case['case_path']):raise ValueError('Stale input motion report')
 if report['surface_region']['status']!='DECLARED_PALETTE_REGION_MEASURED':raise ValueError('Surface observation inconclusive')
 fs=case['frames'];probe=report['surface_region']['frames']
 if len(fs)!=len(source_records) or len(fs)!=len(probe):raise ValueError('Coverage mismatch')
 for i,(f,r) in enumerate(zip(fs,source_records)):
  if sha(f['image'])!=f['sha256'] or f['key']!=i or r['key']!=i or f['source_key16']!=r['source_key16']:raise ValueError('Changed image or source phase')
 expected=[r['bones']['Head']['xy'][1] for r in source_records];observed=[r['centroid_px'][1] for r in probe];dy,targets=offsets(observed,expected)
 expected_x=[r['bones']['Head']['xy'][0] for r in source_records];observed_x=[r['centroid_px'][0] for r in probe];dx,targets_x=offsets(observed_x,expected_x)
 outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True);rows=[]
 for i,f in enumerate(fs):
  im,count=integer_translate(Image.open(f['image']),dy[i],dx=dx[i]);p=outdir/f'{i:02}.png';im.save(p)
  rows.append({'key':i,'source_key16':f['source_key16'],'input':f['image'],'input_sha256':f['sha256'],'output':str(p),'output_sha256':sha(p),'integer_translation_xy':[dx[i],dy[i]],'source_head_xy':[expected_x[i],expected[i]],'observed_hair_xy':[observed_x[i],observed[i]],'calibrated_target_hair_xy':[targets_x[i],targets[i]],'retained_foreground_pixels':count,'inherited_review_issues':f.get('review_issues',[])})
 return {'schema':'integer-source-surface-registration-v1','mode':'SOURCE_ASSISTED_XY_CAPTURE_REGISTRATION','canvas':case['canvas'],'shared_scale':1,'horizontal_motion_changed':True,'root_recovered':False,'anatomy_repaired':False,'contacts_verified':False,'alpha_noise_floor':1,'pixels_above_noise_floor_preserved_without_resampling':True,'rows':rows,'scope':'Corrects image-space XY registration to the actual source Head trajectory using first-exposure hair-to-joint calibration. Does not prove a physical root, floor contact, anatomical correctness, inter-facing size or motion appeal.'}
