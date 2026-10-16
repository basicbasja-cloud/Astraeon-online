"""Actual browser render, player and geometry checks for a declared pickup contract."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from playwright.sync_api import sync_playwright
from PIL import Image
import json,threading,base64,io,hashlib,sys,numpy as np
P=Path(__file__).resolve().parent;name=sys.argv[1];checks={};errors=[];measurements=[]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));threading.Thread(target=s.serve_forever,daemon=True).start()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto(f'http://127.0.0.1:{s.server_port}/{name}-articulated-review.html');p.wait_for_function('window.READY===true||!!window.LOAD_ERROR');assert p.evaluate('window.READY');d=p.evaluate('study.data');frames=json.loads((P/f'{name}-articulated-export.json').read_text())['frames']
 for i,f in enumerate(frames):
  p.locator('#frame').evaluate('(e,i)=>{e.value=i;e.dispatchEvent(new Event("input"))}',i);assert p.evaluate('study.clock.time')==sum(d['durations_ms'][:i])
  data=p.evaluate("document.getElementById('c').toDataURL()");actual=np.array(Image.open(io.BytesIO(base64.b64decode(data.split(',')[1]))));saved=P/f['path'];assert hashlib.sha256(saved.read_bytes()).hexdigest()==f['sha256'];assert np.array_equal(actual,np.array(Image.open(saved)))
  a=actual[:,:,3]>=128;assert not(a[0].any()or a[-1].any()or a[:,0].any()or a[:,-1].any())
  geo=p.evaluate('''()=>{let out={};const pose=study.data.poses[+document.getElementById('frame').value],active=study.data.order.map(n=>n==='head'&&pose.head_card?.[0]?'head'+pose.head_card[0]:n==='scarf0'?'scarf'+(pose.head_card?.[0]||0):n);for(const n of active){const m=study.layers.get(n);if(m.segmentRest){out[n]={};for(const k of ['upper','lower','distal']){m.segment=k;out[n][k]={rest:m.segmentRest[k],next:m.segmentRest[k].map(([x,y])=>m.point(x,y,study.data.poses[+document.getElementById('frame').value]))}}}else out[n]={whole:{rest:m.rest,next:m.vertices,plane:m.definition.front_plane||null}}}return out}''')
  for layer,parts in geo.items():
   for part,g in parts.items():
    r=np.array(g['rest']).reshape(-1,3,2);v=np.array(g['next']).reshape(-1,3,2)
    def area(x):return (x[:,1,0]-x[:,0,0])*(x[:,2,1]-x[:,0,1])-(x[:,1,1]-x[:,0,1])*(x[:,2,0]-x[:,0,0])
    ratios=area(v)/area(r);measurements.append({'frame':i,'layer':layer,'part':part,'min_triangle_area_ratio':float(ratios.min()),'max_triangle_area_ratio':float(ratios.max()),'source_projected_torso_plane':g.get('plane')=='torso'})
 checks['all16_controls_clock_pixel_equivalence_and_no_clipping']=True
 for speed in ['1','0.25']:
  p.evaluate('study.select(0);study.clock.clip.loop=false');p.locator('#speed').select_option(speed);p.locator('#play').click();p.wait_for_function('study.clock.finished',timeout=15000);assert p.locator('#frame').input_value()=='15';checks['actual_one_shot_'+speed]=True
 p.locator('#speed').select_option('1');p.evaluate('study.select(0);study.clock.clip.loop=true');p.locator('#play').click();p.wait_for_function('study.clock.iteration>=1',timeout=6000);p.locator('#play').click();state=p.evaluate('study.clock.sample()');pixels=p.evaluate("document.getElementById('c').toDataURL()");p.wait_for_timeout(100);assert state==p.evaluate('study.clock.sample()') and pixels==p.evaluate("document.getElementById('c').toDataURL()");checks['loop_and_pause_freeze_pixels_clock']=True
 p.evaluate('study.select(7)');x=p.locator('#play').evaluate('(e)=>{const t=study.clock.time;e.click();return t===study.clock.time&&study.clock.running}');assert x;checks['resume_retains_selected_phase']=True;p.locator('#play').click();assert not errors;b.close()
s.shutdown();s.server_close();checks['all_positive_geometry']=min(x['min_triangle_area_ratio'] for x in measurements)>0
checks['minimum_skinning_geometry_ratio_015']=min(x['min_triangle_area_ratio'] for x in measurements if not x['source_projected_torso_plane'])>.15
planes=[x for x in measurements if x['source_projected_torso_plane']]
checks['rigid_source_plane_projection_matches_actual_source']=True
if planes:
 source=P/'source/controlled-retiming-v1.json';assert hashlib.sha256(source.read_bytes()).hexdigest()==d['source_sha256'];source=json.loads(source.read_text())['views'][d['view']]['frames'];t=source[0]['source_bones']['torso'];dy0=t['tail']['xy'][1]-t['head']['xy'][1]
 for x in planes:
  t=source[x['frame']]['source_bones']['torso'];ratio=(t['tail']['xy'][1]-t['head']['xy'][1])/dy0;checks['rigid_source_plane_projection_matches_actual_source'] &= bool(ratio>0 and abs(x['min_triangle_area_ratio']-ratio)<1e-8 and abs(x['max_triangle_area_ratio']-ratio)<1e-8)
r={'pass':all(checks.values()),'checks':checks,'geometry':measurements,'page_errors':errors,'production_pass':False,'scope':'Bounded actual16-frame renderer/player. No game integration or hidden anatomy approval.'};(P/f'{name}-player-qa.json').write_text(json.dumps(r,indent=2)+'\n');print({'pass':r['pass'],'checks':checks,'min_ratio':min(x['min_triangle_area_ratio'] for x in measurements)});raise SystemExit(not r['pass'])
