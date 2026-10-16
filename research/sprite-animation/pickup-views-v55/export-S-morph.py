from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from playwright.sync_api import sync_playwright
from PIL import Image
import threading,json,base64,hashlib
P=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));threading.Thread(target=s.serve_forever,daemon=True).start();out=P/'morph/S';out.mkdir(parents=True,exist_ok=True);rows=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page();p.goto(f'http://127.0.0.1:{s.server_port}/S-morph-review.html');p.wait_for_function('window.READY')
 for i in range(16):
  r=p.evaluate('i=>study.frame(i)',i);f=out/f'{i:02}.png';f.write_bytes(base64.b64decode(r['png'].split(',')[1]));rows.append({'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'geometry':r['geometry']})
 b.close()
s.shutdown();s.server_close();(P/'S-morph-export.json').write_text(json.dumps({'frames':rows,'production_pass':False},indent=2)+'\n');board=Image.new('RGBA',(2048,2048),(40,43,48,255))
for i,f in enumerate(rows):board.alpha_composite(Image.open(P/f['path']),(i%4*512,i//4*512))
board.convert('RGB').save(P/'S-morph-sixteen.png')
