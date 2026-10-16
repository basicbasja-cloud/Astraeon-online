"""Actual isolated GPU layers for contact diagnostics; never compose them as patches."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from playwright.sync_api import sync_playwright
import threading,json,base64,hashlib,sys
P=Path(__file__).resolve().parent;name=sys.argv[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));threading.Thread(target=s.serve_forever,daemon=True).start();export=json.loads((P/f'{name}-articulated-export.json').read_text());rows=[];out=P/'contact-layers'/name;out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page();p.goto(f'http://127.0.0.1:{s.server_port}/{name}-articulated-review.html');p.wait_for_function('window.READY')
 for i,row in enumerate(export['frames']):
  r={'index':i,'composite':row,'layers':{}}
  for layer in ['left_leg','right_leg','right_arm']:
   raw=p.evaluate('''([i,n])=>{study.frame(i);const m=study.layers.get(n),r=m.drawPieces(study.data.poses[i]);return r.canvas.toDataURL()}''',[i,layer]);f=out/f'{i:02}-{layer}.png';f.write_bytes(base64.b64decode(raw.split(',')[1]));r['layers'][layer]={'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
  rows.append(r)
 b.close()
s.shutdown();s.server_close();d={'frames':rows,'foot_windows':{'right_leg':[175,480,250,515],'left_leg':[270,480,345,515]},'occluders':['right_arm'],'rgba_rounding_budget':2,'min_visible_distal_fraction':.5,'min_visible_baseline_fraction':.5,'distal_band_px':8,'scope':'Authored original part owners, independently captured GPU layers and actual composite pixels. Not automatic anatomical recognition or full hidden-sole visibility. Layers are diagnostic only, never final artwork patches.'};(P/f'{name}-layer-contact-case.json').write_text(json.dumps(d,indent=2)+'\n')
