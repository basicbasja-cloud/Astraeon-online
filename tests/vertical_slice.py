"""Play the authored slice through real UI input from a new Ranger save.
No runtime setters, teleport hooks, damage cheats or seeded high-level stats.
Run against the static server; artifacts are written outside the checkout.
"""
import argparse,json,math,time
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8000');parser.add_argument('--output',default='/tmp/astraeon-slice-qa');args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
checks=[];errors=[];resources=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);context=browser.new_context(viewport={'width':1280,'height':800});page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:resources.append(f'{r.status} {r.url}') if r.status>=400 else None)
 page.goto(args.url+'/index.html?qa=1',wait_until='networkidle');page.wait_for_selector('#create');page.locator('#newclass').select_option('3');page.locator('#newname').fill('Moonveil journey');page.locator('#create').click();page.wait_for_selector('#world')
 def snap():return page.evaluate('AstraeonQA.snapshot()')
 def elapsed(seconds):
  start=snap()['time'];page.wait_for_function('(time)=>AstraeonQA.snapshot().time>=time',arg=start+seconds,timeout=20000)
 def point(x,y):
  s=snap();r=page.locator('#world').bounding_box();return r['x']+x*48-y*10+r['width']/2-s['camera']['x'],r['y']+x*7+y*31+r['height']/2-s['camera']['y']
 def click(x,y):
  px,py=point(x,y);r=page.locator('#world').bounding_box();assert r['x']<px<r['x']+r['width'] and r['y']<py<r['y']+r['height'],('target outside viewport',x,y,px,py);page.mouse.click(px,py)
 def walk(x,y,reach=.5):
  click(x,y);page.wait_for_function('(goal)=>{const p=AstraeonQA.snapshot().player.position;return Math.hypot(p.x-goal.x,p.y-goal.y)<goal.reach}',arg={'x':x,'y':y,'reach':reach},timeout=20000);elapsed(.1)
 def pass_check(name,evidence):checks.append({'name':name,'evidence':evidence});print('PASS',name,json.dumps(evidence),flush=True)
 def fight_until(predicate,timeout=75):
  deadline=time.monotonic()+timeout
  while time.monotonic()<deadline:
   s=snap();(out/'latest-state.json').write_text(json.dumps({'position':s['player']['position'],'time':s['time'],'save':s['save'],'dungeon':s['dungeon']}))
   if predicate(s):return s
   alive=[e for e in s['enemies'] if e['hp']>0]
   if not alive:
    elapsed(.2);continue # Allow the final death pose/reward transition to finish.
   position=s['player']['position'];enemy=min(alive,key=lambda e:math.hypot(e['transform']['position']['x']-position['x'],e['transform']['position']['y']-position['y']));target=enemy['transform']['position'];distance=math.hypot(target['x']-position['x'],target['y']-position['y'])
   px,py=point(target['x'],target['y']-.35);rect=page.locator('#world').bounding_box()
   if not (rect['x']+20<px<rect['x']+rect['width']-20 and rect['y']+20<py<rect['y']+rect['height']-35):
    # Use authored road waypoints when the intended enemy is outside the visible world.
    roads=[(14,17),(14.5,8),(14.5,21)] if s['save']['zone']==2 else [(14.5,14),(14.5,9.5)]
    candidates=[]
    for waypoint in roads:
     wx,wy=point(*waypoint)
     if rect['x']+20<wx<rect['x']+rect['width']-20 and rect['y']+20<wy<rect['y']+rect['height']-35 and math.hypot(waypoint[0]-position['x'],waypoint[1]-position['y'])>.7:candidates.append(waypoint)
    assert candidates,('no visible road waypoint',position,target)
    waypoint=min(candidates,key=lambda point:math.hypot(point[0]-target['x'],point[1]-target['y']))
    click(*waypoint);elapsed(2);continue
   click(target['x'],target['y']-.35);button=page.locator('[data-action="attack"]').bounding_box();page.mouse.move(button['x']+button['width']/2,button['y']+button['height']/2);page.mouse.down();elapsed(1.3);page.mouse.up()
   state=snap()['save'];assert state['hp']>0,('player defeated',state)
   if state['hp']<state['maxHp']*.55 and state['inventory']['potion']>0:page.keyboard.press('q')
   elif state['hp']<state['maxHp']*.7 and state['energy']>=18:page.keyboard.press('3')
  raise AssertionError(('combat deadline',snap()))
 page.locator('[data-open="journal"]').click();page.locator('[data-quest="2"]').click();initial=snap()['save'];assert initial['quest']['id']==2
 walk(22,16);click(27.5,14);page.wait_for_function('AstraeonQA.snapshot().save.zone===2');field=fight_until(lambda s:s['save']['clears']>=1);assert field['save']['lv']>=2;assert field['save']['quest'] is None;page.screenshot(path=str(out/'goldenfield.png'));pass_check('new adventurer gate, field combat and contract rewards',{'level':field['save']['lv'],'kills':field['save']['kills'],'clears':field['save']['clears']})
 # Follow the caravan branch instead of teleporting to the supply cache.
 walk(14.5,12);walk(14,17);walk(9.5,19);gold=snap()['save']['gold'];click(10.6,23.1);page.wait_for_function('AstraeonQA.snapshot().save.worldClaims?.["caravan-cache"]===true');after=snap()['save'];assert after['gold']==gold+12;click(10.6,23.1);elapsed(.1);assert snap()['save']['gold']==after['gold'];pass_check('world supply chest awards once',{'gold_added':12,'claim_saved':True})
 walk(14,17);walk(14.5,8);click(14.5,2);page.wait_for_function('AstraeonQA.snapshot().save.zone===1');walk(16.5,19);walk(14.5,14);walk(14.5,11.5,reach=.35);page.screenshot(path=str(out/'moonbamboo.png'));page.keyboard.press('e');page.wait_for_function('AstraeonQA.snapshot().dungeon?.wave===0');pass_check('natural forest route and shrine entry',{'zone':1,'entry':'world interaction'})
 rewards_before=snap()['save'];rooms=[]
 page.evaluate("window.encounterSamples=[];window.collectEncounter=true;const sample=()=>{if(!collectEncounter)return;const s=AstraeonQA.snapshot();if(s.dungeon?.wave===3){const b=s.enemies.find(e=>e.boss);if(b)encounterSamples.push({time:s.time,hp:b.hp,phase:b.phase,shape:b.windup?.shape,attack:b.windup?.name,hazards:s.hazards.length})}requestAnimationFrame(sample)};requestAnimationFrame(sample)")
 for wave in range(4):
  fought=fight_until(lambda s: not s['dungeon'] or s['dungeon']['cleared'],timeout=90);rooms.append(wave)
  if wave<3:
   assert fought['dungeon']['wave']==wave;door=[(8,14.8),(14.5,9),(21,14.8)][wave];click(*door);page.wait_for_function('(wave)=>AstraeonQA.snapshot().dungeon?.wave===wave+1',arg=wave,timeout=20000);elapsed(1.3)
  else:assert fought['dungeon'] is None
 page.evaluate('collectEncounter=false');samples=page.evaluate('encounterSamples');saved=snap()['save'];assert saved['bossKills']==1;assert 0 in saved['chapters'];assert saved['equipment']['relic']=='Moonveil Sigil';assert saved['gold']>=rewards_before['gold']+65;assert abs(saved['x']-14.5)<.1 and abs(saved['y']-9.5)<.1;assert {0,1}.issubset({s['phase'] for s in samples});assert any(s['attack'] for s in samples),samples
 page.screenshot(path=str(out/'shrine-return.png'));pass_check('four rooms, boss phases, relic reward and safe return',{'rooms':rooms,'boss_phases':sorted({s['phase'] for s in samples}),'telegraphs':sorted({s['attack'] for s in samples if s['attack']}),'boss_kills':1,'relic':saved['equipment']['relic']})
 # Material rewards support actual crafting/equipment, followed by persistent reload.
 assert saved['inventory']['ore']>=6,saved['inventory'];page.locator('[data-open="systems"]').click();page.locator('[data-nav="craft"]').click();page.locator('[data-craft="2"]').click();assert snap()['save']['inventory']['plate']==1;page.keyboard.press('Escape');page.locator('[data-open="inventory"]').click();page.locator('[data-item="plate"]').click();page.keyboard.press('Escape');assert snap()['save']['equipment']['armor']=='Warden Plate';before=snap()['save'];page.reload(wait_until='networkidle');page.wait_for_selector('#world');after=snap()['save'];assert before['gold']==after['gold'];assert before['inventory']==after['inventory'];assert before['equipment']==after['equipment'];assert after['worldClaims']['caravan-cache'];assert after['chapters']==before['chapters'];pass_check('crafted equipment, first clear and world claims survive reload',{'armor':after['equipment']['armor'],'save_version':after['saveVersion']})
 context.close();browser.close()
report={'checks':checks,'runtime_errors':errors,'resource_errors':resources};(out/'report.json').write_text(json.dumps(report,indent=2));assert not errors and not resources,report
print(json.dumps({'passed':len(checks),'runtime_errors':errors,'resource_errors':resources,'artifacts':str(out)},indent=2))
