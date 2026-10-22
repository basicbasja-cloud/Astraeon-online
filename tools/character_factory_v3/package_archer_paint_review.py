"""Bundle actual Archer paint candidates without claiming final cutout coverage."""
import argparse,json,shutil,sys
from pathlib import Path
from PIL import Image,ImageDraw
from build_fixed_grid_sequence_review import gif

HTML='''<!doctype html><meta charset="utf-8"><title>Archer production review</title>
<style>body{font:16px system-ui;background:#202632;color:#eee;margin:24px}canvas{background:#ddd;width:480px;height:480px;max-width:45vw;max-height:45vw}button,select,input{margin:8px;padding:8px}a{color:#aadaff}.warning{color:#ffd18a}section{display:flex;gap:16px;flex-wrap:wrap}</style>
<h1>Archer — work in progress</h1><p class="warning">ภาพทดลอง ยังไม่ผ่านตรวจ anatomy และแยกอาวุธไม่ครบ ไม่ใช่แพตช์พร้อมใช้</p>
<select id="sex"><option value="male">ชาย</option><option value="female">หญิง</option></select><select id="direction"><option>SW</option><option>NW</option><option>NE</option><option>SE</option></select>
<button id="play">เล่น / หยุด</button><select id="speed"><option value="1">ความเร็วปกติ</option><option value="0.333333">ช้า</option></select><input id="frame" type="range" min="0" max="15" value="0"><span id="index"></span>
<section><div><h2>Guide</h2><canvas id="guide" width="240" height="240"></canvas></div><div><h2>ภาพวาด</h2><canvas id="paint" width="240" height="240"></canvas></div></section>
<label><input id="head" type="checkbox" checked>หัว+ผม (ไดคัทชาย NW เท่านั้น)</label><label><input id="body" type="checkbox" checked>ตัวรวมอาวุธ (ยังแยกไม่เสร็จ)</label>
<p id="notes"></p><p><a href="four-view-normal.gif">GIF ชาย+หญิง ปกติ</a> · <a href="four-view-slow.gif">GIF ช้า</a> · <a href="review.json">ข้อมูลการตรวจ</a></p>
<script>
const $=id=>document.getElementById(id),cache=new Map();let frame=0,playing=false,acc=0,last=0,data;
function image(path){if(!cache.has(path)){let im=new Image();im.onload=draw;im.src=path;cache.set(path,im)}return cache.get(path)}
function layer(ctx,path){let im=image(path);if(im.complete&&im.naturalWidth)ctx.drawImage(im,0,0,240,240)}
function draw(){if(!data)return;let sex=$('sex').value,d=$('direction').value,g=$('guide').getContext('2d'),p=$('paint').getContext('2d');g.clearRect(0,0,240,240);p.clearRect(0,0,240,240);let n=String(frame).padStart(3,'0'),source=d==='NE'&&frame===9?'008':n;layer(g,`guide/${d}/${source}.png`);
if(sex==='male'&&d==='NW'){if($('body').checked)layer(p,`head-study/BodyCostume/${n}.png`);if($('head').checked)layer(p,`head-study/HeadHair/${n}.png`)}else layer(p,`${sex}/${d}/${n}.png`);
$('frame').value=frame;$('index').textContent=frame+'/15';$('notes').textContent='NE ใช้ pose8 ซ้ำใน slot9 เพื่อคงท่าง้าง; ปล่อยที่ slot10 เท่าเดิม มี15 poses/16 slots. ต้องแก้ลูกธนูที่กลับมาช่วง recovery และตรวจรอยต่อก่อนใช้จริง.';}
function tick(now){if(playing&&data){acc+=(now-last)*Number($('speed').value);while(acc>=data.durations[frame]){acc-=data.durations[frame];if(frame===15){playing=false;break}frame++}draw()}last=now;requestAnimationFrame(tick)}
$('play').onclick=()=>{if(frame===15)frame=0;playing=!playing;acc=0;draw()};$('frame').oninput=e=>{frame=Number(e.target.value);playing=false;draw()};for(const id of ['sex','direction','head','body'])$(id).onchange=draw;fetch('review.json').then(r=>r.json()).then(d=>{data=d;draw();requestAnimationFrame(tick)});
</script>'''

def package(base,outputs,destination):
    destination.mkdir(parents=True,exist_ok=True)
    durations=json.loads((outputs/'archer-NE-canonical-paint-candidate/receipt.json').read_text())['preview_durations_ms']
    directions=['SW','NW','NE','SE'];canvases=[Image.new('RGBA',(960,600),'#e8e8e8')for _ in range(16)];receipts={}
    for row,sex in enumerate(['male','female']):
        for col,direction in enumerate(directions):
            folder=outputs/(f'archer-{direction}-canonical-paint-candidate'if sex=='male'else f'archer-female-{direction}-canonical-paint-candidate')
            receipts[sex+'/'+direction]=json.loads((folder/'receipt.json').read_text())
            target=destination/sex/direction;target.mkdir(parents=True,exist_ok=True)
            for i in range(16):
                source=folder/'runtime'/f'{i:03d}.png';shutil.copy2(source,target/source.name)
                canvases[i].alpha_composite(Image.open(source),(col*240,row*300+30));draw=ImageDraw.Draw(canvases[i]);draw.text((col*240+10,row*300+8),sex+' '+direction,fill='black');draw.text((10,row*300+277),'WIP | source fit / arrow recovery / complete cutouts pending',fill='black')
    guide=base/'guides/2fed9f286cdd5c5ffbf4'
    for direction in directions:
        target=destination/'guide'/direction;target.mkdir(parents=True,exist_ok=True)
        for i in range(16):
            Image.open(guide/direction/f'{i:03d}.png').convert('RGBa').resize((240,240),Image.Resampling.LANCZOS).convert('RGBA').save(target/f'{i:03d}.png')
    heads=base/'painted-candidates/archer-male-basicattack/NW/current-guide-rear-locked/head-cutouts'
    for role in ['HeadHair','BodyCostume']:
        target=destination/'head-study'/role;target.mkdir(parents=True,exist_ok=True)
        for i in range(16):Image.open(heads/role/f'{i:03d}.png').convert('RGBa').resize((240,240),Image.Resampling.LANCZOS).convert('RGBA').save(target/f'{i:03d}.png')
    gif(canvases,destination/'four-view-normal.gif',durations);gif(canvases,destination/'four-view-slow.gif',[d*3 for d in durations])
    report={'status':'WIP_ART_REQUIRES_REVISION','durations':durations,'directions':directions,'characters':['male','female'],'timeline_slots':16,'NE_distinct_poses':15,'source_guide':guide.name,'source_equivalence_receipt':str(base/'research/archer-source-fingerprint-equivalence.json'),'complete_cutout_jobs':0,'owner_approved':False,'runtime_admitted':False,'known_defects':['Painted recovery arrows reappear in some directions; must be removed without changing body pixels.','Raw NE slot9 releases early; explicit certified pose8 hold used for this preview.','Per-frame painting drift and anatomical source fitting still require inspection.','HeadHair proposals are exclusive visible-pixel masks; BodyCostume still contains bow, gloves and quiver.','No hidden-surface costume repair, full weapon separation or runtime admission.'],'candidate_receipts':receipts}
    (destination/'review.json').write_text(json.dumps(report,indent=2)+'\n');(destination/'index.html').write_text(HTML);return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,default=Path('authoring/characters/factory-v3/patch-0.0.1'));p.add_argument('--outputs',type=Path,default=Path('/workspace/outputs'));p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=package(a.base,a.outputs,a.output);print(json.dumps({'output':str(a.output),'status':r['status']}))
