"""Capture fixed playable Golden Wayfarer views for human art review.

Example: python3 tools/capture-wayfarer-views.py --views arrival,avenue,plaza
Requires the local game server and Playwright/Chromium already used for review.
"""
import argparse
import os
import json
import hashlib
import base64
from pathlib import Path

from playwright.sync_api import sync_playwright


VIEWS = {
    'gate': (27, 44),
    'arrival': (27, 47.1),
    'avenue': (27, 36),
    'plaza': (27, 29),
    'hall-axis': (27, 17),
    'hall-terrace': (27, 15),
    'market': (42, 27),
    'inn': (11.5, 23.5),
    'blacksmith': (13, 31.5),
    'shrine': (43, 16),
    'residential': (38, 39),
    'frontage-shop': (34.4, 25.3),
    'frontage-home': (40, 39.5),
    'town-edge': (34, 44),
    'overview': (27, 23.5),
    'hall-skyline': (36.5, 4.5),
    'river-bank': (6.5, 26.5),
    'river-falls': (7.25, 34.5),
    'gate-spillways': (21, 42.5),
    'hall-processional-view': (27, 40),
    'tree-oak-contact': (32.6, 31),
    'tree-garden-contact': (13.15, 18.75),
    'council': (34,38.5),
    'archive': (94,38.5),
    'exchange': (94,72),
    'townhouses': (16,78),
    'street-west': (40,100.5),
    'street-east': (88,100.5),
    'street-artisan': (40,83.5),
    'street-borough': (88,113.5),
    'bank-east': (112,99),
    'artisan-ward': (40,91),
    'south-commons': (48,108),
    'willow-borough': (96,108),
    'royal-parterre': (64,46),
    'south-gate': (64,131.5),
    'east-gate': (117,72),
    'north-gate': (64,12.5),
    'riverwatch': (119,99),
    'council-roof': (41.5,30),
    'archive-roof': (101.5,30),
    'exchange-roof': (101.5,63),
    'hall-court': (64,28),
    'artisan-court': (52.4,82.6),
    'willow-court': (77.25,100),
    'plaza-frontages': (64,66),
    'merchant-frontage': (24,82.5),
    'capital-tree-contact': (72.5,73.5),
}


