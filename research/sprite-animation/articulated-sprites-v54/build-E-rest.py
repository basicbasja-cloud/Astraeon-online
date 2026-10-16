"""Authored static part packing and uniform per-piece scales. No time-dependent fit."""
from pathlib import Path
from PIL import Image
import json,hashlib
P=Path(__file__).resolve().parent;out=P/'parts/E';out.mkdir(exist_ok=True,parents=True);raw=Image.open(P/'raw/E-original-parts-attempt1.png').convert('RGBA');master=Image.open(P.parent/'ro-core-views-v52/neutral/E.png').convert('RGBA');spec={
 'head':{'cell':None,'scale':1,'translation':[32,0]},
 'body':{'cell':1,'scale':.56,'translation':[119,120]},
 'left_arm':{'cell':2,'scale':.48,'translation':[159,140]},
 'right_arm':{'cell':3,'scale':.48,'translation':[159,143]},
 'left_leg':{'cell':4,'scale':.49,'translation':[188,284]},
 'right_leg':{'cell':5,'scale':.49,'translation':[193,296]}}
for n,d in spec.items():
 im=master.crop((0,0,384,204)) if n=='head' else raw.crop((d['cell']%4*384,d['cell']//4*512,d['cell']%4*384+384,d['cell']//4*512+512));s=d['scale'];im=im.resize((round(im.width*s),round(im.height*s)),Image.Resampling.LANCZOS);a=Image.new('RGBA',(512,512));a.alpha_composite(im,tuple(d['translation']));a.save(out/f'{n}.png');d['texture_sha256']=hashlib.sha256((out/f'{n}.png').read_bytes()).hexdigest()
order=['left_leg','right_leg','left_arm','head','body','right_arm'];a=Image.new('RGBA',(1024,512));
for n in order:a.alpha_composite(Image.open(out/f'{n}.png'))
a.alpha_composite(master,(544,0));bg=Image.new('RGBA',a.size,(40,43,48,255));bg.alpha_composite(a);bg.convert('RGB').save(P/'E-rest-comparison.png');(P/'E-rest-contract.json').write_text(json.dumps({'view':'E','parts':spec,'order':order,'packing_scope':'Fixed static artist rest adapter; per-piece uniform scale corrects native atlas packing, no temporal fits. Unreviewed.'},indent=2)+'\n')
