from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,base64,hashlib
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P.parent)));threading.Thread(target=s.serve_forever,daemon=True).start();rows=[];errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1080,'height':650});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{s.server_port}/{P.name}/rest-review.html');page.wait_for_function('window.READY===true');(P/'parts/W').mkdir(parents=True,exist_ok=True)
 for part in page.evaluate('study.data.parts'):
  raw=page.evaluate('n=>study.part(n)',part['name']);f=P/'parts/W'/f"{part['name']}.png";f.write_bytes(base64.b64decode(raw.split(',')[1]));rows.append({'name':part['name'],'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 raw=page.evaluate('study.composite()');(P/'rest-composite-W.png').write_bytes(base64.b64decode(raw.split(',')[1]));page.screenshot(path=str(P/'rest-browser.png'),full_page=True);assert not errors;b.close()
s.shutdown();s.server_close();(P/'rest-export.json').write_text(json.dumps({'parts':rows,'page_errors':errors,'manual_reassembly_review_required':True,'production_pass':False},indent=2)+'\n')
