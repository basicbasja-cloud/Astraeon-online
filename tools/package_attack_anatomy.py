#!/usr/bin/env python3
"""Package the sealed arm paintings, then register the hands to owned swords.

The previous appearance pack and all MotionTemplate bytes remain immutable.
Joint annotations are explicitly review estimates, never gameplay authority.
"""
import copy
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from build_swordsman_registration import relative, tr

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'authoring/characters/builds/swordsman-basicattack-anatomy-v1'
ASSETS = ROOT / 'assets/characters/swordsman-basicattack-anatomy-v1'
OLD = ROOT / 'authoring/characters/appearance/swordsman-bodywithoutfit/appearance-pack.json'
OUT = ROOT / 'authoring/characters/appearance/swordsman-basicattack-anatomy/appearance-pack.json'
MOTION = ROOT / 'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json'


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    ASSETS.mkdir(parents=True, exist_ok=True)
    old = read(OLD)
    pack = copy.deepcopy(old)
    motion = read(MOTION)
    specs = read(BUILD / 'arm-art-edits.json')
    receipt = read(BUILD / 'candidate/normalization-receipt.json')
    edits = {(e['direction'], e['frame']): e for e in receipt['frames']}
    source_receipt = read(ROOT / 'authoring/characters/builds/swordsman-registration-v1/salvage-receipt.json')
    original_pose = {(e['direction'], e['frame']): e for e in source_receipt['frames'] if e['action'] == 'BasicAttack'}
    overrides = read(ROOT / 'authoring/characters/builds/swordsman-registration-v1/socket-overrides.json')
    pack.update(packId='swordsman-basicattack-anatomy-v1', status='REQUIRES_OWNER_VISUAL_REVIEW')
    pack['source'].update(method='Surgical ImageGen arm paintings integrated through authored limb masks; owned sword grip opening', baselineCommit='e0886e419212586161cd778d53e665a170a8f181')

    before = np.asarray(Image.open(ROOT / old['atlases']['body-basicattack']['file']).convert('RGBA'))
    after = np.asarray(Image.open(BUILD / 'candidate/body-basicattack.png').convert('RGBA'))
    Image.fromarray(after).save(ASSETS / 'body-basicattack.png')
    royal = np.asarray(Image.open(ROOT / old['atlases']['royal-basicattack']['file']).convert('RGBA')).copy()
    # Identical anatomical painting and alpha for costume B. Preserve its old
    # non-arm pixels and the original independent-head boundary colour.
    for row, direction in enumerate(old['bodyContract']['directions']):
        for index in range(16):
            if (direction, index) not in edits:
                continue
            y, x = row * 320, index * 320
            candidate = after[y:y+320, x:x+320].copy()
            changed = np.any(candidate != before[y:y+320, x:x+320], axis=2)
            warm = ((candidate[:, :, 0] > candidate[:, :, 2]*1.4) &
                    (candidate[:, :, 1] > candidate[:, :, 2]*1.25) &
                    (candidate[:, :, 0] > 95) & (candidate[:, :, 3] > 0))
            l, top, right, bottom = original_pose[direction, index]['headRect']
            warm[top:bottom, l:right] = False
            candidate[:, :, 0][warm] = (candidate[:, :, 0][warm]*.43).astype('uint8')
            candidate[:, :, 1][warm] = (candidate[:, :, 1][warm]*.88).astype('uint8')
            candidate[:, :, 2][warm] = np.minimum(255, candidate[:, :, 2][warm]*1.8+55).astype('uint8')
            royal[y:y+320, x:x+320][changed] = candidate[changed]
    Image.fromarray(royal).save(ASSETS / 'royal-basicattack.png')
    for atlas in ['body-basicattack', 'royal-basicattack']:
        pack['atlases'][atlas]['file'] = (ASSETS / (atlas+'.png')).relative_to(ROOT).as_posix()

    weapon_receipts = []
    for weapon in ['weapon-a', 'weapon-b']:
        im = Image.open(ROOT / old['atlases'][weapon]['file']).convert('RGBA')
        pixels = np.asarray(im).copy()
        mask = Image.new('L', im.size)
        draw = ImageDraw.Draw(mask)
        for row in range(8):
            # A literal hand opening in our own hilt; guard, blade and pommel
            # remain untouched. Independent body fingers still draw above it.
            draw.ellipse((20, row*128+92.5, 28, row*128+103.5), fill=255)
        pixels[np.asarray(mask) > 0] = 0
        atlas = weapon+'-attack-grip'
        path = ASSETS / (atlas+'.png')
        Image.fromarray(pixels).save(path)
        pack['atlases'][atlas] = dict(file=path.relative_to(ROOT).as_posix(), width=im.width, height=im.height)
        mask.save(BUILD / (weapon+'-grip-opening-mask.png'))
        weapon_receipts.append(dict(weapon=weapon, sourceSHA256=sha(ROOT / old['atlases'][weapon]['file']), outputSHA256=sha(path), pivot=[24, 98], opening='ellipse x20..28, y92.5..103.5 in each 48x128 source cell; owned pixels only'))
        for direction, seq in pack['parts'][weapon]['timelines']['BasicAttack'].items():
            for phase in seq['phases']:
                phase['layers']['MainHand']['atlasId'] = atlas
                phase['layers']['MainHand']['handOpening'] = 'body-owned palm/fingers; transparent hilt opening'
            ready = copy.deepcopy(seq['phases'][0])
            durations = old['bodyContract']['timeline']['BasicAttack'][direction]
            ready.update(at=sum(durations[:15])/sum(durations), name='readyReturn')
            ready['layers']['MainHand']['weaponPhase'] = 'readyReturn'
            seq['phases'].append(ready)

    joints = {}
    hand_receipts = []
    for row, direction in enumerate(old['bodyContract']['directions']):
        sequence = motion['actions']['BasicAttack']['directions'][direction]['frames']
        annotations = {e['frame']: e['originalJoints'] for e in specs[direction]}
        # For untouched poses these are 2D review estimates, including joints
        # hidden by skull/torso. Do not infer a 3D bone length from this overlay.
        keys = sorted(annotations)
        joints[direction] = []
        previous_angles = [overrides['BasicAttack/'+direction][str(i)]['weaponRotation'] for i in range(16)]
        ready_angle = previous_angles[0]
        recovery_angle = previous_angles[13]
        delta = (ready_angle-recovery_angle+math.pi) % (2*math.pi)-math.pi
        for index, frame in enumerate(sequence):
            ov = overrides['BasicAttack/'+direction][str(index)]
            grip = ov['mainHand']
            angle = previous_angles[index]
            if (direction, index) in edits:
                chain = edits[direction, index]['joints']
                grip = chain[3]
                confidence = 'painted arm landmarks manually annotated; hidden joints estimated'
            else:
                lo = max([k for k in keys if k <= index], default=keys[0])
                hi = min([k for k in keys if k >= index], default=keys[-1])
                t = 0 if lo == hi else (index-lo)/(hi-lo)
                chain = [[round((1-t)*a+t*b, 2) for a, b in zip(pa, pb)] for pa, pb in zip(annotations[lo], annotations[hi])]
                chain[3] = grip
                confidence = 'untouched source: approximate 2D review chain; occluded elbow/wrist may be interpolated'
            if direction == 'E' and index == 13:
                grip = [151, 191]  # actual painted palm, source socket was on cloth
                chain[3] = grip
            if index >= 14:
                angle = recovery_angle + delta*((index-13)/2)
            joints[direction].append(dict(frame=index, phase=frame.get('referencePhase', frame['role']), reauthored=(direction, index) in edits, joints=chain, confidence=confidence))
            registration = pack['bodyContract']['anchorRegistration']['BasicAttack'][direction][index]
            for name in ['mainHand', 'fxOrigin']:
                registration[name] = relative(frame['anchors'][name], tr(*grip, angle))
            selected = max((e for e in pack['parts']['weapon-a']['timelines']['BasicAttack'][direction]['phases'] if e['at'] <= sum(f['durationMs'] for f in sequence[:index])/450+1e-9), key=lambda e:e['at'])['layers']['MainHand']
            dx, dy = (selected['bladeTip'][j]-selected['pivot'][j] for j in [0, 1])
            tip = [grip[0]+math.cos(angle)*dx-math.sin(angle)*dy, grip[1]+math.sin(angle)*dx+math.cos(angle)*dy]
            registration['weaponTip'] = relative(frame['anchors']['weaponTip'], tr(*tip))
            polygon = [[round(grip[0]+5*math.cos(k*math.pi/4), 3), round(grip[1]+5*math.sin(k*math.pi/4), 3)] for k in range(8)]
            for body in ['swordsman-body-default', 'swordsman-body-royal-proof']:
                ref = pack['parts'][body]['timelines']['BasicAttack'][direction]['frames'][index]['layers']['Body']
                ref['foregroundPasses'] = [dict(afterLayer=layer, requiresLayer='MainHand', semantic='painted fingers over transparent weapon grip opening', polygon=polygon) for layer in ['MainHand', 'HairFront', 'HeadgearTop']]
            hand_receipts.append(dict(direction=direction, frame=index, grip=grip, rotation=round(angle, 7), repairedBody=(direction, index) in edits))
    write(OUT, pack)
    write(BUILD / 'joint-review.json', dict(status='REVIEW_ONLY_NOT_GAMEPLAY_AUTHORITY', coordinateSpace='canonical 320x320 canvas', note='2D projected landmarks; occlusion and interpolation are review estimates, not anatomy certification', frames=joints))
    write(BUILD / 'packaging-receipt.json', dict(baselineCommit='e0886e419212586161cd778d53e665a170a8f181', baselineAppearanceSHA256=sha(OLD), motionTemplateSHA256=sha(MOTION), motionTemplateChanged=False, sourceFrames=128, reauthoredFrames=len(edits), unchangedBodyFrames=128-len(edits), headRedrawn=False, sharedGeneratedScale=receipt['sharedGeneratedScale'], runtimeAtlases={k:sha(ROOT/v['file']) for k, v in pack['atlases'].items()}, weapons=weapon_receipts, hands=hand_receipts, ownerVisualApproval='PENDING'))
    print('Packaged 55 arm paintings, 73 retained poses, two owned sword grip openings; MotionTemplate unchanged')


if __name__ == '__main__':
    run()
