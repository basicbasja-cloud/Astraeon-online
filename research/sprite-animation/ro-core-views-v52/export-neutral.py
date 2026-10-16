from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,base64,hashlib
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw
import numpy as np
P=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start();rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1200,'height':950});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/neutral-review.html');page.wait_for_function('window.READY===true');(P/'neutral').mkdir(exist_ok=True)
 for i,v in enumerate(['S','SW','W','NW','N','NE','E','SE']):
  data=page.evaluate('i=>study.frame(i)',i);f=P/'neutral'/f'{v}.png';f.write_bytes(base64.b64decode(data.split(',')[1]));a=np.asarray(Image.open(f));y,x=np.where(a[:,:,3]>=128);rows.append({'view':v,'file':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'alpha128_bbox':[int(x.min()),int(y.min()),int(x.max()),int(y.max())],'height_px':int(y.max()-y.min()+1),'canvas_cut':bool(x.min()==0 or y.min()==0 or x.max()==383 or y.max()==511)})
 page.screenshot(path=str(P/'neutral-browser.png'),full_page=True);assert not errors;b.close()
server.shutdown();server.server_close();assert all(not r['canvas_cut'] and abs(r['height_px']-399)<=8 for r in rows)
atlas=Image.new('RGBA',(1536,1024));preview=Image.new('RGB',(1536,1024),(40,43,48));d=ImageDraw.Draw(preview)
for i,r in enumerate(rows):im=Image.open(P/r['file']);atlas.paste(im,(i%4*384,i//4*512));preview.paste(im,(i%4*384,i//4*512),im);d.text((i%4*384+10,i//4*512+10),r['view'],fill='white')
atlas.save(P/'neutral-eight-canonical.png');preview.save(P/'inputs/neutral-eight-canonical-preview.png');(P/'neutral-export-review.json').write_text(json.dumps({'dimension_and_canvas_pass':True,'frames':rows,'same_scale_all_views':True,'world_root_accuracy':None,'manual_anatomy_and_family_review_required':True,'scope':'Actual browser buffers and one-neutral size calibration, not whole factory acceptance'},indent=2)+'\n');print(rows)
