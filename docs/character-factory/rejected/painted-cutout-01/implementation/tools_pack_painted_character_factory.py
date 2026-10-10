"""Adapt a COMPLETE painted factory bake to the existing modular sprite packer.

Partial views and missing actions fail before any package write. PIL is only used
for the requested deterministic frame/strip compilation, not source-art repair.
No alternate skeletal renderer is shipped to ASTRAEON.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

from PIL import Image
from painted_character_factory import DIRECTIONS, SLOTS, read_spec, require_coverage, sample_pose

ROOT = Path(__file__).resolve().parents[1]


def adapt(spec, renders, sources, repository, character_id, actions):
    require_coverage(spec, DIRECTIONS, actions)
    registration = spec['registration']
    # Fixed patch compile: every pixel, socket and root gets one shared 0.5 scale.
    definition = {'version': '0.1', 'characterId': character_id, 'classId': 'Swordsman',
                  'bodyVariant': 'male', 'directions': DIRECTIONS, 'mirroring': 'none',
                  'tags': ['DEV_ONLY','REQUIRES_OWNER_VISUAL_REVIEW'],
                  'canvas': {'frameWidth':160,'frameHeight':160,'rootAnchorX':80,
                             'rootAnchorY':132,'referenceHeight':88},
                  'source': {'status':'DEV_ONLY','reference':None,'approvedBy':None,
                             'camera':'Painted attachments on exact body headings; fixed 30deg orthographic camera',
                             'handedness':'right','normalization':{'sourceFrameWidth':320,
                             'sourceFrameHeight':320,'sourceRootAnchor':[160,264],'scale':0.5},
                             'designLocks':['approved concept identity','root','scale','handedness','painted 2D']},
                  'slots': {slot: ('BaseBody' if slot=='BodyHands' else 'Outfit' if slot=='Hands' else slot) for slot in SLOTS},
                  'defaultParts': {slot:slot.lower() for slot in SLOTS}, 'drawOrder':SLOTS,
                  'parts':{}, 'atlases':{}, 'clips':{}}
    parts = [(slot.lower(), 'default', slot) for slot in SLOTS]
    parts += [('weapon-training','training','Weapon'),('outfit-steel','steel','Outfit')]
    pending = []
    for part, variant, slot in parts:
        definition['parts'][part] = {'slot':slot,'tags':['DEV_ONLY','REQUIRES_OWNER_VISUAL_REVIEW'],'frames':{}}
        for action in actions:
            count = len(spec['motions'][action]['durations'])
            strip = Image.new('RGBA',(160*count,160*8))
            for row,direction in enumerate(DIRECTIONS):
                for index in range(count):
                    file = renders/variant/action/direction/slot/f'{index:02}.png'
                    with Image.open(file) as image:
                        image.load()
                        if image.mode!='RGBA' or image.size!=(320,320):
                            raise ValueError(f'Invalid registered frame: {file}')
                        if image.getchannel('A').getextrema()[0]!=0:
                            raise ValueError(f'Opaque frame: {file}')
                        frame=image.resize((160,160),Image.Resampling.LANCZOS)
                        strip.paste(frame,(160*index,160*row))
            pending.append((sources/'parts'/part/action/'strip.png',strip))
    for action in actions:
        motion=spec['motions'][action]
        clip={'loop':motion['loop'],'durations':motion['durations'],'directions':{}}
        for direction in DIRECTIONS:
            clip['directions'][direction]={'frames':[{'frameIndex':i,
                'sockets':{k:[round(c*0.5,6) for c in point] for k,point in sample_pose(spec,direction,action,i)['sockets'].items()}}
                for i in range(len(motion['durations']))]}
        definition['clips'][action]=clip
    # Missing files/coverage/source validation above completes before any write.
    for file,strip in pending:
        file.parent.mkdir(parents=True,exist_ok=True)
        strip.save(file,compress_level=9)
    sources.mkdir(parents=True,exist_ok=True)
    (sources/'definition.json').write_text(json.dumps(definition,indent=2)+'\n',encoding='utf-8')
    module_spec=importlib.util.spec_from_file_location('astraeon_existing_packer',ROOT/'tools/pack-modular-sprites.py')
    module=importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    target=module.pack(definition,sources,repository,deduplicate=True)
    (sources/'compile-receipt.json').write_text(json.dumps({'status':'DEV_ONLY','sourceRegistration':registration,
        'scale':0.5,'target':str(target),'sourceImageHashes':{k:v['sha256'] for k,v in spec['images'].items()},
        'definitionSHA256':hashlib.sha256(target.read_bytes()).hexdigest()},indent=2)+'\n',encoding='utf-8')
    return target


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec',type=Path,required=True)
    parser.add_argument('--renders',type=Path,required=True)
    parser.add_argument('--sources',type=Path,required=True)
    parser.add_argument('--repository',type=Path,default=ROOT)
    parser.add_argument('--character-id',default='swordsman-painted-factory')
    args=parser.parse_args()
    spec=read_spec(args.spec)
    print(adapt(spec,args.renders,args.sources,args.repository,args.character_id,spec['requiredActions']))
