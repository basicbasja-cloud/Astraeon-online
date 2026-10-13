"""Normalize an imagegen-authored part atlas by explicit empty-gutter panels.
Only crop/translate source asset panels. No repaint or frame-specific geometry fix.
"""
from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent;raw=P/'atlas-raw.png';im=Image.open(raw).convert('RGBA');assert im.size==(1254,1254)
# Explicit panels after inspecting true atlas packing, not nominal equal tiles.
parts=[
 ('head_hair',[0,0,366,365],[202,326],None,.52),
 ('torso',[366,0,637,365],[500,137],[493,310],.5),
 ('cape',[637,0,982,365],[731,118],None,.49),
 ('teal_panel',[982,0,1254,365],[1082,136],None,.43),
 ('right.upperarm',[0,365,318,636],[225,395],[133,565],.25),
 ('right.forearm',[318,365,637,636],[516,401],[438,520],.29),
 ('left.upperarm',[637,365,952,636],[744,403],[851,565],.27),
 ('left.forearm',[952,365,1254,636],[1061,406],[1115,532],.28),
 ('right.thigh',[0,636,318,924],[189,671],[148,854],.31),
 ('right.shin',[318,636,637,924],[496,662],[500,854],.30),
 ('left.thigh',[637,636,952,924],[800,668],[777,855],.33),
 ('left.shin',[952,636,1254,924],[1110,663],[1124,855],.33),
 ('right.foot',[0,924,318,1254],[216,1014],None,.43),
 ('left.foot',[318,924,637,1254],[527,1015],None,.43),
 ('front_tabard',[637,924,952,1254],[798,954],None,.39),
 ('side_tabard',[952,924,1254,1254],[1094,974],None,.37)]
out=P/'parts';out.mkdir(exist_ok=True);rows=[]
for name,box,a,b,width in parts:
 crop=im.crop(box);file=out/(name+'.png');crop.save(file);pivot=[a[0]-box[0],a[1]-box[1]];end=[b[0]-box[0],b[1]-box[1]] if b else None
 rows.append({'name':name,'file':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'atlas_box':box,'pivot':pivot,'end':end,'width_scale':width,'semantic_owner':name.split('.')[0] if '.' in name else 'body','source_role':'newly generated neutral part appearance, not captured anatomy','mirrored':False})
(P/'parts.json').write_text(json.dumps({'atlas_file':str(raw),'atlas_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'parts':rows,'scope':'16source panel crops, complete sprite parts by authoring role; head+hair is combined in this pilot. Hinges are authored, not automatic joint detections. No full replacement hair bank.'},indent=2)+'\n')
print('PARTS_EXTRACTED',len(rows))
