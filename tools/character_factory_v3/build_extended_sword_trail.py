"""Build a longer bounded source-path FX variant without changing character art."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from register_preserved_swordsman import transform

ROOT = Path(__file__).resolve().parents[2]
P = ROOT/'authoring/characters/factory-v3/patch-0.0.1'
SOURCE = ROOT/'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple'
CANONICAL = P/'review/preserved-swordsman-canonical-cutouts-20261023'
ORDER = ['WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','Weapon','WeaponHandOccluder']


def bounded_path(points, maximum):
    """Keep only real recent path segments; interpolate the oldest boundary."""
    if not np.isfinite(maximum) or maximum <= 0:
        raise ValueError('Invalid history bound')
    result = [points[-1]]
    remaining = maximum
    for old, new in reversed(list(zip(points, points[1:]))):
        distance = float(np.linalg.norm(new[1]-old[1]))
        if distance > remaining:
            weight = remaining/distance
            result.append(tuple(n+(o-n)*weight for o,n in zip(old,new)))
            break
        result.append(old)
        remaining -= distance
        if remaining <= 1e-9:
            break
    return list(reversed(result))


def path_length(points):
    return sum(float(np.linalg.norm(b[1]-a[1])) for a,b in zip(points,points[1:]))


def paint(points):
    canvas = Image.new('RGBA',(1024,1024))
    draw = ImageDraw.Draw(canvas)
    total = path_length(points)
    elapsed = 0.
    for old,new in zip(points,points[1:]):
        distance = float(np.linalg.norm(new[1]-old[1]))
        for j in range(36):
            a,b = j/36,(j+1)/36
            ga,ta = [o+(n-o)*a for o,n in zip(old,new)]
            gb,tb = [o+(n-o)*b for o,n in zip(old,new)]
            age = (elapsed+distance*b)/max(total,1e-9)
            color = tuple(int(c) for c in np.array([98,83,139])*(1-age)+np.array([243,239,255])*age)
            start_age = (elapsed+distance*a)/max(total,1e-9)
            # A pointed old tip grows into the blade-width contact end.
            # This preserves the actual sweep envelope without a rectangular tail.
            width_a,width_b = .75*np.sqrt(start_age),.75*np.sqrt(age)
            for band in range(8):
                ra0,ra1 = 1-width_a+width_a*band/8,1-width_a+width_a*(band+1)/8
                rb0,rb1 = 1-width_b+width_b*band/8,1-width_b+width_b*(band+1)/8
                polygon = [ga+(ta-ga)*ra0,ga+(ta-ga)*ra1,gb+(tb-gb)*rb1,gb+(tb-gb)*rb0]
                draw.polygon([tuple(p*2) for p in polygon],fill=(*color,round(225*np.sqrt(age))))
        elapsed += distance
    return canvas.resize((512,512),Image.Resampling.LANCZOS)


def build(output, fraction=.8):
    if output.exists() or not .55 < fraction <= 1:
        raise ValueError('Choose a new output and history fraction above .55, at most 1')
    output.mkdir(parents=True)
    guide = json.loads((SOURCE/'source-guides/manifest.json').read_text())
    registration = json.loads((CANONICAL/'receipt.json').read_text())
    durations = json.loads((SOURCE/'assembly-audit.json').read_text())['durations_ms']
    records=[]; before={}; after={}; pins={}
    for clip in guide['clips']:
        direction=clip['clip']; folder=SOURCE/direction
        annotations=json.loads((folder/'annotations.generated.json').read_text())['frames']
        grip,tip=[np.array(annotations[7][key],float) for key in ['weapon_grip','weapon_tip']]
        native=clip['frames'][7]; g,t=[np.array(native[key],float) for key in ['sword_grip','sword_tip']]
        v,pv=t-g,tip-grip; blade=float(np.linalg.norm(pv))
        angle=np.arctan2(pv[1],pv[0])-np.arctan2(v[1],v[0])
        matrix=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])*blade/np.linalg.norm(v)
        raw=[tuple(matrix@(np.array(r[key])-g)+grip for key in ['sword_grip','sword_tip']) for r in clip['frames'][5:8]]
        if [r['source_frame'] for r in clip['frames'][5:8]] != [11,12,13]:
            raise ValueError('Unexpected source strike sampling')
        history=bounded_path(raw,fraction*blade)
        old=bounded_path(raw[-2:],.55*blade)
        if path_length(history)<=path_length(old):
            raise ValueError('Variant did not increase real source-path history')
        mapping=next(r for r in registration['frames'] if r['action']=='BasicAttack' and r['direction']==direction)['frames'][7]
        effect=transform(paint(history),mapping['camera_scale'],mapping['canvas_translation'])
        before[direction]=[];after[direction]=[]
        for i in range(16):
            new=effect.copy() if i in [7,8] else Image.new('RGBA',(768,768))
            if i==8:new.putalpha(new.getchannel('A').point(lambda a:round(a*.25)))
            fxrole='WeaponLightBack' if direction in ['NW','NE'] else 'WeaponLightFront'
            oldframe=Image.new('RGBA',(768,768));newframe=oldframe.copy()
            for role in ORDER:
                path=CANONICAL/'BasicAttack'/direction/role/f'{i:03d}.png'
                pins[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
                original=Image.open(path).convert('RGBA');oldframe.alpha_composite(original)
                replacement=(new if role==fxrole else Image.new('RGBA',(768,768))) if role.startswith('WeaponLight') else original
                newframe.alpha_composite(replacement)
                if role.startswith('WeaponLight'):
                    dest=output/direction/role;dest.mkdir(parents=True,exist_ok=True);replacement.save(dest/f'{i:03d}.png')
            before[direction].append(oldframe);after[direction].append(newframe)
        records.append({'direction':direction,'source_frames':[11,12,13],'blade_length_author512':blade,'old_tip_history_author512':path_length(old),'new_tip_history_author512':path_length(history),'actual_length_ratio':path_length(history)/path_length(old),'history_extrapolated':False})
    # Identical viewport across before/after, every view and every frame.
    boxes=[im.getbbox() for frames in list(before.values())+list(after.values()) for im in frames]
    box=(min(b[0] for b in boxes)-12,min(b[1] for b in boxes)-12,max(b[2] for b in boxes)+12,max(b[3] for b in boxes)+12)
    w,h=box[2]-box[0],box[3]-box[1]
    boards=[]; singles=[]
    for i in range(16):
        board=Image.new('RGB',(w*4,h*2+48),'#e5e5e5');draw=ImageDraw.Draw(board)
        for row,collection in enumerate([before,after]):
            for col,d in enumerate(before):
                draw.text((col*w+8,row*(h+24)+5),('Before' if row==0 else 'Longer')+' '+d,fill='black')
                crop=collection[d][i].crop(box);board.paste(crop,(col*w,row*(h+24)+24),crop)
        boards.append(board)
        single=Image.new('RGB',(w*2,h+24),'#e5e5e5');draw=ImageDraw.Draw(single)
        for col,collection in enumerate([before,after]):
            draw.text((col*w+8,5),'Before' if col==0 else 'Longer',fill='black');crop=collection['SE'][i].crop(box);single.paste(crop,(col*w,24),crop)
        singles.append(single)
    for name,frames in [('four-direction-comparison',boards),('SE-comparison',singles)]:
        frames[0].save(output/(name+'.png'),save_all=True,append_images=frames[1:],duration=durations,loop=0)
        frames[0].save(output/(name+'.gif'),save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=2)
        frames[7].save(output/(name+'-strike.png'))
    for direction in before:
        for role in ['WeaponLightBack','WeaponLightFront']:
            sheet=Image.new('RGBA',(768*4,768*4))
            for i in range(16):sheet.alpha_composite(Image.open(output/direction/role/f'{i:03d}.png'),((i%4)*768,(i//4)*768))
            sheet.save(output/direction/(role+'-sheet.png'))
    for path,digest in pins.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=digest:raise ValueError('Baseline artwork changed')
    receipt={'status':'EXTENDED_SOURCE_PATH_FX_VARIANT_FOR_REVIEW','maximum_history_blade_fraction':fraction,'emission_indices':[7,8],'first_source_emission_frame':13,'fade_opacity':.25,'timings_ms':durations,'shared_viewport':box,'body_head_weapon_grip_and_motion_changed':False,'baseline_inputs':pins,'views':records,'runtime_admitted':False}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return {k:v for k,v in receipt.items() if k!='baseline_inputs'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--fraction',type=float,default=.8);args=parser.parse_args();print(json.dumps(build(args.output,args.fraction)))
