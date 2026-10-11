"""Compile authoring depth into ordinary ordered 2D slots for the existing runtime.

Core parts retain complete pixels, partitioned by their per-pixel core depth
rank. The union includes alternate garment geometry, so any outfit and sword
combination uses the same ordered slots. No depth map reaches the renderer.
"""
import hashlib,importlib.util,json,subprocess,sys,copy,shutil
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'authoring/characters/swordsman-production/fantasy-base-01';DEST=OUT/'runtime';SOURCES=ROOT/'.character-tools/runtime-sources/fantasy-golden-01'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
packer=module('existing_packer',ROOT/'tools/pack-modular-sprites.py');validator=module('existing_validator',ROOT/'tools/validate-sprites.py')
package=read(OUT/'package.json');bank=read(OUT/'factory/swap-bank.json');assert bank['baseNativeSHA256']==package['nativeSHA256']
key=hashlib.sha256((bank['bankSHA256']+sha(ROOT/'tools/bake-fantasy-swap-bank.py')).encode()).hexdigest()[:16]
basecache=ROOT/'.character-tools/sprite-bakes'/package['cacheKey'];swapcache=ROOT/'.character-tools/swap-bakes'/key
for clip in package['clips']:assert (swapcache/clip['name']/'receipt.json').is_file(),'Finish swap bake: '+clip['name']
core=['BodyOutfit','HeadHair','Cape','Headgear','Offhand','BodyAlt'];prefixes=['BaseBody','Hair','BackAccessory','Headgear','Offhand'];logical=prefixes
specs={};slots={};defaults={};order=[];appearances={g:{} for g in ['outfit','weapon','headgear','offhand','cape']}
def part(id,slot,kind,rank):specs[id]={'slot':slot,'kind':kind,'rank':rank}
for rank in range(len(core)+1):
    slot='Weapon'+str(rank);slots[slot]='Weapon';order.append(slot);defaults[slot]=f'weapon-default-r{rank}'
    for variant,kind in [('default','Weapon'),('alternate','WeaponAlt'),('none','Empty')]:
        id=f'weapon-{variant}-r{rank}';part(id,slot,kind,rank);appearances['weapon'].setdefault(variant,{})[slot]=id
    if rank==len(core):continue
    for m,prefix in zip(core[:5],prefixes):
        slot=prefix+str(rank);slots[slot]=prefix;order.append(slot);id=m.lower()+f'-r{rank}';part(id,slot,m,rank);defaults[slot]=id
        group={'BodyOutfit':'outfit','Cape':'cape','Headgear':'headgear','Offhand':'offhand'}.get(m)
        if group:appearances[group].setdefault('default',{})[slot]=id
        if m=='BodyOutfit':
            alt=f'crimson-outfit-r{rank}';part(alt,slot,'BodyAlt',rank);appearances['outfit'].setdefault('alternate',{})[slot]=alt
        if m in ['Headgear','Offhand','Cape']:
            empty=m.lower()+f'-none-r{rank}';part(empty,slot,'Empty',rank);appearances[group].setdefault('none',{})[slot]=empty
            if m!='Cape':defaults[slot]=empty
slots['Outfit']='Outfit';defaults['Outfit']='outfit-registration';order.append('Outfit');part('outfit-registration','Outfit','Empty',0)
d={'version':'0.1','characterId':'fantasy-golden-01','classId':'Swordsman','bodyVariant':'male','directions':package['directions'],'mirroring':'none',
   'tags':['DEV_ONLY','PLACEHOLDER','NOT_FINAL_ART'],'source':{'status':'DEV_ONLY','reference':'authoring/characters/swordsman-production/fresh-2d/candidate-01/candidate.png','approvedBy':None,
   'camera':'Fixed orthographic camera, 25 degree elevation; eight real rotations','handedness':'right','normalization':{'sourceFrameWidth':320,'sourceFrameHeight':320,'sourceRootAnchor':[160,264],'scale':1},
   'designLocks':['owner-approved concept retained as reference','body + outfit and head + hair follow owner Ragnarok layer grouping','depth used only to compile ordinary 2D slot portions','no pose, root, scale or timing overrides']},
   'canvas':{'frameWidth':320,'frameHeight':320,'rootAnchorX':160,'rootAnchorY':264,'referenceHeight':176},'slots':slots,'defaultParts':defaults,'drawOrder':order,
   'parts':{id:{'slot':s['slot'],'frames':{}} for id,s in specs.items()},'atlases':{},'clips':{}}
