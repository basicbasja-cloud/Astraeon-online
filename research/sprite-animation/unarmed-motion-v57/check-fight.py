"""Current saved-source, rest-binding, actual raster and GPU attachment gates."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np,json,math,hashlib,threading
P=Path(__file__).resolve().parent;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();D=json.loads((P/'fight-rig-contract.json').read_text());E=json.loads((P/'fight-export-review.json').read_text());S=json.loads((P/'source/retargeted-endpoints.json').read_text());A=json.loads((P/'source/authoring-receipt.json').read_text());R=json.loads((P/'source/source-geometry-review.json').read_text());assert sha(P/'source/unarmed-inplace.blend')==A['blend_sha256'];assert R['source_geometry_pass'];out=[]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start();errors=[]
with sync_playwright()as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);page=browser.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/fight-review.html');page.wait_for_function('window.READY===true||!!window.LOAD_ERROR');assert page.evaluate('window.READY')
 for ci,(c,ex)in enumerate(zip(D['clips'],E['clips'])):
  assert c['view']==ex['view'] and c['action']==ex['action'];assert c['source_sha256']==sha(P/'source/retargeted-endpoints.json');assert len(c['poses'])==len(ex['frames']);assert all(t>0 and t%10==0 for t in c['durations_ms']);page.evaluate('i=>study.choose(i)',ci)
  for a in c['definitions'].values():assert sha(P/a['texture'])==a['texture_sha256']
  neck=page.evaluate('''()=>{const d=study.data.clips[study.index],h=study.layers.get('head'),b=study.layers.get('body'),a=document.createElement('canvas');a.width=512;a.height=576;const x=a.getContext('2d'),counts=[];for(let i=0;i<d.poses.length;i++){const p=d.poses[i];h.draw(p);x.clearRect(0,0,512,576);x.drawImage(h.canvas,0,0);const H=x.getImageData(0,0,512,576).data;b.draw(p);x.clearRect(0,0,512,576);x.drawImage(b.canvas,0,0);const B=x.getImageData(0,0,512,576).data,n=d.definitions.body.rest.neck,cx=n[0]+p.neck[0],cy=n[1]+p.neck[1];let count=0;for(let y=Math.max(0,Math.floor(cy-25));y<Math.min(576,cy+25);y++)for(let j=Math.max(0,Math.floor(cx-35));j<Math.min(512,cx+35);j++){const k=(y*512+j)*4+3;if(H[k]>=128&&B[k]>=128)count++}counts.push(count)}return counts}''');assert min(neck)>0,(c['view'],c['action'],'neck',neck)
  foot_y=math.ceil(max(c['definitions'][s+'_leg']['bands'][3]for s in ['left','right'])+8);foot_boxes=[];first=None;maxpixel=0;angle_error=0;affine_error=0
  for i,(p,f)in enumerate(zip(c['poses'],ex['frames'])):
   assert sha(P/f['path'])==f['sha256'];im=np.array(Image.open(P/f['path']).convert('RGBA'));assert not f['canvas_cut'];region=im[foot_y:];mask=region[:,:,3]>=128;y,x=np.where(mask);assert len(x)>100;foot_boxes.append([int(x.min()),int(y.min()),int(x.max()),int(y.max())]);premult=np.concatenate([region[:,:,:3].astype(float)*region[:,:,3:4]/255,region[:,:,3:4]],axis=2)
   if first is None:first=premult
   maxpixel=max(maxpixel,float(np.max(np.abs(premult-first))))
   assert abs(p['head_angle'][0])<math.pi/2
   # Current projected arm directions must match independent saved-source samples.
   phase=c['source_phases'][i];j=min(255,int(phase*256));t=phase*256-j;rows=S['clips'][c['action']]['frames'];q={}
   for side in ['left','right']:
    art=c['definitions'][side+'_arm']['rest'];channels=[('shoulder','upperarm','head'),('elbow','forearm','head'),('wrist','hand','head'),('palm','hand','tail')]
    for label,bone,edge in channels:q[side+'.'+label]=[(1-t)*rows[j]['projected'][c['view']][side+'.'+bone][edge][k]+t*rows[j+1]['projected'][c['view']][side+'.'+bone][edge][k] for k in [0,1]]
    for (aa,*_), (bb,*_)in zip(channels,channels[1:]):
     a=side+'.'+aa;b=side+'.'+bb;u=np.array(q[b])-q[a];v=np.array(art[b])+p[b]-np.array(art[a])-p[a];error=abs(float(u[0]*v[1]-u[1]*v[0]))/(np.linalg.norm(u)*np.linalg.norm(v));angle_error=max(angle_error,error);assert np.dot(u,v)>0
  for g in ex['geometry']:
   assert math.isfinite(g['min_area_ratio']) and g['min_area_ratio']>0
   if g['layer'].endswith('_leg'):assert g['min_area_ratio']>.15,(c['view'],c['action'],g)
   elif g['layer'].endswith('_arm'):
    a=c['definitions'][g['layer']];p=c['poses'][g['frame']];nodes=a['nodes'];aa,bb=(nodes[:2]if g['part']=='upper'else nodes[1:3]);u=np.array(a['rest'][bb])-a['rest'][aa];v=u+np.array(p[bb])-p[aa];expected=np.linalg.norm(v)/np.linalg.norm(u)if g['part']in ['upper','lower','knee']else 1;affine_error=max(affine_error,abs(g['min_area_ratio']-expected),abs(g['max_area_ratio']-expected))
  ranges=np.ptp(np.array(foot_boxes),axis=0).tolist();assert max(ranges)<=1,(c['view'],c['action'],ranges);assert maxpixel<=2,(c['view'],c['action'],maxpixel);assert angle_error<1e-8 and affine_error<1e-7
  if c['action']=='attack1':assert ex['frames'][0]['sha256']==ex['frames'][-1]['sha256']
  out.append({'action':c['action'],'view':c['view'],'frames':len(c['poses']),'frame_sha256':[f['sha256']for f in ex['frames']],'minimum_neck_overlap_px':min(neck),'visible_lower_boot_roi':[0,foot_y,512,576],'lower_boot_bbox_ranges_px':ranges,'lower_boot_max_premultiplied_rgba_difference':maxpixel,'source_arm_direction_max_cross_error':angle_error,'arm_affine_ratio_max_error':affine_error,'minimum_deforming_leg_mesh_ratio':min(g['min_area_ratio']for g in ex['geometry']if g['layer'].endswith('_leg')),'pass':True});print(c['action'],c['view'],'PASS',flush=True)
 assert not errors;browser.close()
server.shutdown();report={'pass':True,'clips':out,'page_errors':errors,'dependencies':{str(f.relative_to(P)):sha(f)for f in [P/'fight-rig-contract.json',P/'fight-export-review.json',P/'source/retargeted-endpoints.json',P/'source/authoring-receipt.json',P/'source/source-geometry-review.json',P/'source/arm-retarget-review.json',P/'check-fight.py',P/'inputs/sprite-mesh-player.js',P/'inputs/sprite-articulated-player.js',P/'inputs/sprite-segmented-player.js',P/'inputs/sprite-segment-ownership.js']},'foreshortening_policy':'Deforming legs retain>.15 area ratio. Each arm submesh must match its single analytically source-driven bone affine ratio at every triangle; rigid wrist/hand pieces retain ratio1. N ready counter forearm is near edge-on (minimum~.08529), not a local fold. No blanket numerical pass for painted appearance.','scope':'Current original in-place unarmed adaptation and actual sampled rasters. Visible lower shoe strips only; no whole-boot or hidden anatomy assertion, exact external-lunge replay, modular swaps, game integration or user acceptance.'};(P/'fight-qa.json').write_text(json.dumps(report,indent=2)+'\n')
