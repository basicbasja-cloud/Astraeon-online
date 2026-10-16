"""Fixed rest assembly: original visible rear cape/head/calves; native hidden limb underlap."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
P=Path(__file__).resolve().parent;out=P/'parts/N';out.mkdir(exist_ok=True,parents=True);master=Image.open(P.parent/'ro-core-views-v52/stage/idle/N/00.png').convert('RGBA');raw=Image.open(P/'raw/N-original-parts-attempt1.png').convert('RGBA');spec={};parts={}
def save(n,im,desc):
 im.save(out/f'{n}.png');spec[n]={**desc,'texture_sha256':hashlib.sha256((out/f'{n}.png').read_bytes()).hexdigest()};parts[n]=im
head=Image.new('RGBA',(512,512));head.alpha_composite(master.crop((0,0,512,198)));save('head',head,{'source':'original stage idle N','crop':[0,0,512,198]})
polygon=[[216,195],[294,195],[292,216],[292,236],[300,275],[313,329],[337,401],[306,394],[275,402],[244,395],[213,403],[177,401],[197,335],[210,277],[223,235],[224,211]];mask=Image.new('L',(512,512));ImageDraw.Draw(mask).polygon(polygon,fill=255);body=master.copy();import PIL.ImageChops;body.putalpha(PIL.ImageChops.multiply(body.getchannel('A'),mask));save('body',body,{'source':'exact original visible cape/scarf clipped with authored cape region, no filled pixels','polygon':polygon,'hidden_body_scope':'Walking-only cape occlusion; no claim that hidden torso art is complete'})
for n,i,s,tx,ty in [('left_arm',2,.5,139,142),('right_arm',3,.5,190,142),('left_leg',4,.4,158,322),('right_leg',5,.4,207,322)]:
 im=raw.crop((i%4*384,i//4*512,i%4*384+384,i//4*512+512));im=im.resize((round(384*s),round(512*s)),Image.Resampling.LANCZOS);a=Image.new('RGBA',(512,512));a.alpha_composite(im,(tx,ty));desc={'native_cell':i,'scale':s,'translation':[tx,ty]}
 if n.endswith('_arm'):
  poly=([[198,208],[225,208],[224,237],[215,273],[201,310],[193,347],[180,347],[184,313],[190,273],[190,236]] if n=='left_arm' else [[291,207],[319,208],[333,237],[335,280],[339,316],[336,349],[318,349],[318,332],[322,310],[318,275],[310,242],[292,237]])
  # Original visible arm pixels plus only the inner, occluded native underlap.
  if n=='left_arm':a.paste((0,0,0,0),(0,0,197,512))
  else:a.paste((0,0,0,0),(318,0,512,512))
  a.paste((0,0,0,0),(0,0,512,225));a.paste((0,0,0,0),(0,265,512,512))
  m=Image.new('L',(512,512));ImageDraw.Draw(m).polygon(poly,fill=255);visible=master.copy();visible.putalpha(PIL.ImageChops.multiply(visible.getchannel('A'),m));a.alpha_composite(visible);desc['original_visible_arm_polygon']=poly
 if n.endswith('_leg'):

  # A static rest texture selection, not an animation-frame foot patch.
  x0,x1=(180,256) if n=='left_leg' else (256,336);a.paste((0,0,0,0),(0,402,512,512));a.alpha_composite(master.crop((x0,402,x1,512)),(x0,402));desc['original_visible_region']=[x0,402,x1,512];desc['underlap']='Native whole-leg art above402 hidden by original cape; original visible knee/shin/boot below402 unchanged'
 save(n,a,desc)
order=['left_leg','right_leg','left_arm','right_arm','head','body'];a=Image.new('RGBA',(1024,512))
for n in order:a.alpha_composite(parts[n])
a.alpha_composite(master,(512,0));bg=Image.new('RGBA',a.size,(40,43,48,255));bg.alpha_composite(a);bg.convert('RGB').save(P/'N-rest-comparison.png');(P/'N-rest-contract.json').write_text(json.dumps({'view':'N','parts':spec,'order':order,'scope':'Static visible-art segmentation and native underlap; no per-frame image normalization or painted correction','production_pass':False},indent=2)+'\n')
