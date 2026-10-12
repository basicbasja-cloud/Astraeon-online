"""Package real source depth and cutaway guides; never infer drawn leg identity."""
import argparse,hashlib,json,shutil,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import OpenEXR
p=argparse.ArgumentParser();p.add_argument('--renders',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--columns',type=int,default=2);a=p.parse_args()
if a.output.exists():raise ValueError('Fresh output required')
a.output.mkdir(parents=True);receipt=json.loads((a.renders/'receipt.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(path):
    with OpenEXR.File(str(path)) as f:
        v=next(iter(f.channels().values())).pixels
        return (v[:,:,0] if v.ndim==3 else v).copy()
views=sorted({s['view'] for s in receipt['samples']});counts={v:sum(s['view']==v for s in receipt['samples']) for v in views}
if a.columns<1 or a.columns>8:raise ValueError('Invalid columns')
records=[];sheets={(v,mode):Image.new('RGBA',(512*a.columns,512*math.ceil(counts[v]/a.columns))) for v in views for mode in ['dressed','cutaway','depth','proximal']}
lo,hi=receipt['fixed_display_depth_range']
for sample in receipt['samples']:
    v,k=sample['view'],sample['key'];src=a.renders/v/f'{k:02}';dst=a.output/v/f'{k:02}';dst.mkdir(parents=True);paths={};depths={};ids={}
    for mode in ['dressed','cutaway','right-amodal','left-amodal','pelvis-amodal']:
        labels=np.rint(read(src/(mode+'-id.exr'))).astype(np.uint8);z=read(src/(mode+'-depth.exr')).astype(np.float32)
        if not np.isin(labels,[0,1,2,3,4]).all():raise ValueError('Owner labels invalid')
        valid=labels>0
        if not np.isfinite(z[valid]).all() or not ((z[valid]>=lo)&(z[valid]<=hi)).all():raise ValueError('Metric depth outside fixed declared range')
        Image.fromarray(labels).save(dst/(mode+'-id.png'));np.save(dst/(mode+'-depth.npy'),z)
        shutil.copyfile(src/(mode+'.png'),dst/(mode+'.png'))
        for suffix in ['-id.png','-depth.npy','.png']:paths[mode+suffix]=str(dst/(mode+suffix))
        depths[mode]=z;ids[mode]=labels
    r,l=ids['right-amodal']==1,ids['left-amodal']==2;both=r&l
    delta=depths['left-amodal']-depths['right-amodal'];separated=both&(np.abs(delta)>.001)
    expected=np.where(delta>0,1,2);observable=separated&np.isin(ids['cutaway'],[1,2])
    mismatches=int(((ids['cutaway']!=expected)&observable).sum())
    if mismatches:raise ValueError('Actual full source depth disagrees with isolated leg depth')
    order=np.where(separated,expected,0).astype(np.uint8);Image.fromarray(order).save(dst/'nearer-leg-id.png');paths['nearer-leg-id.png']=str(dst/'nearer-leg-id.png')
    rgb=np.zeros((512,512,4),np.uint8);shade=np.rint(np.clip((hi-depths['dressed'])/(hi-lo),0,1)*255).astype(np.uint8)
    rgb[:,:,:3]=shade[:,:,None];rgb[:,:,3]=np.where(ids['dressed']>0,255,0)
    Image.fromarray(rgb).save(dst/'fixed-depth.png');paths['fixed-depth.png']=str(dst/'fixed-depth.png')
    proximal=Image.open(dst/'cutaway.png').convert('RGBA');draw=ImageDraw.Draw(proximal);stats={}
    yy,xx=np.ogrid[:512,:512]
    for side,code,color in [('r',1,'#52aaff'),('l',2,'#ff984a')]:
        b=sample['bones']['thigh_'+side];x,y=b['xy'];cx,cy=sample['bones']['calf_'+side]['xy'];draw.line([(x,y),(cx,cy)],fill=color,width=3);draw.ellipse((x-5,y-5,x+5,y+5),outline='white',width=2)
        draw.text((x+8,y-22 if side=='r' else y+8),'HIP '+side.upper(),fill=color)
        region=(((xx-x)**2+(yy-y)**2)<=24**2)&(ids['right-amodal' if side=='r' else 'left-amodal']==code)
        total=int(region.sum());visible=int((region&(ids['dressed']==code)).sum())
        stats[side]={'sample_pixels':total,'dressed_same_owner_pixels':visible,'visible_fraction':visible/total if total else None,'projection_radius_px':24,'internal_bone_visibility_not_claimed':True}
    proximal.save(dst/'proximal-guide.png');paths['proximal-guide.png']=str(dst/'proximal-guide.png')
    for mode,file in [('dressed','dressed.png'),('cutaway','cutaway.png'),('depth','fixed-depth.png'),('proximal','proximal-guide.png')]:sheets[v,mode].paste(Image.open(dst/file),(k%a.columns*512,k//a.columns*512))
    rd,ld=[sample['bones']['thigh_'+s]['camera_axis_depth'] for s in ['r','l']]
    records.append({**sample,'paths':paths,'sha256':{n:sha(p) for n,p in paths.items()},'hip_near_side':'r' if rd<ld else 'l',
        'hip_depth_difference_scene_units':abs(rd-ld),'proximal_surface_visibility':stats,'overlap_depth_pixels':int(observable.sum()),'isolated_depth_order_mismatch_pixels':mismatches})
for (v,mode),im in sheets.items():im.save(a.output/(v+'-'+mode+'-guide.png'))
shutil.copyfile(a.renders/'receipt.json',a.output/'render-receipt.json')
manifest={'schema':'profile-depth-guides-v1','canvas':[512,512],'blend_sha256':receipt['blend_sha256'],'motion_sha256':receipt['motion_sha256'],
    'fixed_display_depth_range':[lo,hi],'depth_is_raw_scene_units':True,'source_pose_edited':False,'records':records,
    'scope':'Source surface/depth/cutaway proof only. Does not recover generated image hidden pelvis anatomy or validate a moved cloth panel.'}
(a.output/'depth-index.json').write_text(json.dumps(manifest,indent=2)+'\n');print('DEPTH_PACK',len(records),'poses; metric overlap depth verified')
