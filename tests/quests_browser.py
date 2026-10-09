"""Quest acceptance: semantic NPC interaction, ordinary travel/movement and real Combat.
Isolated capacity/authorization fixtures never mutate Quest progress or enemy HP.
"""
import argparse,json,math,os,tempfile,time
from pathlib import Path
from playwright.sync_api import sync_playwright,TimeoutError as PlaywrightTimeout
ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8011');ap.add_argument('--browser',default=os.environ.get('ASTRAEON_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe'));ap.add_argument('--output',type=Path,default=Path(tempfile.gettempdir())/'astraeon-quests-browser');ap.add_argument('--classes',default='0,12');args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
checks,errors,http_errors,observations=[],[],[],[];report={};last_page=None;last_snapshot=None

def passed(name,evidence=None):
 checks.append({'name':name,'evidence':evidence});print('PASS',name,flush=True);checkpoint()
def checkpoint():
 (args.output/'progress.json').write_text(json.dumps({'checks':checks,'errors':errors,'httpErrors':http_errors,'observations':observations},indent=2)+'\n',encoding='utf-8')
def qa(page):
 global last_snapshot
 last_snapshot=page.evaluate('AstraeonQA.snapshot()');return last_snapshot
def dev(page,code):return page.evaluate('()=>{const d=AstraeonProgressionDev,q=AstraeonQuestDev;'+code+'}')
def quest(page,key):return dev(page,'return q.inspect("quest-proof-'+key+'")')
def snap(page):return dev(page,'return d.snapshot()')
def close(page):
 if qa(page)['windowName']:page.keyboard.press('Escape');page.locator('#modal').wait_for(state='hidden')
def pause(page):close(page);page.locator('[data-open="character"]').click()
def elapsed(page,seconds):page.wait_for_function('v=>AstraeonQA.snapshot().time>=v',arg=qa(page)['time']+seconds,timeout=60000)
def keyboard_step(page,at,distance=1):
 origin=qa(page)['player']['position'];keys=page.evaluate('''g=>{const p=AstraeonQA.snapshot().player.position,dx=g.x-p.x,dy=g.y-p.y;return [['d'],['s','d'],['s'],['s','a'],['a'],['w','a'],['w'],['w','d']].map(keys=>{const v=AstraeonMotion.cameraMovement(keys.includes('d')?1:keys.includes('a')?-1:0,keys.includes('s')?1:keys.includes('w')?-1:0,AstraeonView.inverse);return {keys,score:v.x*dx+v.y*dy}}).sort((a,b)=>b.score-a.score)[0].keys}''',at)
 for k in keys:page.keyboard.down(k)
 try:page.wait_for_function('({p,d})=>{const s=AstraeonQA.snapshot().player.position;return Math.hypot(s.x-p.x,s.y-p.y)>=d}',arg={'p':origin,'d':distance},timeout=10000)
 finally:
  for k in keys:page.keyboard.up(k)
def field_point(page,at):
 s=qa(page);r=page.locator('#world').bounding_box();v,c=s['view'],s['camera'];return [r['x']+r['width']/2+(at['x']*v['basis']['xx']+at['y']*v['basis']['yx']-c['x'])*v['zoom'],r['y']+r['height']*v['anchorY']+(at['x']*v['basis']['xy']+at['y']*v['basis']['yy']-c['y'])*v['zoom']]
def npc_interaction(page):
 close(page);npc=next(n['transform']['position'] for n in qa(page)['npcs'] if n['id']=='guild-registrar')
 approach=page.evaluate('''n=>{const w=AstraeonContent.nativeWorld.spatial,start=AstraeonQA.snapshot().player.position;return w.navCells.filter(p=>p.walkable&&Math.hypot(p.x-n.x,p.y-n.y)>2.3&&Math.hypot(p.x-n.x,p.y-n.y)<3.2).sort((a,b)=>Math.hypot(a.x-n.x,a.y-n.y-2.8)-Math.hypot(b.x-n.x,b.y-n.y-2.8)).find(p=>w.route(start,p))}''',npc);assert approach
 walk(page,approach['x'],approach['y'])
 picked=page.evaluate('''n=>{const r=world.getBoundingClientRect(),v=AstraeonQA.snapshot().view,p=AstraeonSpatialView.worldToScreen(n.x,n.y,AstraeonContent.nativeWorld.spatial.elevationAt(n.x,n.y));for(const dy of [35,45,55,25,65,15])for(const dx of [0,6,-6,12,-12,18,-18]){const x=p.x+dx*v.zoom,y=p.y-dy*v.zoom;if(AstraeonSpatialView.pickActor(x,y)==='service/guild-registrar')return [r.x+x,r.y+y]}return null}''',npc);assert picked,('NPC occlusion',npc,qa(page)['player']);page.mouse.click(*picked);page.wait_for_selector('#modal:not([hidden])');assert qa(page)['windowName']=='guild'
