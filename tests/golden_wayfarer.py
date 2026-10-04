"""Actual rebuilt-town traversal, services and locomotion via ordinary input.
Read-only snapshots and native route queries guide clicks; no save edits/teleports.
Screens and video are visual evidence to inspect, not automated art approval.
"""
import argparse,base64,json,math,time,os
from pathlib import Path
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8011');ap.add_argument('--output',default='/tmp/astraeon-golden-rebuild');ap.add_argument('--video',action='store_true');ap.add_argument('--motion-series',action='store_true',help='Capture actual rendered actor crops throughout each ordinary gait sample');ap.add_argument('--capture-scale',type=float,default=0,help='Optional still-image device pixel ratio; motion/performance retain runtime policy');ap.add_argument('--phase',choices=['all','districts','services','motion','spatial','reactions'],default='all');ap.add_argument('--modes',default='walk,run,sprint');ap.add_argument('--archetype',choices=['warrior','mage','ranger'],default='warrior');args=ap.parse_args()
out=Path(args.output);out.mkdir(parents=True,exist_ok=True);errors=[];resources=[];evidence=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('ASTRAEON_BROWSER','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--enable-gpu','--use-angle=d3d11'])
 options={'viewport':{'width':1280,'height':800}}
 if args.video:options.update(record_video_dir=str(out/'video'),record_video_size={'width':1280,'height':800})
 context=b.new_context(**options);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);page.on('response',lambda r:resources.append(str(r.status)+' '+r.url) if r.status>=400 else None)
 page.goto(args.url.rstrip('/')+'/index.html?qa=1',wait_until='networkidle');page.locator('#newname').fill('Golden '+args.archetype.title());page.locator('#newclass').select_option({'warrior':'0','mage':'12','ranger':'3'}[args.archetype]);page.locator('#create').click();page.wait_for_selector('#world');page.wait_for_timeout(500)
 def snap():return page.evaluate('AstraeonQA.snapshot()')
 plaza=next(r["position"] for r in snap()["town"]["route"] if r["name"]=="Plaza");arrival=next(r["position"] for r in snap()["town"]["route"] if r["name"]=="Arrival")
 def point(x,y,lift=0):
  r=page.locator('#world').bounding_box();q=page.evaluate('([x,y,lift])=>AstraeonSpatialView.worldToScreen(x,y,AstraeonContent.nativeWorld.spatial.elevationAt(x,y)+lift/35)',[x,y,lift]);return (r['x']+q['x'],r['y']+q['y'])
 def click(x,y,lift=0):page.mouse.click(*point(x,y,lift))
 def elapsed(seconds):page.wait_for_function('(v)=>AstraeonQA.snapshot().time>=v',arg=snap()['time']+seconds,timeout=30000)
 def walk(x,y):
  deadline=time.monotonic()+60;last_click=None
  while math.hypot(snap()['save']['x']-x,snap()['save']['y']-y)>.4:
   if time.monotonic()>=deadline:
    page.screenshot(path=str(out/'failure.png'));raise AssertionError(('walk timeout',x,y,last_click,snap()['navigation'],snap()['windowName'],snap()['player']))
   route=page.evaluate('(g)=>AstraeonContent.nativeWorld.spatial.route(AstraeonQA.snapshot().player.position,{x:g[0],y:g[1]})', [x,y]);assert route,('no route',x,y,snap()['player']['position'],snap()['navigation'])
   candidates=[];previous=snap()['player']['position']
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
    current=snap()['player']['position'];assert len(route)==1 and math.hypot(x-current['x'],y-current['y'])<2.6,('no clickable waypoint',x,y,route,current)
    choice=page.evaluate("""g=>{const p=AstraeonQA.snapshot().player.position,dx=g[0]-p.x,dy=g[1]-p.y;return [['d'],['s','d'],['s'],['s','a'],['a'],['w','a'],['w'],['w','d']].map(keys=>{const v=AstraeonMotion.cameraMovement(keys.includes('d')?1:keys.includes('a')?-1:0,keys.includes('s')?1:keys.includes('w')?-1:0,AstraeonView.inverse);return {keys,score:(v.x*dx+v.y*dy)/Math.hypot(dx,dy)}}).sort((a,b)=>b.score-a.score)[0]}""",[x,y])
    page.evaluate("""({goal,keys})=>{let start=null,best=Infinity;window.keyboardLegDone=false;const observe=()=>{const s=AstraeonQA.snapshot();start??=s.time;const d=Math.hypot(s.player.position.x-goal[0],s.player.position.y-goal[1]);if(d<.33||d>best+.025||s.time-start>.7){for(const key of keys)dispatchEvent(new KeyboardEvent('keyup',{key,bubbles:true}));removeEventListener('astraeon-frame',observe);keyboardLegDone=true}best=Math.min(best,d)};addEventListener('astraeon-frame',observe)}""",{'goal':[x,y],'keys':choice['keys']})
    for key in choice['keys']:page.keyboard.down(key)
    page.wait_for_function('keyboardLegDone',timeout=10000)
    for key in choice['keys']:page.keyboard.up(key)
    continue
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
 if args.phase in ['all','spatial']:
  for name,xy in [('civic-lower-approach',(54,40)),('civic-processional-tread',(54,37)),('civic-upper-court',(54,33)),('civic-west-flight',(26.3,36.2)),('civic-east-flight',(74,35.2)),('shrine-stair-base',(84.866,25.3625)),('shrine-tread',(84.866,24.674)),('hall-stair-base',(55.08,26.075)),('hall-tread',(55.08,25.2785)),('hall-terrace',(55.08,23.375)),('gate-front',(54,94.2)),('gate-under-arch',(54,89.6)),('gate-behind',(54,84.4))]:
   walk(*xy);capture(name,False);evidence.append({'spatial_case':name,'player':snap()['player']});print('SPATIAL',name,flush=True)
 if args.phase in ['all','districts']:
  for stop in snap()['town']['route'][1:]:
   walk(*stop['position']);capture(stop['name'].lower().replace(' ','-'));evidence.append({'stop':stop['name'],'position':snap()['player']['position']});print('CAPTURE',stop['name'],flush=True)
 # Every service still opens from its authored frontage.
 if args.phase in ['all','services']:
  for name in ['Guild Registrar','Quest Board','Merchant','Artisan','Housing Keeper','Gatekeeper',"The Seafarer's Host",'Luna Attendant']:
   npc=next(n for n in snap()['npcs'] if n['name']==name)['transform']['position']
   approach=page.evaluate('''n=>{const w=AstraeonContent.nativeWorld.spatial,start=AstraeonQA.snapshot().player.position;return w.navCells.filter(p=>p.walkable&&Math.hypot(p.x-n.x,p.y-n.y)>2.3&&Math.hypot(p.x-n.x,p.y-n.y)<3.2).sort((a,b)=>Math.hypot(a.x-n.x,a.y-n.y-2.8)-Math.hypot(b.x-n.x,b.y-n.y-2.8)).find(p=>w.route(start,p))}''',npc);assert approach,('no service approach',name)
   walk(approach['x'],approach['y'])
   picked=page.evaluate('''({n,name})=>{const s=AstraeonQA.snapshot(),r=world.getBoundingClientRect(),v=s.view,service=AstraeonContent.services.find(p=>p.name===name),expected=service.kind==='journal'?'object/'+service.objectId:'service/'+service.id,p=AstraeonSpatialView.worldToScreen(n.x,n.y,AstraeonContent.nativeWorld.spatial.elevationAt(n.x,n.y)),px=p.x,py=p.y;
    for(const dy of [35,45,55,25,65,15])for(const dx of [0,6,-6,12,-12,18,-18]){const x=px+dx*v.zoom,y=py-dy*v.zoom;if(AstraeonSpatialView.pickActor(x,y)===expected)return {screen:[r.x+x,r.y+y],expected}}
    return {expected,root:[px,py],picks:[25,35,45,55,65].map(h=>AstraeonSpatialView.pickActor(px,py-h*v.zoom))};}''',{'n':npc,'name':name})
   if 'screen' not in picked:page.screenshot(path=str(out/'service-occlusion-failure.png'));raise AssertionError(('service hidden',name,picked,snap()['player']['position']))
   page.mouse.click(*picked['screen']);page.wait_for_selector('#modal:not([hidden])');evidence.append({'service':name,'title':page.locator('#window-title').inner_text()});page.keyboard.press('Escape');print('SERVICE',name,flush=True)
 # Raw motion in open plaza: three modes, 8 headings, then reversals/turns.
 if args.phase in ['all','motion']:
  walk(*plaza)
  for mode,modifier in [('walk','Alt'),('run',None),('sprint','Shift')]:
   if mode not in args.modes.split(','):continue
   for keys in [('s',),('s','d'),('d',),('w','d'),('w',),('w','a'),('a',),('s','a')]:
    duration=({'walk':2.9,'run':2.35,'sprint':1.95} if args.motion_series else {'walk':1.61,'run':1.23,'sprint':1.11})[mode]
    # Select a clear corridor in the real plaza from authored navigation.
    axes=[sum(1 if k=='d' else -1 if k=='a' else 0 for k in keys),sum(1 if k=='s' else -1 if k=='w' else 0 for k in keys)]
    anchor=page.evaluate("""({axes,mode,duration,archetype})=>{const w=AstraeonContent.nativeWorld.spatial,v=AstraeonMotion.cameraMovement(...axes,AstraeonView.inverse),center=w.scene.route.find(s=>s.name==='Plaza').position,speed=(archetype==='warrior'?{walk:1.3,run:2.7,sprint:4.1}:{walk:1.3,run:3.5,sprint:4.6})[mode],distance=speed*(duration+.25)+.5;
     return w.navCells.filter(p=>p.walkable&&Math.hypot(p.x-center[0],p.y-center[1])<8).sort((a,b)=>Math.hypot(a.x-center[0],a.y-center[1])-Math.hypot(b.x-center[0],b.y-center[1])).find(p=>{for(let d=0;d<=distance;d+=.1)if(w.blocked(p.x+v.x*d,p.y+v.y*d,.5))return false;return true})
    }""",{'axes':axes,'mode':mode,'duration':duration,'archetype':args.archetype});assert anchor,('no review corridor',mode,keys)
    walk(anchor['x'],anchor['y'])
    # Only normal input events release held keys. Positions, animation and time
    # are never changed. Capture the actual rendered frame before tool latency
    # can extend a sprint into an unrelated obstacle.
    page.evaluate("""({keys,modifier,duration,series})=>{window.motionSample=null;window.motionFrames=[];window.motionRoots=[];let start=null,lastFrame=-Infinity,lastPose=null;const held=[...keys,...(modifier?[modifier]:[])];
     const begin=e=>{if(e.key===keys.at(-1)){start=AstraeonQA.snapshot().time;removeEventListener('keydown',begin)}};addEventListener('keydown',begin);
     const record=e=>{if(start===null)return;
      const entry=AstraeonSpatialView.actors.get('player'),actor=entry?.motionSample;if(actor){const sample=structuredClone(actor);sample.time=e.detail.time;if(series){sample.simulation=AstraeonQA.snapshot().player;sample.intervalMs=AstraeonQA.performance().intervalMs;sample.quad=Array.from(entry.mesh.geometry.attributes.position.array);sample.scale=entry.mesh.scale.toArray()}motionRoots.push(sample)}
      const pose=actor?.frame,poseId=pose?`${pose.clip}/${pose.row}/${pose.column}`:null;
      if(series&&e.detail.time-start>=.2&&poseId!==lastPose){const s=AstraeonQA.snapshot(),v=AstraeonSpatialView,p=s.player.position,c=document.createElement('canvas');c.width=144;c.height=160;const g=c.getContext('2d'),q=v.worldToScreen(p.x,p.y,p.z),x=q.x,y=q.y,buffer=v.renderer.getDrawingBufferSize(new AstraeonSpatialRenderer.THREE.Vector2());g.drawImage(v.canvas,(x-72)*buffer.x/v.width,(y-125)*buffer.y/v.height,144*buffer.x/v.width,160*buffer.y/v.height,0,0,144,160);motionFrames.push({time:s.time,elapsed:e.detail.time-start,motion:s.player,selectedPose:structuredClone(pose),image:c.toDataURL()});lastFrame=e.detail.time;lastPose=poseId}
      if(e.detail.time-start<duration)return;const s=AstraeonQA.snapshot(),canvas=document.createElement('canvas'),overlay=document.querySelector('#world');canvas.width=overlay.clientWidth;canvas.height=overlay.clientHeight;const g=canvas.getContext('2d');g.drawImage(document.querySelector('#spatial-world'),0,0,canvas.width,canvas.height);g.drawImage(overlay,0,0,canvas.width,canvas.height);
      window.motionSample={motion:s.player,time:s.time,duration:s.time-start,image:canvas.toDataURL()};for(const key of held)dispatchEvent(new KeyboardEvent('keyup',{key,bubbles:true}));removeEventListener('astraeon-frame',record)};addEventListener('astraeon-frame',record);
    }""",{'keys':list(keys),'modifier':modifier,'duration':duration,'series':args.motion_series})
    if modifier:page.keyboard.down(modifier)
    for key in keys:page.keyboard.down(key)
    page.wait_for_function('window.motionSample!==null',timeout=30000);sample=page.evaluate('motionSample');moving=sample['motion'];assert moving['speed']>.1,(mode,keys,anchor,moving)
    roots=page.evaluate('motionRoots');assert len(roots)>10,(mode,keys,'no rendered movement')
    moving_pairs=[(a,b) for a,b in zip(roots,roots[1:]) if math.dist(a['root'][:2],b['root'][:2])>1e-5]
    held=sum(math.dist(a['renderedRoot'][:2],b['renderedRoot'][:2])<1e-5 for a,b in moving_pairs)
    continuity={'samples':len(roots),'movingPairs':len(moving_pairs),'frozenBodyFrames':held,'columns':sorted(set(s['frame']['column'] for s in roots if s.get('frame')))}
    assert moving_pairs and held==0,(mode,keys,continuity)
    (out/f'{mode}-{"".join(keys)}.png').write_bytes(base64.b64decode(sample['image'].split(',')[1]));evidence.append({'mode':mode,'keys':keys,'motion':moving,'duration':sample['duration'],'anchor':anchor,'renderedContinuity':continuity})
    if args.motion_series:
     folder=out/'motion-series'/f'{mode}-{"".join(keys)}';folder.mkdir(parents=True,exist_ok=True);frames=page.evaluate('motionFrames')
     for i,frame in enumerate(frames):(folder/f'{i:03d}.png').write_bytes(base64.b64decode(frame.pop('image').split(',')[1]))
     (folder/'frames.json').write_text(json.dumps(frames,indent=2))
     (folder/'runtime-timeline.json').write_text(json.dumps(roots,indent=2))
    for key in keys:page.keyboard.up(key)
    if modifier:page.keyboard.up(modifier)
    elapsed(.35)
   print('LOCOMOTION',mode,flush=True)
  walk(*plaza)
  if args.motion_series:
   page.evaluate("""()=>{window.transitionTimeline=[];window.transitionFrames=[];let lastPose=null;
    const record=e=>{const v=AstraeonSpatialView,a=v.actors.get('player'),m=a?.motionSample;if(!m)return;const s=AstraeonQA.snapshot();transitionTimeline.push({time:s.time,simulation:s.player,actor:structuredClone(m),intervalMs:AstraeonQA.performance().intervalMs,quad:Array.from(a.mesh.geometry.attributes.position.array),scale:a.mesh.scale.toArray()});const f=m.frame,id=f?`${f.clip}/${f.row}/${f.column}`:null;if(id===lastPose)return;lastPose=id;
     const c=document.createElement('canvas');c.width=144;c.height=160;const g=c.getContext('2d'),p=s.player.position,q=v.worldToScreen(p.x,p.y,p.z),buffer=v.renderer.getDrawingBufferSize(new AstraeonSpatialRenderer.THREE.Vector2());g.drawImage(v.canvas,(q.x-72)*buffer.x/v.width,(q.y-125)*buffer.y/v.height,144*buffer.x/v.width,160*buffer.y/v.height,0,0,144,160);transitionFrames.push({time:s.time,simulation:s.player,selectedPose:structuredClone(f),image:c.toDataURL()})};addEventListener('astraeon-frame',record);window.stopTransitionRecorder=()=>removeEventListener('astraeon-frame',record)}""")
   page.keyboard.down('Alt');page.keyboard.down('d');elapsed(.45)
   page.keyboard.up('Alt');elapsed(.45)
   page.keyboard.down('Shift');elapsed(.45)
   page.keyboard.up('Shift');page.keyboard.down('Alt');elapsed(.45)
   page.keyboard.up('d');page.keyboard.up('Alt');elapsed(.35)
  for keys in [('d',),('d','w'),('w',),('s',),('a',),('d',)]:
   for key in keys:page.keyboard.down(key)
   elapsed(.4)
   for key in keys:page.keyboard.up(key)
   elapsed(.1)
  elapsed(.3);capture('turn-stop',False)
  if args.motion_series:
   page.evaluate('stopTransitionRecorder()');folder=out/'transitions';folder.mkdir(exist_ok=True);frames=page.evaluate('transitionFrames')
   for i,frame in enumerate(frames):(folder/f'{i:03d}.png').write_bytes(base64.b64decode(frame.pop('image').split(',')[1]))
   (folder/'frames.json').write_text(json.dumps(frames,indent=2))
   (folder/'runtime-timeline.json').write_text(json.dumps(page.evaluate('transitionTimeline'),indent=2))
  # Diagnostic motion-only captures stay focused on gait transitions; the full
  # gameplay review retains its attack coverage.
  for degrees in ([] if args.phase=='motion' and args.motion_series else [0,45,90,135,180,225,270,315]):
   walk(*plaza);a=math.radians(degrees);page.mouse.move(*point(plaza[0]+math.cos(a)*3,plaza[1]+math.sin(a)*3));page.keyboard.press('f');elapsed(.22);page.screenshot(path=str(out/f'attack-{degrees}.png'));elapsed(.7)
 if args.phase in ['all','reactions']:
  for row,name in enumerate(['S','SE','E','NE','N','NW','W','SW']):
   walk(*plaza);position=snap()['player']['position'];angle=math.pi/2-row*math.pi/4
   direction=page.evaluate('(a)=>AstraeonView.inverse(Math.cos(a),Math.sin(a))',angle);length=math.hypot(direction['x'],direction['y'])
   page.mouse.move(*point(position['x']+direction['x']/length*3,position['y']+direction['y']/length*3));page.keyboard.press('f');elapsed(.9)
   actual=page.evaluate('AstraeonDirectionalArt.directionRow(AstraeonQA.snapshot().player.rotation)');assert actual==row,(name,actual,snap()['player'])
   page.locator('[data-open="systems"]').click();page.locator('[data-nav="pvp"]').click()
   # Observe hit/death caused by the real sparring encounter. No HP, actor,
   # pose, facing, save or clock setter is used to manufacture these states.
   page.evaluate("""()=>{window.reactionFrames=[];window.reactionDone=false;let last=-1,dead=false;const observe=()=>{const s=AstraeonQA.snapshot(),state=s.animation.state,p=s.player.position,v=AstraeonSpatialView;dead||=s.save.hp===0;if(dead&&s.save.hp>0){reactionDone=true;removeEventListener('astraeon-frame',observe);return}if(!['hit','death'].includes(state)||s.time>s.animation.until||s.time-last<.045)return;last=s.time;const c=document.createElement('canvas');c.width=200;c.height=180;const g=c.getContext('2d'),q=v.worldToScreen(p.x,p.y,p.z),x=q.x,y=q.y,buffer=v.renderer.getDrawingBufferSize(new AstraeonSpatialRenderer.THREE.Vector2());g.drawImage(v.canvas,(x-100)*buffer.x/v.width,(y-135)*buffer.y/v.height,200*buffer.x/v.width,180*buffer.y/v.height,0,0,200,180);const shadow=v.actors.get('player').shadow;reactionFrames.push({time:s.time,state,progress:(s.time-s.animation.started)/s.animation.duration,direction:AstraeonDirectionalArt.directionRow(s.player.rotation),player:s.player,shadow:{visible:shadow.visible,opacity:shadow.material.opacity},image:c.toDataURL()})};addEventListener('astraeon-frame',observe)}""")
   page.locator('#pvp-start').click();page.wait_for_function('reactionDone',timeout=180000)
   frames=page.evaluate('reactionFrames');folder=out/'reaction-series'/name;folder.mkdir(parents=True,exist_ok=True)
   for i,frame in enumerate(frames):(folder/f'{i:03d}.png').write_bytes(base64.b64decode(frame.pop('image').split(',')[1]))
   (folder/'frames.json').write_text(json.dumps(frames,indent=2))
   assert {f['state'] for f in frames}=={'hit','death'} and all(f['direction']==row for f in frames),(name,frames)
   assert all(not f['shadow']['visible'] and f['shadow']['opacity']==0 for f in frames if f['state']=='death' and f['progress']>=1)
   evidence.append({'reaction_direction':name,'states':['hit','death'],'rendered_frames':len(frames),'normal_respawn':snap()['save']['hp']>0});print('REACTIONS',name,flush=True)
 # Approach the gate from town, then use its actual authored field threshold.
 walk(*arrival);capture('gate-departure');exit=next(e for e in snap()['town']['transitions'] if e['to']==2);click(exit['x'],exit['y'],17);page.wait_for_function('AstraeonQA.snapshot().save.zone===2',timeout=20000);capture('field-threshold')
 saved=snap()['save'];page.reload(wait_until='networkidle');page.wait_for_selector('#world');assert snap()['save']['name']==saved['name'] and snap()['save']['zone']==2
 # Live review telemetry, not physical-device certification.
 report={'layout':snap()['town']['layout'],'evidence':evidence,'runtime_errors':errors,'resource_errors':resources}
 (out/'report.json').write_text(json.dumps(report,indent=2));context.close();b.close();assert not errors and not resources,report
 print('REVIEW ARTIFACTS',out,flush=True)
