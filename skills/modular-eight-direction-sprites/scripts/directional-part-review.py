"""Bound authoring/image checks for a new view, never semantic anatomy certification."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def apply(m,p):return[m[0]*p[0]+m[2]*p[1]+m[4],m[1]*p[0]+m[3]*p[1]+m[5]]
def review(case,root):
 root=Path(root).resolve();checks=[]
 def check(n,ok):checks.append(dict(name=n,pass_=bool(ok)))
 def file(row):
  p=(root/row['path']).resolve()
  if not p.is_relative_to(root) or sha(p)!=row['sha256']:raise ValueError('Changed/missing/outside-root evidence: '+row['path'])
  return p
 bank=json.loads(file(case['bank']).read_text());bindings=json.loads(file(case['bindings']).read_text());poses=json.loads(file(case['poses']).read_text());source=json.loads(file(case['source']).read_text());old=json.loads(file(case['original_source']).read_text())
 check('same fresh physical source and unchanged source clip/phase times',source['source_sha256']==old['source_sha256'] and source['clip']==old['clip'] and [f['source_time_seconds'] for f in source['frames']]==[f['source_time_seconds'] for f in old['frames']])
 check('different physical camera, not reflected source skeleton',source['camera_world_matrix']!=old['camera_world_matrix'] and all(np.allclose(source['frames'][i]['points'][n]['world_xyz'],old['frames'][i]['points'][n]['world_xyz'],atol=1e-6) for i in range(len(poses)) for n in source['frames'][i]['points']))
 view=case['view'];parts={p['name']:p for p in bank['parts']}
 check('authored samples keep exact source clock',len(poses)==len(source['frames']) and all(q['source_time_seconds']==f['source_time_seconds'] for q,f in zip(poses,source['frames'])))
 check('every source asset has required view, no mirrored fallback',all(p['view']==view and not p['mirrored'] and sha(root/p['file'])==p['sha256'] for p in parts.values()))
 mechanical=[]
 for style,frames in case['styles'].items():
  check(style+' covers every source sample',len(frames)==len(poses)==len(bindings[style]))
  for i,(f,rows) in enumerate(zip(frames,bindings[style])):
   a=np.array(Image.open(file(f)).convert('RGBA'));check(f'{style}/{i} canvas',list(a.shape[:2][::-1])==case['canvas'])
   check(f'{style}/{i} exact required piece count',len(rows)==case['active_parts'][style] and len({r['name'] for r in rows})==len(rows))
   for r in rows:
    p=r['part'];m=r['matrix'];check(f'{style}/{i}/{r["name"]} bank/view/determinant',r['view']==view and p==parts.get(r['name']) and m[0]*m[3]-m[1]*m[2]>0)
    if r.get('joint_chain'):
     an,bn=r['joint_chain'];error=max(math.dist(apply(m,p['pivot']),poses[i]['joints'][an]),math.dist(apply(m,p['end']),poses[i]['joints'][bn]));mechanical.append(error)
     check(f'{style}/{i}/{r["name"]} endpoints and anatomical side',error<1e-6 and (not p['name'].startswith(('left.','right.')) or all(n.startswith(p['semantic_owner']+'.') for n in (an,bn))))
    elif r['name'].endswith('.foot'):
     owner=p['semantic_owner'];check(f'{style}/{i}/{r["name"]} authored ankle mount',math.dist(apply(m,p['pivot']),poses[i]['joints'][owner+'.ankle'])<1e-6)
   names=[r['name'] for r in rows];check(f'{style}/{i} far cloth/near right arm ordering',names.index('teal_panel')<names.index('torso')<names.index('right.forearm'))
   check(f'{style}/{i} thigh covers receiving shin rim',all(names.index(side+'.shin')<names.index(side+'.thigh') for side in ['left','right']))
 for i in range(len(poses)):
  rows0={r['name']:r for r in bindings['original'][i] if not r['name'].startswith(('head','hair.'))}
  for s in ['silver','bald']:check(f'{s}/{i} body rows unchanged by hair swap',rows0=={r['name']:r for r in bindings[s][i] if not r['name'].startswith(('head','hair.'))})
 for side in ['left','right']:
  for a,b in [('hip','knee'),('knee','ankle'),('shoulder','elbow'),('elbow','wrist')]:
   lengths=[math.dist(q['joints'][side+'.'+a],q['joints'][side+'.'+b]) for q in poses];check(side+'/'+a+'-'+b+' fixed length',max(lengths)-min(lengths)<1e-6)
 pixel=[]
 for i in range(len(poses)):
  arrays={s:np.array(Image.open(file(case['styles'][s][i])).convert('RGBA')) for s in case['styles']};masks={s:np.array(Image.open(file(case['head_passes'][s][i])).convert('RGBA'))[:,:,3]>0 for s in arrays}
  for s in ['silver','bald']:
   changed=int(np.any(arrays['original']!=arrays[s],axis=2)[~(masks['original']|masks[s])].sum());check(f'{s}/{i} actual body pixels outside head union unchanged',changed==0)
  head=next(r for r in bindings['bald'][i] if r['name']=='head.base');roi=Image.new('L',tuple(case['canvas']));ImageDraw.Draw(roi).polygon([tuple(apply(head['matrix'],p)) for p in case['eye_polygon_in_base_head']],fill=255);roi=np.array(roi.filter(ImageFilter.MinFilter(3)))>0
  eye=int(np.any(arrays['silver']!=arrays['bald'],axis=2)[roi].sum());check(f'{i} exposed eye pixels match bald base',roi.sum()>20 and eye==0)
  scalp=Image.new('L',tuple(case['canvas']));ImageDraw.Draw(scalp).polygon([tuple(apply(head['matrix'],p)) for p in case['scalp_polygon_in_base_head']],fill=255);scalp=np.array(scalp.filter(ImageFilter.MinFilter(3)))>0
  unchanged=float(np.all(arrays['silver']==arrays['bald'],axis=2)[scalp].mean());check(f'{i} defined scalp guide covered by actual hair pixels',unchanged<=case['max_uncovered_scalp_fraction'])
  pixel.append(dict(frame=i,eye_pixels=int(roi.sum()),eye_changed_pixels=eye,uncovered_scalp_fraction=unchanged))
 return dict(schema='directional-part-review-v1',checks=checks,numeric_view_check_pass=all(r['pass_'] for r in checks),failed_checks=[r['name'] for r in checks if not r['pass_']],max_bound_endpoint_error_px=max(mechanical),actual_head_pixel_checks=pixel,semantic_image_anatomy_accuracy_claim=False,production_pass=False,scope='Declared bank/kinematics and authored eye/scalp region pixel checks. Not automatic anatomy, skin segmentation, balance, eight-direction coverage or acting approval.')
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=review(json.loads(a.case.read_text()),a.root);a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['numeric_view_check_pass','failed_checks','max_bound_endpoint_error_px']}));raise SystemExit(0 if r['numeric_view_check_pass'] else 1)
if __name__=='__main__':main()
