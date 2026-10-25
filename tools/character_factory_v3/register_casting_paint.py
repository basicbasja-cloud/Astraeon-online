"""Register NE caster illustrations using two boot parts and native foot motion.

Fixed scale. Match only the same illustrated anatomical parts; do not fit a
whole-character bounding box. Native ankle/toe controls preserve genuine pose
motion. Disagreeing feet or weak matches fail before producing registered art.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from reuse_planted_boots_pilot import angle, rigid_slot


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rgb(image):
    background = Image.new('RGBA', image.size, '#eeeeee')
    background.alpha_composite(image)
    return np.array(background.convert('RGB'))


def locate(image, template, expected_delta, radius=35):
    alpha = np.array(template.getchannel('A'))
    ys, xs = np.where(alpha>64)
    box = [int(xs.min())-5, int(ys.min())-5, int(xs.max())+6, int(ys.max())+6]
    patch = rgb(template.crop(box))
    foreground = (np.array(template.crop(box).getchannel('A'))>64).astype('uint8')
    mask = cv2.dilate(foreground, np.ones((9,9),'uint8'))*255
    expected = np.array(box[:2],float)+expected_delta
    origin = np.floor(expected-radius).astype(int)
    far = np.ceil(expected+np.array(patch.shape[1::-1])+radius).astype(int)
    if min(origin)<0 or far[0]>image.width or far[1]>image.height:
        raise ValueError('Boot search exceeds the fixed canvas')
    search = rgb(image.crop((*origin,*far)))
    scores = cv2.matchTemplate(search, patch, cv2.TM_SQDIFF_NORMED, mask=mask)
    if not np.isfinite(scores).all():
        raise ValueError('Nonfinite boot correspondence')
    error, _, point, _ = cv2.minMaxLoc(scores)
    observed = origin+np.array(point)
    correction = expected-observed
    return {'translation_correction':correction.tolist(),'similarity':float(1-error),
            'expected_part_origin':expected.tolist(),'observed_part_origin':observed.tolist()}


def build(paint,guide,aliases,output,diagnostic_only=False):
    if output.exists():
        raise ValueError('Choose a new registration output')
    capture = json.loads((guide/'pilot-receipt.json').read_text())
    rows = capture['views']['NE']['frames']
    alias = json.loads(aliases.read_text())['views']['NE']
    if len(rows)!=len(alias) or capture['weapon']!='staff':
        raise ValueError('Caster alias/capture layout differs')
    first = Image.open(paint/'000.png').convert('RGBA')
    if first.size!=(1536,1536):
        raise ValueError('Expected native illustration canvas')
    templates = {}
    a = np.array(first)
    for side,left,right in [('L',610,800),('R',800,980)]:
        part = np.zeros_like(a)
        part[985:,left:right] = a[985:,left:right]
        templates[side] = Image.fromarray(part)
    output.mkdir(parents=True)
    records = []
    for row,link in zip(rows,alias):
        index = row['index']
        source_index = link['same_visible_source_pose_as']
        if source_index!=index:
            source = rows[source_index]
            if row['landmarks']!=source['landmarks'] or row['grip_world']!=source['grip_world'] or row['staff_tip_world']!=source['staff_tip_world']:
                raise ValueError('Aliased native anatomy/prop controls differ')
            for frame in [index,source_index]:
                pixels = np.array(Image.open(guide/'NE'/f'{frame:03d}.png').convert('RGBA'))
                pixels[pixels[:,:,3]==0] = 0
                if hashlib.sha256(pixels.tobytes()).hexdigest()!=link['visible_rgba_sha256']:
                    raise ValueError('Aliased visible native pose changed')
        path = paint/f'{source_index:03d}.png'
        image = Image.open(path).convert('RGBA')
        matches = {}
        for side in ['L','R']:
            base = rows[0]['landmarks']['Foot.'+side]
            target = row['landmarks']['Foot.'+side]
            rotation = angle(row['landmarks'],side)-angle(rows[0]['landmarks'],side)
            rotation = math.atan2(math.sin(rotation),math.cos(rotation))
            template = rigid_slot(templates[side],base,base,rotation)
            matches[side] = locate(image,template,np.array(target)-base)
        delta = np.mean([m['translation_correction']for m in matches.values()],axis=0)
        disagreement = math.dist(matches['L']['translation_correction'],matches['R']['translation_correction'])
        accepted = bool(min(m['similarity']for m in matches.values())>=.75 and disagreement<=12 and max(abs(delta))<=35)
        records.append({'index':index,'source_index':source_index,'source_master_sha256':sha(path),
                        'boot_matches':matches,'draw_translation_native_px':delta.tolist(),
                        'two_foot_disagreement_native_px':disagreement,'registration_gate_passed':accepted})
    (output/'registration-diagnostic.json').write_text(json.dumps({'status':'ANATOMICAL_PART_CORRESPONDENCE_DIAGNOSTIC',
        'frames':records,'scale':1,'bounding_box_fit':False,'runtime_admitted':False},indent=2)+'\n')
    if diagnostic_only:
        return records
    if not all(r['registration_gate_passed']for r in records):
        raise ValueError('Anatomical registration needs manual review; diagnostic retained')
    for record in records:
        index,source_index = record['index'],record['source_index']
        image = Image.open(paint/f'{source_index:03d}.png').convert('RGBA')
        translated = rigid_slot(image,[0,0],record['draw_translation_native_px'],0)
        (output/'frames').mkdir(exist_ok=True)
        translated.save(output/'frames'/f'{index:03d}.png')
    (output/'renderer-source.py').write_bytes(Path(__file__).read_bytes())
    (output/'receipt.json').write_text(json.dumps({'status':'TWO_FOOT_TRANSLATION_REGISTERED_PAINT_REQUIRES_ART_REVIEW',
        'frames':records,'implementation_sha256':sha(__file__),'guide_receipt_sha256':sha(guide/'pilot-receipt.json'),
        'scale':1,'bounding_box_fit':False,'native_pose_changed':False,'runtime_admitted':False},indent=2)+'\n')
    return records


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['paint','guide','aliases','output']:
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--diagnostic-only',action='store_true')
    args=parser.parse_args()
    result=build(args.paint,args.guide,args.aliases,args.output,args.diagnostic_only)
    print(json.dumps({'poses':len(result),'passed':sum(r['registration_gate_passed']for r in result),
                      'maximum_two_foot_disagreement_px':max(r['two_foot_disagreement_native_px']for r in result)}))
