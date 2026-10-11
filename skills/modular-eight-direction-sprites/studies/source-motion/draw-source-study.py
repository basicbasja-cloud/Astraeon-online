"""Draw source-known anatomical guides, not inferred screenshot skeletons."""
import argparse,json,math
from pathlib import Path
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);a=p.parse_args();data=json.loads(a.input.read_text());out=a.input.parent
DIRS=['S','SE','E','NE','N','NW','W','SW'];colors={'right':'#4ba0ff','left':'#ff9740','torso':'#eceef2'}
def projection(v,view=1):
    x,y,z=v;theta=view*math.pi/4;x,y=x*math.cos(theta)-y*math.sin(theta),x*math.sin(theta)+y*math.cos(theta)
    return (96+x*70,182+y*35-z*70*math.cos(math.pi/6))
def diagram(frame,view=1):
    im=Image.new('RGB',(192,192),'#26303b');draw=ImageDraw.Draw(im);j=frame['root_relative_joints'];pts={n:projection(v,view) for n,v in j.items()}
    draw.line((0,182,192,182),fill='#4e5967');draw.line((93,182,99,182),fill='#5fea9d',width=2)
    chains=[('torso',['pelvis','spine.low','spine.mid','chest','neck','head'])]
    for side in ['right','left']:
        chains.extend([(side,['chest',side+'.clavicle',side+'.shoulder',side+'.elbow',side+'.wrist']),
                       (side,['pelvis',side+'.hip',side+'.knee',side+'.ankle',side+'.ball',side+'.toe'])])
        for finger in ['thumb','index','middle','ring','pinky']:chains.append((side,[side+'.wrist']+[f'{side}.{finger}.{k}' for k in range(1,5)]))
    for color,chain in chains:
        draw.line([pts[n] for n in chain],fill=colors[color],width=2 if len(chain)>5 else 1)
    for n,xy in pts.items():
        if any('.'+f+'.' in n for f in ['thumb','index','middle','ring','pinky']):continue
        x,y=xy;draw.ellipse((x-2,y-2,x+2,y+2),fill=colors['right' if n.startswith('right') else 'left' if n.startswith('left') else 'torso'])
    return im
for clip in data['clips']:
    directory=out/clip['name'];directory.mkdir(exist_ok=True);fs=clip['frames'];cols=8;cell=(192,222)
    board=Image.new('RGB',(cols*cell[0],math.ceil(len(fs)/cols)*cell[1]),'#202630');draw=ImageDraw.Draw(board)
    for i,f in enumerate(fs):
        im=diagram(f);im.save(directory/f'{i:03}-SE.png');x=i%cols*192;y=i//cols*222;board.paste(im,(x,y+28))
        draw.text((x+3,y+2),f'{clip["name"]} {i}\nsource {f["time_seconds"]:.3f}s',fill='white')
    board.save(out/f'{clip["name"]}-all-source-samples.png')
    selected=[round(i*(len(fs)-1)/7) for i in range(8)]  # overview only, NOT production key selection
    b=Image.new('RGB',(192*8,222*8),'#202630');d=ImageDraw.Draw(b)
    for view,heading in enumerate(DIRS):
        for k,i in enumerate(selected):
            x=k*192;y=view*222;b.paste(diagram(fs[i],view),(x,y+28));d.text((x+3,y+2),f'{heading} source {i}\n{fs[i]["time_seconds"]:.3f}s',fill='white')
    b.save(out/f'{clip["name"]}-eight-views-overview.png')
    print(clip['name'],len(fs),'source samples, measured root travel',fs[0]['root_world'],fs[-1]['root_world'])
