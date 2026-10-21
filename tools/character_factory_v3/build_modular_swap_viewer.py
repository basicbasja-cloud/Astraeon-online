"""Build an offline, self-contained viewer for same-frame cosmetic cutouts."""
import argparse
import base64
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('folder',type=Path);args=parser.parse_args();root=args.folder
    data={}
    for skin in ['gold','moon']:
        data[skin]={}
        for part in ['HeadHair','BodyCostume','Weapon','WeaponHandOccluder']:
            data[skin][part]=['data:image/png;base64,'+base64.b64encode((root/skin/part/f'{i:03d}.png').read_bytes()).decode() for i in range(16)]
    data['trail']=['data:image/png;base64,'+base64.b64encode((root/'WeaponLight'/f'{i:03d}.png').read_bytes()).decode() for i in range(16)]
    timing=json.loads((root.parent/'no-cloak-continuous-review/assembly-audit.json').read_text())['durations_ms']
    template='''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Astraeon · ทดลองสลับชิ้นส่วน</title>
<style>*{box-sizing:border-box}body{margin:0;background:#151a25;color:#e9edf6;font:16px system-ui,sans-serif}main{max-width:1080px;margin:32px auto;padding:0 20px}h1{font-size:26px;margin:0 0 8px}p{color:#aeb9cf;line-height:1.6}section{display:grid;grid-template-columns:minmax(300px,560px) minmax(240px,1fr);gap:24px;margin-top:24px}.stage{background:#ececec;border-radius:16px;overflow:hidden}canvas{display:block;width:100%;height:auto}aside{background:#202839;border:1px solid #38445a;padding:24px;border-radius:16px}label{display:block;margin:0 0 18px}select,button{font:inherit;border:1px solid #586782;border-radius:8px;padding:10px;background:#2c3951;color:#fff}select{display:block;width:100%;margin-top:6px}button{cursor:pointer}button:hover{background:#405474}input[type=range]{width:100%}.controls{display:flex;gap:8px;align-items:center;margin:16px 0;flex-wrap:wrap}.presets{display:flex;flex-wrap:wrap;gap:8px}.note{font-size:14px}#status{color:#9fcaea}@media(max-width:720px){section{grid-template-columns:1fr}main{margin-top:20px}}</style>
<main><h1>ทดลองสลับชิ้นส่วน</h1><p>ท่าฟันเดิม · หัว/ทรงผม ชุด และดาบเลือกแยกกันได้</p>
<section><div><div class="stage"><canvas id="canvas" width="512" height="512"></canvas></div><div class="controls"><button id="play" disabled>กำลังโหลด…</button><button id="previous">◀</button><button id="next">▶</button><span id="position">1 / 16</span></div><input id="frame" type="range" min="0" max="15" value="0" aria-label="เลือกเฟรม"><p id="status">กำลังเตรียมภาพ</p></div>
<aside><label>หัว / ทรงผม<select id="head"><option value="gold">ผมเงินเดิม</option><option value="moon">ผมน้ำเงิน ปอยเงิน</option></select></label><label>ชุด<select id="outfit"><option value="gold">นักดาบทอง</option><option value="moon">เกราะเงิน–น้ำเงิน</option></select></label><label>อาวุธ<select id="weapon"><option value="gold">ดาบเหล็กเดิม</option><option value="moon">ดาบผลึกฟ้า</option></select></label><label><input id="trail" type="checkbox" checked> แสดง trail ดาบ</label><label>ความเร็ว<select id="speed"><option value="1">ปกติ</option><option value="0.3333333333" selected>ช้า 3 เท่า</option></select></label><div class="presets"><button data-preset="original">ชุดเดิม</button><button data-preset="head">เปลี่ยนหัว</button><button data-preset="outfit">เปลี่ยนชุด</button><button data-preset="weapon">เปลี่ยนดาบ</button><button data-preset="all">เปลี่ยนทั้งหมด</button></div><p class="note">พรีวิว 16 เฟรม มุม SE · หัวรวมกับผม ส่วนชุดเป็นชิ้นตัวที่สวมชุดแล้ว</p><p class="note">เล่นจบแล้วหยุด กดเล่นอีกครั้งเพื่อเริ่มใหม่</p></aside></section></main>
<script>
const DATA=__DATA__,timing=__TIMING__;
const $=id=>document.getElementById(id),canvas=$('canvas'),ctx=canvas.getContext('2d');let images={},index=0,playing=false,lastTime=null,elapsed=0,loaded=false;
async function loadImage(url){return new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>resolve(image);image.onerror=reject;image.src=url;});}
async function init(){for(const skin of ['gold','moon']){images[skin]={};for(const part of ['HeadHair','BodyCostume','Weapon','WeaponHandOccluder'])images[skin][part]=await Promise.all(DATA[skin][part].map(loadImage));}images.trail=await Promise.all(DATA.trail.map(loadImage));loaded=true;$('play').disabled=false;$('play').textContent='เล่น';$('status').textContent='พร้อมตรวจ · เปิดปิด trail และเลือกชิ้นส่วนได้';render();}
function render(){if(!loaded)return;ctx.clearRect(0,0,512,512);ctx.fillStyle='#ececec';ctx.fillRect(0,0,512,512);ctx.drawImage(images[$('outfit').value].BodyCostume[index],0,0);if($('trail').checked)ctx.drawImage(images.trail[index],0,0);ctx.drawImage(images[$('head').value].HeadHair[index],0,0);ctx.drawImage(images[$('outfit').value].WeaponHandOccluder[index],0,0);ctx.drawImage(images[$('weapon').value].Weapon[index],0,0);$('position').textContent=`${index+1} / 16`;$('frame').value=index;}
function pause(){playing=false;lastTime=null;elapsed=0;if(loaded)$('play').textContent='เล่น';}
function tick(now){if(!playing)return;if(lastTime===null)lastTime=now;elapsed+=(now-lastTime)*Number($('speed').value);lastTime=now;while(elapsed>=timing[index]){elapsed-=timing[index];if(index===15){pause();render();return;}index++;render();}requestAnimationFrame(tick);}
$('play').onclick=()=>{if(!loaded)return;if(playing){pause();return;}if(index===15)index=0;elapsed=0;lastTime=null;playing=true;$('play').textContent='หยุด';render();requestAnimationFrame(tick);};
$('frame').oninput=()=>{pause();index=Number($('frame').value);render();};$('previous').onclick=()=>{pause();index=Math.max(0,index-1);render();};$('next').onclick=()=>{pause();index=Math.min(15,index+1);render();};
for(const id of ['head','outfit','weapon','trail'])$(id).onchange=render;
for(const button of document.querySelectorAll('[data-preset]'))button.onclick=()=>{const preset=button.dataset.preset;for(const id of ['head','outfit','weapon'])$(id).value=(preset==='all'||preset===id)?'moon':'gold';render();};
init().catch(()=>{$('status').textContent='โหลดภาพไม่สำเร็จ กรุณาเปิดไฟล์ใหม่';});
</script></html>'''
    (root/'review.html').write_text(template.replace('__DATA__',json.dumps(data)).replace('__TIMING__',json.dumps(timing)))
    print(json.dumps({'viewer_bytes':(root/'review.html').stat().st_size,'external_dependencies':0,'possible_skin_combinations':8,'trail_toggle':True}))


if __name__=='__main__':main()
