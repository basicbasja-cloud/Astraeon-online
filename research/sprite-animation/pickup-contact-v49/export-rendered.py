"""Export actual browser render buffers; input PNGs never edited."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,base64
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P.parent)));threading.Thread(target=server.serve_forever,daemon=True).start()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1200,'height':1000});page.goto(f'http://127.0.0.1:{server.server_port}/{P.name}/review.html');page.wait_for_function('window.READY===true')
 for i in range(16):
  for name,value in [('corrected',True),('before',False)]:
   data=page.evaluate('([i,c])=>study.frame(i,c)',[i,value]);out=P/'renders'/name;out.mkdir(parents=True,exist_ok=True);(out/f'{i:02}.png').write_bytes(base64.b64decode(data.split(',')[1]))
 page.evaluate('study.select(9)');page.locator('#grid').uncheck();page.screenshot(path=str(P/'contact-preview.png'),full_page=True);b.close()
server.shutdown();server.server_close();print('32actualbrowserbuffers exported')
