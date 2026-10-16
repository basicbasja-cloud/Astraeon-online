"""Visible contour timing profile, not automatic anatomy recognition."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image
from scipy import ndimage
def evaluate(c,base):
 errors=[];observations=[]
 if len(c.get('frames',[]))<3:return {'motion_profile_pass':False,'failures':['insufficient_frames']}
 for i,f in enumerate(c['frames']):
  path=base/f['path']
  if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=f['sha256']:errors.append(['stale_or_missing_frame',i]);continue
  im=np.asarray(Image.open(path).convert('RGBA'));x0,y0,x1,y1=c['crown_window'];a=im[y0:y1,x0:x1,3]>=c.get('alpha',128);labels,n=ndimage.label(a);counts=np.bincount(labels.ravel());counts[0]=0;good=np.flatnonzero(counts>=c.get('min_component_area',100));mask=np.isin(labels,good)
  if not good.size:errors.append(['UNKNOWN_MISSING_CONTOUR',i]);continue
  y,x=np.where(mask);crown=int(y.min()+y0);xs=x[y<=y.min()+12]+x0
  observations.append({'index':i,'crown_y':crown,'top_band_mid_x':float((xs.min()+xs.max())/2)})
 if len(observations)!=len(c['frames']):return {'motion_profile_pass':False,'failures':errors,'observations':observations}
 y=np.array([r['crown_y'] for r in observations],dtype=float);d=np.array(c['durations'],dtype=float)
 if len(d)!=len(y) or not np.all(np.isfinite(d)) or min(d)<=0:return {'motion_profile_pass':False,'failures':['invalid_clock']}
 delta=np.diff(y);vel=delta/d[:-1]*1000;acc=np.diff(vel)/((d[:-2]+d[1:-1])/2000);p=c['profile'];peak=int(np.argmax(y));stated=c['peak_index_range'];checks={
  'max_visible_crown_step':float(abs(delta).max())<=p['max_step_px'],
  'max_visible_crown_speed':float(abs(vel).max())<=p['max_speed_px_s'],
  'max_visible_crown_acceleration':float(abs(acc).max())<=p['max_acceleration_px_s2'],
  'one_descent_without_reverse_bob':bool(np.all(delta[:peak]>=-p['reverse_slack_px'])),
  'one_recovery_without_reverse_bob':bool(np.all(delta[peak:]<=p['reverse_slack_px'])),
  'peak_in_declared_phase':stated[0]<=peak<=stated[1],
  'real_bend_not_frozen':p['min_excursion_px']<=float(y.max()-y.min())<=p['max_excursion_px'],
  'neutral_closes':abs(y[-1]-y[0])<=p['neutral_slack_px']}
 checks={k:bool(v) for k,v in checks.items()}
 return {'motion_profile_pass':bool(all(checks.values()) and not errors),'checks':checks,'measurements':{'max_step_px':float(abs(delta).max()),'max_speed_px_s':float(abs(vel).max()),'max_acceleration_px_s2':float(abs(acc).max()),'peak_index':peak,'excursion_px':float(y.max()-y.min())},'observations':observations,'velocity_px_s':vel.tolist(),'acceleration_px_s2':acc.tolist(),'failures':errors,'scope':'Authored pickup contour/phase profile, not joint detection, source equivalence or universal animation physics','production_pass':False}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('contract');ap.add_argument('--output');ap.add_argument('--require-motion',action='store_true');a=ap.parse_args();p=Path(a.contract);r=evaluate(json.loads(p.read_text()),p.parent)
 if a.output:Path(a.output).write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps({k:v for k,v in r.items() if k not in ['observations','velocity_px_s','acceleration_px_s2']}));raise SystemExit(int(a.require_motion and not r['motion_profile_pass']))
