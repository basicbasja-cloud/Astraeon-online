"""Normal mouse/keyboard camera gestures, picking and an independent lens check."""
import argparse,json,math,os
from pathlib import Path
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8011');ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=os.environ.get('ASTRAEON_BROWSER','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--enable-gpu']+(['--use-angle=d3d11'] if os.name=='nt' else ['--use-angle=swiftshader','--enable-unsafe-swiftshader']))
    page=b.new_page(viewport={'width':1280,'height':800});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(args.url+'/index.html?qa=1');page.locator('#newname').fill('Camera Review');page.locator('#create').click();page.wait_for_selector('#world');page.wait_for_timeout(500)
    def snapshot():return page.evaluate('AstraeonQA.snapshot()')
    def lens_check():
        # Native content uses a reflected horizontal coordinate convention.
        # Compare with a standard Three PerspectiveCamera in that convention;
        # this also catches an incorrect lens, depth denominator or orbit sign.
        result=page.evaluate('''()=>{const T=AstraeonSpatialRenderer.THREE,v=AstraeonSpatialView,c=v.cameraProfile,f=AstraeonView.inverse(v.focus.x,v.focus.y),pitch=c.pitch*Math.PI/180,yaw=c.yaw*Math.PI/180,d=c.zoom/2;
          const z=v.focus.z||0,camera=new T.PerspectiveCamera(c.fov,v.width/v.height,1,1000);camera.up.set(0,0,1);camera.position.set(-f.x-Math.cos(pitch)*Math.sin(yaw)*d,f.y+Math.cos(pitch)*Math.cos(yaw)*d,z+Math.sin(pitch)*d);camera.lookAt(-f.x,f.y,z);camera.updateMatrixWorld();
          const samples=[[f.x,f.y,0],[f.x+3,f.y+5,0],[f.x-4,f.y-7,2],[f.x+2,f.y-1,6]];
          return samples.map(([x,y,z])=>{const actual=v.worldToScreen(x,y,z),q=new T.Vector3(-x,y,z).project(camera);return {pixelError:Math.hypot(actual.x-(q.x+1)*v.width/2,actual.y-(1-q.y)*v.height/2),depthError:Math.abs(actual.depth-q.z)}})}''')
        assert max(q['pixelError'] for q in result)<.001,result
        assert max(q['depthError'] for q in result)<.000001,result
        return result
    c=snapshot()['renderer']['cameraProfile'];assert c['kind']=='ragnarok' and c['fov']==15 and c['pitch']==46 and c['yaw']==0 and c['zoom']==125,c
    checks={'default':lens_check()};before=snapshot()['player']['position'];r=page.locator('#world').bounding_box();x=r['x']+r['width']*.5;y=r['y']+r['height']*.55
    def drag(dx,dy,modifier=None):
        if modifier:page.keyboard.down(modifier)
        page.mouse.move(x,y);page.mouse.down(button='right');page.mouse.move(x+dx,y+dy,steps=8);page.mouse.up(button='right')
        if modifier:page.keyboard.up(modifier)
        page.wait_for_timeout(700)
    drag(-50,0);assert snapshot()['renderer']['cameraProfile']['yaw']>20;checks['orbit']=lens_check()
    drag(0,-25,'Shift');assert snapshot()['renderer']['cameraProfile']['pitch']<45;checks['tilt']=lens_check()
    page.mouse.move(x,y);page.mouse.wheel(0,120);page.wait_for_timeout(700);assert snapshot()['renderer']['cameraProfile']['zoom']>139;checks['zoom']=lens_check()
    after=snapshot()['player']['position'];assert math.hypot(after['x']-before['x'],after['y']-before['y'])<.001,'Camera gestures navigated the player'
    # Actual raycast lands at the intended authored floor after an orbit/tilt/zoom.
    q=page.evaluate('''()=>{const s=AstraeonQA.snapshot(),w=AstraeonContent.nativeWorld.spatial,v=AstraeonSpatialView,p=s.player.position;
      return w.navCells.filter(n=>n.walkable&&n.y<p.y-.5&&Math.hypot(n.x-p.x,n.y-p.y)>2&&Math.hypot(n.x-p.x,n.y-p.y)<3&&AstraeonNavigation.clear(p,n,w.blocked)).map(n=>{const screen=v.worldToScreen(n.x,n.y,w.elevationAt(n.x,n.y));return {n,screen,hit:v.screenToWorld(screen.x,screen.y)}}).find(q=>q.screen.x>350&&q.screen.x<900&&q.screen.y>200&&q.screen.y<v.height-80&&!v.pickActor(q.screen.x,q.screen.y)?.startsWith('service/'))}''')
    assert q and math.hypot(q['n']['x']-q['hit']['x'],q['n']['y']-q['hit']['y'])<.001,q
    page.mouse.click(r['x']+q['screen']['x'],r['y']+q['screen']['y']);page.wait_for_function('(q)=>Math.hypot(AstraeonQA.snapshot().player.position.x-q.x,AstraeonQA.snapshot().player.position.y-q.y)<.4',arg=q['n'])
    checks['picking']=q;page.screenshot(path=str(args.output/'orbit-picking.png'))
    for modifier,key,value in [(None,'yaw',0),('Shift','pitch',46),('Control','zoom',125)]:
        if modifier:page.keyboard.down(modifier)
        page.mouse.click(x,y,button='right',click_count=2,delay=100)
        if modifier:page.keyboard.up(modifier)
        page.wait_for_timeout(750);assert abs(snapshot()['renderer']['cameraProfile'][key]-value)<.02,(key,snapshot()['renderer']['cameraProfile'])
    checks['reset']=lens_check();page.screenshot(path=str(args.output/'reset.png'))
    # Reach the raised civic precinct with ordinary clicks and compare the
    # elevated follow against the independent physical camera, including rays.
    for attempt in range(80):
        state=snapshot();pos=state['player']['position']
        if math.hypot(pos['x']-54,pos['y']-33)<.4:break
        step=page.evaluate('''()=>{const w=AstraeonContent.nativeWorld.spatial,v=AstraeonSpatialView,p=AstraeonQA.snapshot().player.position,route=w.route(p,{x:54,y:33});if(!route)return null;
          const a=route.find(q=>Math.hypot(q.x-p.x,q.y-p.y)>.12)||route.at(-1),d=Math.hypot(a.x-p.x,a.y-p.y),t=Math.min(1,3/d),q={x:p.x+(a.x-p.x)*t,y:p.y+(a.y-p.y)*t};return {q,screen:v.worldToScreen(q.x,q.y,w.elevationAt(q.x,q.y))}}''')
        assert step,'No raised precinct route';page.mouse.click(r['x']+step['screen']['x'],r['y']+step['screen']['y'])
        page.wait_for_function('(q)=>Math.hypot(AstraeonQA.snapshot().player.position.x-q.x,AstraeonQA.snapshot().player.position.y-q.y)<.4',arg=step['q'],timeout=15000)
    else:raise AssertionError('Raised precinct walk did not finish')
    page.wait_for_timeout(600);assert snapshot()['camera']['z']>1.4
    checks['raised-floor']=lens_check();page.screenshot(path=str(args.output/'raised-floor.png'));assert not errors,errors
    (args.output/'report.json').write_text(json.dumps({'checks':checks,'errors':errors,'camera':snapshot()['renderer']['cameraProfile']},indent=2));b.close()
print('PASS classic RO camera defaults, physical lens, orbit, tilt, zoom, reset and click navigation')
