"""Real UI selection, persistent nodes, and gameplay effects; no runtime setters."""
import argparse,json,math
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8000');parser.add_argument('--output',default='/tmp/astraeon-node-qa');args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True);checks=[];errors=[];http=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 def start(cls):
  context=browser.new_context(viewport={'width':1280,'height':800});page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:http.append(f'{r.status} {r.url}') if r.status>=400 else None);page.goto(args.url+'/index.html?qa=1',wait_until='networkidle');page.locator('#newclass').select_option(str(cls));page.locator('#create').click();page.wait_for_selector('#world');return context,page
 def snap(page):return page.evaluate('AstraeonQA.snapshot()')
 def point(page,x,y):
  s=snap(page);r=page.locator('#world').bounding_box();v=s['view'];return r['x']+r['width']/2+(x*48-y*10-s['camera']['x'])*v['zoom'],r['y']+r['height']*v['anchorY']+(x*7+y*31-s['camera']['y'])*v['zoom']
 def equip(page,skill,node):
  page.locator('[data-open="skills"]').click();page.locator(f'[data-node-skill="{skill}"][data-node="{node}"]').click();assert snap(page)['save']['skillNodes'][skill]==node;page.keyboard.press('Escape')
 def field(page,y=20):
  page.locator('[data-open="map"]').click();page.locator('[data-travel="2"]').click();page.wait_for_function('AstraeonQA.snapshot().save.zone===2');page.mouse.click(*point(page,14.5,y));page.wait_for_function('(y)=>Math.hypot(AstraeonQA.snapshot().player.position.x-14.5,AstraeonQA.snapshot().player.position.y-y)<.4',arg=y)
 def passed(name,data):checks.append({'name':name,'evidence':data});print('PASS',name,json.dumps(data),flush=True)
 context,page=start(12);page.locator('[data-open="character"]').click();assert page.locator('[data-path]').count()==0;page.keyboard.press('Escape');equip(page,'tempest','fire');equip(page,'tempest','ice');page.locator('[data-open="skills"]').click();assert page.locator('[data-base-skill]').count()==4;assert page.locator('[data-weave]').count()==0;assert page.locator('[data-node-skill="tempest"][aria-pressed="true"]').count()==1;assert page.locator('[data-node-skill="tempest"][data-node="plasma"]').count()==0;page.screenshot(path=str(out/'skills-desktop.png'));page.set_viewport_size({'width':390,'height':844});assert not page.locator('#actions').is_visible();page.locator('#modal').evaluate('(m)=>m.scrollTop=0');page.screenshot(path=str(out/'skills-portrait.png'));page.locator('[data-base-skill="tempest"]').scroll_into_view_if_needed();page.locator('[data-node-skill="tempest"][data-node="fire"]').click();assert snap(page)['save']['skillNodes']['tempest']=='fire';page.locator('[data-node-skill="tempest"][data-node="ice"]').click();page.screenshot(path=str(out/'skills-portrait-tempest.png'));page.keyboard.press('Escape');page.reload(wait_until='networkidle');page.wait_for_selector('#world');assert snap(page)['save']['skillNodes']=={'tempest':'ice'};context.close();passed('authored compatibility, one-layer replacement, Tier-1 controls and reload',{'base_skills':4,'saved_node':'ice','advanced_controls':0,'composer_controls':0})
 for node in ['fire','ice','gravity','lightning','void','spirit']:
  context,page=start(12);equip(page,'tempest',node);field(page);
  if node=='spirit':
   page.wait_for_function('AstraeonQA.snapshot().save.hp<AstraeonQA.snapshot().save.maxHp',timeout=15000);t=snap(page)['time'];page.wait_for_function('(t)=>AstraeonQA.snapshot().time>t',arg=t+.8);page.wait_for_function('AstraeonQA.snapshot().enemies.every(e=>!e.windup)',timeout=15000)
  page.keyboard.press('4');page.wait_for_function('(node)=>AstraeonQA.snapshot().nodeEvents.some(e=>e.skill==="tempest"&&e.node===node)',arg=node);page.wait_for_function('AstraeonQA.snapshot().time>3');start_time=snap(page)['time'];page.wait_for_function('(time)=>AstraeonQA.snapshot().time>time',arg=start_time+2.2);s=snap(page);events=[e for e in s['nodeEvents'] if e['skill']=='tempest'];assert events
  if node=='fire':assert any((e.get('burnUntil') or 0)>e['time'] for e in events)
  if node=='ice':assert any((e.get('frozenUntil') or 0)>e['time'] for e in events),events
  if node=='gravity':assert any(math.hypot(e['to']['x']-e['from']['x'],e['to']['y']-e['from']['y'])>.15 for e in events),events
  if node=='lightning':assert any((e.get('stunnedUntil') or 0)>e['time'] for e in events)
  if node=='void':assert any((e.get('attackDelayedUntil') or 0)>e['time'] for e in events)
  if node=='spirit':assert any((e.get('healed') or 0)>0 for e in events),events
  page.screenshot(path=str(out/f'tempest-{node}.png'));passed('Tempest '+node+' contacts through gameplay',{'contacts':len(events),'node':node,'remaining_fields':len(s['skillFields'])});context.close()
 for cls,skill,node,slot in [(0,'rising-edge','qi','1'),(3,'piercing-arrow','plasma','1'),(3,'piercing-arrow','wind','1')]:
  context,page=start(cls);equip(page,skill,node);field(page)
  if cls==0:page.mouse.click(*point(page,14.5,22));page.wait_for_function('AstraeonQA.snapshot().player.position.y>21.4')
  position=snap(page)['player']['position'];page.keyboard.press(slot);page.wait_for_function('(node)=>AstraeonQA.snapshot().nodeEvents.some(e=>e.node===node)',arg=node,timeout=15000);s=snap(page);events=[e for e in s['nodeEvents'] if e['node']==node]
  if node=='qi':assert any(e.get('restore')==4 for e in events)
  if node=='plasma':
   assert any(e.get('heat') for e in events);assert s['playerBursts'];hp=[e['hp'] for e in s['enemies']];later=s['time']+1.2;page.wait_for_function('(time)=>AstraeonQA.snapshot().time>time',arg=later);assert any(e['hp']<before for e,before in zip(snap(page)['enemies'],hp))
  if node=='wind':assert math.hypot(s['player']['position']['x']-position['x'],s['player']['position']['y']-position['y'])>.3
  passed(skill+' '+node+' preserves class behavior',{'contacts':len(events),'class':cls});context.close()
 browser.close()
report={'checks':checks,'runtime_errors':errors,'http_errors':http};(out/'report.json').write_text(json.dumps(report,indent=2));assert not errors and not http,report;print(json.dumps({'passed':len(checks),'errors':errors,'http_errors':http,'artifacts':str(out)},indent=2))
