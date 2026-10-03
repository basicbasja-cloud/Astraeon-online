"""Register whole authored bodies; never redraw, splice or synthesize their limbs.

Usage: python tools/register-painted-locomotion.py walk.png run.png [sprint.png]
Source components must contain eight complete bodies in each of eight directions.
"""
import argparse,json,shutil
from pathlib import Path
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
DIRECTIONS=['S','SE','E','NE','N','NW','W','SW']
parser=argparse.ArgumentParser();parser.add_argument('walk',type=Path);parser.add_argument('run',type=Path);parser.add_argument('sprint',type=Path,nargs='?');args=parser.parse_args()
out=ROOT/'authoring/characters/painted-v4';out.mkdir(parents=True,exist_ok=True)
data={'version':4,'directions':DIRECTIONS,'cellSize':320,'referenceHeight':176,'clips':{}}
for mode,source in [('walk',args.walk),('run',args.run),('sprint',args.sprint)]:
    if source is None:continue
    im=Image.open(source).convert('RGBA');rgba=np.array(im);labels,n=ndimage.label(rgba[:,:,3]>100);components={}
    for k,slices in enumerate(ndimage.find_objects(labels),1):
        if slices is None or np.sum(labels[slices]==k)<700:continue
        ys,xs=slices;y0,y1=ys.start,ys.stop;x0,x1=xs.start,xs.stop
        assert 0<x0<x1<im.width and 0<y0<y1<im.height,('clipped source',mode,k)
        row=min(7,int((y0+(y1-y0)*.45)/(im.height/8)))
        col=min(7,int((x0+x1)/2/(im.width/8)))
        assert (row,col) not in components,('merged/doubled body',mode,row,col)
        components[row,col]=(k,x0,y0,x1,y1)
    assert len(components)==64,(mode,'requires 64 complete bodies',len(components))
    # One scale for the entire clip. Run head size is matched to walk, preserving
    # the shorter forward-lean silhouette rather than stretching it to stand.
    head_widths=[]
    for k,x0,y0,x1,y1 in components.values():
        rgb=rgba[y0:y1,x0:x1,:3].astype(float);mask=labels[y0:y1,x0:x1]==k
        hair=mask&(np.indices(mask.shape)[0]<mask.shape[0]*.40)&(rgb[:,:,2]>rgb[:,:,0]+7)&(rgb[:,:,2]>rgb[:,:,1]+2)&(rgb[:,:,0]>70)
        yy,xx=np.nonzero(hair)
        assert len(xx)>25,('cannot register silver hair',mode,k)
        head_widths.append(np.quantile(xx,.95)-np.quantile(xx,.05))
    head_width=float(np.median(head_widths))
    if mode=='walk':walk_head=head_width;scale=176/float(np.median([p[4]-p[2] for p in components.values()]));walk_scale=scale
    else:scale=walk_scale*walk_head/head_width
    atlas=Image.new('RGBA',(2560,2560));frames=[];reviews=[]
    for row,direction in enumerate(DIRECTIONS):
        baseline=float(np.median([components[row,c][4] for c in range(8)]))
        for col in range(8):
            k,x0,y0,x1,y1=components[row,col]
            x0=max(0,x0-3);y0=max(0,y0-3);x1=min(im.width,x1+3);y1=min(im.height,y1+3)
            isolated=rgba[y0:y1,x0:x1].copy()
            mask=ndimage.binary_dilation(labels[y0:y1,x0:x1]==k,iterations=3)
            isolated[:,:,3]=np.where(mask,isolated[:,:,3],0)
            sprite=Image.fromarray(isolated).resize((round((x1-x0)*scale),round((y1-y0)*scale)),Image.Resampling.LANCZOS)
            yy,xx=np.nonzero((labels[y0:y1,x0:x1]==k)&(np.indices(mask.shape)[0]<(y1-y0)*.18))
            head_x=float(np.mean(xx))
            left=round(160-head_x*scale);top=round(264-(baseline-y0)*scale)
            assert left>=2 and top>=2 and left+sprite.width<=318 and top+sprite.height<=318,('registration overflow',mode,row,col,left,top,sprite.size)
            atlas.alpha_composite(sprite,(col*320+left,row*320+top))
            frames.append({'direction':direction,'phase':col/8,'rect':[col*320,row*320,320,320],'anchor':[160,264],'sourceRect':[x0,y0,x1-x0,y1-y0]})
            cell=Image.new('RGBA',(320,320),'#cad3d5');cell.alpha_composite(sprite,(left,top));draw=ImageDraw.Draw(cell);draw.line([(0,264),(320,264)],fill='#61806b',width=1);reviews.append(cell.convert('RGB'))
    key=f'warrior-{mode}-v4';destination=ROOT/'assets'/f'{key}.webp';temporary=destination.with_name(key+'.tmp.webp');atlas.save(temporary,quality=95,method=6);temporary.replace(destination)
    target=out/f'{key}-source.png'
    if source.resolve()!=target.resolve():shutil.copyfile(source,target)
    review=Image.new('RGB',(2560,2560),'#cad3d5')
    for i,cell in enumerate(reviews):review.paste(cell,(i%8*320,i//8*320))
    review.resize((1024,1024)).save(out/f'{key}-registration.jpg',quality=94)
    data['clips'][mode]={'clip':key,'atlas':f'assets/{key}.webp','cols':8,'rows':8,'frames':frames,'heights':[176]*8,'scale':round(scale,5),'source':f'authoring/characters/painted-v4/{key}-source.png'}
    # Whole strips, displayed at enlarged size for checking knees, cape and loop seam.
    for row in (0,2,4,6):
        reviews[row*8].save(out/f'{key}-{DIRECTIONS[row]}.gif',save_all=True,append_images=reviews[row*8+1:row*8+8],duration={'walk':110,'run':75,'sprint':55}[mode],loop=0)
    print(mode,'64 full bodies, scale',round(scale,3))
destination=ROOT/'world/v3/warrior-painted-locomotion.json';temporary=destination.with_suffix('.json.tmp');temporary.write_text(json.dumps(data,indent=2)+'\n');temporary.replace(destination)
