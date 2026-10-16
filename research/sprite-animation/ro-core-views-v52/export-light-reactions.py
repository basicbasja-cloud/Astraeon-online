from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,base64,hashlib
from PIL import Image,ImageDraw
import numpy as np
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));threading.Thread(target=server.serve_forever,daemon=True).start();results={};errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);page=b.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/light-reaction-review.html');page.wait_for_function('window.READY===true');D=page.evaluate('study.data')
 for view,a in D['views'].items():
  page.evaluate('v=>study.choose(v)',view);dst=P/'light-reactions'/view;dst.mkdir(parents=True,exist_ok=True);frames=[];ims=[];rest=None
  for i in range(16):
   data=page.evaluate('([v,i])=>study.frame(v,i)',[view,i]);f=dst/f'{i:02}.png';f.write_bytes(base64.b64decode(data.split(',')[1]));im=Image.open(f);pixels=np.asarray(im)
   if rest is None:rest=pixels.copy()
   assert np.array_equal(pixels[448:],rest[448:]);frames.append({'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()});ims.append(im.copy())
  assert (dst/'00.png').read_bytes()==(dst/'15.png').read_bytes()
  geo=page.evaluate('''v=>{const m=study.mesh,ps=study.data.views[v].poses;let min=Infinity,max=0,fixed=0,head=0;const area=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);for(let k=0;k<=240;k++){let t=k/240*15,i=Math.min(14,Math.floor(t)),f=t-i,p={};for(let key of Object.keys(ps[0]))p[key]=ps[i][key].map((x,j)=>x*(1-f)+ps[i+1][key][j]*f);let a=m.draw(p);for(let j=0;j<a.length;j++){let r=m.rest[j],q=a[j];if(r[1]>=432)fixed=Math.max(fixed,Math.hypot(q[0]-r[0],q[1]-r[1]));if(r[1]<=212)head=Math.max(head,Math.hypot(q[0]-r[0]-p.head[0],q[1]-r[1]-p.head[1]));}for(let j=0;j<a.length;j+=3){let r=area(a[j],a[j+1],a[j+2])/area(m.rest[j],m.rest[j+1],m.rest[j+2]);min=Math.min(min,r);max=Math.max(max,r)}}return{samples:241,min_triangle_area_ratio:min,max_triangle_area_ratio:max,max_fixed_distal_vertex_error:fixed,max_head_rigid_translation_error:head}}''',view)
  assert geo['min_triangle_area_ratio']>.6 and geo['max_triangle_area_ratio']<1.4 and geo['max_fixed_distal_vertex_error']==0 and geo['max_head_rigid_translation_error']<1e-10
  board=Image.new('RGB',(2048,560),(40,43,48));draw=ImageDraw.Draw(board);gif=[]
  for i,im in enumerate(ims):
   th=im.resize((256,256));board.paste(th,(i%8*256,i//8*280+20),th);draw.text((i%8*256+3,i//8*280+2),str(i+1),fill='white');bg=Image.new('RGBA',im.size,(40,43,48,255));bg.alpha_composite(im);gif.append(bg.convert('RGB'))
  board.save(dst/'sixteen.png');gif[0].save(dst/'preview.gif',save_all=True,append_images=gif[1:],duration=a['durations_ms'],loop=0);encoded=Image.open(dst/'preview.gif');clock=[]
  for i in range(encoded.n_frames):encoded.seek(i);clock.append(encoded.info['duration'])
  assert sum(clock)==670;results[view]={'frames':frames,'durations_ms':a['durations_ms'],'unique_rasters':len(set(f['sha256'] for f in frames)),'dense_geometry':geo,'distal_pixels_identical':True,'closed_neutral_exact':True,'encoded_clock_ms':sum(clock)}
 assert not errors;b.close()
server.shutdown();server.server_close();(P/'light-reaction-qa.json').write_text(json.dumps({'bounded_checks_pass':True,'views':results,'page_errors':errors,'manual_image_review_required':True},indent=2)+'\n');print({v:r['dense_geometry'] for v,r in results.items()})
