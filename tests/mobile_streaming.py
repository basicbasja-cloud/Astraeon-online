"""Real-capital mobile traversal using ordinary touch input; no runtime setters."""
import argparse, json, math, time
from pathlib import Path
from playwright.sync_api import sync_playwright

ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8011/?qa=1');ap.add_argument('--output',type=Path,required=True);ap.add_argument('--engine',choices=['chromium','webkit'],default='chromium');ap.add_argument('--legs',default='128,150;128,200;80,200;13.4,144;128,150;13.4,144');a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
errors=[];samples=[];events=[]
with sync_playwright() as p:
 if a.engine=='chromium':browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--enable-precise-memory-info'])
 else:browser=p.webkit.launch(executable_path='/workspace/.cache/astraeon-playwright/webkit-2336/pw_run.sh',headless=True)
 context=browser.new_context(**p.devices['iPhone 13']);page=context.new_page();page.set_default_timeout(180000);page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
 page.on('request',lambda r:events.append({'url':r.url,'at':time.monotonic(),'kind':'request'}))
 started=time.monotonic();page.goto(a.url,wait_until='domcontentloaded');page.locator('#newname').fill('Mobile Streaming');page.locator('#create').click();page.wait_for_function('document.getElementById("world") && window.AstraeonQA?.snapshot().time>0 && AstraeonWorldStreaming.readyForMovement');cold_ms=(time.monotonic()-started)*1000
 def snap():return page.evaluate('AstraeonQA.snapshot()')
 def observe(label):
  data=page.evaluate('''label=>{const s=AstraeonQA.snapshot(),v=AstraeonSpatialView,stream=AstraeonWorldStreaming.snapshot(),meshes=[...v.chunkNodes.values()].flat(),names=meshes.map(m=>m.name);return {label,position:s.player.position,time:s.time,blocked:AstraeonContent.nativeWorld.spatial.blocked(s.player.position.x,s.player.position.y),stream,heap:performance.memory?.usedJSHeapSize||null,geometries:v.renderer.info.memory.geometries,textures:v.renderer.info.memory.textures,staticMeshes:meshes.length,uniqueNames:new Set(names).size,geometryBytes:meshes.reduce((n,m)=>n+Object.values(m.geometry.attributes).reduce((k,a)=>k+a.array.byteLength,0)+m.geometry.index.array.byteLength,0),visibleMissing:stream.required.filter(id=>!stream.loaded.includes(id)),renderer:s.renderer}}''',label)
  assert not data['blocked'],('player inside authored solid',data['position']);assert data['uniqueNames']==data['staticMeshes'],'duplicate chunk meshes';samples.append(data)
  (a.output/'progress.json').write_text(json.dumps({'status':'in_progress','coldMs':cold_ms,'samples':samples,'errors':errors},indent=2)+'\n');print(label,data['position'],len(data['stream']['loaded']),data['stream']['unloads'],data['stream']['reloads'],flush=True);return data
 initial=observe('cold-playable');assert len(initial['stream']['loaded'])<len(page.evaluate('AstraeonWorldStreaming.zone.chunks'))/2;assert not any('wayfarer-spatial.json' in e['url'] for e in events);page.screenshot(path=str(a.output/'cold-mobile.png'))
 def walk(goal):
  start=snap()['player']['position'];deadline=time.monotonic()+max(180,math.hypot(goal[0]-start['x'],goal[1]-start['y'])*8);clicks=0
  while True:
   s=snap();current=s['player']['position'];distance=math.hypot(goal[0]-current['x'],goal[1]-current['y'])
   if distance<.4:break
   if time.monotonic()>deadline:page.screenshot(path=str(a.output/'failure.png'));raise AssertionError(('touch traversal timeout',goal,current,s['navigation']))
   target=page.evaluate('''goal=>{const s=AstraeonQA.snapshot(),v=AstraeonSpatialView,r=document.getElementById('world').getBoundingClientRect(),sp=AstraeonContent.nativeWorld.spatial,route=sp.route(s.player.position,{x:goal[0],y:goal[1]});if(!route)return {noRoute:true};let previous=s.player.position,qs=[];for(const q of route){const n=Math.max(1,Math.ceil(Math.hypot(q.x-previous.x,q.y-previous.y)));for(let i=1;i<=n;i++)qs.push({x:previous.x+(q.x-previous.x)*i/n,y:previous.y+(q.y-previous.y)*i/n});previous=q}
    return qs.map(q=>{const p=v.worldToScreen(q.x,q.y,sp.elevationAt(q.x,q.y));return {q,screen:[p.x+r.x,p.y+r.y],inside:p.x>22&&p.x<r.width-22&&p.y>50&&p.y<r.height-50,element:document.elementFromPoint(p.x+r.x,p.y+r.y)?.id,pick:v.pickActor(p.x,p.y),distance:Math.hypot(q.x-s.player.position.x,q.y-s.player.position.y)}}).filter(t=>t.inside&&t.element==='world'&&!t.pick?.startsWith('service/')&&t.distance>.2&&t.distance<8).at(-1)||null}''',goal)
   assert not target or not target.get('noRoute'),('navigation lost across chunks',goal,current)
   if not target:page.wait_for_timeout(500);continue
   page.touchscreen.tap(*target['screen']);clicks+=1
   try:page.wait_for_function('''q=>{const s=AstraeonQA.snapshot();return Math.hypot(s.player.position.x-q.x,s.player.position.y-q.y)<.4||s.windowName}''',arg=target['q'],timeout=12000)
   except Exception:pass
   if page.locator('#modal').is_visible():page.keyboard.press('Escape')
   if clicks%8==0:observe('travel-'+str(goal)+'-'+str(clicks))
  return clicks
 page.keyboard.down('Shift')
 for i,goal in enumerate([list(map(float,pair.split(','))) for pair in a.legs.split(';') if pair]):
  clicks=walk(goal);page.wait_for_function('AstraeonWorldStreaming.readyForMovement');data=observe('leg-'+str(i));page.screenshot(path=str(a.output/f'leg-{i}.png'));assert clicks>0
 page.keyboard.up('Shift');page.wait_for_timeout(3500);final=observe('travel-final');assert final['stream']['unloads']>0,'no distant unload';assert final['stream']['reloads']>0,'no return reload'
 before=snap()['save'];started=time.monotonic();page.reload(wait_until='domcontentloaded');page.wait_for_function('document.getElementById("world") && window.AstraeonQA?.snapshot().time>0 && AstraeonWorldStreaming.readyForMovement');warm_ms=(time.monotonic()-started)*1000;after=snap()['save'];assert all(after[k]==before[k] for k in ['name','zone','lv','xp','gold','inventory','equipment']);warm=observe('warm-playable');page.screenshot(path=str(a.output/'warm-mobile.png'))
 report={'engine':a.engine,'mobileDevice':'iPhone13 emulation','physicalIPhoneSafari':'PENDING','coldMs':cold_ms,'warmMs':warm_ms,'samples':samples,'requests':events,'errors':errors,'noMonolithicBootRequest':not any('wayfarer-spatial.json' in e['url'] for e in events),'traversalUnloads':final['stream']['unloads'],'traversalReloads':final['stream']['reloads'],'visualReview':'Inspect cold/warm and traversal screenshots; no quality setters used'}
 (a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n');browser.close();assert not errors,errors;print('PASS mobile cold/warm, ordinary traversal, chunk return reload, collision and duplicate guards',flush=True)
