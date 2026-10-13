"""Selected integrated body bank, exact ready closure and separate pose-bound tail."""
import json,hashlib,shutil,base64,importlib.util
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'research/sprite-animation/stable-hand-sweep-v24'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def url(p):return 'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()
def main():
    source=json.loads((OUT/'source/source-index.json').read_text());packing=json.loads((OUT/'evidence/attempt2-packing.json').read_text());bank=OUT/'body/frames';bank.mkdir(parents=True,exist_ok=True)
    pts=[[[234,337],[220,318],[241,345],[202,283],[211,233]],[[188,190],[175,201],[197,180],[153,210],[216,223]],
         [[220,128],[206,151],[229,117],[185,178],[218,207]],[[354,311],[333,301],[365,315],[287,278],[242,240]],
         [[351,317],[330,307],[362,323],[286,281],[241,241]],[[281,326],[264,310],[288,333],[238,282],[221,228]],
         [[225,282],[205,274],[233,289],[178,260],[209,223]],[[234,337],[220,318],[241,345],[202,283],[211,233]]]
    frames=[];metrics=[]
    for i,ref in enumerate(source['records']):
        src=OUT/'attempt2/frames'/f'{i if i<7 else 0:02}.png';path=bank/f'{i:02}.png';shutil.copyfile(src,path)
        palm,wrist,knuckles,elbow,shoulder=pts[i]
        vector=[ref['blade_tip_xy'][k]-ref['right_grip_xy'][k] for k in [0,1]]
        frames.append({'key':i,'time_ms':ref['time_ms'],'duration_ms':ref['duration_ms'],'phase':ref['phase'],**bind(path),
            'palm_xy':palm,'visible_points':{'palm':palm,'wrist':wrist,'knuckles':knuckles,'elbow':elbow,'shoulder':shoulder},
            'right_hand_identity_reviewed':True,'balance_review':'reviewed','uncertainty_px':4,
            'source_key':i,'source_image':bind(ROOT/ref['image']),'guide_vector_xy':vector,
            'source_hand_matrix_world':ref['hand_matrix_world'],'source_matrix_scope':'Actual template only; NOT a recovered painted hand matrix.',
            'closing_key_copy_of':0 if i==7 else None})
        a=np.array(Image.open(path).convert('RGBA'));rgb=a[:,:,:3].astype(float);mask=(a[:,:,3]>128)&(rgb[:,:,2]>100)&(rgb[:,:,0]>105)&(rgb[:,:,1]>85)&(rgb[:,:,2]>rgb[:,:,1]+8)&(rgb[:,:,0]<rgb[:,:,2]+20)
        yy,xx=np.indices(mask.shape);mask&=(yy<240)&(xx>140)&(xx<380);ys,xs=np.where(mask)
        metrics.append({'key':i,'hair_surface_centroid_xy':[float(xs.mean()),float(ys.mean())],'pixels':len(xs),'scope':'Palette/ROI surface diagnostic, not a skull joint/root/COM.'})
    data={'schema':'stable-hand-tail-demo-v24','duration_ms':720,'frames':frames,'virtual_blade_scale':.85,'FX_window_ms':[260,440],
        'virtual_trajectory_scope':'Projected hidden source blade vectors and manually observed painted palms, authored mapping; no rendered rigid blade or actual painted 3D reconstruction.',
        'user_approved':False,'painted_parts_complete':False,'known_review_limits':['screen-right lowest-alpha boot point has up to15.53pxX variation; Ydelta0. Calibration boot excluded from validation.','Hidden hips/palm internals/world contacts and full replacement parts unverified.']}
    e=OUT/'evidence';(e/'selected-bank.json').write_text(json.dumps(data,indent=2)+'\n');(e/'hair-surface-review.json').write_text(json.dumps(metrics,indent=2)+'\n')
    case={'schema':'motion-mechanics-v1','action':'attack','attack_representation':'hand_sweep_tail','user_status':'REVIEW_REQUIRED',
        'bindings':[bind(e/'selected-bank.json'),bind(OUT/'source/source-index.json')],
        'frames':[{'time_ms':f['time_ms'],'image':{'path':f['path'],'sha256':f['sha256']},'source_image':f['source_image'],'visible_points':f['visible_points'],
            'right_hand_identity_reviewed':True,'balance_review':'reviewed','uncertainty_px':4} for f in frames]}
    (e/'painted-mechanics-case.json').write_text(json.dumps(case,indent=2)+'\n');spec=importlib.util.spec_from_file_location('mechanics',ROOT/'skills/modular-eight-direction-sprites/scripts/motion-mechanics.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);(e/'painted-mechanics-report.json').write_text(json.dumps(module.audit(case,ROOT),indent=2)+'\n')
    board=Image.new('RGB',(2048,1104),'#272727');draw=ImageDraw.Draw(board)
    annotations=Image.new('RGB',(2048,1104),'#272727');ad=ImageDraw.Draw(annotations)
    for i,f in enumerate(frames):
        im=Image.open(ROOT/f['path']).convert('RGBA');x=i%4*512;y=i//4*552;board.paste(im,(x,y+40),im);annotations.paste(im,(x,y+40),im);draw.text((x+8,y+8),f'{i+1} {f["phase"]} / {f["time_ms"]}ms',fill='white')
        chain=[f['visible_points'][n] for n in ['shoulder','elbow','wrist','palm']];ad.line([(p[0]+x,p[1]+y+40) for p in chain],fill='#29d6ff',width=2)
        for n,p in f['visible_points'].items():
            xx=p[0]+x;yy=p[1]+y+40;ad.ellipse((xx-3,yy-3,xx+3,yy+3),fill='#29d6ff');ad.text((xx+4,yy+2),n,fill='white')
    board.save(OUT/'eight-key-review.png');annotations.save(OUT/'evidence/observed-hand-review.png')
    for f in data['frames']:
        f['art']=url(ROOT/f['path']);f['source']=url(ROOT/f['source_image']['path']);f['source_bones']=source['records'][f['key']]['bones']
    runtime=(OUT/'hand-tail.mjs').read_text().replace('export ','')
    html='''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport"content="width=device-width,initial-scale=1"><title>Stable hand-sweep attack v24</title><style>body{font:15px system-ui;background:#171b20;color:#e9edf2;max-width:1350px;margin:auto;padding:20px}h1{font-size:24px}button,select{font:inherit;background:#303845;color:white;border:1px solid #67758a;padding:8px;border-radius:5px}nav{display:flex;gap:12px;flex-wrap:wrap;align-items:center}#panels{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:18px 0}canvas{display:block;width:100%;background:#272727}#strip{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:5px}small{color:#bbc5d3}#phase{width:min(450px,85vw)}@media(max-width:700px){body{padding:12px}#panels{grid-template-columns:1fr}#strip{grid-template-columns:repeat(4,minmax(0,1fr))}}</style><h1>ท่าฟันฐานสองเท้า · กวาดมือขวา + sword tail</h1><p>8 ช่วงท่า / 720ms · ง้าง → ฟัน → ตามแรง → คืนท่า</p><nav><button id="play">Play once</button><button id="reset">Restart</button><button id="prev">◀</button><button id="next">▶</button><label><input id="fx"type="checkbox"checked>Tail</label><label><input id="markers"type="checkbox">Hand points / source bones</label><select id="speed"><option value="1">1×</option><option value=".5">½×</option></select></nav><p><input id="phase"type="range"min="0"max="720"value="0"> <span id="clock"></span></p><div id="panels"><div><small>ต้นแบบใหม่ · กระดูกแสดงเฉพาะต้นแบบ</small><canvas id="source"width="512"height="512"></canvas></div><div><small>ภาพเรา · ปิดเอฟเฟกต์</small><canvas id="body"width="512"height="512"></canvas></div><div><small>ภาพเรา + tail แยกเลเยอร์</small><canvas id="main"width="512"height="512"></canvas></div></div><div id="strip"></div><p><small>ฉบับตรวจภาพ: มือขวา/ฐานเท้ามีการตรวจด้วยสายตาและจุดภาพ ขอบรองเท้าข้างไกลยังต่างแนวนอนสูงสุด15.53px; ไม่ได้ยืนยัน foot-lock ในเกมหรือชุดชิ้นส่วนภาพตัวละครครบ ตัวดาบจริงไม่ถูกวาดในช่วงโจมตี</small></p><script>const DATA=__DATA__;__RUNTIME__
const $=id=>document.getElementById(id),images=new Map(),state={time:0,playing:false,cancelled:false};
function paint(c,im){const ctx=c.getContext('2d');ctx.clearRect(0,0,512,512);ctx.drawImage(im,0,0)}
function render(t=state.time){state.time=Math.max(0,Math.min(DURATION,t));const i=keyAt(state.time),f=DATA.frames[i];$('phase').value=state.time;$('clock').textContent=`${Math.round(state.time)}ms · pose${i+1}/8 · ${f.phase}`;paint($('source'),images.get(f.source));paint($('body'),images.get(f.art));const ctx=$('main').getContext('2d');ctx.clearRect(0,0,512,512);const g=drawTail(ctx,state.time,DATA,{cancelled:state.cancelled,enabled:$('fx').checked});ctx.drawImage(images.get(f.art),0,0);
if($('markers').checked){for(const id of ['body','main']){const c=$(id).getContext('2d');c.strokeStyle='#24d6ff';c.beginPath();['shoulder','elbow','wrist','palm'].forEach((n,j)=>j?c.lineTo(...f.visible_points[n]):c.moveTo(...f.visible_points[n]));c.stroke()}const c=$('source').getContext('2d');for(const side of ['r','l']){c.strokeStyle=side==='r'?'#2aa0ff':'#ff9738';for(const chain of [['upperarm','lowerarm','hand'],['thigh','calf','foot']]){c.beginPath();chain.forEach((n,j)=>{const p=f.source_bones[n+'_'+side].xy;j?c.lineTo(...p):c.moveTo(...p)});c.stroke()}}}
for(let j=0;j<8;j++)$('strip').children[j].style.outline=j===i?'2px solid #ddba6a':'none';$('play').textContent=state.playing?'Pause':'Play once';return {key:i,fx_active:g.active,endpoint_error_px:g.endpoint_error_px,rendered_rigid_weapon:false}}
function setTime(t){state.playing=false;state.cancelled=false;return render(t)};$('phase').oninput=()=>setTime(Number($('phase').value));$('prev').onclick=()=>setTime(TIMES[Math.max(0,keyAt(state.time)-1)]);$('next').onclick=()=>setTime(TIMES[Math.min(7,keyAt(state.time)+1)]);$('reset').onclick=()=>setTime(0);$('fx').onchange=$('markers').onchange=()=>render();$('play').onclick=()=>{if(state.time>=DURATION)state.time=0;state.playing=!state.playing;render()};let last=performance.now();function tick(now){if(state.playing){state.time+=(now-last)*Number($('speed').value);if(state.time>=DURATION){state.time=DURATION;state.playing=false}render()}last=now;requestAnimationFrame(tick)}
async function init(){for(const f of DATA.frames)for(const src of[f.art,f.source])if(!images.has(src)){const im=new Image();im.src=src;await im.decode();images.set(src,im)}for(let i=0;i<8;i++){const c=document.createElement('canvas');c.width=c.height=512;paint(c,images.get(DATA.frames[i].art));$('strip').append(c)}render();window.SLASHQA={DATA,state,setTime,render,keyAt,geometry:t=>geometry(t,DATA),cancel(){state.cancelled=true;render()},drawFX(t,c){const ctx=c.getContext('2d');ctx.clearRect(0,0,512,512);return drawTail(ctx,t,DATA)}};requestAnimationFrame(tick)}init();</script></html>'''
    (OUT/'review.html').write_text(html.replace('__DATA__',json.dumps(data,separators=(',',':'))).replace('__RUNTIME__',runtime));print('STABLE_SLASH_REVIEW_READY',len((OUT/'review.html').read_bytes()))
if __name__=='__main__':main()
