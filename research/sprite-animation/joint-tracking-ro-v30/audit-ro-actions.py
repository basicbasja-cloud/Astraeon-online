#!/usr/bin/env python3
"""Bounded public RO action probes with persistent resume journal.
Community APNG render, NOT official client timing or a recovered skeleton.
Raw raster cache stays local; publish timing/hash/coverage analysis and bounded boards.
"""
import concurrent.futures,hashlib,io,json,time
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from PIL import Image,ImageSequence
ROOT=Path(__file__).resolve().parent
LABELS=['stand','walk','sit','pickup','combat_ready','attack','hurt','provider_frozen_1','dead','provider_frozen_2','attack_variant_1','attack_variant_2','attack_variant_3']
DIRS=['S','SW','W','NW','N','NE','E','SE']
def requests():
 jobs=[]
 for gender in ('male','female'):
  for block in range(13):
   for direction in range(8):jobs.append({'job':1,'gender':gender,'block':block,'direction':direction})
 for job in (0,2,3,4,5,6):
  for block in range(13):jobs.append({'job':job,'gender':'male','block':block,'direction':7})
 # Full indexed player class-family snapshot at one declared direction/gender.
 classes=json.loads((ROOT/'local-cache/ro-classes.json').read_text())
 for job in sorted({c['renderId'] for c in classes}):
  for block in range(13):
   q={'job':job,'gender':'male','block':block,'direction':7}
   if q not in jobs:jobs.append(q)
 for block in range(5):
  for direction in range(8):jobs.append({'job':1002,'gender':'monster','block':block,'direction':direction})
 return jobs
def probe(q):
 name=f"job{q['job']}-{q['gender']}-action{q['block']*8+q['direction']}";r=dict(q,id=name)
 params={'job':q['job'],'action':q['block']*8+q['direction'],'enableShadow':'false','canvas':'256x256+128+220'}
 if q['gender']!='monster':params.update(gender=q['gender'],head=1,headdir='straight')
 url='https://assets.latam-tools.com.br/image?'+urlencode(params);r['url']=url
 try:
  with urlopen(Request(url,headers={'User-Agent':'AstraeonBoundedAnimationResearch/1.0'}),timeout=18) as f:data=f.read(2_000_000)
  frames=[];pts=0;sequence=hashlib.sha256();unique=set()
  with Image.open(io.BytesIO(data)) as im:
   size=im.size
   for i,f in enumerate(ImageSequence.Iterator(im)):
    rgba=f.convert('RGBA');pixels=rgba.tobytes();ph=hashlib.sha256(pixels).hexdigest();duration=f.info.get('duration');sequence.update(pixels);unique.add(ph)
    frames.append({'index':i,'source_pts_ms':pts,'duration_ms':duration,'rgba_sha256':ph,'bbox':rgba.getbbox()})
    pts=pts+duration if duration and pts is not None else None
  file=ROOT/'local-cache/ro-apng'/ (name+'.png');file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes(data)
  r.update(status='decoded',file=str(file.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),canvas=list(size),frames=frames,duration_ms=pts,unique_drawings=len(unique),sequence_rgba_sha256=sequence.hexdigest(),direction_label=DIRS[q['direction']],action_label=LABELS[q['block']] if q['gender']!='monster' else ['idle','walk','attack','hurt','dead'][q['block']],clock_authority='Community renderer APNG exposure, not original client/action-speed truth',anatomy_pass=False)
 except Exception as e:r.update(status='failed',error=str(e)[:240])
 time.sleep(.10);return r
def main():
 journal=ROOT/'ro-probe-journal.jsonl';known={}
 if journal.exists():
  for line in journal.read_text().splitlines():
   r=json.loads(line);known[r['id']]=r
 pending=[]
 for q in requests():
  id=f"job{q['job']}-{q['gender']}-action{q['block']*8+q['direction']}"
  if id not in known:pending.append(q)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(probe,pending):
   with journal.open('a') as stream:stream.write(json.dumps(r,separators=(',',':'))+'\n')
   known[r['id']]=r
 rows=list(known.values());groups=[]
 for gender in ('male','female'):
  for block in range(13):
   bank=[r for r in rows if r['job']==1 and r['gender']==gender and r['block']==block and r['status']=='decoded'];same={}
   for r in bank:same.setdefault(r['sequence_rgba_sha256'],[]).append(r['direction_label'])
   groups.append({'job':1,'gender':gender,'block':block,'provider_label':LABELS[block],'requested_directions':8,'decoded':len(bank),'distinct_decoded_sequences':len(same),'identical_direction_groups':list(same.values())})
 classes=json.loads((ROOT/'local-cache/ro-classes.json').read_text())
 report={'schema':'fresh-bounded-ro-action-audit-v1','provider':'ragassets public community renderer','expected_probes':len(requests()),'decoded':sum(r['status']=='decoded' for r in rows),'failed':sum(r['status']=='failed' for r in rows),'direction_order':DIRS,'requests':rows,'direction_reuse':groups,'indexed_player_class_rows':len(classes),'class_family_render_ids':sorted({c['renderId'] for c in classes}),'family_audit_scope':'All indexed renderIDs, male SE,13providerblocks; Swordman additionally both genders/all8directions; Poring all5blocks/all8directions. Not every class/gender/direction/weapon/item/client combination.','all_RO_classes_or_clients_audited':False,'source_art_in_original_shipping_assets':False,'skeleton_recovered':False}
 (ROOT/'ro-action-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('expected_probes','decoded','failed')}))
if __name__=='__main__':main()
