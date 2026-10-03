"""Assemble complete authored sprint bodies, with SW from a separate painted strip.
Two overlapping source bodies use the corresponding complete run poses. Nothing
is repainted or constructed from fragments; provenance records the repair.
"""
import sys,json,shutil
from pathlib import Path
import numpy as np
from scipy import ndimage
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
output=ROOT/'authoring/characters/painted-v4';output.mkdir(parents=True,exist_ok=True)
def read(path,strip=False):
    rgba=np.array(Image.open(path).convert('RGBA'));labels,n=ndimage.label(rgba[:,:,3]>100);parts={}
    for k,s in enumerate(ndimage.find_objects(labels),1):
        if s is None or np.sum(labels[s]==k)<700:continue
        y0,y1=s[0].start,s[0].stop;x0,x1=s[1].start,s[1].stop
        if y1-y0>230 and not strip:continue
        assert 0<x0<x1<rgba.shape[1] and 0<y0<y1<rgba.shape[0],('clipped body',path,k)
        row=7 if strip else min(7,int((y0+(y1-y0)*.45)/(rgba.shape[0]/8)))
        col=min(7,int((x0+x1)/2/(rgba.shape[1]/8)))
        assert (row,col) not in parts,('duplicate body',row,col)
        parts[row,col]=(k,x0,y0,x1,y1)
    return rgba,labels,parts
main=read(sys.argv[1]);sw=read(sys.argv[2],True);run=read(sys.argv[3])
assert len(main[2])==54 and len(sw[2])==8 and len(run[2])==64
sources={p:(main,t,'sprint') for p,t in main[2].items()}
sources.update({p:(sw,t,'sprint-SW') for p,t in sw[2].items()})
for pos in ((5,2),(6,2)):
    assert pos not in sources;sources[pos]=(run,run[2][pos],'run-repair')
assert len(sources)==64
def head_width(src):
    widths=[]
    for k,x0,y0,x1,y1 in src[2].values():
        mask=src[1][y0:y1,x0:x1]==k;rgb=src[0][y0:y1,x0:x1,:3].astype(float)
        hair=mask&(np.indices(mask.shape)[0]<mask.shape[0]*.40)&(rgb[:,:,2]>rgb[:,:,0]+7)&(rgb[:,:,2]>rgb[:,:,1]+2)&(rgb[:,:,0]>70)
        yy,xx=np.nonzero(hair)
        assert len(xx)>25,('cannot register silver hair',k)
        widths.append(np.quantile(xx,.95)-np.quantile(xx,.05))
    return float(np.median(widths))
reference=head_width(main);scales={'sprint':1,'sprint-SW':reference/head_width(sw),'run-repair':reference/head_width(run)}
atlas=Image.new('RGBA',(2560,2560));provenance=[]
for (row,col),(src,(k,x0,y0,x1,y1),kind) in sorted(sources.items()):
    rgba,labels,parts=src;scale=scales[kind];baseline=float(np.median([p[4] for (r,c),p in parts.items() if r==row]))
    x0=max(0,x0-3);y0=max(0,y0-3);x1=min(rgba.shape[1],x1+3);y1=min(rgba.shape[0],y1+3)
    mask=labels[y0:y1,x0:x1]==k;image=rgba[y0:y1,x0:x1].copy();image[:,:,3]=np.where(ndimage.binary_dilation(mask,iterations=3),image[:,:,3],0)
    sprite=Image.fromarray(image).resize((round(image.shape[1]*scale),round(image.shape[0]*scale)),Image.Resampling.LANCZOS)
    yy,xx=np.nonzero(mask[:max(1,round(mask.shape[0]*.18))]);left=round(160-float(np.mean(xx))*scale);top=round(264-(baseline-y0)*scale)
    assert left>=3 and top>=3 and left+sprite.width<317 and top+sprite.height<317,('registration overflow',row,col,left,top,sprite.size)
    atlas.alpha_composite(sprite,(col*320+left,row*320+top));provenance.append({'row':row,'phase':col,'source':kind})
atlas.save(output/'warrior-sprint-complete-source.png')
for path,name in [(sys.argv[1],'warrior-sprint-seven-directions-source.png'),(sys.argv[2],'warrior-sprint-SW-source.png')]:
    if Path(path).resolve()!=(output/name).resolve():shutil.copyfile(path,output/name)
(output/'sprint-assembly.json').write_text(json.dumps(provenance,indent=2)+'\n')
print('Registered 54 sprint bodies, eight SW bodies and two complete run pose repairs')
