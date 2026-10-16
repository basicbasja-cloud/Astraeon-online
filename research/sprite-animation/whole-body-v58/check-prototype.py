"""Browser layer contract, actual RGBA roundtrip, and deliberately failing art gates."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from playwright.sync_api import sync_playwright
from PIL import Image
import threading,json,hashlib,base64,io,importlib.util,numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[2];D=json.loads((P/'pickup-S-four-slot.json').read_text());errors=[];rows=[]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));threading.Thread(target=s.serve_forever,daemon=True).start()
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{s.server_port}/four-slot-review.html');page.wait_for_function('window.READY||window.LOAD_ERROR');assert page.evaluate('window.READY')
 for i in range(16):
  page.evaluate('i=>prototypeStudy.select(i)',i);raw=page.evaluate('document.querySelector("canvas").toDataURL()');actual=np.array(Image.open(io.BytesIO(base64.b64decode(raw.split(',')[1]))).convert('RGBA')).astype(float);expected=np.array(Image.open(P/'frames/full'/f'{i:02}.png').convert('RGBA')).astype(float);assert np.array_equal(actual[:,:,3],expected[:,:,3]);delta=np.abs(actual[:,:,:3]*actual[:,:,3:4]/255-expected[:,:,:3]*expected[:,:,3:4]/255);assert delta.max()<=1.1
  calls=page.evaluate('''i=>{const x=prototypeStudy,ctx=x.ctx;const old=ctx.drawImage;let calls=0;ctx.drawImage=function(...args){calls++;return old.apply(ctx,args)};x.drawFrame(ctx,x.clip,x.images,i);ctx.drawImage=old;return calls}''',i);assert calls==2
  for name in ['head','body']:
   page.uncheck('#'+name);page.check('#'+name)
  rows.append({'index':i,'alpha_exact':True,'max_premultiplied_color_error':float(delta.max()),'runtime_draw_calls':calls})
 controls=page.evaluate('''()=>{const x=prototypeStudy,cs=[];for(const mutate of [d=>d.frames[0].slots.knee=d.frames[0].slots.body,d=>d.frames[0].order=['body','body','head','trail'],d=>delete d.frames[0].slots.body,d=>d.frames[0].slots.body.scale=0.8,d=>d.bodyPolicy='segmented-limbs']){const d=structuredClone(x.clip);mutate(d);let rejected=false;try{x.validateClip(d)}catch(e){rejected=true}cs.push(rejected)}return cs}''');assert all(controls)
 for rate in ['1','0.25']:
  page.select_option('#rate',rate);page.evaluate('prototypeStudy.select(0)');page.click('#play');page.wait_for_timeout(450);assert int(page.input_value('#seek'))>0;page.click('#play');paused=page.input_value('#seek');page.wait_for_timeout(100);assert page.input_value('#seek')==paused
 page.screenshot(path=str(P/'prototype-browser.png'));b.close()
s.shutdown();assert not errors
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
(P/'prototype-browser-review.json').write_text(json.dumps({'architecture_and_roundtrip_pass':True,'actual_frames':rows,'reject_fragment_or_transform_controls':controls,'page_errors':errors,'dependencies':{n:sha(P/n)for n in ['four-slot-review.html','four-slot-player.js','pickup-S-four-slot.json','extraction-review.json']},'art_approval':False,'scope':'Complete body/head technical composition and player behavior only. Provisional head masks include costume fragments; no interchangeable-head approval. Native timing/contact fail separately.'},indent=2)+'\n')
def mod(n):
 spec=importlib.util.spec_from_file_location(n,ROOT/'tools'/('sprite-'+n+'-review.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
frames=[{'path':f'frames/full/{i:02}.png','sha256':sha(P/'frames/full'/f'{i:02}.png')}for i in range(16)];motion={'frames':frames,'crown_window':[50,0,235,250],'durations':[f['duration_ms']for f in D['frames']],'peak_index_range':[6,8],'profile':{'max_step_px':35,'max_speed_px_s':500,'max_acceleration_px_s2':5000,'reverse_slack_px':2,'neutral_slack_px':3,'min_excursion_px':60,'max_excursion_px':180},'scope':'Provisional prototype gate; failure is not repaired by registration fitting.'};mr=mod('motion').evaluate(motion,P);(P/'motion-case.json').write_text(json.dumps(motion,indent=2)+'\n');(P/'motion-review.json').write_text(json.dumps(mr,indent=2)+'\n');assert not mr['motion_profile_pass']
contact={'frames':frames,'surfaces':{n:{'window':rect,'planted_frames':list(range(16)),'budget_px':{'x':6,'y':6}}for n,rect in [('screen_left',[75,260,140,345]),('screen_right',[148,260,212,345])]}};cr=mod('contact').evaluate(contact,P);(P/'contact-case.json').write_text(json.dumps(contact,indent=2)+'\n');(P/'contact-review.json').write_text(json.dumps(cr,indent=2)+'\n');assert not cr['visible_surface_contact_pass'];print({'architecture_and_roundtrip_pass':True,'frames':16,'motion_pass':False,'contact_pass':False,'production_pass':False})
