"""One neutral adapter / two external-source curves. No per-frame art fitting."""
from pathlib import Path
import json,hashlib
from PIL import Image
P=Path(__file__).resolve().parent;root=P.parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=P/'inputs/family-pickup-eight.png';neutral=Image.open(source).crop((1152,512,1536,1024));neutral.save(P/'inputs/neutral-family.png')
plate=Image.new('RGBA',(1536,1024))
for i in range(8):plate.paste(neutral,(i%4*384,i//4*512))
plate.save(P/'inputs/neutral-registration-guide.png')
for name in ['sprite-mesh-player.js','sprite-clip-clock.cjs']:(P/'inputs'/name).write_bytes((root/'tools'/name).read_bytes())
adapter={'width':384,'height':512,'grid_px':16,'texture':'inputs/neutral-family.png','texture_sha256':sha(P/'inputs/neutral-family.png'),'bands':[{'y':0,'channel':'head'},{'y':192,'channel':'head'},{'y':256,'channel':'chest'},{'y':384,'channel':'hips'},{'y':432,'channel':'fixed'},{'y':512,'channel':'fixed'}], 'influences':[{'center':[151,337],'radius':[20,42],'support_y':[192,224,400,432],'channel':'left_hand'},{'center':[291,337],'radius':[20,42],'support_y':[192,224,400,432],'channel':'right_hand'}], 'scope':'Rear N small-motion texture deformation only. One rest adapter, rigid complete head region, fixed distal support; not new out-of-plane art, hidden anatomy, sitting or a complete head/body swap bank.'}
records=json.loads((P.parent/'pickup-contact-v49/references/kaykit-captures.json').read_text())['frames'];clips={}
for source_clip,name,total,loop,gain in [('Idle_A','idle.relaxed',1600,True,4.0),('Hit_A','hit.light',670,False,1.6)]:
 rows=[x for x in records if x['clip']==source_clip and x['view']=='N'];base=rows[0];poses=[]
 for sample in rows:
  delta={n:[(sample['actual_source_bones'][n]['xy'][j]-base['actual_source_bones'][n]['xy'][j])*gain for j in range(2)] for n in ['head','chest','hips','wrist.l','wrist.r','foot.l','foot.r']}
  # Declared in-place adaptation: subtract source foot projection translation.
  floor=[(delta['foot.l'][j]+delta['foot.r'][j])/2 for j in range(2)]
  pose={key:[delta[bone][j]-floor[j] for j in range(2)] for key,bone in [('head','head'),('chest','chest'),('hips','hips')]}
  # Wrist displacement relative to moving chest; reduced for a relaxed family pose.
  for key,bone in [('left_hand','wrist.l'),('right_hand','wrist.r')]:pose[key]=[(delta[bone][j]-delta['chest'][j])*.5 for j in range(2)]
  poses.append(pose)
 boundaries=[round(i*total/16/10)*10 for i in range(17)];durations=[boundaries[i+1]-boundaries[i] for i in range(16)]
 clips[name]={'durations':durations,'loop':loop,'poses':poses,'source_clip':source_clip,'source_capture_times_seconds':[r['source_time_seconds'] for r in rows], 'source_native_duration_seconds':rows[0]['source_duration_seconds'],'source_projection_gain':gain,'retiming_total_ms':total,'adaptation':'One constant projection gain per clip; source foot projection translation removed for in-place support; static rest weights. Wrist residual reduced by0.5; source poses are references, not an exact retarget or physical rig.'}
data={'adapter':adapter,'clips':clips,'source_capture_sha256':sha(P.parent/'pickup-contact-v49/references/kaykit-captures.json')};(P/'mesh-contract.json').write_text(json.dumps(data,indent=2)+'\n')
html='''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>ท่าเคลื่อนไหวเพิ่มเติม</title><style>body{font:16px system-ui;background:#20252d;color:#eee;margin:24px}canvas{background:#292b30;width:384px;max-width:100%;height:auto}button,select,input{font:inherit;margin:6px}p{max-width:850px;line-height:1.5}</style><h1>หายใจ / สะดุ้ง · 16 เฟรม</h1><p>เมช 2D จากภาพตัวละครเดิม · ควบคุมจังหวะด้วยคลิปอ้างอิงภายนอก · ใช้สำหรับท่าขยับเล็กในมุมหลังนี้</p><canvas id="sprite"></canvas><p><select id="clip"><option value="idle.relaxed">ยืนผ่อนคลาย</option><option value="hit.light">สะดุ้งเมื่อโดนโจมตีเบา</option></select><button id="play">เล่น</button><button id="prev">ก่อนหน้า</button><button id="next">ถัดไป</button><input id="frame" type="range" min="0" max="15" value="0"><select id="speed"><option value="1">1×</option><option value="0.25">0.25×</option></select><label><input id="loop" type="checkbox" checked>วนดู</label></p><p id="status"></p><p><a href="../pickup-contact-v49/review.html">ดูท่าก้ม16เฟรมก่อน–หลัง</a></p><script src="inputs/sprite-mesh-player.js"></script><script src="inputs/sprite-clip-clock.cjs"></script><script>
const DATA=__DATA__,$=id=>document.getElementById(id);let mesh,clock,k=0,last=0,name='idle.relaxed';function draw(){mesh.draw(DATA.clips[name].poses[k]);$('frame').value=k;$('status').textContent=`${name} · เฟรม${k+1}/16 · ${DATA.clips[name].durations[k]}ms`;$('play').textContent=clock.running?'หยุด':'เล่น'}function select(i){k=i;clock.cancel();draw()}function choose(value){name=value;clock=new SpriteClipClock({...DATA.clips[name],loop:$('loop').checked});k=0;draw()}
$('clip').onchange=()=>choose($('clip').value);$('frame').oninput=()=>select(+$('frame').value);$('prev').onclick=()=>select(Math.max(0,k-1));$('next').onclick=()=>select(Math.min(15,k+1));$('play').onclick=()=>{if(clock.running)clock.cancel();else{clock.clip.loop=$('loop').checked;clock.start()}last=performance.now();draw()};
function tick(t){if(clock&&clock.running){k=clock.advance((t-last)*+$('speed').value).frame;draw()}last=t;requestAnimationFrame(tick)}const im=new Image();im.onload=()=>{mesh=new SpriteMesh($('sprite'),im,DATA.adapter);choose(name);window.READY=true;requestAnimationFrame(tick)};im.src=DATA.adapter.texture;
window.study={data:DATA,choose,select,get mesh(){return mesh},get clock(){return clock},frame(clip,i){mesh.draw(DATA.clips[clip].poses[i]);return $('sprite').toDataURL('image/png')}};
</script></html>'''
(P/'review.html').write_text(html.replace('__DATA__',json.dumps(data,separators=(',',':'))));print('Two16-exposure clips built from one rest adapter')
