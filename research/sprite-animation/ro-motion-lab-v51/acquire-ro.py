"""Bounded public research capture; originals remain outside the repository."""
from pathlib import Path
import urllib.request,urllib.parse,json,hashlib,time,concurrent.futures,io
from PIL import Image
P=Path(__file__).resolve().parent;CACHE=Path('/workspace/work/ro-v51/captures');CACHE.mkdir(parents=True,exist_ok=True)
actors=[('sword-m',1,'male'),('sword-f',1,'female'),('mage-f',2,'female'),('thief-m',6,'male')]
jobs=[]
for name,job,gender in actors:
 for block in range(13):
  for direction in range(8):jobs.append((name,job,gender,block,direction,0,0))
for block in range(13):
 for direction in range(8):jobs.append(('sword-m',1,'male',block,direction,1,0))
for block in [5,10,11,12]:
 for direction in range(8):jobs.append(('sword-m',1,'male',block,direction,0,2))
def acquire(task):
 name,job,gender,block,direction,head,weapon=task;key=f'{name}-b{block:02}-d{direction}-h{head}-w{weapon}';f=CACHE/(key+'.png')
 q={'job':job,'gender':gender,'head':head,'weapon':weapon,'action':block*8+direction,'headdir':'straight','enableShadow':'false','canvas':'240x260+120+225'};url='https://assets.latam-tools.com.br/image?'+urllib.parse.urlencode(q)
 record={'key':key,'actor':name,'job':job,'gender':gender,'block':block,'direction':direction,'head':head,'weapon':weapon,'url':url,'cache':str(f)}
 try:
  if not f.exists():
   data=urllib.request.urlopen(url,timeout=40).read();Image.open(io.BytesIO(data)).verify();f.write_bytes(data);time.sleep(.12)
  data=f.read_bytes();im=Image.open(f);rgba=[];durations=[];nonempty=[]
  for i in range(getattr(im,'n_frames',1)):
   im.seek(i);frame=im.convert('RGBA');alpha=frame.getchannel('A');nonempty.append(alpha.getbbox() is not None);canonical=Image.new('RGBA',frame.size);canonical.alpha_composite(frame);rgba.append(hashlib.sha256(canonical.tobytes()).hexdigest());durations.append(im.info.get('duration'))
  seq=hashlib.sha256(json.dumps([im.size,rgba,durations],separators=(',',':')).encode()).hexdigest();record.update(status='decoded',file_sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),canvas=list(im.size),frames=len(rgba),frame_sha256=rgba,durations_ms=durations,sequence_sha256=seq,all_frames_nonempty=all(nonempty))
 except Exception as e:record.update(status='ERROR',error=str(e))
 return record
records=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for item in pool.map(acquire,jobs):
  records.append(item)
  if len(records)%32==0:print('CAPTURED',len(records),'/',len(jobs),flush=True)
(P/'ro-capture-ledger.json').write_text(json.dumps({'provider':'Public ragassets community renderer, not official gameplay capture','date':'2026-10-15','request_count':len(jobs),'head0_scope':'Observed head-suppressed version compared with head1 and resolver source; host revision not asserted','gameplay_pacing_verified':False,'original_art_redistributed':False,'captures':records},indent=2)+'\n');print('DONE',len(records),'errors',sum(r['status']=='ERROR' for r in records))
