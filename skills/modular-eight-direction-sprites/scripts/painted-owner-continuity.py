"""Enforce SHA-bound image-side ownership reviews across animation exposures.

The points/owner judgements are explicit manual observations, not automatic
anatomical detection. Missing/occluded evidence is UNKNOWN and cannot pass.
Known rejected RGBA pixels cannot be repaired by changing their owner label.
"""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pixels(im):return hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
def audit(c,root,negatives):
 root=Path(root);im=Image.open(root/c['atlas']['path']).convert('RGBA');bound=sha(root/c['atlas']['path'])==c['atlas']['sha256'];rows=[]
 for f in c['frames']:
  frame=im.crop(tuple(f['atlas_box']));obs=f.get('review');ph=pixels(frame);negative=next((n for n in negatives['negative_frames'] if n['rgba_pixel_sha256']==ph),None);known=obs is not None and obs.get('status')=='OBSERVED_CURRENT_PIXELS';alpha=np.array(frame.getchannel('A'));on_surface=True
  if known:
   known &= len(obs.get('visible_chain',[]))>=2
   for point in obs.get('visible_chain',[]):
    x,y=point['xy'];r=point.get('uncertainty_px',3);x0,x1=max(0,int(x-r)),min(frame.width,int(x+r+1));y0,y1=max(0,int(y-r)),min(frame.height,int(y+r+1));on_surface &= x0<x1 and y0<y1 and bool((alpha[y0:y1,x0:x1]>=128).any())
   known &= obs.get('rgba_pixel_sha256')==ph and on_surface
  actual=obs.get('holding_owner') if known else None;expected='right' if c['grasp_index']<=f['index']<c['store_index'] else 'none'
  status='REJECTED_KNOWN_PIXELS' if negative else 'UNKNOWN' if not known else 'PASS_OWNER_REVIEW' if actual==expected else 'FAIL_OWNER_REVIEW'
  rows.append(dict(index=f['index'],rgba_pixel_sha256=ph,status=status,expected_holding_owner=expected,observed_holding_owner=actual,reviewed_points_touch_current_foreground=bool(on_surface),known_rejection=negative))
 held=[r for r in rows if c['grasp_index']<=r['index']<c['store_index']];changes=[]
 for a,b in zip(held,held[1:]):
  if a['observed_holding_owner'] is not None and b['observed_holding_owner'] is not None and a['observed_holding_owner']!=b['observed_holding_owner']:changes.append([a['index'],b['index']])
 checks=dict(current_atlas_hash=bound,eight_required_exposures=[f['index'] for f in c['frames']]==list(range(8)),all_required_held_frames_reviewed=bool(held) and all(r['status']=='PASS_OWNER_REVIEW' for r in held),no_known_rejected_pixels=not any(r['known_rejection'] for r in rows),no_observed_holding_owner_swap=not changes)
 return dict(checks=checks,frames=rows,observed_owner_changes=changes,temporal_owner_review_pass=all(checks.values()),scope='Manual image-side topology/owner observations with current-pixel binding and temporal enforcement. Not an automatic joint/hand/arm detector; on-alpha points do not establish their anatomical meaning. UNKNOWN/new drawings require fresh review.',production_pass=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--contract',type=Path,required=True);p.add_argument('--negatives',type=Path,required=True);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--out',type=Path,required=True);p.add_argument('--require-owner-review',action='store_true');a=p.parse_args();q=audit(json.loads(a.contract.read_text()),a.root,json.loads(a.negatives.read_text()));a.out.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q['checks']));return int(a.require_owner_review and not q['temporal_owner_review_pass'])
if __name__=='__main__':raise SystemExit(main())
