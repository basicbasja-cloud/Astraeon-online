"""Rebuild native-input guide plates in a temporary directory, never final art."""
import hashlib,json,tempfile
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as td:
    T=Path(td);a=Image.open(P/'painted-owner-guide.png').convert('RGBA');a.paste(Image.open(P/'goal-attempt1.png'),(1152,0));a.save(T/'attempt3-guide.png')
    raw=Image.open(P/'attempt3-raw.png').convert('RGBA');out=Image.new('RGBA',raw.size)
    for i in range(8):
        c=raw.crop((i%4*384,i//4*512,i%4*384+384,i//4*512+512));z=np.array(c);yy,xx=np.where((z[:,:,3]>=128)&(np.indices(z.shape[:2])[0]>420));yb=int(yy.max());xnear=int(xx[yy>=yb-32].min());dx,dy=119-xnear,490-yb
        c=c.transform(c.size,Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),Image.Resampling.NEAREST)
        shift=[(0,0),(-3,0),(-15,5),(-25,12),(-10,0),(-5,0),(0,0),(0,0)][i];xg,yg=np.meshgrid(np.arange(384),np.arange(512));weight=np.clip((450-yg)/150,0,1);v=np.array(c);w=np.stack([map_coordinates(v[:,:,k],[yg-shift[1]*weight,xg-shift[0]*weight],order=1,mode='constant',cval=0) for k in range(4)],axis=2).astype('uint8');out.paste(Image.fromarray(w),(i%4*384,i//4*512))
    a=out;patch=a.crop((65,400,121,460))
    for i in range(3):
        c=a.crop((i*384,0,i*384+384,512));z=np.array(c);r,g,b=z[:,:,:3].astype(float).transpose(2,0,1);m=(g>r+20)&(b>r+20)&(np.indices(r.shape)[0]>375)&(np.indices(r.shape)[1]<145);z[m]=0;c=Image.fromarray(z);c.alpha_composite(patch,(65,367));a.paste(c,(i*384,0))
    a.save(T/'attempt4-guide.png')
    a=Image.open(P/'attempt4-raw.png').convert('RGBA');boot=a.crop((80,438,315,512));out=Image.new('RGBA',a.size)
    for i in range(8):
        c=a.crop((i%4*384,i//4*512,i%4*384+384,i//4*512+512));c.paste(boot,(80,438));out.paste(c,(i%4*384,i//4*512))
    out.save(T/'attempt5-guide.png')
    a=Image.open(P/'attempt5-raw.png').convert('RGBA');q=Image.new('RGBA',a.size);mask=Image.new('L',(384,512));d=ImageDraw.Draw(mask);d.polygon([(108,458),(130,443),(171,435),(218,442),(225,502),(108,502)],fill=255);d.polygon([(211,438),(273,438),(292,460),(292,485),(218,484)],fill=255);d.rectangle((0,0,383,437),fill=0);boot=Image.new('RGBA',(384,512));boot.paste(a.crop((0,0,384,512)),(0,0),mask);z=np.array(a.crop((0,0,384,512)));r,g,b=z[:,:,:3].astype(float).transpose(2,0,1);yy,xx=np.indices(r.shape);gem=(g>r+15)&(b>r+15)&(xx<120)&(yy>375);z[~gem]=0;prop=Image.fromarray(z)
    for i in range(8):
        c=a.crop((i%4*384,i//4*512,i%4*384+384,i//4*512+512));ImageDraw.Draw(c).rectangle((65,438,330,511),fill=(0,0,0,0));c.alpha_composite(boot)
        if i<4:
            z=np.array(c);r,g,b=z[:,:,:3].astype(float).transpose(2,0,1);z[(g>r+15)&(b>r+15)&(xx<155)&(yy>375)]=0;c=Image.fromarray(z);c.alpha_composite(prop)
        q.paste(c,(i%4*384,i//4*512))
    q.save(T/'attempt6-guide.png')
    a=Image.open(P/'attempt6-raw.png').convert('RGBA');out=Image.new('RGBA',a.size);owner=Image.new('RGBA',a.size)
    for i in range(8):
        c=a.crop((i%4*384,i//4*512,i%4*384+384,i//4*512+512));s=Image.open(P/f'source-full-owner/owner/{i:02}.png').convert('RGBA').transform((384,512),Image.Transform.AFFINE,(1/1.04,0,3/1.04,0,1/1.04,29/1.04),Image.Resampling.BICUBIC);c.paste(s.crop((0,330,384,512)),(0,330));out.paste(c,(i%4*384,i//4*512));owner.paste(s,(i%4*384,i//4*512))
    out.save(T/'attempt7-guide.png');owner.save(T/'full-owner-guide.png')
    rows=[dict(file=p.name,expected=sha(P/p.name),reproduced=sha(p),exact=sha(P/p.name)==sha(p)) for p in sorted(T.glob('*.png'))]
(P/'guide-reproduction.json').write_text(json.dumps(dict(scope='Only native authoring-input plates; rejected guide pixels never final sprite pixels.',files=rows,exact=all(r['exact'] for r in rows)),indent=2)+'\n')
print(json.dumps(dict(files=len(rows),exact=all(r['exact'] for r in rows))))
assert all(r['exact'] for r in rows)
