"""Export clear 2x2 GIFs, a two-action offline viewer and separate sheets."""
from pathlib import Path
import json,hashlib,shutil,zipfile
from PIL import Image,ImageDraw
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_four_direction_attack_review import compose
repo=Path(__file__).resolve().parents[2];b=repo/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset';import argparse
parser=argparse.ArgumentParser(description='Package the two registered layered action reviews and offline viewer');parser.add_argument('--output',type=Path,default=Path('/workspace/outputs'));args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
actions={'BasicAttack':b/'basic-attack-simple','SkillOverhead':b/'skill-overhead-registered'};pages={};checks=[]
for name,r in actions.items():
 a=json.loads((r/'assembly-audit.json').read_text());manifest=json.loads((r/'sprite-sheets-manifest.json').read_text());pages[name]=(r/'review.html').read_text();frames=[]
 for i in range(16):
  canvas=Image.new('RGB',(1024,1080),'#ececec');draw=ImageDraw.Draw(canvas)
  for j,d in enumerate(['SW','NW','NE','SE']):
   x=j%2*512;y=j//2*540;canvas.paste(compose(r,d,i),(x,y+28));draw.text((x+12,y+8),name+' / '+d,fill='black')
  frames.append(canvas)
 for suffix,timing in [('',a['durations_ms']),('-slow',a['slow_durations_ms'])]:
  frames[0].save(out/(name+suffix+'.gif'),save_all=True,append_images=frames[1:],duration=timing,disposal=2,optimize=False)
  shutil.copy2(out/(name+suffix+'.gif'),r/('review-2x2'+suffix+'.gif'))
 checks.append({'action':name,'poses':64,'exported_cells_checked':sum(c['cells_checked'] for c in manifest['sheet_checks']),'visible_cell_mismatches':sum(c['visible_rgba_mismatches'] for c in manifest['sheet_checks']),'effect_edge_touches':sum(c['edge_touch'] for c in manifest['effect_checks'])})
text='''<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Astraeon · Layered Action Factory</title><style>body{margin:0;background:#141b28;color:#eef2fa;font:16px system-ui}header{padding:20px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}h1{font-size:21px;margin:0}button{font:inherit;padding:12px;background:#344863;color:white;border:1px solid #8b9bb1;border-radius:8px;cursor:pointer}button.active{background:#795f30}iframe{width:100%;height:1100px;border:0}p{margin:0;color:#b6c3d8}</style><header><h1>Astraeon · Action Factory</h1><button id="BasicAttack">Basic Attack</button><button id="SkillOverhead">Skill · ฟันหนัก</button><p>4 ทิศ · เลือกท่าและตรวจเลเยอร์แยกส่วน</p></header><iframe title="ตรวจแอนิเมชันและเลเยอร์" id="stage"></iframe><script>const pages=__PAGES__;function choose(name){document.getElementById('stage').srcdoc=pages[name];for(const key of Object.keys(pages))document.getElementById(key).classList.toggle('active',key===name);}for(const key of Object.keys(pages))document.getElementById(key).onclick=()=>choose(key);choose('BasicAttack');</script></html>'''
(out/'astraeon-layered-factory-review.html').write_text(text.replace('__PAGES__',json.dumps(pages).replace('<','\\u003c')))
with zipfile.ZipFile(out/'astraeon-layered-factory-sheets.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name,r in actions.items():
  for p in sorted((r/'sheets').glob('*.png')):z.write(p,name+'/sheets/'+p.name)
  for p in [r/'sprite-sheets-manifest.json',r/'factory-receipt.json',r/'README.md']:z.write(p,name+'/'+p.name)
 z.write(repo/'authoring/characters/factory-v3/configs/layered_action_catalog.json','layered_action_catalog.json')
 z.write(repo/'authoring/characters/factory-v3/motions/legal-evidence/mesh2motion-cc0-license.md','mesh2motion-cc0-license.md')
(out/'astraeon-layered-factory-export-audit.json').write_text(json.dumps({'actions':checks,'total_poses':128,'owner_approved':False,'runtime_admitted':False,'browser_interactions_automated':False},indent=2)+'\n')
print(json.dumps(checks))
