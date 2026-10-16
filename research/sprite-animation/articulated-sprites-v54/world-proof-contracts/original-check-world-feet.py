"""Actual GPU distal-art pixels in world space, with bad-clock and held-pose controls."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
import threading,json,hashlib,base64,math,io,sys
from PIL import Image
import numpy as np
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent;view=sys.argv[1] if len(sys.argv)>1 else 'W';prefix='' if view=='W' else view+'-'
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P.parent)));threading.Thread(target=s.serve_forever,daemon=True).start();out={};errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto(f'http://127.0.0.1:{s.server_port}/{P.name}/{prefix}walk-review.html');p.wait_for_function('window.READY===true');data=p.evaluate('study.data');spatial={k:data[k] for k in ['definitions','poses','world_offsets','source_sha256']};binding=hashlib.sha256(json.dumps(spatial,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for label,count,gain in [('continuous',0,1),('wrong_root_speed',0,1.25),('held16',16,1),('held20',20,1),('held40',40,1),('held80',80,1)]:
  groups={};frames=[];dst=P/(prefix+'world-foot-renders')/label;dst.mkdir(parents=True,exist_ok=True)
  for side,offset in [('left',0),('right',.5)]:
   for i in range(241):
    t=i/240;phase=(t+offset)%1
    if phase>=.6:continue
    raw=p.evaluate('a=>study.footFrame(...a)',[side+'_leg',t,count,gain]);f=dst/f'{side}-{i:03}.png';f.write_bytes(base64.b64decode(raw.split(',')[1]));a=np.array(Image.open(f));y,x=np.where(a[:,:,3]>=128);assert len(x)>0;box=[int(x.min()),int(y.min()),int(x.max()),int(y.max())];g=f'{side}-stance{math.floor(t+offset)}';groups.setdefault(g,[]).append(box);frames.append({'phase':t,'side':side,'stance_group':g,'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'distal_alpha128_bbox':box})
  ranges={n:np.ptp(np.array(v),axis=0).tolist() for n,v in groups.items() if len(v)>=3};passed=all(max(v)<=2 for v in ranges.values());out[label]={'pass':passed,'maximum_bbox_ranges_px':ranges,'frames':frames,'explanation':'Actual lower-boot UV diagnostic through the same rest skin, projected source delta and world root. Mask is diagnostic only, not a patched final foot. Hidden/occluded fullscene contact is a separate image review.'};print(label,passed,ranges,flush=True)
 assert not errors;b.close()
s.shutdown();s.server_close();(P/(prefix+'world-foot-qa.json')).write_text(json.dumps({'results':out,'spatial_binding_sha256':binding,'production_baked_durations_ms':data['durations_ms'],'budget_px':2,'sample_times':241,'page_errors':errors,'scope':'Actual raster world registration of isolated distal boot art during declared stance intervals; not hidden anatomical detection or universal game integration'},indent=2)+'\n')
assert out['continuous']['pass'] and out['held80']['pass'];assert not out['wrong_root_speed']['pass'] and not out['held16']['pass']
# Held40 is a measured comparison, not a universal negative: its projected travel can pass in diagonal views.
