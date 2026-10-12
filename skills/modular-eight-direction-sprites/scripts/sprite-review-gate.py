"""A shared, image-bound review gate, not an automatic anatomy classifier.

Confirmed sequence errors override unrelated file/floor/continuity diagnostics.
New bytes start unreviewed. Actual fractional source phases remain authoritative.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read_source(path,expected):
 if sha(path)!=expected:raise ValueError('Stale authoritative source receipt')
 source=json.loads(Path(path).read_text())
 for stem in ['blend','motion']:
  if sha(source[stem+'_path'])!=source[stem+'_sha256']:raise ValueError('Stale authoritative '+stem)
 return source
def initialize(paths,source_path,keys,rejections):
 source=read_source(source_path,sha(source_path))
 if len(paths)!=len(keys) or not paths:raise ValueError('Artwork/source phase count mismatch')
 rows=[]
 for path,key in zip(paths,keys):
  if type(key)!=int or not 0<=key<len(source['frames']):raise ValueError('Invalid source phase key')
  with Image.open(path) as im:canvas=list(im.size)
  rows.append({'image':str(path),'sha256':sha(path),'canvas':canvas,'source_key':key,'source_sample_position':source['frames'][key]['source_sample_position'],'anatomy_review':{'left_proximal_chain':'unconfirmed','right_proximal_chain':'unconfirmed','paired_occlusion':'unconfirmed'},'notes':'No hidden joints or identity inferred from source, cloth color or floor score.'})
 return {'schema':'sprite-review-gate-case-v1','facing':source['facing'],'source_ground_path':str(source_path),'source_ground_sha256':sha(source_path),'rejection_receipts':[{'path':str(p),'sha256':sha(p)} for p in rejections],'frames':rows}
def audit(case):
 source=read_source(case['source_ground_path'],case['source_ground_sha256'])
 if case['facing']!=source['facing']:raise ValueError('Facing changed from authoritative source')
 rejected={}
 for binding in case['rejection_receipts']:
  path=binding['path']
  if sha(path)!=binding['sha256']:raise ValueError('Stale rejection receipt')
  receipt=json.loads(Path(path).read_text())
  if receipt['authority']!='user' or receipt['sequence_status']!='REJECTED':raise ValueError('Not a confirmed user sequence rejection')
  if receipt['source_ground_sha256']!=case['source_ground_sha256']:raise ValueError('Rejection belongs to another authoritative source')
  for f in receipt['frames']:
   if sha(f['image'])!=f['sha256']:raise ValueError('Changed rejected pixels')
   rejected.setdefault(f['sha256'],[]).append({'receipt':path,'scope':receipt['scope'],'user_message':receipt['user_message']})
 result=[];camera_inverse=np.linalg.inv(np.array(source['camera_matrix_world'],float))
 for f in case['frames']:
  if sha(f['image'])!=f['sha256']:raise ValueError('Changed candidate pixels require fresh review')
  key=f['source_key']
  if type(key)!=int or not 0<=key<len(source['frames']):raise ValueError('Invalid source phase key')
  phase=source['frames'][key]
  if f['source_sample_position']!=phase['source_sample_position']:raise ValueError('Fractional source sample changed or truncated')
  with Image.open(f['image']) as im:
   if list(im.size)!=f['canvas']:raise ValueError('Changed candidate canvas')
  depths={side:float(-(camera_inverse@np.array(phase['bones']['thigh_'+suffix]['world']+[1]))[2]) for side,suffix in [('left','l'),('right','r')]}
  errors=rejected.get(f['sha256'],[])
  status='REJECTED_SEQUENCE_MEMBER' if errors else 'REVIEWED_NOT_USER_APPROVED' if all(f['anatomy_review'].get(k)=='confirmed' for k in ['left_proximal_chain','right_proximal_chain','paired_occlusion']) else 'ANATOMY_REVIEW_REQUIRED'
  result.append({'image':f['image'],'sha256':f['sha256'],'source_key':key,'source_sample_position':phase['source_sample_position'],'source_hip_axis_depth':depths,'source_near_side':min(depths,key=depths.get),'status':status,'confirmed_sequence_errors':errors,'art_anatomy_inferred_from_source':False})
 return {'schema':'sprite-review-gate-report-v1','status':'REJECTED' if any(f['confirmed_sequence_errors'] for f in result) else 'REVIEW_REQUIRED','frames':result,'semantic_classifier_used':False,'floor_scores_can_override_rejection':False,'new_pixels_inherit_approval':False,'complete_anatomy_accepted':False,'production_ready':False,'scope':'Image-bound review-state gate. Rejected sequence members are blocked as a group, not a claim of separately observed hidden anatomy in each image. Source depth is source geometry only.'}
def main():
 p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--observations',type=Path);mode.add_argument('--init-from-frames',type=Path);p.add_argument('--source',type=Path);p.add_argument('--source-keys');p.add_argument('--rejection',type=Path,action='append',default=[]);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 if a.init_from_frames:
  if a.out.exists():raise ValueError('Refusing to overwrite review observations')
  if a.source is None or a.source_keys is None:p.error('Initialization requires --source and --source-keys (receipt phase keys)')
  value=initialize(sorted(a.init_from_frames.glob('*.png')),a.source,[int(k) for k in a.source_keys.split(',')],a.rejection)
 else:value=audit(json.loads(a.observations.read_text()))
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(value,indent=2)+'\n');print('SPRITE_REVIEW_GATE',value.get('status','UNKNOWN_FIRST_CASE'))
if __name__=='__main__':main()
