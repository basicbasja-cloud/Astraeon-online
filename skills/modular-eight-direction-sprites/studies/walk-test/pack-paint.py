"""Normalize a returned 4x2 redraw sheet; preserve drift instead of hiding it."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

p=argparse.ArgumentParser()
p.add_argument('--sheet',type=Path,required=True)
p.add_argument('--motion-package',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--row-pitch',type=int,default=512,help='One measured grid-row pitch; not a per-pose fit')
a=p.parse_args()
if a.output.exists():raise ValueError('Use a fresh redraw package directory')
im=Image.open(a.sheet).convert('RGBA')
if im.size!=(1536,1024):raise ValueError('Returned grid requires new explicit registration')
if not 480<=a.row_pitch<=512:raise ValueError('Invalid bounded two-row grid calibration')
m=json.loads((a.motion_package/'package.json').read_text())
a.output.mkdir(parents=True);(a.output/'frames').mkdir()
frames=[];cards=[];diagnostics=[]
for k in range(8):
    x,y=k%4*384,k//4*a.row_pitch
    cell=im.crop((x,y,x+384,y+512))
    alpha=np.asarray(cell)[:,:,3];ys,xs=np.nonzero(alpha>64)
    if not len(xs):raise ValueError('Empty redraw exposure')
    bounds=[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1]
    if alpha[0].max()>64 or alpha[-1].max()>64 or alpha[:,0].max()>64 or alpha[:,-1].max()>64:
        raise ValueError('Meaningful character alpha touches a cell boundary')
    # One declared 512-square canvas for every key; no bbox alignment or per-pose scaling.
    square=Image.new('RGBA',(512,512));square.paste(cell,(64,0))
    f=square.resize((128,128),Image.Resampling.LANCZOS)
    f.save(a.output/'frames'/f'{k:02}.png');frames.append(f)
    bg=Image.new('RGBA',(128,128),'#dce0df');bg.alpha_composite(f);cards.append(bg.convert('RGB'))
    diagnostics.append({'key':k,'source_cell':[x,y,384,512],'alpha_over_64_bounds_in_cell':bounds,
                        'highest_visible_pixel_native_y':bounds[1]/4})
palette_board=Image.new('RGB',(128*8,128))
for k,f in enumerate(cards):palette_board.paste(f,(128*k,0))
palette=palette_board.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
gif=[f.quantize(palette=palette,dither=Image.Dither.NONE).resize((512,512),Image.Resampling.NEAREST) for f in cards]
gif[0].save(a.output/'walk-painted-SE.gif',save_all=True,append_images=gif[1:],
            duration=m['gif_delays_ms'],loop=0,disposal=2,optimize=False)
frames[0].save(a.output/'walk-painted-SE.png',save_all=True,append_images=frames[1:],
               duration=m['apng_delays_ms'],loop=0,disposal=0,blend=0)
strip=Image.new('RGBA',(128*8,128))
for k,f in enumerate(frames):strip.paste(f,(128*k,0))
strip.save(a.output/'walk-painted-SE-strip.png')
board=Image.new('RGB',(128*8,148*2),'#e7e9e8');d=ImageDraw.Draw(board)
for k,f in enumerate(cards):
    source=Image.open(a.motion_package/'frames'/'SE'/f'{k:02}.png').convert('RGBA')
    bg=Image.new('RGBA',(128,128),'#dce0df');bg.alpha_composite(source)
    board.paste(bg.convert('RGB'),(k*128,20));board.paste(f,(k*128,168))
    d.text((k*128+4,3),f'Rig #{k}',fill='#263238');d.text((k*128+4,151),f'Redraw #{k}',fill='#263238')
board.save(a.output/'rig-vs-painted.png')
tops=[f['highest_visible_pixel_native_y'] for f in diagnostics]
report={'schema':'walk-redraw-preview-v1','raw_sheet_sha256':hashlib.sha256(a.sheet.read_bytes()).hexdigest(),
        'logical_canvas':[128,128],'cell_size':[384,512],'cell_padding':[64,0],
        'global_scale':.25,'grid_row_pitch':a.row_pitch,'per_pose_recenter':False,'per_pose_scale':False,
        'grid_calibration':'Second-row common hair-top translation: raw local y89 vs first row y102. One 499px row pitch for all four lower-row cells; no per-frame bbox correction.',
        'gif_delays_ms':m['gif_delays_ms'],'apng_delays_ms':m['apng_delays_ms'],
        'frames':diagnostics,'highest_visible_pixel_native_range':max(tops)-min(tops),
        'pose_lock_verified':False,'complete_replaceable_parts':False,'release_ready':False,
        'observations':['Image generation changed source silhouette, proportions and registration.',
                        ('Raw 512px row pitch retains a 13px row displacement.' if a.row_pitch==512 else 'One shared measured grid-row correction removes the 13px common row displacement; it does not recover exact rig poses.'),
                        'Hair, cape edges, tabard and glove contours drift; surface motion is not verified by the rig check.',
                        'The redraw is a flat original-style preview. Complete modular geometry lives in the separate rig package.',
                        'No per-frame bbox fitting, painting, anatomy repair or artificial pose smoothing was applied.']}
(a.output/'redraw-check.json').write_text(json.dumps(report,indent=2)+'\n')
print('REDRAW_PACKED',len(frames),'top silhouette range',report['highest_visible_pixel_native_range'])
