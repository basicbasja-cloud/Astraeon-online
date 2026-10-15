#!/usr/bin/env python3
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial
P=Path(__file__).resolve().parent
checks={};errors=[];requests=[]
server=ThreadingHTTPServer(('127.0.0.1',0),partial(SimpleHTTPRequestHandler,directory=str(P)))
threading.Thread(target=server.serve_forever,daemon=True).start()
origin=f'http://127.0.0.1:{server.server_port}'
with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1400,'height':1000})
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.route('http://**/*',lambda route:route.continue_() if route.request.url.startswith(origin+'/') else (requests.append(route.request.url),route.abort()))
    page.route('https://**/*',lambda route:(requests.append(route.request.url),route.abort()))
    page.goto(origin+'/review.html');page.wait_for_function('window.reviewReady===true')
    checks['all_images_decoded']=page.evaluate('Object.values(drawings).every(im=>im.complete&&im.naturalWidth===1536&&im.naturalHeight===1024)')
    checks['default_selected_attempt3']=page.locator('#attempt').input_value()=='3'
    for k in range(8):
        page.locator('#key').evaluate('(e,k)=>{e.value=k;e.dispatchEvent(new Event("input"))}',k)
        checks[f'step_{k}']=f'เฟรม {k+1}/8' in page.locator('#label').inner_text()
    page.locator('#play').click();page.wait_for_timeout(2150)
    checks['normal_once_stops_at_last']=page.locator('#play').inner_text()=='เล่น' and page.locator('#key').input_value()=='7'
    page.locator('#speed').select_option('0.25');page.locator('#play').click();page.wait_for_timeout(1200)
    checks['quarter_speed_advances_slowly']=int(page.locator('#key').input_value()) in [1,2]
    page.wait_for_timeout(6800)
    checks['quarter_once_stops']=page.locator('#key').input_value()=='7' and page.locator('#play').inner_text()=='เล่น'
    page.locator('#loop').check();page.locator('#speed').select_option('1');page.locator('#play').click();page.wait_for_timeout(2150)
    checks['review_loop_continues']=page.locator('#play').inner_text()=='หยุด'
    page.locator('#key').evaluate('(e)=>{e.value=5;e.dispatchEvent(new Event("input"))}')
    for v in ['1','2','3']:
        page.locator('#attempt').select_option(v);checks['candidate_control_'+v]=page.locator('#attempt').input_value()==v
    page.locator('#grid').uncheck();checks['grid_off']=not page.locator('#grid').is_checked()
    page.screenshot(path=str(P/'evidence/current-comparison.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844});checks['mobile_no_horizontal_overflow']=page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    checks['no_page_errors']=not errors;checks['no_external_network']=not requests
    browser.close()
server.shutdown();server.server_close()
report={'pass':all(checks.values()),'checks':checks,'errors':errors,'production_pass':False,'scope':'Actual offline viewer controls/decode/normal and quarter-speed clocks; anatomy reviewed separately'}
(P/'browser-qa.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));raise SystemExit(0 if report['pass'] else 1)
