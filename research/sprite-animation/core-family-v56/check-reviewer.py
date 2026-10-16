"""Exercise the shipped PNG viewer, clocks, all samples, aliases and async switches."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from playwright.sync_api import sync_playwright
from PIL import Image
import threading,json,hashlib,base64,io,numpy as np
P=Path(__file__).resolve().parent;D=json.loads((P/'catalog.json').read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();errors=[];requests=[];results=[]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright()as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url));page.goto(f'http://127.0.0.1:{server.server_port}/core-family-review.html');page.wait_for_function('window.READY===true||!!window.LOAD_ERROR');assert page.evaluate('window.READY')
 for action,a in D['actions'].items():
  for view,c in a['clips'].items():
   direction=D['directions'].index(view);assert page.evaluate('([a,d])=>study.choose(a,d,0)',[action,direction]);assert page.evaluate('study.current.view')==view;maxdiff=0
   for i,f in enumerate(c['frames']):
    raw=page.evaluate('i=>{study.select(i);return study.frame(i)}',i);actual=np.array(Image.open(io.BytesIO(base64.b64decode(raw.split(',')[1]))).convert('RGBA')).astype(float);expected=np.array(Image.open(P/f['path']).convert('RGBA')).astype(float);assert actual.shape==expected.shape;assert np.array_equal(actual[:,:,3],expected[:,:,3]),(action,view,i,'alpha/crop mismatch')
    # Compare visible premultiplied color/alpha; unused transparent RGB has no appearance.
    delta=np.abs(actual[:,:,:3]*actual[:,:,3:4]/255-expected[:,:,:3]*expected[:,:,3:4]/255);err=max(float(delta.max()),float(np.abs(actual[:,:,3]-expected[:,:,3]).max()));maxdiff=max(maxdiff,err);assert err<=2,(action,view,i,err)
    assert page.evaluate('study.clock.time')==sum(c['durations_ms'][:i])
   checks=page.evaluate('''()=>{const c=study.clock;c.clip.loop=false;c.start();study.draw(c.advance(c.total).frame);const end=c.finished&&!c.running&&study.frameIndex===c.clip.durations.length-1;c.clip.loop=true;c.start();c.advance(c.total+1);const loop=c.iteration===1&&c.time===1;study.select(0);return{end,loop}}''');assert all(checks.values())
   # Actual RAF playback through shipped controls at both speeds, then pause/resume.
   rates=[]
   for speed in ['1','0.25']:
    page.select_option('#speed',speed);page.evaluate('study.select(0)');page.click('#play');page.wait_for_timeout(140);t=page.evaluate('study.clock.time');assert t>0 and t<240*float(speed)+30,(action,view,speed,t);page.click('#play');paused=page.evaluate('study.clock.time');page.wait_for_timeout(35);assert page.evaluate('study.clock.time')==paused;page.click('#play');page.wait_for_timeout(65);assert page.evaluate('study.clock.time')>paused or len(c['frames'])==1;page.click('#play');rates.append({'speed':float(speed),'clock_progress_ms_after140ms':t})
   results.append({'action':action,'view':view,'frame_sha256':[f['sha256']for f in c['frames']],'durations_ms':c['durations_ms'],'actual_raster_comparisons':len(c['frames']),'maximum_premultiplied_rgba_error':maxdiff,'browser_codec_rounding_budget':2,'alpha_exact':True,'clock_end_loop_pause_resume_seek_pass':True,'actual_raf_rates':rates,'pass':True});print(action,view,'PASS',flush=True)
 # Exercise real camera selections for each action/heading, with rotating camera.
 aliases=[]
 for action,a in D['actions'].items():
  for direction in range(8):
   camera=(direction*3+1)%8;logical=D['directions'][(direction+camera)%8];expected=a['aliases'][logical];assert page.evaluate('([a,d,c])=>study.choose(a,d,c)',[action,direction,camera]);assert page.evaluate('study.current.view')==expected;aliases.append([action,direction,camera,expected])
 race=page.evaluate("async()=>{const p=study.choose('walk',0,0),q=study.choose('pickup',4,0);await Promise.all([p,q]);return study.current.action==='pickup'&&study.current.view==='N'}");assert race
 assert not errors;browser.close()
server.shutdown();report={'pass':True,'html_sha256':sha(P/'core-family-review.html'),'catalog_sha256_at_test':sha(P/'catalog.json'),'policy':{'canvas':D['canvas'],'directions':D['directions'],'aliases':{a:v['aliases']for a,v in D['actions'].items()}},'clips':results,'actual_camera_selections':aliases,'latest_requested_clip_wins':race,'page_errors':errors,'external_requests':[r for r in requests if not r.startswith('http://127.0.0.1:')and not r.startswith('data:')],'codec_policy':'Decoded WebP cells are exactly identical RGBA to original PNG in atlas-transport-review. Chrome WebP premultiplication can round semi-transparent color differently from native PNG (measured1.3098 on idleS, equal alpha); allow2/255 premultiplied color, never geometric fitting.','scope':'Actual portable PNG player on local HTTP, no external assets. Checks every selected raster and authored clip controls; native file:// policy is not tested here.'};assert not report['external_requests'];(P/'player-qa.json').write_text(json.dumps(report,indent=2)+'\n');print('ALL',len(results),'clips PASS')
