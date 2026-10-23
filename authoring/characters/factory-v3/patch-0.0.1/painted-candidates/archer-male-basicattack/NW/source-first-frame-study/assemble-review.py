from pathlib import Path
import json,hashlib,subprocess,sys
from PIL import Image
b=Path('authoring/characters/factory-v3/patch-0.0.1');p=b/'painted-candidates/archer-male-basicattack/NW/source-first-frame-study';raw=[p/f'{i:03d}/raw-repaint.png'for i in range(16)]
selection=p/'selected-frame-repairs.json'
if selection.exists():
 for key,value in json.loads(selection.read_text()).items():raw[int(key)]=(p/value).resolve()
if any(not f.is_file()for f in raw):raise ValueError('Missing actual source-first frame')
sizes=[Image.open(f).size for f in raw]
if len(set(sizes))!=1 or sizes[0][0]!=sizes[0][1]:raise ValueError('Raw output canvases differ')
size=sizes[0][0];sheet=Image.new('RGBA',(size*4,size*4))
for i,f in enumerate(raw):sheet.alpha_composite(Image.open(f).convert('RGBA'),((i%4)*size,(i//4)*size))
sheet.save(p/'native-master-sheet.png')
(p/'sequence-inputs.json').write_text(json.dumps({'status':'SOURCE_FIRST_SEQUENCE_REQUIRES_VISUAL_REVIEW','frames':[{'index':i,'raw_sha256':hashlib.sha256(f.read_bytes()).hexdigest()}for i,f in enumerate(raw)],'source_canvas':sizes[0],'per_frame_fitting':False,'guide_job':'2fed9f286cdd5c5ffbf4','input_guide_job':'4f6e96426d00fa15c9a3','geometry_equivalence_receipt':str(b/'research/archer-source-fingerprint-equivalence.json'),'owner_approved':False,'runtime_admitted':False},indent=2)+'\n')
subprocess.run([sys.executable,'tools/character_factory_v3/register_clear_paint_candidate.py','--paint',str(p/'native-master-sheet.png'),'--guide',str(b/'guides/2fed9f286cdd5c5ffbf4'),'--direction','NW','--opaque-interior-threshold','245','--pose-recipe',str(p/'pose-recipe.json'),'--viewport','378','454','1158','1234','--timing',str(b/'research/archer-contact-motion-audit.json'),'--output',str(p/'sequence')],check=True)
