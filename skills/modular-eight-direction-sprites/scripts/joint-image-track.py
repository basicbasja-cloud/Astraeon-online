#!/usr/bin/env python3
"""Image-seeded point correspondence with explicit uncertainty/identity gates.
Tracks pixels after labelled seeds; NOT automatic semantic joint detection.
Unseeded future truth is never input. Explicit labelled keyframes may include
source-projected benchmark seeds; their use is disclosed and excluded from scoring.
"""
import argparse,hashlib,json,math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw

JOINTS=['head','neck','pelvis','right.shoulder','right.elbow','right.wrist','right.hip','right.knee','right.ankle','right.toe','left.shoulder','left.elbow','left.wrist','left.hip','left.knee','left.ankle','left.toe','grip','blade_tip']
DEFAULTS={'window':21,'levels':3,'min_eigen':0.0001,'fb_error_px':1.0,'ncc_min':0.65,'max_step_px':32.0,'patch_radius':7,'counterpart_collision_px':4.0}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load_case(path,root):
 c=json.loads(path.read_text());c['_case_sha256']=sha(path);images=[]
 if c.get('schema')!='sprite-image-joint-tracks-v1':raise ValueError('Wrong case schema')
 if not c['frames']:raise ValueError('Empty case')
 for i,f in enumerate(c['frames']):
  p=(root/f['path']).resolve()
  if not p.is_relative_to(root.resolve()):raise ValueError('Image outside root')
  if sha(p)!=f['sha256']:raise ValueError('Changed image binding')
  with Image.open(p) as im:rgba=np.array(im.convert('RGBA'))
  if [rgba.shape[1],rgba.shape[0]]!=c['canvas']:raise ValueError('Canvas drift; no per-frame fitting')
  if not math.isfinite(f['time_ms']) or not math.isfinite(f['duration_ms']) or f['duration_ms']<=0:raise ValueError('Invalid source clock')
  if i and abs(f['time_ms']-(c['frames'][i-1]['time_ms']+c['frames'][i-1]['duration_ms']))>1e-4:raise ValueError('Noncontinuous exposure clock')
  rgb=np.rint(rgba[:,:,:3]*(rgba[:,:,3:4]/255)+39*(1-rgba[:,:,3:4]/255)).astype(np.uint8)
  images.append({'gray':cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY),'rgba':rgba})
 for s in c.get('seeds',[]):
  if s['joint'] not in JOINTS or not 0<=s['frame']<len(images):raise ValueError('Bad seed joint/frame')
  if s['image_sha256']!=c['frames'][s['frame']]['sha256']:raise ValueError('Stale seed after image edit')
  if s['kind'] not in ('manual_visible','source_projected_benchmark'):raise ValueError('Estimated/unknown point cannot seed visible tracking')
  if len(s['xy'])!=2 or any(not math.isfinite(v) for v in s['xy']):raise ValueError('Invalid seed coordinates')
  x,y=s['xy'];w,h=c['canvas']
  if not (0<=x<w and 0<=y<h):raise ValueError('Seed outside canvas')
  if s.get('uncertainty_px') is not None and (not math.isfinite(s['uncertainty_px']) or s['uncertainty_px']<0):raise ValueError('Invalid seed uncertainty')
  if s['kind']=='manual_visible' and images[s['frame']]['rgba'][int(y),int(x),3]<128:raise ValueError('Visible seed on transparent background')
 for hidden in c.get('explicit_unknowns',[]):
  if hidden['joint'] not in JOINTS or not 0<=hidden['frame']<len(images) or hidden['image_sha256']!=c['frames'][hidden['frame']]['sha256']:raise ValueError('Invalid/stale hidden-point binding')
 return c,images

def patch(im,xy,radius):
 x,y=xy;h,w=im.shape
 if x-radius<0 or y-radius<0 or x+radius>=w or y+radius>=h:return None
 return cv2.getRectSubPix(im,(radius*2+1,radius*2+1),(float(x),float(y))).astype(np.float32)
def ncc(a,b):
 if a is None or b is None:return None
 a=a-a.mean();b=b-b.mean();norm=float(np.linalg.norm(a)*np.linalg.norm(b))
 return float((a*b).sum()/norm) if norm>1e-6 else None
