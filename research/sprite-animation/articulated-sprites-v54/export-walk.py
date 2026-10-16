"""Actual layered pixel export and independent dense geometry/clock inspection."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,base64,hashlib,sys
from PIL import Image,ImageDraw
import numpy as np
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent;view=sys.argv[1] if len(sys.argv)>1 else 'W';prefix='' if view=='W' else view+'-'
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P.parent)));threading.Thread(target=server.serve_forever,daemon=True).start();errors=[];results={};ims=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);page=b.new_page(viewport={'width':1100,'height':850});page.on('pageerror',lambda e:errors.append(str(e)));page.goto(f'http://127.0.0.1:{server.server_port}/{P.name}/{prefix}walk-review.html');page.wait_for_function('window.READY===true',timeout=30000);(P/'walk'/view).mkdir(parents=True,exist_ok=True);frames=[];data=page.evaluate('study.data');count=len(data['durations_ms'])
 for i in range(count):
  raw=page.evaluate('i=>study.frame(i)',i);im=Image.open(__import__('io').BytesIO(base64.b64decode(raw.split(',')[1]))).copy();f=P/'walk'/view/f'{i:02}.png';im.save(f);frames.append({'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()});ims.append(im.copy())
 geo=page.evaluate('''()=>{const area=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]),out={};for(const [name,m]of study.layers){let min=Infinity,max=0,rigid=0;for(let k=0;k<=256;k++){let p=study.poseAt(k/256),v=m.draw(p);for(let j=0;j<v.length;j+=3){let ratio=area(v[j],v[j+1],v[j+2])/area(m.rest[j],m.rest[j+1],m.rest[j+2]);min=Math.min(min,ratio);max=Math.max(max,ratio)}for(let j=0;j<v.length;j++){let r=m.rest[j],q=v[j];if(name==='head')rigid=Math.max(rigid,Math.hypot(q[0]-r[0]-p.head[0],q[1]-r[1]-p.head[1]));if(name.endsWith('_leg')&&r[1]>=m.definition.bands[3]){let a=p[m.definition.nodes[2]];rigid=Math.max(rigid,Math.hypot(q[0]-r[0]-a[0],q[1]-r[1]-a[1]));}}}out[name]={samples:257,active_triangle_count:m.rest.length/3,min_triangle_area_ratio:min,max_triangle_area_ratio:max,max_rigid_distal_or_head_error_px:rigid}}return out}''')
 results['dense_geometry']=geo; (P/(prefix+'walk-geometry-current.json')).write_text(json.dumps(geo,indent=2)+'\n')
 for name,r in geo.items():assert r['min_triangle_area_ratio']>.15,(name,r)
 for name in ['head','left_leg','right_leg']:assert geo[name]['max_rigid_distal_or_head_error_px']<1e-8
 page.evaluate('study.select(5)');page.screenshot(path=str(P/(prefix+'walk-browser.png')),full_page=True);assert not errors;b.close()
server.shutdown();server.server_close();board=Image.new('RGB',(2048,((count+7)//8)*308),(40,43,48));d=ImageDraw.Draw(board);gif=[]
for i,im in enumerate(ims):
 th=im.resize((256,288));board.paste(th,(i%8*256,i//8*308+20),th);d.text((i%8*256+4,i//8*308+2),str(i+1),fill='white');bg=Image.new('RGBA',im.size,(40,43,48,255));bg.alpha_composite(im);gif.append(bg.convert('RGB'))
critical=Image.new('RGBA',(2048,576),(40,43,48,255))
for j,i in enumerate([0,count//4,count//2,count*3//4]):critical.alpha_composite(ims[i],(j*512,0))
critical.convert('RGB').save(P/('walk-critical-poses-'+view+'.png'));board.save(P/('walk-contact-sheet-'+view+'.png'));preview=gif[::2];preview[0].save(P/('walk-'+view+'.gif'),save_all=True,append_images=preview[1:],duration=[20]*len(preview),loop=0);encoded=Image.open(P/('walk-'+view+'.gif'));durations=[]
for i in range(encoded.n_frames):encoded.seek(i);durations.append(encoded.info['duration'])
assert sum(durations)==800;results.update({'rig_contract_sha256':hashlib.sha256((P/(prefix+'walk-rig-contract.json')).read_bytes()).hexdigest(),'renderer_sha256':hashlib.sha256((P/'inputs/sprite-articulated-player.js').read_bytes()).hexdigest(),'view':view,'frames':frames,'page_errors':errors,'preview_gif_clock_ms':durations,'preview_gif_exposures':len(preview),'baked_png_durations_ms':data['durations_ms'],'preview_scope':'GIF uses every second80-sample frame at20ms to preserve800ms playback on browser GIF decoders; authoritative80PNG/10ms timeline and continuous rig are separate' ,'unique_rasters':len(set(f['sha256'] for f in frames)),'geometry_checks_pass':True,'manual_image_contact_and_playback_review_required':True,'production_pass':False});(P/(prefix+'walk-geometry-qa.json')).write_text(json.dumps(results,indent=2)+'\n');print(geo)
