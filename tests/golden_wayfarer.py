"""Actual rebuilt-town traversal, services and locomotion via ordinary input.
Read-only snapshots and native route queries guide clicks; no save edits/teleports.
Screens and video are visual evidence to inspect, not automated art approval.
"""
import argparse,base64,json,math,time
from pathlib import Path
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8011');ap.add_argument('--output',default='/tmp/astraeon-golden-rebuild');ap.add_argument('--video',action='store_true');ap.add_argument('--capture-scale',type=float,default=0,help='Optional still-image device pixel ratio; motion/performance retain runtime policy');ap.add_argument('--phase',choices=['all','districts','services','motion'],default='all');args=ap.parse_args()
out=Path(args.output);out.mkdir(parents=True,exist_ok=True);errors=[];resources=[];evidence=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 options={'viewport':{'width':1280,'height':800}}
 if args.video:options.update(record_video_dir=str(out/'video'),record_video_size={'width':1280,'height':800})
 context=b.new_context(**options);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:resources.append(str(r.status)+' '+r.url) if r.status>=400 else None)
 page.goto(args.url.rstrip('/')+'/index.html?qa=1',wait_until='networkidle');page.locator('#newname').fill('Golden Warrior');page.locator('#create').click();page.wait_for_selector('#world');page.wait_for_timeout(500)
 def snap():return page.evaluate('AstraeonQA.snapshot()')
 def point(x,y,lift=0):
  s=snap();r=page.locator('#world').bounding_box();v=s['view'];lift+=page.evaluate('(p)=>AstraeonContent.nativeWorld.spatial.elevationAt(...p)',[x,y])*35;return (r['x']+r['width']/2+(x*v['basis']['xx']+y*v['basis']['yx']-s['camera']['x'])*v['zoom'],r['y']+r['height']*v['anchorY']+(x*v['basis']['xy']+y*v['basis']['yy']-s['camera']['y']-lift)*v['zoom'])
 def click(x,y,lift=0):page.mouse.click(*point(x,y,lift))
 def elapsed(seconds):page.wait_for_function('(v)=>AstraeonQA.snapshot().time>=v',arg=snap()['time']+seconds,timeout=30000)
 def walk(x,y):
  deadline=time.monotonic()+60;last_click=None
  while math.hypot(snap()['save']['x']-x,snap()['save']['y']-y)>.35:
   if time.monotonic()>=deadline:
    page.screenshot(path=str(out/'failure.png'));raise AssertionError(('walk timeout',x,y,last_click,snap()['navigation'],snap()['windowName'],snap()['player']))
   route=page.evaluate('(g)=>AstraeonContent.nativeWorld.spatial.route(AstraeonQA.snapshot().player.position,{x:g[0],y:g[1]})', [x,y]);assert route,('no route',x,y,snap()['player']['position'],snap()['navigation'])
   candidates=[];previous=snap()['player']['position']
   for q in route:
    n=math.ceil(math.hypot(q['x']-previous['x'],q['y']-previous['y'])/2)
    candidates.extend({'x':previous['x']+(q['x']-previous['x'])*i/max(1,n),'y':previous['y']+(q['y']-previous['y'])*i/max(1,n)} for i in range(1,n+1));previous=q
   selected=page.evaluate("""(qs)=>{const s=AstraeonQA.snapshot(),r=world.getBoundingClientRect(),v=s.view;
    return qs.map(q=>{const z=AstraeonContent.nativeWorld.spatial.elevationAt(q.x,q.y)*35,px=r.width/2+(q.x*v.basis.xx+q.y*v.basis.yx-s.camera.x)*v.zoom,py=r.height*v.anchorY+(q.x*v.basis.xy+q.y*v.basis.yy-s.camera.y-z)*v.zoom;
     return {q,screen:[r.x+px,r.y+py],inside:px>30&&px<r.width-30&&py>50&&py<r.height-40,element:document.elementFromPoint(r.x+px,r.y+py)?.id,pick:AstraeonSpatialView.pickActor(px,py),distance:Math.hypot(q.x-s.player.position.x,q.y-s.player.position.y)}})
    .filter(p=>p.inside&&p.element==='world'&&!p.pick?.startsWith('service/')&&p.distance>.5).at(-1);
   }""",candidates)
   assert selected,('no clickable waypoint',x,y,route,snap()['player']['position'])
   q=selected['q'];last_click=selected;page.mouse.click(*selected['screen']);
   try:page.wait_for_function('(g)=>Math.hypot(AstraeonQA.snapshot().save.x-g[0],AstraeonQA.snapshot().save.y-g[1])<.4||!document.querySelector("#modal").hidden',arg=[q['x'],q['y']],timeout=12000)
   except Exception:pass
   if page.locator('#modal').is_visible():page.keyboard.press('Escape')
  elapsed(.2)
 def capture(name,responsive=True):
  for w,h in ([(1280,800),(390,844),(844,390),(768,1024)] if responsive else [(1280,800)]):
   page.set_viewport_size({'width':w,'height':h});elapsed(.16)
   if args.capture_scale:page.evaluate('(ratio)=>AstraeonSpatialView.renderer.setPixelRatio(ratio)',args.capture_scale);elapsed(.3)
   page.screenshot(path=str(out/f'{name}-{w}-{h}.png'))
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
   if args.capture_scale:page.evaluate('AstraeonSpatialView.renderer.setPixelRatio(AstraeonSpatialView.stats.pixelRatio)')
  page.set_viewport_size({'width':1280,'height':800});elapsed(.2)
 capture('arrival')
 if args.phase in ['all','districts']:
  for stop in snap()['town']['route'][1:]:
   walk(*stop['position']);capture(stop['name'].lower().replace(' ','-'));evidence.append({'stop':stop['name'],'position':snap()['player']['position']});print('CAPTURE',stop['name'],flush=True)
 # Every service still opens from its authored frontage.
 if args.phase in ['all','services']:
  for name in ['Guild Registrar','Quest Board','Merchant','Artisan','Housing Keeper','Gatekeeper',"The Seafarer's Host",'Luna Attendant']:
   npc=next(n for n in snap()['npcs'] if n['name']==name)['transform']['position']
   approach=page.evaluate('''n=>{const w=AstraeonContent.nativeWorld.spatial,start=AstraeonQA.snapshot().player.position;return w.navCells.filter(p=>p.walkable&&Math.hypot(p.x-n.x,p.y-n.y)>2.3&&Math.hypot(p.x-n.x,p.y-n.y)<3.2).sort((a,b)=>Math.hypot(a.x-n.x,a.y-n.y-2.8)-Math.hypot(b.x-n.x,b.y-n.y-2.8)).find(p=>w.route(start,p))}''',npc);assert approach,('no service approach',name)
   walk(approach['x'],approach['y'])
   picked=page.evaluate('''({n,name})=>{const s=AstraeonQA.snapshot(),r=world.getBoundingClientRect(),v=s.view,service=AstraeonContent.services.find(p=>p.name===name),expected=service.kind==='journal'?'object/'+service.objectId:'service/'+service.id,z=AstraeonContent.nativeWorld.spatial.elevationAt(n.x,n.y)*35,px=r.width/2+(n.x*v.basis.xx+n.y*v.basis.yx-s.camera.x)*v.zoom,py=r.height*v.anchorY+(n.x*v.basis.xy+n.y*v.basis.yy-s.camera.y-z)*v.zoom;
    for(const dy of [35,45,55,25,65,15])for(const dx of [0,6,-6,12,-12,18,-18]){const x=px+dx*v.zoom,y=py-dy*v.zoom;if(AstraeonSpatialView.pickActor(x,y)===expected)return {screen:[r.x+x,r.y+y],expected}}
    return {expected,root:[px,py],picks:[25,35,45,55,65].map(h=>AstraeonSpatialView.pickActor(px,py-h*v.zoom))};}''',{'n':npc,'name':name})
   if 'screen' not in picked:page.screenshot(path=str(out/'service-occlusion-failure.png'));raise AssertionError(('service hidden',name,picked,snap()['player']['position']))
   page.mouse.click(*picked['screen']);page.wait_for_selector('#modal:not([hidden])');evidence.append({'service':name,'title':page.locator('#window-title').inner_text()});page.keyboard.press('Escape');print('SERVICE',name,flush=True)
 # Raw motion in open plaza: three modes, 8 headings, then reversals/turns.
 if args.phase in ['all','motion']:
  walk(19.8,24.3)
  for mode,modifier in [('walk','Alt'),('run',None),('sprint','Shift')]:
   for keys in [('s',),('s','d'),('d',),('w','d'),('w',),('w','a'),('a',),('s','a')]:
    duration={'walk':1.61,'run':1.23,'sprint':1.11}[mode]
    # Select a clear corridor in the real plaza from authored navigation.
    axes=[sum(1 if k=='d' else -1 if k=='a' else 0 for k in keys),sum(1 if k=='s' else -1 if k=='w' else 0 for k in keys)]
    anchor=page.evaluate("""({axes,mode,duration})=>{const w=AstraeonContent.nativeWorld.spatial,v=AstraeonMotion.cameraMovement(...axes,AstraeonView.inverse),center=w.scene.route.find(s=>s.name==='Plaza').position,speed={walk:1.3,run:2.7,sprint:4.1}[mode],distance=speed*(duration+.25)+.5;
     return w.navCells.filter(p=>p.walkable&&Math.hypot(p.x-center[0],p.y-center[1])<8).sort((a,b)=>Math.hypot(a.x-center[0],a.y-center[1])-Math.hypot(b.x-center[0],b.y-center[1])).find(p=>{for(let d=0;d<=distance;d+=.1)if(w.blocked(p.x+v.x*d,p.y+v.y*d,.5))return false;return true})
    }""",{'axes':axes,'mode':mode,'duration':duration});assert anchor,('no review corridor',mode,keys)
    walk(anchor['x'],anchor['y'])
    # Only normal input events release held keys. Positions, animation and time
    # are never changed. Capture the actual rendered frame before tool latency
    # can extend a sprint into an unrelated obstacle.
    page.evaluate("""({keys,modifier,duration})=>{window.motionSample=null;let start=null;const held=[...keys,...(modifier?[modifier]:[])];
     const begin=e=>{if(e.key===keys.at(-1)){start=AstraeonQA.snapshot().time;removeEventListener('keydown',begin)}};addEventListener('keydown',begin);
     const record=e=>{if(start===null||e.detail.time-start<duration)return;const s=AstraeonQA.snapshot(),canvas=document.createElement('canvas'),overlay=document.querySelector('#world');canvas.width=overlay.clientWidth;canvas.height=overlay.clientHeight;const g=canvas.getContext('2d');g.drawImage(document.querySelector('#spatial-world'),0,0,canvas.width,canvas.height);g.drawImage(overlay,0,0,canvas.width,canvas.height);
      window.motionSample={motion:s.player,time:s.time,duration:s.time-start,image:canvas.toDataURL()};for(const key of held)dispatchEvent(new KeyboardEvent('keyup',{key,bubbles:true}));removeEventListener('astraeon-frame',record)};addEventListener('astraeon-frame',record);
    }""",{'keys':list(keys),'modifier':modifier,'duration':duration})
    if modifier:page.keyboard.down(modifier)
    for key in keys:page.keyboard.down(key)
    page.wait_for_function('window.motionSample!==null',timeout=30000);sample=page.evaluate('motionSample');moving=sample['motion'];assert moving['speed']>.1,(mode,keys,anchor,moving)
    (out/f'{mode}-{"".join(keys)}.png').write_bytes(base64.b64decode(sample['image'].split(',')[1]));evidence.append({'mode':mode,'keys':keys,'motion':moving,'duration':sample['duration'],'anchor':anchor})
    for key in keys:page.keyboard.up(key)
    if modifier:page.keyboard.up(modifier)
    elapsed(.35)
   print('LOCOMOTION',mode,flush=True)
  walk(19.8,24.3)
  for keys in [('d',),('d','w'),('w',),('s',),('a',),('d',)]:
   for key in keys:page.keyboard.down(key)
   elapsed(.4)
   for key in keys:page.keyboard.up(key)
   elapsed(.1)
  elapsed(.3);capture('turn-stop',False)
  for degrees in [0,45,90,135,180,225,270,315]:
   walk(19.8,24.3);a=math.radians(degrees);page.mouse.move(*point(19.8+math.cos(a)*3,24.3+math.sin(a)*3));page.keyboard.press('f');elapsed(.22);page.screenshot(path=str(out/f'attack-{degrees}.png'));elapsed(.7)
 # Approach the gate from town, then use its actual authored field threshold.
 walk(6.95,24.6);capture('gate-departure');exit=next(e for e in snap()['town']['transitions'] if e['to']==2);click(exit['x'],exit['y'],17);page.wait_for_function('AstraeonQA.snapshot().save.zone===2',timeout=20000);capture('field-threshold')
 saved=snap()['save'];page.reload(wait_until='networkidle');page.wait_for_selector('#world');assert snap()['save']['name']==saved['name'] and snap()['save']['zone']==2
 # Live review telemetry, not physical-device certification.
 report={'layout':snap()['town']['layout'],'evidence':evidence,'runtime_errors':errors,'resource_errors':resources}
 (out/'report.json').write_text(json.dumps(report,indent=2));context.close();b.close();assert not errors and not resources,report
 print('REVIEW ARTIFACTS',out,flush=True)