def correspondence(a,b,xy,thresholds):
 p=np.array(xy,np.float32).reshape(1,1,2)
 params=dict(winSize=(thresholds['window'],thresholds['window']),maxLevel=thresholds['levels'],criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,40,0.001),minEigThreshold=thresholds['min_eigen'])
 q,ok,eigen=cv2.calcOpticalFlowPyrLK(a['gray'],b['gray'],p,None,flags=cv2.OPTFLOW_LK_GET_MIN_EIGENVALS,**params)
 if q is None or not ok[0,0]:return {'xy':None,'status':'unknown','reason':'low_texture_or_failed_forward_flow'}
 r,back,_=cv2.calcOpticalFlowPyrLK(b['gray'],a['gray'],q,None,**params)
 candidate=q[0,0].astype(float);h,w=b['gray'].shape
 if not np.isfinite(candidate).all() or not (0<=candidate[0]<w and 0<=candidate[1]<h):return {'xy':None,'status':'unknown','reason':'out_of_canvas'}
 fb=float(np.linalg.norm(r[0,0]-p[0,0])) if r is not None and back[0,0] else None
 score=ncc(patch(a['gray'],xy,thresholds['patch_radius']),patch(b['gray'],candidate,thresholds['patch_radius']))
 step=float(np.linalg.norm(candidate-np.array(xy)))
 foreground=int(b['rgba'][int(candidate[1]),int(candidate[0]),3])>127
 reasons=[]
 if fb is None or fb>thresholds['fb_error_px']:reasons.append('forward_backward_disagreement')
 if score is None or score<thresholds['ncc_min']:reasons.append('appearance_or_occlusion_disagreement')
 if step>thresholds['max_step_px']:reasons.append('large_step_requires_review')
 if not foreground:reasons.append('point_on_transparent_background')
 return {'xy':candidate.tolist(),'status':'proposal' if not reasons else 'untrusted','reason':','.join(reasons) if reasons else None,'fb_error_px':fb,'ncc':score,'step_px':step,'min_eigenvalue':float(eigen[0,0]),'independently_reviewed':False,'anatomical_identity_verified':False}

def track(case,images,thresholds=None):
 t=dict(DEFAULTS);t.update(thresholds or {});t.update(case.get('thresholds',{}));seeds={};hidden={(p['frame'],p['joint']) for p in case.get('explicit_unknowns',[])}
 for s in case.get('seeds',[]):
  k=(s['frame'],s['joint'])
  if k in seeds:raise ValueError('Duplicate seed')
  seeds[k]=s
 frames=[];active={}
 for i,img in enumerate(images):
  points={j:{'xy':None,'status':'unknown','reason':'no_valid_seed_or_previous_track','anatomical_identity_verified':False} for j in JOINTS}
  for j in JOINTS:
   if (i,j) in hidden:
    points[j].update(reason='explicit_image_occlusion_or_unknown');continue
   seed=seeds.get((i,j))
   if seed:
    points[j]={'xy':seed['xy'],'status':'seed','seed_kind':seed['kind'],'seed_uncertainty_px':seed.get('uncertainty_px'),'anatomical_identity_verified':seed.get('owner_confirmed',False) and seed['kind']=='manual_visible','independently_reviewed':seed['kind']=='manual_visible'}
   elif j in active and i:
    points[j]=correspondence(images[i-1],img,active[j],t)
  # Pixel tracking cannot resolve two limbs that collapse to the same support.
  for part in ('shoulder','elbow','wrist','hip','knee','ankle','toe'):
   right,left=points['right.'+part],points['left.'+part]
   if right['xy'] is not None and left['xy'] is not None and not (right['status']=='seed' and left['status']=='seed') and np.linalg.norm(np.array(right['xy'])-left['xy'])<t['counterpart_collision_px']:
    for point in (right,left):
     if point['status']!='seed':point.update(status='untrusted',reason='paired_owner_overlap_requires_review',anatomical_identity_verified=False)
  active={j:p['xy'] for j,p in points.items() if p['status'] in ('seed','proposal')}
  frames.append({'index':i,'image_sha256':case['frames'][i]['sha256'],'source_time_ms':case['frames'][i]['time_ms'],'reference_time_seconds':case['frames'][i].get('source_time_seconds'),'points':points})
 return {'schema':'image-correspondence-proposals-v1','case_sha256':case.get('_case_sha256'),'reference_source_sha256':case.get('source_sha256'),'opencv':cv2.__version__,'thresholds':t,'canvas':case['canvas'],'frames':frames,'semantic_joint_detector':False,'production_pass':False,'anatomy_pass':False,'accuracy_probability':None,'future_reference_coordinates_used':False,'scope':'Seeded image correspondences only. Numerical checks do not establish joint/limb identity. Unknown/occluded/lost points remain unapproved; reseed from independently inspected image.'}

