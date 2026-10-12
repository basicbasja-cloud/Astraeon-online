"""Self-contained Canvas review and exact-clock capture surface; no SVG."""
import base64,hashlib,json,io
from PIL import Image
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'research/sprite-animation/registered-walk-attack-v21'
def url(p,lossless_webp=False):
 if not lossless_webp:return 'data:image/png;base64,'+base64.b64encode(Path(p).read_bytes()).decode()
 im=Image.open(p).convert('RGBA');b=io.BytesIO();im.save(b,format='WEBP',lossless=True,exact=True,method=6);payload=b.getvalue();decoded=Image.open(io.BytesIO(payload)).convert('RGBA');assert np.array_equal(np.array(im),np.array(decoded)),'Lossless source preview changed RGBA'
 return 'data:image/webp;base64,'+base64.b64encode(payload).decode()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 data={'walk':[]};walk_source=json.loads((ROOT/'research/sprite-animation/eight-walk-factory-v20/source-phase12/source-index.json').read_text())
 for view in ['S','SE','E','NE','N','NW','W','SW']:
  case=json.loads((OUT/'evidence'/(view+'-motion-case.json')).read_text());report=json.loads((OUT/'evidence'/(view+'-motion-report.json')).read_text());assert sha(OUT/'evidence'/(view+'-motion-case.json'))==report['case_sha256']
  for f in case['frames']:assert sha(ROOT/f['image'])==f['sha256']
  wr=[r for r in walk_source['records'] if r['facing']==view]
  data['walk'].append({'view':view,'art':[url(ROOT/f['image']) for f in case['frames']],'before':[url(ROOT/'research/sprite-animation/eight-walk-factory-v20/candidates'/view/'frames'/f'{i:02}.png') for i in range(8)],'source':[url(ROOT/r['paths']['dressed-owner'],True) for r in wr],'bones':[r['bones'] for r in wr],'vertical_step':report['surface_axis_metrics']['max_vertical_step_px'],'metrics':report['surface_axis_metrics'],'status':report['status']})
 attack=json.loads((OUT/'attack/evidence/painted-attack.json').read_text());source=json.loads((OUT/'attack/source-palm-fixed/source-index.json').read_text());data['attack']=attack;attack['pose_status']='USER_REJECTED'
 for f in attack['frames']:assert sha(ROOT/f['image'])==f['sha256'];f['art']=url(ROOT/f['image'])
 data['attack']['source']=[url(ROOT/r['image'],True) for r in source['records'] if r['view']=='SE'];data['attack']['bones']=[r['bones'] for r in source['records'] if r['view']=='SE']
 fx=(Path(__file__).with_name('attack-trail.mjs')).read_text().replace('export ','')
 html='''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Walk registration & sword attack v21</title>
<style>body{background:#17191d;color:#e7eaf0;font:15px system-ui;margin:0;padding:20px;max-width:1200px;margin:auto}h1{font-size:23px}button,select,input{font:inherit}button,select{padding:8px;background:#303640;color:white;border:1px solid #697281;border-radius:5px}nav{display:flex;flex-wrap:wrap;gap:10px;align-items:center}canvas{background:#272727;width:100%;height:auto;max-width:512px}#panels{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:14px}.card{min-width:0}#grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:18px 0}#grid canvas{max-width:260px}small{display:block;color:#b1bbc8}#measure{width:100%;max-width:100%;height:110px}#status{min-height:46px}#phase{width:min(300px,70vw)}@media(max-width:600px){body{padding:12px}#panels{grid-template-columns:1fr}#grid{grid-template-columns:repeat(2,minmax(0,1fr))}}</style>
<h1>เดิน 8 ทิศ / ฟันดาบมือขวา — v21</h1><p>ชุดตรวจภาพใหม่ · กล้องคงที่ · เก็บภาพก่อนแก้ไว้เทียบ</p>
<nav><select id="mode"><option value="walk">Walk · 8 directions</option><option value="attack">Sword attack · SE (USER_REJECTED poses)</option></select><select id="view"></select><select id="clock"><option value="800">Walk800ms / 8×100</option><option value="600">Walk600ms / 8×75</option></select><button id="play">Play</button><button id="reset">Restart</button><button id="prev">◀</button><button id="next">▶</button><label><input type="checkbox" id="fx" checked>Trail</label><label><input type="checkbox" id="guide">Guides</label></nav>
<p><input id="phase" type="range" min="0" max="7" value="0"> <span id="time"></span></p><p id="status"></p>
<div id="panels"><div class="card"><small id="a-label">New registered pixels</small><canvas id="main" width="512" height="512"></canvas></div><div class="card"><small id="b-label">Previous pixels / same phase</small><canvas id="before" width="512" height="512"></canvas></div><div class="card"><small>Measured motion / actual source</small><canvas id="source" width="512" height="512"></canvas></div></div>
<canvas id="measure" width="1100" height="110"></canvas><div id="grid"></div><p><small>Surface registration passes do not approve hidden hips, finger wrapping, physical contact or complete painted replacement parts. Original source poses and actual painted observations have separate evidence. Attack is a one-shot; body poses and trail share the same clock. All assets remain review candidates.</small></p>
<script>const DATA=__DATA__;__FX__
const $=id=>document.getElementById(id);const state={mode:'walk',view:'W',clock:800,time:0,playing:false,cancelled:false};const imgs=new Map();
async function imageFor(src){if(imgs.has(src))return imgs.get(src);const im=new Image();im.src=src;await im.decode();imgs.set(src,im);return im}
function paint(c,im){const ctx=c.getContext('2d');ctx.clearRect(0,0,c.width,c.height);if(im)ctx.drawImage(im,0,0,c.width,c.height)}
function key(){return state.mode==='attack'?attackKey(state.time):Math.floor(((state.time%state.clock)+state.clock)%state.clock/(state.clock/8))}
function render(ms=state.time){state.time=ms;const i=key();$('phase').value=i;$('time').textContent=`${state.mode} · ${Math.round(ms)}ms · frame${i+1}`;
 const c=$('main'),ctx=c.getContext('2d');ctx.clearRect(0,0,512,512);
 if(state.mode==='attack'){
  const a=DATA.attack;const g=trailGeometry(ms,a.frames,state.cancelled||!$('fx').checked);drawTrail(ctx,g);ctx.drawImage(imgs.get(a.frames[i].art),0,0);paint($('before'),imgs.get(a.frames[i].art));paint($('source'),imgs.get(a.source[i]));
  $('a-label').textContent='Painted body + separate runtime trail';$('b-label').textContent='Same body pixels · FX off';$('status').textContent=`USER_REJECTED posing · SE / anatomical RIGHT weapon · ${i+1}/8 · FX ${g.active?'strike only':'off'} · expires430ms · other boot surface deviation≤${a.independent_other_boot_max_abs_deviation_px.toFixed(2)}px. Contact calibration is not anatomy approval.`;
  if($('guide').checked){ctx.strokeStyle='#00dcff';ctx.beginPath();ctx.moveTo(...a.frames[i].right_palm_xy);ctx.lineTo(...a.frames[i].blade_base_xy);ctx.lineTo(...a.frames[i].blade_tip_xy);ctx.stroke();for(const [p,col] of [[a.frames[i].right_boot_calibration.output_xy,'#2895ff'],[a.frames[i].left_boot_held_out.output_xy,'#ff8b20']]){ctx.fillStyle=col;ctx.beginPath();ctx.arc(...p,4,0,Math.PI*2);ctx.fill()}}
 }else{
  const b=DATA.walk.find(x=>x.view===state.view);ctx.drawImage(imgs.get(b.art[i]),0,0);paint($('before'),imgs.get(b.before[i]));paint($('source'),imgs.get(b.source[i]));$('a-label').textContent='New registered pixels';$('b-label').textContent='v20 before · same exposure';$('status').textContent=`${state.view} · max measured vertical step${b.vertical_step.toFixed(2)}px · ${b.status}. Source-assisted surface calibration; physical root/contact and hidden anatomy unresolved.`;
  if($('guide').checked){const p=b.metrics.xy[i];ctx.strokeStyle='#93dbff';ctx.beginPath();ctx.moveTo(p[0]-12,p[1]);ctx.lineTo(p[0]+12,p[1]);ctx.moveTo(p[0],p[1]-12);ctx.lineTo(p[0],p[1]+12);ctx.stroke()}
 }
 if($('guide').checked){const bones=state.mode==='attack'?DATA.attack.bones[i]:DATA.walk.find(x=>x.view===state.view).bones[i];const sc=$('source').getContext('2d');for(const [side,col] of [['r','#2895ff'],['l','#ff891b']])for(const chain of [['thigh_'+side,'calf_'+side,'foot_'+side,'ball_'+side],['upperarm_'+side,'lowerarm_'+side,'hand_'+side]]){sc.strokeStyle=col;sc.lineWidth=2;sc.beginPath();chain.forEach((n,j)=>j?sc.lineTo(...bones[n].xy):sc.moveTo(...bones[n].xy));sc.stroke()}}
 const gc=$('measure').getContext('2d');gc.clearRect(0,0,1100,110);gc.fillStyle='#272727';gc.fillRect(0,0,1100,110);gc.strokeStyle='#cfa45d';gc.beginPath();const ys=state.mode==='walk'?DATA.walk.find(x=>x.view===state.view).metrics.xy.map(p=>p[1]):DATA.attack.frames.map(f=>f.left_boot_held_out.output_xy[1]);const base=ys[0];ys.forEach((y,j)=>{const x=25+j*145,py=55+(y-base)*7;j?gc.lineTo(x,py):gc.moveTo(x,py)});gc.stroke();gc.fillStyle='#e9edf4';gc.fillText(state.mode==='walk'?'Calibrated hair-surface Y (×7) · not independent root/contact proof':'Held-out other-boot contour Y (×7) · not calibrated boot',20,18);gc.fillStyle='#95ddff';gc.fillRect(22+i*145,90,8,8);
 for(const [n,b] of DATA.walk.entries()){const c=$('grid').children[n].querySelector('canvas');paint(c,imgs.get(b.art[state.mode==='walk'?i:0]));c.dataset.frame=state.mode==='walk'?i:0}
 $('clock').disabled=state.mode==='attack';$('view').disabled=state.mode==='attack';$('play').textContent=state.playing?'Pause':'Play';return {key:i,fx:state.mode==='attack'?trailState(ms,state.cancelled||!$('fx').checked):null};}
 function setTime(t){state.playing=false;state.cancelled=false;render(t)}
 $('mode').onchange=()=>{state.mode=$('mode').value;setTime(0)};$('view').onchange=()=>{state.view=$('view').value;render()};$('clock').onchange=()=>{const i=key();state.clock=Number($('clock').value);setTime(i*state.clock/8)};$('phase').oninput=()=>setTime(state.mode==='attack'?ATTACK_STARTS[Number($('phase').value)]:Number($('phase').value)*state.clock/8);$('reset').onclick=()=>setTime(0);
 for(const [id,step] of [['prev',-1],['next',1]])$(id).onclick=()=>{const k=state.mode==='attack'?Math.max(0,Math.min(7,key()+step)):(key()+step+8)%8;setTime(state.mode==='attack'?ATTACK_STARTS[k]:k*state.clock/8)};
 $('play').onclick=()=>{if(state.mode==='attack'&&state.time>=800)state.time=0;state.playing=!state.playing;render()};$('fx').onchange=()=>render();$('guide').onchange=()=>render();
 let last=performance.now();function tick(now){if(state.playing){state.time+=now-last;if(state.mode==='attack'&&state.time>=800){state.time=800;state.playing=false}render()}last=now;requestAnimationFrame(tick)}
 async function init(){for(const b of DATA.walk){const o=document.createElement('option');o.value=b.view;o.textContent=b.view;$('view').append(o);const card=document.createElement('div');card.innerHTML=`<small>${b.view}</small><canvas width="512" height="512"></canvas>`;$('grid').append(card);for(const src of [...b.art,...b.before,...b.source])await imageFor(src)}for(const f of DATA.attack.frames)await imageFor(f.art);for(const src of DATA.attack.source)await imageFor(src);$('view').value='W';render();window.LAB={DATA,state,setTime,render,key,cancel(){state.cancelled=true;render()},drawFX(t,canvas){const ctx=canvas.getContext('2d');ctx.clearRect(0,0,512,512);drawTrail(ctx,trailGeometry(t,DATA.attack.frames))}};requestAnimationFrame(tick)}init();
</script></html>'''
 html=html.replace('__DATA__',json.dumps(data,separators=(',',':'))).replace('__FX__',fx);(OUT/'review.html').write_text(html)
 print('REVIEW_HTML',len(html.encode()),'bytes,208embedded frames')
if __name__=='__main__':main()
