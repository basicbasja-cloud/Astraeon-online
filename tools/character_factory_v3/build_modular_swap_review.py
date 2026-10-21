"""Same-frame visible cutouts, cosmetic combinations and painted-blade trail review."""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from assemble_mesh2motion_paint_review import cut_white


PARTS = ['BodyCostume', 'HeadHair', 'Weapon']


def png(image):
    stream = io.BytesIO(); image.save(stream, format='PNG'); return stream.getvalue()


def capsule(draw, a, b, width):
    draw.line([tuple(a), tuple(b)], fill=1, width=width)
    for x, y in [a, b]:
        r = width / 2; draw.ellipse((x-r, y-r, x+r, y+r), fill=1)


def masks(annotation, reference):
    size = reference.size
    head = Image.new('1', size); hd = ImageDraw.Draw(head)
    hd.polygon([tuple(p) for p in annotation['head_polygon']], fill=1)
    weapon = Image.new('1', size); wd = ImageDraw.Draw(weapon)
    tip, guard, pommel = [np.array(annotation[key], float) for key in ['weapon_tip', 'weapon_guard', 'weapon_pommel']]
    axis = guard-tip; axis /= np.linalg.norm(axis); perpendicular = np.array([-axis[1], axis[0]])
    # Full visible blade, crossguard and pommel; the gripping glove stays in BodyCostume.
    quad = [tip-perpendicular*5-axis*4, tip+perpendicular*5-axis*4,
            guard+perpendicular*17, guard-perpendicular*17]
    wd.polygon([tuple(p) for p in quad], fill=1)
    capsule(wd, guard-perpendicular*21, guard+perpendicular*21, 9)
    if annotation['frame'] != 4:
        capsule(wd, pommel-axis*3, pommel+axis*3, 15)
    hsv=np.asarray(reference.convert('RGB').convert('HSV'))/255.0
    hue,saturation,value=hsv[:,:,0],hsv[:,:,1],hsv[:,:,2]
    head_final=np.asarray(head,bool)
    gold=(hue>.075)&(hue<.17)&(saturation>.32)
    metal=(saturation<.32)|(value<.24)|gold
    weapon_final=np.asarray(weapon,bool)&metal
    weapon_final=ndimage.binary_dilation(weapon_final,iterations=1)&np.asarray(weapon,bool)
    return head_final, weapon_final


def source_components(master):
    labels, _ = ndimage.label(np.asarray(master.getchannel('A')) > 0)
    counts = np.bincount(labels.ravel()); entries = []
    for label in np.flatnonzero(counts > 1000):
        if label == 0: continue
        yy, xx = np.nonzero(labels == label)
        entries.append((int(label), [int(xx.min()), int(yy.min()), int(xx.max())+1, int(yy.max())+1]))
    if len(entries) != 16: raise ValueError(f'Expected 16 connected figures, found {len(entries)}')
    ordered = []
    for lo, hi in zip([0,350,700,965], [350,700,965,master.height]):
        row = sorted([entry for entry in entries if lo <= entry[1][1] < hi], key=lambda e:e[1][0])
        if len(row) != 4: raise ValueError('Unexpected figure packing')
        ordered.extend(row)
    return labels, ordered


