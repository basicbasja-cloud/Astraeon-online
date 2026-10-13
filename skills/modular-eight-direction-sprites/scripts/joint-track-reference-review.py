#!/usr/bin/env python3
"""Compare actual image proposals to a separate bound source projection.
No auto-fit/owner relabeling. At overlaps it returns ambiguity, never certainty.
This flags disagreements; no hidden anatomy/semantic accuracy is inferred.
"""
import argparse,hashlib,json,math
from pathlib import Path
def audit(tracks,truth,budget=3,overlap=4):
 if len(tracks['frames'])!=len(truth['frames']):raise ValueError('Frame count mismatch')
 if not truth.get('source_sha256') or tracks.get('reference_source_sha256')!=truth.get('source_sha256'):raise ValueError('Source binding mismatch')
 if budget<=0 or overlap<=0:raise ValueError('Positive budgets required')
 rows=[];issues=[]
 for f,t in zip(tracks['frames'],truth['frames']):
  if f['index']!=t['index']:raise ValueError('Source/frame correspondence mismatch')
  if t.get('candidate_image_sha256')!=f['image_sha256']:raise ValueError('Stale candidate/reference image binding')
  if f.get('reference_time_seconds') is None or t.get('source_time_seconds') is None or abs(f['reference_time_seconds']-t['source_time_seconds'])>1e-6:raise ValueError('Source phase/time binding mismatch')
  observations=[]
  for name,p in f['points'].items():
   if name not in t['points'] or p.get('xy') is None:
    status='REFERENCE_UNAVAILABLE' if name not in t['points'] else 'TRACK_UNAVAILABLE'
    issues.append({'frame':f['index'],'joint':name,'status':status})
    observations.append({'joint':name,'status':status,'anatomical_identity_verified':False});continue
   ref=t['points'][name]['xy'];error=math.dist(p['xy'],ref);opposite=('left.'+name[6:]) if name.startswith('right.') else ('right.'+name[5:]) if name.startswith('left.') else None
   separation=math.dist(ref,t['points'][opposite]['xy']) if opposite in t['points'] else None
   swapped=math.dist(p['xy'],t['points'][opposite]['xy']) if opposite in t['points'] else None
   status='SOURCE_POINT_DISAGREEMENT' if error>budget else 'WITHIN_SOURCE_POINT_BUDGET'
   if separation is not None and separation<overlap:status='OWNER_AMBIGUOUS_AT_OVERLAP'
   elif swapped is not None and error>budget and swapped+budget<error:status='POSSIBLE_OWNER_OR_POSE_MISMATCH'
   if p.get('status') in ('unknown','untrusted'):status='TRACK_UNTRUSTED'
   if status!='WITHIN_SOURCE_POINT_BUDGET':issues.append({'frame':f['index'],'joint':name,'status':status})
   observations.append({'joint':name,'direct_error_px':error,'opposite_reference_error_px':swapped,'pair_reference_separation_px':separation,'status':status,'anatomical_identity_verified':p.get('anatomical_identity_verified',False)})
  rows.append({'index':f['index'],'points':observations})
 return {'schema':'bound-image-track-source-review-v1','frames':rows,'issues':issues,'budget_px':budget,'overlap_ambiguity_px':overlap,'production_pass':False,'anatomy_pass':False,'automatic_owner_labels_changed':False,'scope':'Same camera/canvas/phase source-projection adapter only. Numerical fit, near/far color or tracker correspondence is not limb identity/contact approval.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--tracks',type=Path,required=True);p.add_argument('--truth',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=audit(json.loads(a.tracks.read_text()),json.loads(a.truth.read_text()));r['tracks_sha256']=hashlib.sha256(a.tracks.read_bytes()).hexdigest();r['truth_sha256']=hashlib.sha256(a.truth.read_bytes()).hexdigest();a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'issues':len(r['issues']),'production_pass':False}))
if __name__=='__main__':main()
