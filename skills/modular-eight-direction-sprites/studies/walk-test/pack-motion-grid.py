"""Fixed-grid arbitrary-frame review pack; shared scale/padding and explicit clocks."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('--sheet',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--columns',type=int,required=True);p.add_argument('--rows',type=int,required=True);p.add_argument('--source-keys',required=True);p.add_argument('--frame-ms',type=float,default=75);p.add_argument('--source-cycle-ms',type=int,default=1333);a=p.parse_args()
keys=[float(x) for x in a.source_keys.split(',')];keys=[int(x) if x.is_integer() else x for x in keys]
if a.output.exists():raise ValueError('Fresh output required')
if a.columns<1 or a.rows<1 or len(keys)!=a.columns*a.rows or not np.isfinite(keys).all() or not np.isfinite(a.frame_ms) or a.frame_ms<10 or a.source_cycle_ms<len(keys)*10:raise ValueError('Grid/clock mismatch or delay too short for GIF')
im=Image.open(a.sheet).convert('RGBA');w,h=im.size
cw,ch=w/a.columns,h/a.rows;scale=512/max(cw,ch);dw,dh=round(cw*scale),round(ch*scale);pad=((512-dw)//2,512-dh)
frames=[];opaque=[];rows=[]
for k,index in enumerate(keys):
    x,y=k%a.columns*cw,k//a.columns*ch;c=im.crop(tuple(round(v) for v in (x,y,x+cw,y+ch)));alpha=np.array(c)[:,:,3]
    edge=int(max(alpha[0].max(),alpha[-1].max(),alpha[:,0].max(),alpha[:,-1].max()))
    if edge>64:raise ValueError(f'Frame {k+1} clipped at cell edge')
    if np.count_nonzero(alpha>64)<32:raise ValueError('Empty frame')
    cell=c if cw==dw and ch==dh and all(float(v).is_integer() for v in [x,y,cw,ch]) else im.transform((dw,dh),Image.Transform.EXTENT,(x,y,x+cw,y+ch),resample=Image.Resampling.BICUBIC)
    f=Image.new('RGBA',(512,512));f.paste(cell,pad);frames.append(f)
    bg=Image.new('RGBA',(512,512),'#272727');bg.alpha_composite(f);opaque.append(bg.convert('RGB'))
    rows.append({'key':k,'source_index':index,'raw_crop':[x,y,cw,ch],'edge_max_alpha':edge})
a.output.mkdir(parents=True);(a.output/'frames').mkdir()
for k,f in enumerate(frames):f.save(a.output/'frames'/f'{k:02}.png')
def save(name,delays):
    frames[0].save(a.output/(name+'.png'),save_all=True,append_images=frames[1:],duration=delays,loop=0,disposal=0,blend=0)
    frames[0].save(a.output/(name+'.webp'),save_all=True,append_images=frames[1:],duration=delays,loop=0,lossless=True,quality=100,method=6,exact=True)
    strip=Image.new('RGB',(len(frames)*512,512))
    for k,f in enumerate(opaque):strip.paste(f,(k*512,0))
    palette=strip.quantize(colors=256,method=Image.Quantize.MEDIANCUT);gif=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in opaque]
    cumulative=0;gif_delays=[]
    for d in delays:
        nxt=round((cumulative+d)/10)*10;gif_delays.append(nxt-round(cumulative/10)*10);cumulative+=d
    gif[0].save(a.output/(name+'.gif'),save_all=True,append_images=gif[1:],duration=gif_delays,loop=0,disposal=2,optimize=False)
    return gif_delays
delays=[round((k+1)*a.frame_ms)-round(k*a.frame_ms) for k in range(len(frames))];gif_ms=save('walk-ro-cadence',delays)
source_ms=[round((k+1)*a.source_cycle_ms/len(frames))-round(k*a.source_cycle_ms/len(frames)) for k in range(len(frames))];source_gif=save('walk-source-cadence',source_ms)
board=Image.new('RGB',(a.columns*512,a.rows*536),'#272727');d=ImageDraw.Draw(board)
for k,f in enumerate(opaque):board.paste(f,(k%a.columns*512,k//a.columns*536+24));d.text((k%a.columns*512+8,k//a.columns*536+5),f'{k+1} / source {keys[k]}',fill='white')
board.save(a.output/'frames-review.png')
(a.output/'manifest.json').write_text(json.dumps({'schema':'fixed-grid-motion-review-v1','raw_sha256':hashlib.sha256(a.sheet.read_bytes()).hexdigest(),'raw_size':[w,h],'grid':[a.columns,a.rows],'raw_cell':[cw,ch],'shared_scale':scale,'shared_padding':pad,'per_frame_bbox_fit':False,'master_canvas':[512,512],'frames':rows,'ro_reference_frame_delays_ms':delays,'gif_delays_ms':gif_ms,'source_clock_delays_ms':source_ms,'source_clock_gif_delays_ms':source_gif,'new_pixels_user_approved':False,'complete_replaceable_painted_parts':False,'release_ready':False},indent=2)+'\n')
print('GRID_PACK',len(frames),'frames;',sum(delays),'ms RO-reference cadence;',sum(source_ms),'ms source cadence')
