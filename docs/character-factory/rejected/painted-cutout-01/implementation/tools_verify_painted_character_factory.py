"""Inspect real pilot PNG bytes, layer invariants, grip mask and repeated renders."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from painted_character_factory import SLOTS, read_spec


def pixels(path):
    with Image.open(path) as image:
        image.load()
        if image.mode!='RGBA' or image.size!=(320,320):
            raise ValueError(f'Wrong registered RGBA frame: {path}')
        return np.array(image)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder',type=Path,required=True)
    args=parser.parse_args()
    folder=args.folder.resolve()
    spec=read_spec(folder/'rig.json')
    report={'status':'STRUCTURAL_PILOT_CHECKS_PASS','visualApproval':'PENDING',
            'directions':['SE'],'registeredAttachments':len(spec['views']['SE']['attachments']),
            'sourceHashes':{k:v['sha256'] for k,v in spec['images'].items()},
            'checks':[],'motions':{},'limitations':spec['limits']}
    def check(condition,name,details=None):
        report['checks'].append({'check':name,'pass':bool(condition),'details':details})
        if not condition:
            report['status']='STRUCTURAL_PILOT_CHECKS_FAILED'
    total=0
    for action,clip in spec['motions'].items():
        uniques=[];composite_errors=[]
        for index in range(len(clip['durations'])):
            prefix=folder/'motion-pilot-02'/'default'/action/'SE'
            composite=pixels(prefix/'Composite'/f'{index:02}.png')
            uniques.append(hashlib.sha256(composite.tobytes()).hexdigest())
            layers={s:pixels(prefix/s/f'{index:02}.png') for s in SLOTS}
            for slot,rgba in layers.items():
                total+=1
                check(not np.any(rgba[[0,-1],:,3]) and not np.any(rgba[:,[0,-1],3]),
                      f'No crop at frame border: {action}/{index}/{slot}')
            overlap=((layers['Weapon'][:,:,3]>128)&(layers['Hands'][:,:,3]>128)).sum()
            check(overlap==0,f'Grip-covered weapon pixels omitted: {action}/{index}',int(overlap))
            for variant in ('training','steel'):
                variant_prefix=folder/'motion-pilot-02'/variant/action/'SE'
                stable=('BaseBody','BodyHands','Hair','BackAccessory','Hands')
                for slot in stable:
                    check(np.array_equal(layers[slot],pixels(variant_prefix/slot/f'{index:02}.png')),
                          f'Independent {slot}: {variant}/{action}/{index}')
                if variant=='training':
                    check(np.array_equal(layers['Outfit'],pixels(variant_prefix/'Outfit'/f'{index:02}.png')),
                          f'Sword swap keeps costume: {action}/{index}')
                if variant=='steel':
                    check(np.array_equal(layers['Weapon'],pixels(variant_prefix/'Weapon'/f'{index:02}.png')),
                          f'Chest swap keeps weapon: {action}/{index}')
            composed=Image.new('RGBA',(320,320))
            for slot in SLOTS:
                composed=Image.alpha_composite(composed,Image.fromarray(layers[slot]))
            array=np.array(composed)
            # Separate passes and a simultaneous ray render differ at filtered,
            # semitransparent edges. Report the measurement, never call it exact.
            diff=np.abs(array.astype(np.int16)-composite.astype(np.int16))
            foreground=(array[:,:,3]>32)|(composite[:,:,3]>32)
            composite_errors.append({'frame':index,'maxRGBAError':int(diff.max()),
                                     'meanForegroundRGBAError':float(diff[foreground].mean())})
        report['motions'][action]={'frames':len(clip['durations']),'uniqueCompositeRGBAFrames':len(set(uniques)),
                                  'compositionVsSimultaneousRayRender':composite_errors}
        check(len(set(uniques))>=3,f'{action} contains real changing poses')
        for variant in ('default','training','steel'):
            original=pixels(folder/'motion-pilot-02'/variant/action/'SE/Composite/00.png')
            repeated=pixels(folder/'repeatability'/variant/action/'SE/Composite/00.png')
            check(np.array_equal(original,repeated),f'Repeated decoded RGBA render: {variant}/{action}',
                  hashlib.sha256(original.tobytes()).hexdigest())
    default=folder/'fitting-02/default/Idle/SE'
    for variant in ('body-only','no-weapon','no-cape'):
        prefix=folder/'fitting-02'/variant/'Idle/SE'
        for slot in ('BaseBody','BodyHands'):
            check(np.array_equal(pixels(default/slot/'00.png'),pixels(prefix/slot/'00.png')),
                  f'Removing {variant} keeps independent {slot}')
    report['checkedDefaultLayerFrames']=total
    report['checksPassed']=sum(c['pass'] for c in report['checks'])
    report['checksTotal']=len(report['checks'])
    report['repeatabilityScope']='Decoded RGBA pixels; raw Blender PNG metadata contains variable render timing.'
    (folder/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','checksPassed','checksTotal','registeredAttachments','motions')},indent=2))
    if report['status'].endswith('FAILED'):
        raise SystemExit(1)


if __name__=='__main__':
    main()
