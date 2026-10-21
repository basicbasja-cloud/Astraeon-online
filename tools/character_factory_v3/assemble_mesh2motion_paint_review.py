#!/usr/bin/env python3
"""Cut white-background sprite cells without moving, warping or bbox-scaling art."""
import argparse,json,hashlib,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage


def cut_white(image):
    rgb=np.asarray(image.convert('RGB')).copy()
    white=np.min(rgb,axis=2)>=245
    seed=np.zeros(white.shape,dtype=bool);seed[0,:]=white[0,:];seed[-1,:]=white[-1,:];seed[:,0]=white[:,0];seed[:,-1]=white[:,-1]
    background=ndimage.binary_propagation(seed,mask=white,structure=np.ones((3,3),dtype=bool))
    alpha=(~background).astype(np.uint8)*255
    labels,n=ndimage.label(alpha>0,structure=np.ones((3,3),dtype=bool));sizes=np.bincount(labels.ravel());small=sizes<32;small[0]=False;debris=small[labels];alpha[debris]=0
    result=np.dstack((rgb,alpha));result[alpha==0,:3]=0
    return Image.fromarray(result,'RGBA'),{'background_pixels':int(background.sum()),'tiny_disconnected_matte_pixels':int(debris.sum()),'retained_visible_rgb_pixels_repainted':0}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('folder',type=Path);args=ap.parse_args();root=args.folder
    plan=json.loads((root/'batch-plan.json').read_text());guide=root.parent/'overhead-B-compact-guide';m=json.loads((guide/'manifest.json').read_text())
    frames_dir=root/'cutout-frames';frames_dir.mkdir(exist_ok=True);poses=[];reports=[]
    for batch in plan['batches']:
        source=root/f"batch-{batch['batch']:02d}-paint-white.png"
        if not source.exists():continue
        sheet=Image.open(source).convert('RGB');w,h=sheet.size
        if w%2 or h%2:raise ValueError(f'Non-integral 2x2 cells: {source}')
        for cell_index,source_frame in enumerate(batch['frames']):
            x,y=cell_index%2*w//2,cell_index//2*h//2
            raw=sheet.crop((x,y,x+w//2,y+h//2));cut,cleanup=cut_white(raw)
            # Normalize only the requested canvas size, never a figure's bounds.
            frame=cut.convert('RGBa').resize((1024,1024),Image.Resampling.LANCZOS).convert('RGBA')
            index=(batch['batch']-1)*4+cell_index;path=frames_dir/f'paint_{index:02d}.png';frame.save(path)
            mask=np.asarray(frame.getchannel('A'))>8;ys,xs=np.nonzero(mask)
            reports.append({'frame':index,'source_motion_frame':source_frame,'source_sheet':source.name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cell':cell_index,'source_cell_size':[w//2,h//2],'normalization':'whole cell to 1024; no bbox fit, no recenter, no deformation','visible_bbox':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'touches_canvas_edge':bool(mask[0,:].any() or mask[-1,:].any() or mask[:,0].any() or mask[:,-1].any()),**cleanup})
            poses.append((index,source_frame,frame))
    if not poses:raise ValueError('No painted batches')
    poses.sort();comparisons=[];beauties=[];markers=[]
    for index,f,frame in poses:
        body=frame.convert('RGBa').resize((512,512),Image.Resampling.LANCZOS).convert('RGBA');bg=Image.new('RGBA',(512,512),'#ececec');bg.alpha_composite(body);beauties.append(bg.convert('RGB'))
        src=Image.open(guide/'frames'/f'{f:03d}.png').convert('RGBA').resize((512,512),Image.Resampling.LANCZOS);sg=Image.new('RGBA',(512,512),'#ececec');sg.alpha_composite(src)
        pair=Image.new('RGB',(1024,544),'#ececec');d=ImageDraw.Draw(pair);pair.paste(sg.convert('RGB'),(0,32));pair.paste(bg.convert('RGB'),(512,32));d.text((8,8),f'Source B {f}',fill='black');d.text((520,8),f'Paint {index} / registration review',fill='black');comparisons.append(pair)
        marked=bg.convert('RGB');draw=ImageDraw.Draw(marked)
        for name in ['pelvis','hand_r','ball_l','ball_r']:
            px,py=m['frames'][f]['landmarks'][name];px/=2;py/=2;draw.line([(px-5,py),(px+5,py)],fill='#ff0066',width=2);draw.line([(px,py-5),(px,py+5)],fill='#ff0066',width=2)
        markers.append(marked)
    timings=[round((poses[i+1][1]-poses[i][1])*1000/60) if i+1<len(poses) else 300 for i in range(len(poses))]
    beauties[0].save(root/'painted-one-shot-review.gif',save_all=True,append_images=beauties[1:],duration=timings,disposal=2,optimize=False)
    comparisons[0].save(root/'guide-vs-painted-one-shot-review.gif',save_all=True,append_images=comparisons[1:],duration=timings,disposal=2,optimize=False)
    sheet=Image.new('RGB',(320*4,320*math.ceil(len(poses)/4)),'#ececec');draw=ImageDraw.Draw(sheet)
    for i,im in enumerate(beauties):
        x,y=i%4*320,i//4*320;sheet.paste(im.resize((320,320)),(x,y));draw.text((x+5,y+5),f'{poses[i][0]} / src {poses[i][1]}',fill='black')
    sheet.save(root/'painted-contact.png')
    diagnostic=Image.new('RGB',(320*4,320*math.ceil(len(poses)/4)),'#ececec')
    for i,im in enumerate(markers):diagnostic.paste(im.resize((320,320)),(i%4*320,i//4*320))
    diagnostic.save(root/'guide-anchor-overlay-contact.png')
    report={'status':'UNAPPROVED_REGISTRATION_AND_CONTINUITY_REVIEW','painted_frame_count':len(poses),'planned_frame_count':plan['output_frame_count'],'semantic_layers':'not yet cut; full-character cutouts only','method':'edge-connected pure-white matte removal and sub-32px disconnected debris removal; retained visible RGB is unchanged; same whole-cell normalization, no per-frame figure registration','frames':reports,'timings_ms':timings,'limitations':['Numerical guide anchors are only diagnostic crosses; the artwork is not moved to meet them.','Review the full animation for body, cloak and costume drift before creating semantic layers or WeaponLight.']}
    (root/'cutout-review-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'frames':len(poses),'touching_edge':[r['frame'] for r in reports if r['touches_canvas_edge']]}))

if __name__=='__main__':main()