def capture(url, output, names, zoom=None, yaw=None, pitch=None, capture_scale=None, startup_timeout_ms=120000, verify_culling=False, append=False, template_file=None, viewport_width=1280, scene_only=False, viewport_height=800):
    output.mkdir(parents=True, exist_ok=True)
    records = json.loads((output/'views.json').read_text()) if append and (output/'views.json').exists() else []
    raw=Path('world/v3/wayfarer-spatial.json').read_bytes();source_hash=hashlib.sha256(raw).hexdigest()
    native=json.loads(raw);route=native['route'];layout=native['layoutId'];capital='capital' in layout
    architecture_revision=native.get('architectureRevision')
    runtime_hashes={name:hashlib.sha256(Path(name).read_bytes()).hexdigest()
                    for name in ('world-view.js','world/v3/renderer.js','boot.js')}
    ground_bake=native.get('lighting',{}).get('groundShadow')
    ground_hash=hashlib.sha256(Path(ground_bake['file']).read_bytes()).hexdigest() if ground_bake else None
    doors=[{'owner':o['id'],'vertices':a['vertices']}
           for o in native['objects'] for a in o['parts'] if a['id'].endswith('-door-leaf')]
    del raw,native  # The capture needs metadata, not a retained 89 MB mesh document.
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=os.environ.get('ASTRAEON_BROWSER', '/usr/bin/chromium'), headless=True,
            args=['--no-sandbox', '--enable-webgl', '--enable-gpu'] +
                 (['--use-angle=d3d11'] if os.name == 'nt' else
                  ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']))
        context = browser.new_context(viewport={'width': viewport_width, 'height': viewport_height},
                                      device_scale_factor=1)
        if template_file:
            template=json.loads(template_file.read_text())
            assert template['worldLayout']==layout, 'Capture template belongs to a different layout'
        else:
            first = context.new_page()
            first.set_default_timeout(startup_timeout_ms)
            first.goto(url, wait_until='domcontentloaded', timeout=startup_timeout_ms)
            first.locator('#create').wait_for(timeout=startup_timeout_ms)
            first.locator('#newname').fill('Golden Warrior')
            first.locator('#create').click(timeout=startup_timeout_ms)
            first.wait_for_function(
                'document.getElementById("world") && window.AstraeonQA && '
                'window.AstraeonQA.snapshot().renderer', timeout=startup_timeout_ms)
            template = first.evaluate('window.AstraeonQA.snapshot().save')
            first.close()
        (output/'fixture-save.json').write_text(json.dumps(template,indent=2)+'\n')
        for name in names:
            x, y = (v*2 for v in VIEWS[name])
            stop=next((a for a in route if a['name'].lower().replace(' ','-')==name),None)
            if stop:x,y=stop['position']
            if capital and name=='plaza-frontages':
                plaza=next((a for a in route if a['name'].lower()=='plaza'),None)
                if plaza:x,y=plaza['position']
            if capital and name=="gate":x,y=18,144
            if capital and name=="avenue":x,y=128,176
            if capital and name=="hall-skyline":x,y=128,100
            if name=="hall-terrace":x,y=(128,52) if capital else (54,24)
            if name=="hall-axis":x,y=(128,77) if capital else (54,42)
            page = context.new_page()
            page.set_default_timeout(startup_timeout_ms)
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('console', lambda message: errors.append(message.text) if message.type=='error' else None)
            state = {**template, 'x': x, 'y': y}
            page.add_init_script('localStorage.setItem("astraeon-iso-v1",'
                                 'JSON.stringify(' + json.dumps(state) + '))')
            page.goto(url, wait_until='domcontentloaded', timeout=startup_timeout_ms)
            page.wait_for_function(
                'document.getElementById("world") && window.AstraeonQA && '
                'window.AstraeonQA.snapshot().renderer', timeout=startup_timeout_ms)
            page.wait_for_timeout(450)
            if zoom is not None:
                current_zoom=page.evaluate('AstraeonQA.snapshot().renderer.cameraProfile.zoom')
                rect=page.locator('#world').bounding_box();pointer_x=rect['x']+rect['width']/2;pointer_y=rect['y']+rect['height']/2
                page.keyboard.down('Control');page.mouse.move(pointer_x,pointer_y);page.mouse.down(button='right');page.mouse.move(pointer_x,pointer_y-(zoom-current_zoom)/1.5,steps=8);page.mouse.up(button='right');page.keyboard.up('Control');page.wait_for_timeout(800)
            if yaw is not None:
                current_yaw=page.evaluate('AstraeonQA.snapshot().renderer.cameraProfile.yaw')
                rect=page.locator('#world').bounding_box();px=rect['x']+rect['width']/2;py=rect['y']+rect['height']/2
                page.mouse.move(px,py);page.mouse.down(button='right');page.mouse.move(px-(yaw-current_yaw)*rect['width']/720,py,steps=8);page.mouse.up(button='right');page.wait_for_timeout(800)
            if pitch is not None:
                current_pitch=page.evaluate('AstraeonQA.snapshot().renderer.cameraProfile.pitch')
                rect=page.locator('#world').bounding_box();px=rect['x']+rect['width']/2;py=rect['y']+rect['height']/2
                page.keyboard.down('Shift');page.mouse.move(px,py);page.mouse.down(button='right');page.mouse.move(px,py+(pitch-current_pitch)*rect['height']/300,steps=8);page.mouse.up(button='right');page.keyboard.up('Shift');page.wait_for_timeout(800)
            if capture_scale is not None:
                page.evaluate('(ratio)=>AstraeonSpatialView.renderer.setPixelRatio(ratio)', capture_scale)
                page.wait_for_timeout(450)
            snap = page.evaluate('window.AstraeonQA.snapshot()')
            assert abs(snap['save']['x']-x)<.05 and abs(snap['save']['y']-y)<.05, (name,'Blocked capture fixture fell back to a different position',[x,y],snap['save']['x'],snap['save']['y'])
            culling = None
            if verify_culling:
                # Render the exact same state twice: exhaustive static submission
                # versus the ordinary frustum. Restore flags before the screenshot.
                culling = page.evaluate('''()=>{
                  const v=AstraeonSpatialView,r=v.renderer,gl=r.getContext();
                  const nodes=v.scene.children.filter(n=>n.name.startsWith('static/')||n.name.startsWith('floor-shadow/'));
                  const flags=nodes.map(n=>n.frustumCulled),size=v.canvas.width*v.canvas.height*4;
                  const full=new Uint8Array(size),culled=new Uint8Array(size);
                  let exhaustive,ordinary;
                  try {
                    nodes.forEach(n=>n.frustumCulled=false);r.info.reset();r.render(v.scene,v.camera);
                    gl.readPixels(0,0,v.canvas.width,v.canvas.height,gl.RGBA,gl.UNSIGNED_BYTE,full);
                    exhaustive={calls:r.info.render.calls,triangles:r.info.render.triangles};
                    nodes.forEach((n,i)=>n.frustumCulled=flags[i]);r.info.reset();r.render(v.scene,v.camera);
                    gl.readPixels(0,0,v.canvas.width,v.canvas.height,gl.RGBA,gl.UNSIGNED_BYTE,culled);
                    ordinary={calls:r.info.render.calls,triangles:r.info.render.triangles};
                  } finally { nodes.forEach((n,i)=>n.frustumCulled=flags[i]); }
                  let differentPixels=0,maxChannelDifference=0;
                  for(let i=0;i<size;i+=4){let different=false;for(let k=0;k<4;k++){
                    const d=Math.abs(full[i+k]-culled[i+k]);different ||= d>0;
                    maxChannelDifference=Math.max(maxChannelDifference,d);
                  }if(different)differentPixels++;}
                  return {exhaustive,ordinary,differentPixels,maxChannelDifference,width:v.canvas.width,height:v.canvas.height};
                }''')
                assert culling['differentPixels'] == 0, (name, 'Frustum culling changes visible pixels', culling)
            image = output / (name + '.png')
            scene_image=None
            if scene_only:
                # Export the same native WebGL frame without DOM HUD panels.
                # The ordinary screenshot remains the gameplay/UI evidence.
                frame=page.evaluate('''()=>{const v=AstraeonSpatialView;v.renderer.render(v.scene,v.camera);return v.canvas.toDataURL('image/png').split(',')[1]}''')
                scene_image=output/(name+'-scene.png');scene_image.write_bytes(base64.b64decode(frame))
            page.screenshot(path=str(image))
            record = {'name': name, 'requested': [x, y],
                      'viewport': {'width': viewport_width, 'height': viewport_height},
                      'sourceSHA256': source_hash,
                      'runtimeSHA256': runtime_hashes,
                      'groundShadowSHA256': ground_hash,
                      'architectureRevision': architecture_revision,
                      'actual': [snap['save']['x'], snap['save']['y']],
                      'layout': snap['town']['layout'],
                      'actors': len(snap['renderer']['actors']),
                      'fadedBuildings': snap['renderer'].get('fadedBuildings', []),
                      'actorArtwork': {a['id']: a.get('motionSample', {}).get('frame') for a in snap['renderer']['actors']},
                      'renderCalls': snap['renderer']['calls'],
                      'renderTriangles': snap['renderer'].get('triangles'),
                      'frameMs': round(snap['renderer']['frameMs'], 2),
                      'rendererTiming': {key:snap['renderer'].get(key) for key in
                                         ('occlusionMs','renderMs','assemblyMs','totalMs')},
                      'device': snap['renderer'].get('device'),
                      'camera': snap['renderer'].get('cameraProfile'),
                      'captureScale': capture_scale,
                      'renderResolution': page.evaluate('({width:AstraeonSpatialView.canvas.width,height:AstraeonSpatialView.canvas.height,pixelRatio:AstraeonSpatialView.renderer.getPixelRatio()})'),
                      'errors': errors, 'image': str(image)}
            # A projected geometry rectangle permits person-relative comparison
            # across camera settings. It is not an alpha-tight artwork bound.
            record['playerGeometryScreenRect'] = page.evaluate('''()=>{
              const v=AstraeonSpatialView,a=v.actors.get('player');
              if(!a)return null;
              const p=a.mesh.geometry.attributes.position,q=[];
              a.mesh.updateWorldMatrix(true,false);
              for(let i=0;i<p.count;i++){
                const w=a.mesh.position.clone().set(p.getX(i),p.getY(i),p.getZ(i));
                a.mesh.localToWorld(w);q.push(v.worldToScreen(w.x,w.y,w.z));
              }
              const xs=q.map(p=>p.x),ys=q.map(p=>p.y);
              return {minX:Math.min(...xs),maxX:Math.max(...xs),
                minY:Math.min(...ys),maxY:Math.max(...ys),
                height:Math.max(...ys)-Math.min(...ys)};
            }''')
            record['playerAlphaScreenRect'] = page.evaluate('''()=>{
              const v=AstraeonSpatialView,a=v.actors.get('player');
              if(!a?.directFrame)return null;
              const im=a.mesh.material.map.image,uv=a.mesh.geometry.attributes.uv;
              const xs=[],ys=[];for(let i=0;i<uv.count;i++){xs.push(uv.getX(i));ys.push(1-uv.getY(i));}
              const x=Math.round(Math.min(...xs)*im.width),y=Math.round(Math.min(...ys)*im.height);
              const w=Math.round((Math.max(...xs)-Math.min(...xs))*im.width),h=Math.round((Math.max(...ys)-Math.min(...ys))*im.height);
              const canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;
              const ctx=canvas.getContext('2d',{willReadFrequently:true});ctx.drawImage(im,x,y,w,h,0,0,w,h);
              const pixels=ctx.getImageData(0,0,w,h).data;let xa=w,xb=-1,ya=h,yb=-1;
              for(let py=0;py<h;py++)for(let px=0;px<w;px++)if(pixels[(py*w+px)*4+3]>=16){xa=Math.min(xa,px);xb=Math.max(xb,px);ya=Math.min(ya,py);yb=Math.max(yb,py);}
              if(xb<0)return null;
              const p=a.mesh.geometry.attributes.position;a.mesh.updateWorldMatrix(true,false);
              const corner=i=>a.mesh.localToWorld(a.mesh.position.clone().set(p.getX(i),p.getY(i),p.getZ(i)));
              const base=corner(0),right=corner(1).sub(base),up=corner(3).sub(base),q=[];
              for(const px of [xa,xb+1])for(const py of [ya,yb+1]){
                const z=base.clone().addScaledVector(right,px/w).addScaledVector(up,1-py/h);q.push(v.worldToScreen(z.x,z.y,z.z));
              }
              const sx=q.map(p=>p.x),sy=q.map(p=>p.y);
              return {minX:Math.min(...sx),maxX:Math.max(...sx),minY:Math.min(...sy),maxY:Math.max(...sy),height:Math.max(...sy)-Math.min(...sy),alphaThreshold:16};
            }''')
            nearby=sorted(doors,key=lambda a:sum((sum(v[i] for v in a['vertices'])/len(a['vertices'])-[x,y][i])**2 for i in (0,1)))[:8]
            record['projectedNearbyDoors'] = page.evaluate('''doors=>doors.map(d=>{
              const q=d.vertices.map(p=>AstraeonSpatialView.worldToScreen(...p)),xs=q.map(p=>p.x),ys=q.map(p=>p.y);
              const zs=d.vertices.map(v=>v[2]),low=Math.min(...zs),high=Math.max(...zs),edges=[];
              d.vertices.forEach((v,i)=>{if(Math.abs(v[2]-low)>.0001)return;
                const j=d.vertices.findIndex(w=>Math.abs(w[2]-high)<.0001&&Math.hypot(w[0]-v[0],w[1]-v[1])<.0001);
                if(j>=0)edges.push(Math.hypot(q[j].x-q[i].x,q[j].y-q[i].y));});
              return {owner:d.owner,minX:Math.min(...xs),maxX:Math.max(...xs),minY:Math.min(...ys),maxY:Math.max(...ys),height:Math.max(...ys)-Math.min(...ys),verticalEdgeHeights:edges,meanVerticalEdgeHeight:edges.length?edges.reduce((a,b)=>a+b)/edges.length:null};
            })''',nearby)
            if scene_image:record['sceneImage']=str(scene_image)
            if culling is not None: record['cullingVerification'] = culling
            records.append(record)
            (output / 'views.json').write_text(json.dumps(records, indent=2) + '\n')
            print(json.dumps(record), flush=True)
            page.close()
            assert not errors, (name, 'Browser errors during native capture', errors)
        browser.close()
    (output / 'views.json').write_text(json.dumps(records, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8011/?qa=1')
    parser.add_argument('--output', type=Path, default=Path('/tmp/wayfarer-golden-views'))
    parser.add_argument('--views', default=','.join(VIEWS))
    parser.add_argument('--zoom', type=float, help='Use ordinary Ctrl-right-drag zoom for a still review (65–325)')
    parser.add_argument('--yaw',type=float,help='Absolute ordinary right-drag orbit; omit to keep the gameplay default')
    parser.add_argument('--pitch',type=float,help='Absolute ordinary Shift-right-drag pitch; omit to keep the gameplay default')
    parser.add_argument('--capture-scale', type=float,
                        help='Still-image pixel ratio, independent of the runtime performance policy')
    parser.add_argument('--startup-timeout-ms', type=int, default=120000,
                        help='Bounded browser startup deadline; capture quality is unchanged')
    parser.add_argument('--verify-culling', action='store_true',
                        help='Compare exact native frame pixels with/without static frustum culling')
    parser.add_argument('--append', action='store_true', help='Append captures to an existing review manifest')
    parser.add_argument('--template-file', type=Path, help='Reuse an ordinary-UI character save for visual fixtures only')
    parser.add_argument('--width', type=int, default=1280, help='Viewport width; standard comparison remains 1280')
    parser.add_argument('--height', type=int, default=800, help='Viewport height; use910×512 to compare the supplied beta frames')
    parser.add_argument('--scene-only', action='store_true', help='Also save the native WebGL frame without DOM HUD panels')
    args = parser.parse_args()
    names = args.views.split(',')
    if any(name not in VIEWS for name in names):
        parser.error('Unknown view; choose from ' + ', '.join(VIEWS))
    if args.zoom is not None and not 65<=args.zoom<=325:parser.error('Zoom must be within classic RO limits, 65–325')
    if args.pitch is not None and not 10<=args.pitch<=89:parser.error('Pitch must be within gameplay limits, 10–89')
    if args.capture_scale is not None and not .5<=args.capture_scale<=3:parser.error('Capture scale must be within .5–3')
    if args.width<360 or args.height<360:parser.error('Viewport dimensions must be at least360 pixels')
    capture(args.url, args.output, names,args.zoom,args.yaw,args.pitch,args.capture_scale,args.startup_timeout_ms,args.verify_culling,args.append,args.template_file,args.width,args.scene_only,args.height)
