"""Build source-registered, same-frame basic attack cutouts and short late FX."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from assemble_mesh2motion_paint_review import cut_white
from build_four_direction_attack_review import DIRECTIONS, manual_parts, previews, package_sheets


def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')


def build(root):
    source=json.loads((root/'source-guides/manifest.json').read_text())
    manual=json.loads((root/'manual-annotations.json').read_text())['views']
    audits=[];views=[]
    for direction,clip in zip(DIRECTIONS,source['clips']):
        if clip['clip']!=direction:raise ValueError('Source direction mismatch')
        folder=root/direction;sheet=Image.open(folder/'painted-sheet.png').convert('RGB');w,h=sheet.size
        if w!=h:raise ValueError('Expected square 4x4 art sheet')
        records=[];annotations=[];frames=[]
        for i,rec in enumerate(clip['frames']):
            raw=manual[direction][i];observed=np.array(raw['pelvis'],float)
            target=np.array(rec['landmarks']['pelvis'])*.5
            origin=np.array([round(i%4*w/4),round(i//4*h/4)])
            end=[round((i%4+1)*w/4),round((i//4+1)*h/4)]
            cell,_=cut_white(sheet.crop((*origin,*end)))
            # Generated row packing can leave a neighboring boot fragment in
            # the cell. Retain the main figure and only nearby detached pixels
            # (e.g. a blade separated by an occluding glove), not another row.
            pixels=np.array(cell);labels,count=ndimage.label(pixels[:,:,3]>0)
            sizes=np.bincount(labels.ravel());sizes[0]=0;main=labels==int(np.argmax(sizes))
            near=ndimage.distance_transform_edt(~main)<24
            keep={int(v) for v in np.unique(labels[near]) if v!=0}
            pixels[~np.isin(labels,list(keep))]=0;cell=Image.fromarray(pixels)
            # The original cell pixels stay at native scale; one translation
            # registers the complete pose to its corresponding source pelvis.
            delta=np.rint(target-observed).astype(int)
            frame=Image.new('RGBA',(512,512));frame.alpha_composite(cell,tuple(origin+delta))
            if np.array(cell.getchannel('A')).sum()!=np.array(frame.getchannel('A')).sum():raise ValueError(f'Clipped {direction}/{i}')
            parts,annotation=manual_parts(frame,raw,delta)
            if 'head_polygon' in raw:
                poly=Image.new('L',(512,512));ImageDraw.Draw(poly).polygon([tuple(np.array(p)+delta) for p in raw['head_polygon']],fill=255)
                head=(np.array(poly)>0)&(np.array(frame.getchannel('A'))>0)&(np.array(parts['Weapon'].getchannel('A'))==0)
                pixels=np.zeros((512,512,4),np.uint8);pixels[head]=np.array(frame)[head];parts['HeadHair']=Image.fromarray(pixels)
            # Keep neighboring glove/armor flecks out of replaceable head and
            # blade layers. Reassign rejected pixels to the clothed body so
            # visible source art still reconstructs exactly.
            masks={}
            for name in ['HeadHair','Weapon']:
                mask=np.array(parts[name].getchannel('A'))>0
                labels,count=ndimage.label(mask);sizes=np.bincount(labels.ravel());sizes[0]=0
                if count:
                    main=labels==int(np.argmax(sizes));near=ndimage.distance_transform_edt(~main)<4
                    allowed={int(v) for v in np.unique(labels[near]) if v and sizes[v]>=(30 if name=='HeadHair' else 12)}
                    mask=np.isin(labels,list(allowed))
                masks[name]=mask
            visible=np.array(frame.getchannel('A'))>0
            masks['BodyCostume']=visible&~masks['HeadHair']&~masks['Weapon']
            for name,mask in masks.items():
                pixels=np.zeros((512,512,4),np.uint8);pixels[mask]=np.array(frame)[mask];parts[name]=Image.fromarray(pixels)
            merged=Image.new('RGBA',(512,512))
            for name in ['BodyCostume','HeadHair','Weapon']:merged.alpha_composite(parts[name])
            if not np.array_equal(np.array(merged),np.array(frame)):raise ValueError('Cutout reconstruction differs')
            parts['Master']=frame;frames.append(parts);annotations.append(annotation)
            error=float(np.linalg.norm(observed+delta-target))
            records.append({'frame':i,'source_frame':rec['source_frame'],'packing_translation':delta.tolist(),'pelvis_target':target.tolist(),'rounding_residual_px':error})
            audits.append({'direction':direction,'frame':i,'recomposition_mismatches':0,'rounding_residual_px':error})
        # The cut passes between source poses 11 and 13; first visible FX is
        # frame 7 / source13, never on the raised preparation poses.
        contact=7;grip=np.array(annotations[contact]['weapon_grip']);tip=np.array(annotations[contact]['weapon_tip']);length=float(np.linalg.norm(tip-grip))
        g0=np.array(clip['frames'][contact-1]['sword_grip']);t0=np.array(clip['frames'][contact-1]['sword_tip']);g1=np.array(clip['frames'][contact]['sword_grip']);t1=np.array(clip['frames'][contact]['sword_tip'])
        v=t1-g1;pv=tip-grip;angle=np.arctan2(pv[1],pv[0])-np.arctan2(v[1],v[0]);scale=length/max(1,np.linalg.norm(v));matrix=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])*scale
        oldg=matrix@(g0-g1)+grip;oldt=matrix@(t0-g1)+grip
        travel=float(np.linalg.norm(tip-oldt));fraction=min(1,.55*length/max(1,travel));oldg=grip+(oldg-grip)*fraction;oldt=tip+(oldt-tip)*fraction
        fx=Image.new('RGBA',(1024,1024));draw=ImageDraw.Draw(fx)
        for j in range(36):
            a=j/36;b=(j+1)/36;ga=oldg+(grip-oldg)*a;gb=oldg+(grip-oldg)*b;ta=oldt+(tip-oldt)*a;tb=oldt+(tip-oldt)*b
            for band in range(8):
                r0=.25+.75*band/8;r1=.25+.75*(band+1)/8
                poly=[ga+(ta-ga)*r0,ga+(ta-ga)*r1,gb+(tb-gb)*r1,gb+(tb-gb)*r0]
                color=tuple(int(c) for c in np.array([98,83,139])*(1-b)+np.array([243,239,255])*b)
                draw.polygon([tuple(p*2) for p in poly],fill=(*color,int(80+145*b)))
        fx=fx.resize((512,512),Image.Resampling.LANCZOS)
        # Explicit per-view artist staging, not a claim of mesh depth.
        behind=direction in ['NW','NE']
        for i,parts in enumerate(frames):
            blank=Image.new('RGBA',(512,512));effect=blank.copy()
            if i in [7,8]:
                effect=fx.copy()
                if i==8:effect.putalpha(effect.getchannel('A').point(lambda a:round(a*.25)))
            parts['WeaponLightBack']=effect if behind else blank.copy();parts['WeaponLightFront']=blank.copy() if behind else effect;parts['WeaponLight']=effect
            hand=Image.new('L',(512,512));x,y=annotations[i]['weapon_grip'];ImageDraw.Draw(hand).ellipse((x-17,y-17,x+17,y+17),fill=255);pixels=np.array(parts['BodyCostume']);pixels[np.array(hand)==0]=0;parts['WeaponHandOccluder']=Image.fromarray(pixels)
            for name,im in parts.items():
                dest=folder/name;dest.mkdir(exist_ok=True);im.save(dest/f'{i:03d}.png')
        write(folder/'assembly.json',{'direction':direction,'frames':records,'normalization':'manual pelvis to source at one fixed .5 projection scale; native art pixels, whole-frame translation only'})
        write(folder/'annotations.generated.json',{'frames':annotations,'trail':{'first_emission':7,'fade_frame':8,'maximum_recent_tip_travel_fraction':.55,'depth':'artist-selected per-view foreground/background, not 3D mesh occlusion'}})
        views.append({'direction':direction,'frames':records})
    timing=[max(20,round(x/1.4/10)*10) for x in source['clips'][0]['durations_ms']];timing[-1]=250
    write(root/'assembly-audit.json',{'action':'BasicAttack','timing_policy':'source holds compacted in guide; painted playback 1.4 times faster, 10ms GIF quantization, 250ms terminal preview hold','durations_ms':timing,'slow_durations_ms':[x*3 for x in timing],'directions':DIRECTIONS,'views':views})
    write(root/'cutout-audit.json',{'poses':64,'recomposition_mismatches':0,'maximum_annotation_rounding_residual_px':max(r['rounding_residual_px'] for r in audits),'frames':audits,'limitations':['Pelvis annotations are approximate visible waist centers.','Pixel reconstruction is not anatomical or motion acceptance.','Material-assisted cutouts still need edge inspection.']})
    previews(root)
    # Reuse the sheet exporter with explicit action-specific FX frames.
    package_sheets(root,effect_frames=(7,8))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);a=p.parse_args();build(a.folder)
