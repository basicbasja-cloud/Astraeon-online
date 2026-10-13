"""Observe calibrated visible texture patches from RGBA frames, not hidden joints.
Only the first image, a fixed search window, and optional first-frame isolated
alpha mask calibrate matching. No later pose coordinates or predicted angles.
Rotation search is valid for this rigid texture family, not redraws/deformation.
"""
import argparse,hashlib,json
from pathlib import Path
import cv2,numpy as np
from PIL import Image
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read_bound(root,row):
 path=(root/row['path']).resolve()
 if not path.is_relative_to(root.resolve()) or sha(path)!=row['sha256']:raise ValueError('Changed/outside-root image')
 return np.array(Image.open(path).convert('RGBA'))
def match(frames,spec,isolated=None):
 x,y=spec['seed_xy'];hx,hy=spec['half_extent'];l,t,r,b=spec['search_box'];base=frames[0]
 if not(0<=x-hx<x+hx<base.shape[1] and 0<=y-hy<y+hy<base.shape[0]):raise ValueError('Invalid seed patch')
 if not(0<=l<r<=base.shape[1] and 0<=t<b<=base.shape[0]):raise ValueError('Invalid fixed search box')
 template=base[y-hy:y+hy+1,x-hx:x+hx+1,:3].astype('float32')
 alpha=(isolated if isolated is not None else base)[y-hy:y+hy+1,x-hx:x+hx+1,3]
 mask=(alpha>=128).astype('uint8')*255
 if (mask>0).sum()<30 or float(template[mask>0].std())<3:raise ValueError('Insufficient visible texture')
 H,W=mask.shape;lo,hi,step=spec['rotation_search_degrees'];bank=[]
 if r-l<W or b-t<H or step<=0 or hi<lo:raise ValueError('Invalid search geometry')
 for angle in range(lo,hi+1,step):
  matrix=cv2.getRotationMatrix2D((hx,hy),angle,1)
  bank.append((angle,cv2.warpAffine(template,matrix,(W,H)),cv2.warpAffine(mask,matrix,(W,H),flags=cv2.INTER_NEAREST)))
 result=[]
 for i,image in enumerate(frames):
  search=image[t:b,l:r,:3].astype('float32');best=(-1,None,None);maps=[]
  for angle,template_rot,mask_rot in bank:
   scores=cv2.matchTemplate(search,template_rot,cv2.TM_CCOEFF_NORMED,mask=mask_rot)
   scores[~np.isfinite(scores)]=-1;scores=np.clip(scores,-1,1);maps.append(scores)
   _,score,_,location=cv2.minMaxLoc(scores)
   if score>best[0]:best=(score,location,angle)
  if best[1] is None:
   result.append({'frame':i,'status':'unknown','xy':None,'ncc':None,'position_margin':None,'uncertainty_px':None,'anatomical_owner':'unknown','method':'no finite textured match; abstained'})
   continue
  score,(px,py),angle=best
  # Ambiguity across positions: nearby rotation alternatives are the same match.
  peak=np.maximum.reduce(maps);yy,xx=np.indices(peak.shape);peak[(xx-px)**2+(yy-py)**2<=spec['ambiguity_radius_px']**2]=-1
  second=float(peak.max());margin=score-second;xy=[l+px+hx,t+py+hy]
  visible=image[xy[1],xy[0],3]>=128
  known=visible and score>=spec['minimum_ncc'] and margin>=spec['minimum_margin']
  result.append({'frame':i,'status':'visible' if known else 'unknown','xy':xy if known else None,'ncc':score,'position_margin':margin,'rotation_search_match_degrees':angle,'uncertainty_px':2,'anatomical_owner':'unknown','method':'first-frame masked rotation-NCC; no later pose input'})
 return result
def observe(case,root):
 frames=[read_bound(root,r) for r in case['frames']]
 if any(list(a.shape[:2][::-1])!=case['canvas'] for a in frames):raise ValueError('Canvas drift')
 tracks={}
 for name,spec in case['patches'].items():
  isolated=read_bound(root,spec['isolated_first_frame']) if spec.get('isolated_first_frame') else None
  tracks[name]=match(frames,spec,isolated)
 return {'schema':'rigid-painted-surface-observer-v1','tracks':tracks,'later_pose_coordinates_used':False,'hidden_anatomy_detected':False,'scope':'Calibrated rigid texture patches in this part-rendered family. NCC is not an accuracy probability. Unknowns block downstream review.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 r=observe(json.loads(a.case.read_text()),a.root);r['case_sha256']=sha(a.case);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'retained':sum(p['status']=='visible' for v in r['tracks'].values() for p in v),'targets':sum(len(v) for v in r['tracks'].values())}))
if __name__=='__main__':main()
