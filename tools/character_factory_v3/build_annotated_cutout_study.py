"""Extract visible same-frame parts using retained manual annotations.

Technical cutout/assembly only. No pose warping, hidden-surface generation or
automatic visual acceptance. This pilot deliberately stays outside import counts.
"""
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_propagation


def build(folder):
    annotations=json.loads((folder/'cutout-annotations.json').read_text())
    sheet=Image.open(folder/'master-sheet.png').convert('RGBA')
    scale=512/annotations['annotation_canvas_per_cell']; roles=['BodyCostume','HeadHair','Weapon','WeaponHandOccluder','WeaponLightFront']
    sheets={r:Image.new('RGBA',(2048,2048))for r in ['Master',*roles]}
    frames=[];report=[]
    def xy(p):return tuple(round(v*scale)for v in p)
    for i,a in enumerate(annotations['frames']):
        col=i%4;row=i//4
        cell=sheet.crop((round(col*sheet.width/4),round(row*sheet.height/4),round((col+1)*sheet.width/4),round((row+1)*sheet.height/4))).resize((512,512),Image.Resampling.LANCZOS)
        rgba=np.array(cell);rgb=rgba[:,:,:3]
        # Only border-connected near-white is removed: ivory costume and
        # enclosed highlights remain. No per-frame scaling or fitting follows.
        white=rgb.min(axis=2)>242;seed=np.zeros_like(white);seed[0,:]=white[0,:];seed[-1,:]=white[-1,:];seed[:,0]=white[:,0];seed[:,-1]=white[:,-1]
        bg=binary_propagation(seed,mask=white);rgba[bg]=0
        master=Image.fromarray(rgba);visible=rgba[:,:,3]>0
        labels=Image.new('L',(512,512),1);draw=ImageDraw.Draw(labels)
        tip=np.array(xy(a['sword_tip']),float);grip=np.array(xy(a['sword_grip']),float)
        blade_end=xy(a.get('visible_blade_end',a['sword_grip']))
        draw.line([tuple(tip),blade_end],fill=3,width=round(10*scale))
        draw.ellipse(xy(a['head_ellipse']),fill=2)
        hand=Image.new('L',(512,512));hd=ImageDraw.Draw(hand);radius=a['hand_radius']*scale
        if a.get('hand_visible',True):hd.ellipse((grip[0]-radius,grip[1]-radius,grip[0]+radius,grip[1]+radius),fill=255)
        ids=np.array(labels);hm=np.array(hand)>0
        # Annotated head region excludes yellow scarf/bronze costume pixels.
        color=rgb.astype(float);r,g,b=color[:,:,0],color[:,:,1],color[:,:,2]
        gold=(r>80)&(r>g*1.15)&(g>r*.5)&(b<r*.38)
        ids[(ids==2)&gold]=1
        ids[hm]=1;ids[~visible]=0
        parts={}
        for role,value in [('BodyCostume',1),('HeadHair',2),('Weapon',3)]:
            arr=rgba.copy();arr[ids!=value]=0;parts[role]=Image.fromarray(arr)
        arr=rgba.copy();arr[~hm]=0;parts['WeaponHandOccluder']=Image.fromarray(arr)
        fx=Image.new('RGBA',(512,512))
        if a['trail_active'] and i:
            prev=annotations['frames'][i-1];old=np.array(xy(prev['sword_tip']),float)
            travel=old-tip;distance=float(np.linalg.norm(travel));blade=float(np.linalg.norm(tip-grip))
            # Recent spatial travel only; no trail on wind-up or stationary hold.
            if distance>2 and blade>2:
                prev_grip=np.array(xy(prev['sword_grip']),float)
                previous_axis=old-prev_grip;current_axis=tip-grip
                old_angle=math.atan2(previous_axis[1],previous_axis[0]);angle=math.atan2(current_axis[1],current_axis[0])
                sweep=(angle-old_angle+math.pi)%(2*math.pi)-math.pi
                recent=math.copysign(min(abs(sweep),.55),sweep)
                # Curved blade-plane ribbon: history trails the current edge.
                # Its arc is capped at .55 current projected blade lengths.
                high=Image.new('RGBA',(2048,2048));fd=ImageDraw.Draw(high)
                for angular in range(32):
                    t0=angular/32;t1=(angular+1)/32
                    a0=angle-recent*(1-t0);a1=angle-recent*(1-t1)
                    tail=math.sin(t0*math.pi/2)**.7
                    for band in range(16):
                        r0=blade*(.55+.45*band/16);r1=blade*(.55+.45*(band+1)/16)
                        points=[grip+np.array([math.cos(a0),math.sin(a0)])*r0,grip+np.array([math.cos(a1),math.sin(a1)])*r0,grip+np.array([math.cos(a1),math.sin(a1)])*r1,grip+np.array([math.cos(a0),math.sin(a0)])*r1]
                        bright=band/16;c=(round(155+90*bright),round(151+91*bright),round(209+46*bright),round((95+95*bright)*tail*a['trail_fade']))
                        fd.polygon([tuple(p*4)for p in points],fill=c)
                fx=high.resize((512,512),Image.Resampling.LANCZOS)
        parts['WeaponLightFront']=fx
        reconstructed=Image.new('RGBA',(512,512))
        for role in ['BodyCostume','HeadHair','Weapon']:reconstructed.alpha_composite(parts[role])
        mismatch=int(np.any(np.array(reconstructed)!=rgba,axis=2).sum())
        if mismatch:raise ValueError(f'Cutouts do not recompose at frame {i}: {mismatch}')
        composited=master.copy();composited.alpha_composite(fx);composited.alpha_composite(parts['Weapon']);composited.alpha_composite(parts['WeaponHandOccluder'])
        # Preview on dark backdrop exposes white matte and mask problems.
        bgim=Image.new('RGBA',(512,512),(44,48,60,255));bgim.alpha_composite(composited);frames.append(bgim.convert('RGB'))
        for role,im in {'Master':master,**parts}.items():
            target=folder/'cutout-study'/role/f'{i:03d}.png';target.parent.mkdir(parents=True,exist_ok=True);im.save(target)
            sheets[role].paste(im,(col*512,row*512))
        edge=visible[0,:].any()or visible[-1,:].any()or visible[:,0].any()or visible[:,-1].any()
        report.append({'frame':i,'recomposition_mismatch_pixels':mismatch,'visible_pixels':int(visible.sum()),'touches_cell_edge':bool(edge),'trail_active':bool(fx.getbbox()),'mask_boundary_review_required':True})
    out=folder/'cutout-study';out.mkdir(exist_ok=True)
    for role,im in sheets.items():im.save(out/f'{role}.png')
    durations=[80]*4+[55]*3+[65]*3+[90]*6
    frames[0].save(out/'normal.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0)
    frames[0].save(out/'slow.gif',save_all=True,append_images=frames[1:],duration=[d*3 for d in durations],loop=0)
    receipt={'status':'CUTOUT_AND_FX_STUDY_REQUIRES_VISUAL_REVIEW','source_sha256':hashlib.sha256((folder/'master-sheet.png').read_bytes()).hexdigest(),'frames':report,'all_base_parts_recompose':True,'hidden_surfaces_authored':False,'source_landmark_registration_approved':False,'owner_approved':False,'runtime_admitted':False,'limitations':['Head/weapon masks are manual seeds; inspect every edge before swapping.','Glove overlay is a provisional local mask, not an independently redrawn hand.','Trail ribbon uses only recent annotated tip travel; source blade-plane/depth fidelity still requires visual review.','Looped GIF restarts one-shot action; it is not a locomotion loop.']}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);args=p.parse_args();r=build(args.folder);print(json.dumps({'frames':len(r['frames']),'status':r['status'],'edge_frames':[f['frame']for f in r['frames']if f['touches_cell_edge']]}))