used_slots=set();metrics=[];holdout_records=[];clipped=[]
for clip in package['clips']:
    name=clip['name'];receipt=read(swapcache/name/'receipt.json');assert receipt['baseNativeSHA256']==package['nativeSHA256']
    d['clips'][name]={'loop':clip['loop'],'durations':clip['durationsMs'],'directions':{direction:{'frames':[{'frameIndex':f-1,'sockets':receipt['sockets'][f'{direction}-{f:03}']} for f in range(1,clip['frames']+1)]} for direction in package['directions']}}
    records=[]
    for direction in package['directions']:
        for frame in range(1,clip['frames']+1):
            tag=f'{direction}-{frame:03}'
            a=np.asarray(Image.open(basecache/name/(tag+'-tile.png')).convert('RGBA'));az=np.asarray(Image.open(basecache/name/(tag+'-depth.png')))
            b=np.asarray(Image.open(swapcache/name/(tag+'-tile.png')).convert('RGBA'));bz=np.asarray(Image.open(swapcache/name/(tag+'-depth.png')))
            colors={'BodyOutfit':a[:,320:640].copy(),'HeadHair':a[:,640:960].copy(),'Weapon':a[:,960:1280].copy(),'Cape':a[:,1280:1600].copy(),
                    'BodyAlt':b[:,:320].copy(),'WeaponAlt':b[:,320:640].copy(),'Headgear':b[:,640:960].copy(),'Offhand':b[:,960:1280].copy()}
            depths={'BodyOutfit':az[:,320:640],'HeadHair':az[:,640:960],'Weapon':az[:,960:1280],'Cape':az[:,1280:1600],
                    'BodyAlt':bz[:,:320],'WeaponAlt':bz[:,320:640],'Headgear':bz[:,640:960],'Offhand':bz[:,960:1280]}
            for kind,color in colors.items():
                alpha=color[:,:,3];border=int(np.count_nonzero(alpha[0]))+int(np.count_nonzero(alpha[-1]))+int(np.count_nonzero(alpha[1:-1,0]))+int(np.count_nonzero(alpha[1:-1,-1]))
                if border:clipped.append({'action':name,'direction':direction,'frame':frame,'part':kind,'borderPixels':border})
            z=np.stack([depths[m] for m in core]);sort=np.argsort(z,axis=0,kind='stable')[::-1];ranks={m:np.argmax(sort==i,axis=0).astype(np.uint8) for i,m in enumerate(core)}
            priority=np.array([0,1,3,4,5,0])[:,None,None]
            buckets={m:np.sum((z>depths[m])|((z==depths[m])&(priority>2)),axis=0).astype(np.uint8) for m in ['Weapon','WeaponAlt']}
            # Verify actual opaque hand coverage against an unmasked blade/hilt
            # render, rather than assuming a rounded center lies inside a finger.
            raw=b[:,1280:1600];hand=b[:,1600:1920];covered=(raw[:,:,3]>224)&(hand[:,:,3]>224)&(bz[:,1600:1920]<bz[:,1280:1600])
            retained=colors['Weapon'][:,:,3][covered];bad=int(np.sum(retained>96))
            holdout_records.append({'action':name,'direction':direction,'frame':frame,'opaqueHandCoveredWeaponPixels':int(covered.sum()),'residualPixelsAbove96':bad})
            records.append((colors,ranks,buckets))
    for id,info in specs.items():
        strip=Image.new('RGBA',(320*clip['frames'],320*8));kind=info['kind'];rank=info['rank']
        for i,(colors,ranks,buckets) in enumerate(records):
            if kind=='Empty':continue
            mask=(buckets[kind] if kind in buckets else ranks[kind])==rank
            pixels=colors[kind].copy();pixels[~mask]=0
            if np.any(pixels[:,:,3]):used_slots.add(info['slot'])
            strip.paste(Image.fromarray(pixels),((i%clip['frames'])*320,(i//clip['frames'])*320))
        path=SOURCES/'parts'/id/name/'strip.png';path.parent.mkdir(parents=True,exist_ok=True);strip.save(path,compress_level=1);del strip
        single=copy.deepcopy(d);single['parts']={id:{'slot':info['slot'],'frames':{}}};single['clips']={name:d['clips'][name]}
        packer.pack(single,SOURCES,DEST,deduplicate=True)
        d['parts'][id]['frames'].update(single['parts'][id]['frames']);d['atlases'].update(single['atlases'])
    del records
    print('RUNTIME_PACKED '+name,flush=True)
assert not clipped, ('Clipped equipment/outfit bake',clipped)
# Remove globally empty implementation slots, retaining the logical Outfit
# registration slot for the owner's combined body/outfit grouping.
used_slots.add('Outfit');d['slots']={s:l for s,l in slots.items() if s in used_slots};d['defaultParts']={s:p for s,p in defaults.items() if s in used_slots};d['drawOrder']=[s for s in order if s in used_slots]
d['parts']={id:p for id,p in d['parts'].items() if p['slot'] in used_slots};needed={ref['atlasId'] for p in d['parts'].values() for ref in p['frames'].values()};d['atlases']={id:a for id,a in d['atlases'].items() if id in needed}
for group,variants in appearances.items():
    for variant,mapping in variants.items():variants[variant]={s:p for s,p in mapping.items() if s in used_slots}
# Immutable atlas URLs also work with older service workers that predate the
# development-cache opt-out. Their contents always identify the actual bake.
for atlas in d['atlases'].values():
    original=DEST/atlas['file'];unique=original.with_name(original.stem+'-'+sha(original)[:12]+original.suffix)
    if not unique.exists():shutil.copyfile(original,unique)
    atlas['file']=unique.relative_to(DEST).as_posix()
target=DEST/'assets/characters/fantasy-golden-01/sprite.json';target.write_text(json.dumps(d,indent=2)+'\n')
immutable=target.with_name('sprite-'+package['nativeSHA256'][:12]+'-'+bank['bankSHA256'][:12]+'.json')
shutil.copyfile(target,immutable)
(DEST/'appearance-sets.json').write_text(json.dumps(appearances,indent=2)+'\n')
schema=read(ROOT/'assets/characters/schemas/sprite-definition.schema.json');validator.jsonschema.Draft202012Validator(schema).validate(d);validator.validate_file(target,DEST,schema)
subprocess.run(['C:/Program Files/nodejs/node.exe',str(ROOT/'tools/validate-modular-metadata.cjs'),str(target)],check=True,cwd=ROOT)
report={'technicalVerdict':'PASS','nativeSHA256':package['nativeSHA256'],'bankSHA256':bank['bankSHA256'],'directions':package['directions'],'requiredFramePositions':1392,'totalFramePositions':1456,
        'slots':len(d['slots']),'parts':len(d['parts']),'atlases':len(d['atlases']),'existingRendererSHA256':sha(ROOT/'modular-sprites.js'),
        'runtimeRepresentation':'ordinary RGBA PNG atlases, shared sockets, timing and ordered 2D slots; no depth maps or 3D',
        'outfitVariantScope':'crimson garment with fitted closed cuirass and raised bronze border; same source body, rig and motion','ownerApproved':False,'runtimeDefaultRegistered':False,
        'clippedEquipmentBorders':clipped,'holdout':holdout_records}
(OUT/'factory/runtime-compatibility.json').write_text(json.dumps(report,indent=2)+'\n');print('RUNTIME_COMPATIBILITY_PASS',flush=True)
