"""Selected integrated body bank, exact ready closure and separate pose-bound tail."""
import json,hashlib,shutil,base64,importlib.util
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'research/sprite-animation/weighted-slash-v27'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def url(p):return 'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()
def main():
    source=json.loads((OUT/'rig-source/source-index.json').read_text());packing=json.loads((OUT/'evidence/full-sword-recovered-packing.json').read_text());bank=OUT/'body/frames';bank.mkdir(parents=True,exist_ok=True)
    pts=[[[223, 336], [214, 324], [230, 344], [194, 294], [210, 236]], [[157, 192], [138, 199], [165, 190], [116, 208], [174, 231]], [[165, 182], [147, 187], [173, 184], [127, 196], [184, 232]], [[285, 276], [272, 265], [294, 280], [236, 252], [204, 235]], [[291, 315], [278, 302], [297, 319], [238, 274], [207, 235]], [[291, 311], [277, 301], [299, 316], [242, 274], [206, 235]], [[215, 265], [202, 253], [223, 271], [184, 230], [205, 200]], [[223, 336], [214, 324], [230, 344], [194, 294], [210, 236]]]
    tips=[[391, 452], [136, 98], [148, 102], [414, 325], [438, 396], [426, 407], [398, 382], [391, 452]]
    frames=[];metrics=[]
    for i,ref in enumerate(source['records']):
        src=OUT/'full-sword-recovered/frames'/f'{i if i<7 else 0:02}.png';path=bank/f'{i:02}.png';shutil.copyfile(src,path)
        palm,wrist,knuckles,elbow,shoulder=pts[i]
        vector=[tips[i][k]-palm[k] for k in [0,1]]
        frames.append({'key':i,'time_ms':ref['time_ms'],'duration_ms':ref['duration_ms'],'phase':ref['phase'],**bind(path),
            'palm_xy':palm,'visible_points':{'palm':palm,'wrist':wrist,'knuckles':knuckles,'elbow':elbow,'shoulder':shoulder},
            'right_hand_identity_reviewed':False,'balance_review':'review_required','uncertainty_px':8,
            'source_key':i,'source_image':bind(OUT/'rig-source/grip-guide'/f'{i:02}.png'),'guide_vector_xy':vector,'visible_tip_xy':tips[i],'blade_vector_scope':'Observed painted grip-to-tip; NOT source projection or rotation of a flat weapon sprite.',
            'source_hand_matrix_world':ref['hand_matrix_world'],'source_matrix_scope':'Actual template only; NOT a recovered painted hand matrix.',
            'closing_key_copy_of':0 if i==7 else None})
        a=np.array(Image.open(path).convert('RGBA'));rgb=a[:,:,:3].astype(float);mask=(a[:,:,3]>128)&(rgb[:,:,2]>100)&(rgb[:,:,0]>105)&(rgb[:,:,1]>85)&(rgb[:,:,2]>rgb[:,:,1]+8)&(rgb[:,:,0]<rgb[:,:,2]+20)
        yy,xx=np.indices(mask.shape);mask&=(yy<240)&(xx>140)&(xx<380);ys,xs=np.where(mask)
        metrics.append({'key':i,'hair_surface_centroid_xy':[float(xs.mean()),float(ys.mean())],'pixels':len(xs),'scope':'Palette/ROI surface diagnostic, not a skull joint/root/COM.'})
    data={'schema':'weighted-sword-tail-demo-v27','duration_ms':680,'frames':frames,'virtual_blade_scale':1,'FX_window_ms':[230,400],
        'virtual_trajectory_scope':'Projected hidden source blade vectors and manually observed painted palms, authored mapping; no rendered rigid blade or actual painted 3D reconstruction.',
        'user_approved':False,'painted_parts_complete':False,'known_review_limits':['Screen-left rear warm-brown boot surface varies25.85pxX/9.57pxY after front-boot registration; calibration front boot excluded from validation. Source heel roll does not approve this discrepancy.','Hidden hips/palm internals/world contacts and full replacement parts unverified.']}
    e=OUT/'evidence';(e/'selected-bank.json').write_text(json.dumps(data,indent=2)+'\n');(e/'hair-surface-review.json').write_text(json.dumps(metrics,indent=2)+'\n')
    case={'schema':'motion-mechanics-v1','action':'attack','attack_representation':'hand_sweep_tail','user_status':'REVIEW_REQUIRED',
        'bindings':[bind(e/'selected-bank.json'),bind(OUT/'rig-source/source-index.json')],
        'frames':[{'time_ms':f['time_ms'],'image':{'path':f['path'],'sha256':f['sha256']},'source_image':f['source_image'],'visible_points':f['visible_points'],
            'right_hand_identity_reviewed':False,'balance_review':'review_required','uncertainty_px':8} for f in frames]}
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
    html='''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport"content="width=device-width,initial-scale=1"><title>Weighted diagonal slash v27</title><style>body{font:15px system-ui;background:#171b20;color:#e9edf2;max-width:1350px;margin:auto;padding:20px}h1{font-size:24px}button,select{font:inherit;background:#303845;color:white;border:1px solid #67758a;padding:8px;border-radius:5px}nav{display:flex;gap:12px;flex-wrap:wrap;align-items:center}#panels{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:18px 0}canvas{display:block;width:100%;background:#272727}#strip{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:5px}small{color:#bbc5d3}#phase{width:min(450px,85vw)}@media(max-width:700px){body{padding:12px}#panels{grid-template-columns:1fr}#strip{grid-template-columns:repeat(4,minmax(0,1fr))}}</style><h1>ท่าฟันเฉียง · ถ่ายน้ำหนัก / ภาพดาบรายท่า</h1><p>8 ช่วงท่า / 680ms · ง้าง → ฟัน → ตามแรง → คืนท่า</p><nav><button id="play">Play once</button><button id="reset">Restart</button><button id="prev">◀</button><button id="next">▶</button><label><input id="fx"type="checkbox">Tail (ทดลอง)</label><label><input id="markers"type="checkbox">Hand points / source bones</label><select id="speed"><option value="1">1×</option><option value=".5">½×</option></select></nav><p><input id="phase"type="range"min="0"max="680"value="0"> <span id="clock"></span></p><div id="panels"><div><small>ต้นแบบใหม่ · กระดูกแสดงเฉพาะต้นแบบ</small><canvas id="source"width="512"height="512"></canvas></div><div><small>ภาพเรา + ดาบรายท่า · ปิดเอฟเฟกต์</small><canvas id="body"width="512"height="512"></canvas></div><div><small>ภาพเรา + tail แยกเลเยอร์</small><canvas id="main"width="512"height="512"></canvas></div></div><div id="strip"></div><p><small>ฉบับตรวจภาพ: มือขวา/ฐานเท้าใช้จุดภาพเพื่อทบทวน ยังไม่อนุมัติ รองเท้าหลังยังต่างแนวนอน25.85px; แนวตั้ง9.57px; ไม่ได้ยืนยัน foot-lock ในเกมหรือชุดชิ้นส่วนภาพตัวละครครบ ดาบอยู่ในภาพของแต่ละคีย์ ไม่มีการหมุนภาพดาบใบเดียว; เลเยอร์อาวุธที่วาดใหม่ยังตรวจการแทนชิ้นส่วนไม่ครบ</small></p><script>const DATA=__DATA__;__RUNTIME__
const $=id=>document.getElementById(id),images=new Map(),state={time:0,playing:false,cancelled:false};
function paint(c,im){const ctx=c.getContext('2d');ctx.clearRect(0,0,512,512);ctx.drawImage(im,0,0)}
function render(t=state.time){state.time=Math.max(0,Math.min(DURATION,t));const i=keyAt(state.time),f=DATA.frames[i];$('phase').value=state.time;$('clock').textContent=`${Math.round(state.time)}ms · pose${i+1}/8 · ${f.phase}`;paint($('source'),images.get(f.source));paint($('body'),images.get(f.art));const ctx=$('main').getContext('2d');ctx.clearRect(0,0,512,512);const g=drawTail(ctx,state.time,DATA,{cancelled:state.cancelled,enabled:$('fx').checked});ctx.drawImage(images.get(f.art),0,0);
if($('markers').checked){for(const id of ['body','main']){const c=$(id).getContext('2d');c.strokeStyle='#24d6ff';c.beginPath();['shoulder','elbow','wrist','palm'].forEach((n,j)=>j?c.lineTo(...f.visible_points[n]):c.moveTo(...f.visible_points[n]));c.stroke()}const c=$('source').getContext('2d');for(const side of ['r','l']){c.strokeStyle=side==='r'?'#2aa0ff':'#ff9738';for(const chain of [['upperarm','lowerarm','hand'],['thigh','calf','foot']]){c.beginPath();chain.forEach((n,j)=>{const p=f.source_bones[n+'_'+side].xy;j?c.lineTo(...p):c.moveTo(...p)});c.stroke()}}}
for(let j=0;j<8;j++)$('strip').children[j].style.outline=j===i?'2px solid #ddba6a':'none';$('play').textContent=state.playing?'Pause':'Play once';return {key:i,fx_active:g.active,endpoint_error_px:g.endpoint_error_px,rendered_rigid_weapon:true}}
function setTime(t){state.playing=false;state.cancelled=false;return render(t)};$('phase').oninput=()=>setTime(Number($('phase').value));$('prev').onclick=()=>setTime(TIMES[Math.max(0,keyAt(state.time)-1)]);$('next').onclick=()=>setTime(TIMES[Math.min(7,keyAt(state.time)+1)]);$('reset').onclick=()=>setTime(0);$('fx').onchange=$('markers').onchange=()=>render();$('play').onclick=()=>{if(state.time>=DURATION)state.time=0;state.playing=!state.playing;render()};let last=performance.now();function tick(now){if(state.playing){state.time+=(now-last)*Number($('speed').value);if(state.time>=DURATION){state.time=DURATION;state.playing=false}render()}last=now;requestAnimationFrame(tick)}
async function init(){for(const f of DATA.frames)for(const src of[f.art,f.source])if(!images.has(src)){const im=new Image();im.src=src;await im.decode();images.set(src,im)}for(let i=0;i<8;i++){const c=document.createElement('canvas');c.width=c.height=512;paint(c,images.get(DATA.frames[i].art));$('strip').append(c)}render();window.SLASHQA={DATA,state,setTime,render,keyAt,geometry:t=>geometry(t,DATA),cancel(){state.cancelled=true;render()},drawFX(t,c){const ctx=c.getContext('2d');ctx.clearRect(0,0,512,512);return drawTail(ctx,t,DATA)}};requestAnimationFrame(tick)}init();</script></html>'''
    (OUT/'review.html').write_text(html.replace('__DATA__',json.dumps(data,separators=(',',':'))).replace('__RUNTIME__',runtime));print('STABLE_SLASH_REVIEW_READY',len((OUT/'review.html').read_bytes()))
if __name__=='__main__':main()
