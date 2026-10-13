#!/usr/bin/env python3
"""Read creator's 32-column,8-row atlas, keep original pixels and action IDs.
Boards show a diagnostic clothes+head composite, not recovered engine layer order.
No runtime timing inferred from a PNG; source descriptions and engine templates
are separate evidence. Native cells are not recentered/scaled in the dataset.
"""
import hashlib,json,shutil
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
source=ROOT/'local-cache/oga-isometric-hero/isometric_hero'
preserved=ROOT/'open-data/oga-hero';preserved.mkdir(parents=True,exist_ok=True)
for name in ('clothes.png','male_head1.png'):shutil.copyfile(source/name,preserved/name)
(preserved/'ATTRIBUTION.txt').write_text('Isometric Hero and Heroine — Clint Bellanger\nSource: https://opengameart.org/content/isometric-hero-and-heroine\nCreator page license: CC-BY 3.0\nLicense: https://creativecommons.org/licenses/by/3.0/\nOriginal clothes.png and male_head1.png are preserved unchanged.\nThe v29 boards combine these two layers and enlarge nearest-neighbor for diagnostic study.\nNo leather or weapon assets are used in these published boards.\nSource page gives additional equipment credits to D. Sharon Pruitt and Naraphim; review those separately before using that equipment.\nResearch references only; not admitted into Astraeon shipping character assets.\n')
out=ROOT/'sprite-boards';out.mkdir(exist_ok=True)
body=Image.open(source/'clothes.png').convert('RGBA');head=Image.open(source/'male_head1.png').convert('RGBA')
if body.size!=(4096,1024) or head.size!=body.size:raise ValueError('Unexpected source grid')
ACTIONS=[('stance',0,4),('run',4,8),('swing',12,4),('block',16,2),('hit',18,2),('die',18,6),('cast',24,4),('shoot',28,4)]
records=[]
for name,start,count in ACTIONS:
 board=Image.new('RGB',(count*256,8*280),(35,39,47));d=ImageDraw.Draw(board);cells=[]
 for direction in range(8):
  for i in range(count):
   box=((start+i)*128,direction*128,(start+i+1)*128,(direction+1)*128)
   b=body.crop(box);h=head.crop(box);composite=Image.alpha_composite(b,h)
   x=i*256;y=direction*280
   d.text((x+5,y+4),f'{name} / dir-index {direction} / cell {start+i}',fill='white')
   enlarged=composite.resize((256,256),Image.Resampling.NEAREST);board.paste(enlarged,(x,y+24),enlarged)
   cells.append({'direction_index':direction,'source_frame_column':start+i,'source_rect':list(box),'body_rgba_sha256':hashlib.sha256(b.tobytes()).hexdigest(),'head_rgba_sha256':hashlib.sha256(h.tobytes()).hexdigest(),'duration_ms':None,'anatomical_owner':'unverified','contact':'unknown'})
 path=out/(name+'.png');board.save(path)
 records.append({'action':name,'board_file':str(path.relative_to(ROOT)),'board_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cell_count':len(cells),'cells':cells,'timing':'unknown for this archived PNG; current Flare descriptor clock is separate','scope':'Diagnostic clothes/head composite; source author describes rows as eight directions, cardinal mapping not inferred.'})
(ROOT/'sprite-board-manifest.json').write_text(json.dumps({'schema':'creator-atlas-study-v1','source_id':'oga-hero','author':'Clint Bellanger','url':'https://opengameart.org/content/isometric-hero-and-heroine','page_license':'CC-BY 3.0','source_image_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (source/'clothes.png',source/'male_head1.png')},'additional_credit_scope':'The published diagnostic uses clothes+head; leather and weapon assets are not incorporated. Original page names D.SharonPruitt and Naraphim for other equipment.','boards':records,'production_admitted':False},indent=2)+'\n')
print(json.dumps({'boards':len(records),'action_cells':sum(x['cell_count'] for x in records),'unique_native_cells':256}))