def export_ora(path, layers):
    size = layers[0][1].size
    tree = ET.Element('image', {'w': str(size[0]), 'h': str(size[1]), 'name': 'Same-frame modular visible cutouts'})
    stack = ET.SubElement(tree, 'stack'); merged = Image.new('RGBA', size)
    for _, layer in reversed(layers): merged.alpha_composite(layer)
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
        for i,(name,layer) in enumerate(layers):
            src=f'data/layer{i}.png'
            ET.SubElement(stack,'layer',{'name':name,'src':src,'opacity':'1.0','visibility':'visible','composite-op':'svg:src-over','x':'0','y':'0'})
            archive.writestr(src,png(layer),compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr('stack.xml',ET.tostring(tree),compress_type=zipfile.ZIP_DEFLATED)
        archive.writestr('mergedimage.png',png(merged),compress_type=zipfile.ZIP_DEFLATED)


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('folder',type=Path); args=parser.parse_args(); root=args.folder
    previous=root.parent/'no-cloak-continuous-review'
    annotations=json.loads((root/'manual-cutout-annotations.json').read_text())['frames']
    assembly=json.loads((previous/'assembly-audit.json').read_text())
    reference,_=cut_white(Image.open(previous/'clean-white-sheet.png'))
    semantic_masks=[masks(annotation,reference) for annotation in annotations]
    skins={}; reports=[]; sheets={}
    for name,path in [('gold',previous/'clean-white-sheet.png'),('moon',root/'moon-knight-sheet.png')]:
        master,matte=cut_white(Image.open(path)); rgba=np.asarray(master)
        if master.size!=(1254,1254): raise ValueError('Source canvas differs; do not fit automatically')
        labels,components=source_components(master); frames=[]
        for i,((label,bbox),annotation,registered) in enumerate(zip(components,annotations,assembly['frames'])):
            head,weapon=semantic_masks[i]; visible=(labels==label)
            selections={'Weapon':visible & weapon,'HeadHair':visible & head & ~weapon,'BodyCostume':visible & ~head & ~weapon}
            tx,ty=registered['packing_translation']; parts={}; recomposed=Image.new('RGBA',(512,512))
            for part in PARTS:
                pixels=np.zeros_like(rgba); pixels[selections[part]]=rgba[selections[part]]
                raw=Image.fromarray(pixels).crop(tuple(bbox)); frame=Image.new('RGBA',(512,512)); frame.alpha_composite(raw,(bbox[0]+tx,bbox[1]+ty))
                destination=root/name/part; destination.mkdir(parents=True,exist_ok=True); frame.save(destination/f'{i:03d}.png'); parts[part]=frame; recomposed.alpha_composite(frame)
            raw=np.zeros_like(rgba);raw[visible]=rgba[visible];expected=Image.new('RGBA',(512,512));expected.alpha_composite(Image.fromarray(raw).crop(tuple(bbox)),(bbox[0]+tx,bbox[1]+ty))
            mismatch=int(np.any(np.asarray(recomposed)!=np.asarray(expected),axis=2).sum())
            if mismatch:raise ValueError(f'Recomposition mismatch {name} {i}')
            if name=='gold':
                accepted=np.asarray(Image.open(previous/'frames'/f'{i:03d}.png').convert('RGBA'))
                if not np.array_equal(accepted,np.asarray(recomposed)):raise ValueError('Accepted frame changed')
            frames.append(parts);reports.append({'skin':name,'frame':i,'recomposition_mismatched_pixels':mismatch,'part_visible_pixels':{part:int((np.asarray(im)[:,:,3]>0).sum()) for part,im in parts.items()}})
        skins[name]=frames
        for part in PARTS:
            sheet=Image.new('RGBA',(2048,2048))
            for i,parts in enumerate(frames):sheet.alpha_composite(parts[part],(i%4*512,i//4*512))
            sheet.save(root/name/(part+'-sheet.png'));sheets[name,part]=sheet
    # The effect uses annotated accepted painted blades, not the mannequin path.
    grips=[];tips=[]
    for annotation,frame in zip(annotations,assembly['frames']):
        offset=np.array(frame['packing_translation']); grips.append(np.array(annotation['weapon_grip'])+offset); tips.append(np.array(annotation['weapon_tip'])+offset)
    effects=[];fx_folder=root/'WeaponLight';fx_folder.mkdir(exist_ok=True)
    angles=np.unwrap(np.array([math.atan2(*(tip-grip)[::-1]) for tip,grip in zip(tips,grips)]))
    # Preserve the owner's forward sweep: the shortest projected turn at
    # contact reversed the ribbon behind the torso. Continue clockwise through
    # the contact pose instead; every sampled blade endpoint remains unchanged.
    for i in range(2,5):
        while angles[i] < angles[i-1]: angles[i] += 2*math.pi
    lengths=np.array([np.linalg.norm(tip-grip) for tip,grip in zip(tips,grips)])
    def interpolate(points,t):
        j=min(len(points)-2,max(0,int(t)));f=t-j;return points[j]*(1-f)+points[j+1]*f
    def blade(t):
        j=min(14,max(0,int(t)));f=t-j;grip=interpolate(grips,t)
        angle=angles[j]*(1-f)+angles[j+1]*f;length=lengths[j]*(1-f)+lengths[j+1]*f
        return grip,grip+np.array([math.cos(angle),math.sin(angle)])*length
    def tip_path_length(begin,end):
        points=[blade(t)[1] for t in np.linspace(begin,end,80)]
        return sum(float(np.linalg.norm(b-a)) for a,b in zip(points,points[1:]))
    # Emit only after the downstroke reaches the low follow-through (source
    # frame 16), not during the preceding raised guard. Bound the afterimage
    # by recent painted tip travel rather than keeping a long circular ribbon.
    emission_frame=4;cap=float(lengths[emission_frame]*.65)
    lo,hi=emission_frame-.9,float(emission_frame)
    for _ in range(20):
        mid=(lo+hi)/2
        if tip_path_length(mid,emission_frame)>cap:lo=mid
        else:hi=mid
    ribbon_begin=hi
    for i in range(16):
        layer=Image.new('RGBA',(1024,1024));draw=ImageDraw.Draw(layer)
        if 4<=i<=5:
            newest=emission_frame;begin=ribbon_begin;times=np.linspace(begin,newest,60);fade=1 if i==4 else .25
            for a,b in zip(times,times[1:]):
                age=(b-begin)/max(.001,newest-begin); g0,t0=blade(a);g1,t1=blade(b)
                for band in range(12):
                    r0=.15+.85*band/12;r1=.15+.85*(band+1)/12
                    color=np.array([95,81,126])*(1-age)+np.array([242,237,255])*age
                    alpha=int((105+125*age)*fade*(.65+.35*math.sin(math.pi*(band+.5)/12)))
                    quad=[g0+(t0-g0)*r0,g0+(t0-g0)*r1,g1+(t1-g1)*r1,g1+(t1-g1)*r0]
                    draw.polygon([tuple(p*2) for p in quad],fill=(*[int(c) for c in color],alpha))
            if i==4:
                edge=[tuple(blade(t)[1]*2) for t in np.linspace(begin,newest,70)]
                draw.line(edge,fill=(255,250,235,235),width=4)
        layer=layer.resize((512,512),Image.Resampling.LANCZOS);layer.save(fx_folder/f'{i:03d}.png');effects.append(layer)
    fx_sheet=Image.new('RGBA',(2048,2048))
    for i,layer in enumerate(effects):fx_sheet.alpha_composite(layer,(i%4*512,i//4*512))
    fx_sheet.save(root/'WeaponLight-sheet.png')
    for name in skins:
        occluder_sheet=Image.new('RGBA',(2048,2048));destination=root/name/'WeaponHandOccluder';destination.mkdir(exist_ok=True)
        for i,parts in enumerate(skins[name]):
            mask=Image.new('L',(512,512));draw=ImageDraw.Draw(mask);gx,gy=grips[i];draw.ellipse((gx-18,gy-18,gx+18,gy+18),fill=255)
            pixels=np.array(parts['BodyCostume']);pixels[np.asarray(mask)==0]=0
            occluder=Image.fromarray(pixels);occluder.save(destination/f'{i:03d}.png');parts['WeaponHandOccluder']=occluder
            occluder_sheet.alpha_composite(occluder,(i%4*512,i//4*512))
        occluder_sheet.save(root/name/'WeaponHandOccluder-sheet.png');sheets[name,'WeaponHandOccluder']=occluder_sheet
    for name in skins:
        export_ora(root/name/'layered-sprite-sheet.ora',[(part,sheets[name,part]) for part in ['Weapon','HeadHair','WeaponHandOccluder']]+[('WeaponLight',fx_sheet),('BodyCostume',sheets[name,'BodyCostume'])])
    configurations=[('original',{'BodyCostume':'gold','HeadHair':'gold','Weapon':'gold'}),('head-only',{'BodyCostume':'gold','HeadHair':'moon','Weapon':'gold'}),('outfit-only',{'BodyCostume':'moon','HeadHair':'gold','Weapon':'gold'}),('weapon-only',{'BodyCostume':'gold','HeadHair':'gold','Weapon':'moon'}),('all-swapped',{'BodyCostume':'moon','HeadHair':'moon','Weapon':'moon'})]
    previews={};timings=assembly['durations_ms'];slow=assembly['slow_durations_ms']
    for title,configuration in configurations:
        frames=[]
        for i in range(16):
            bg=Image.new('RGBA',(512,512),'#ececec');bg.alpha_composite(skins[configuration['BodyCostume']][i]['BodyCostume'])
            bg.alpha_composite(effects[i]);bg.alpha_composite(skins[configuration['HeadHair']][i]['HeadHair'])
            bg.alpha_composite(skins[configuration['BodyCostume']][i]['WeaponHandOccluder']);bg.alpha_composite(skins[configuration['Weapon']][i]['Weapon'])
            frames.append(bg.convert('RGB'))
        previews[title]=frames
        frames[0].save(root/(title+'.gif'),save_all=True,append_images=frames[1:],duration=timings,disposal=2,optimize=False)
    compare=[]
    for i in range(16):
        row=Image.new('RGB',(384*5,416),'#ececec');draw=ImageDraw.Draw(row)
        for j,(title,_) in enumerate(configurations):
            row.paste(previews[title][i].resize((384,384),Image.Resampling.LANCZOS),(j*384,32));draw.text((j*384+8,10),title,fill='black')
        compare.append(row)
    compare[0].save(root/'five-way-swaps-slow.gif',save_all=True,append_images=compare[1:],duration=slow,disposal=2,optimize=False)
    front=[]
    for i in range(16):
        row=Image.new('RGB',(1024,544),'#ececec');draw=ImageDraw.Draw(row)
        for j,name in enumerate(['original','all-swapped']):
            row.paste(previews[name][i],(j*512,32));draw.text((j*512+8,8),name+' / forward trail',fill='black')
        front.append(row)
    front[0].save(root/'forward-trail-slow.gif',save_all=True,append_images=front[1:],duration=slow,disposal=2,optimize=False)
    contact=Image.new('RGB',(512*3,544),'#ececec');draw=ImageDraw.Draw(contact)
    for j,i in enumerate([3,4,5]):
        contact.paste(previews['original'][i],(j*512,32));draw.text((j*512+8,8),f'Forward sweep / {i}',fill='black')
    contact.save(root/'forward-trail-contact.png')
    preview=Image.new('RGB',(512*4,560),'#ececec');draw=ImageDraw.Draw(preview)
    for j,part in enumerate(['BodyCostume','HeadHair','Weapon','WeaponLight']):
        layer=effects[4] if part=='WeaponLight' else skins['gold'][4][part]
        preview.paste(layer,(j*512,40),layer);draw.text((j*512+8,10),part,fill='black')
    preview.save(root/'cutout-layer-review.png')
    report={'status':'OWNER_REVIEW_MODULAR_COSMETIC_PROTOTYPE','frame_count':16,'direction':'SE','parts':PARTS+['WeaponLight'],'source_master_pixels_changed':0,'original_matches_accepted_frames':True,'variant_source_sha256':hashlib.sha256((root/'moon-knight-sheet.png').read_bytes()).hexdigest(),'normalization':'all parts and both skins share exactly the accepted per-frame packing translations; no per-part or alternate-pose fitting','trail':{'path':'manual accepted painted sword grip/tip, independent transparent layer','spawn':2,'last_emission':4,'last_fade':6,'palette':'original plum/lavender/silver/ivory','occlusion':'behind body, head and weapon','grips':[p.tolist() for p in grips],'tips':[p.tolist() for p in tips]},'configurations':dict(configurations),'frames':reports,'limitations':['Manual semantic edges and wrist/guard occlusion require visual inspection.','BodyCostume is the complete clothed body replacement, not independently naked BaseBody and clothing.','HeadHair combines visible head and hair; separate hair-only and helmet interfaces are not supplied.','Only the reviewed sixteen SE poses are provided; no other directions are synthesized.','Trail follows manually annotated painted points; weapon edges and alternative blade alignment require review.']}
    effect_frames=[]
    for i,effect in enumerate(effects):
        alpha=np.asarray(effect.getchannel('A'))>8
        edge=bool(alpha[0].any() or alpha[-1].any() or alpha[:,0].any() or alpha[:,-1].any())
        if edge:raise ValueError(f'Trail touches canvas boundary at {i}')
        effect_frames.append({'frame':i,'visible_pixels':int(alpha.sum()),'edge_touch':edge})
    report['trail']['interpolation']='interpolated grip with angular/length blade rotation; owner-corrected consistent clockwise forward arc through frames 2-4; sampled endpoints unchanged; 0.9-frame ribbon history'
    report['trail']['occlusion']='in front of BodyCostume, behind HeadHair, gripping-hand occluder and Weapon'
    report['trail']['angle_radians_at_sampled_poses']=angles.tolist()
    report['trail']['owner_correction']='Forward sweep requested; previous shortest-turn, behind-body ribbon rejected.'
    report['trail'].update({'spawn':4,'last_emission':4,'last_fade':5,'interpolation':'forward angular blade sweep, bounded recent painted tip travel; no effect during raised guard','history_start_sample':ribbon_begin,'tip_path_length_px':tip_path_length(ribbon_begin,emission_frame),'tip_path_length_limit_px':cap,'length_limit_fraction_of_painted_blade':.65,'fade_alpha_after_emission':.25,'timing_owner_correction':'Emit after the downstroke has passed, not during wind-up; shorten the afterimage and remove the long lingering ribbon.'})
    report['support_layers']=['WeaponHandOccluder: visible BodyCostume glove pixels redrawn above WeaponLight; not an independent cosmetic slot']
    report['trail']['frames']=effect_frames
    (root/'modular-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'frames':16,'skins':len(skins),'recomposition_mismatched_pixels':0,'configurations':len(configurations)}))


if __name__=='__main__':main()
