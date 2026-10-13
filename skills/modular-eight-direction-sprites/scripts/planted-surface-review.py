"""Bound visible surface trajectories versus declared planted-source policy.
Manual observations have uncertainty; static surfaces do not prove world contact.
"""
import argparse,hashlib,json,math
from pathlib import Path
from PIL import Image
def audit(case,root):
 rows=case['frames'];issues=[];markers={};images=[]
 for i,f in enumerate(rows):
  if not math.isfinite(f['time_ms']) or not math.isfinite(f['duration_ms']) or f['duration_ms']<=0 or (i and abs(f['time_ms']-rows[i-1]['time_ms']-rows[i-1]['duration_ms'])>1e-4):raise ValueError('Invalid/noncontinuous exposure clock')
  path=(root/f['path']).resolve()
  if not path.is_relative_to(root.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest()!=f['sha256']:raise ValueError('Stale/outside-root image')
  with Image.open(path) as im:
   if list(im.size)!=case['canvas']:raise ValueError('Canvas drift')
   images.append(im.convert('RGBA'))
 for name,definition in case['surface_landmarks'].items():
  pts=[]
  for i,f in enumerate(rows):
   p=f.get('observations',{}).get(name)
   if not p or p.get('status')!='visible':pts.append(None);issues.append({'frame':i,'marker':name,'kind':'UNKNOWN_SURFACE'});continue
   xy=p['xy'];uncertainty=p['uncertainty_px']
   if any(not math.isfinite(v) for v in xy) or not math.isfinite(uncertainty) or uncertainty<0:raise ValueError('Invalid observation')
   x,y=xy;im=images[i]
   if not (0<=x<im.width and 0<=y<im.height) or im.getpixel((int(x),int(y)))[3]<128:raise ValueError('Visible observation is outside opaque-enough sprite')
   pts.append(xy)
  valid=[p for p in pts if p is not None]
  if not valid:continue
  ranges=[max(p[k] for p in valid)-min(p[k] for p in valid) for k in range(2)]
  steps=[{'from':i-1,'to':i,'distance_px':math.dist(pts[i-1],pts[i]),'velocity_px_s':math.dist(pts[i-1],pts[i])*1000/(rows[i]['time_ms']-rows[i-1]['time_ms'])} for i in range(1,len(pts)) if pts[i] and pts[i-1]]
  if definition['policy']=='planted_surface_proxy' and max(ranges)>case['planted_budget_px']:issues.append({'marker':name,'kind':'PLANTED_SURFACE_DRIFT','range_xy_px':ranges,'budget_px':case['planted_budget_px']})
  markers[name]={'range_xy_px':ranges,'adjacent_steps':steps,'observation_uncertainty_px':[f.get('observations',{}).get(name,{}).get('uncertainty_px') for f in rows],'anatomical_owner':'unknown'}
 phase=case.get('reference_phase')
 if phase:
  path=root/phase['source_file']
  if hashlib.sha256(path.read_bytes()).hexdigest()!=phase['source_sha256']:raise ValueError('Changed phase reference')
  reference=json.loads(path.read_text());name=phase['marker'];a,b=phase['calibration_frames'];axis=phase['axis'];candidate=[f.get('observations',{}).get(name) for f in rows];src=[f['points'][phase['source_joint']]['xy'][axis] for f in reference['frames']]
  if len(src)!=len(rows):raise ValueError('Phase frame mismatch')
  calibrated=all(candidate[i] and candidate[i].get('status')=='visible' for i in (a,b))
  den_src=src[b]-src[a];den_art=candidate[b]['xy'][axis]-candidate[a]['xy'][axis] if calibrated else 0
  if not calibrated or abs(den_src)<1 or abs(den_art)<1:issues.append({'kind':'INSUFFICIENT_PHASE_EXCURSION'})
  else:
   phase_rows=[]
   for i,p in enumerate(candidate):
    if not p or p.get('status')!='visible':continue
    if abs(reference['frames'][i]['source_time_seconds']-rows[i]['source_time_seconds'])>1e-6:raise ValueError('Source time correspondence mismatch')
    ref=(src[i]-src[a])/den_src;art=(p['xy'][axis]-candidate[a]['xy'][axis])/den_art;delta=abs(ref-art);heldout=i not in (a,b);phase_rows.append({'frame':i,'source_fraction':ref,'image_surface_fraction':art,'absolute_fraction_difference':delta,'held_out':heldout})
    if heldout and delta>phase['warning_fraction']:issues.append({'frame':i,'kind':'SOURCE_RELATIVE_PHASE_DISAGREEMENT','difference':delta})
   markers[name]['source_relative_phase']=phase_rows
 return {'schema':'bound-visible-surface-review-v1','markers':markers,'issues':issues,'numerical_surface_check_pass':not issues,'anatomy_pass':False,'contact_pass':False,'production_pass':False,'scope':'Single-reviewer visible-surface proxies, declared support budget and source-relative calibrated phase. Neither hidden joint truth nor detector accuracy/force/world contact. Calibration frames excluded from phase warning evaluation.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--out',type=Path,required=True);a=p.parse_args();c=json.loads(a.case.read_text());r=audit(c,a.root);r['case_sha256']=hashlib.sha256(a.case.read_bytes()).hexdigest();a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'issues':r['issues'],'production_pass':False}))
if __name__=='__main__':main()
