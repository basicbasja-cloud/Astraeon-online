"""Exercise actual player controls and both real-time playback rates."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,hashlib
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P.parent)));threading.Thread(target=server.serve_forever,daemon=True).start()
checks={};errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1100,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/{P.name}/review.html');page.wait_for_function('window.READY===true')
 for i in range(16):
  page.evaluate('i=>study.select(i)',i);assert page.locator('#frame').input_value()==str(i);assert page.evaluate('study.clock.sample().frame')==i
 checks['all16_frame_controls_and_clock_boundaries']=True
 page.locator('#prev').click();assert page.locator('#frame').input_value()=='14';page.locator('#next').click();assert page.locator('#frame').input_value()=='15';checks['step_controls']=True
 for speed,timeout in [('1',4000),('0.25',11000)]:
  page.locator('#speed').select_option(speed);page.locator('#play').click()
  page.wait_for_function('study.clock.sample().finished',timeout=timeout)
  assert page.locator('#frame').input_value()=='15';checks['actual_playback_'+speed]=True
 page.locator('#loop').check();page.locator('#speed').select_option('1');page.locator('#play').click();page.wait_for_function('study.clock.sample().iteration>=1',timeout=4000);page.locator('#play').click();a=page.evaluate('study.clock.sample()');page.wait_for_timeout(120);assert a==page.evaluate('study.clock.sample()');checks['loop_and_pause']=True
 page.evaluate('study.select(0)');page.locator('#prev').click();assert page.locator('#frame').input_value()=='0';page.evaluate('study.select(15)');page.locator('#next').click();assert page.locator('#frame').input_value()=='15';checks['step_bounds']=True
 page.locator('#grid').uncheck();page.evaluate('study.select(9)');page.screenshot(path=str(P/'verified-player.png'),full_page=True);assert not errors;checks['no_page_errors']=True;b.close()
server.shutdown();server.server_close()
assert (P/'inputs/sprite-clip-clock.cjs').read_bytes()==(P.parents[2]/'tools/sprite-clip-clock.cjs').read_bytes();checks['player_uses_exact_reusable_clock']=True
(P/'browser-qa.json').write_text(json.dumps({'pass':True,'checks':checks,'errors':errors,'player_sha256':hashlib.sha256((P/'review.html').read_bytes()).hexdigest(),'scope':'Actual browser controls and progression, not subjective smoothness proof'},indent=2)+'\n');print(checks)