def accept(page,key):page.locator('[data-quest-accept="quest-proof-'+key+'"]').click();assert quest(page,key)['status'] in ['ACTIVE','READY_TO_TURN_IN']
def turn_in(page,key):page.locator('[data-quest-turn-in="quest-proof-'+key+'"]').click();assert quest(page,key)['status']=='COMPLETED'
def travel(page,zone):
 close(page);page.locator('[data-open="map"]').click();page.locator('[data-travel="'+str(zone)+'"]').click();page.wait_for_function('z=>AstraeonQA.snapshot().save.zone===z&&AstraeonQA.snapshot().windowName!=="loading"',arg=zone);close(page)
def actor(page,id):return next(e['lifecycle'] for e in qa(page)['enemies'] if e['lifecycle']['instanceId']==id)
def fight(page,id,skill=None):
 deadline=time.monotonic()+240;skill_hit=False
 while actor(page,id)['hp']>0:
  assert time.monotonic()<deadline,('bounded real encounter',actor(page,id),qa(page)['navigation']);close(page);page.wait_for_function('!AstraeonQA.snapshot().action')
  s=qa(page);a=actor(page,id);at=a['position'];p=s['player']['position'];distance=math.hypot(at['x']-p['x'],at['y']-p['y']);x,y=field_point(page,at)
  if not page.evaluate('p=>document.elementFromPoint(p[0],p[1]-16)?.id==="world"',[x,y]):keyboard_step(page,at);continue
  page.mouse.click(x,y-16)
  try:page.wait_for_function('({id,reach})=>{const s=AstraeonQA.snapshot(),m=s.enemies.find(e=>e.lifecycle.instanceId===id)?.lifecycle;return m?.hp===0||Math.hypot(s.player.position.x-m.position.x,s.player.position.y-m.position.y)<=reach}',arg={'id':id,'reach':2 if s['save']['cls']==0 else 5.5},timeout=15000)
  except PlaywrightTimeout:
   observations.append({'event':'real encounter approach retry','state':actor(page,id),'navigation':qa(page)['navigation']});checkpoint();keyboard_step(page,actor(page,id)['position']);continue
  if actor(page,id)['hp']==0:break
  if skill and not skill_hit:
   page.wait_for_function('!AstraeonQA.snapshot().action');page.keyboard.press('1')
   try:page.wait_for_function('skill=>AstraeonCombatDev.results().some(r=>r.result.ok&&r.result.input.context.sourceSkillId===skill)',arg=skill,timeout=10000);skill_hit=True
   except PlaywrightTimeout:observations.append({'event':'learned skill contact retry','state':actor(page,id)});checkpoint()
  if actor(page,id)['hp']==0:break
  b=page.locator('[data-action="attack"]').bounding_box();page.mouse.move(b['x']+b['width']/2,b['y']+b['height']/2);page.mouse.down()
  try:page.wait_for_function('id=>AstraeonQA.snapshot().enemies.find(e=>e.lifecycle.instanceId===id)?.hp===0',arg=id,timeout=7000)
  except PlaywrightTimeout:
   observations.append({'event':'bounded Basic Attack retarget','state':actor(page,id)});checkpoint()
  finally:page.mouse.up()
  if actor(page,id)['hp']>0:keyboard_step(page,actor(page,id)['position'],.5)
 if skill:assert skill_hit,('no learned Skill contact',skill,actor(page,id))
 pause(page);return actor(page,id)

