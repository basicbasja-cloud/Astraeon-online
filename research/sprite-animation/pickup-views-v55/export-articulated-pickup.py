"""Inspect actual prototype renders; no acceptance is inferred from a successful export."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,base64,io,hashlib,sys
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent;view=sys.argv[1] if len(sys.argv)>1 else 'W'
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P.parent)));threading.Thread(target=s.serve_forever,daemon=True).start();frames=[];ims=[];errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto(f'http://127.0.0.1:{s.server_port}/{P.name}/{view}-articulated-review.html');p.wait_for_function('window.READY===true||!!window.LOAD_ERROR');assert p.evaluate('window.READY'),p.evaluate('window.LOAD_ERROR');out=P/'articulated'/view;out.mkdir(parents=True,exist_ok=True)
 for i in range(16):
  raw=p.evaluate('i=>study.frame(i)',i);im=Image.open(io.BytesIO(base64.b64decode(raw.split(',')[1]))).copy();f=out/f'{i:02}.png';im.save(f);ims.append(im);frames.append({'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 p.screenshot(path=str(P/(view+'-articulated-browser.png')),full_page=True);assert not errors;b.close()
s.shutdown();s.server_close();height=ims[0].height;board=Image.new('RGBA',(2048,height*4),(40,43,48,255))
for i,im in enumerate(ims):board.alpha_composite(im,(i%4*512,i//4*height))
board.convert('RGB').save(P/(view+'-articulated-sixteen.png'));critical=Image.new('RGBA',(2048,height),(40,43,48,255))
for j,i in enumerate([0,4,8,12]):critical.alpha_composite(ims[i],(j*512,0))
critical.convert('RGB').save(P/(view+'-articulated-critical.png'));(P/(view+'-articulated-export.json')).write_text(json.dumps({'frames':frames,'page_errors':errors,'production_pass':False,'manual_review_required':True},indent=2)+'\n')
