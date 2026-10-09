"""Ordinary-input semantic NPC fixture; copied retained Quest navigation semantics."""
import math,time,tempfile
from pathlib import Path
from playwright.sync_api import TimeoutError as PlaywrightTimeout
observations=[];last_snapshot=None
evidence_dir=Path(tempfile.gettempdir())/'astraeon-service-navigation';evidence_dir.mkdir(parents=True,exist_ok=True)
def checkpoint():
 import json
 (evidence_dir/'navigation-observations.json').write_text(json.dumps(observations,indent=2),encoding='utf-8')
def qa(page):
 global last_snapshot
 last_snapshot=page.evaluate('AstraeonQA.snapshot()');return last_snapshot

def close(page):
 if qa(page)['windowName']:page.keyboard.press('Escape');page.locator('#modal').wait_for(state='hidden')

def elapsed(page,seconds):page.wait_for_function('v=>AstraeonQA.snapshot().time>=v',arg=qa(page)['time']+seconds,timeout=60000)

def keyboard_step(page,at,distance=1):
 origin=qa(page)['player']['position'];keys=page.evaluate('''g=>{const p=AstraeonQA.snapshot().player.position,dx=g.x-p.x,dy=g.y-p.y;return [['d'],['s','d'],['s'],['s','a'],['a'],['w','a'],['w'],['w','d']].map(keys=>{const v=AstraeonMotion.cameraMovement(keys.includes('d')?1:keys.includes('a')?-1:0,keys.includes('s')?1:keys.includes('w')?-1:0,AstraeonView.inverse);return {keys,score:v.x*dx+v.y*dy}}).sort((a,b)=>b.score-a.score)[0].keys}''',at)
 for k in keys:page.keyboard.down(k)
 try:page.wait_for_function('({p,d})=>{const s=AstraeonQA.snapshot().player.position;return Math.hypot(s.x-p.x,s.y-p.y)>=d}',arg={'p':origin,'d':distance},timeout=10000)
 finally:
  for k in keys:page.keyboard.up(k)

def npc_interaction(page,target_id='merchant'):
 close(page);npc=next(n['transform']['position'] for n in qa(page)['npcs'] if n['id']==target_id)
 npc={**npc,'targetId':target_id};approach=page.evaluate('''n=>{const w=AstraeonContent.nativeWorld.spatial,start=AstraeonQA.snapshot().player.position;return w.navCells.filter(p=>p.walkable&&Math.hypot(p.x-n.x,p.y-n.y)>2.3&&Math.hypot(p.x-n.x,p.y-n.y)<3.2).sort((a,b)=>Math.hypot(a.x-n.x,a.y-n.y-2.8)-Math.hypot(b.x-n.x,b.y-n.y-2.8)).find(p=>w.route(start,p))}''',npc);assert approach
 walk(page,approach['x'],approach['y'])
 picked=page.evaluate('''n=>{const r=world.getBoundingClientRect(),v=AstraeonQA.snapshot().view,p=AstraeonSpatialView.worldToScreen(n.x,n.y,AstraeonContent.nativeWorld.spatial.elevationAt(n.x,n.y));for(const dy of [35,45,55,25,65,15])for(const dx of [0,6,-6,12,-12,18,-18]){const x=p.x+dx*v.zoom,y=p.y-dy*v.zoom;if(AstraeonSpatialView.pickActor(x,y)==='service/'+n.targetId)return [r.x+x,r.y+y]}return null}''',npc);assert picked,('NPC occlusion',npc,qa(page)['player']);page.mouse.click(*picked);page.wait_for_selector('#modal:not([hidden])');assert qa(page)['windowName']==next(n['kind'] for n in qa(page)['npcs'] if n['id']==target_id)

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
   page.screenshot(path=str(evidence_dir/'navigation-failure.png'));raise AssertionError(('walk timeout',x,y,last_click,observed['navigation'],observed['windowName'],observed['player']))
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

def dev(page,code):return page.evaluate('()=>{const d=AstraeonProgressionDev,q=AstraeonQuestDev;'+code+'}')

def snap(page):return dev(page,'return d.snapshot()')

def pause(page):close(page);page.locator('[data-open="character"]').click()

def field_point(page,at):
 s=qa(page);r=page.locator('#world').bounding_box();v,c=s['view'],s['camera'];return [r['x']+r['width']/2+(at['x']*v['basis']['xx']+at['y']*v['basis']['yx']-c['x'])*v['zoom'],r['y']+r['height']*v['anchorY']+(at['x']*v['basis']['xy']+at['y']*v['basis']['yy']-c['y'])*v['zoom']]

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
