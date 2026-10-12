"""Rebuild v14 comparison artifacts. Diagnostic display only, no art repair."""
import base64
import hashlib
import importlib.util
import io
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT/'research/sprite-animation/continuity-v14'


def uri(path):
    return 'data:image/png;base64,' + base64.b64encode(Path(path).read_bytes()).decode()


def read_frames(path, pattern):
    return sorted(path.glob(pattern))


def on_gray(path):
    f = Image.open(path).convert('RGBA')
    bg = Image.new('RGBA', f.size, '#272727')
    bg.alpha_composite(f)
    return bg.convert('RGB')


def main():
    before = read_frames(ROOT/'research/sprite-animation/ro-walk-eight-v13/master/frames', '*.png')
    after = read_frames(OUT/'attempts/geometry-first/frames', '*.png')
    rig = [ROOT/f'research/sprite-animation/ro-walk-eight-v13/source-depth/W/{i:02}/proximal-guide.png' for i in range(8)]
    ro = read_frames(ROOT/'research/sprite-animation/motion-reference-v6/ro/walk-W', '[0-9][0-9][0-9][0-9].png')
    king = read_frames(ROOT/'research/sprite-animation/motion-reference-v6/other-games/king-lucas-walk-2', '[0-9][0-9][0-9][0-9].png')
    ro_map = [2,3,4,5,6,7,0,1]
    king_map = [4,6,8,10,12,14,0,2]
    mapping = {'schema':'phase-comparison-layout-v1', 'original_source_indices':list(range(0,40,5)),
        'ro_native_indices':ro_map, 'king_native_indices':king_map,
        'mapping_method':'Visual stride-window alignment, approximate. External exposures are not source-bone-equivalent poses or verified contact events.',
        'king_native_frame_count':16, 'king_native_durations_ms':[30]*16,
        'ro_native_frame_count':8, 'ro_native_durations_ms':[75]*8,
        'display_only':{'before_and_after_and_rig_scale':.5,'ro_scale':2.5,
                        'king_fixed_crop':[40,20,170,195],'king_scale':1.5},
        'no_per_frame_fit':True,'art_pixels_repaired':False,'external_pixels_used_as_imagegen_input':False}
    (OUT/'evidence/phase-mapping.json').write_text(json.dumps(mapping,indent=2)+'\n')
    rows = [('V13 / user: legs accepted, motion rejected',before),
            ('V14 / new candidate, no approval transfer',after),
            ('Original bone/near-far guide',rig),
            ('RO / approximate stride-window alignment',[ro[i] for i in ro_map]),
            ('King Lucas / approximate phase, native sequence has 16 frames',[king[i] for i in king_map])]
    board = Image.new('RGB',(2048,len(rows)*304),'#272727');d=ImageDraw.Draw(board)
    for row,(label,files) in enumerate(rows):
        d.text((8,row*304+4),label,fill='white')
        for i,p in enumerate(files):
            im=on_gray(p)
            if row<3:im=im.resize((256,256),Image.Resampling.NEAREST)
            elif row==3:im=im.resize((115,233),Image.Resampling.NEAREST)
            else:im=im.crop((40,20,170,195)).resize((195,262),Image.Resampling.NEAREST)
            board.paste(im,(i*256+(256-im.width)//2,row*304+40))
            native=i if row<3 else ro_map[i] if row==3 else king_map[i]
            d.text((i*256+8,row*304+23),f'Slot {i+1} / native {native}',fill='white')
    board.save(OUT/'frame-by-frame.png')
    # Before/after GIF has exactly the same exposure durations and frame count.
    gif_frames=[]
    for i in range(8):
        im=Image.new('RGB',(1024,540),'#272727');dr=ImageDraw.Draw(im)
        im.paste(on_gray(before[i]),(0,28));im.paste(on_gray(after[i]),(512,28))
        dr.text((8,8),f'BEFORE V13 / {i+1}',fill='white');dr.text((520,8),f'AFTER V14 candidate / {i+1}',fill='white')
        gif_frames.append(im)
    strip=Image.new('RGB',(1024*8,540))
    for i,f in enumerate(gif_frames):strip.paste(f,(i*1024,0))
    palette=strip.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
    quantized=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in gif_frames]
    quantized[0].save(OUT/'before-after.gif',save_all=True,append_images=quantized[1:],duration=[80,70,70,80,80,70,70,80],loop=0,disposal=2,optimize=False)
    # Retain native-reference speed/order: phase pairing never rewrites source GIFs.
    for name,files,delay in [('ro-native',ro,75),('king-native',king,30)]:
        fs=[on_gray(p) for p in files]
        fs[0].save(OUT/(name+'.gif'),save_all=True,append_images=fs[1:],duration=delay if name=='king-native' else [80,70,70,80,80,70,70,80],loop=0,disposal=2)
    # Visible landmark chart: one declared body-height reference per entire clip.
    fig,ax=plt.subplots(2,1,figsize=(12,7),constrained_layout=True)
    for name,color in [('v13','#ff6868'),('v14','#61ccb0'),('ro','#e3b966')]:
        r=json.loads((OUT/f'check/{name}-continuity.json').read_text())
        o=json.loads((OUT/f'evidence/{name}-observations.json').read_text())
        p=np.array(r['landmarks']['eye']['positions_px']);height=o['reference_body_height_px']
        y=(p[:,1]-p[:,1].mean())/height*100
        ax[0].plot(range(9),np.r_[y,y[0]],'o-',label=name.upper(),color=color)
        step=np.array(r['landmarks']['eye']['step_px'])/height*100
        ax[1].plot(range(1,9),step,'o-',label=name.upper(),color=color)
    ax[0].set(xlabel='Native frame (9 repeats frame1)',ylabel='Eye Y / reference height (%)',title='Visible-eye observations, not recovered bones. RO starts at a different gait phase.')
    ax[1].set(xlabel='Transition (8 = last -> first)',ylabel='Eye jump / reference height (%)')
    for a in ax:a.grid(alpha=.25);a.legend()
    fig.savefig(OUT/'continuity-measurements.png',dpi=140);plt.close(fig)
    # Review the measurements themselves. A manually placed point can be wrong.
    for name in ['v13','v14']:
        observations=json.loads((OUT/f'evidence/{name}-observations.json').read_text())
        report=json.loads((OUT/f'check/{name}-continuity.json').read_text())
        board=Image.new('RGB',(1536,840),'#272727');draw=ImageDraw.Draw(board)
        for i,f in enumerate(observations['frames']):
            im=on_gray(f['image']);d=ImageDraw.Draw(im)
            for landmark in ['eye','belt']:
                value=f['landmarks'].get(landmark)
                if value is None:continue
                x,y=value['xy'];d.line((x-8,y,x+8,y),fill='cyan',width=2);d.line((x,y-8,x,y+8),fill='cyan',width=2)
            region=report['palette_patch_probe']['frames'][i]
            if region['status']=='DECLARED_PALETTE_REGION_MEASURED':
                d.rectangle(region['bounds_xyxy'],outline='#e3b966',width=2)
                x,y=region['centroid_px'];d.ellipse((x-4,y-4,x+4,y+4),fill='#e3b966')
            board.paste(im.resize((384,384)),(i%4*384,i//4*420+24))
            draw.text((i%4*384+4,i//4*420+4),f'{name} slot{i+1}: pupil cyan / palette region gold',fill='white')
        board.save(OUT/f'evidence/{name}-visible-observations-review.png')
    # Save the actual original head-bone path separately: eye surface != Head joint.
    module_path=ROOT/'skills/modular-eight-direction-sprites/scripts/leg-continuity.py'
    loader=importlib.util.spec_from_file_location('leg_ref',module_path);mod=importlib.util.module_from_spec(loader);loader.loader.exec_module(mod)
    motion_path=ROOT/'research/sprite-animation/walk-test-v9/motion.json';motion=json.loads(motion_path.read_text())
    trajectory={'schema':'source-head-trajectory-v1','motion_sha256':hashlib.sha256(motion_path.read_bytes()).hexdigest(),
        'facing':'W','canvas':[512,512],'sample_count':41,'eye_equivalence_claimed':False,
        'scope':'Actual source Head-joint projection. Eye surface observations are independent; no anatomy pass or art fit.',
        'samples':[{'source_index':f['source_index'],'time_seconds':f['time_seconds'],'xy':mod.project(f['in_place_joints']['Head'],512,'W')} for f in motion['frames']]}
    (OUT/'evidence/source-head-trajectory.json').write_text(json.dumps(trajectory,indent=2)+'\n')
    data={'before':[uri(p) for p in before],'after':[uri(p) for p in after],
          'rig':[uri(p) for p in rig],'ro':[uri(p) for p in ro],'king':[uri(p) for p in king],
          'roMap':ro_map,'kingMap':king_map,
          'spacingWarnings':json.loads((OUT/'check/v14-continuity.json').read_text()).get('span_profile_warning_frames',[])}
    template=Path(__file__).with_name('continuity-viewer.html').read_text()
    (OUT/'frame-review.html').write_text(template.replace('__FRAME_DATA__',json.dumps(data)))
    print('V14 study rebuilt: eight-slot board, equal-speed GIF, native refs, chart and offline viewer')


if __name__=='__main__':main()
