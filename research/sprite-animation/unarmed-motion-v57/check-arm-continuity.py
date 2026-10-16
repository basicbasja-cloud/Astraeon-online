"""Actual isolated GPU arm continuity. Detects detached sleeves/armor/fists."""
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from functools import partial
from playwright.sync_api import sync_playwright
from PIL import Image
from scipy.ndimage import label
import json,threading,base64,hashlib,numpy as np
P=Path(__file__).resolve().parent
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
s=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(P)));threading.Thread(target=s.serve_forever,daemon=True).start();out=[]
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-unsafe-swiftshader']);p=b.new_page();p.goto(f'http://127.0.0.1:{s.server_port}/fight-review.html');p.wait_for_function('window.READY');D=p.evaluate('study.data')
 for ci,c in enumerate(D['clips']):
  p.evaluate('i=>study.choose(i)',ci);bad=[];frames=[]
  for i in range(len(c['poses'])):
   for side in ['left','right']:
    raw=p.evaluate("([i,s])=>study.layers.get(s+'_arm').drawPieces(study.data.clips[study.index].poses[i]).canvas.toDataURL('image/png')",[i,side]);f=P/'diagnostics/arm-continuity'/c['action']/c['view']/f'{side}-{i:02}.png';f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(base64.b64decode(raw.split(',')[1]));a=np.array(Image.open(f).convert('RGBA'))[:,:,3]>=128;lab,n=label(a,np.ones((3,3)));counts=sorted(np.bincount(lab.ravel())[1:].tolist(),reverse=True);significant=[v for v in counts if v>=24];row={'frame':i,'side':side,'path':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'component_sizes_px':counts[:10],'significant_components':len(significant),'pass':len(significant)==1};frames.append(row)
    if not row['pass']:bad.append([i,side,counts[:5]])
  print(c['action'],c['view'],'BAD',bad[:12],flush=True);out.append({'action':c['action'],'view':c['view'],'frames':frames,'pass':not bad})
 b.close()
s.shutdown();r={'pass':all(c['pass']for c in out),'source_contract_sha256':hashlib.sha256((P/'fight-rig-contract.json').read_bytes()).hexdigest(),'alpha_threshold':128,'minimum_significant_component_px':24,'clips':out,'scope':'Actual isolated full arms must retain one connected substantial silhouette; small antialias specks ignored. Does not detect anatomical correctness or full-scene occlusion.'};(P/'arm-continuity-review.json').write_text(json.dumps(r,indent=2)+'\n')
