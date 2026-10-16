"""Failure injection and different-size fixture; fixture is not character artwork."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,base64,io,hashlib
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P.parent)));threading.Thread(target=s.serve_forever,daemon=True).start();checks={};overlaps=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);url=f'http://127.0.0.1:{s.server_port}/{P.name}/walk-review.html'
 for mode in ['missing','wrong_size']:
  p=b.new_page()
  if mode=='missing':p.route('**/parts/W/head.png',lambda r:r.abort())
  else:
   buf=io.BytesIO();Image.new('RGBA',(1,1),(255,255,255,255)).save(buf,format='PNG');p.route('**/parts/W/head.png',lambda r:r.fulfill(content_type='image/png',body=buf.getvalue()))
  p.goto(url);p.wait_for_function('!!window.LOAD_ERROR');assert not p.evaluate('!!window.READY');assert p.locator('#play').is_disabled() and p.locator('#frame').is_disabled();assert p.evaluate("document.getElementById('c').getContext('2d').getImageData(0,0,512,512).data.every(x=>x===0)");checks[mode+'_fails_closed']=p.evaluate('LOAD_ERROR');p.close()
 p=b.new_page();p.goto(url);p.wait_for_function('window.READY===true')
 checks.update(p.evaluate('''()=>{const out={},base=structuredClone(study.data.definitions.left_leg),im=study.layers.get('left_leg').image;for(const kind of ['owner','role','bone','bands','pose']){let d=structuredClone(base),m;try{if(kind==='owner')d.nodes[0]='right.hip';if(kind==='role')d.role='arm';if(kind==='bone')d.rest[d.nodes[1]]=d.rest[d.nodes[0]];if(kind==='bands')d.bands.reverse();m=new SpriteArticulatedLayer(document.createElement('canvas'),im,d);if(kind==='pose'){let q=study.poseAt(.2);delete q['left.knee'];m.draw(q)}throw Error('Accepted invalid '+kind)}catch(e){if(e.message.startsWith('Accepted'))throw e;out['reject_'+kind]=e.message}finally{if(m)m.dispose()}}const f=document.createElement('canvas');f.width=256;f.height=384;const x=f.getContext('2d');x.fillStyle='#8ed';x.fillRect(96,80,28,210);x.fillRect(74,290,56,24);let d={kind:'chain',owner:'left',role:'leg',canvas:[256,384],nodes:['left.hip','left.knee','left.ankle','left.toe'],rest:{'left.hip':[110,80],'left.knee':[110,180],'left.ankle':[110,295],'left.toe':[80,305]},bands:[155,205,260,285],distal:'fixed_orientation'},m=new SpriteArticulatedLayer(document.createElement('canvas'),f,d),pose={'left.hip':[0,0],'left.knee':[8,0],'left.ankle':[20,-10],'left.toe':[20,-10],output_offset:[64,48]};m.setViewport(384,512);m.draw(pose);let err=0;for(let i=0;i<m.rest.length;i++){let a=m.rest[i],q=m.vertices[i];if(a[1]>=285)err=Math.max(err,Math.hypot(q[0]-a[0]-84,q[1]-a[1]-38))}if(err>1e-8)throw Error('Fixture rigid boot changed');out.different_canvas_and_proportions_fixture={canvas:[256,384],viewport:[384,512],max_distal_error:err,scope:'Synthetic geometric fixture, not validation of a second character'};m.dispose();return out}'''))
 def pixels(name,t,dy=0):
  raw=p.evaluate('a=>{const m=study.layers.get(a[0]),q=study.poseAt(a[1]);if(a[2])q.head[1]+=a[2];m.setViewport(512,512);m.draw(q);return m.canvas.toDataURL()}',[name,t,dy]);return np.array(Image.open(io.BytesIO(base64.b64decode(raw.split(',')[1]))))[:,:,3]>=128
 bad=[];sizes=[]
 for i in range(80):
  h=pixels('head',i/80);body=pixels('body',i/80);overlaps.append(int((h&body)[184:246,226:290].sum()));bad.append(int((pixels('head',i/80,-30)&body)[184:246,226:290].sum()));y,x=np.where(h);sizes.append([int(np.ptp(x)),int(np.ptp(y))])
 checks['neck_overlap_actual_buffers']={'roi':[226,184,290,246],'minimum_pixels':min(overlaps),'shifted_head_negative_minimum':min(bad),'samples':80};assert min(overlaps)>=12;assert min(bad)<12
 checks['rigid_head_raster_extent_range']=np.ptp(sizes,axis=0).tolist();assert max(checks['rigid_head_raster_extent_range'])<=2;b.close()
s.shutdown();s.server_close();result={'pass':True,'checks':checks,'neck_overlap_pixels':overlaps,'head_shift_negative_overlap_pixels':bad,'renderer_sha256':hashlib.sha256((P/'inputs/sprite-articulated-player.js').read_bytes()).hexdigest(),'scope':'Authored rest binding and reviewed neck region only; no automatic anatomy detector or universal character approval'};(P/'reuse-qa.json').write_text(json.dumps(result,indent=2)+'\n');print(checks)
