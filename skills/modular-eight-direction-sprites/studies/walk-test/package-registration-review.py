"""Pack captured native runtime frames; audit clocks, hashes and source links."""
import hashlib,importlib.util,json,gzip
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'research/sprite-animation/registered-walk-attack-v21'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 sp=importlib.util.spec_from_file_location('walk_build',Path(__file__).with_name('build-registered-walk.py'));m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 browser=json.loads((OUT/'evidence/browser-report.json').read_text());paint=json.loads((OUT/'attack/evidence/painted-attack.json').read_text());images=[];empty_fx=[];active=[]
 for row in browser['capture']:
  name=f'{row["time_ms"]:04}.png';p=OUT/'attack/capture'/name;fx=OUT/'attack/fx'/name;assert sha(p)==row['capture_sha256'];assert sha(fx)==row['fx_sha256'];images.append(Image.open(p).convert('RGBA'));a=np.array(Image.open(fx).convert('RGBA'))[:,:,3];occupancy=int((a>0).sum())
  assert (occupancy>0)==row['fx_active']
  (active if occupancy else empty_fx).append(row['time_ms'])
 m.clip(OUT/'attack/SE/attack-with-trail',images,[20]*40,False)
 # Explicit repeating review version includes1200ms settled idle; never changes
 # the one-shot clock or adds a gameplay return edge.
 m.clip(OUT/'attack/SE/attack-loop-demo',images+[images[-1]],[20]*40+[1200],True)
 source=json.loads((OUT/'attack/source-palm-fixed/source-index.json').read_text())
 for v in ['SE','NE','NW','SW']:
  records=[r for r in source['records'] if r['view']==v];ims=[]
  for r in records:assert sha(ROOT/r['image'])==r['sha256'];ims.append(Image.open(ROOT/r['image']).convert('RGBA'))
  m.clip(OUT/'attack/source-palm-fixed'/v/'source-attack',ims,[r['duration_ms'] for r in records],False)
 formats=[]
 for path in sorted(OUT.rglob('*.gif'))+sorted(OUT.rglob('*.png')):
  with Image.open(path) as im:
   if getattr(im,'n_frames',1)==1:continue
   times=[]
   for i in range(im.n_frames):im.seek(i);times.append(im.info['duration'])
   expected=2000 if 'loop-demo' in path.name else 600 if '600ms' in path.name else 800
   assert abs(sum(times)-expected)<1e-5,(str(path),times)
   formats.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'decoded_frame_count':im.n_frames,'decoded_exposures_ms':times,'total_ms':sum(times),'gif_loop':im.info.get('loop') if path.suffix=='.gif' else None,'scope':'Decoded container presentation count may merge equal body/FX samples; body retains8source-authored poses.'})
 for j,views in enumerate([['S','SE'],['E','NE'],['N','NW'],['W','SW']]):
  sheet=Image.new('RGBA',(2048,1072),'#272727');d=ImageDraw.Draw(sheet)
  for n,v in enumerate(views):
   d.text((10,n*536+6),v+' / registered actual pixels,8frames / REVIEW_REQUIRED',fill='white')
   for i in range(8):
    frame=Image.open(OUT/'walk'/v/'frames'/f'{i:02}.png').convert('RGBA').resize((512,512));frame=frame.resize((256,256));sheet.alpha_composite(frame,(i%4*256,n*536+i//4*256+24))
    src=ROOT/'research/sprite-animation/eight-walk-factory-v20/source-phase12'/v/f'{i:02}/dressed-owner.png';sheet.alpha_composite(Image.open(src).convert('RGBA').resize((256,256)),(1024+i%4*256,n*536+i//4*256+24))
  sheet.save(OUT/'evidence'/f'walk-source-review-{j}.png')
 # Observational source comparison stays research-only, outside character bank.
 ro=ROOT/'research/sprite-animation/motion-reference-v6/ro/attack-SE';cap=json.loads((ro/'capture.json').read_text());board=Image.new('RGBA',(9*256,560),'#272727');d=ImageDraw.Draw(board)
 for i,f in enumerate(cap['frames']):
  ref=Image.open(ro/f['file']).convert('RGBA');ref=ref.resize((ref.width*2,ref.height*2),Image.Resampling.NEAREST);board.alpha_composite(ref,(i*256+(256-ref.width)//2,24));d.text((i*256+6,6),f'RO{i+1} / {f.get("duration_ms",100)}ms',fill='white')
 for i,r in enumerate(paint['frames']):board.alpha_composite(Image.open(ROOT/r['image']).convert('RGBA').resize((256,256)),(i*256,300));d.text((i*256+6,278),f'OURS{i+1} / {r["duration_ms"]}ms',fill='white')
 board.save(OUT/'evidence/RO-SE-attack-observation.png')
 save(OUT/'evidence/decoded-format-clocks.json',formats);save(OUT/'evidence/FX-export-check.json',{'source':'Actual browser-rendered separate runtime FX','capture_samples':40,'sample_exposure_ms':20,'body_pose_count':8,'active_fx_sample_times_ms':active,'empty_fx_sample_times_ms':empty_fx,'expiry_ms':430,'cancel_checked':True,'one_shot_duration_ms':800,'loop_demo_duration_ms':2000,'scope':'Observed blade-span interpolation is authored; not recovered continuous painted weapon motion or force simulation.'})
 # Lossless preserve export log; do not invent a paper/source inspection receipt.
 for name,src in [('source-export','/tmp/astraeon-v21-source.log'),('palm-source-export','/tmp/astraeon-v21-palm-source.log'),('source-reopen','/tmp/astraeon-v21-source-reopen.log')]:
  log=Path(src);(OUT/'evidence'/(name+'.log.gz')).write_bytes(gzip.compress(log.read_bytes(),mtime=0))
 print('PACKAGED_CLOCKS',len(formats),'FX_ACTIVE_SAMPLES',active)
if __name__=='__main__':main()
