"""Compare the legacy orthographic software cache/direct shared-depth pixels.
The default Ragnarok perspective camera uses direct rendering, tested separately.
Only renderer mode changes; ordinary input drives the game. No position/time setters.
"""
import argparse,base64,io,json,math,time,os
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8011');ap.add_argument('--output',default='/tmp/astraeon-depth-cache');args=ap.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True);reports=[];errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('ASTRAEON_BROWSER','/usr/bin/chromium'),args=['--no-sandbox','--enable-gpu','--use-angle=d3d11']);page=b.new_page(viewport={'width':1280,'height':800});page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);page.goto(args.url+'/index.html?qa=1&camera=legacy');page.locator('#create').click();page.wait_for_function('AstraeonQA.snapshot().renderer.frames>10')
 # A full camera-facing quad can lean its head into a wall even when its feet
 # stand in front. Require real upright world height while retaining the exact
 # illustration size at the gameplay projection.
 upright=page.evaluate('''()=>{const v=AstraeonSpatialView,a=v.actors.get('player'),p=a.mesh.geometry.attributes.position.array,project=([x,y,z])=>{const q=AstraeonView.project(x,y);return [q.x,q.y-z*35]},vs=Array.from({length:4},(_,i)=>Array.from(p.slice(i*3,i*3+3)));return {vertices:vs,projected:vs.map(project)}}''')
 vs=upright['vertices'];projected=upright['projected']
 for bottom,top in [(0,3),(1,2)]:
  assert all(abs(vs[bottom][axis]-vs[top][axis])<1e-6 for axis in [0,1]),'Actor height must not lean into a wall'
  assert 1<(vs[top][2]-vs[bottom][2])<8,'Registered complete frame retains real upright height'
 assert projected[1][0]>projected[0][0] and abs(projected[1][1]-projected[0][1])<1e-4
 def compare(name):
  sample=page.evaluate(r'''()=>{const v=AstraeonSpatialView;const software=v.stats.software;v.stats.software=true;v.end();const cached=v.canvas.toDataURL(),before=v.snapshot();v.stats.software=false;v.end();const direct=v.canvas.toDataURL();
const THREE=AstraeonSpatialRenderer.THREE,original=[...v.actors.values()].map(a=>[a,a.mesh.material]);
for(const [a,old] of original){const m=new THREE.MeshBasicMaterial({map:old.map,alphaTest:.1,depthWrite:true,side:THREE.DoubleSide});m.onBeforeCompile=s=>{s.fragmentShader=s.fragmentShader.replace('#include <alphatest_fragment>','#include <alphatest_fragment>\n diffuseColor.rgb=vec3(1.,0.,1.);')};a.mesh.material=m}
v.stats.software=true;v.end();const maskCached=v.canvas.toDataURL();v.stats.software=false;v.end();const maskDirect=v.canvas.toDataURL();for(const [a,old] of original){a.mesh.material.dispose();a.mesh.material=old}v.stats.software=software;return {cached,direct,maskCached,maskDirect,before}}''')
  arrays=[]
  for mode in ['cached','direct']:
   raw=base64.b64decode(sample.pop(mode).split(',')[1]);(out/f'{name}-{mode}.png').write_bytes(raw);arrays.append(np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'),dtype=float))
  delta=np.abs(arrays[0]-arrays[1]);mean=float(delta.mean());p95=float(np.percentile(delta,95));assert mean<3 and p95<=10,(name,mean,p95)
  masks=[]
  for mode in ['maskCached','maskDirect']:
   raw=base64.b64decode(sample.pop(mode).split(',')[1]);(out/f'{name}-{mode}.png').write_bytes(raw);a=np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'));masks.append((a[:,:,0]>150)&(a[:,:,1]<50)&(a[:,:,2]>150))
  disagreement=int(np.count_nonzero(masks[0]!=masks[1]));union=int(np.count_nonzero(masks[0]|masks[1]));assert union>100 and disagreement<=union*.03+10,(name,disagreement,union)
  # GPU frames intentionally leave the composition Canvas empty. Use actual
  # visible shared-depth actor masks, rather than that obsolete alpha source.
  values=delta[masks[0]|masks[1]];actor_deltas=[{'mean':float(values.mean()),'p95':float(np.percentile(values,95))}]
  assert all(d['mean']<3 and d['p95']<20 for d in actor_deltas),(name,actor_deltas)
  reports.append({'name':name,'mean_pixel_delta':mean,'p95_pixel_delta':p95,'actor_region_deltas':actor_deltas,'cache_updates':sample['before'].get('cacheUpdates'),'depth_mask_disagreement':disagreement,'actor_mask_pixels':union})
 # Exercise the actual cache-mode begin() as well as end(): it snaps the
 # camera to the drawing-buffer grid, including odd viewport dimensions.
 page.evaluate('AstraeonSpatialView.stats.software=true');page.wait_for_timeout(150)
 compare('arrival')
 # Follow ordinary route clicks far enough to cross a cache boundary. A timed
 # keypress can hit the forge and never move the camera beyond its padded cache.
 deadline=time.monotonic()+70
 plaza=page.evaluate('AstraeonContent.nativeWorld.spatial.scene.route.find(s=>s.name==="Plaza").position')
 while page.evaluate('(g)=>Math.hypot(AstraeonQA.snapshot().save.x-g[0],AstraeonQA.snapshot().save.y-g[1])',plaza)>.4:
  assert time.monotonic()<deadline,'Arrival-to-plaza navigation timed out'
  target=page.evaluate(r'''goal=>{const s=AstraeonQA.snapshot(),v=s.view,r=world.getBoundingClientRect(),route=AstraeonContent.nativeWorld.spatial.route(s.player.position,{x:goal[0],y:goal[1]});let previous=s.player.position;const candidates=[];for(const q of route){const count=Math.ceil(Math.hypot(q.x-previous.x,q.y-previous.y)/2);for(let i=1;i<=count;i++)candidates.push({x:previous.x+(q.x-previous.x)*i/count,y:previous.y+(q.y-previous.y)*i/count});previous=q}return candidates.map(q=>{const p=AstraeonSpatialView.worldToScreen(q.x,q.y,AstraeonContent.nativeWorld.spatial.elevationAt(q.x,q.y)),x=p.x,y=p.y;return{q,x,y,screen:[r.x+x,r.y+y]}}).filter(p=>p.x>30&&p.x<r.width-30&&p.y>50&&p.y<r.height-40&&!AstraeonSpatialView.pickActor(p.x,p.y)?.startsWith('service/')&&document.elementFromPoint(r.x+p.x,r.y+p.y)?.id==='world').at(-1)}''',plaza)
  assert target,'No visible route waypoint'
  page.mouse.click(*target['screen'])
  page.wait_for_function('(q)=>Math.hypot(AstraeonQA.snapshot().save.x-q.x,AstraeonQA.snapshot().save.y-q.y)<.4',arg=target['q'],timeout=20000)
 page.wait_for_timeout(600);compare('camera-pan');assert reports[-1]['cache_updates']>reports[0]['cache_updates']
 page.set_viewport_size({'width':391,'height':843});page.wait_for_timeout(500);compare('odd-phone-size')
 page.set_viewport_size({'width':844,'height':390});page.wait_for_timeout(500);compare('phone-landscape')
 b.close()
report={'comparisons':reports,'errors':errors};(out/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert not errors
