"""Preview only: one actor-only rest calibration, no per-pose/view fitting."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,base64
import numpy as np
P=Path(__file__).resolve().parent;r=json.loads((P/'receipt.json').read_text());views=list(r['frames'][0]['views']);ref=P.parent/'recovery-key-v39/renders/review/full/00.png'
raw=Image.open(P/'renders/key/S/00.png').convert('RGBA');ids=np.asarray(Image.open(P/'renders/ownership/S/00.png').convert('RGBA'));a=np.asarray(raw);actor=(a[:,:,3]>=128)&~((ids[:,:,0]>200)&(ids[:,:,1]<35)&(ids[:,:,2]<35));ys,xs=np.where(actor);bbox=[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())];height=bbox[3]-bbox[1]+1;scale=399/height;tx=224.5-scale*(bbox[0]+bbox[2])/2;ty=480-scale*bbox[3];inv=(1/scale,0,-tx/scale,0,1/scale,-ty/scale)
mat=dict(matrix=[scale,0,0,scale,tx,ty],calibration='Actor-only S neutral; red collectible excluded using actual depth-tested ID capture; 399px height, floor480, horizontal center224.5. All views and phases share exactly this matrix; not a matching-view family-proportion approval.',bbox_raw=bbox,reference_sha256=hashlib.sha256(ref.read_bytes()).hexdigest(),production_pass=False);(P/'display-bind.json').write_text(json.dumps(mat,indent=2)+'\n')
preview={};BG=(36,40,47,255)
for bank,n in [('key',8),('dense',27),('ownership',8)]:
 for view in views:
  folder=P/'review'/bank/view;folder.mkdir(parents=True,exist_ok=True);ims=[]
  for i in range(n):
   src=P/f'renders/{bank}/{view}/{i:02}.png';im=Image.open(src).convert('RGBA').transform((384,512),Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC);im.save(folder/f'{i:02}.png');preview[f'{bank}/{view}/{i}']=dict(path=str((folder/f'{i:02}.png').relative_to(P)),sha256=hashlib.sha256((folder/f'{i:02}.png').read_bytes()).hexdigest());bg=Image.new('RGBA',im.size,BG);bg.alpha_composite(im);ims.append(bg.convert('RGB'))
  if bank!='ownership':
   durations=[190,180,190,180,190,180,190,600] if bank=='key' else [50]*26+[600];ims[0].save(folder/'motion.gif',save_all=True,append_images=ims[1:],duration=durations,loop=0,disposal=2)
for bank,n in [('key',8),('dense',27)]:
 ims=[]
 for i in range(n):
  sheet=Image.new('RGBA',(768,512),BG);d=ImageDraw.Draw(sheet)
  for j,v in enumerate(views):
   im=Image.open(P/f'review/{bank}/{v}/{i:02}.png').resize((192,256),Image.Resampling.LANCZOS);sheet.alpha_composite(im,(j%4*192,j//4*256));d.text((j%4*192+6,j//4*256+6),v+' '+str(i+1),fill='white')
  ims.append(sheet.convert('RGB'))
 ims[0].save(P/f'eight-view-{bank}.gif',save_all=True,append_images=ims[1:],duration=[190,180,190,180,190,180,190,600] if bank=='key' else [50]*26+[600],loop=0,disposal=2)
# Actual approved drawing next to current original 3D blockout; no quality acceptance implied.
proof=Image.new('RGBA',(1152,512),BG);d=ImageDraw.Draw(proof);proof.alpha_composite(Image.open(ref).convert('RGBA'),(0,0));proof.alpha_composite(Image.open(P/'review/key/SW/00.png'),(384,0));proof.alpha_composite(Image.open(P/'review/key/NW/03.png'),(768,0));d.text((8,8),'EXACT USER-APPROVED v39 ART',fill='white');d.text((392,8),'LOCAL RIG BLOCKOUT / NOT FINAL ART',fill='white');d.text((776,8),'BACK REACH / SAME CHARACTER RIG',fill='white');proof.save(P/'approved-vs-local.png')
# Offline reviewer: synchronized actual images + source projections. Bones are source-only.
frames=[]
for fr in r['frames']:
 if fr['bank']!='dense':continue
 dic={}
 for v in views:
  f=P/f'review/dense/{v}/{fr["index"]:02}.png';dic[v]='data:image/png;base64,'+base64.b64encode(f.read_bytes()).decode()
 frames.append(dict(index=fr['index'],t=fr['t'],images=dic,projected=fr['projected_points']))
html='''<!doctype html><html lang="en"><meta charset="utf-8"><title>v44 Free local rig proof</title><style>body{background:#20252d;color:#eee;font:16px sans-serif;margin:20px}button,input{margin:8px}main{display:grid;grid-template-columns:repeat(4,minmax(160px,1fr));gap:8px}canvas{width:100%;background:#24282f}figure{margin:0}.warn{padding:12px;background:#563a18}label{white-space:nowrap}</style><h1>v44 — Free local rig proof</h1><p class="warn">LOCAL 3D BLOCKOUT — NOT approved painted sprites. No paid provider, upload, credits, or generation job. Same physical rig in eight real cameras. Complete-head/body-outfit authoring groups; runtime compositing/swaps not yet approved.</p><button id="play">Play once</button><button id="reset">Reset</button><label>Phase <input id="phase" type="range" min="0" max="26" value="0"></label><label><input id="grid" type="checkbox">20px grid</label><label><input id="bones" type="checkbox">Source joint projection (not image tracking)</label><span id="status"></span><main></main><p>Dense preview: 26 × 50ms intervals + 600ms final hold = 1900ms. GIF repeats for review; the action is pickup, not a walking loop. One neutral display calibration shared by the bank. More frames do not establish anatomy, contact or visual quality.</p><script>const DATA=__DATA__, VIEWS=__VIEWS__, M=__M__;let cache=[],phase=0,timer=null,loaded=0;const main=document.querySelector('main');for(const v of VIEWS){let f=document.createElement('figure');f.innerHTML='<figcaption>'+v+'</figcaption><canvas width="384" height="512" data-view="'+v+'"></canvas>';main.append(f)}const cvs=[...document.querySelectorAll('canvas')];function draw(){document.querySelector('#phase').value=phase;document.querySelector('#status').textContent='Frame '+(phase+1)+'/27';for(let j=0;j<8;j++){let c=cvs[j],x=c.getContext('2d');x.clearRect(0,0,384,512);x.drawImage(cache[phase][j],0,0);if(document.querySelector('#grid').checked){x.strokeStyle='#ffffff30';x.lineWidth=1;for(let p=0;p<512;p+=20){x.beginPath();x.moveTo(p,0);x.lineTo(p,512);x.stroke();x.beginPath();x.moveTo(0,p);x.lineTo(384,p);x.stroke()}}if(document.querySelector('#bones').checked){for(let side of ['left','right'])for(let chain of [['shoulder','elbow','wrist','palm','grip'],['hip','knee','ankle','toe']]){x.strokeStyle=side==='right'?'#1e8dff':'#ff8708';x.lineWidth=2;x.beginPath();for(let k=0;k<chain.length;k++){let a=DATA[phase].projected[VIEWS[j]][side+'.'+chain[k]],px=M[0]*a[0]+M[4],py=M[3]*a[1]+M[5];k?x.lineTo(px,py):x.moveTo(px,py)}x.stroke()}}}}function stop(){clearTimeout(timer);timer=null}function tick(){draw();if(phase<26)timer=setTimeout(()=>{phase++;tick()},50);else timer=setTimeout(stop,600)}document.querySelector('#play').onclick=()=>{stop();phase=0;tick()};document.querySelector('#reset').onclick=()=>{stop();phase=0;draw()};document.querySelector('#phase').oninput=e=>{stop();phase=+e.target.value;draw()};for(let s of ['grid','bones'])document.querySelector('#'+s).onchange=draw;window.READY=false;Promise.all(DATA.map(async f=>Promise.all(VIEWS.map(v=>new Promise((resolve,reject)=>{let i=new Image();i.onload=()=>resolve(i);i.onerror=reject;i.src=f.images[v]}))))).then(v=>{cache=v;window.READY=true;draw()});window.V44={setPhase(p){stop();phase=p;draw()},getPhase(){return phase}};</script></html>'''
html=html.replace('__DATA__',json.dumps(frames)).replace('__VIEWS__',json.dumps(views)).replace('__M__',json.dumps(mat['matrix']));(P/'review.html').write_text(html)
(P/'preview-bindings.json').write_text(json.dumps(dict(files=preview,one_bank_matrix=mat['matrix'],source_clock_ms=[190,180,190,180,190,180,190,600],dense_clock_ms=[50]*26+[600],production_pass=False),indent=2)+'\n');print('LOCAL_REVIEW_BUILT',len(preview))
