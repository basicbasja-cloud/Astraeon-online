"""Preserve high-detail four-pose art masters and declare returned-grid calibration."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

p=argparse.ArgumentParser();p.add_argument('--sheet',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--row-offset',type=int,default=0,help='One second-row grid offset, never individual pose fitting')
a=p.parse_args()
if a.output.exists():raise ValueError('Use a fresh output directory')
im=Image.open(a.sheet).convert('RGBA');w,h=im.size
if w!=h or w%2:raise ValueError('Expected returned square 2x2 sheet')
cell=w//2;row_pitch=cell+a.row_offset
if not cell-32<=row_pitch<=cell:raise ValueError('Unsupported bounded grid calibration')
master=512;apng_ms=[333,334,333,333];gif_ms=[330,340,330,330]
a.output.mkdir(parents=True);(a.output/'frames').mkdir();frames=[];cards=[];bounds=[]
for k in range(4):
    x,y=k%2*cell,k//2*row_pitch;c=im.crop((x,y,x+cell,y+cell))
    alpha=np.asarray(c)[:,:,3];ys,xs=np.nonzero(alpha>64)
    if not len(xs):raise ValueError('Empty frame')
    edge=max(alpha[0].max(),alpha[-1].max(),alpha[:,0].max(),alpha[:,-1].max())
    if edge>64:raise ValueError('Meaningful subject clipped at cell edge')
    f=c.resize((master,master),Image.Resampling.LANCZOS);f.save(a.output/'frames'/f'{k:02}.png');frames.append(f)
    bg=Image.new('RGBA',f.size,'#272727');bg.alpha_composite(f);cards.append(bg.convert('RGB'))
    bounds.append({'key':k,'crop':[x,y,cell,cell],'alpha_over_64_bounds':[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1],
                   'edge_max_alpha':int(edge)})
frames[0].save(a.output/'walk-quality.png',save_all=True,append_images=frames[1:],duration=apng_ms,loop=0,disposal=0,blend=0)
frames[0].save(a.output/'walk-quality.webp',save_all=True,append_images=frames[1:],duration=apng_ms,loop=0,lossless=True,quality=100,method=6,exact=True)
palette_canvas=Image.new('RGB',(master*4,master))
for k,f in enumerate(cards):palette_canvas.paste(f,(master*k,0))
palette=palette_canvas.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
g=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in cards]
g[0].save(a.output/'walk-quality.gif',save_all=True,append_images=g[1:],duration=gif_ms,loop=0,disposal=2,optimize=False)
board=Image.new('RGB',(master*2,(master+24)*2),'#272727');d=ImageDraw.Draw(board)
strip=Image.new('RGBA',(master*4,master))
for k,f in enumerate(cards):
    board.paste(f,(k%2*master,k//2*(master+24)+24));d.text((k%2*master+12,k//2*(master+24)+6),f'{k+1} / source {[0,10,20,30][k]}',fill='#ece4d6')
    strip.paste(frames[k],(k*master,0))
board.save(a.output/'quality-review.png');strip.save(a.output/'walk-quality-strip.png')
report={'schema':'four-pose-quality-review-v1','sheet_sha256':hashlib.sha256(a.sheet.read_bytes()).hexdigest(),
        'actual_returned_sheet':[w,h],'requested_sheet':[1024,1024],'raw_cell':[cell,cell],
        'master_canvas':[master,master],'global_scale':master/cell,'row_pitch':row_pitch,'row_offset':a.row_offset,
        'calibration_basis':'Common lower-row displacement: upper hair tops y51; lower y36/y26; one -20 row offset. Manual grid calibration, not rig-contact recovery.',
        'per_frame_bbox_fit':False,'per_frame_scale':False,'source_pose_indices':[0,10,20,30],
        'frames':bounds,'apng_delays_ms':apng_ms,'gif_delays_ms':gif_ms,
        'art_review':'Premium reference-directed candidate; user acceptance pending',
        'motion_review':'Guide-conditioned original art; generated anatomy, world contacts and intentional bob remain unverified',
        'complete_replaceable_painted_parts':False,'release_ready':False,
        'format_notes':'PNG/APNG and lossless WebP preserve full RGBA; GIF uses one 256-color global palette and opaque dark review background.'}
(a.output/'quality-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
print('QUALITY_PACKED',im.size,'to',master,'square masters;',len(frames),'poses; row pitch',row_pitch)
