"""Fixed static packing. Body rect retains cape that crosses an otherwise empty atlas gutter."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import json,hashlib
P=Path(__file__).resolve().parent;out=P/'parts/SW';out.mkdir(exist_ok=True,parents=True);raw=Image.open(P/'raw/SW-original-parts-attempt1.png').convert('RGBA');master=Image.open(P.parent/'ro-core-views-v52/neutral/SW.png').convert('RGBA');spec={
 'head':{'rect':None,'scale':1,'translation':[32,0]},
 'body':{'rect':[384,0,446,512],'scale':.56,'translation':[160,123]},
 'left_arm':{'rect':[848,0,304,512],'scale':.46,'translation':[215.8,143],'rotation_deg':5,'pivot':[286,230]},
 'right_arm':{'rect':[1152,0,384,512],'scale':.46,'translation':[136,145],'rotation_deg':-13,'pivot':[213,229]},
 'left_leg':{'rect':[384,512,384,512],'scale':.44,'translation':[200,316]},
 'right_leg':{'rect':[0,512,384,512],'scale':.5,'translation':[115,292]}}
for n,d in spec.items():
 r=d['rect'];im=master.crop((0,0,384,211)) if n=='head' else raw.crop((r[0],r[1],r[0]+r[2],r[1]+r[3]));s=d['scale'];im=im.resize((round(im.width*s),round(im.height*s)),Image.Resampling.LANCZOS);a=Image.new('RGBA',(512,512));a.alpha_composite(im,tuple(round(x) for x in d['translation']));
 if d.get('rotation_deg'):a=a.rotate(d['rotation_deg'],resample=Image.Resampling.BICUBIC,center=tuple(d['pivot']))
 if n.endswith('_arm'):
  if n=='left_arm':
   poly=[[270,219],[292,222],[307,240],[309,282],[310,310],[301,349],[280,359],[267,353],[272,323],[273,288],[269,263],[260,241]];a.paste((0,0,0,0),(279,0,512,512))
  else:
   poly=[[205,219],[216,229],[210,253],[205,279],[199,303],[193,327],[191,345],[178,357],[170,347],[173,324],[181,296],[187,274],[192,249],[194,232]];a.paste((0,0,0,0),(0,0,208,512))
  full=Image.new('RGBA',(512,512));full.alpha_composite(master,(32,0));mask=Image.new('L',(512,512));ImageDraw.Draw(mask).polygon(poly,fill=255);full.putalpha(ImageChops.multiply(full.getchannel('A'),mask));a.alpha_composite(full);d['original_visible_arm_polygon']=poly;d['scope']='Exact original visible arm plus native inner hidden overlap; static source composition, not animation-frame patch'
 a.save(out/f'{n}.png');d['texture_sha256']=hashlib.sha256((out/f'{n}.png').read_bytes()).hexdigest()
order=['right_leg','left_leg','right_arm','body','head','left_arm'];a=Image.new('RGBA',(1024,512))
for n in order:a.alpha_composite(Image.open(out/f'{n}.png'))
a.alpha_composite(master,(544,0));bg=Image.new('RGBA',a.size,(40,43,48,255));bg.alpha_composite(a);bg.convert('RGB').save(P/'SW-rest-comparison.png');(P/'SW-rest-contract.json').write_text(json.dumps({'view':'SW','parts':spec,'order':order,'packing_scope':'Fixed static adapter. Expanded body source crop preserves cape in empty neighboring gutter; arm source excludes that gutter. No per-frame image fit. Unreviewed.'},indent=2)+'\n')
