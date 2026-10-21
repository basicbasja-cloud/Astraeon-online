"""Create a standalone four-view attack and visible-layer review page."""
import argparse
import base64
import json
from pathlib import Path

DIRECTIONS=['SW','NW','NE','SE']
PARTS=['WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','WeaponHandOccluder','Weapon']


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('folder',type=Path);args=parser.parse_args();root=args.folder
    data={direction:{part:['data:image/png;base64,'+base64.b64encode((root/direction/part/f'{i:03d}.png').read_bytes()).decode() for i in range(16)] for part in PARTS} for direction in DIRECTIONS}
    timing=json.loads((root/'assembly-audit.json').read_text())['durations_ms']
    template='''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Astraeon · โจมตี 4 ทิศ</title>
<style>*{box-sizing:border-box}body{margin:0;font:16px system-ui,sans-serif;background:#141b28;color:#eef2fa}main{max-width:1000px;margin:30px auto;padding:20px}h1{font-size:26px;margin:0}p{color:#b6c3d8;line-height:1.6}.layout{display:grid;grid-template-columns:minmax(280px,540px) 280px;gap:24px}.stage{background:#ececec;border-radius:16px;overflow:hidden}canvas{width:100%;height:auto;display:block}aside{padding:22px;background:#222e43;border:1px solid #41516c;border-radius:16px}button,select{padding:10px 14px;font:inherit;color:#fff;background:#344863;border:1px solid #617593;border-radius:8px;cursor:pointer}button.active{background:#5e4c2b;border-color:#d4af64}button:disabled{opacity:.5;cursor:wait}.directions,.controls{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}label{display:block;margin:18px 0}input[type=range]{width:100%}select{width:100%;margin-top:8px}.note{font-size:14px}#status{min-height:1.6em}@media(max-width:720px){.layout{grid-template-columns:1fr}main{padding:14px;margin:10px auto}}</style>
<main><h1>ทดลองโจมตี 4 ทิศ</h1><p>ชุดทอง · 16 เฟรมต่อทิศ · เลือกมุมและเปิดปิดส่วนที่ต้องการตรวจ</p><div class="directions"><button data-view="SW">SW</button><button data-view="NW">NW</button><button data-view="NE">NE</button><button data-view="SE">SE</button></div><div class="layout"><div><div class="stage"><canvas id="canvas" width="512" height="512"></canvas></div><div class="controls"><button id="play" disabled>กำลังโหลด…</button><button id="previous">◀</button><button id="next">▶</button><span id="position">1 / 16</span></div><input id="frame" type="range" min="0" max="15" value="0" aria-label="เลือกเฟรม"><p id="status"></p></div><aside><label><input id="head" type="checkbox" checked> หัวและผม</label><label><input id="body" type="checkbox" checked> ตัวพร้อมชุด</label><label><input id="weapon" type="checkbox" checked> อาวุธ</label><label><input id="trail" type="checkbox" checked> Trail ดาบ</label><label>ความเร็ว<select id="speed"><option value="1">ปกติ</option><option value="0.3333333333" selected>ช้า 3 เท่า</option></select></label><p class="note">เล่นจบแล้วหยุด กดเล่นอีกครั้งเพื่อเริ่มใหม่</p><p class="note">เป็นพรีวิวไดคัทส่วนที่มองเห็น ยังไม่มีพื้นผิวที่ซ่อนอยู่ใต้ชิ้นส่วน</p></aside></div></main>
<script>
const DATA=__DATA__,timing=__TIMING__,parts=__PARTS__, $=id=>document.getElementById(id),ctx=$('canvas').getContext('2d');let images={},view='SE',index=0,loaded=false,playing=false,last=null,elapsed=0,request=0;
function stop(){playing=false;last=null;elapsed=0;if(loaded)$('play').textContent='เล่น';}
function render(){if(!loaded)return;ctx.fillStyle='#ececec';ctx.fillRect(0,0,512,512);for(const part of parts){if(part.startsWith('WeaponLight')&&!$('trail').checked)continue;if((part==='BodyCostume'||part==='WeaponHandOccluder')&&!$('body').checked)continue;if(part==='HeadHair'&&!$('head').checked)continue;if(part==='Weapon'&&!$('weapon').checked)continue;ctx.drawImage(images[part][index],0,0);}$('position').textContent=`${view} · ${index+1} / 16`;$('frame').value=index;}
function loadImage(url){return new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>resolve(image);image.onerror=reject;image.src=url;});}
async function choose(direction){stop();const token=++request;loaded=false;$('play').disabled=true;$('status').textContent='กำลังโหลด '+direction;const next={};await Promise.all(parts.map(async part=>{next[part]=await Promise.all(DATA[direction][part].map(loadImage));}));if(token!==request)return;images=next;view=direction;index=0;loaded=true;$('play').disabled=false;$('play').textContent='เล่น';$('status').textContent='พรีวิว '+view+' · Trail เริ่มหลังฟันและจางเร็ว';for(const button of document.querySelectorAll('[data-view]'))button.classList.toggle('active',button.dataset.view===view);render();}
function tick(now){if(!playing)return;if(last===null)last=now;elapsed+=(now-last)*Number($('speed').value);last=now;while(elapsed>=timing[index]){elapsed-=timing[index];if(index===15){stop();render();return;}index++;render();}requestAnimationFrame(tick);}
$('play').onclick=()=>{if(!loaded)return;if(playing){stop();return;}if(index===15)index=0;playing=true;last=null;elapsed=0;$('play').textContent='หยุด';render();requestAnimationFrame(tick);};
$('frame').oninput=()=>{stop();index=Number($('frame').value);render();};$('previous').onclick=()=>{stop();index=Math.max(0,index-1);render();};$('next').onclick=()=>{stop();index=Math.min(15,index+1);render();};for(const id of ['head','body','weapon','trail'])$(id).onchange=render;for(const button of document.querySelectorAll('[data-view]'))button.onclick=()=>choose(button.dataset.view).catch(error=>{$('status').textContent='โหลดภาพไม่สำเร็จ';});choose('SE').catch(error=>{$('status').textContent='โหลดภาพไม่สำเร็จ';});
</script></html>'''
    (root/'review.html').write_text(template.replace('__DATA__',json.dumps(data)).replace('__TIMING__',json.dumps(timing)).replace('__PARTS__',json.dumps(PARTS)))
    print(json.dumps({'directions':4,'frames_per_direction':16,'external_dependencies':0,'bytes':(root/'review.html').stat().st_size}))


if __name__=='__main__':main()
