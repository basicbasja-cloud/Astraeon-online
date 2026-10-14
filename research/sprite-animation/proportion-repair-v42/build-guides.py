"""Input-only plates: actual source geometry, exact accepted art, rear head crop."""
from pathlib import Path
import json,hashlib
from PIL import Image
P=Path(__file__).resolve().parent;ROOT=P.parents[2];old=P.parent/'forward-pickup-v41'
def bind(p):return dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def bounds(im):
 a=im.getchannel('A').point(lambda x:255 if x>=128 else 0);return a.getbbox()
source=Image.open(P/'source/rear/00.png').convert('RGBA');x0,y0,x1,y1=bounds(source);s=398/(y1-y0-1);tx=192-s*192;ty=82-s*y0;inverse=(1/s,0,-tx/s,0,1/s,-ty/s)
for kind in ['rear','owner']:
 atlas=Image.new('RGBA',(1536,1024))
 for i in range(8):
  im=Image.open(P/f'source/{kind}/{i:02}.png').convert('RGBA').transform((384,512),Image.Transform.AFFINE,inverse,Image.Resampling.BICUBIC);atlas.paste(im,(i%4*384,i//4*512));d=P/f'guide-{kind}';d.mkdir(exist_ok=True);im.save(d/f'{i:02}.png')
 atlas.save(P/f'guide-{kind}.png')
reference=Image.new('RGBA',(1536,1024))
for i in range(8):reference.paste(Image.open(P.parent/f'recovery-key-v39/renders/review/full/{i:02}.png').convert('RGBA'),(i%4*384,i//4*512))
reference.save(P/'approved-reference.png')
# Identity only; none of v41's criticized arms/boots enter this crop.
Image.open(old/'size-locked-review/00.png').crop((102,72,242,181)).save(P/'rear-head-identity.png')
(P/'guide-receipt.json').write_text(json.dumps(dict(source_neutral_extent=[x0,y0,x1,y1],bank_matrix=[s,0,0,s,tx,ty],scope='One shared world-source display transform; input geometry only, not final art. Approved reference PNGs copied exactly. Rear head crop excludes arms/boots.',inputs=[bind(P/f'{name}.png') for name in ['guide-rear','guide-owner','approved-reference','rear-head-identity']],source_binding=bind(P/'source/source.json')),indent=2)+'\n')
print('Four input plates built; common source scale',s)
