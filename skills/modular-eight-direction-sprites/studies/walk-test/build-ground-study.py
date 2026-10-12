"""Build v15 actual-contact review, equal-duration8/16 control and offline viewer."""
import base64,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'research/sprite-animation/ground-walk-sixteen-v15'
def uri(p):return 'data:image/png;base64,'+base64.b64encode(Path(p).read_bytes()).decode()
def gray(p):
 with Image.open(p) as original:im=original.convert('RGBA')
 bg=Image.new('RGBA',im.size,'#272727');bg.alpha_composite(im);return bg.convert('RGB')
def gif(fs,path,delays):
 strip=Image.new('RGB',(len(fs)*fs[0].width,fs[0].height))
 for i,f in enumerate(fs):strip.paste(f,(i*f.width,0))
 palette=strip.quantize(colors=256,method=Image.Quantize.MEDIANCUT);q=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in fs];q[0].save(path,save_all=True,append_images=q[1:],duration=delays,loop=0,disposal=2,optimize=False)
def main():
 source=json.loads((OUT/'source/source-ground.json').read_text());case=json.loads((OUT/'evidence/v15-ground-observations.json').read_text());report=json.loads((OUT/'check/v15-floor-report.json').read_text());manifest=json.loads((OUT/'candidate/manifest.json').read_text())
 files=[ROOT/f['image'] for f in case['frames']];overlays=[];comparison=[];pairs=[];(OUT/'check/overlays').mkdir(parents=True,exist_ok=True)
 for i,p in enumerate(files):
  overlay=gray(p);d=ImageDraw.Draw(overlay)
  for side,color in [('left','#ff9b34'),('right','#359aff')]:
   ys=[case['shared_scale']*s['same_xy_on_ground_projected'][1]+case['shared_translation_y_px'] for n,s in source['frames'][i]['soles'].items() if n.startswith('sole.'+side)]
   y=sum(ys)/len(ys);d.line((65,y,455,y),fill=color,width=2)
  for o in report['frames'][i]['observations']:
   color='#ff7f7f' if o.get('contact_floor_warning') else '#e9dc8e';d.rectangle(o['roi_xyxy'],outline=color,width=1)
   if o.get('lower_contour_y_px') is not None:
    x=(o['roi_xyxy'][0]+o['roi_xyxy'][2])/2;y=o['lower_contour_y_px'];d.ellipse((x-3,y-3,x+3,y+3),fill=color)
  d.text((8,8),f'{i+1}/16 | source {source["frames"][i]["time_seconds"]:.4f}s',fill='white');d.text((8,25),'source floor lanes / sole ROIs; diagnostic only',fill='white')
  op=OUT/'check/overlays'/f'{i:02}.png';overlay.save(op);overlays.append(op)
  control=files[(i//2)*2];combo=Image.new('RGB',(1024,540),'#272727');combo.paste(gray(control),(0,28));combo.paste(gray(p),(512,28));dr=ImageDraw.Draw(combo);dr.text((8,8),'8-FRAME SUBSET / SAME ART BANK',fill='white');dr.text((520,8),'16-FRAME TEST / SAME600ms',fill='white');comparison.append(combo)
  pair=Image.new('RGB',(1024,540),'#272727');pair.paste(gray(source['frames'][i]['dressed_path']),(0,28));pair.paste(gray(p),(512,28));ImageDraw.Draw(pair).text((8,8),f'SOURCE vs PAINT / slot{i+1}; intended phase is not proof of matching bones',fill='white');pairs.append(pair)
 gif(comparison,OUT/'eight-vs-sixteen.gif',manifest['gif_delays_ms']);gif([Image.open(p).convert('RGB') for p in overlays],OUT/'floor-review.gif',manifest['gif_delays_ms'])
 board=Image.new('RGB',(2048,4*288),'#272727')
 for i,f in enumerate(pairs):board.paste(f.resize((512,270)),(i%4*512,i//4*288))
 # Keep pair sizes useful: four rows each show the paired source/art above
 # the original full-size contact-sheet links, without recentering individual poses.
 board.save(OUT/'source-vs-paint.png')
 rejected=Image.open(OUT/'evidence/user-rejected-attempt1-slot5.png').convert('RGBA');bad=Image.new('RGBA',(512,512));bad.alpha_composite(rejected.resize((448,448)),(32,32));badbg=Image.new('RGBA',(512,512),'#272727');badbg.alpha_composite(bad)
 diagnostic=Image.new('RGB',(1536,550),'#272727');diagnostic.paste(badbg.convert('RGB'),(0,30));diagnostic.paste(gray(source['frames'][4]['cutaway_path']),(512,30));diagnostic.paste(gray(files[4]),(1024,30));d=ImageDraw.Draw(diagnostic)
 for x,text in [(8,'USER-REJECTED OLD SLOT5 / diagnostic crop'),(520,'ACTUAL SOURCE SLOT5 / LEFT orange, RIGHT blue'),(1032,'NEW SLOT5 / anatomy still needs review')]:d.text((x,8),text,fill='white')
 diagnostic.save(OUT/'slot5-recheck.png')
 data={'art':[uri(p) for p in files],'overlay':[uri(p) for p in overlays],'source':[uri(f['dressed_path']) for f in source['frames']], 'old8':[uri(ROOT/f'research/sprite-animation/continuity-v14/attempts/geometry-first/frames/{i:02}.png') for i in range(8)],'warnings':report['contact_warning_keys'],'anchors':[0,4,8,12]}
 template='''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>16-frame grounded walk review</title><style>body{background:#181b22;color:#eee;margin:0;padding:18px;font:16px/1.5 system-ui}main{max-width:1400px;margin:auto}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}figure{margin:0;background:#272727;padding:10px;min-width:0}img{width:100%;height:430px;object-fit:contain}button,select{font:inherit;padding:5px}input[type=range]{width:min(650px,90vw)}.warn{color:#ffce78}h1{font-size:23px}h2{font-size:17px}</style><main><h1>เดิน16เฟรม — ตรวจพื้นและเทียบ8เฟรม</h1><p class="warn">เป็นการทดสอบ ยังไม่รับรอง anatomy/contact/foot-lock · เท้าข้างใกล้/ไกลเป็นสองเส้นภาพของพื้นโลกเดียวกัน ไม่ใช่พื้นสองชั้น</p><button id="play">เล่น</button> <button id="next">ถัดไป</button> <select id="clock"><option value="600">600ms / รอบเดียวกัน</option><option value="1333">1333ms / source clock</option><option value="2400">2400ms / ดูช้า</option></select> <label><input type="checkbox" id="floor" checked>แสดงพื้นและROI</label><p><input type="range" id="phase" min="0" max="15" value="0"><output id="label"></output></p><p id="warning" class="warn"></p><div class="grid"><figure><h2>กระดูก/ฝ่าเท้าจริงในrig</h2><img id="source" alt="source rig"></figure><figure><h2>8เฟรมเลือกจากภาพชุดเดียวกัน</h2><img id="control" alt="eight-frame same-art control"></figure><figure><h2>16เฟรมใหม่</h2><img id="art" alt="new16-frame candidate"></figure></div><p>ไม่มีper-frame bbox fit; ใช้สเกลร่วมและแก้registrationทั้งแถว จุดanchor1/5/9/13ไม่ใช่การตรวจอิสระ ส่วนอีกเท้าในเฟรมเดียวกันยังตรวจแยก</p><details><summary>เทียบv14เดิมด้วย (เปลี่ยนภาพและregistration จึงไม่ใช่การเทียบจำนวนเฟรมอย่างเดียว)</summary><img id="old" alt="prior v14 candidate"></details><p>ตัวตรวจพื้นอ่านcontourจริงในROIที่คนเลือกและเทียบfloor projection ไม่อนุมานhidden joints/น้ำหนักจากภาพ ตรวจทั้งchainคู่ขาและsource phaseแยกต่างหาก</p></main><script>const data=DATA;let current=0,playing=false,start=0;const phase=document.querySelector('#phase');function show(i){current=(i+16)%16;phase.value=current;document.querySelector('#label').textContent='เฟรม '+(current+1)+' / source sample '+current*2.5;document.querySelector('#source').src=data.source[current];document.querySelector('#control').src=data.art[Math.floor(current/2)*2];document.querySelector('#art').src=(document.querySelector('#floor').checked?data.overlay:data.art)[current];document.querySelector('#old').src=data.old8[Math.floor(current/2)];document.querySelector('#warning').textContent=(data.warnings.includes(current)?'เครื่องมือเตือนความสัมพันธ์ฝ่าเท้ากับเส้นพื้น ต้องตรวจpose/ROI/identity เพิ่ม':'ยังไม่พบคำเตือนในROIที่วัด ไม่ใช่PASSของทั้งตัว')+(data.anchors.includes(current)?' · เฟรมนี้มีanchorที่ใช้calibrate ห้ามนับเป็นvalidationของจุดเดียวกัน':'');}phase.oninput=()=>{playing=false;document.querySelector('#play').textContent='เล่น';show(+phase.value)};document.querySelector('#next').onclick=()=>{playing=false;document.querySelector('#play').textContent='เล่น';show(current+1)};document.querySelector('#floor').onchange=()=>show(current);document.querySelector('#play').onclick=()=>{playing=!playing;start=performance.now()-current*(+document.querySelector('#clock').value/16);document.querySelector('#play').textContent=playing?'หยุด':'เล่น'};document.querySelector('#clock').onchange=()=>{start=performance.now()-current*(+document.querySelector('#clock').value/16)};function tick(t){if(playing)show(Math.floor((t-start)/(+document.querySelector('#clock').value/16))%16);requestAnimationFrame(tick)}show(0);requestAnimationFrame(tick);</script></html>'''
 (OUT/'frame-review.html').write_text(template.replace('DATA',json.dumps(data)));print('GROUND_STUDY frame16 UI, equal-duration8/16 comparison, source pairs and floor overlays')
if __name__=='__main__':main()
