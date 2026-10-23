"""Pack complete same-frame imports into the real modular sprite runtime.

No pose, missing motion, timing, event or source socket is invented. All inputs
are checked before the target character directory is replaced.
"""
import argparse,hashlib,json,math,shutil,subprocess,tempfile
from pathlib import Path
import numpy as np
from PIL import Image
from patch001_factory import ROOT,BASE,read

CORE=('BodyCostume','HeadHair','Weapon')
ORDER=('WeaponLightBack','BackAccessory','BodyCostume','HeadHair','Weapon','WeaponLightFront','WeaponHandOccluder','Headgear')

def trimmed_source(im):
    """Trim transparent storage only; retain the original integer placement."""
    bbox=im.getchannel('A').getbbox()
    return (im.crop(bbox),list(bbox[:2]))if bbox else(Image.new('RGBA',(1,1)),[0,0])

def atlas_pages(pixels,limit=4096,padding=2):
    """Stream one shelf-packed page at a time instead of retaining all pages."""
    page=Image.new('RGBA',(limit,limit));x=y=padding;row=0;used=padding;placements=[]
    for index,im in enumerate(pixels):
        if im.width+2*padding>limit or im.height+2*padding>limit:raise ValueError('Source part exceeds atlas page')
        if x+im.width+padding>limit:x=padding;y+=row;row=0
        if y+im.height+padding>limit:
            yield page.crop((0,0,used,y+row)),placements
            page=Image.new('RGBA',(limit,limit));x=y=padding;row=0;used=padding;placements=[]
        page.paste(im,(x,y));placements.append((index,[x,y,im.width,im.height]));x+=im.width+padding;row=max(row,im.height+padding);used=max(used,x)
    if placements:yield page.crop((0,0,used,y+row)),placements

def composed_draw_order(base_order,roles):
    base=[r for r in roles if not r.startswith('WeaponLight')]
    if len(base_order)!=len(set(base_order))or any(r not in base for r in base_order):raise ValueError('Invalid imported base draw order')
    order=list(base_order)+[r for r in base if r not in base_order]
    if 'WeaponLightBack'in roles:order.insert(0,'WeaponLightBack')
    if 'WeaponLightFront'in roles:order.insert(order.index('Weapon')+1,'WeaponLightFront')
    return order

def downsample_partition(parts,order,size):
    """One shared full-canvas reduction, with exclusive visible-pixel ownership.

    Independent RGBA reduction can overlap adjacent head/body alpha and darken
    their seam. Ownership is selected from reduced coverage, but output pixels
    always come from the one reduced complete master. No figure fitting occurs.
    """
    if not parts or set(order)!=set(parts):raise ValueError('Parts/order mismatch')
    canvas=next(iter(parts.values())).size
    if any(im.size!=canvas for im in parts.values()):raise ValueError('Part canvases differ')
    visible_count=np.zeros((canvas[1],canvas[0]),dtype=np.uint8)
    for im in parts.values():visible_count+=(np.array(im.getchannel('A'))>0).astype(np.uint8)
    if np.any(visible_count>1):raise ValueError('Exclusive visible-cutout partition cannot discard overlapping hidden surfaces')
    master=Image.new('RGBA',canvas)
    for role in order:master.alpha_composite(parts[role].convert('RGBA'))
    reduced=master.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA');pixels=np.array(reduced);pixels[pixels[:,:,3]==0]=0
    coverage=np.stack([np.array(parts[r].getchannel('A').resize(size,Image.Resampling.LANCZOS))for r in order])
    owner=np.argmax(coverage,axis=0);output={}
    for i,role in enumerate(order):
        layer=np.zeros_like(pixels);selected=owner==i;layer[selected]=pixels[selected];output[role]=Image.fromarray(layer)
    return output,Image.fromarray(pixels)

