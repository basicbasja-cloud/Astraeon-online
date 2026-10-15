"""Assemble fixed source plates. The one inherited matrix is shared for every key."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
P=Path(__file__).resolve().parent;old=P.parent/'painted-pickup-v47';(P/'inputs').mkdir(exist_ok=True)
m=json.loads((P/'source/display-bind.json').read_text())['matrix'];s,tx,ty=m[0],m[4],m[5];inv=(1/s,0,-tx/s,0,1/s,-ty/s)
for bank in ['midpoints','owners']:
 sheet=Image.new('RGBA',(1536,1024))
 for k in range(8):
  im=Image.open(P/'source'/f'raw-{bank}'/f'{k:02}.png').convert('RGBA').transform((384,512),Image.Transform.AFFINE,inv,Image.Resampling.BICUBIC)
  sheet.alpha_composite(im,((k%4)*384,(k//4)*512))
 sheet.save(P/'inputs'/f'{bank}.png')
# Explicit alternate guide layouts, never modifications of final art.
for name in ['midpoints','owners']:
 src=Image.open(P/'inputs'/f'{name}.png').convert('RGBA');out=Image.new('RGBA',(1536,1024));quartet=src.crop((0,512,1536,1024));out.paste(quartet,(0,0));out.paste(quartet,(0,512));out.save(P/'inputs'/f'{name}-recovery-quartet.png')
out=Image.new('RGBA',(1536,1024),'#292b30');out.alpha_composite(Image.open(P/'inputs/midpoints.png'));draw=ImageDraw.Draw(out)
for x in [0,384,768,1152,1535]:draw.line([(x,0),(x,1023)],fill='#7a8a9c',width=1)
draw.line([(0,512),(1535,512)],fill='#7a8a9c',width=1)
for y in [486,998]:draw.line([(0,y),(1535,y)],fill='#00f5a0',width=2)
out.save(P/'inputs/midpoints-floor-guide.png')
shutil.copyfile(old/'raw/N-attempt3.png',P/'inputs/v47-parent.png')
shutil.copyfile(old/'inputs/accepted-v39.png',P/'inputs/accepted-v39.png')
data={'parent_commit':'436aaace57311885bef8a28efab652e3d2006558','parent_raw_sha256':hashlib.sha256((old/'raw/N-attempt3.png').read_bytes()).hexdigest(),'inherited_source_matrix':m,'new_source_key_fractions':[.5,1.5,2.5,3.5,4.5,5.5,6+1/3,6+2/3],'original_key_output_indices':[0,2,4,6,8,10,12,15],'original_clock_ms':[190,180,190,180,190,180,190,600],'sixteen_clock_ms':[90,100,90,90,90,100,90,90,90,100,90,90,60,60,70,600],'source_vs_painted_authority_separate':True,'per_key_fitting':False,'production_pass':False}
assert sum(data['original_clock_ms'])==sum(data['sixteen_clock_ms'])==1900
(P/'contract.json').write_text(json.dumps(data,indent=2)+'\n')
print('8 new actual-source guides; 8 unchanged parent keys; same1900ms')