def walk_route(page,x,y):
 start=qa(page)['player']['position']
 if math.hypot(x-start['x'],y-start['y'])<=.4:elapsed(page,.2);return
 initial_route=page.evaluate('(g)=>AstraeonContent.nativeWorld.spatial.route(AstraeonQA.snapshot().player.position,{x:g[0],y:g[1]})',[x,y])
 assert initial_route,('no route',x,y,start)
 length=0;previous=start
 for waypoint in initial_route:length+=math.hypot(waypoint['x']-previous['x'],waypoint['y']-previous['y']);previous=waypoint
 # Account for actual detours and the existing 250ms simulation-delta cap
 # when cloud RAF intervals are longer. Only the bounded test deadline changes;
 # game input, simulation clock, travel speed and performance gates stay intact.
 slowdown=max(1,min(4,page.evaluate('AstraeonQA.performance().intervalMs')/250))
 deadline=time.monotonic()+max(90,length/1.3+45)*slowdown;last_click=None
 while True:
  # Observe both coordinates in one live snapshot. Separate cross-process
  # reads can straddle movement frames and manufacture a position the actor
  # never occupied; the arrival tolerance and travel deadline stay unchanged.
  observed=qa(page);current=observed['player']['position']
  if math.hypot(current['x']-x,current['y']-y)<=.4:break
  if time.monotonic()>=deadline:
   page.screenshot(path=str(args.output/'failure.png'));raise AssertionError(('walk timeout',x,y,last_click,observed['navigation'],observed['windowName'],observed['player']))
  route=page.evaluate('(g)=>AstraeonContent.nativeWorld.spatial.route(AstraeonQA.snapshot().player.position,{x:g[0],y:g[1]})', [x,y]);assert route,('no route',x,y,qa(page)['player']['position'],qa(page)['navigation'])
  candidates=[];previous=qa(page)['player']['position']
  for q in route:
   n=math.ceil(math.hypot(q['x']-previous['x'],q['y']-previous['y'])/2)
   candidates.extend({'x':previous['x']+(q['x']-previous['x'])*i/max(1,n),'y':previous['y']+(q['y']-previous['y'])*i/max(1,n)} for i in range(1,n+1));previous=q
  selected=page.evaluate("""(qs)=>{const s=AstraeonQA.snapshot(),r=world.getBoundingClientRect(),v=s.view;
   return qs.map(q=>{const p=AstraeonSpatialView.worldToScreen(q.x,q.y,AstraeonContent.nativeWorld.spatial.elevationAt(q.x,q.y)),px=p.x,py=p.y;
    return {q,screen:[r.x+px,r.y+py],inside:px>30&&px<r.width-30&&py>50&&py<r.height-40,element:document.elementFromPoint(r.x+px,r.y+py)?.id,pick:AstraeonSpatialView.pickActor(px,py),distance:Math.hypot(q.x-s.player.position.x,q.y-s.player.position.y)}})
   .filter(p=>p.inside&&p.element==='world'&&!p.pick?.startsWith('service/')&&p.distance>.2).at(-1);
  }""",candidates)
  if not selected:
   # An NPC's real silhouette can cover the last ground waypoint. Complete
   # only a short, straight authored route using normal keyboard movement.
   current=qa(page)['player']['position'];assert len(route)==1 and math.hypot(x-current['x'],y-current['y'])<2.6,('no clickable waypoint',x,y,route,current)
   choice=page.evaluate("""g=>{const p=AstraeonQA.snapshot().player.position,dx=g[0]-p.x,dy=g[1]-p.y;return [['d'],['s','d'],['s'],['s','a'],['a'],['w','a'],['w'],['w','d']].map(keys=>{const v=AstraeonMotion.cameraMovement(keys.includes('d')?1:keys.includes('a')?-1:0,keys.includes('s')?1:keys.includes('w')?-1:0,AstraeonView.inverse);return {keys,score:(v.x*dx+v.y*dy)/Math.hypot(dx,dy)}}).sort((a,b)=>b.score-a.score)[0]}""",[x,y])
   page.evaluate("""({goal,keys})=>{let start=null,best=Infinity;window.keyboardLegDone=false;const observe=()=>{const s=AstraeonQA.snapshot();start??=s.time;const d=Math.hypot(s.player.position.x-goal[0],s.player.position.y-goal[1]);if(d<.33||d>best+.025||s.time-start>.7){for(const key of keys)dispatchEvent(new KeyboardEvent('keyup',{key,bubbles:true}));removeEventListener('astraeon-frame',observe);keyboardLegDone=true}best=Math.min(best,d)};addEventListener('astraeon-frame',observe)}""",{'goal':[x,y],'keys':choice['keys']})
   for key in choice['keys']:page.keyboard.down(key)
   page.wait_for_function('keyboardLegDone',timeout=10000)
   for key in choice['keys']:page.keyboard.up(key)
   continue
  q=selected['q'];last_click=selected;page.mouse.click(*selected['screen']);
  try:page.wait_for_function('(g)=>{const p=AstraeonQA.snapshot().player.position;return Math.hypot(p.x-g[0],p.y-g[1])<.4||!document.querySelector("#modal").hidden}',arg=[q['x'],q['y']],timeout=12000)
  except Exception:pass
  if page.locator('#modal').is_visible():page.keyboard.press('Escape')
 elapsed(page,.2)
