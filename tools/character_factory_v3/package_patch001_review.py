"""Package actual review artifacts; source guides never count as painted coverage."""
import argparse,json,shutil
from pathlib import Path
from patch001_factory import BASE,ROOT,read,status

HTML='''<!doctype html><meta charset="utf-8"><title>ASTRAEON 0.0.1 production review</title>
<style>body{font:15px system-ui;background:#171b24;color:#e7e8ee;margin:24px}button,select,input{margin:6px;padding:6px}header{max-width:1100px}.warn{color:#ffd08a}canvas{max-width:46vw;background:repeating-conic-gradient(#313641 0% 25%,#383e49 0% 50%) 50%/24px 24px}section{display:flex;gap:18px;flex-wrap:wrap}label{white-space:nowrap}a{color:#9ad8ff}pre{white-space:pre-wrap}#roles{max-width:1000px}</style>
<header><h1>Patch 0.0.1 — production review</h1><p class="warn">In production. Review study only; no owner approval or runtime admission. A clean recomposition does not establish anatomy, motion or replacement quality.</p><pre id="progress"></pre></header>
<select id="clip"></select><button id="play">Play</button><label>Speed <select id="speed"><option value="1">Normal</option><option value="0.333">Slow</option></select></label><label><input id="loop" type="checkbox">Repeat one-shot</label><input id="frame" type="range" min="0" max="15" value="0"><span id="number"></span>
<div id="roles"></div><section><div><h2>Painted same-frame cutouts</h2><canvas id="paint" width="512" height="512"></canvas></div><div><h2>Source pose — separate, unregistered comparison</h2><canvas id="source" width="512" height="512"></canvas></div></section><p id="notes"></p><div id="downloads"></div>
<script>
const $=id=>document.getElementById(id),images={},roles=['BodyCostume','HeadHair','WeaponLightFront','Weapon','WeaponHandOccluder'];let data,current,playing=false,frame=0,last=0,acc=0,drawSerial=0;
async function pic(path){if(!images[path])images[path]=new Promise((resolve,reject)=>{let i=new Image;i.onload=()=>resolve(i);i.onerror=reject;i.src=path});return images[path]}
async function draw(){if(!current)return;const serial=++drawSerial,index=frame,selected=current,enabled=roles.filter(r=>$(r).checked),buffer=document.createElement('canvas');buffer.width=buffer.height=512;const c=buffer.getContext('2d');for(const role of enabled){const image=await pic(selected.layers[role]);if(serial!==drawSerial)return;c.drawImage(image,(index%4)*512,Math.floor(index/4)*512,512,512,0,0,512,512)}const guide=await pic(selected.guides[index]);if(serial!==drawSerial)return;const paint=$('paint').getContext('2d'),source=$('source').getContext('2d');paint.clearRect(0,0,512,512);paint.drawImage(buffer,0,0);source.clearRect(0,0,512,512);source.drawImage(guide,0,0,512,512);$('frame').value=index;$('number').textContent=(index+1)+' / '+selected.frames}
function select(){current=data.clips[$('clip').selectedIndex];frame=0;playing=false;acc=0;$('frame').max=current.frames-1;$('notes').textContent=current.notes;$('downloads').replaceChildren();for(const [label,path]of Object.entries(current.downloads)){let a=document.createElement('a');a.href=path;a.textContent=label;a.style.marginRight='20px';$('downloads').append(a)}draw()}
function tick(now){if(playing&&current){acc+=(now-last)*Number($('speed').value);while(acc>=current.durations[frame]){acc-=current.durations[frame];if(frame===current.frames-1){if($('loop').checked)frame=0;else{playing=false;break}}else frame++;draw()}}last=now;requestAnimationFrame(tick)}
for(const role of roles){let label=document.createElement('label'),box=document.createElement('input');box.type='checkbox';box.id=role;box.checked=true;box.onchange=draw;label.append(box,role);$('roles').append(label)}$('play').onclick=()=>{if(frame===current.frames-1)frame=0;playing=!playing;acc=0;draw()};$('frame').oninput=e=>{playing=false;frame=Number(e.target.value);draw()};$('clip').onchange=select;
fetch('review-data.json').then(r=>r.json()).then(d=>{data=d;$('progress').textContent=JSON.stringify(d.progress,null,2);for(const c of d.clips){let o=document.createElement('option');o.textContent=c.label;$('clip').append(o)}if(d.clips.length)select();else $('notes').textContent='No assembled cutout study exists.';requestAnimationFrame(tick)});
</script>'''


def package(output):
    output.mkdir(parents=True,exist_ok=True);progress=status(read(BASE/'ledger.json'));clips=[]
    folder=BASE/'painted-candidates/swordsman-male-basicattack/SE/padded/cutout-study'
    if(folder/'receipt.json').is_file():
        receipt=read(folder/'receipt.json');target=output/'swordsman-male-basicattack-SE';target.mkdir(exist_ok=True)
        layers={}
        for role in ['BodyCostume','HeadHair','Weapon','WeaponHandOccluder','WeaponLightFront']:
            shutil.copy2(folder/(role+'.png'),target/(role+'.png'));layers[role]=str((target/(role+'.png')).relative_to(output))
        for name in ['normal.gif','slow.gif','receipt.json']:shutil.copy2(folder/name,target/name)
        source=BASE/'guides/d78dbe4acd39ad7c4209/SE';guides=[]
        for i in range(16):
            destination=target/f'guide-{i:03d}.png';shutil.copy2(source/f'{i:03d}.png',destination);guides.append(str(destination.relative_to(output)))
        clips.append({'id':'swordsman-male-basicattack-SE','label':'Swordsman male BasicAttack SE — provisional masks','frames':16,'durations':[80]*4+[55]*3+[65]*3+[90]*6,'layers':layers,'guides':guides,'notes':'Manual mask seeds require edge review. No per-frame scaling/warping; source and painted anatomy are not registered or approved. Independent short curved FX only on cut frames. No hairstyle/costume variant authored yet.','downloads':{'Normal GIF':str((target/'normal.gif').relative_to(output)),'Slow GIF':str((target/'slow.gif').relative_to(output)),'Receipt':str((target/'receipt.json').relative_to(output))}})
    (output/'index.html').write_text(HTML)
    (output/'review-data.json').write_text(json.dumps({'progress':progress,'clips':clips,'runtime_admitted':False},indent=2)+'\n')
    shutil.make_archive(str(output), 'zip', output)
    print(json.dumps({'review':str(output/'index.html'),'archive':str(output)+'.zip','assembled_studies':len(clips),'complete':False}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=Path('/workspace/outputs/patch001-production-review'));a=p.parse_args();package(a.output.resolve())
