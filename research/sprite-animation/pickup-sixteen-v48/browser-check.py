from pathlib import Path
from playwright.sync_api import sync_playwright
import json,threading
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
P=Path(__file__).resolve().parent
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start();origin=f'http://127.0.0.1:{server.server_port}'
checks={};errors=[];external=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1400,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(origin+'/') else (external.append(route.request.url),route.abort()))
 page.goto(origin+'/review.html');page.wait_for_function('window.reviewReady===true')
 checks['40_frames_decoded']=page.evaluate('Object.values(images).flat().length===40&&Object.values(images).flat().every(im=>im.complete&&im.naturalWidth===384&&im.naturalHeight===512)')
 for i,t in enumerate([0,90,190,280,370,460,560,650,740,830,930,1020,1110,1170,1230,1300]):
  page.locator('#time').evaluate('(e,t)=>{e.value=t;e.dispatchEvent(new Event("input"))}',t);checks[f'seek16_{i}']=f'ทดลอง {i+1}/16' in page.locator('#status').inner_text()
 page.locator('#time').evaluate('(e)=>{e.value=0;e.dispatchEvent(new Event("input"))}');page.locator('#play').click();page.wait_for_timeout(2150);checks['normal_once_stops']=page.locator('#play').inner_text()=='เล่น' and page.locator('#time').input_value()=='1899'
 page.locator('#speed').select_option('0.25');page.locator('#play').click();page.wait_for_timeout(1200);checks['quarter_speed_clock']=200<float(page.locator('#time').input_value())<400;page.wait_for_timeout(6800);checks['quarter_once_stops']=page.locator('#play').inner_text()=='เล่น'
 page.locator('#loop').check();page.locator('#speed').select_option('1');page.locator('#play').click();page.wait_for_timeout(2150);checks['review_loop']=page.locator('#play').inner_text()=='หยุด'
 page.locator('#time').evaluate('(e)=>{e.value=830;e.dispatchEvent(new Event("input"))}');page.locator('#next').click();checks['next_key']='ทดลอง 11/16' in page.locator('#status').inner_text();page.locator('#prev').click();checks['prev_key']='ทดลอง 10/16' in page.locator('#status').inner_text();page.locator('#grid').uncheck();checks['grid_off']=not page.locator('#grid').is_checked()
 page.screenshot(path=str(P/'browser-review.png'),full_page=True);page.set_viewport_size({'width':390,'height':844});checks['mobile_no_overflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth');checks['no_errors']=not errors;checks['no_external_network']=not external;browser.close()
server.shutdown();server.server_close();report={'checks':checks,'pass':all(checks.values()),'errors':errors,'production_pass':False,'scope':'Synchronized8/16 clocks, decode and controls; not painted motion acceptance'};(P/'browser-qa.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(0 if report['pass'] else 1)
