"""Non-AA owner labels and mandatory visible crossing events from actual source masks."""
import argparse,collections,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image
import OpenEXR
p=argparse.ArgumentParser();p.add_argument('--renders',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--profile',action='store_true');p.add_argument('--columns',type=int,default=2);a=p.parse_args()
if a.output.exists():raise ValueError('Use fresh owner package')
a.output.mkdir(parents=True);receipt=json.loads((a.renders/('receipt.json' if a.profile else 'owner-receipt.json')).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
    with OpenEXR.File(str(p)) as f:
        ch=f.channels();key=next(iter(ch));v=ch[key].pixels;v=v[:,:,0] if v.ndim==3 else v
    if not np.isfinite(v).all() or not np.isin(np.rint(v),[0,1,2,3,4] if a.profile else [0,1,2,3]).all():raise ValueError('Invalid integer owner pass')
    values=np.rint(v).astype(np.uint8);values[values==4]=3
    return values
def components(mask):
    visited=np.zeros(mask.shape,bool);groups=[]
    for yy,xx in zip(*np.nonzero(mask)):
        if visited[yy,xx]:continue
        queue=collections.deque([(int(xx),int(yy))]);visited[yy,xx]=True;pts=[]
        while queue:
            x,y=queue.popleft();pts.append((x,y))
            for nx,ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
                if 0<=nx<512 and 0<=ny<512 and mask[ny,nx] and not visited[ny,nx]:visited[ny,nx]=True;queue.append((nx,ny))
        if len(pts)>=32:groups.append(np.array(pts))
    return groups
views=sorted({s['view'] for s in receipt['samples']});counts={v:sum(s['view']==v for s in receipt['samples']) for v in views}
if a.columns<1 or a.columns>8:raise ValueError('Invalid columns')
records=[];sheets={v:Image.new('RGBA',(512*a.columns,512*math.ceil(counts[v]/a.columns))) for v in views}
for sample in receipt['samples']:
    view,k=sample['view'],sample['key'];src=a.renders/view/f'{k:02}';dr=a.output/view/f'{k:02}';dr.mkdir(parents=True)
    visible=read(src/('dressed-id.exr' if a.profile else 'visible.exr'));right=read(src/('right-amodal-id.exr' if a.profile else 'right-amodal.exr'))==1;left=read(src/('left-amodal-id.exr' if a.profile else 'left-amodal.exr'))==2
    cross=right&left&np.isin(visible,[1,2]);events=[]
    for owner,code in [('r',1),('l',2)]:
        for pts in components(cross&(visible==code)):
            center=np.median(pts,axis=0);xy=pts[np.argmin(np.linalg.norm(pts-center,axis=1))].tolist()
            x0,y0=pts.min(axis=0).tolist();x1,y1=(pts.max(axis=0)+1).tolist()
            events.append({'id':f'{owner}-{len(events)}','expected_foreground':owner,'source_xy':xy,'source_box':[x0,y0,x1,y1],'pixels':len(pts),
                'observed_foreground':'unknown','art_xy':None,'review':'unconfirmed','notes':''})
    Image.fromarray(visible).save(dr/'visible-id.png');Image.fromarray(right.astype(np.uint8)*255).save(dr/'right-amodal.png')
    Image.fromarray(left.astype(np.uint8)*255).save(dr/'left-amodal.png');Image.fromarray(cross.astype(np.uint8)*255).save(dr/'crossing-mask.png')
    colors=np.array([[0,0,0,0],[25,135,255,255],[247,125,22,255],[105,109,114,255]],np.uint8);color=Image.fromarray(colors[visible]);color.save(dr/'visible-color.png')
    sheets[view].paste(color,(k%a.columns*512,k//a.columns*512))
    paths={name:str(dr/(name+'.png')) for name in ['visible-id','right-amodal','left-amodal','crossing-mask','visible-color']}
    records.append({**sample,'paths':paths,'sha256':{n:sha(Path(path)) for n,path in paths.items()},'crossing_pixels':int(cross.sum()),'events':events})
for v,im in sheets.items():im.save(a.output/(v+'-owner-guide.png'))
manifest={'schema':'source-leg-occlusion-v1','canvas':[512,512],'blend_sha256':receipt['blend_sha256'],'motion_sha256':receipt['motion_sha256'],
    'owner_derivation':'Actual bone weight groups, integer non-AA IndexOB and isolated complete leg geometry; not predicted art labels',
    'records':records,'required_rule':'Every visible source crossing event requires independent generated-image foreground-owner review. Unknown means blocked.'}
(a.output/'owner-index.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('OWNER_PACKED',len(records),'frames;',sum(len(r['events']) for r in records),'visible crossing review regions')
