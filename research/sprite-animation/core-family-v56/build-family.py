"""Assemble declared candidates on a common canvas; never invent visual approval."""
from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent;cases=P.parent;dirs=['S','SW','W','NW','N','NE','E','SE'];counts={'idle':8,'walk':8,'sit':8,'pickup':4,'ready':4,'attack1':4,'hurt':4,'dead':4,'skill':4}
catalog={'canvas':[512,576],'directions':dirs,'clock_quantum_ms':10,'actions':{a:{'aliases':{v:dirs[i//2*2] if n==4 else v for i,v in enumerate(dirs)},'clips':{}} for a,n in counts.items()},'production_pass':False};sources=[]
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def add(action,view,files,clock,notes):
 rows=[];out=P/'frames'/action/view;out.mkdir(parents=True,exist_ok=True)
 for i,src in enumerate(files):
  im=Image.open(src).convert('RGBA');assert im.width==512 and im.height in [512,576];dest=out/f'{i:02}.png';canvas=Image.new('RGBA',(512,576));canvas.alpha_composite(im);canvas.save(dest);rows.append({'path':str(dest.relative_to(P)),'sha256':sha(dest)});sources.append({'output':str(dest.relative_to(P)),'output_sha256':sha(dest),'source':str(src.relative_to(cases)),'source_sha256':sha(src),'operation':'Visible RGBA identity with transparent bottom padding; unused zero-alpha RGB may be cleared' if im.height==512 else 'Visible RGBA identity on common canvas; unused zero-alpha RGB may be cleared'})
 clip={'frames':rows,'durations_ms':clock,'mirrored':False,'assembly_notes':notes,'review':{'status':'pending','frame_sha256':[],'observations':[]},'checks':dict.fromkeys(['registration','appearance','playback','pose_readability','whole_motion'],False)}
 review=P/'reviews'/f'{action}-{view}.json'
 if review.exists():
  r=json.loads(review.read_text());assert r['frame_sha256']==[f['sha256'] for f in rows],f'Stale manual receipt {review}';clip['review']=r['review'];clip['checks']=r['checks']
 catalog['actions'][action]['clips'][view]=clip
prior=cases/'ro-core-views-v52';stage=json.loads((prior/'stage-export-review.json').read_text())
for clip in stage['clips']:
 if clip['action']=='ready' or (clip['action']=='dead' and clip['view']=='S'):continue
 files=[prior/f['path'] for f in clip['frames']]
 for f,row in zip(files,clip['frames']):assert sha(f)==row['sha256']
 add(clip['action'],clip['view'],files,clip['clock_ms'],'Existing v52 candidate, transparent bottom padding. Review does not transfer automatically.')
walk=cases/'articulated-sprites-v54'
for v in dirs:add('walk',v,[walk/'walk'/v/f'{i:02}.png' for i in range(80)],[10]*80,'80 source-evaluated rasters/800ms, not80 native drawings; current576px walk viewport.')
pickup=cases/'pickup-views-v55'
selected=json.loads((pickup/'selected-profile-pickups.json').read_text())
for v,r in selected.items():
 for f in r['evidence']+r['dependencies']:assert sha(pickup/f['path'])==f['sha256'],f'Stale pickup evidence {f["path"]}'
 ex=json.loads((pickup/(r['selected']+'-articulated-export.json')).read_text());add('pickup',v,[pickup/f['path'] for f in ex['frames']],[90]*15+[550],'Selected source-controlled profile candidate; actual prior motion/contact/player/manual receipts retained. Common576px padding requires final catalog review.')
fight=cases/'unarmed-motion-v57';fight_export=json.loads((fight/'fight-export-review.json').read_text())
assert len(fight_export['clips'])==8
for c in fight_export['clips']:
 files=[fight/f['path'] for f in c['frames']]
 for f,row in zip(files,c['frames']):assert sha(f)==row['sha256']
 add(c['action'],c['view'],files,c['durations_ms'],'Fresh saved in-place CC0-adapted original rig; static original/native rest-part binding. Not an external full-lunge replay or new native drawing per frame.')
# Actual image review found foreign neighboring atlas art in the old416px crop.
# Re-extract ONE static terminal pose, retaining the full actor through x394.
raw=prior/'raw/dead-wardrobe-repair2.png';im=Image.open(raw).convert('RGBA');fixed=Image.new('RGBA',(512,512));fixed.alpha_composite(im.crop((0,0,400,512)),(32,0));f=P/'inputs/dead-S-atlas400.png';f.parent.mkdir(exist_ok=True);fixed.save(f);add('dead','S',[f],[1000],'Static source atlas width400 retains actor bbox17..394 with5px gutter; excludes foreign pose at410..415. Old v52 contaminated raster retained as negative.')
(P/'dead-S-atlas-extraction.json').write_text(json.dumps({'source':str(raw.relative_to(cases)),'source_sha256':sha(raw),'source_rect':[0,0,400,512],'translation':[32,0],'output':str(f.relative_to(P)),'output_sha256':sha(f)},indent=2)+'\n')
(P/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n');(P/'assembly-ledger.json').write_text(json.dumps({'canvas':[512,576],'sources':sources,'production_pass':False},indent=2)+'\n');print(sum(len(a['clips']) for a in catalog['actions'].values()),'assembled clips; acceptance is recorded by verify-family.py')