def walk(page,x,y):
 page.keyboard.down('Shift')
 try:walk_route(page,x,y)
 finally:
  page.keyboard.up('Shift')
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=args.browser,headless=True,args=['--no-sandbox','--enable-gpu']+(['--use-angle=d3d11'] if os.name=='nt' else ['--use-angle=swiftshader','--enable-unsafe-swiftshader']))
  def open_page(path='/?qa=1&dev=1'):
   global last_page
   context=browser.new_context(viewport={'width':1280,'height':800});page=context.new_page();last_page=page;page.set_default_timeout(180000);page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);page.on('response',lambda r:http_errors.append(f'{r.status} {r.url}') if r.status>=400 else None);page.goto(args.url.rstrip('/')+path,wait_until='load');return context,page
  for cls in args.classes.split(','):
   skill='rising-edge' if cls=='0' else 'ember-bloom';context,page=open_page();page.wait_for_selector('#create');page.locator('#newname').fill('Quest disposable '+cls);page.locator('#newclass').select_option(cls);page.locator('#create').click();page.wait_for_selector('#world');elapsed(page,.3)
   assert not qa(page)['quests']['state']['entries'] and quest(page,'chain')['status']=='LOCKED';passed('new '+cls+' character has no fabricated Quest progress or rewards')
   pause(page);setup=dev(page,"d.setBaseLevel(8);d.setBaseJobLevel(20);d.addSkillPoints(50);const learned=d.learnSkill('"+skill+"'),assigned=d.assignSkill(0,'"+skill+"');return {learned,assigned}");assert setup['learned']['ok'] and setup['assigned']['ok'];close(page)
   print('WALK registrar',cls,flush=True);npc_interaction(page);assert not qa(page)['quests']['state']['entries'];passed('actual ordinary city walk and NPC interaction do not auto-accept quests',{'class':cls,'position':qa(page)['player']['position']})
   for key in ['talk','kill','collect','mixed']:accept(page,key)
   assert quest(page,'talk')['objectives'][0]['progress']==0 and quest(page,'mixed')['objectives'][0]['progress']==0;passed('explicit acceptance starts Talk at zero; existing ownership derives Collect',{'class':cls})
   close(page);page.keyboard.press('e');page.wait_for_selector('#modal:not([hidden])');assert quest(page,'talk')['status']=='READY_TO_TURN_IN' and quest(page,'mixed')['objectives'][0]['progress']==1;passed('actual second NPC interaction satisfies independent Talk objectives once',{'class':cls})
   before=snap(page);turn_in(page,'talk');after=snap(page);assert after['baseExp']==before['baseExp']+3 and after['baseJobExp']==before['baseJobExp']+2 and after['gold']==before['gold']+4 and after['itemInventory']['stacks']['potion']==before['itemInventory']['stacks']['potion']+1;assert quest(page,'chain')['status']=='AVAILABLE';passed('Talk turn-in grants authored Base/Job EXP gold and canonical Potion once',{'class':cls})
   before=snap(page);assert dev(page,'return q.turnIn("quest-proof-talk")')['code']=='QUEST_COMPLETED' and snap(page)==before;passed('completed quest cannot reward or restart again',{'class':cls})
   accept(page,'chain');close(page);page.keyboard.press('e');page.wait_for_selector('#modal:not([hidden])');turn_in(page,'chain');assert quest(page,'chain')['status']=='COMPLETED';passed('completed-quest prerequisite unlocks and completes a non-repeatable chain',{'class':cls})
   assert quest(page,'collect')['status']=='READY_TO_TURN_IN';assert dev(page,'return d.consumeStack("herb",2)')['ok'];assert quest(page,'collect')['status']=='ACTIVE' and quest(page,'collect')['objectives'][0]['progress']==1;passed('spending canonical items invalidates Collect readiness without a second ledger',{'class':cls})
   dev(page,'d.save()');partial=snap(page);page.reload(wait_until='load');page.wait_for_selector('#world');pause(page);assert snap(page)['questState']==partial['questState'] and quest(page,'collect')['objectives'][0]['progress']==1;assert quest(page,'talk')['status']=='COMPLETED' and quest(page,'chain')['status']=='COMPLETED';passed('actual reload preserves Talk accepted chain and current Collect ownership without reward replay',{'class':cls})
   travel(page,2);pause(page);fox=next(e['lifecycle'] for e in qa(page)['enemies'] if e['lifecycle']['definitionId']=='leafmane-fox');id=fox['instanceId'];before=snap(page);close(page);dead=fight(page,id);after=snap(page)
   assert dead['deathId'] and not dead['alive'] and quest(page,'kill')['objectives'][0]['progress']==1 and quest(page,'mixed')['objectives'][1]['progress']==1;assert after['kills']==before['kills']+1 and after['gold']==before['gold']+dead['rewardResult']['currencyGranted'];passed('ordinary-input Basic Attack creates one authoritative Lifecycle death; matching quests each +1',{'class':cls,'deathId':dead['deathId'],'reward':dead['rewardResult']})
   before=snap(page);duplicate=page.evaluate('id=>AstraeonMonsterLifecycleDev.repeatDeath(id)',id);assert duplicate['duplicate'] and snap(page)==before and quest(page,'kill')['objectives'][0]['progress']==1;passed('existing death replay cannot duplicate Quest progress Loot EXP or gold',{'class':cls})
   expected_kill=1
   if cls=='12':
    close(page);page.wait_for_function('!AstraeonQA.snapshot().action');keyboard_step(page,{'x':14.5,'y':14.5},1);life=dead['lifeGeneration'];page.wait_for_function('({id,life})=>{const m=AstraeonQA.snapshot().enemies.find(e=>e.lifecycle.instanceId===id)?.lifecycle;return m?.lifeGeneration===life+1&&m.hp>0}',arg={'id':id,'life':life},timeout=60000);pause(page);newlife=actor(page,id);assert newlife['deathId'] is None and quest(page,'kill')['objectives'][0]['progress']==1
    close(page);second=fight(page,id);assert second['lifeGeneration']==life+1 and second['deathId']!=dead['deathId'] and quest(page,'kill')['objectives'][0]['progress']==2;expected_kill=2;passed('same runtime respawned new life legitimately increments active Kill from one to two',{'class':cls,'first':dead['deathId'],'second':second['deathId']})
   # Swordsman persists genuine 1/2 partial progress; Mage persists the same-
   # runtime new-life completion. Reload never replays either death.
   dev(page,'d.save()');partial=snap(page);page.reload(wait_until='load');page.wait_for_selector('#world');pause(page);assert snap(page)['questState']==partial['questState'] and quest(page,'kill')['objectives'][0]['progress']==expected_kill and not qa(page)['quests']['events'];passed('durable Kill persists; reconstructed Lifecycle does not replay historical evidence',{'class':cls})
   durable=snap(page)['questState'];travel(page,0);travel(page,2);pause(page);assert snap(page)['questState']==durable;passed('town/field round trip preserves partial state without duplicate event listeners',{'class':cls})
   # Isolated player-resource setup for death policy only. The actual enemy AI
   # causes death; no position, enemy HP, AI, collision or Quest state changes.
   dev(page,'d.setCurrentHP(1)');close(page);s=qa(page);living=min((e['lifecycle'] for e in s['enemies'] if e['hp']>0),key=lambda m:math.hypot(m['position']['x']-s['save']['x'],m['position']['y']-s['save']['y']))
   at=living['position'];position=s['player']['position'];distance=math.hypot(at['x']-position['x'],at['y']-position['y']);goal={'x':at['x']+(position['x']-at['x'])/distance*5.5,'y':at['y']+(position['y']-at['y'])/distance*5.5}
   # Latch authoritative observation before movement: HP=0 is transient until
   # auto-respawn, so two separate host waits can miss it. This observer only
   # reads QA/Combat evidence and never mutates gameplay or Quest progress.
   page.evaluate('''()=>{window.questDeathEvidence=null;window.questDeathObserver=()=>{const s=AstraeonQA.snapshot();if(s.save.currentHP===0){window.questDeathEvidence={hp:s.save.currentHP,time:s.time,questState:s.save.questState,position:s.player.position,incoming:s.incomingCombat.at(-1)};removeEventListener('astraeon-frame',window.questDeathObserver)}};addEventListener('astraeon-frame',window.questDeathObserver)}''')
   try:
    page.mouse.click(*field_point(page,goal));page.wait_for_function('g=>{const s=AstraeonQA.snapshot();return !!window.questDeathEvidence||Math.hypot(s.save.x-g.x,s.save.y-g.y)<.5}',arg=goal,timeout=30000)
    page.wait_for_function('window.questDeathEvidence?.hp===0',timeout=60000);death=page.evaluate('window.questDeathEvidence');assert death['questState']==durable and death['incoming']['hp']['killed'] and death['incoming']['hp']['hpAfter']==0
    observations.append({'event':'latched real enemy-caused player death after ordinary ground navigation','actor':living,'goal':goal,'death':death});checkpoint()
    page.wait_for_function('AstraeonQA.snapshot().save.zone===0&&AstraeonQA.snapshot().save.currentHP>0',timeout=30000);pause(page);assert snap(page)['questState']==durable;passed('real enemy damage player death and respawn retain partial Quest progress',{'class':cls,'deathTime':death['time']})
   except Exception:
    report['lastState']=qa(page);report['browserState']=page.evaluate('({hidden:document.hidden,visibilityState:document.visibilityState,performance:AstraeonQA.performance(),deathEvidence:window.questDeathEvidence})');raise
   finally:page.evaluate("removeEventListener('astraeon-frame',window.questDeathObserver);delete window.questDeathObserver")
   travel(page,2);pause(page);fox=next(e['lifecycle'] for e in qa(page)['enemies'] if e['lifecycle']['definitionId']=='leafmane-fox');id=fox['instanceId'];before=snap(page);close(page);dead=fight(page,id,skill);assert quest(page,'kill')['status']=='READY_TO_TURN_IN';passed('learned Skill contacts real monster and next legitimate death finishes Kill',{'class':cls,'deathId':dead['deathId']})
   # The same runtime actor gets a new life: use ordinary input to retreat and
   # wait on the authoritative simulation-clock/life condition.
   close(page);keyboard_step(page,{'x':14.5,'y':14.5},1);life=dead['lifeGeneration'];page.wait_for_function('({id,life})=>{const m=AstraeonQA.snapshot().enemies.find(e=>e.lifecycle.instanceId===id)?.lifecycle;return m?.lifeGeneration===life+1&&m.hp>0}',arg={'id':id,'life':life},timeout=60000);pause(page);newlife=actor(page,id);assert newlife['deathId'] is None and quest(page,'kill')['objectives'][0]['progress']==2;passed('monster respawn produces a new life without replaying old death or over-counting objectives',{'class':cls})
   before=snap(page);close(page);second=fight(page,id);assert second['deathId']!=dead['deathId'] and second['lifeGeneration']==life+1;assert snap(page)['kills']>=before['kills']+1 and quest(page,'kill')['objectives'][0]['progress']==2;passed('same runtime new life dies legitimately while satisfied Kill remains capped',{'class':cls,'first':dead['deathId'],'second':second['deathId']})
   travel(page,0);print('WALK turn-in registrar',cls,flush=True);npc_interaction(page);before=snap(page);turn_in(page,'kill');after=snap(page);assert after['baseExp']==before['baseExp']+5 and after['baseJobExp']==before['baseJobExp']+3 and after['gold']==before['gold']+6;passed('Kill turn-in adds Quest rewards independently of exact-once death rewards',{'class':cls})
   assert quest(page,'collect')['status']=='READY_TO_TURN_IN';before=snap(page);turn_in(page,'collect');after=snap(page);assert after['itemInventory']['stacks'].get('herb',0)==before['itemInventory']['stacks']['herb']-3 and after['itemInventory']['stacks']['potion']==before['itemInventory']['stacks']['potion']+1;passed('real Monster Loot ownership satisfies Collect and turn-in consumes exactly three canonical Herbs',{'class':cls})
   assert quest(page,'mixed')['status']=='READY_TO_TURN_IN';assert dev(page,'return d.addStack("ore",1)')['ok'];cap=qa(page)['inventoryCapacity'];page.evaluate('n=>AstraeonInventoryCapacityDev.setTestPolicy({mode:"bounded",slotLimit:n,weightLimit:100000,overLimitPolicy:"no-worse"})',cap['occupiedSlots']);before=snap(page);blocked=dev(page,'return q.turnIn("quest-proof-mixed")');assert not blocked['ok'] and blocked['code']=='SLOT_LIMIT_EXCEEDED' and snap(page)==before and quest(page,'mixed')['status']=='READY_TO_TURN_IN';passed('insufficient net capacity preserves every required item reward serial and ready state',{'class':cls,'blocked':blocked})
   assert dev(page,'return d.consumeStack("ore",d.getQuantity("ore")-2)')['ok'];before=snap(page);ticket=dev(page,'window.questTicket=q.prepare("quest-proof-mixed");return window.questTicket');assert ticket['ok'],ticket;assert snap(page)==before;copied=dev(page,'return q.commit({...window.questTicket})');assert copied['code']=='INVALID_QUEST_TICKET' and snap(page)==before;receipt=dev(page,'return q.commit(window.questTicket)');after=snap(page);assert receipt['ok'] and after['itemInventory']['stacks'].get('ore',0)==0 and len(receipt['instanceRewards'])==1 and after['itemInventory']['nextItemSerial']==before['itemInventory']['nextItemSerial']+1;passed('source consumption frees capacity; mixed turn-in commits one canonical equipment instance atomically',{'class':cls,'receipt':receipt})
   before=snap(page);assert dev(page,'return q.commit(window.questTicket)')['code']=='ALREADY_COMMITTED' and snap(page)==before;page.evaluate('AstraeonInventoryCapacityDev.restorePolicy()');gear=receipt['instanceRewards'][0]['instanceId'];assert gear not in snap(page)['equippedItems'].values();stats=dev(page,'return d.getDerivedStats()');assert dev(page,'return d.equip('+json.dumps(gear)+',"offHand")')['ok'];assert dev(page,'return d.getDerivedStats().DEF')==stats['DEF']+1;passed('copied/duplicate authorization grants nothing; rewarded gear equips through existing Stats path',{'class':cls})
   # Action Item / Box canonical fixtures are isolated to their subsystem.
   item=dev(page,'d.setCurrentHP(1);d.resetActionItemCooldowns();return d.requestActionItem("potion",{now:AstraeonQA.snapshot().time,intent:"inventory"})');assert item['ok'];before=snap(page)['questState'];box=dev(page,'d.addStack("monster-box-proof",1);return AstraeonMonsterBoxDev.open("monster-box-proof")');assert box['ok'] and snap(page)['questState']==before;passed('Action Item and Box remain separate from Quest Kill/EXP completion semantics',{'class':cls})
   dev(page,'d.save()');saved=snap(page);page.reload(wait_until='load');page.wait_for_selector('#world');pause(page);loaded=snap(page)
   for key in ['questState','itemInventory','equippedItems','gold','baseExp','baseJobExp','kills']:assert loaded[key]==saved[key],key
   assert all(q['status']=='COMPLETED' for q in qa(page)['questObjectives']);assert dev(page,'return q.commit(window.questTicket)')['code']=='INVALID_QUEST_TICKET';passed('all completed quests contents gear serial and rewards survive reload with no ticket replay',{'class':cls})
   page.evaluate('navigator.serviceWorker.ready');page.wait_for_function('navigator.serviceWorker.controller');cached=page.evaluate('async()=>{const cache=await caches.open("astraeon-static-v95");return (await cache.keys()).map(r=>r.url)}');assert all(any(url.endswith("/"+n+".js?v=95") for url in cached) for n in ['quest-definitions','quest-state','quest-evidence','quest-runtime']);context.set_offline(True);page.reload(wait_until='load');page.wait_for_selector('#world');pause(page);assert snap(page)['questState']==loaded['questState'] and snap(page)['itemInventory']==loaded['itemInventory'];context.set_offline(False);passed('Quest modules and completed durable state resume offline without reward replay',{'class':cls})
   durable=loaded['questState'];ownership=loaded['itemInventory'];travel(page,2);travel(page,0);pause(page);assert snap(page)['questState']==durable and snap(page)['itemInventory']==ownership;passed('completed Quest and canonical rewards survive later travel without re-publication',{'class':cls});context.close()
  context,page=open_page('/tools/quest.html');page.wait_for_function('AstraeonQuestHarness.snapshot().inventory');page.locator('#accept').click();page.locator('#talk').click();page.locator('#prepare').click();page.locator('#commit').click();r=json.loads(page.locator('#result').inner_text());assert r['ok'];page.locator('#duplicate').click();assert json.loads(page.locator('#result').inner_text())['code']=='ALREADY_COMMITTED';passed('isolated harness validates definitions and private turn-in duplicate rejection')
  page.locator('#quest').select_option('quest-proof-kill');page.locator('#accept').click();page.locator('#spawn').click();page.locator('#attack').click();assert page.evaluate('AstraeonQuestHarness.snapshot().objectives[1].objectives[0].progress')==1;page.locator('#respawn').click();page.locator('#attack').click();assert page.evaluate('AstraeonQuestHarness.snapshot().objectives[1].objectives[0].progress')==2;passed('isolated harness routes Combat HP application through Lifecycle and new-life evidence')
  page.locator('#talk').click();page.locator('#prepare').click();page.locator('#save').click();before=page.evaluate('AstraeonQuestHarness.snapshot().save');page.locator('#reload').click();page.locator('#commit').click();assert json.loads(page.locator('#result').inner_text())['code']=='INVALID_QUEST_TICKET';assert page.evaluate('AstraeonQuestHarness.snapshot().save')==before;assert page.evaluate('localStorage.getItem("astraeon-iso-v1")') is None;passed('isolated save uses a separate key; old runtime turn-in authorization cannot replay');context.close()
  context,page=open_page('/');page.wait_for_selector('#create');page.locator('#create').click();page.wait_for_selector('#world');assert page.evaluate('typeof AstraeonQuestDev')=='undefined' and page.evaluate('typeof AstraeonQuestHarness')=='undefined';passed('normal URL boots without unrestricted Quest mutation APIs');context.close();browser.close()
 assert not errors and not http_errors,(errors,http_errors);report['result']='passed'
except Exception as error:
 report.update(result='failed',failure=str(error),lastState=last_snapshot)
 try:
  if last_page and not last_page.is_closed():
   report['lastState']=qa(last_page);report['browserState']=last_page.evaluate('({hidden:document.hidden,visibilityState:document.visibilityState,performance:AstraeonQA.performance()})');last_page.screenshot(path=str(args.output/'failure.png'))
 except Exception:pass
 raise
finally:
 report.update(checks=checks,runtimeErrors=errors,httpErrors=http_errors,observations=observations);(args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS',len(checks),'Quest browser groups',flush=True)
