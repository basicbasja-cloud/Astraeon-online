"""Capture actual candidate WebGL buffers and all triangle geometry; never grant art approval."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from playwright.sync_api import sync_playwright
from PIL import Image,ImageDraw
import json,threading,base64,io,hashlib,numpy as np
P=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));threading.Thread(target=s.serve_forever,daemon=True).start();results=[];errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto(f'http://127.0.0.1:{s.server_port}/fight-review.html');p.wait_for_function('window.READY===true||!!window.LOAD_ERROR');assert p.evaluate('window.READY'),p.evaluate('window.LOAD_ERROR');data=p.evaluate('study.data')
 for j,d in enumerate(data['clips']):
  p.evaluate('i=>study.choose(i)',j);folder=P/'renders'/d['action']/d['view'];folder.mkdir(parents=True,exist_ok=True);frames=[];geometry=[];images=[]
  for i in range(len(d['poses'])):
   raw=p.evaluate('i=>study.frame(i)',i);f=folder/f'{i:02}.png';f.write_bytes(base64.b64decode(raw.split(',')[1]));im=Image.open(f).convert('RGBA');images.append(im.copy());a=np.array(im)[:,:,3]>=128;cut=bool(a[0].any()or a[-1].any()or a[:,0].any()or a[:,-1].any());frames.append({'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'canvas_cut':cut})
   g=p.evaluate('''i=>{const pose=study.data.clips[study.index].poses[i],out=[];function area(a,b,c){return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])}for(const[n,m]of study.layers){const parts=m.segmentRest?Object.keys(m.segmentRest):['whole'];for(const part of parts){if(m.segmentRest)m.segment=part;const r=m.segmentRest?m.segmentRest[part]:m.rest;if(!r.length)continue;let lo=Infinity,hi=-Infinity;for(let k=0;k<r.length;k+=3){const a=r.slice(k,k+3),b=a.map(([x,y])=>m.point(x,y,pose)),ratio=area(...b)/area(...a);lo=Math.min(lo,ratio);hi=Math.max(hi,ratio)}out.push({frame:i,layer:n,part,min_area_ratio:lo,max_area_ratio:hi})}}return out}''',i);geometry.extend(g)
  cols=4;board=Image.new('RGBA',(2048,((len(images)+cols-1)//cols)*600),(40,43,48,255));draw=ImageDraw.Draw(board)
  for i,im in enumerate(images):board.alpha_composite(im,(i%cols*512,i//cols*600+24));draw.text((i%cols*512+8,i//cols*600+4),f"{d['action']} {d['view']} {i}",fill='white')
  board.convert('RGB').save(P/f"{d['action']}-{d['view']}-all.png");critical=Image.new('RGBA',(2048,576),(40,43,48,255));ids=[0,len(images)//3,len(images)//2,len(images)-1]
  for k,i in enumerate(ids):critical.alpha_composite(images[i],(k*512,0))
  critical.convert('RGB').save(P/f"{d['action']}-{d['view']}-critical.png");r={'action':d['action'],'view':d['view'],'frames':frames,'durations_ms':d['durations_ms'],'geometry':geometry,'geometry_min_ratio':min(v['min_area_ratio'] for v in geometry),'unclipped':not any(f['canvas_cut'] for f in frames),'production_pass':False};results.append(r);print({k:r[k] for k in ['action','view','geometry_min_ratio','unclipped']},flush=True)
 assert not errors;b.close()
s.shutdown();s.server_close();(P/'fight-export-review.json').write_text(json.dumps({'clips':results,'page_errors':errors,'production_pass':False},indent=2)+'\n')
