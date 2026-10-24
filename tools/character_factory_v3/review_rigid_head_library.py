"""Review an explicitly authored head-angle library on unchanged covered armor.

Head-only rigid slot attachment is not same-pose paint-over certification.
No body, weapon or FX pixels are moved. Neck offsets and quantized face-angle
selection remain artistic draft decisions requiring visual review.
"""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from track_visible_cutouts import pin_inputs,verify_inputs,sha


def angle_difference(a,b):return (a-b+180)%360-180


def choose_entry(entries,yaw,pitch,hemisphere_guard=False):
    if hemisphere_guard:
        back=abs(angle_difference(yaw,0))>90
        entries=[e for e in entries if (abs(angle_difference(e['authored_yaw_degrees'],0))>90)==back]
        if not entries:raise ValueError('Head library lacks the required face hemisphere')
    return min(entries,key=lambda e:angle_difference(yaw,e['authored_yaw_degrees'])**2+.65*(pitch-e['authored_pitch_degrees'])**2)


def attach_head(image,anchor,scale,angle,target,size=(768,768)):
    if not math.isfinite(scale)or not 0<scale<=1:raise ValueError('Invalid head-only artist scale')
    if len(anchor)!=2 or len(target)!=2 or not all(math.isfinite(v)for v in [*anchor,*target,angle]):raise ValueError('Invalid rigid attachment')
    # Inverse map: positive angle follows the clockwise screen-space native roll.
    theta=math.radians(angle);c=math.cos(theta)/scale;s=math.sin(theta)/scale
    tx,ty=target;ax,ay=anchor
    return image.transform(size,Image.Transform.AFFINE,(c,s,ax-c*tx-s*ty,-s,c,ay+s*tx-c*ty),Image.Resampling.BICUBIC)


