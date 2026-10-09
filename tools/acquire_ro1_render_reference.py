#!/usr/bin/env python3
"""Capture public rendered RO reference privately, never into runtime assets.

The API renders existing action indices. Its APNG delays are RENDERED_REFERENCE,
not proof of raw ACT intervals or gameplay attack speed. Bounded concurrency and
local reuse avoid repeatedly rendering the same reference on the hobby instance.
"""
import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image, ImageDraw

DIRECTIONS = ['S','SW','W','NW','N','NE','E','SE']
PHASES = {
    'idle':['stand'],
    'walk':['passingRightSupport','advanceLeft','contactLeft','loadLeft',
            'passingLeftSupport','advanceRight','contactRight','loadRight'],
    'attack':['readyRaised','anticipation1','anticipation2','anticipation3',
              'weightCommit','contactSweep','followThrough1','followThrough2','recoveryIntent']
}

def capture(root, action, family, direction, weapon=True):
    folder=root/action; folder.mkdir(parents=True,exist_ok=True)
    index=family+DIRECTIONS.index(direction)
    params={'job':1,'gender':'male','head':1,'headdir':'straight','action':index,
            'enableShadow':'false','canvas':'192x192+96+160'}
    if weapon:params['weapon']=2
    url='https://assets.latam-tools.com.br/image?'+urllib.parse.urlencode(params)
    path=folder/(direction+'.apng')
    if not path.exists():
        with urllib.request.urlopen(url,timeout=45) as response:path.write_bytes(response.read())
    image=Image.open(path); frames=[]; delays=[]; hashes=[]
    for i in range(image.n_frames):
        image.seek(i); frame=image.convert('RGBA');frames.append(frame)
        delays.append(image.info.get('duration'))
        hashes.append(hashlib.sha256(frame.tobytes()).hexdigest())
        frame.save(folder/(direction+f'-{i:02}.png'))
    sheet=Image.new('RGB',(192*len(frames),224),'#53616d');draw=ImageDraw.Draw(sheet)
    for i,frame in enumerate(frames):
        sheet.paste(frame,(192*i,25),frame)
        phase=PHASES.get(action,[])
        label=phase[min(i,len(phase)-1)] if phase else 'comparison'
        draw.text((192*i+4,5),f'{direction} F{i} {label}',fill='white')
    sheet.save(folder/(direction+'-strip.png'))
    cols=4;guide=Image.new('RGB',(1280,320*((len(frames)+3)//4)),'#78848c')
    for i,frame in enumerate(frames):
        enlarged=frame.resize((320,320),Image.Resampling.NEAREST)
        guide.paste(enlarged,((i%cols)*320,(i//cols)*320),enlarged)
    guide.save(folder/(direction+'-pose-guide.png'))
    return {'action':action,'direction':direction,'actionId':index,'url':url,
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'decodedFrameSHA256':hashes,'frameCount':len(frames),
        'uniqueRenderedFrames':len(set(hashes)),'renderedDelaysMs':delays,
        'rawACTInspected':False,'classification':'RENDERED_REFERENCE',
        'confidence':{'poseSequence':'HIGH','anatomicalAnnotation':'MEDIUM','exactACTDelay':'UNKNOWN'},
        'canvas':[192,192],'rendererOrigin':[96,160], 'weaponView':2 if weapon else None}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('authoring/characters/private-ro-reference/RO_REFERENCE'))
    parser.add_argument('--metadata',type=Path,default=Path('authoring/characters/motion-templates/ro1-swordsman-male/rendered-reference.json'))
    args=parser.parse_args()
    tasks=[(action,family,d) for action,family in [('idle',0),('walk',8),('attack',80),('ready',32)] for d in DIRECTIONS]
    tasks += [('attack-40',40,'S'),('attack-88',88,'S'),('attack-96',96,'S')]
    with ThreadPoolExecutor(max_workers=2) as pool:
        records=list(pool.map(lambda t:capture(args.output,*t),tasks))
    for action in ['idle','walk','attack','ready']:
        rows=[r for r in records if r['action']==action]
        sheet=Image.new('RGB',(max(r['frameCount'] for r in rows)*192,224*8+30),'#344453')
        ImageDraw.Draw(sheet).text((6,6),'RO RESEARCH ONLY / '+action+' / RENDERED_REFERENCE',fill='white')
        for i,r in enumerate(rows):sheet.paste(Image.open(args.output/action/(r['direction']+'-strip.png')),(0,30+224*i))
        sheet.save(args.output/action/'eight-direction-contact-sheet.png')
        (args.output/action/'provenance-phases.json').write_text(json.dumps({'phaseLabels':PHASES.get(action,['ready']), 'labelAuthority':'Visual annotation, not ACT action phase names','records':rows},indent=2)+'\n')
    metadata={'referenceId':'RO1-SWORDMAN-MALE-RENDERED-2026-10-09','classification':'RENDERED_REFERENCE',
        'rawACTInspected':False,'renderSource':'https://assets.latam-tools.com.br',
        'rendererDocumentation':'https://github.com/adsonpleal/ragassets',
        'clientMappingRevision':'e4b5b53aa1f8b7e429bfa987ab321c96502ba1da',
        'attackMappingSources':[
            'https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/DB/Jobs/WeaponAction.js',
            'https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Renderer/Entity/EntityAction.js'],
        'selectedAttack':{'family':80,'weaponView':2,'reason':'Swordman SWORD maps to selector1, which resolves ATTACK2/group10; rendered overhead sweep matches the one-handed blade. Group40 is unarmed,88 is thrust,96 is skill in inspected client.'},
        'timingPolicy':'APNG presentation delays are observed renderer output; exact ACT intervals and original-client gameplay durations remain unknown.',
        'standingObservation':'Pinned straight-head output repeats one identical standing image; do not treat head orientation slices or duplicate frames as breathing keys.',
        'phaseLabels':PHASES,'records':records,
        'referenceImagery':'Ignored private-ro-reference/RO_REFERENCE; not runtime, not shipped, not committed'}
    args.metadata.parent.mkdir(parents=True,exist_ok=True)
    args.metadata.write_text(json.dumps(metadata,indent=2)+'\n')
    print('Captured',len(records),'rendered direction/variant sequences; private boards ready')

if __name__=='__main__':main()
