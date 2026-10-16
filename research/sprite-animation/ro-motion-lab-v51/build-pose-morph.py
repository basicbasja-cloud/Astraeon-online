"""Original key-assisted mesh authoring, not16native drawings or foot patching."""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from scipy.interpolate import PchipInterpolator
from PIL import Image
P=Path(__file__).resolve().parent;root=P.parents[2];bank=P/'candidates/N-empty-body-attempt1.png';im=Image.open(bank).convert('RGBA');(P/'pose-textures').mkdir(exist_ok=True)
for i in range(8):im.crop((i%4*384,i//4*512,i%4*384+384,i//4*512+512)).save(P/'pose-textures'/f'{i:02}.png')
for name in ['sprite-pose-morph.js','sprite-clip-clock.cjs']:shutil.copyfile(root/'tools'/name,P/'inputs'/name)
# Visible art contours/collar/embroidered hem/knee-armor band, manually authored.
# These are not recovered anatomical joints. Source bands below450are fixed.
crowns=[80,84,147,204,172,83,82,82];nape=[188,193,245,291,264,190,190,190];shoulder=[220,224,278,316,292,220,220,220];logo=[355,356,352,356,347,354,354,354];hem=[391,392,375,380,376,388,391,391];knee=[407,409,417,439,434,408,408,408]
cages=[[0,crowns[i]-8,crowns[i]+40,nape[i],shoulder[i],logo[i],hem[i],knee[i],450,512] for i in range(8)]
keys=[0,1,2,3,4,5,7];variants={}
for early in [.13,.16,.19]:
 for down in [.30,.33]:
  for up in [.79,.84,.89,.93]:
   times=[0,early,down,7/15,.63,up,1];curve=PchipInterpolator(times,[crowns[k] for k in keys]);samples=[]
   for t in np.linspace(0,1,16):
    j=min(len(keys)-2,max(0,np.searchsorted(times,t,side='right')-1));a,b=keys[j:j+2];cy=float(curve(t));f=max(0,min(1,(cy-crowns[a])/(crowns[b]-crowns[a])));samples.append({'a':a,'b':b,'f':f,'phase':float(t),'authored_crown_y':cy})
   name=f'e{early:.2f}-d{down:.2f}-u{up:.2f}';variants[name]={'samples':samples,'durations':[90]*15+[550],'source_key_times':times}
data={'width':384,'height':512,'grid_px':16,'textures':[f'pose-textures/{i:02}.png' for i in range(8)],'texture_sha256':[hashlib.sha256((P/'pose-textures'/f'{i:02}.png').read_bytes()).hexdigest() for i in range(8)],'cage_y':cages,'cage_scope':'Manually observed painted contours, not anatomical joint recovery; same source cages across all24variants, fixed distal rows>=450','variants':variants,'new_native_drawings':False,'source_art_bank_sha256':hashlib.sha256(bank.read_bytes()).hexdigest(),'body_renderer':'Two original painted key textures in a common interpolated mesh; premultiplied color interpolation, no sole clone/foot patch or frame-to-frame coordinate fitting','prop':'Separate original SVG geometry, not an external sprite; bound receiver/occlusion remains subject to image review'}
(P/'pose-morph-contract.json').write_text(json.dumps(data,indent=2)+'\n')
html='''<!doctype html><html lang="th"><meta charset="utf-8"><title>ตรวจท่าก้มทั้งตัว</title><style>body{font:16px system-ui;background:#20252d;color:#eee;margin:24px}canvas{background:#292b30;max-width:100%;height:auto}button,select,input{font:inherit;margin:6px}p{max-width:1000px;line-height:1.5}</style><h1>ท่าก้ม16เฟรม · ตรวจจังหวะทั้งตัว</h1><p>ภาพวาดคีย์เดิมกับเมชสร้างท่าระหว่างคีย์ · กำลังตรวจ ไม่ใช่ผลอนุมัติชุดท่า</p><canvas id="view" width="768" height="512"></canvas><p><select id="variant"></select><button id="play">เล่น</button><button id="prev">ก่อนหน้า</button><button id="next">ถัดไป</button><input id="frame" type="range" min="0" max="15" value="0"><select id="speed"><option value="1">1×</option><option value="0.25">0.25×</option></select><label><input id="loop" type="checkbox">วน</label></p><p id="status"></p><script src="inputs/sprite-pose-morph.js"></script><script src="inputs/sprite-clip-clock.cjs"></script><script>
const D=__DATA__,$=x=>document.getElementById(x),ctx=$('view').getContext('2d');let morph,clock,name=Object.keys(D.variants)[0],k=0,last=0,before=[];const off=document.createElement('canvas');
for(let n of Object.keys(D.variants))$('variant').add(new Option(n,n));
function draw(){ctx.clearRect(0,0,768,512);ctx.drawImage(before[k],0,0);morph.draw(D.variants[name].samples[k]);ctx.drawImage(off,384,0);$('frame').value=k;$('status').textContent=`เฟรม${k+1}/16 · ซ้าย: ชุดที่ผู้ใช้แจ้งว่ายังเด้ง · ขวา: ตัวเลือกที่กำลังตรวจ · ${name}`;$('play').textContent=clock.running?'หยุด':'เล่น'}
function choose(n){name=n;clock=new SpriteClipClock({...D.variants[n],loop:$('loop').checked});k=0;draw()}function select(i){k=i;clock.cancel();draw()}
$('variant').onchange=()=>choose($('variant').value);$('frame').oninput=()=>select(+$('frame').value);$('prev').onclick=()=>select(Math.max(0,k-1));$('next').onclick=()=>select(Math.min(15,k+1));$('play').onclick=()=>{if(clock.running)clock.cancel();else{clock.clip.loop=$('loop').checked;clock.start()}last=performance.now();draw()};
function tick(t){if(clock&&clock.running){k=clock.advance((t-last)*+$('speed').value).frame;draw()}last=t;requestAnimationFrame(tick)}
function load(s){return new Promise((ok,no)=>{let im=new Image();im.onload=()=>ok(im);im.onerror=no;im.src=s})}
Promise.all([Promise.all(D.textures.map(load)),Promise.all(Array.from({length:16},(_,i)=>load('../pickup-contact-v49/renders/corrected/'+String(i).padStart(2,'0')+'.png')))]).then(([images,old])=>{before=old;morph=new SpritePoseMorph(off,images,D);choose(name);window.READY=true;requestAnimationFrame(tick)});
window.study={data:D,choose,select,get morph(){return morph},get clock(){return clock},frame(n,i){const geo=morph.draw(D.variants[n].samples[i]);return{png:off.toDataURL('image/png'),geometry:geo}}};
</script></html>'''
(P/'pose-morph-review.html').write_text(html.replace('__DATA__',json.dumps(data,separators=(',',':'))));print('24true curve variants /16render samples each /same8source poses')
