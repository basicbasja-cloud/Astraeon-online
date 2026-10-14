"""Bound actual RGBA replacement checks. Counterfactual head render is a declared
authoring pass, not a learned detector/segmentation proof or hidden joint truth.
"""
import argparse,hashlib,json
from pathlib import Path
import cv2,numpy as np
from PIL import Image
def bound(root,row):
 p=(root/row['path']).resolve()
 if not p.is_relative_to(root.resolve()) or hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:raise ValueError('Stale/outside-root replacement evidence')
 return p
def compare_pixels(base,candidate,basehead,newhead):
 if not(base.shape==candidate.shape==basehead.shape==newhead.shape):raise ValueError('Changed canvas')
 support=(basehead[:,:,3]>0)|(newhead[:,:,3]>0);diff=np.any(base!=candidate,axis=2)
 return {'changed_pixels_outside_head_pass_union':int((diff&~support).sum()),'changed_pixels_inside_head_union':int((diff&support).sum())}
def multiply(a,b):return [a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5]]
def review(case,root):
 checks=[];measurements={}
 def check(name,v):checks.append({'name':name,'pass':bool(v)})
 check('exact original source-driven pose file unchanged',bound(root,case['poses']).read_bytes()==bound(root,case['baseline_poses']).read_bytes())
 styles=case['styles'];check('complete original/silver/auburn/bald banks',set(styles)=={'original','silver','auburn','bald'} and all(len(v)==8 for v in styles.values()))
 bindings=json.loads(bound(root,case['bindings']).read_text());baseline_bindings=json.loads(bound(root,case['baseline_bindings']).read_text())['frames'];registration=json.loads(bound(root,case['registration']).read_text())['part_to_original_head_space'];parts={p['name']:p for p in json.loads(bound(root,case['parts']).read_text())['parts']}
 check('all four actual binding banks present',set(bindings)==set(styles))
 for p in parts.values():bound(root,p)
 for style,bank in bindings.items():
  if style not in styles or len(bank)!=8:raise ValueError('Incomplete binding bank')
  ok=True
  for i,rows in enumerate(bank):
   old=baseline_bindings[i]['rows'];head=next(r for r in old if r['name']=='head_hair');body={r['name']:r for r in old if r['name']!='head_hair'};hair_names=['head_hair'] if style=='original' else ['head.base'] if style=='bald' else [style+'.rear','head.base',style+'.front']
   expected=[n for r in old for n in (hair_names if r['name']=='head_hair' else [r['name']])]
   ok=ok and [r['name'] for r in rows]==expected
   for row in rows:
    name=row['name'];matrix=row['matrix'];ok=ok and matrix[0]*matrix[3]-matrix[1]*matrix[2]>0
    if name in body:ok=ok and matrix==body[name]['matrix'] and row['texture_sha256']==body[name]['texture_sha256']
    elif name=='head_hair':ok=ok and matrix==head['matrix'] and row['texture_sha256']==head['texture_sha256']
    else:ok=ok and name in hair_names and np.allclose(matrix,multiply(head['matrix'],registration[name]),rtol=0,atol=1e-8) and row['texture_sha256']==parts[name]['sha256']
  check('constant common head mount / depth order / unchanged body binds '+style,ok)
 for style,rows in styles.items():
  observations=[]
  for i,row in enumerate(rows):
   baseline=case['baseline_frames'][i];a=np.array(Image.open(bound(root,baseline)).convert('RGBA'));b=np.array(Image.open(bound(root,row)).convert('RGBA'));oldhead=np.array(Image.open(bound(root,styles['original'][i]['head_pass'])).convert('RGBA'));head=np.array(Image.open(bound(root,row['head_pass'])).convert('RGBA'))
   if a.shape!=(case['canvas'][1],case['canvas'][0],4):raise ValueError('Canvas drift')
   measurements_row=compare_pixels(a,b,oldhead,head);observations.append(measurements_row)
   check('clock identity '+style+' frame'+str(i),row['source_time_seconds']==baseline['source_time_seconds'] and row['time_ms']==baseline['time_ms'] and row['duration_ms']==baseline['duration_ms'])
   mask=b[:,:,3]>=128;check('no foreground clipping '+style+' frame'+str(i),not(mask[0].any() or mask[-1].any() or mask[:,0].any() or mask[:,-1].any()))
  measurements[style]=observations;check('actual body pixels unchanged outside head passes '+style,all(r['changed_pixels_outside_head_pass_union']==0 for r in observations))
  if style=='original':check('comparison replays exact entire v32 RGBA frames',all(r['changed_pixels_inside_head_union']==0 for r in observations))
 heads={s:np.array(Image.open(bound(root,r)).convert('RGBA')) for s,r in case['head_previews'].items()};l,t,r,b=case['protected_eye_roi'];eye=heads['bald'][t:b,l:r]
 check('same visible purple-eye pixels in silver/auburn/bald rest previews',np.array_equal(eye,heads['silver'][t:b,l:r]) and np.array_equal(eye,heads['auburn'][t:b,l:r]))
 eye_rows=[]
 for i,rows in enumerate(bindings['original']):
  matrix=next(row['matrix'] for row in rows if row['name']=='head_hair');corners=np.array([[matrix[0]*x+matrix[2]*y+matrix[4],matrix[1]*x+matrix[3]*y+matrix[5]] for x,y in [(l,t),(r,t),(r,b),(l,b)]])
  mask=np.zeros((case['canvas'][1],case['canvas'][0]),dtype='uint8');cv2.fillConvexPoly(mask,np.rint(corners).astype('int32'),255);mask=cv2.erode(mask,np.ones((3,3),dtype='uint8'))>0
  images=[np.array(Image.open(bound(root,styles[s][i])).convert('RGBA')) for s in ('silver','auburn','bald')];delta=[int(np.any(images[0][mask]!=im[mask],axis=1).sum()) for im in images[1:]]
  eye_rows.append({'frame':i,'projected_eye_interior_pixels':int(mask.sum()),'silver_vs_auburn_different_pixels':delta[0],'silver_vs_bald_different_pixels':delta[1]});check('actual protected eye pixels identical across new appearances frame'+str(i),mask.sum()>0 and delta==[0,0])
 silhouettes=int(np.count_nonzero((heads['silver'][:,:,3]>=128)!=(heads['auburn'][:,:,3]>=128)));check('styles have distinct silhouettes rather than color-only change',silhouettes>=500)
 return {'schema':'bound-hair-replacement-review-v1','replacement_numeric_pass':all(c['pass'] for c in checks),'checks':checks,'actual_pixel_measurements':measurements,'projected_eye_pixel_checks':eye_rows,'eye_projection_definition':'Rest visible eye rectangle projected by common authoring head matrix, one-pixel interior erosion excludes raster boundary. Actual RGBA comparison, not a blinded eye detector.','distinct_silhouette_pixels':silhouettes,'user_hair_art_approved':False,'full_factory_production_pass':False,'hidden_anatomy_detected':False,'scope':case['scope']+' This is rendering/appearance replacement QA, not user art acceptance or all-direction compatibility.'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',type=Path,required=True);p.add_argument('--root',type=Path,default=Path.cwd());p.add_argument('--out',type=Path,required=True);a=p.parse_args();r=review(json.loads(a.case.read_text()),a.root);r['case_sha256']=hashlib.sha256(a.case.read_bytes()).hexdigest();a.out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'replacement_numeric_pass':r['replacement_numeric_pass'],'checks':len(r['checks']),'distinct_silhouette_pixels':r['distinct_silhouette_pixels']}));raise SystemExit(0 if r['replacement_numeric_pass'] else 1)
if __name__=='__main__':main()
