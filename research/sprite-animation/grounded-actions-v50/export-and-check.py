"""Capture actual WebGL pixels, inspect triangles and drive both players."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,hashlib,base64,importlib.util
from PIL import Image,ImageDraw
import numpy as np
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent;root=P.parents[2]
spec=importlib.util.spec_from_file_location('contact',P/'inputs/sprite-contact-review.py');observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P.parent)));threading.Thread(target=server.serve_forever,daemon=True).start();checks={};errors=[];geometry={};case_reports={};d=json.loads((P/'mesh-contract.json').read_text())
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);page=b.new_page(viewport={'width':1100,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/{P.name}/review.html');page.wait_for_function('window.READY===true');out=P/'renders';out.mkdir(exist_ok=True)
 raw=page.evaluate("()=>{study.mesh.draw({});return document.getElementById('sprite').toDataURL('image/png')}");(out/'rest.png').write_bytes(base64.b64decode(raw.split(',')[1]));rest=np.asarray(Image.open(out/'rest.png'))
 for name,clip in d['clips'].items():
  directory=out/name;directory.mkdir(exist_ok=True);frames=[];images=[]
  for i in range(16):
   data=page.evaluate('([c,i])=>study.frame(c,i)',[name,i]);f=directory/f'{i:02}.png';f.write_bytes(base64.b64decode(data.split(',')[1]));frames.append({'path':str(f.relative_to(P)),'sha256':observer.sha(f)});im=Image.open(f).convert('RGBA');images.append(im)
   # Bottom region is untouched by a common mesh across all frames, not patched.
   assert np.array_equal(np.asarray(im)[448:,:,:],rest[448:,:,:])
  checks[name+'_distal_pixels_identical_to_actual_rest_render']=True
  unique=len(set(x['sha256'] for x in frames));assert unique>=8;checks[name+'_sixteen_samples_with_measured_unique_'+str(unique)]=True
  contract={'frames':frames,'calibration_output_frames':[],'surfaces':{n:{'window':box,'planted_frames':list(range(16)),'budget_px':{'x':6,'y':6}} for n,box in [('screen_left',[150,450,224,500]),('screen_right',[224,450,294,500])]}}
  (P/(name+'-contact-case.json')).write_text(json.dumps(contract,indent=2)+'\n');r=observer.evaluate(contract,P);assert r['visible_surface_contact_pass'];case_reports[name]=r
  (P/(name+'-contact-review.json')).write_text(json.dumps(r,indent=2)+'\n')
  geo=page.evaluate('''name=>{const m=study.mesh,poses=study.data.clips[name].poses;let min=Infinity,max=0,feet=0,head=0;
  for(let k=0;k<241;k++){let t=k/240*15,i=Math.min(14,Math.floor(t)),f=t-i,pose={};for(const key of Object.keys(poses[0]))pose[key]=poses[i][key].map((v,j)=>v*(1-f)+poses[i+1][key][j]*f);let v=m.draw(pose);
  for(let j=0;j<v.length;j++){const a=m.rest[j],q=v[j];if(a[1]>=432)feet=Math.max(feet,Math.hypot(q[0]-a[0],q[1]-a[1]));if(a[1]<=192)head=Math.max(head,Math.hypot(q[0]-a[0]-pose.head[0],q[1]-a[1]-pose.head[1]));}
  const area=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);for(let j=0;j<v.length;j+=3){let ratio=area(v[j],v[j+1],v[j+2])/area(m.rest[j],m.rest[j+1],m.rest[j+2]);min=Math.min(min,ratio);max=Math.max(max,ratio);}}
  return{samples:241,min_triangle_area_ratio:min,max_triangle_area_ratio:max,max_fixed_distal_vertex_error_px:feet,max_head_rigid_translation_error_px:head};}''',name)
  assert geo['min_triangle_area_ratio']>.6 and geo['max_triangle_area_ratio']<1.4 and geo['max_fixed_distal_vertex_error_px']==0 and geo['max_head_rigid_translation_error_px']<1e-10;geometry[name]=geo
  checks[name+'_dense_no_fold_and_rigid_head_fixed_support']=True
  bg=[]
  for im in images:
   canvas=Image.new('RGBA',im.size,(40,43,48,255));canvas.alpha_composite(im);bg.append(canvas.convert('RGB'))
  bg[0].save(P/(name+'-16.gif'),save_all=True,append_images=bg[1:],duration=clip['durations'],loop=0)
  gif=Image.open(P/(name+'-16.gif'));encoded=[]
  for gi in range(gif.n_frames):gif.seek(gi);encoded.append(gif.info['duration'])
  assert sum(encoded)==sum(clip['durations']);checks[name+'_encoded_gif_clock_matches_player_total']=True
  board=Image.new('RGB',(1536,560),(40,43,48));draw=ImageDraw.Draw(board)
  for i,im in enumerate(images):im=im.resize((192,256));board.paste(im,(i%8*192,i//8*280+20),im);draw.text((i%8*192+4,i//8*280+3),str(i+1),(230,230,230))
  board.save(P/(name+'-sixteen.png'))
  page.locator('#clip').select_option(name)
  for i in range(16):page.evaluate('i=>study.select(i)',i);assert page.locator('#frame').input_value()==str(i)
  page.locator('#loop').uncheck()
  for speed in ['1','0.25']:
   page.locator('#speed').select_option(speed);page.locator('#play').click();page.wait_for_function('study.clock.finished',timeout=10000);assert page.locator('#frame').input_value()=='15'
  checks[name+'_actual_controls_all_frames_and_both_rates']=True
  page.locator('#loop').check();page.locator('#speed').select_option('1');page.locator('#play').click();page.wait_for_function('study.clock.iteration>=1',timeout=4000);page.locator('#play').click();snapshot=page.evaluate('study.clock.sample()');page.wait_for_timeout(80);assert snapshot==page.evaluate('study.clock.sample()');checks[name+'_loop_pause']=True
 page.evaluate("study.choose('hit.light');study.select(7)");page.screenshot(path=str(P/'verified-player.png'),full_page=True);assert not errors;b.close()
server.shutdown();server.server_close();checks['no_browser_errors']=True
(P/'mesh-qa.json').write_text(json.dumps({'pass':True,'checks':checks,'dense_geometry':geometry,'errors':errors,'scope':'Two small-motion N texture clips. No out-of-plane, hidden anatomy, seated pose, head swaps or universal production approval.'},indent=2)+'\n');print(json.dumps({'checks':checks,'geometry':geometry}))
