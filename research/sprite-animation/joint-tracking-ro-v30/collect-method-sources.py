"""Retrieve public primary method documents with hashes; no provider inference."""
import concurrent.futures,hashlib,json
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parent
SOURCES=[
 ('cotracker','https://raw.githubusercontent.com/facebookresearch/co-tracker/main/README.md'),
 ('tapir','https://raw.githubusercontent.com/google-deepmind/tapnet/main/README.md'),
 ('dwpose','https://raw.githubusercontent.com/IDEA-Research/DWPose/main/README.md'),
 ('rtmpose','https://raw.githubusercontent.com/open-mmlab/mmpose/main/projects/rtmpose/README.md'),
 ('blender-ik','https://docs.blender.org/manual/en/latest/animation/constraints/tracking/ik_solver.html'),
 ('mixamo-faq','https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html'),
 ('rrl-act','https://ragnarokresearchlab.github.io/file-formats/act/'),
 ('rrl-spr','https://ragnarokresearchlab.github.io/file-formats/spr/'),
 ('amass','https://amass.is.tue.mpg.de/')]
def fetch(row):
 name,url=row
 try:
  with urlopen(Request(url,headers={'User-Agent':'AstraeonResearch/1.0'}),timeout=30) as f:raw=f.read(4_000_000);status=f.status
  path=ROOT/'local-cache'/('method-'+name+'.txt');path.write_bytes(raw)
  return {'id':name,'url':url,'status':status,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'cache':str(path.relative_to(ROOT)),'retrieved_utc_date':'2026-10-13','full_text_read':False,'model_or_motion_inference_executed':False}
 except Exception as e:return {'id':name,'url':url,'error':str(e)[:160]}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(fetch,SOURCES))
(ROOT/'method-source-receipts.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'retrieved':sum('sha256' in r for r in rows),'failed':[r['id'] for r in rows if 'error' in r]}))
