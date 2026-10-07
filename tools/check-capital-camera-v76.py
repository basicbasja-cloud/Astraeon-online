"""Exercise the selected camera through ordinary mouse controls and resets."""
import json, hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'docs/review/wayfarer-capital-v76/property-frontages/camera-controls';O.mkdir(exist_ok=True)
fixture=json.loads((R/'docs/review/wayfarer-capital-v75/before-density/views/fixture-save.json').read_text());fixture.update(x=128,y=150)
errors=[];records=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-webgl','--enable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    page=browser.new_page(viewport={'width':910,'height':512});page.set_default_timeout(300000)
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.add_init_script('localStorage.setItem("astraeon-iso-v1",JSON.stringify('+json.dumps(fixture)+'))')
    page.goto('http://127.0.0.1:8011/?qa=1',wait_until='domcontentloaded')
    page.wait_for_function('document.getElementById("world") && window.AstraeonQA?.snapshot().renderer')
    baseline=page.evaluate('AstraeonView.cameraBaseline')
    def sample(name):
        record=page.evaluate('''()=>{
          const v=AstraeonSpatialView,a=v.actors.get('player'),g=a.mesh.geometry,p=g.attributes.position,uv=g.attributes.uv;
          a.mesh.updateWorldMatrix(true,false);
          const q=[];for(let i=0;i<p.count;i++){const t=a.mesh.localToWorld(a.mesh.position.clone().set(p.getX(i),p.getY(i),p.getZ(i)));q.push(v.worldToScreen(t.x,t.y,t.z));}
          const width=Math.hypot(q[1].x-q[0].x,q[1].y-q[0].y),height=Math.hypot(q[3].x-q[0].x,q[3].y-q[0].y),im=a.mesh.material.map.image;
          const u=[],w=[];for(let i=0;i<uv.count;i++){u.push(uv.getX(i));w.push(uv.getY(i));}
          const artworkRatio=(Math.max(...u)-Math.min(...u))*im.width/((Math.max(...w)-Math.min(...w))*im.height);
          const position=AstraeonQA.snapshot().player.position,z=AstraeonContent.nativeWorld.spatial.elevationAt(position.x+1,position.y),screen=v.worldToScreen(position.x+1,position.y,z),world=v.screenToWorld(screen.x,screen.y);
          return {camera:structuredClone(v.cameraProfile),spriteAspectError:Math.abs(width/height/artworkRatio-1),projectedHeight:height,
            groundInverseError:world?Math.hypot(world.x-position.x-1,world.y-position.y):null,
            resolution:{width:v.canvas.width,height:v.canvas.height,cssWidth:v.width,cssHeight:v.height}};
        }''')
        record['name']=name;assert record['spriteAspectError']<.06,record
        assert record['groundInverseError'] is not None and record['groundInverseError']<.001,record
        assert record['resolution']['width']>=record['resolution']['cssWidth']
        assert record['resolution']['height']>=record['resolution']['cssHeight']
        records.append(record);print(name,record['camera']['pitch'],record['camera']['yaw'],record['camera']['zoom'],flush=True)
        return record
    record=sample('default')
    for key in ('fov','pitch','yaw','zoom'):assert abs(record['camera'][key]-baseline[key])<.01
    def drag(key,dx=0,dy=0):
        rect=page.locator('#world').bounding_box();x=rect['x']+rect['width']/2;y=rect['y']+rect['height']/2
        field='pitch' if key=='Shift' else 'zoom' if key=='Control' else 'yaw'
        initial=page.evaluate('(key)=>AstraeonView.cameraProfile[key]',field)
        target=initial+(dy/rect['height']*300 if key=='Shift' else -dy*1.5 if key=='Control' else -dx/rect['width']*720)
        page.wait_for_timeout(500)
        if key:page.keyboard.down(key)
        page.mouse.move(x,y);page.mouse.down(button='right');page.mouse.move(x+dx,y+dy,steps=8);page.mouse.up(button='right')
        if key:page.keyboard.up(key)
        page.wait_for_function('(a)=>Math.abs(AstraeonView.cameraProfile[a.key]-a.value)<.05',arg={'key':field,'value':target},timeout=30000)
    def reset(key,field):
        rect=page.locator('#world').bounding_box();page.wait_for_timeout(500)
        if key:page.keyboard.down(key)
        page.mouse.dblclick(rect['x']+rect['width']/2,rect['y']+rect['height']/2,button='right',delay=80)
        if key:page.keyboard.up(key)
        page.wait_for_function('(a)=>Math.abs(AstraeonView.cameraProfile[a.key]-a.value)<.05',arg={'key':field,'value':baseline[field]})
        sample(field+' reset')
    drag(None,dx=-910*40/720);assert abs(sample('orbit')['camera']['yaw']-baseline['yaw']-40)<.1
    reset(None,'yaw')
    rect=page.locator('#world').bounding_box();drag('Shift',dy=rect['height']*10/300);assert abs(sample('pitch')['camera']['pitch']-baseline['pitch']-10)<.1
    reset('Shift','pitch')
    drag('Control',dy=10);assert abs(sample('distance')['camera']['zoom']-baseline['zoom']+15)<.1
    reset('Control','zoom')
    page.screenshot(path=str(O/'default-reset.png'));browser.close()
assert not errors,errors
report={'sourceSHA256':hashlib.sha256((R/'world/v3/wayfarer-spatial.json').read_bytes()).hexdigest(),
        'runtimeSHA256':{n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ('world-view.js','world/v3/renderer.js')},
        'baseline':baseline,'samples':records,'ordinaryMouseControls':True,'spriteAspectVerified':True,'groundInverseVerified':True,'errors':errors,'pass':True}
(O/'report.json').write_text(json.dumps(report,indent=2)+'\n')
