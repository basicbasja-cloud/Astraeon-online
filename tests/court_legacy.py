"""Preserved court diagnostic boots and walks via ordinary input."""
import argparse,json,math
from pathlib import Path
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']);page=b.new_page(viewport={'width':910,'height':512});page.set_default_timeout(180000);page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto('http://127.0.0.1:8011/?qa=1&world=court-legacy',wait_until='domcontentloaded');page.locator('#newname').fill('Legacy Court');page.locator('#create').click();page.wait_for_function('document.getElementById("world") && window.AstraeonQA?.snapshot().time>0');before=page.evaluate('AstraeonQA.snapshot()');assert not page.evaluate('!!AstraeonContent.nativeWorld.spatial.scene.streaming')
 target=page.evaluate('''()=>{const s=AstraeonQA.snapshot(),w=AstraeonContent.nativeWorld.spatial,v=window.AstraeonSpatialView,r=world.getBoundingClientRect(),p=s.player.position;return w.navCells.filter(q=>q.walkable&&Math.hypot(q.x-p.x,q.y-p.y)>1.5&&Math.hypot(q.x-p.x,q.y-p.y)<3&&AstraeonNavigation.clear(p,q,w.blocked)).map(q=>{const t=AstraeonView.screen(q.x,q.y,w.elevationAt(q.x,q.y)*35,s.camera,r.width,r.height);return {q,screen:[t.x+r.x,t.y+r.y],hit:v?.pickActor(t.x,t.y)}}).find(q=>document.elementFromPoint(...q.screen)?.id==='world'&&!q.hit?.startsWith('service/'))}''');assert target;page.mouse.click(*target['screen']);page.wait_for_function('q=>{const p=AstraeonQA.snapshot().player.position;return Math.hypot(p.x-q.x,p.y-q.y)<.4}',arg=target['q']);after=page.evaluate('AstraeonQA.snapshot()');page.screenshot(path=str(a.output/'court-walk.png'));assert not errors,errors
 (a.output/'report.json').write_text(json.dumps({'legacyDiagnosticPreserved':True,'ordinaryClickWalk':True,'before':before['player']['position'],'after':after['player']['position'],'errors':errors},indent=2)+'\n');b.close()
print('PASS original court-legacy boot and ordinary walk',flush=True)
