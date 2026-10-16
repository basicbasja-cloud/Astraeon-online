"""Geometry-only static binding search. Never inspect/fits rendered frame images."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from playwright.sync_api import sync_playwright
import threading,json,sys
P=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));threading.Thread(target=s.serve_forever,daemon=True).start();existing=P/'leg-binding-search.json';results=json.loads(existing.read_text())['results'] if existing.exists() else {}
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page();p.goto(f'http://127.0.0.1:{s.server_port}/fight-review.html');p.wait_for_function('window.READY');
 for ci,v in enumerate(['S','W','N','E']):
  p.evaluate('i=>study.choose(i*2)',ci)
  for side in ['left','right']:
   if len(sys.argv)>1 and v+'-'+side not in sys.argv[1:]:continue
   r=p.evaluate('''side=>{const m=study.layers.get(side+'_leg'),d=m.definition,poses=study.data.clips.filter(c=>c.view===study.data.clips[study.index].view).flatMap(c=>c.poses),[h,k,a,t]=d.nodes,ky=d.rest[k][1],end=d.bands[3],out=[];function area(a,b,c){return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])}for(const upper of [8,16,24,32,40,48,56,64,80])for(const lower of [2,4,8,12,16,20,24,32])for(const width of [16,20,24,28,32,40,48,56,64]){const bands=[ky-upper,ky+lower,end-width,end];if(bands.some((v,i)=>i&&v<=bands[i-1]))continue;let min=Infinity;for(const pose of poses){for(let i=0;i<m.rest.length;i+=3){const r=m.rest.slice(i,i+3),z=r.map(([x,y])=>{const u=1-m.smooth(bands[0],bands[1],y),v=m.smooth(bands[2],bands[3],y),A=m.mapBone([x,y],h,k,pose),B=m.mapBone([x,y],k,a,pose),C=[x+pose[a][0],y+pose[a][1]];return[A[0]*u+B[0]*(1-u)*(1-v)+C[0]*(1-u)*v,A[1]*u+B[1]*(1-u)*(1-v)+C[1]*(1-u)*v]});min=Math.min(min,area(...z)/area(...r));if(min<.15)break}if(min<.15)break}out.push({bands,min})}return out.sort((a,b)=>b.min-a.min)}''',side);results[v+'-'+side]=r;print(v,side,r[0],flush=True)
 b.close()
s.shutdown();(P/'leg-binding-search.json').write_text(json.dumps({'method':'Static rest-weight parameter search against source-driven geometry only; old retained alpha cells sampled. Selected binding must pass a fresh actual mesh export. No frame-image fitting.','results':results},indent=2)+'\n')
