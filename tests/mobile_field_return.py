"""Enter the original field and return through real gate input, no setters."""
import argparse,json,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
errors=[];requests=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']);c=b.new_context(**p.devices['iPhone 13']);page=c.new_page();page.set_default_timeout(180000);page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:requests.append(r.url))
 page.goto('http://127.0.0.1:8011/?qa=1',wait_until='domcontentloaded');page.locator('#newname').fill('Mobile Field Return');page.locator('#create').click();page.wait_for_function('document.getElementById("world") && window.AstraeonQA?.snapshot().time>0 && AstraeonWorldStreaming.readyForMovement')
 before=page.evaluate('AstraeonQA.snapshot().save');assert not any('town-atlas-v1.webp' in r for r in requests),'legacy Canvas sheet downloaded during city boot'
 def gate(x,y):
  q=page.evaluate('''([x,y])=>{const s=AstraeonQA.snapshot(),r=world.getBoundingClientRect(),p=AstraeonView.screen(x,y,0,s.camera,r.width,r.height);return [p.x+r.x,p.y+r.y-17]}''',[x,y]);assert page.evaluate('p=>document.elementFromPoint(...p)?.id===\'world\'',q),q;page.touchscreen.tap(*q)
 gate(8.599998474121094,143.99998474121094);page.wait_for_function('AstraeonQA.snapshot().save.zone===2');page.wait_for_function('AstraeonWorldStreaming.loaded.size===0');field=page.evaluate('({save:AstraeonQA.snapshot().save,stream:AstraeonWorldStreaming.snapshot(),sceneReady:!!AstraeonScene.ready()})');assert field['sceneReady'];assert field['save']['name']==before['name'];assert any('town-atlas-v1.webp' in r for r in requests);page.screenshot(path=str(a.output/'field-mobile.png'))
 gate(2.5,14);page.wait_for_function('AstraeonQA.snapshot().save.zone===0 && AstraeonWorldStreaming.readyForMovement');returned=page.evaluate('({save:AstraeonQA.snapshot().save,stream:AstraeonWorldStreaming.snapshot()})');assert returned['stream']['reloads']>0;assert returned['save']['name']==before['name'];assert returned['save']['gold']==before['gold'];page.screenshot(path=str(a.output/'city-return-mobile.png'));assert not errors,errors
 (a.output/'report.json').write_text(json.dumps({'physicalIPhoneSafari':'PENDING','normalTouchGateEntry':True,'cityGeometryReleasedInField':True,'lazyOriginalFieldArt':True,'field':field,'returned':returned,'errors':errors},indent=2)+'\n');b.close()
print('PASS ordinary mobile field gate, lazy original field art, city release and exact return reload',flush=True)
