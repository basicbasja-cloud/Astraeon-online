"""Draw an original joint diagram for whole-strip generation, not game artwork.

Red = anatomical left, blue = anatomical right; these exchange stance at phase4.
The diagram gives the image model explicit poses instead of repeated costumes.
"""
from PIL import Image,ImageDraw
from pathlib import Path
import math,json
out=Path('authoring/characters/gait-v48');out.mkdir(parents=True,exist_ok=True)
dirs=['S','SE','E','NE','N','NW','W','SW']
im=Image.new('RGB',(2048,2048),'#e1ded2');d=ImageDraw.Draw(im)
for row,name in enumerate(dirs):
    a=row*math.pi/4;forward=(math.sin(a),math.cos(a));right=(math.cos(a),-math.sin(a))
    def project(x,y,z,col):return (col*256+128+x*83,row*256+228+y*45-z*90)
    for col in range(8):
        q=col/8;ox=col*256;oy=row*256
        d.text((ox+8,oy+8),f'{name} {col+1}: '+('LEFT support' if col<4 else 'RIGHT support'),fill='#253243')
        d.line([(ox+8,oy+228),(ox+248,oy+228)],fill='#9eaa99',width=2)
        legs=[]
        for side,color,phase in [(-1,'#cf403d',q),(1,'#356fc5',(q+.5)%1)]:
            # Full stride: planted boot travels backward relative to the hip;
            # the other boot swings forward with bent knee and raised ankle.
            stance=phase<.5
            u=phase*2 if stance else (phase-.5)*2
            along=.37-.74*u if stance else -.37+.74*(u*u*(3-2*u))
            lift=0 if stance else .23*math.sin(math.pi*u)
            hip=(right[0]*side*.13,right[1]*side*.13,1.10)
            ankle=(right[0]*side*.13+forward[0]*along,right[1]*side*.13+forward[1]*along,.09+lift)
            knee=(right[0]*side*.13+forward[0]*(along*.48+.17+.17*lift),right[1]*side*.13+forward[1]*(along*.48+.17+.17*lift),.59+lift*.38)
            toe=(ankle[0]+forward[0]*.15,ankle[1]+forward[1]*.15,ankle[2]-.05)
            legs.append((side,color,hip,knee,ankle,toe))
        # Draw back leg first, preserving identities through the overlap.
        for side,color,hip,knee,ankle,toe in sorted(legs,key=lambda p:p[4][1]):
            pts=[project(*p,col) for p in [hip,knee,ankle,toe]]
            d.line(pts,fill=color,width=14)
            for x,y in pts[:-1]:d.ellipse((x-8,y-8,x+8,y+8),fill=color,outline='#252c36',width=1)
        torso=[project(*p,col) for p in [(-right[0]*.25,-right[1]*.25,1.71),(right[0]*.25,right[1]*.25,1.71),(right[0]*.17,right[1]*.17,1.10),(-right[0]*.17,-right[1]*.17,1.10)]]
        d.polygon(torso,fill='#5b6772',outline='#252c36')
        x,y=project(0,0,1.98,col);d.ellipse((x-20,y-23,x+20,y+23),fill='#b7b7ba',outline='#333d49',width=2)
        nx,ny=project(forward[0]*.25,forward[1]*.25,1.98,col);d.line((x,y,nx,ny),fill='#2e3d48',width=4)
        for side,color in [(-1,'#cf403d'),(1,'#356fc5')]:
            shift=-math.cos(q*math.tau)*side*.22
            sh=(right[0]*side*.25,right[1]*side*.25,1.66)
            el=(right[0]*side*.29+forward[0]*shift,right[1]*side*.29+forward[1]*shift,1.35)
            hand=(right[0]*side*.30+forward[0]*shift*1.2,right[1]*side*.30+forward[1]*shift*1.2,1.18)
            d.line([project(*p,col) for p in [sh,el,hand]],fill=color,width=10)
im.save(out/'joint-guide.png')
print(out/'joint-guide.png')