def bidirectional(case,images):
 """Sparse labelled-keyframe assisted tracking; later unseeded truth is absent."""
 forward=track(case,images);t=forward['thresholds'];back_case=dict(case);n=len(images)
 back_case['seeds']=[dict(s,frame=n-1-s['frame']) for s in case.get('seeds',[])]
 back_case['explicit_unknowns']=[dict(s,frame=n-1-s['frame']) for s in case.get('explicit_unknowns',[])]
 back_case['frames']=list(reversed(case['frames']));backward=track(back_case,list(reversed(images)))
 seeds={(s['frame'],s['joint']) for s in case.get('seeds',[])};bound=t.get('endpoint_agreement_px',1.5)
 for i,frame in enumerate(forward['frames']):
  for name,point in frame['points'].items():
   if (i,name) in seeds:continue
   back=backward['frames'][n-1-i]['points'][name]
   if point['status']=='proposal' and back['status']=='proposal':
    error=float(np.linalg.norm(np.array(point['xy'])-back['xy']));point['endpoint_agreement_error_px']=error
    if error>bound:point.update(status='untrusted',reason='labelled_keyframe_bidirectional_disagreement')
    else:point['xy']=((np.array(point['xy'])+back['xy'])/2).tolist()
   elif point['status']=='proposal':point.update(status='untrusted',reason='missing_independent_backtrack')
 forward.update(mode='sparse_labelled_keyframe_bidirectional',labelled_seed_frames=sorted({s['frame'] for s in case['seeds']}),endpoint_agreement_px=bound,future_reference_coordinates_used=any(s['kind']=='source_projected_benchmark' and s['frame']>0 for s in case['seeds']),future_unseeded_truth_used=False,scope='Labelled-keyframe assisted image correspondence; benchmark source-projected seed frames explicitly supplied and excluded from evaluation. Not automatic semantic detection, anatomical identity or painted-art accuracy.')
 return forward

def grid_board(case,report,root,out):
 w,h=case['canvas'];columns=min(4,len(case['frames']));scale=min(1.0,320/max(w,h));dw,dh=round(w*scale),round(h*scale)
 board=Image.new('RGB',(columns*(dw+12),math.ceil(len(case['frames'])/columns)*(dh+35)),(31,35,45));d=ImageDraw.Draw(board)
 for i,f in enumerate(case['frames']):
  x=i%columns*(dw+12)+6;y=i//columns*(dh+35)+28
  with Image.open(root/f['path']) as im:rgba=im.convert('RGBA').resize((dw,dh),Image.Resampling.NEAREST)
  board.paste(rgba,(x,y),rgba)
  for gx in range(0,dw,round(32*scale) or 1):d.line((x+gx,y,x+gx,y+dh),fill=(70,75,82))
  for gy in range(0,dh,round(32*scale) or 1):d.line((x,y+gy,x+dw,y+gy),fill=(70,75,82))
  for name,p in report['frames'][i]['points'].items():
   if p['xy'] is None:continue
   px=x+p['xy'][0]*scale;py=y+p['xy'][1]*scale;color='#309aff' if name.startswith('right.') else '#ff9a32' if name.startswith('left.') else 'white'
   if p['status']=='untrusted':color='#ff4760'
   d.ellipse((px-3,py-3,px+3,py+3),outline=color,width=2)
  d.text((x,y-25),f"frame {i} / {f['time_ms']}ms; proposals",fill='white')
 board.save(out)
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--out',type=Path,required=True);p.add_argument('--bidirectional',action='store_true');a=p.parse_args()
 c,images=load_case(a.case,a.root);r=bidirectional(c,images) if a.bidirectional else track(c,images);a.out.mkdir(parents=True,exist_ok=True)
 (a.out/'tracks.json').write_text(json.dumps(r,indent=2)+'\n');grid_board(c,r,a.root,a.out/'grid-tracks.png');print(json.dumps({'frames':len(r['frames']),'proposal_points':sum(p['status']=='proposal' for f in r['frames'] for p in f['points'].values()),'anatomy_pass':False}))
if __name__=='__main__':main()
