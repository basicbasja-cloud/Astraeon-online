"""Package real-camera four-direction illustration studies without mirroring."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.spatial import ConvexHull
from assemble_mesh2motion_paint_review import cut_white
from build_modular_swap_review import export_ora
from audit_sprite_candidate import _iou, RESEARCH_IOU_WARNING

DIRECTIONS=['SW','NW','NE','SE']
PARTS=['BodyCostume','HeadHair','Weapon','WeaponHandOccluder','WeaponLightBack','WeaponLightFront','WeaponLight']


def write_json(path,data):path.write_text(json.dumps(data,indent=2)+'\n')


def components(image):
    labels,_=ndimage.label(np.asarray(image.getchannel('A'))>0)
    sizes=np.bincount(labels.ravel());entries=[]
    for label in np.flatnonzero(sizes>1000):
        if label==0:continue
        yy,xx=np.nonzero(labels==label);entries.append({'label':int(label),'bbox':[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1]})
    if len(entries)!=16:raise ValueError(f'Expected 16 complete figures, found {len(entries)}')
    rows=[]
    for low,high in zip([0,350,680,945],[350,680,945,image.height]):
        row=sorted([e for e in entries if low<=e['bbox'][1]<high],key=lambda e:e['bbox'][0])
        if len(row)!=4:raise ValueError('Unexpected sheet row packing')
        rows.append(row)
    return labels,rows


def pack(root):
    plan=json.loads((root/'plan.json').read_text());ids=plan['source_frames']
    previous=root.parent/'no-cloak-continuous-review';timing=json.loads((previous/'assembly-audit.json').read_text())
    report=[]
    for direction in DIRECTIONS:
        folder=root/direction;folder.mkdir(exist_ok=True);output=folder/'Master';output.mkdir(exist_ok=True)
        records=[]
        if direction=='SE':
            for i,entry in enumerate(timing['frames']):
                shutil.copy2(previous/'frames'/f'{i:03d}.png',output/f'{i:03d}.png');records.append(dict(entry))
            source=previous/'clean-white-sheet.png';baselines=[336,665,953,1229]
        else:
            source=folder/'painted-sheet.png';image,matte=cut_white(Image.open(source))
            if image.size!=(1254,1254):raise ValueError('Do not silently rescale a new generation canvas')
            rgba=np.asarray(image);labels,rows=components(image);baselines=[max(e['bbox'][3] for e in row) for row in rows]
            for row,entries in enumerate(rows):
                for column,entry in enumerate(entries):
                    i=row*4+column;bbox=entry['bbox'];pixels=np.zeros_like(rgba);pixels[labels==entry['label']]=rgba[labels==entry['label']]
                    tx=round(-column*image.width/4+(512-image.width/4)/2);ty=432-baselines[row]
                    frame=Image.new('RGBA',(512,512));frame.alpha_composite(Image.fromarray(pixels).crop(tuple(bbox)),(bbox[0]+tx,bbox[1]+ty));frame.save(output/f'{i:03d}.png')
                    a=np.asarray(frame.getchannel('A'))>8
                    if a[0].any() or a[-1].any() or a[:,0].any() or a[:,-1].any():raise ValueError(f'Clipped figure: {direction} {i}')
                    records.append({'frame':i,'source_frame':ids[i],'source_bbox':bbox,'packing_translation':[tx,ty],'visible_pixels':int(a.sum())})
        manifest={'direction':direction,'frames':records,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'row_baselines':baselines,'canvas':[512,512],'normalization':'native shared pixel scale, common X slot offsets and four explicitly recorded row packing translations; no individual figure fitting, no body warp','mirroring':False,'status':'ART_REVIEW_NOT_SOURCE_REGISTERED_PRODUCTION'}
        write_json(folder/'assembly.json',manifest);report.append(manifest)
        print('PACKED',direction,flush=True)
    write_json(root/'assembly-audit.json',{'directions':DIRECTIONS,'frame_count_per_direction':16,'painted_pose_count':64,'mirroring':False,'shared_source_canvas':[1254,1254],'output_canvas':[512,512],'durations_ms':timing['durations_ms'],'slow_durations_ms':timing['slow_durations_ms'],'views':report,'limitations':['Generated illustrations follow the actual fixed-camera diagonal guides but exact joint/root agreement is not proven.','Four common row translations correct generated sheet packing; they are not a physical root track.','Only the gold skin is expanded to four attack directions; existing SE alternate cosmetics remain separate.']})


def manual_parts(frame,raw,offset):
    pixels=np.asarray(frame);rgb=pixels[:,:,:3].astype(float);hsv=np.asarray(frame.convert('RGB').convert('HSV'))/255;visible=pixels[:,:,3]>0
    r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2];yy,xx=np.mgrid[:512,:512]
    center=np.array(raw['head_center'])+offset;tip=np.array(raw['weapon_tip'],float)+offset;guard=np.array(raw['weapon_guard'],float)+offset
    axis=(tip-guard)/max(1,np.linalg.norm(tip-guard));normal=np.array([-axis[1],axis[0]]);mid=tip+(guard-tip)*.6
    polygon=Image.new('1',(512,512));draw=ImageDraw.Draw(polygon)
    draw.polygon([tuple(p) for p in [tip-normal,tip+normal,mid+normal*6.5,guard+normal*4.5,guard-normal*4.5,mid-normal*6.5]],fill=1)
    steel=np.asarray(polygon,bool)&(hsv[:,:,1]<.36)&(hsv[:,:,2]>.23)&(b>=r-22)&visible
    weapon=ndimage.binary_dilation(steel,iterations=1)&visible
    region=Image.new('1',(512,512));ImageDraw.Draw(region).line([tuple(guard-normal*15),tuple(guard+normal*15)],fill=1,width=7)
    gold=(hsv[:,:,0]>.07)&(hsv[:,:,0]<.18)&(hsv[:,:,1]>.25)&(hsv[:,:,2]>.27)
    weapon|=ndimage.binary_dilation(np.asarray(region,bool)&gold,iterations=1)&visible
    radius=(xx-center[0])**2+(yy-center[1])**2<33**2
    gray=(b>=r-21)&(r>=g-5)&((rgb.max(2)-rgb.min(2))<65)&(rgb.max(2)>105)&visible&radius&~weapon
    gray=ndimage.binary_closing(gray,iterations=1);labels,count=ndimage.label(gray);sizes=np.bincount(labels.ravel());candidates=[]
    for label in np.flatnonzero(sizes>12):
        if label==0:continue
        ys,xs=np.nonzero(labels==label);distance=float(np.linalg.norm(np.array([xs.mean(),ys.mean()])-center));candidates.append((distance-math.sqrt(len(xs))*.45,int(label)))
    if not candidates:raise ValueError('Manual head seed has no silver hair pixels')
    chosen=min(candidates)[1];selected=labels==chosen
    near=ndimage.distance_transform_edt(~selected)<10
    skin=(hsv[:,:,0]<.075)&(hsv[:,:,1]>.16)&(hsv[:,:,2]>.38)&near&visible&radius&~weapon
    points=np.column_stack(np.nonzero(selected|skin))[:,::-1];hull=points[ConvexHull(points).vertices]
    head=Image.new('1',(512,512));ImageDraw.Draw(head).polygon([tuple(p) for p in hull],fill=1)
    head_mask=ndimage.binary_dilation(np.asarray(head,bool),iterations=2)&visible&~weapon
    # Warm scarf/armor pixels must stay with the costume, even when the head
    # convex hull crosses the collar. Preserve separate visible head islands
    # where the blade/arm occludes the face; remove only tiny mask debris.
    cloth=(hsv[:,:,0]>.08)&(hsv[:,:,0]<.18)&(hsv[:,:,1]>.25)&visible
    cloth=ndimage.binary_closing(cloth,iterations=1)
    head_mask&=~cloth
    pieces,_=ndimage.label(head_mask);counts=np.bincount(pieces.ravel());keep=counts>=8;keep[0]=False
    head_mask=keep[pieces]
    selections={'BodyCostume':visible&~head_mask&~weapon,'HeadHair':head_mask,'Weapon':weapon};parts={}
    for name,mask in selections.items():
        out=np.zeros_like(pixels);out[mask]=pixels[mask];parts[name]=Image.fromarray(out)
    return parts,{'head_seed':center.tolist(),'head_polygon':hull.tolist(),'weapon_grip':(guard-axis*12).tolist(),'weapon_tip':tip.tolist(),'weapon_guard':guard.tolist(),'weapon_detection':'manual visible blade endpoints with material and outline masks','method':'manual head seed and blade endpoints, color-assisted same-frame visible cutout; source pixels unchanged'}


def guide_effect(root,direction,annotation,guide):
    records=guide['frames'];index=16;pg=np.array(annotation['weapon_grip']);pt=np.array(annotation['weapon_tip']);pv=pt-pg;length=np.linalg.norm(pv)
    gs=np.array([r['sword_grip'] for r in records]);ts=np.array([r['sword_tip'] for r in records]);vectors=ts-gs
    angles=np.unwrap(np.arctan2(vectors[:,1],vectors[:,0]));lengths=np.linalg.norm(vectors,axis=1)
    v=ts[index]-gs[index];rotation=math.atan2(pv[1],pv[0])-math.atan2(v[1],v[0]);scale=length/max(1,np.linalg.norm(v));matrix=np.array([[math.cos(rotation),-math.sin(rotation)],[math.sin(rotation),math.cos(rotation)]])*scale
    def lerp(points,t):
        j=min(58,max(0,int(t)));f=t-j;return np.array(points[j])*(1-f)+np.array(points[j+1])*f
    def pose(t):
        angle=float(lerp(angles,t));extent=float(lerp(lengths,t));grip=lerp(gs,t);tip=grip+np.array([math.cos(angle),math.sin(angle)])*extent
        return matrix@(grip-gs[index])+pg,matrix@(tip-gs[index])+pg
    def path_length(start):
        points=[pose(t)[1] for t in np.linspace(start,index,60)]
        return sum(float(np.linalg.norm(b-a)) for a,b in zip(points,points[1:]))
    low,high=15.,16.;cap=.65*length
    if path_length(low)>cap:
        for _ in range(18):
            mid=(low+high)/2
            if path_length(mid)>cap:low=mid
            else:high=mid
        start=high
    else:start=low
    world=json.loads((root/'source-world-landmarks.json').read_text())['frames'][index]['bones'];center=np.array(world['spine_02']);camera=np.array(guide['camera']['location']);toward=camera-center;toward/=np.linalg.norm(toward)
    world_grips=[r['world_sword_grip'] for r in records];world_tips=[r['world_sword_tip'] for r in records]
    back=Image.new('RGBA',(1024,1024));front=Image.new('RGBA',(1024,1024));bd,fd=ImageDraw.Draw(back),ImageDraw.Draw(front)
    samples=np.linspace(start,index,60)
    for a,b in zip(samples,samples[1:]):
        phase=(b-start)/max(.0001,index-start);g0,t0=pose(a);g1,t1=pose(b)
        wg0,wt0=lerp(world_grips,a),lerp(world_tips,a);wg1,wt1=lerp(world_grips,b),lerp(world_tips,b)
        color=np.array([95,81,126])*(1-phase)+np.array([242,237,255])*phase
        for band in range(12):
            r0=.15+.85*band/12;r1=.15+.85*(band+1)/12;radial=(r0+r1)/2
            depth=(((wg0+(wt0-wg0)*radial)+(wg1+(wt1-wg1)*radial))/2-center)@toward
            draw=fd if depth>=0 else bd;alpha=int((105+125*phase)*(.65+.35*math.sin(math.pi*(band+.5)/12)))
            quad=[g0+(t0-g0)*r0,g0+(t0-g0)*r1,g1+(t1-g1)*r1,g1+(t1-g1)*r0]
            draw.polygon([tuple(p*2) for p in quad],fill=(*[int(c) for c in color],alpha))
    return back.resize((512,512),Image.Resampling.LANCZOS),front.resize((512,512),Image.Resampling.LANCZOS),{'source_interval':[start,16],'tip_path_length_px':path_length(start),'length_limit_px':cap,'mapping':'effect-only similarity transform from source contact blade to painted contact blade','depth':'source world ribbon relative to spine_02 and the real camera; approximate torso-plane occlusion, not per-pixel mesh depth'}


def build_parts(root):
    plan=json.loads((root/'plan.json').read_text());ids=plan['source_frames'];audits=[];overrides_path=root/'annotation-overrides.json';overrides=json.loads(overrides_path.read_text()) if overrides_path.exists() else {}
    previous=root.parent/'modular-swaps-review'
    manual=json.loads((root/'manual-raw-annotations.json').read_text())['views'] if (root/'manual-raw-annotations.json').exists() else {}
    for direction in DIRECTIONS:
        folder=root/direction;guide=json.loads((root.parent/'eight-direction-guides'/direction/'manifest.json').read_text());annotations=[];frames=[]
        packing=json.loads((folder/'assembly.json').read_text())['frames']
        for i,source_frame in enumerate(ids):
            master=Image.open(folder/'Master'/f'{i:03d}.png').convert('RGBA')
            if direction not in manual:raise ValueError('Manual pose annotations are required for every direction')
            parts,annotation=manual_parts(master,manual[direction][i],np.array(packing[i]['packing_translation']))
            override=overrides.get(direction,{}).get(str(i),{})
            if override:
                if 'head_polygon' in override:
                    visible=np.asarray(master.getchannel('A'))>0;mask=Image.new('1',(512,512));ImageDraw.Draw(mask).polygon([tuple(p) for p in override['head_polygon']],fill=1);head=np.asarray(mask,bool)&visible&(np.asarray(parts['Weapon'].getchannel('A'))==0);body=visible&~head&(np.asarray(parts['Weapon'].getchannel('A'))==0)
                    for name,selection in [('HeadHair',head),('BodyCostume',body)]:
                        pixels=np.zeros((512,512,4),np.uint8);pixels[selection]=np.asarray(master)[selection];parts[name]=Image.fromarray(pixels)
                annotation.update(override)
            annotations.append(annotation);frames.append(parts)
            reconstructed=Image.new('RGBA',(512,512))
            for name in ['BodyCostume','HeadHair','Weapon']:reconstructed.alpha_composite(parts[name])
            mismatch=int(np.any(np.asarray(reconstructed)!=np.asarray(master),axis=2).sum())
            if mismatch:raise ValueError(f'Cutout mismatch {direction} {i}: {mismatch}')
            audits.append({'direction':direction,'frame':i,'recomposition_mismatched_pixels':mismatch,'weapon_detection':annotation.get('weapon_detection','accepted SE manual mask')})
        if direction=='SE':
            back=Image.new('RGBA',(512,512));front=Image.open(previous/'WeaponLight/004.png').convert('RGBA');fx_audit={'method':'accepted short after-cut SE effect reused'}
        else:back,front,fx_audit=guide_effect(root,direction,annotations[4],guide)
        for i,parts in enumerate(frames):
            blank=Image.new('RGBA',(512,512));bg,fg=blank.copy(),blank.copy()
            if i in [4,5]:
                bg,fg=back.copy(),front.copy()
                if i==5:
                    for effect in [bg,fg]:effect.putalpha(effect.getchannel('A').point(lambda a:round(a*.25)))
            combined=Image.new('RGBA',(512,512));combined.alpha_composite(bg);combined.alpha_composite(fg)
            hand_mask=Image.new('L',(512,512));draw=ImageDraw.Draw(hand_mask);x,y=annotations[i]['weapon_grip'];draw.ellipse((x-18,y-18,x+18,y+18),fill=255);pixels=np.array(parts['BodyCostume']);pixels[np.asarray(hand_mask)==0]=0
            parts.update({'WeaponLightBack':bg,'WeaponLightFront':fg,'WeaponLight':combined,'WeaponHandOccluder':Image.fromarray(pixels)})
            for name,image in parts.items():
                destination=folder/name;destination.mkdir(exist_ok=True);image.save(destination/f'{i:03d}.png')
        write_json(folder/'annotations.generated.json',{'direction':direction,'status':'SEMANTIC_EDGES_AND_WEAPON_ALIGNMENT_REQUIRE_REVIEW','frames':annotations,'trail':fx_audit})
        print('CUTOUTS',direction,flush=True)
    write_json(root/'cutout-audit.json',{'directions':DIRECTIONS,'pose_count':64,'recomposition_mismatched_pixels':0,'frames':audits,'limitations':['Manual pose annotations and color-assisted cutouts are provisional; inspect collar, hair and hilt boundaries.','BodyCostume is the whole clothed body; no hidden anatomy is supplied.','Trail depth uses an approximate source torso plane; it is not per-pixel 3D occlusion.']})


def compose(root,direction,index,trail=True):
    folder=root/direction
    if not (folder/'BodyCostume').exists():
        frame=Image.open(folder/'Master'/f'{index:03d}.png').convert('RGBA')
        bg=Image.new('RGBA',(512,512),'#ececec');bg.alpha_composite(frame);return bg.convert('RGB')
    bg=Image.new('RGBA',(512,512),'#ececec')
    order=['WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','WeaponHandOccluder','Weapon']
    for part in order:
        if not trail and part.startswith('WeaponLight'):continue
        bg.alpha_composite(Image.open(folder/part/f'{index:03d}.png').convert('RGBA'))
    return bg.convert('RGB')


def previews(root):
    audit=json.loads((root/'assembly-audit.json').read_text());durations=audit['durations_ms'];slow=audit['slow_durations_ms'];views={}
    for direction in DIRECTIONS:
        images=[compose(root,direction,i) for i in range(16)];views[direction]=images
        for name,timing in [('attack.gif',durations),('attack-slow.gif',slow)]:images[0].save(root/direction/name,save_all=True,append_images=images[1:],duration=timing,disposal=2,optimize=False)
    combined=[]
    for i in range(16):
        canvas=Image.new('RGB',(1536,408),'#ececec');draw=ImageDraw.Draw(canvas)
        for j,direction in enumerate(DIRECTIONS):
            x,y=j%4*384,j//4*408;canvas.paste(views[direction][i].resize((384,384),Image.Resampling.LANCZOS),(x,y+24));draw.text((x+8,y+6),direction,fill='black')
        combined.append(canvas)
    for name,timing in [('four-directions-attack.gif',durations),('four-directions-attack-slow.gif',slow)]:combined[0].save(root/name,save_all=True,append_images=combined[1:],duration=timing,disposal=2,optimize=False)
    turns=[]
    for direction in DIRECTIONS:
        canvas=Image.new('RGB',(512,544),'#ececec');canvas.paste(views[direction][-1],(0,32));ImageDraw.Draw(canvas).text((12,10),direction+' / turntable review',fill='black');turns.append(canvas)
    turns[0].save(root/'four-direction-turntable.gif',save_all=True,append_images=turns[1:],duration=550,loop=0,disposal=2,optimize=False)
    contact=7 if audit.get('action')=='BasicAttack' else 4
    combined[0].save(root/'four-directions-guard.png');combined[contact].save(root/'four-directions-strike.png');combined[-1].save(root/'four-directions-recovery.png')


def package_sheets(root,effect_frames=(4,5)):
    sheets=root/'sheets';sheets.mkdir(exist_ok=True);checks=[];assets={}
    for part in ['Master']+PARTS:
        sheet=Image.new('RGBA',(2048,8192))
        for column,direction in enumerate(DIRECTIONS):
            for i in range(16):sheet.alpha_composite(Image.open(root/direction/part/f'{i:03d}.png').convert('RGBA'),(column*512,i*512))
        path=sheets/(part+'.png');sheet.save(path);assets[part]={'file':'sheets/'+path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        for column,direction in enumerate(DIRECTIONS):
            for i in range(16):
                actual=np.asarray(sheet.crop((column*512,i*512,column*512+512,i*512+512)));expected=np.asarray(Image.open(root/direction/part/f'{i:03d}.png').convert('RGBA'));visible=(actual[:,:,3]>0)|(expected[:,:,3]>0)
                if not np.array_equal(actual[:,:,3],expected[:,:,3]) or not np.array_equal(actual[visible],expected[visible]):raise ValueError('Sheet cell differs from source frame')
        checks.append({'part':part,'cells_checked':64,'visible_rgba_mismatches':0})
    for direction in DIRECTIONS:
        layers=[]
        for part in ['Weapon','WeaponHandOccluder','HeadHair','WeaponLightFront','BodyCostume','WeaponLightBack']:
            sheet=Image.new('RGBA',(2048,2048))
            for i in range(16):sheet.alpha_composite(Image.open(root/direction/part/f'{i:03d}.png').convert('RGBA'),(i%4*512,i//4*512))
            sheet.save(root/direction/(part+'-sheet.png'));layers.append((part,sheet))
        export_ora(root/direction/'layered-sprite-sheet.ora',layers)
    fx_checks=[]
    for direction in DIRECTIONS:
        for i in range(16):
            alpha=np.asarray(Image.open(root/direction/'WeaponLight'/f'{i:03d}.png').getchannel('A'))>8
            edge=bool(alpha[0].any() or alpha[-1].any() or alpha[:,0].any() or alpha[:,-1].any())
            if edge:raise ValueError(f'Effect clipped at {direction} {i}')
            if i not in effect_frames and alpha.any():raise ValueError('Wind-up/recovery effect must be clear')
            fx_checks.append({'direction':direction,'frame':i,'visible_pixels':int(alpha.sum()),'edge_touch':edge})
    assembly=json.loads((root/'assembly-audit.json').read_text())
    manifest={'status':'FOUR_DIRECTION_ATTACK_REVIEW_NOT_RUNTIME_APPROVAL','directions':DIRECTIONS,'frame_count_per_direction':16,'painted_pose_count':64,'mirroring':False,'layout':{'columns':'directions: SW, NW, NE, SE','rows':'chronological frames 0..15','cell_width':512,'cell_height':512,'sheet_width':2048,'sheet_height':8192},'assets':assets,'durations_ms':assembly['durations_ms'],'slow_durations_ms':assembly['slow_durations_ms'],'render_order_bottom_to_top':['WeaponLightBack','BodyCostume','WeaponLightFront','HeadHair','WeaponHandOccluder','Weapon'],'references_only':['Master is the full unmodified illustration; not an extra drawable layer.','WeaponLight is the merged FX reference; use the Back/Front sheets for actual depth ordering.'],'part_scope':'HeadHair is the visible head plus hair; BodyCostume is the complete clothed body. No hidden anatomy or separate naked-body/clothing is supplied.','trail_timing':{'first_emission':4,'last_emission':4,'fade_frame':5,'fade_opacity':.25,'clear_before':4,'clear_from':6,'maximum_recent_tip_path_fraction_of_blade':.65},'sheet_checks':checks,'effect_checks':fx_checks,'semantic_review':'Manual boundaries and world-depth approximation remain for visual inspection; zero recomposition error does not certify semantic cutout edges.'}
    manifest['trail_timing'].update(first_emission=effect_frames[0],last_emission=effect_frames[0],fade_frame=effect_frames[1],clear_before=effect_frames[0],clear_from=effect_frames[1]+1)
    if assembly.get('action')=='BasicAttack':manifest['trail_timing']['maximum_recent_tip_path_fraction_of_blade']=.55
    manifest['action']=assembly.get('action',assembly.get('classification','BasicAttack'))
    write_json(root/'sprite-sheets-manifest.json',manifest)
    print('PACKAGED_SHEETS',len(assets),flush=True)


def quality_audit(root):
    views=[]
    for direction in DIRECTIONS:
        folder=root/direction;annotations=json.loads((folder/'annotations.generated.json').read_text())['frames'];packing=json.loads((folder/'assembly.json').read_text())['frames'];guide=json.loads((root.parent/'eight-direction-guides'/direction/'manifest.json').read_text())['frames'];angles=[]
        masters=[Image.open(folder/'Master'/f'{i:03d}.png').convert('RGBA') for i in range(16)]
        pairs=[{'from':i-1,'to':i,'alpha_iou':round(_iou(masters[i-1],masters[i]),5)} for i in range(1,16)]
        for i,annotation in enumerate(annotations):
            record=guide[packing[i]['source_frame']];paint=np.array(annotation['weapon_tip'])-np.array(annotation['weapon_grip']);source=np.array(record['sword_tip'])-np.array(record['sword_grip']);angle=math.degrees(math.atan2(paint[1],paint[0])-math.atan2(source[1],source[0]));difference=abs((angle+180)%360-180)
            steel_length=float(np.linalg.norm(np.array(annotation['weapon_tip'])-np.array(annotation['weapon_guard'])))
            source_length=float(np.linalg.norm(source));readable=steel_length>=25 and source_length>=50
            angles.append({'frame':i,'source_frame':packing[i]['source_frame'],'angle_difference_degrees':round(difference,2),'painted_steel_length_px':round(steel_length,2),'source_projected_blade_length_in_1024px_guide':round(source_length,2),'angle_readable':readable,'foreshortening_review_needed':bool(steel_length>=25 and source_length<50)})
        valid=[a['angle_difference_degrees'] for a in angles if a['angle_readable']]
        views.append({'direction':direction,'adjacent_alpha_iou':pairs,'research_warning_pairs':[p for p in pairs if p['alpha_iou']<RESEARCH_IOU_WARNING],'valid_median_angle_difference_degrees':round(float(np.median(valid)),2) if valid else None,'blade_frames':angles})
    report={'status':'DIAGNOSTIC_OWNER_REVIEW_NOT_ANATOMICAL_ACCEPTANCE','research_helper':'audit_sprite_candidate._iou and RESEARCH_IOU_WARNING','research_iou_warning':RESEARCH_IOU_WARNING,'interpretation':'Low IoU can reflect the intended fast cut; it is a review flag, not proof of jitter. Angle medians exclude near-axis/occluded blades. Manual painted endpoints are approximate.','views':views,'known_review_items':['NE frame 8 shows a longer visible blade while the source blade projects to approximately 8.6px at 1024px; inspect and refine this foreshortened recovery pose.','Manual head/collar and blade/guard boundaries remain provisional.']}
    write_json(root/'quality-audit.json',report)
    write_json(root/'painted-blade-guide-audit.json',{'status':report['status'],'method':'manual painted endpoints versus matching source pose; angles excluded when the source projects below 50px or the painted blade below 25px','views':[{'direction':v['direction'],'valid_median_angle_difference_degrees':v['valid_median_angle_difference_degrees'],'frames':v['blade_frames']} for v in views]})


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('folder',type=Path);parser.add_argument('--stage',choices=['pack','parts','previews','sheets','quality','all'],default='all');args=parser.parse_args();root=args.folder
    if args.stage in ['pack','all']:pack(root)
    if args.stage in ['parts','all']:build_parts(root)
    if args.stage in ['pack','previews','all']:previews(root)
    if args.stage in ['sheets','all']:package_sheets(root)
    if args.stage in ['quality','all']:quality_audit(root)


if __name__=='__main__':main()
