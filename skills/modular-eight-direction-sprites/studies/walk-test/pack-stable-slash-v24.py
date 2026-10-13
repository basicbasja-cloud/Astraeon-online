"""Shared-scale packing; one visible boot is calibration, the other is held out."""
import argparse,json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'research/sprite-animation/stable-hand-sweep-v24'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sole(im,a,b):
    alpha=np.asarray(im)[:,:,3];h,w=alpha.shape;y0=int(h*.70);x0=int(w*a);x1=int(w*b);roi=alpha[y0:,x0:x1];ys,xs=np.where(roi>128)
    if not len(ys):raise ValueError('Missing boot in declared ROI')
    y=int(ys.max());x=float(np.median(xs[ys==y]))+x0
    return [x,y+y0]
def main():
    p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);p.add_argument('--bank',required=True);args=p.parse_args()
    args.raw=args.raw.resolve();im=Image.open(args.raw).convert('RGBA');cells=[];boxes=[]
    for i in range(8):
        box=[round(i%4*im.width/4),round(i//4*im.height/2),round((i%4+1)*im.width/4),round((i//4+1)*im.height/2)];cells.append(im.crop(box));boxes.append(box)
    alpha=np.asarray(cells[0])[:,:,3];ys,xs=np.where(alpha>128);scale=360/(ys.max()-ys.min()+1);directory=OUT/args.bank/'frames';directory.mkdir(parents=True,exist_ok=True)
    frames=[];durations=[100,100,60,60,80,100,100,120];times=[0,100,200,260,320,400,500,600]
    for i,cell in enumerate(cells):
        l=sole(cell,.08,.53);r=sole(cell,.55,.98);dx=168-scale*l[0];dy=456-scale*l[1]
        packed=cell.transform((512,512),Image.Transform.AFFINE,(1/scale,0,-dx/scale,0,1/scale,-dy/scale),Image.Resampling.BICUBIC)
        # Only fully transparent/sub-visible noise is cleaned; no body painting or limb warp.
        arr=np.array(packed);arr[arr[:,:,3]<=1]=0;packed=Image.fromarray(arr)
        path=directory/f'{i:02}.png';packed.save(path)
        frames.append({'key':i,'time_ms':times[i],'duration_ms':durations[i],'path':str(path.relative_to(ROOT)),'sha256':sha(path),'raw_cell':boxes[i],
            'global_scale':scale,'whole_frame_translation_xy':[dx,dy],'raw_calibration_boot_xy':l,'raw_held_out_boot_xy':r,
            'calibration_boot_xy':[168,456],'held_out_boot_xy':[scale*r[0]+dx,scale*r[1]+dy],
            'boot_observation_scope':'Lowest visible alpha>128 surface in declared screen-side ROIs, not an anatomical owner/world contact or stable tracked heel vertex.'})
    base=frames[0]['held_out_boot_xy']
    for f in frames:f['held_out_boot_delta_xy']=[f['held_out_boot_xy'][j]-base[j] for j in [0,1]]
    report={'raw':str(args.raw.relative_to(ROOT)),'raw_sha256':sha(args.raw),'global_scale':scale,'frames':frames,
        'calibration':'One screen-left boot aligns the whole frame; excluded from independent contact validation. Shared scale, no body warp or per-frame silhouette resizing.',
        'max_held_out_x_delta_px':max(abs(f['held_out_boot_delta_xy'][0]) for f in frames),'max_held_out_y_delta_px':max(abs(f['held_out_boot_delta_xy'][1]) for f in frames),
        'source_stance':'Source sole vertices fixed; painted lowest-alpha points are surface diagnostics, not recovered vertex trajectories.',
        'physical_contacts_verified':False,'user_approved':False,'painted_parts_complete':False}
    e=OUT/'evidence';e.mkdir(exist_ok=True);(e/(args.bank+'-packing.json')).write_text(json.dumps(report,indent=2)+'\n')
    board=Image.new('RGB',(2048,1104),'#272727');draw=ImageDraw.Draw(board);plain=Image.new('RGBA',(2048,1024))
    targets=Image.new('RGB',(2048,1104),'#272727');td=ImageDraw.Draw(targets)
    for i,f in enumerate(frames):
        image=Image.open(ROOT/f['path']).convert('RGBA');x=i%4*512;y=i//4*552;board.paste(image,(x,y+40),image);targets.paste(image,(x,y+40),image);plain.paste(image,(i%4*512,i//4*512));draw.text((x+10,y+8),f'{i+1} / {f["time_ms"]}ms / {f["duration_ms"]}ms',fill='white')
        for point,col in [([168,456],'#29d5ff'),(base,'#ffb341')]:
            px=point[0]+x;py=point[1]+y+40;td.line((px-12,py,px+12,py),fill=col,width=2);td.line((px,py-12,px,py+12),fill=col,width=2)
    board.save(OUT/args.bank/'eight-key-review.png');plain.save(OUT/args.bank/'eight-body.png');targets.save(OUT/args.bank/'boot-target-review.png')
    print('PACKED',args.bank,'shared scale',scale,'held-out deltas',report['max_held_out_x_delta_px'],report['max_held_out_y_delta_px'])
if __name__=='__main__':main()
