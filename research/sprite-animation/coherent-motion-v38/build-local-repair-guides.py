"""Reproduce retained diagnostic references. None is a selected animation asset."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import math,json
P=Path(__file__).resolve().parent;V=P.parent/'neck-motion-v36'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)

raw=Image.open(V/'motion-attempt2-raw.png').convert('RGBA')
template=Image.new('RGBA',raw.size,'#263443');ghost=raw.copy();ghost.putalpha(ghost.getchannel('A').point(lambda a:round(a*.35)));template.alpha_composite(ghost)
seed=raw.crop((3*384,512,4*384,1024));lip=json.loads((V/'motion-contract.json').read_text())['variants']['raw8'];d=ImageDraw.Draw(template)
for i in range(8):
    ox,oy=i%4*384,i//4*512
    for box in [(100,425,194,477),(194,436,274,493)]:template.alpha_composite(seed.crop(box),(ox+box[0],oy+box[1]))
    points=lip[i]['body_collar_lip_points_native'];cx=sum(t[0] for t in points)/2;cy=sum(t[1] for t in points)/2
    if i==6:cx,cy=184,143
    d.ellipse((ox+cx-6,oy+cy-6,ox+cx+6,oy+cy+6),outline='#ff72f3',width=3)
    d.line((ox+100,oy+466,ox+180,oy+466),fill='#66ffff');d.line((ox+194,oy+485,ox+275,oy+485),fill='#66ffff')
    d.rectangle((ox+1,oy+1,ox+382,oy+510),outline='#8196a9');d.text((ox+8,oy+8),f'Key{i+1} / fixed shoes / collar({cx:.0f},{cy:.0f})',font=font,fill='white')
template.convert('RGB').save(P/'contact-stencil-guide.png')

raw=Image.open(P/'attempt2-raw.png').convert('RGBA')
b=Image.new('RGBA',raw.size,'#263443');b.alpha_composite(raw);d=ImageDraw.Draw(b);ox,oy=768,512
d.rectangle((ox+1,oy+1,ox+382,oy+510),outline='#a6bccb',width=2)
d.ellipse((ox+158,oy+134,ox+170,oy+146),outline='#ff8c8c',width=3)
d.ellipse((ox+176,oy+121,ox+190,oy+135),outline='#68ffb6',width=3)
d.line((ox+164,oy+140,ox+183,oy+128),fill='#68ffb6',width=3)
d.text((ox+5,oy+8),'KEY7 ONLY: torso to collar(183,128)',font=font,fill='white')
d.line((ox+95,oy+468,ox+180,oy+468),fill='#65ffff',width=2);d.line((ox+190,oy+488,ox+272,oy+488),fill='#65ffff',width=2)
b.convert('RGB').save(P/'recovery-guide.png')

b=Image.new('RGBA',raw.size,'#263443');b.alpha_composite(raw);d=ImageDraw.Draw(b)
for index,current,target in [(5,(177,153),(165,170)),(6,(164,140),(183,128))]:
    ox,oy=index%4*384,512;d.rectangle((ox+1,oy+1,ox+382,oy+510),outline='#a6bccb',width=2)
    x,y=current;d.ellipse((ox+x-6,oy+y-6,ox+x+6,oy+y+6),outline='#ff8c8c',width=3)
    x,y=target;d.ellipse((ox+x-7,oy+y-7,ox+x+7,oy+y+7),outline='#68ffb6',width=3)
    d.line((ox+current[0],oy+current[1],ox+x,oy+y),fill='#68ffb6',width=3)
    d.text((ox+5,oy+8),f'KEY{index+1}: collar({x},{y}), feet fixed',font=font,fill='white')
    d.line((ox+95,oy+468,ox+180,oy+468),fill='#65ffff',width=2);d.line((ox+190,oy+488,ox+272,oy+488),fill='#65ffff',width=2)
b.convert('RGB').save(P/'half-recovery-guide.png')

seed=raw.crop((1152,512,1536,1024));guide=raw.copy();upper=seed.copy();alpha=upper.getchannel('A');alpha.paste(0,(0,350,384,512));upper.putalpha(alpha)
t=-.03;c,s=math.cos(t),math.sin(t);px,py=195,310;tx=px-c*px+s*py;ty=py-s*px-c*py+12;dx=c*tx+s*ty;dy=-s*tx+c*ty
upper=upper.transform((384,512),Image.Transform.AFFINE,(c,s,-dx,-s,c,-dy),Image.Resampling.BICUBIC)
lower=seed.copy();alpha=lower.getchannel('A');alpha.paste(0,(0,0,384,345));lower.putalpha(alpha)
pose=Image.new('RGBA',(384,512));pose.alpha_composite(lower);pose.alpha_composite(upper)
guide.paste((0,0,0,0),(768,512,1152,1024));guide.alpha_composite(pose,(768,512));guide.save(P/'near-rest-pose-guide.png')
