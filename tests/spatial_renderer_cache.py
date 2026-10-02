"""Compare cached/direct shared-depth pixels at the same actual rendered frame.
Only renderer mode changes; ordinary input drives the game. No position/time setters.
"""
import argparse,base64,io,json
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8011');ap.add_argument('--output',default='/tmp/astraeon-depth-cache');args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True);reports=[];errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':1280,'height':800});page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);page.goto(args.url+'/index.html?qa=1');page.locator('#create').click();page.wait_for_function('AstraeonQA.snapshot().renderer.frames>10')
 def compare(name):
  sample=page.evaluate('''()=>{const v=AstraeonSpatialView;const software=v.stats.software;v.stats.software=true;v.end();const cached=v.canvas.toDataURL(),before=v.snapshot();v.stats.software=false;v.end();const direct=v.canvas.toDataURL();
const THREE=AstraeonSpatialRenderer.THREE,original=[...v.actors.values()].map(a=>[a,a.mesh.material]);
for(const [a,old] of original){const m=new THREE.MeshBasicMaterial({map:old.map,alphaTest:.1,depthWrite:true,side:THREE.DoubleSide});m.onBeforeCompile=s=>{s.fragmentShader=s.fragmentShader.replace('#include <alphatest_fragment>','#include <alphatest_fragment>\n diffuseColor.rgb=vec3(1.,0.,1.);')};a.mesh.material=m}
v.stats.software=true;v.end();const maskCached=v.canvas.toDataURL();v.stats.software=false;v.end();const maskDirect=v.canvas.toDataURL();for(const [a,old] of original){a.mesh.material.dispose();a.mesh.material=old}v.stats.software=software;const size=v.renderer.getDrawingBufferSize(new AstraeonSpatialRenderer.THREE.Vector2()),scale=size.x/v.width;
const actors=[...v.actors.values()].filter(a=>a.mesh.visible).map(a=>{const p=a.mesh.position,alpha=a.ctx.getImageData(0,0,256,256).data,sx=v.width/2+(48*p.x-32*p.y-v.focus.x)*v.zoom,sy=v.height*v.anchorY+(14*p.x+22*p.y-v.focus.y-p.z*35)*v.zoom,points=[];
for(let y=Math.max(0,Math.floor((sy-224*v.zoom)*scale));y<Math.min(size.y,(sy+32*v.zoom)*scale);y++)for(let x=Math.max(0,Math.floor((sx-128*v.zoom)*scale));x<Math.min(size.x,(sx+128*v.zoom)*scale);x++){const u=Math.floor(((x+.5)/scale-sx)/v.zoom+128),k=Math.floor(((y+.5)/scale-sy)/v.zoom+224);if(u>1&&u<254&&k>1&&k<254&&alpha[(k*256+u)*4+3]>220)points.push([x,y])}return points});return {cached,direct,maskCached,maskDirect,before,actors}}''')
  arrays=[]
  for mode in ['cached','direct']:
   raw=base64.b64decode(sample.pop(mode).split(',')[1]);(out/f'{name}-{mode}.png').write_bytes(raw);arrays.append(np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'),dtype=float))
  delta=np.abs(arrays[0]-arrays[1]);mean=float(delta.mean());p95=float(np.percentile(delta,95));assert mean<3 and p95<10,(name,mean,p95)
  actor_deltas=[]
  for points in sample['actors']:
   values=np.array([delta[y,x] for x,y in points])
   if values.size:actor_deltas.append({'mean':float(values.mean()),'p95':float(np.percentile(values,95))})
  assert all(d['mean']<3 and d['p95']<20 for d in actor_deltas),(name,actor_deltas)
  masks=[]
  for mode in ['maskCached','maskDirect']:
   raw=base64.b64decode(sample.pop(mode).split(',')[1]);(out/f'{name}-{mode}.png').write_bytes(raw);a=np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'));masks.append((a[:,:,0]>150)&(a[:,:,1]<50)&(a[:,:,2]>150))
  disagreement=int(np.count_nonzero(masks[0]!=masks[1]));union=int(np.count_nonzero(masks[0]|masks[1]));assert union>100 and disagreement<=union*.03+10,(name,disagreement,union)
  reports.append({'name':name,'mean_pixel_delta':mean,'p95_pixel_delta':p95,'actor_region_deltas':actor_deltas,'cache_updates':sample['before'].get('cacheUpdates'),'depth_mask_disagreement':disagreement,'actor_mask_pixels':union})
 compare('arrival')
 start=page.evaluate('AstraeonQA.snapshot().time');page.keyboard.down('d');page.wait_for_function('(t)=>AstraeonQA.snapshot().time>t+2.4',arg=start);page.keyboard.up('d');page.wait_for_timeout(600);compare('camera-pan');assert reports[-1]['cache_updates']>reports[0]['cache_updates']
 page.set_viewport_size({'width':391,'height':843});page.wait_for_timeout(500);compare('odd-phone-size')
 page.set_viewport_size({'width':844,'height':390});page.wait_for_timeout(500);compare('phone-landscape')
 b.close()
report={'comparisons':reports,'errors':errors};(out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not errors
