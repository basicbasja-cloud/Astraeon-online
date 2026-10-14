from pathlib import Path
import json
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parent;s=json.loads((P/'source/source.json').read_text())
for view in ['rear','side']:
    b=Image.new('RGBA',(1536,1024));r=Image.new('RGB',(1536,1080),'#344351');d=ImageDraw.Draw(r)
    for i,f in enumerate(s['frames']):
        im=Image.open(P/f'source/{view}/{i:02}.png').convert('RGBA');x=i%4*384;y=i//4*512;b.alpha_composite(im,(x,y));r.paste(im,(x,i//4*540+25),im);d.text((x+8,i//4*540+5),f'{i+1} / {f["time_seconds"]:.3f}s / bend{f["hip_hinge_degrees"]}deg',fill='white')
    b.save(P/f'{view}-guide.png');r.save(P/f'{view}-source-review.png')
b=Image.new('RGBA',(1536,1024));d=ImageDraw.Draw(b)
for i,f in enumerate(s['frames']):
    offset=[i%4*384,i//4*512];pts={k:[p['xy']['rear'][j]+offset[j] for j in [0,1]] for k,p in f['points'].items()}
    for side,color in [('left','#ff943b'),('right','#389bff')]:
        for a,z in [('hip','knee'),('knee','ankle'),('ankle','toe'),('shoulder','elbow'),('elbow','wrist'),('wrist','palm')]:d.line([pts[side+'.'+a],pts[side+'.'+z]],fill=color,width=5)
    for a,z in [('pelvis','chest'),('chest','neck'),('neck','head')]:d.line([pts[a],pts[z]],fill='white',width=5)
    for p in pts.values():d.ellipse([p[0]-3,p[1]-3,p[0]+3,p[1]+3],fill='white')
b.save(P/'joint-guide.png')
