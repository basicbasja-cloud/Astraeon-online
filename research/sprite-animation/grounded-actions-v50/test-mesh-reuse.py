"""Actual second model/size plus deliberate fold-over negative control."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import json,threading,base64,importlib.util
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('contact',P/'inputs/sprite-contact-review.py');obs=importlib.util.module_from_spec(spec);spec.loader.exec_module(obs)
adapter={'width':256,'height':384,'grid_px':12,'bands':[{'y':0,'channel':'head'},{'y':180,'channel':'head'},{'y':220,'channel':'chest'},{'y':280,'channel':'hips'},{'y':300,'channel':'fixed'},{'y':384,'channel':'fixed'}],'influences':[],'texture':'../pickup-contact-v49/references/kaykit-captures/Idle_A/N/00.png','purpose':'Second texture/character and dimensions; independent rest bands. Technical reuse demonstration only.'}
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P.parent)));threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);page=b.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/{P.name}/review.html');page.wait_for_function('window.READY===true');page.evaluate('''async adapter=>{let im=new Image();im.src=adapter.texture;await im.decode();let c=document.createElement('canvas');document.body.appendChild(c);window.second=new SpriteMesh(c,im,adapter);}''',adapter)
 rows=[];out=P/'reuse-external';out.mkdir(exist_ok=True);reference=None
 for i in range(16):
  data=page.evaluate('''i=>{let p=study.data.clips['hit.light'].poses[i];second.draw(p);return second.canvas.toDataURL('image/png')}''',i);f=out/f'{i:02}.png';f.write_bytes(base64.b64decode(data.split(',')[1]));a=np.asarray(Image.open(f));reference=a if reference is None else reference;assert np.array_equal(a[304:],reference[304:]);rows.append({'path':str(f.relative_to(P)),'sha256':obs.sha(f)})
 # Geometry observation is independent of source delta magnitude metadata.
 negative=page.evaluate('''()=>{let m=study.mesh,v=m.draw({chest:[0,1000]}),min=Infinity;const area=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);for(let j=0;j<v.length;j+=3)min=Math.min(min,area(v[j],v[j+1],v[j+2])/area(m.rest[j],m.rest[j+1],m.rest[j+2]));return min;}''');assert negative<0
 schema_checks=page.evaluate("""()=>{const m=study.mesh,a=m.adapter;let count=0;for(const bad of [{...a,grid_px:0},{...a,width:385},{...a,bands:[...a.bands].reverse()}]){let rejected=false;try{new SpriteMesh(document.createElement('canvas'),m.image,bad)}catch(e){rejected=true}if(!rejected)throw Error('Invalid adapter passed');count++}let rejected=false;try{m.draw({head:[NaN,0]})}catch(e){rejected=true}if(!rejected)throw Error('Invalid pose passed');return count+1;}""")
 b.close()
server.shutdown();server.server_close()
case={'frames':rows,'surfaces':{name:{'window':box,'planted_frames':list(range(16)),'budget_px':{'x':3,'y':3},'distal_band_px':4,'min_component_area':20} for name,box in [('screen_left',[75,300,124,355]),('screen_right',[125,300,174,355])]}}
r=obs.evaluate(case,P);assert r['visible_surface_contact_pass'];(P/'reuse-external-adapter.json').write_text(json.dumps(adapter,indent=2)+'\n');(P/'reuse-external-contact-case.json').write_text(json.dumps(case,indent=2)+'\n');(P/'reuse-external-contact-review.json').write_text(json.dumps(r,indent=2)+'\n');(P/'reuse-qa.json').write_text(json.dumps({'pass':True,'different_character_dimensions_and_adapter':True,'all16_distal_buffers_exact':True,'injected_triangle_fold_detected':True,'invalid_adapters_and_pose_rejected':schema_checks,'negative_min_triangle_area_ratio':negative,'scope':'Renderer/contact reuse only. Does not prove full automatic retargeting, appearance acceptance or every motion.'},indent=2)+'\n');print('External character16buffers pass; injected mesh fold rejected',negative)
