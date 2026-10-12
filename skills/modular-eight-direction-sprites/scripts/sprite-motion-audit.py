"""Image-derived temporal diagnostics plus explicit source/semantic review gates.

No metric is a naturalness score. Optical-flow warping is measurement-only;
original RGBA masters are never aligned, repaired, relabeled or rewritten.
"""
import argparse, hashlib, importlib.util, json, math
from pathlib import Path
import numpy as np
from PIL import Image

FACINGS=['S','SE','E','NE','N','NW','W','SW']

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def module(name):
 p=Path(__file__).with_name(name+'.py');s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def axis_metrics(points,durations,loop,budgets):
 p=np.asarray(points,float);dt=np.asarray(durations,float)/1000
 if len(p)<3 or len(p)!=len(dt) or p.shape[1:]!=(2,) or not np.isfinite(p).all() or not np.isfinite(dt).all() or np.any(dt<=0):raise ValueError('Invalid temporal points/clock')
 if any(not isinstance(v,(float,int)) or not math.isfinite(v) or v<0 for v in budgets.values()):raise ValueError('Invalid axis warning budget')
 delta=np.roll(p,-1,axis=0)-p if loop else np.diff(p,axis=0)
 velocity=delta/(dt if loop else dt[:-1])[:,None]
 dv=velocity-np.roll(velocity,1,axis=0) if loop else np.diff(velocity,axis=0)
 centers=(dt+np.roll(dt,1))/2 if loop else (dt[:-2]+dt[1:-1])/2
 acceleration=dv/centers[:,None]
 flags=[]
 for i,(dx,dy) in enumerate(delta):
  if abs(dx)>budgets['max_horizontal_step_px']:flags.append({'from':i,'to':(i+1)%len(p),'kind':'horizontal_step','value_px':float(abs(dx))})
  if abs(dy)>budgets['max_vertical_step_px']:flags.append({'from':i,'to':(i+1)%len(p),'kind':'vertical_bounce_candidate','value_px':float(abs(dy))})
 return {'xy':p.tolist(),'delta_xy_px':delta.tolist(),'velocity_xy_px_s':velocity.tolist(),
  'acceleration_xy_px_s2':acceleration.tolist(),'vertical_range_px':float(np.ptp(p[:,1])),
  'max_vertical_step_px':float(abs(delta[:,1]).max()),'max_horizontal_step_px':float(abs(delta[:,0]).max()),
  'last_to_first_xy_px':delta[-1].tolist() if loop else None,'warnings':flags,
  'vertical_range_warning':bool(np.ptp(p[:,1])>budgets['max_vertical_range_px'])}

