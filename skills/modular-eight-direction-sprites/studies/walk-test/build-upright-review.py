"""Compare source/old/new and retained RO at one clock, with explicit pose limits."""
import argparse,base64,hashlib,json
from pathlib import Path
from PIL import Image
def main():
 p=argparse.ArgumentParser();p.add_argument('--study',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
 repo=Path(__file__).resolve().parents[4];g=json.loads((a.study/'source/source-ground.json').read_text())
 m=json.loads((repo/'research/sprite-animation/leg-ownership-v16/uniform-review/manifest.json').read_text())
 for f in g['frames']:
  if hashlib.sha256(Path(f['dressed_path']).read_bytes()).hexdigest()!=f['dressed_sha256']:raise ValueError('Changed source render')
 for f in m['source_frames']:
  if hashlib.sha256(Path(f['path']).read_bytes()).hexdigest()!=f['sha256']:raise ValueError('Changed rejected reference bank')
 banks=[('RO reference (8; approximate phase windows)',[repo/'research/sprite-animation/motion-reference-v6/ro/walk-W'/f'{(i+2)%8:04}.png' for i in range(8)]),('Original upright source (16)',[Path(f['dressed_path']) for f in g['frames']]),('Rejected v16 (16)',[Path(f['path']) for f in m['source_frames']]),('New art: UNAPPROVED (8)',sorted((a.candidate/'frames').glob('*.png')))]
 if [len(files) for _,files in banks]!=[8,16,16,8]:raise ValueError('Expected actual comparison banks 8/16/16/8')
 data=[];receipt=[]
 for label,files in banks:
  urls=[];entries=[]
  for file in files:
   raw=file.read_bytes();urls.append('data:image/png;base64,'+base64.b64encode(raw).decode());entries.append({'path':str(file),'sha256':hashlib.sha256(raw).hexdigest(),'size':list(Image.open(file).size)})
  data.append({'label':label,'urls':urls});receipt.append({'label':label,'frames':entries,'per_frame_fit':False})
 html='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Upright walk v17 review</title><style>body{margin:20px;background:#181a20;color:#eee;font:16px system-ui}button,select,input{font:inherit;margin:6px;max-width:90%}.banks{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:12px}.bank{min-width:0;background:#272727;border:1px solid #555;padding:8px}.bank img{height:300px;max-width:100%;object-fit:contain;display:block;margin:auto}.bank:first-child img{image-rendering:pixelated}p{max-width:1000px;line-height:1.5}.status{color:#ffc571}#phase{width:300px}</style><h1>เดินตัวตรง / Upright walk v17</h1><p class="status">New art is UNAPPROVED. Source checks do not certify painted leg owners or natural movement.</p><p>เทียบที่ clock เดียวกัน; RO phase windows เป็นการจัดด้วยสายตา ไม่ใช่ skeleton ที่กู้คืนมาได้ ทุก bank ใช้ canvas เดิมและ scale คงที่ตลอดคลิป ไม่ fit แต่ละเฟรม ขนาดบนจอไม่ใช่การ align กระดูกข้ามตัวละคร</p><button id="play">Pause</button><button id="back">Previous</button><button id="next">Next</button><select id="clock"><option value="800">800 ms equal-cycle control</option><option value="1600">1600 ms slow review</option><option value="600">600 ms equal-cycle / RO converter clock</option></select><input id="phase" type="range" min="0" max="15" value="0"><output id="readout"></output><div class="banks" id="banks"></div><p>ต้นแบบใหม่มี 16 phase samples; ภาพใหม่ทดลอง 8 โพส ไม่ใช่ downsample ของภาพเก่า RO ที่เก็บไว้มี8×75ms; การเล่น800msตรงนี้เปลี่ยนความเร็ว reference เพื่อเทียบ ไม่ใช่ native timing. ใบหน้าคงที่อย่างเดียวไม่ยืนยันการเดิน. ภาพวาดยังไม่มี replacement parts ครบ.</p><script>const data=DATA;let phase=0,playing=true,start=performance.now(),duration=800;const slider=document.querySelector('#phase');data.forEach(b=>{const el=document.createElement('div');el.className='bank';const title=document.createElement('h3');title.textContent=b.label;const img=document.createElement('img');img.alt=b.label;el.append(title,img);document.querySelector('#banks').append(el);b.img=img;});function show(){data.forEach(b=>{const i=Math.min(b.urls.length-1,Math.floor(phase*b.urls.length/16));b.img.src=b.urls[i];b.img.dataset.frame=i;});slider.value=phase;document.querySelector('#readout').textContent=' source phase '+(phase+1)+'/16';}function stop(){playing=false;document.querySelector('#play').textContent='Play';}document.querySelector('#play').onclick=()=>{playing=!playing;start=performance.now()-phase*duration/16;document.querySelector('#play').textContent=playing?'Pause':'Play';};document.querySelector('#next').onclick=()=>{stop();phase=(phase+1)%16;show();};document.querySelector('#back').onclick=()=>{stop();phase=(phase+15)%16;show();};slider.oninput=()=>{stop();phase=Number(slider.value);show();};document.querySelector('#clock').onchange=e=>{duration=Number(e.target.value);start=performance.now()-phase*duration/16;};function tick(t){if(playing){phase=Math.floor(((t-start)%duration)/duration*16);show();}requestAnimationFrame(tick);}show();requestAnimationFrame(tick);</script>'''.replace('DATA',json.dumps(data))
 (a.study/'frame-review.html').write_text(html)
 (a.study/'evidence/comparison-banks.json').write_text(json.dumps({'banks':receipt,'ro_phase_mapping':[2,3,4,5,6,7,0,1],'alignment_scope':'Approximate visual phase windows only. No recovered RO skeleton or cross-character joint accuracy. Uniform clock changes reference speed.'},indent=2)+'\n')
 frames=[Image.open(f['dressed_path']).convert('RGBA') for f in g['frames']];opaque=[]
 for f in frames:
  bg=Image.new('RGBA',f.size,'#272727');bg.alpha_composite(f);opaque.append(bg.convert('RGB').quantize(colors=256))
 opaque[0].save(a.study/'upright-source-800ms.gif',save_all=True,append_images=opaque[1:],duration=50,loop=0,disposal=2)
 print('UPRIGHT_REVIEW',len(receipt),'banks')
if __name__=='__main__':main()
