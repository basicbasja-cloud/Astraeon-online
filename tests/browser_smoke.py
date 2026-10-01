"""Functional checks against a running static server; no runtime mutation/debug setters.
Run: python3 tests/browser_smoke.py --url http://127.0.0.1:8000
Artifacts are written outside the checkout by default.
"""
import argparse,base64,hashlib,json,math
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8000');parser.add_argument('--output',default='/tmp/astraeon-qa');parser.add_argument('--only',default='');parser.add_argument('--world',default='');args=parser.parse_args()
output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
checks=[];failures=[];errors=[];http_errors=[]
def check(name,fn):
 if args.only and args.only not in name:return
 try:
  value=fn();checks.append({'name':name,'result':'passed','evidence':value});print('PASS',name,flush=True)
 except Exception as e:
  failures.append({'name':name,'error':str(e)});print('FAIL',name,str(e),flush=True)
def angular(a,b):return math.atan2(math.sin(a-b),math.cos(a-b))
def snapshot(page):return page.evaluate('AstraeonQA.snapshot()')
def elapsed(page,seconds):
 start=snapshot(page)['time'];page.wait_for_function('(start)=>AstraeonQA.snapshot().time>start',arg=start+seconds)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 def new_page(save=None,width=1280,height=800,touch=False):
  context=browser.new_context(viewport={'width':width,'height':height},has_touch=touch)
  if save:
   context.add_init_script(f'if(!localStorage.getItem("astraeon-iso-v1"))localStorage.setItem("astraeon-iso-v1",{json.dumps(json.dumps(save))})')
  page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:http_errors.append(f'{r.status} {r.url}') if r.status>=400 else None)
  page.goto(args.url+'/index.html?qa=1'+('&world='+args.world if args.world else ''),wait_until='networkidle');page.wait_for_function('document.querySelector("#world")||document.querySelector("#create")');return context,page
 context,page=new_page();page.locator('#newname').fill('Directional QA');page.locator('#create').click();page.wait_for_selector('#world');elapsed(page,.1);base=snapshot(page)['save'];context.close()
 def fixture(**updates):return {**base,**updates}
 def keyboard_case(keys):
  context,page=new_page(fixture(x=14.5,y=26));start=snapshot(page)
  for key in keys:page.keyboard.down(key)
  elapsed(page,.8)
  mid=snapshot(page)
  for key in keys:page.keyboard.up(key)
  elapsed(page,.2)
  end=snapshot(page);vx=mid['player']['velocity']['x'];vy=mid['player']['velocity']['y'];assert math.hypot(vx,vy)>3.3,mid['player']
  x=sum(1 if key=='d' else -1 if key=='a' else 0 for key in keys);y=sum(1 if key=='s' else -1 if key=='w' else 0 for key in keys)
  basis=mid['view']['basis'];expected=math.atan2(basis['xx']*y-basis['xy']*x,basis['yy']*x-basis['yx']*y)
  assert abs(angular(mid['player']['rotation'],expected))<.04,(mid['player'],expected)
  assert end['player']['speed']==0,('stopped speed',end['player'])
  elapsed(page,.5);settled=snapshot(page)['player'];assert abs(angular(settled['rotation'],settled['desiredRotation']))<.04,settled
  context.close();return {'rotation':round(mid['player']['rotation'],3),'speed':round(math.hypot(vx,vy),3)}
 for keys in [['w'],['w','d'],['d'],['s','d'],['s'],['s','a'],['a'],['w','a']]:check('keyboard '+'+'.join(keys),lambda keys=keys:keyboard_case(keys))
 def mobile_case():
  context,page=new_page(fixture(),width=390,height=844,touch=True)
  rect=page.locator('#mobile-controls').bounding_box();knob=page.locator('#joystick-knob').bounding_box();cx=rect['x']+rect['width']/2;cy=rect['y']+rect['height']/2;radius=(rect['width']-knob['width'])/2
  def joy(x,y,kind):
   page.locator('#mobile-controls').dispatch_event(kind,{'pointerId':1,'pointerType':'touch','clientX':cx+x*radius,'clientY':cy+y*radius,'buttons':0 if kind=='pointerup' else 1,'bubbles':True})
  # Synthetic pointer events have no native capture ID; use Chromium's real mouse pointer,
  # routed through the exact same analog handler, with touch layout enabled.
  page.mouse.move(cx,cy);page.mouse.down();page.mouse.move(cx+.35*radius,cy);elapsed(page,.7);slow=snapshot(page)['player'];assert .95<slow['speed']<1.5,slow
  page.mouse.move(cx+radius,cy);elapsed(page,.4);fast=snapshot(page)['player'];assert 3.3<fast['speed']<3.6,fast
  headings=[]
  for degrees in range(0,360,23):
   a=math.radians(degrees);page.mouse.move(cx+math.cos(a)*radius,cy+math.sin(a)*radius);elapsed(page,.09);headings.append(snapshot(page)['player']['desiredRotation'])
  page.mouse.up();elapsed(page,.1);assert snapshot(page)['player']['speed']==0
  assert len({round(a,2) for a in headings})==len(headings)
  page.screenshot(path=str(output/'mobile-portrait.png'));context.close();return {'slow_speed':slow['speed'],'full_speed':fast['speed'],'analog_angles':len(headings)}
 check('mobile analog magnitude and circular input',mobile_case)
 def dodge_case():
  context,page=new_page(fixture());page.keyboard.down('w');page.keyboard.down('d');elapsed(page,.12)
  page.evaluate("""()=>{window.dodgeSamples=[];addEventListener('keydown',function collect(e){if(e.code!=='Space')return;removeEventListener('keydown',collect);const start=AstraeonQA.snapshot().time;const record=()=>{dodgeSamples.push(AstraeonQA.snapshot());if(AstraeonQA.snapshot().time-start<.65)requestAnimationFrame(record)};requestAnimationFrame(record)})}""")
  page.keyboard.press('Space');page.keyboard.up('w');page.keyboard.up('d');page.wait_for_function('dodgeSamples.length>1&&dodgeSamples.at(-1).time-dodgeSamples[0].time>.6')
  samples=page.evaluate('dodgeSamples');active=[s for s in samples if s['animation']['state']=='dodge'];assert len(active)>=2,'dodge animation not observed';start,end=active[0],active[-1]
  dx=end['player']['position']['x']-start['player']['position']['x'];dy=end['player']['position']['y']-start['player']['position']['y'];basis=end['view']['basis'];sx=basis['xx']*dx+basis['yx']*dy;sy=basis['xy']*dx+basis['yy']*dy;assert sx>0 and sy<0,('screen dodge direction',sx,sy);assert samples[-1]['animation']['state']!='dodge','dodge did not recover';context.close();return {'world_delta':[dx,dy],'screen_delta':[sx,sy],'active_samples':len(active),'recovery_observed':True}
 check('diagonal dodge',dodge_case)
 def attack_case(cls,degrees):
  context,page=new_page(fixture(cls=cls));a=math.radians(degrees);dx=math.cos(a)*4;dy=math.sin(a)*4;snap=snapshot(page);r=page.locator('#world').bounding_box();origin=snap['player']['position'];cam=snap['camera']
  v=snap['view'];px=r['width']/2+((origin['x']+dx)*v['basis']['xx']+(origin['y']+dy)*v['basis']['yx']-cam['x'])*v['zoom'];py=r['height']*v['anchorY']+((origin['x']+dx)*v['basis']['xy']+(origin['y']+dy)*v['basis']['yy']-cam['y'])*v['zoom'];page.mouse.move(r['x']+px,r['y']+py)
  page.evaluate("""()=>{window.attackSamples=[];addEventListener('keydown',function collect(e){if(e.key!=='f')return;removeEventListener('keydown',collect);const start=AstraeonQA.snapshot().time;const record=()=>{const s=AstraeonQA.snapshot();attackSamples.push({time:s.time,player:s.player,action:s.action,projectiles:s.projectiles});if(s.time-start<1.4)requestAnimationFrame(record)};requestAnimationFrame(record)})}""")
  page.keyboard.press('f')
  page.wait_for_function('attackSamples.length>1&&attackSamples.at(-1).time-attackSamples[0].time>1.3')
  samples=page.evaluate('attackSamples')
  phases=[s for s in samples if s['action'] and s['action']['phase']=='active'];assert phases,('active phase never observed',samples[-1])
  for s in phases:assert abs(angular(s['player']['rotation'],a))<.04,(s,a)
  shots=[shot for s in samples for shot in s['projectiles']]
  if cls in [3,12]:
   assert shots,'projectile not released'
   for shot in shots:assert abs(angular(math.atan2(shot['direction']['y'],shot['direction']['x']),a))<.01
  context.close();return {'active_samples':len(phases),'projectile_samples':len(shots)}
 for cls in [0,3,12]:
  for degrees in [0,45,90,135,180,225,270,315,17]:check(f'attack class {cls} heading {degrees}',lambda cls=cls,degrees=degrees:attack_case(cls,degrees))
 def responsive():
  context,page=new_page(fixture());elapsed(page,.5);initial=snapshot(page)
  sizes=[]
  for width,height in [(1280,720),(390,844),(844,390),(768,1024)]:
   page.set_viewport_size({'width':width,'height':height});elapsed(page,.15);s=snapshot(page);assert s['save']['name']==initial['save']['name'];assert s['player']['position']==initial['player']['position'];assert s['player']['rotation']==initial['player']['rotation'];assert s['time']>initial['time'];sizes.append([width,height]);page.screenshot(path=str(output/f'viewport-{width}-{height}.png'))
  page.evaluate('navigator.serviceWorker.ready');assert page.evaluate('navigator.serviceWorker.controller!==null');assert 'astraeon-static-v30' in page.evaluate('caches.keys()')
  page.reload(wait_until='networkidle');page.wait_for_selector('#world');assert snapshot(page)['save']['name']==initial['save']['name']
  context.close();return {'viewports':sizes,'service_worker':'v30','legacy_save_reload':'passed'}
 check('responsive state continuity, service worker, and legacy saves',responsive)
 def gallery():
  context,page=new_page(fixture());result=page.evaluate('''()=>{const canvas=document.createElement('canvas');canvas.width=1120;canvas.height=450;canvas.id='direction-gallery';document.body.replaceChildren(canvas);const ctx=canvas.getContext('2d');ctx.fillStyle='#1d3038';ctx.fillRect(0,0,1120,450);const hashes=[];for(let row=0;row<3;row++)for(let col=0;col<8;col++){const a=col*Math.PI/4,facing=AstraeonView.inverse(Math.cos(a),Math.sin(a)),t=new AstraeonMotion.CharacterTransform(0,0,Math.atan2(facing.y,facing.x));t.tick(0,0,1/60);const iso=(x,y,z=0)=>({x:col*140+70+x*48,y:row*150+125+y*31+x*7-z});AstraeonCharacters.humanoid(ctx,iso,t,{archetype:['warrior','mage','ranger'][row],time:0,scale:1.2});ctx.fillStyle='#e8d6b4';ctx.font='12px system-ui';ctx.textAlign='center';ctx.fillText(col*45+'°',col*140+70,row*150+145);hashes.push(Array.from(ctx.getImageData(col*140,row*150,140,130).data).reduce((h,v)=>(h*31+v)>>>0,0))}return {data:canvas.toDataURL(),hashes}}''')
  hashes=result['hashes'];assert all(len(set(hashes[row*8:row*8+8]))==8 for row in range(3)),hashes
  (output/'direction-gallery.png').write_bytes(base64.b64decode(result['data'].split(',')[1]));context.close();return {'distinct_renders_per_class':8}
 check('illustrated front, back, side, and diagonal views',gallery)
 def walk_gallery():
  context,page=new_page(fixture());result=page.evaluate("""()=>{const canvas=document.createElement('canvas');canvas.width=1120;canvas.height=450;document.body.replaceChildren(canvas);const ctx=canvas.getContext('2d');ctx.fillStyle='#1d3038';ctx.fillRect(0,0,1120,450);const hashes=[];for(let row=0;row<3;row++)for(let col=0;col<8;col++){const t=new AstraeonMotion.CharacterTransform(0,0,0);t.speed=3;t.gait=col/8;t.state='walk';const iso=(x,y,z=0)=>({x:col*140+70+x*48,y:row*150+125+y*31+x*7-z});AstraeonDirectionalArt.humanoid(ctx,iso,t,{archetype:['warrior','mage','ranger'][row],state:'walk',time:0,scale:1.2});hashes.push(Array.from(ctx.getImageData(col*140,row*150,140,130).data).reduce((h,v)=>(h*31+v)>>>0,0))}return {data:canvas.toDataURL(),hashes,headCoverage:Array.from({length:24},(_,i)=>{const pixels=ctx.getImageData((i%8)*140+15,Math.floor(i/8)*150+10,110,50).data;let count=0;for(let n=0;n<pixels.length;n+=4)if(pixels[n]>90&&pixels[n+1]>60)count++;return count})}}""")
  assert all(count>20 for count in result['headCoverage']),result['headCoverage']
  distinct=[len(set(result['hashes'][row*8:row*8+8])) for row in range(3)]
  assert distinct==[8,8,8],result['hashes']
  (output/'walk-gallery.png').write_bytes(base64.b64decode(result['data'].split(',')[1]));context.close();return {'stride_phases':8,'distinct_renders_per_class':distinct,'rear_view_policy':'eight-phase registered cycles'}
 check('extended painted stride cycles',walk_gallery)
 def golden_registration():
  context,page=new_page(fixture(cls=0));result=page.evaluate("""()=>{
   const canvas=document.createElement('canvas');canvas.width=200;canvas.height=150;const ctx=canvas.getContext('2d');
   function bounds(row,state,gait=0){
    ctx.clearRect(0,0,200,150);const heading=Math.PI/2-row*Math.PI/4,facing=AstraeonView.inverse(Math.cos(heading),Math.sin(heading)),t=new AstraeonMotion.CharacterTransform(0,0,Math.atan2(facing.y,facing.x));t.speed=state==='walk'?3:0;t.gait=gait;t.state=state;
    AstraeonDirectionalArt.humanoid(ctx,(x,y,z=0)=>({x:100+x*48-y*10,y:130+x*7+y*31-z}),t,{archetype:'warrior',state,progress:.2});
    const pixels=ctx.getImageData(0,0,200,150).data;let left=200,right=-1,top=150,bottom=-1;
    for(let y=0;y<150;y++)for(let x=0;x<200;x++)if(pixels[(y*200+x)*4+3]>128){left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y)}
    return {height:bottom-top+1,width:right-left+1,bottom,top};
   }
   return Array.from({length:8},(_,row)=>({row,idle:bounds(row,'idle'),walk:Array.from({length:8},(_,i)=>bounds(row,'walk',i/8)),hit:bounds(row,'hit'),death:bounds(row,'death')}));
  }""")
  for direction in result:
   idle=direction['idle'];assert 60<=idle['height']<=72,direction
   # A high-angle gait projects the forward foot below the root. Stature is
   # measured at the head, while contact bounds are checked against authored feet.
   for frame,walk in enumerate(direction['walk']):
    assert abs(walk['top']-idle['top'])<=5,direction
    assert abs(walk['top']-direction['walk'][0]['top'])<=1,direction
    contact=page.evaluate('(v)=>{const r=AstraeonHeroRegistration["warrior-walk"],f=r.frames[v[0]*8+v[1]];return 130+(Math.max(...f.contacts.map(c=>c.y))-f.footAnchorY)*70/r.heights[v[0]]}',[direction['row'],frame])
    assert abs(walk['bottom']-contact)<=2,(direction,contact)
   assert direction['hit']['height']>direction['death']['height']*1.5,direction
   assert direction['death']['width']>direction['death']['height']*2,direction
  context.close();return {'directions':8,'gait_samples':64,'stable_stature_and_ground_contact':True,'distinct_standing_hit_and_fallen_death':True}
 check('Golden Warrior stable stature, grounded gait and distinct reactions',golden_registration)
 def death_recovery():
  context,page=new_page(fixture(zone=2,x=17,y=22,hp=1));initial=snapshot(page)['save'];page.evaluate("window.deathSeen=false;window.watchDeath=true;const observe=()=>{if(!watchDeath)return;if(AstraeonQA.snapshot().save.hp===0)deathSeen=true;requestAnimationFrame(observe)};requestAnimationFrame(observe)")
  page.wait_for_function('AstraeonQA.snapshot().save.hp===0',timeout=30000);page.screenshot(path=str(output/'warrior-death-runtime.png'));
  page.wait_for_function('AstraeonQA.snapshot().save.zone===0&&AstraeonQA.snapshot().save.hp>0',timeout=30000);assert page.evaluate('deathSeen');page.evaluate('watchDeath=false');after=snapshot(page)['save'];assert after['gold']==max(0,initial['gold']-8);assert after['hp']==math.ceil(after['maxHp']*.65);assert abs(after['x']-14.5)<.01 and abs(after['y']-18)<.01;page.reload(wait_until='networkidle');page.wait_for_selector('#world');assert snapshot(page)['save']['gold']==after['gold'];context.close();return {'death_pose_observed':True,'recovery_zone':0,'gold_cost':8,'reload':'passed'}
 check('defeat, town recovery and persisted penalty',death_recovery)
 def hit_capture():
  context,page=new_page(fixture(cls=0,zone=2,x=17,y=22,hp=100))
  page.wait_for_function('AstraeonQA.snapshot().animation.state==="hit"',timeout=30000)
  page.screenshot(path=str(output/'warrior-hit-runtime.png'))
  assert snapshot(page)['save']['hp']<100
  context.close();return {'actual_enemy_hit':'captured'}
 check('Warrior hit presentation in actual field combat',hit_capture)

 def load_retry():
  context,page=new_page(fixture());initial=snapshot(page)['save'];context.route('**/meadow-ground-v1.webp',lambda route:route.abort());page.locator('[data-open="map"]').click();page.locator('[data-travel="2"]').click();page.wait_for_selector('.transition-overlay',state='detached');assert snapshot(page)['save']['zone']==0;assert snapshot(page)['save']['gold']==initial['gold'];context.unroute('**/meadow-ground-v1.webp');page.locator('[data-travel="2"]').click();page.wait_for_function('AstraeonQA.snapshot().save.zone===2');assert snapshot(page)['save']['gold']==initial['gold']-5;context.close();return {'failed_travel_preserved_zone_and_gold':True,'retry':'passed'}
 check('lazy zone loading failure and successful retry',load_retry)
 def completion_scope():
  context,page=new_page(fixture(chapters=[0],discovered=[0,1,2],lv=3));assert 'พิชิตศาลแล้ว' in page.locator('#mission').inner_text();page.locator('[data-open="journal"]').click();assert 'Shenzhou' in page.locator('#modal .notification').first.inner_text();page.keyboard.press('Escape');page.locator('[data-open="map"]').click();assert page.locator('[data-travel]').count()==3;page.keyboard.press('Escape');page.locator('[data-open="systems"]').click();page.locator('[data-nav="raid"]').click();assert page.locator('[data-dungeon]').count()==1;context.close()
  context,page=new_page(fixture(chapters=[0,1],discovered=[0,1,2,3],lv=5));page.locator('[data-open="map"]').click();assert page.locator('[data-travel]').count()==5;page.keyboard.press('Escape');page.locator('[data-open="systems"]').click();page.locator('[data-nav="raid"]').click();assert page.locator('[data-dungeon]').count()==4;context.close();return {'first_clear_stays_in_shenzhou':True,'legacy_region_and_chapter_access':'preserved'}
 check('Shenzhou completion and legacy content access',completion_scope)
 def enemy_and_gameplay():
  context,page=new_page(fixture(zone=2,x=17,y=22,cls=3,lv=5,maxHp=500,hp=500,equipment={'weapon':'Astral Blade','armor':'Warden Plate','relic':'None'}));elapsed(page,.1);initial=snapshot(page);assert len(initial['enemies'])>=4
  button=page.locator('[data-action="attack"]').bounding_box();page.mouse.move(button['x']+button['width']/2,button['y']+button['height']/2);page.mouse.down();elapsed(page,4);page.mouse.up();after=snapshot(page);assert after['save']['kills']>initial['save']['kills'],after['save'];assert after['save']['xp']>initial['save']['xp'];assert after['save']['gold']>initial['save']['gold']
  page.screenshot(path=str(output/'field.png'))
  page.locator('[data-open="systems"]').click();page.locator('[data-nav="raid"]').click();page.locator('[data-dungeon="0"]').click();elapsed(page,.1);dungeon=snapshot(page);assert dungeon['save']['zone']==1;assert len(dungeon['enemies'])==2
  page.screenshot(path=str(output/'dungeon.png'))
  page.locator('[data-open="systems"]').click();page.locator('[data-nav="raid"]').click();page.locator('#leave-dungeon').click();elapsed(page,.1);assert snapshot(page)['save']['zone']==0
  page.keyboard.press('q');saved=snapshot(page)['save'];page.reload(wait_until='networkidle');restored=snapshot(page)['save'];assert saved['gold']==restored['gold'];assert saved['kills']==restored['kills'];assert saved['inventory']==restored['inventory']
  context.close();return {'field_enemies':len(initial['enemies']),'kills_added':after['save']['kills']-initial['save']['kills'],'dungeon_entry_exit':'passed','progress_reload':'passed'}
 check('field combat, loot, progression, dungeon entry/exit and reload',enemy_and_gameplay)
 browser.close()
report={'checks':checks,'failures':failures,'runtime_errors':errors,'http_errors':http_errors};(output/'report.json').write_text(json.dumps(report,indent=2));print(json.dumps({'passed':len(checks),'failed':len(failures),'runtime_errors':errors,'http_errors':http_errors,'artifacts':str(output)},indent=2));assert not failures and not errors and not http_errors,report