def flow_metrics(frames,loop,settings):
 try:import cv2
 except ImportError:return {'status':'DEPENDENCY_MISSING','anatomy_pass':False}
 if settings['diagnostic_size']<64 or settings['diagnostic_size']>512:raise ValueError('Invalid diagnostic resolution')
 n=settings['diagnostic_size'];arrays=[]
 for f in frames:
  with Image.open(f['image']) as im:a=np.array(im.convert('RGBA').resize((n,n),Image.Resampling.BILINEAR))
  arrays.append(a)
 yy,xx=np.mgrid[:n,:n].astype(np.float32);rows=[]
 for i in range(len(arrays) if loop else len(arrays)-1):
  j=(i+1)%len(arrays);a,b=arrays[i],arrays[j]
  gray=lambda x:cv2.cvtColor(np.rint(x[:,:,:3].astype(float)*(x[:,:,3:4]/255)+39*(1-x[:,:,3:4]/255)).astype(np.uint8),cv2.COLOR_RGB2GRAY)
  fw=cv2.calcOpticalFlowFarneback(gray(a),gray(b),None,.5,3,21,3,5,1.2,0)
  bw=cv2.calcOpticalFlowFarneback(gray(b),gray(a),None,.5,3,21,3,5,1.2,0)
  tx=xx+fw[:,:,0];ty=yy+fw[:,:,1]
  back=cv2.remap(bw,tx,ty,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
  residual=np.linalg.norm(fw+back,axis=2)
  alpha=cv2.remap(b[:,:,3],tx,ty,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
  fg=a[:,:,3]>128
  valid=fg&(alpha>128)&(tx>=0)&(tx<n-1)&(ty>=0)&(ty<n-1)&(residual<=settings['max_forward_backward_error_px'])
  coverage=float(valid.sum()/max(1,fg.sum()))
  row={'from':i,'to':j,'loop_seam':j==0,'consistent_foreground_fraction':coverage,'status':'INCONCLUSIVE'}
  if coverage>=settings['minimum_consistent_fraction'] and valid.sum()>32:
   warped=cv2.remap(b[:,:,:3],tx,ty,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
   err=np.mean(np.abs(a[:,:,:3].astype(float)-warped.astype(float)),axis=2)
   row.update(status='SCOPED_FLOW_DIAGNOSTIC',photometric_mae_255=float(err[valid].mean()),
      p95_photometric_error_255=float(np.percentile(err[valid],95)),median_flow_xy_diagnostic_px=np.median(fw[valid],axis=0).tolist())
  rows.append(row)
 return {'status':'SCOPED_FLOW_DIAGNOSTIC' if all(r['status']=='SCOPED_FLOW_DIAGNOSTIC' for r in rows) else 'INCONCLUSIVE',
  'diagnostic_size':[n,n],'opencv':cv2.__version__,'edges':rows,'original_images_modified':False,'anatomy_pass':False,
  'scope':'Farneback forward/backward consistency masks uncertain/occluded pixels. Low warp error does not establish correct pose, limb identity, contact or naturalness.'}

def audit(case):
 fs=case['frames'];size=case['canvas'];loop=case['loop'];duration=[f['duration_ms'] for f in fs]
 if case['facing'] not in FACINGS or len(fs)<3:raise ValueError('Invalid facing/frame count')
 for i,f in enumerate(fs):
  if f['key']!=i or not math.isfinite(f['duration_ms']) or f['duration_ms']<=0:raise ValueError('Invalid frame order/clock')
  if sha(f['image'])!=f['sha256']:raise ValueError('Changed artwork requires fresh review')
  with Image.open(f['image']) as im:
   if list(im.size)!=size:raise ValueError('Mixed canvas')
 source=case['source'];path=Path(source['path'])
 if sha(path)!=source['sha256']:raise ValueError('Changed actual source index')
 idx=json.loads(path.read_text())
 for b in ['blend','motion']:
  if sha(idx[b]['path'])!=idx[b]['sha256']:raise ValueError('Changed source rig/action')
 records=[r for r in idx['records'] if r['facing']==case['facing']]
 if len(records)!=len(fs):raise ValueError('Source pose coverage differs')
 for i,(f,r) in enumerate(zip(fs,records)):
  if r['key']!=i or f['source_key16']!=r['source_key16']:raise ValueError('Wrong source phase')
  for name,p in r['paths'].items():
   if sha(p)!=r['sha256'][name]:raise ValueError('Changed source owner image')
  f.get('anatomical_review',{}) # Presence is not a semantic approval.
 probe_case={'canvas':size,'frames':fs,'loop':loop,'palette_patch_probe':case['palette_patch_probe']}
 probe=module('walk-continuity').palette_patch_probe(probe_case);axis=None;blockers=[]
 if probe['status']=='DECLARED_PALETTE_REGION_MEASURED':
  axis=axis_metrics([r['centroid_px'] for r in probe['frames']],duration,loop,case['budgets'])
  if axis['warnings'] or axis['vertical_range_warning']:blockers.append('visible_surface_bounce_or_registration_warning')
 else:blockers.append('visible_surface_measurement_inconclusive')
 history_binding=case['review_history']
 if sha(history_binding['path'])!=history_binding['sha256']:raise ValueError('Changed image review history')
 history=json.loads(Path(history_binding['path']).read_text())
 known=[]
 for f in fs:
  for issue in f.get('review_issues',[]):
   if issue['confirmed']:known.append({'key':f['key'],'image_sha256':f['sha256'],**issue})
  for issue in history['issues']:
   if issue['image_sha256']==f['sha256'] and issue['facing']==case['facing'] and issue['source_key16']==f['source_key16']:
    match={'key':f['key'],**issue}
    if not any(x.get('image_sha256')==f['sha256'] and x.get('kind')==issue['kind'] for x in known):known.append(match)
  # A semantic pass requires image traces for both proximal chains, not color labels.
  review=f.get('anatomical_review',{})
  if review.get('status')=='confirmed':
   if review.get('r',{}).get('trace_xy') == review.get('l',{}).get('trace_xy'):raise ValueError('Two anatomical sides cannot share an identical proximal trace')
   for side in ['r','l']:
    evidence=review.get(side,{})
    if evidence.get('kind') not in ('visible_junction','reviewed_occlusion') or len(evidence.get('trace_xy',[]))<3:
     raise ValueError('Confirmed identity requires actual proximal image evidence')
    with Image.open(f['image']) as im:a=np.array(im.convert('RGBA'))
    points=np.asarray(evidence['trace_xy'],float)
    if points.ndim!=2 or points.shape[1]!=2 or not np.isfinite(points).all() or np.any(points<0) or np.any(points[:,0]>=size[0]) or np.any(points[:,1]>=size[1]):raise ValueError('Proximal trace outside image')
    samples=np.concatenate([np.linspace(x,y,24) for x,y in zip(points,points[1:])]);coords=np.rint(samples).astype(int)
    if np.mean(a[coords[:,1],coords[:,0],3]>128)<.8:raise ValueError('Proximal trace lacks painted-pixel support')
 if known:blockers.append('confirmed_actual_image_issue')
 unresolved=[f['key'] for f in fs if f.get('anatomical_review',{}).get('status')!='confirmed']
 if unresolved:blockers.append('proximal_anatomical_continuity_unresolved')
 # This source is an approximate comparison to observed RO poses, never an exact recovered RO rig.
 if source['correspondence']!='exact_original_source':blockers.append('source_to_painted_pose_correspondence_approximate')
 if any(f.get('logical_root_observed_xy') is None for f in fs):blockers.append('painted_logical_root_unresolved')
 if any(f.get('contact_review')!='confirmed' for f in fs):blockers.append('painted_floor_contacts_unresolved')
 if not case.get('complete_parts_adapter'):blockers.append('complete_painted_parts_not_supplied')
 source_head=axis_metrics([r['bones']['Head']['xy'] for r in records],duration,loop,case['budgets'])
 flow=flow_metrics(fs,loop,case['flow_settings']) if case.get('flow_settings') else {'status':'NOT_REQUESTED'}
 if flow['status']=='INCONCLUSIVE':blockers.append('flow_tracking_inconclusive')
 return {'schema':'sprite-motion-audit-v1','facing':case['facing'],'frame_count':len(fs),'duration_ms':sum(duration),
   'status':'REJECTED' if known else 'REVIEW_REQUIRED','production_ready':False,
   'surface_region':probe,'surface_axis_metrics':axis,'actual_source_head_metrics':source_head,'flow':flow,
   'source_known_bone_samples':len(records),'unresolved_anatomy_keys':unresolved,'confirmed_image_issues':known,'blockers':blockers,
   'source_native_cycle_ms':idx['duration_seconds']*1000,'source_metrics_clock_scope':'Actual original source coordinates sampled at recorded source times; temporal derivatives above use the selected comparison exposures, not native source cadence.',
   'anatomy_accuracy_percent':None,'naturalness_score':None,'world_support_verified':False,
   'scope':'Surface step/bounce and flow are independent temporal diagnostics. Source bones are actual original rig; RO/painter correspondence is approximate. Unknown hips/root/contact and new art never get PASS.'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--require-production',action='store_true');a=p.parse_args();r=audit(json.loads(a.case.read_text()));r['case_sha256']=sha(a.case);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+'\n');print('MOTION_AUDIT',r['facing'],r['status'],r['blockers']);
 if a.require_production:raise SystemExit(2)

if __name__=='__main__':main()
