"""User package: ready PNGs, executable bounded checks and selected authoring examples."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil,copy,importlib.util,zipfile,io
P=Path(__file__).resolve().parent;ROOT=P.parents[2];OUT=Path('/codex/browser/projectless/0001-branch-research-handoff/output');KIT=ROOT/'work/final-delivery';cases=P.parent;D=json.loads((P/'catalog.json').read_text());final=json.loads((P/'final-review.json').read_text());assert final['finite_core_review_pass'];KIT.mkdir(parents=True,exist_ok=True);preferred_output=OUT
try:OUT.mkdir(parents=True,exist_ok=True)
except PermissionError:OUT=P/'delivery';OUT.mkdir(exist_ok=True)
(P/'delivery-location.json').write_text(json.dumps({'requested':str(preferred_output),'actual':str(OUT),'reason':'Requested projectless output root is not writable in attached Cloud OS; deliver through authorized research branch.'if OUT!=preferred_output else'Projectless output available'},indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def cp(src,dst):dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
cp(P/'core-family-review.html',OUT/'astraeon-motion-review.html')
for a,d in D['actions'].items():
 for v,c in d['clips'].items():
  for f in c['frames']:assert sha(P/f['path'])==f['sha256'];cp(P/f['path'],KIT/f['path'])
for n in ['catalog.json','final-review.json','coverage-review.json','player-qa.json','codec-rounding-review.json','KNOW-HOW.md','REFERENCES.md']:cp(P/n,KIT/n)
for n in ['sprite-coverage-review.py','sprite-motion-review.py','sprite-contact-review.py','sprite-layer-contact-review.py','sprite-foot-binding.py','sprite-clip-clock.cjs','sprite-mesh-player.js','sprite-articulated-player.js','sprite-segmented-player.js','sprite-segment-ownership.js','sprite-pose-morph.js']:cp(ROOT/'tools'/n,KIT/'tools'/n)
for n in ['ro-capture-ledger.json','direction-policy.json','ro-direction-analysis.json']:cp(cases/'ro-motion-lab-v51'/n,KIT/n)
# Copy profiles verified against actual common-canvas PNGs.
shutil.copytree(P/'profiles',KIT/'profiles',dirs_exist_ok=True)
cp(P/'profile-provenance.json',KIT/'profile-provenance.json')
# Selected local editable part viewers keep their original directory layout.
AUTH=KIT/'authoring'
def auth(src):cp(src,AUTH/src.relative_to(ROOT))
walk=cases/'articulated-sprites-v54'
for p in (walk/'parts').rglob('*.png'):auth(p)
for p in (walk/'inputs').glob('*.js'):auth(p)
for p in (walk/'inputs').glob('*.cjs'):auth(p)
for v in ['S','SW','W','NW','N','NE','E','SE']:
 prefix=''if v=='W'else v+'-'
 for n in ['walk-rig-contract.json','walk-review.html']:auth(walk/(prefix+n))
auth(walk/'source/walk-natural.blend');auth(walk/'source/source-walk-endpoints.json')
pickup=cases/'pickup-views-v55'
for name in ['W-split-drape5','E-split-drape4','S-front4']:
 contract=pickup/(name+'-articulated-contract.json');auth(contract);auth(pickup/(name+'-articulated-review.html'))
 def refs(x):
  if isinstance(x,dict):
   for y in x.values():refs(y)
  elif isinstance(x,list):
   for y in x:refs(y)
  elif isinstance(x,str)and len(x)<240 and Path(x).suffix in ['.png','.js','.cjs']and'://'not in x:
   f=pickup/x
   if f.is_file()and f.resolve().is_relative_to(ROOT):auth(f.resolve())
 refs(json.loads(contract.read_text()))
for n in ['sprite-mesh-player.js','sprite-articulated-player.js','sprite-segmented-player.js','sprite-clip-clock.cjs']:auth(pickup/'inputs'/n)
fight=cases/'unarmed-motion-v57'
for n in ['fight-review.html','fight-rig-contract.json','source/unarmed-inplace.blend','source/retargeted-endpoints.json','source/cc0-motion.json','source/KayKit-License.txt']:auth(fight/n)
for p in (fight/'inputs').rglob('*'):
 if p.is_file()and p.suffix in ['.png','.js','.cjs']:auth(p)
for n in ['sprite-mesh-player.js','sprite-articulated-player.js','sprite-segmented-player.js','sprite-segment-ownership.js','sprite-clip-clock.cjs']:cp(ROOT/'tools'/n,AUTH/'tools'/n)
cp(cases/'pickup-sixteen-v48/source/parent-v45.blend',KIT/'source/pickup-original-source.blend');cp(pickup/'source/controlled-retiming-v1.json',KIT/'source/pickup-retiming.json')
for folder in ['ro-motion-lab-v51','ro-core-views-v52','articulated-sprites-v54','pickup-views-v55']:
 f=cases/folder/'generation-ledger.json'
 if f.exists():cp(f,KIT/'provenance'/folder/'generation-ledger.json')
# Lightweight visual previews; measurement remains tied to original PNGs.
q=[]
for i in ([] if '--skip-previews' in __import__('sys').argv else range(16)):
 board=Image.new('RGBA',(1024,1152),(40,43,48,255));draw=ImageDraw.Draw(board)
 for j,v in enumerate(['S','W','N','E']):
  f=D['actions']['pickup']['clips'][v]['frames'][i];x=j%2*512;y=j//2*576;board.alpha_composite(Image.open(P/f['path']).convert('RGBA'),(x,y));draw.text((x+18,y+18),v+'  '+str(i),fill='white')
 q.append(board)
if q:q[0].save(OUT/'pickup-four-views.webp',save_all=True,append_images=q[1:],duration=[90]*15+[550],loop=0,lossless=True,quality=100,method=6,exact=True)
q=[]
for i in ([] if '--skip-previews' in __import__('sys').argv else range(0,80,2)):
 board=Image.new('RGBA',(1024,616),(40,43,48,255));draw=ImageDraw.Draw(board)
 for j,v in enumerate(D['directions']):
  f=D['actions']['walk']['clips'][v]['frames'][i];x=j%4*256;y=j//4*308;im=Image.open(P/f['path']).convert('RGBA').resize((256,288),Image.Resampling.LANCZOS);board.alpha_composite(im,(x,y+20));draw.text((x+10,y+3),v,fill='white')
 q.append(board)
if q:q[0].save(OUT/'walk-eight-views.webp',save_all=True,append_images=q[1:],duration=[20]*40,loop=0,lossless=True,quality=100,method=6,exact=True)
(KIT/'README.md').write_text('''# Astraeon · PNG48คลิปและเครื่องมือตรวจ

มี PNG964เฟรมพร้อมใช้ใน `frames/` และตารางเวลา/มุมใน `catalog.json` ยืน เดิน นั่งใช้8มุม; ก้ม เตรียมสู้ หมัด โดนโจมตี ล้ม สกิลใช้4มุม ห้ามกลับภาพซ้ายขวา

ติดตั้ง `Pillow numpy scipy` แล้วเรียก `python verify-package.py` เพื่อทวน SHA, ตาราง48คลิป, โปรไฟล์จังหวะก้ม และหลักฐานเท้าที่รวมมา คำสั่งไม่แก้ภาพต้นฉบับ ดู KNOW-HOW.md สำหรับขั้นตอนใช้ซ้ำ และ REFERENCES.md/ro-capture-ledger.json สำหรับเรฟภายนอกที่ตรวจจริง

แตก ZIP ทั้งสองไฟล์ลงโฟลเดอร์เดียวกัน (แพ็กหนึ่งเป็นท่าเดิน อีกแพ็กเป็นท่าอื่นและเครื่องมือ) แล้วตรวจด้วย verify-package.py ตัวเล่นไฟล์เดียว `astraeon-motion-review.html` ส่งแยกจาก ZIP เพื่อลดข้อมูลซ้ำ เปิดในเบราว์เซอร์สมัยใหม่เพื่อเล่น1×/¼× หยุด ไล่เฟรม วน และหมุนกล้อง ตัวอย่างแก้ไขชิ้นภาพอยู่ใน `authoring/research/sprite-animation/` พร้อมริกต้นทางที่เลือกและ renderer

โปรไฟล์ของตัวละครใหม่ต้องระบุท่าพัก จุดข้อมือ ชิ้น underlap และบริเวณรองเท้าที่เห็นจริง ไม่ใช่ระบบอนุมัติกายวิภาคอัตโนมัติ ท่าก้มเป็น empty-hand mime; มุม S เฟรม7–9มีเท้าถูกบังบางส่วนจึงตรวจด้วยเลเยอร์ที่มีเงื่อนไข ท่านั่ง/ล้มเป็นสถานะค้าง ไม่มีช่วงล้มลงหรือเปลี่ยนจากยืนไปนั่ง

แพ็กนี้มีไฟล์ที่พร้อมใช้และตัวอย่างตรวจซ้ำ ประวัติการลองผิด บัฟเฟอร์โลกทั้งหมด และ raw native jobs อยู่ใน branch `research/modular-sprites-full-body-2026-10-11` ในเคส v51–v57 ไม่รวมภาพ RO ในเฟรมส่งออก แหล่ง CC0 ระบุใบอนุญาตไว้ ไม่ได้อ้างสิทธิ์แจกภาพ RO หรือยืนยันค่าใช้จ่าย host generation เป็นศูนย์
''')
# This verifier intentionally has no dependency on the research checkout.
(KIT/'verify-package.py').write_text('''from pathlib import Path
import hashlib,json,importlib.util,argparse
P=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args()
for r in json.loads((P/'FILES.json').read_text())['files']:
 f=P/r['path'];assert f.is_file()and hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'],r['path']
def load(n):
 s=importlib.util.spec_from_file_location(n,P/'tools'/('sprite-'+n+'-review.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
D=json.loads((P/'catalog.json').read_text());c=load('coverage').evaluate(D,P);assert c['pass'],c['errors'];motion=load('motion');contact=load('contact');layer=load('layer-contact');results={}
for v in ['N','W','E','S']:
 f=P/'profiles'/(v+'-motion.json');m=motion.evaluate(json.loads(f.read_text()),f.parent);assert m['motion_profile_pass'];f=P/'profiles'/(v+'-contact.json');x=(layer if v=='S'else contact).evaluate(json.loads(f.read_text()),f.parent);assert x['layer_contact_pass'if v=='S'else'visible_surface_contact_pass'];results[v]={'motion':True,'contact':True,'qualified_layers':v=='S'}
r={'package_pass':True,'authored_clips':48,'exported_exposures':sum(len(c['frames'])for d in D['actions'].values()for c in d['clips'].values()),'pickup_checks':results,'scope':'Current package inventory, coverage/manual receipts and included motion/contact profiles. Full browser/source/world diagnostics are separately recorded in research reports.'}
if a.output:a.output.write_text(json.dumps(r,indent=2)+'\\n')
print(json.dumps(r,indent=2))
''')
files=[{'path':str(p.relative_to(KIT)),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(KIT.rglob('*'))if p.is_file()and p.name not in ['FILES.json','verification.json']and'__pycache__'not in p.parts];(KIT/'FILES.json').write_text(json.dumps({'files':files,'excluded':['FILES.json','verification.json','__pycache__']},indent=2)+'\n');print('Staged',len(files),'files and previews',flush=True)