def validate_timing(action,timing):
    durations=timing.get('durations',[])
    if len(durations)!=action['frames']or any(isinstance(v,bool)or not isinstance(v,(int,float))or not math.isfinite(v)or v<=0 for v in durations):raise ValueError('Missing explicit positive per-pose timing')
    events=timing.get('events',[]);total=sum(durations)
    if not isinstance(events,list):raise ValueError('Events must be a list')
    for event in events:
        index=event.get('frameIndex');time=event.get('timeMs');phase=event.get('phase')
        if not isinstance(index,int)or isinstance(index,bool)or not 0<=index<len(durations)or not isinstance(time,int)or isinstance(time,bool)or not 0<=time<=total or not isinstance(phase,(int,float))or isinstance(phase,bool)or not math.isfinite(phase)or abs(phase-time/total)>1e-5:raise ValueError('Invalid semantic event timing')
        if not (sum(durations[:index])<=time<sum(durations[:index+1])or index==len(durations)-1 and time==total):raise ValueError('Semantic event outside declared pose')
    if 'cycleDistance'in timing and(not action['loop']or isinstance(timing['cycleDistance'],bool)or not isinstance(timing['cycleDistance'],(float,int))or not math.isfinite(timing['cycleDistance'])or timing['cycleDistance']<=0):raise ValueError('Invalid locomotion cycle distance')
    return durations,events

def preflight(character,config,ledger,base,timings):
    klass=config['classes'][character['class']];imports={};errors=[]
    for action in klass['actions']:
        jobs=[j for j in ledger['paint_jobs'].values()if j['character']==character['id']and action in j['actions']]
        if len(jobs)!=1:errors.append(action+': missing or ambiguous paint job');continue
        job=jobs[0];folder=base/'cutouts'/job['id']
        if not(folder/'import-receipt.json').is_file()or not(folder/'bindings.json').is_file():errors.append(action+': actual cutout import missing');continue
        receipt=read(folder/'import-receipt.json');binding=read(folder/'bindings.json')
        expected={(d,i)for d in klass['actions'][action]['authored_directions']for i in range(klass['actions'][action]['frames'])};actual={(f['direction'],f['index'])for f in binding['frames']}
        if any(not set(CORE)<=set(f.get('assets',{})) for f in binding['frames']):errors.append(action+': required visible cutout slot missing');continue
        if receipt.get('paint_job')!=job['id']or binding.get('paint_job')!=job['id']or binding.get('character')!=character['id']or len(actual)!=len(binding['frames'])or receipt.get('guide_job')!=job['guide_job']or not receipt.get('all_frames_present')or receipt.get('recomposition_mismatches')!=0 or not expected<=actual:errors.append(action+': stale or incomplete import');continue
        try:
            validate_timing(klass['actions'][action],timings[action])
            if action in ['BasicAttack','SkillAction','SpinAttack','ArrowRain','TrapPlace','CastRelease']and not any(e.get('name')in ['impact','projectileRelease','release']for e in timings[action].get('events',[])):raise ValueError('Missing explicit contact/release marker')
        except (KeyError,ValueError)as error:errors.append(action+': '+str(error));continue
        imports[action]=(job,binding)
    if errors:raise ValueError('Cannot package '+character['id']+'\n'+'\n'.join(errors))
    return imports