def review(library_path,slots_path,source,output,art_slots_path=None):
    if output.exists():raise ValueError('Choose a fresh review destination')
    library=json.loads(library_path.read_text());slots=json.loads(slots_path.read_text());raw=library_path.parent/library['raw']
    if sha(raw)!=library['raw_sha256']or slots['status']!='NATIVE_HEAD_SLOTS_VERIFIED':raise ValueError('Stale library or native head slots')
    entries=library['entries']
    if len({e['index']for e in entries})!=len(entries):raise ValueError('Duplicate library entry')
    if not library.get('library_not_same_pose_strip'):raise ValueError('Head library provenance must be explicit')
    directions=['SW','NW','NE','SE'];roles=['BodyCostume','HeadHair','Weapon','WeaponHandOccluder','WeaponLightBack','WeaponLightFront']
    rows=slots['frames'];art_rows={}
    if art_slots_path:
        art=json.loads(art_slots_path.read_text())
        if art['native_guide_job']!=slots['guide_job']:raise ValueError('2D slot guide differs')
        art_rows={(r['direction'],r['index']):r for r in art['frames']}
        if len(art_rows)!=len(rows):raise ValueError('Incomplete 2D art slots')
        for r in art['frames']:
            if sha(Path(r['source_head_mask']))!=r['source_sha256']:raise ValueError('Stale source head for 2D slot')
    inputs=[library_path,slots_path,raw,Path(__file__)]+[source/r['direction']/role/f"{r['index']:03d}.png"for r in rows for role in roles]
    inputs+=([art_slots_path]if art_slots_path else []);pinned=pin_inputs(inputs);output.mkdir(parents=True);sheet=Image.open(raw).convert('RGBA');w,h=sheet.size;cols,lines=library['grid'];heads={};removed=0
    for e in entries:
        i=e['index'];x=i%cols;y=i//cols;box=(round(x*w/cols),round(y*h/lines),round((x+1)*w/cols),round((y+1)*h/lines))
        crop=sheet.crop(box);a=np.array(crop);noise=(a[:,:,3]>0)&(a[:,:,3]<=library['low_alpha_noise_threshold']);removed+=int(noise.sum());a[noise]=0;a[a[:,:,3]==0]=0
        anchor=[e['neck_anchor_raw'][0]-box[0],e['neck_anchor_raw'][1]-box[1]];heads[i]=(Image.fromarray(a),anchor)
        (output/'library').mkdir(exist_ok=True);Image.fromarray(a).save(output/'library'/f'{i:03d}.png')
    frame_records=[];view_images={d:[]for d in directions}
    for r in rows:
        d=r['direction'];i=r['index'];orientation=r['head_orientation'];e=choose_entry(entries,orientation['yaw_degrees'],orientation['pitch_degrees'],library.get('preserve_face_hemisphere',False));im,anchor=heads[e['index']]
        offset=library['direction_neck_offset_author_px'][d];target=[a+b for a,b in zip(r['sockets']['neck'],offset)];roll=orientation['roll_degrees']-e['authored_roll_degrees']
        if art_rows:target=art_rows[d,i]['neck_pivot_author_px']
        legacy_head=Image.open(source/d/'HeadHair'/f'{i:03d}.png').convert('RGBA');old=np.array(legacy_head);rgb=old[:,:,:3].astype(float)/255;maximum=rgb.max(2);minimum=rgb.min(2)
        if library.get('attach_to_observed_head_center'):
            # Head-only rigid cosmetic placement; figure/root are never fitted.
            weights=old[:,:,3].astype(float);yy,xx=np.indices(weights.shape)
            if weights.sum()==0:raise ValueError('Empty observed head slot')
            observed=np.array([(xx*weights).sum()/weights.sum(),(yy*weights).sum()/weights.sum()])
            index=e['index'];origin=np.array([round((index%cols)*w/cols),round((index//cols)*h/lines)])
            skull=np.array(e['skull_anchor_raw'])-origin
            head=attach_head(im,skull,library['artist_scale'],roll,observed)
            theta=math.radians(roll);rotation=np.array([[math.cos(theta),-math.sin(theta)],[math.sin(theta),math.cos(theta)]])
            target=(observed+rotation@(np.array(anchor)-skull)*library['artist_scale']).tolist()
        else:head=attach_head(im,anchor,library['artist_scale'],roll,target)
        folder=output/d;(folder/'HeadHair').mkdir(parents=True,exist_ok=True);(folder/'Master').mkdir(exist_ok=True);head.save(folder/'HeadHair'/f'{i:03d}.png')
        # Draft material ownership only: the old HeadHair mask contains gold collar
        # fragments. Retain those exact pixels as a separate untransformed patch.
        saturated=(maximum-minimum)/np.maximum(maximum,1e-6)
        gold=(old[:,:,3]>0)&(rgb[:,:,0]>rgb[:,:,1]*1.05)&(rgb[:,:,1]>rgb[:,:,2]*1.45)&(saturated>.53)
        if library.get('preserve_visible_neck_underlay'):
            # Preserve existing visible neck/collar art in an explicitly scoped
            # underlay. This does not invent skin behind the original head.
            yy,xx=np.indices(old.shape[:2]);tx,ty=target
            radius=library['visible_neck_underlay_radius_author_px']
            gold|=(old[:,:,3]>0)&((xx-tx)**2+(yy-ty)**2<=radius**2)&(yy>=ty-4)
        patch=np.zeros_like(old);patch[gold]=old[gold];underlay=Image.fromarray(patch)
        (folder/'CollarOwnershipPatch').mkdir(exist_ok=True);underlay.save(folder/'CollarOwnershipPatch'/f'{i:03d}.png')
        composite=Image.new('RGBA',(768,768));reused={} 
        for role in ['WeaponLightBack','BodyCostume','CollarOwnershipPatch','WeaponLightFront','HeadHair','Weapon','WeaponHandOccluder']:
            if role=='HeadHair':part=head
            elif role=='CollarOwnershipPatch':part=underlay
            else:
                path=source/d/role/f'{i:03d}.png';part=Image.open(path).convert('RGBA');reused[role]={'path':str(path),'sha256':sha(path)}
            composite.alpha_composite(part)
        composite.save(folder/'Master'/f'{i:03d}.png');view_images[d].append(composite)
        frame_records.append({'direction':d,'index':i,'library_entry':e['index'],'source_action':r['source_action'],'source_frame':r['source_frame'],'native_orientation':orientation,'head_artist_scale':library['artist_scale'],'head_roll_degrees':roll,'target_neck_author_px':target,'collar_patch_pixels':int(gold.sum()),'head_sha256':sha(folder/'HeadHair'/f'{i:03d}.png'),'unchanged_reused_parts':reused})
    contact=Image.new('RGB',(1280,320),(225,225,225));draw=ImageDraw.Draw(contact)
    for col,d in enumerate(directions):
        image=view_images[d][0].crop((270,300,510,570)).resize((264,297));contact.paste(image,(col*320+28,20),image);draw.text((col*320+8,4),d,fill='black')
    contact.save(output/'first-pose-contact.png')
    boards=[]
    for i in range(16):
        board=Image.new('RGB',(1280,360),(225,225,225));draw=ImageDraw.Draw(board)
        for col,d in enumerate(directions):
            image=view_images[d][i].crop((240,260,560,620));board.paste(image,(col*320,0),image);draw.text((col*320+8,5),f'{d} {i:02d}',fill='black')
        boards.append(board)
    palette=Image.new('RGB',(1280,360*len(boards)))
    for i,b in enumerate(boards):palette.paste(b,(0,i*360))
    palette=palette.quantize(colors=255);frames=[b.quantize(palette=palette,dither=Image.Dither.NONE)for b in boards]
    for name,delay in [('four-view-normal.gif',65),('four-view-slow.gif',160)]:frames[0].save(output/name,save_all=True,append_images=frames[1:],duration=delay,loop=0,disposal=2)
    verify_inputs(pinned)
    result={'status':'DRAFT_RIGID_HEAD_SLOT_REVIEW_NOT_ADMITTED','guide_job':slots['guide_job'],'implementation_sha256':sha(Path(__file__)),'art_slots_sha256':sha(art_slots_path)if art_slots_path else None,'library_sha256':sha(library_path),'native_slots_sha256':sha(slots_path),'low_alpha_noise_pixels_cleared':removed,'body_weapon_fx_pixels_transformed':False,'same_pose_paint_over_claimed':False,'hidden_neck_and_foreground_arm_review_required':True,'runtime_admitted':False,'frames':frame_records}
    (output/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['library','slots','source','output']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--art-slots',type=Path);a=p.parse_args();r=review(a.library,a.slots,a.source,a.output,a.art_slots);print(json.dumps({'status':r['status'],'frames':len(r['frames'])}))
