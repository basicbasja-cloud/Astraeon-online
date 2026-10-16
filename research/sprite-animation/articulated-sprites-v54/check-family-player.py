"""Exercise the standalone multi-view review tool and compare actual exported pixels."""
from pathlib import Path
import json,io,base64,hashlib
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent;checks={};errors=[];network=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page(viewport={'width':1100,'height':950});p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) else None);p.context.set_offline(True);p.set_content((P/'walk-family-review.html').read_text(),wait_until='load');p.wait_for_function('window.READY===true')
 for v in ['S','SW','W','NW','N','NE','E','SE']:
  p.locator('#view').select_option(v);p.wait_for_function('(v)=>window.READY&&study.view===v',arg=v);assert len(p.evaluate('Array.from(study.layers.keys())'))==6
  for i in [0,20,40,60,79]:
   raw=p.evaluate('i=>study.frame(i)',i);actual=np.array(Image.open(io.BytesIO(base64.b64decode(raw.split(',')[1]))));expected=np.array(Image.open(P/'walk'/v/f'{i:02}.png'));assert np.array_equal(actual,expected),(v,i)
  p.locator('#speed').select_option('0.25');p.locator('#loop').uncheck();p.evaluate('study.select(0)');p.locator('#play').click();p.wait_for_function('study.clock.finished',timeout=12000);assert p.locator('#frame').input_value()=='79';checks[v]={'actual_exported_pixel_comparisons':5,'quarter_speed_one_shot':True}
 # Exercise resource release and latest-request-wins loading without relying on GC timing.
 for i in range(18):
  v=['W','NE','S'][i%3];p.locator('#view').select_option(v);p.wait_for_function('(v)=>window.READY&&study.view===v',arg=v)
 p.evaluate("Promise.all([study.choose('N'),study.choose('SW'),study.choose('E')])");p.wait_for_function("window.READY&&study.view==='E'");assert p.locator('#view').input_value()=='E';checks['repeated_switches_and_latest_request_wins']=True
 p.locator('#travel').check();assert p.locator('#loop').is_disabled() and not p.locator('#loop').is_checked();p.locator('#speed').select_option('1');p.locator('#play').click();p.wait_for_function('study.clock.finished',timeout=6000);assert p.evaluate("document.getElementById('c').width")==768;checks['world_one_shot']=True
 p.locator('#travel').uncheck();p.evaluate('study.select(20)');p.screenshot(path=str(P/'walk-family-player-verified.png'),full_page=True);b.close()
assert not errors and not network;(P/'family-player-qa.json').write_text(json.dumps({'pass':True,'checks':checks,'page_errors':errors,'external_network_requests':network,'standalone_html_sha256':hashlib.sha256((P/'walk-family-review.html').read_bytes()).hexdigest(),'scope':'Standalone document content evaluated offline, 8 view switches and actual pixels/clocks. Managed browser blocks file:// navigation, so this does not certify its file-open policy. Not game-engine integration or universal rig approval.'},indent=2)+'\n');print(checks)