def pack(character_id,timing_path,repository=ROOT,base=BASE,*,raster_mode='source-composite'):
    if raster_mode not in ['source-composite','visible-partition']:raise ValueError('Unknown raster mode')
    config=read(base/'factory.json');ledger=read(base/'ledger.json');character=next((c for c in config['characters']if c['id']==character_id),None)
    if character is None:raise ValueError('Unknown patch character')
    timings=read(timing_path);imports=preflight(character,config,ledger,base,timings);index=read(base/'cutout-store/index.json');klass=config['classes'][character['class']]
    width,height=config['canvas']['runtime'];author=config['canvas']['authoring'];scale=width/author[0]
    if width/author[0]!=height/author[1]:raise ValueError('Nonuniform runtime canvas transform')
    roles=set(CORE)
    for _,binding in imports.values():
        for frame in binding['frames']:roles.update(frame['assets'])
    roles=[r for r in ORDER if r in roles]
    if set(roles)!={r for _,b in imports.values()for f in b['frames']for r in f['assets']}|set(CORE):raise ValueError('Unknown imported role')
    part_ids={r:r.lower().replace('weaponhandoccluder','weapon-hand-occluder').replace('bodycostume','body-costume').replace('headhair','head-hair')for r in roles}
    d={'version':'0.1','characterId':character_id,'classId':character['class'],'bodyVariant':character['body_variant'],'layerMode':'visible-cutout','directions':config['direction_inputs'],'mirroring':'none','canvas':{'frameWidth':width,'frameHeight':height,'rootAnchorX':config['canvas']['runtime_root'][0],'rootAnchorY':config['canvas']['runtime_root'][1],'referenceHeight':config['canvas']['runtime_reference_height']},'source':{'status':'DEV_ONLY','camera':'factory-v3 locked orthographic camera; uniform1536-to240 full-canvas reduction','handedness':'right','reference':str((base/'factory.json').relative_to(repository))},'tags':['DEV_ONLY','PLACEHOLDER','NOT_FINAL_ART','PATCH_0_0_1_CANDIDATE'],'slots':{r:r for r in roles},'defaultParts':part_ids,'drawOrder':roles,'parts':{part_ids[r]:{'slot':r,'frames':{}}for r in roles},'atlases':{},'clips':{}}
    if raster_mode=='source-composite':d['canvas'].update({'compositionWidth':author[0],'compositionHeight':author[1]})
    d['parts'][part_ids['HeadHair']]['cosmeticId']='hair-native';d['parts'][part_ids['BodyCostume']]['cosmeticId']=character['class'].lower()+'-traveler'
    pixels=[];unique={};recomposition=0
    def asset_image(asset_id,role,frame,fit):
        a=index['assets'][asset_id]
        if any(a.get(k)!=v for k,v in {'role':role,'fit_id':fit,'pose_id':frame['pose_id'],'camera_id':frame['camera_id'],'root':frame['sockets']['root'],'canvas':author}.items()):raise ValueError('Cutout fitting changed: '+role)
        obj=index['objects'][a['object']];path=(repository/obj['file']).resolve()
        if not path.is_relative_to(repository.resolve()):raise ValueError('Cutout object escaped repository')
        im=Image.open(path).convert('RGBA');arr=np.array(im);arr[arr[:,:,3]==0]=0
        if list(im.size)!=author or hashlib.sha256(arr.tobytes()).hexdigest()!=a['object']:raise ValueError('Stored pixels changed')
        return im
    for action,spec in klass['actions'].items():
        job,binding=imports[action];frames={(f['direction'],f['index']):f for f in binding['frames']};durations,events=validate_timing(spec,timings[action]);clip={'durations':durations,'loop':spec['loop'],'authoredDirections':spec['authored_directions'],'directionMap':spec['direction_map'],'events':events,'directions':{}}
        if 'cycleDistance'in timings[action]:clip['cycleDistance']=timings[action]['cycleDistance']
        d['clips'][action]=clip
        for direction in spec['authored_directions']:
            seq={'frames':[]};clip['directions'][direction]=seq
            for i in range(spec['frames']):
                frame=frames[(direction,i)];parts={r:asset_image(a,r,frame,job['fit_id'])for r,a in frame['assets'].items()};base_order=frame.get('base_draw_order',[r for r in roles if r in parts and not r.startswith('WeaponLight')]);ordered=list(base_order)
                # Explicit authored base order wins. FX retain their back/front
                # relationship to the weapon; missing optional roles stay empty.
                for r in roles:
                    if r not in parts:parts[r]=Image.new('RGBA',tuple(author))
                ordered=composed_draw_order(ordered,roles)
                # Independent FX must never be merged into the base ownership
                # partition or they would erase the interchangeable body pixels.
                base_order=[r for r in ordered if not r.startswith('WeaponLight')];base_parts={r:parts[r]for r in base_order}
                if raster_mode=='visible-partition':
                    reduced,master=downsample_partition(base_parts,base_order,(width,height));check=Image.new('RGBA',(width,height))
                    for r in base_order:check.alpha_composite(reduced[r])
                    if check.tobytes()!=master.tobytes():raise ValueError('Runtime base recomposition changed')
                else:reduced=dict(parts)
                for r in ordered:
                    if r not in reduced:reduced[r]=parts[r].convert('RGBa').resize((width,height),Image.Resampling.LANCZOS).convert('RGBA')
                    im=reduced[r];arr=np.array(im);arr[arr[:,:,3]==0]=0;im=Image.fromarray(arr);offset=None
                    if raster_mode=='source-composite':
                        original=im;im,offset=trimmed_source(im)
                        if original.getchannel('A').getbbox()is None:offset=[min(author[0]-1,round(frame['sockets']['root'][0])),min(author[1]-1,round(frame['sockets']['root'][1]))]
                        restored=Image.new('RGBA',tuple(author));restored.paste(im,tuple(offset))
                        if restored.tobytes()!=original.tobytes():raise ValueError('Atlas trimming changed source pixels')
                    key=hashlib.sha256(str(im.size).encode()+im.tobytes()).hexdigest()
                    if key not in unique:unique[key]=len(pixels);pixels.append(im)
                    frame_id=f'{character_id}_{part_ids[r]}_{action}_{direction}_{i:02d}';d['parts'][part_ids[r]]['frames'][frame_id]={'pixelIndex':unique[key]}
                    if offset is not None:d['parts'][part_ids[r]]['frames'][frame_id]['offset']=offset
                sockets={k:[v[0]*scale,v[1]*scale]for k,v in frame['sockets'].items()};seq['frames'].append({'frameIndex':i,'sockets':sockets,'drawOrder':ordered})
    verifier="const fs=require('node:fs'),api=require(process.argv[1]);const errors=api.validateDefinition(JSON.parse(fs.readFileSync(0,'utf8')));if(errors.length){process.stderr.write(errors.join('\\n'));process.exit(1)}"
    target=repository/'assets/characters'/character_id;target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target.parent,prefix='.packing-')as temporary:
        temp=Path(temporary);(temp/'atlases').mkdir()
        locations={}
        for i,(page,placements)in enumerate(atlas_pages(pixels)):
            name=f'page-{i}';page.save(temp/'atlases'/f'{name}.png');d['atlases'][name]={'file':f'assets/characters/{character_id}/atlases/{name}.png','width':page.width,'height':page.height}
            for index,rect in placements:locations[index]={'atlasId':name,'rect':rect}
        for part in d['parts'].values():
            for ref in part['frames'].values():ref.update(locations[ref.pop('pixelIndex')])
        result=subprocess.run(['node','-e',verifier,str(ROOT/'modular-sprites.js')],input=json.dumps(d),text=True,capture_output=True)
        if result.returncode:raise ValueError('Runtime definition validation failed: '+result.stderr)
        (temp/'sprite.json').write_text(json.dumps(d,indent=2)+'\n');receipt={'character':character_id,'actions':list(d['clips']),'source_paint_jobs':sorted({j['id']for j,_ in imports.values()}),'unique_pixel_frames':len(pixels),'base_recomposition_mismatches':recomposition,'raster_mode':raster_mode,'source_resolution_layers_preserved':raster_mode=='source-composite','status':'PACKED_CANDIDATE_REQUIRES_GAMEPLAY_VISUAL_REVIEW','owner_approved':False,'runtime_admitted':False};(temp/'package-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        if target.exists():raise ValueError('Target exists; preserve the existing package and review replacement explicitly')
        shutil.copytree(temp,target)
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--character',required=True);p.add_argument('--timing',type=Path,required=True);p.add_argument('--raster-mode',choices=['source-composite','visible-partition'],default='source-composite');a=p.parse_args();print(json.dumps(pack(a.character,a.timing,raster_mode=a.raster_mode)))
