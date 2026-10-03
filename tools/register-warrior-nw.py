"""Replace drifting NW views with three strips authored from the approved rear seed."""
import argparse,json,shutil
from pathlib import Path
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw
parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);parser.add_argument('--direction',choices=['NW','W'],default='NW');parser.add_argument('--modes',default='walk,run,sprint');args=parser.parse_args()
modes=args.modes.split(',');assert all(m in ('walk','run','sprint') for m in modes)
target_row={'NW':5,'W':6}[args.direction]
ROOT=Path(__file__).resolve().parents[1];source=args.source;out=ROOT/'authoring/characters/painted-v4'
im=Image.open(source).convert('RGBA');rgba=np.array(im);labels,n=ndimage.label(rgba[:,:,3]>100);parts={}
for k,s in enumerate(ndimage.find_objects(labels),1):
    if s is None or np.sum(labels[s]==k)<900:continue
    y0,y1=s[0].start,s[0].stop;x0,x1=s[1].start,s[1].stop
    assert 0<x0<x1<im.width and 0<y0<y1<im.height,('clipped NW body',k)
    row=min(len(modes)-1,int((y0+(y1-y0)*.45)/(im.height/len(modes))));col=min(7,int((x0+x1)/2/(im.width/8)))
    assert (row,col) not in parts,('joined NW body',row,col);parts[row,col]=(k,x0,y0,x1,y1)
assert len(parts)==8*len(modes),('direction strip needs eight complete bodies per mode',len(parts))
target=out/('warrior-NW-three-gaits-source.png' if args.direction=='NW' else 'warrior-W-sprint-source.png')
if source.resolve()!=target.resolve():shutil.copyfile(source,target)
path=ROOT/'world/v3/warrior-painted-locomotion.json';data=json.loads(path.read_text())
for row,mode in enumerate(modes):
    clip=data['clips'][mode];atlas=Image.open(ROOT/clip['atlas']).convert('RGBA');cell=data['cellSize']
    reference=[]
    for col in range(8):
        a=np.array(atlas.crop((col*cell,4*cell,(col+1)*cell,5*cell)))[:,:,3];ys,xs=np.nonzero(a>100);reference.append(ys.max()-ys.min()+1)
    scale=float(np.median(reference))/float(np.median([parts[row,c][4]-parts[row,c][2] for c in range(8)]))
    baseline=float(np.median([parts[row,c][4] for c in range(8)]));reviews=[]
    atlas.paste((0,0,0,0),(0,target_row*cell,8*cell,(target_row+1)*cell))
    for col in range(8):
        k,x0,y0,x1,y1=parts[row,col];x0=max(0,x0-3);y0=max(0,y0-3);x1=min(im.width,x1+3);y1=min(im.height,y1+3)
        image=rgba[y0:y1,x0:x1].copy();mask=labels[y0:y1,x0:x1]==k;image[:,:,3]=np.where(ndimage.binary_dilation(mask,iterations=3),image[:,:,3],0)
        rgb=image[:,:,:3].astype(float);hair=mask&(np.indices(mask.shape)[0]<mask.shape[0]*.4)&(rgb[:,:,2]>rgb[:,:,0]+7)&(rgb[:,:,2]>rgb[:,:,1]+2)&(rgb[:,:,0]>70);ys,xs=np.nonzero(hair);assert len(xs)>25
        sprite=Image.fromarray(image).resize((round(image.shape[1]*scale),round(image.shape[0]*scale)),Image.Resampling.LANCZOS)
        left=round(160-float(np.mean(xs))*scale);top=round(264-(baseline-y0)*scale)
        assert left>=2 and top>=2 and left+sprite.width<=318 and top+sprite.height<=318,(mode,col,'NW overflow')
        atlas.alpha_composite(sprite,(col*cell+left,target_row*cell+top))
        frame=clip['frames'][target_row*8+col];frame['sourceRect']=[x0,y0,x1-x0,y1-y0];frame['sourceFile']='authoring/characters/painted-v4/'+target.name
        review=Image.new('RGBA',(cell,cell),'#cad3d5');review.alpha_composite(sprite,(left,top));ImageDraw.Draw(review).line([(0,264),(cell,264)],fill='#61806b');reviews.append(review.convert('RGB'))
    destination=ROOT/clip['atlas'];temporary=destination.with_name(destination.stem+'.tmp.webp');atlas.save(temporary,quality=95,method=6);temporary.replace(destination)
    reviews[0].save(out/f'{clip["clip"]}-{args.direction}.gif',save_all=True,append_images=reviews[1:],duration={'walk':110,'run':75,'sprint':55}[mode],loop=0)
    sheet=Image.new('RGB',(cell*8,cell),'#cad3d5')
    for col,picture in enumerate(reviews):sheet.paste(picture,(col*cell,0))
    sheet.save(out/f'{clip["clip"]}-{args.direction}-registration.jpg',quality=95)
    print(mode,args.direction,'body scale',round(scale,3))
data.setdefault('directionRepairs',{})[args.direction]={'source':'authoring/characters/painted-v4/'+target.name,'reason':'consistent facing and full authored strip','modes':modes}
temporary=path.with_suffix('.json.tmp');temporary.write_text(json.dumps(data,indent=2)+'\n');temporary.replace(path)
