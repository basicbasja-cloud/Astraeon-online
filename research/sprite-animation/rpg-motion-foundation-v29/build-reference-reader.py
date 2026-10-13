#!/usr/bin/env python3
"""Read-only native-clock browser for actual creator GIF captures. No SVG."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
captures=[]
for folder in sorted((ROOT/'captures').glob('kaykit-preview-*')):
 c=json.loads((folder/'capture.json').read_text())
 captures.append({'name':folder.name,'duration_ms':c['duration_ms'],'source_url':c['source_url'],'source_sha256':c['source_sha256'],'frames':[dict(f,url=str((folder/f['file']).relative_to(ROOT))) for f in c['frames']]})
html='''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>RPG motion reference reader v29</title><style>
body{background:#171d28;color:#e8edf6;font:16px system-ui;margin:0;padding:24px;max-width:1100px;margin:auto}h1{font-size:26px;margin-top:0}a{color:#9aceff}button,select{font:inherit;padding:8px 12px;color:#e8edf6;background:#293448;border:1px solid #526078;border-radius:6px}button{cursor:pointer}.row{display:flex;gap:12px;flex-wrap:wrap;margin:18px 0;align-items:center}img{display:block;max-width:100%;width:900px;background:#262d39;image-rendering:pixelated}input{width:100%}pre{white-space:pre-wrap;color:#bacade;background:#222b3b;padding:14px;overflow-wrap:anywhere}small{color:#bacade}nav{line-height:2}
</style><h1>RPG motion reference reader</h1>
<p>เฟรมจริงจาก preview ผู้สร้าง • Native PTS/exposure • มี montage/title changes • ยังไม่ใช่ motion ที่ตรวจ anatomy/contact ครบ</p>
<nav><a href="README.md">ชุดวิจัย</a> · <a href="KNOW-HOW.md">Know-how</a> · <a href="MOTION-RECIPES.md">99 motion recipes</a> · <a href="CLIP-BROWSER.md">71 source clips</a> · <a href="SOURCES.md">92 sources</a></nav>
<div class="row"><label>Capture <select id="capture"></select></label><label>Speed <select id="speed"><option value="1">Native 1x</option><option value="0.25">Inspection 0.25x</option></select></label><button id="prev">← Previous</button><button id="play">Play once</button><button id="next">Next →</button></div>
<img id="frame" alt="Actual captured creator preview frame"><div class="row"><input id="seek" type="range" min="0" value="0" aria-label="Frame ordinal"></div>
<pre id="meta"></pre><small>เล่นคลิปครั้งเดียวและค้างเฟรมสุดท้าย ไม่สร้าง loop ข้าม title/cut; 0.25x เปลี่ยน review speed เท่านั้น ไม่เปลี่ยน source timing</small>
<script>const DATA=__DATA__;let source=0,index=0,running=false,base=0,started=0;const $=id=>document.getElementById(id);const clip=()=>DATA[source];
DATA.forEach((c,i)=>{const o=document.createElement('option');o.value=i;o.textContent=c.name+' / '+c.frames.length+' exposures';$('capture').appendChild(o)});
function draw(){const c=clip(),f=c.frames[index];$('frame').src=f.url;$('seek').max=c.frames.length-1;$('seek').value=index;$('play').textContent=running?'Pause':'Play once';$('meta').textContent=`${c.name}\nFrame ${index+1}/${c.frames.length} • Source ordinal ${f.source_index}\nPTS ${f.source_pts_ms}ms • Exposure ${f.duration_ms}ms • Elapsed ${f.time_ms}ms\nFile SHA256 ${f.sha256}\nSource ${c.source_url}\nSemantic/contact/anatomy review: pending; capture is a montage`}
function pause(){running=false;draw()}
function select(i){index=Math.max(0,Math.min(clip().frames.length-1,i));pause()}
function advance(elapsed){let n=0;while(n+1<clip().frames.length&&clip().frames[n+1].time_ms<=elapsed)n++;index=n;if(elapsed>=clip().duration_ms)running=false;draw()}
function tick(now){if(running){advance(base+(now-started)*Number($('speed').value));if(running)requestAnimationFrame(tick)}}
$('capture').onchange=()=>{source=Number($('capture').value);select(0)};
$('seek').oninput=()=>select(Number($('seek').value));$('prev').onclick=()=>select(index-1);$('next').onclick=()=>select(index+1);
$('play').onclick=()=>{if(running)return pause();if(index===clip().frames.length-1)index=0;base=clip().frames[index].time_ms;started=performance.now();running=true;draw();requestAnimationFrame(tick)};
$('speed').onchange=()=>pause();draw();window.referenceReader={get state(){return {source,index,running}},select,advance,data:DATA};</script></html>'''
(ROOT/'reference-reader.html').write_text(html.replace('__DATA__',json.dumps(captures,separators=(',',':'))))
print(json.dumps({'captures':len(captures),'actual_frames':sum(len(c['frames']) for c in captures),'native_clock':True,'svg':False}))
