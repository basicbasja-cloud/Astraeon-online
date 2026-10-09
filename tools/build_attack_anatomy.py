#!/usr/bin/env python3
"""Integrate ImageGen arm art into immutable, registered source body cells.

Only authored limb masks are replaced. Head identity, root, timeline and pixels
outside those masks are protected. The raw generated sheets remain provenance.
"""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'authoring/characters/builds/swordsman-basicattack-anatomy-v1'
SOURCE = ROOT / 'authoring/characters/appearance/swordsman-bodywithoutfit/appearance-pack.json'
SCALE = 0.45

def arm_mask(points, width=25):
    mask = Image.new('L', (320, 320))
    draw = ImageDraw.Draw(mask)
    draw.line([tuple(p) for p in points], fill=255, width=width, joint='curve')
    for x, y in points:
        radius = width / 2
        draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=255)
    return mask

def replace_arm(body, raw, annotation, head_mask):
    # Discard the generated head before normalization. Its largest connected
    # skin silhouette is identity context only; no face pixels are admitted.
    arr = np.asarray(raw).copy()
    skin = ((arr[:, :, 0] > 125) & (arr[:, :, 1] > 65) &
            (arr[:, :, 2] > 50) & (arr[:, :, 0] > arr[:, :, 1]*1.18) &
            (arr[:, :, 1] > arr[:, :, 2]*1.04) &
            (arr[:, :, 2] > arr[:, :, 0]*.45) & (arr[:, :, 3] > 180))
    skin[315:] = False
    labels, count = ndimage.label(ndimage.binary_closing(skin, iterations=1))
    if 'generatedHeadPolygon' in annotation:
        # Warm ivory cloth can touch the skin seed. A reviewed skull contour
        # keeps that sleeve intact instead of treating it as generated face.
        head = Image.new('L', raw.size)
        if annotation['generatedHeadPolygon']:
            ImageDraw.Draw(head).polygon([tuple(p) for p in annotation['generatedHeadPolygon']], fill=255)
        arr[np.asarray(head) > 0] = 0
    elif count:
        sizes = np.bincount(labels.ravel()); sizes[0] = 0
        context_head = ndimage.binary_dilation(ndimage.binary_fill_holes(labels == sizes.argmax()), iterations=2)
        arr[context_head] = 0
    raw = Image.fromarray(arr)
    raw_points = annotation['generatedJoints']
    shoulder = annotation['shoulder']
    angle = annotation.get('armRotation', 0)
    c, s = math.cos(angle), math.sin(angle)
    a, b, d, e = c/SCALE, s/SCALE, -s/SCALE, c/SCALE
    matrix = (a, b, raw_points[0][0]-a*shoulder[0]-b*shoulder[1],
              d, e, raw_points[0][1]-d*shoulder[0]-e*shoulder[1])
    shift = [shoulder[0]-SCALE*(c*raw_points[0][0]-s*raw_points[0][1]),
             shoulder[1]-SCALE*(s*raw_points[0][0]+c*raw_points[0][1])]
    normalized = raw.transform((320, 320), Image.Transform.AFFINE,
                               matrix,
                               resample=Image.Resampling.BICUBIC)
    points = [[round(SCALE*(c*p[0]-s*p[1])+shift[0], 2),
               round(SCALE*(s*p[0]+c*p[1])+shift[1], 2)] for p in raw_points]
    new_mask = arm_mask(points, annotation.get('width', 27))
    old_mask = arm_mask(annotation['originalJoints'], annotation.get('oldWidth', 27))
    for chain in annotation.get('extraEraseChains', []):
        extra = arm_mask(chain, annotation.get('oldWidth', 27))
        old_mask = Image.fromarray(np.maximum(np.asarray(old_mask), np.asarray(extra)))
    if 'oldEraseMaxY' in annotation:
        bounded = np.asarray(old_mask).copy()
        bounded[annotation['oldEraseMaxY']+1:] = 0
        old_mask = Image.fromarray(bounded)
    mask = Image.fromarray(np.maximum(np.asarray(new_mask), np.asarray(old_mask)))
    # Never admit a generated face or costume redesign outside the arm area.
    mask_array = np.asarray(mask).copy()
    mask_array[np.asarray(head_mask) > 0] = 0
    mask = Image.fromarray(mask_array)
    if annotation.get('exclude'):
        for polygon in annotation['exclude']:
            ImageDraw.Draw(mask).polygon([tuple(p) for p in polygon], fill=0)
    # A narrow seam, wholly inside the mask, preserves all exterior bytes.
    soft = mask.filter(ImageFilter.GaussianBlur(.65))
    soft = Image.fromarray(np.minimum(np.asarray(soft), np.asarray(mask)))
    arr = np.asarray(normalized).copy()
    arr[:, :, 3][arr[:, :, 3] >= 250] = 255
    normalized = Image.fromarray(arr)
    if annotation.get('isolatedArm'):
        # An unoccluded limb cutout supplies the missing upper arm. Remove
        # only the old limb above the protected collar, then paint the new
        # arm over its shoulder. Empty cutout margin cannot erase the torso.
        old_array = np.asarray(old_mask).copy()
        new_array = np.asarray(new_mask).copy()
        protected = np.asarray(head_mask) > 0
        old_array[protected] = 0
        new_array[protected] = 0
        old_soft = Image.fromarray(old_array).filter(ImageFilter.GaussianBlur(.65))
        old_soft = Image.fromarray(np.minimum(np.asarray(old_soft), old_array))
        base = Image.composite(Image.new('RGBA', body.size), body, old_soft)
        new_soft = Image.fromarray(new_array).filter(ImageFilter.GaussianBlur(.65))
        new_soft = np.minimum(np.asarray(new_soft), new_array)
        patch = np.asarray(normalized).copy()
        patch[:, :, 3] = (patch[:, :, 3].astype(float)*new_soft/255).round().astype('uint8')
        result = Image.alpha_composite(base, Image.fromarray(patch))
    else:
        result = Image.composite(normalized, body, soft)
    # Keep transparent RGB canonical. This is normalization, not pose drawing.
    arr = np.asarray(result).copy(); arr[arr[:, :, 3] == 0] = 0
    return Image.fromarray(arr), mask, points, shift

def run():
    pack = json.loads(SOURCE.read_text())
    atlas = Image.open(ROOT / pack['atlases']['body-basicattack']['file']).convert('RGBA')
    head_atlas = Image.open(ROOT / pack['atlases']['head-basicattack']['file']).convert('RGBA')
    heads = {}
    for direction in pack['bodyContract']['directions']:
        for i, frame in enumerate(pack['parts']['swordsman-head']['timelines']['BasicAttack'][direction]['frames']):
            ref = frame['layers']['HeadBase']; x, y, w, h = ref['rect']
            mask = Image.new('L', (320, 320))
            mask.paste(head_atlas.crop((x, y, x+w, y+h)).getchannel('A'), tuple(ref['trim']['offset']))
            heads[direction, i] = mask
    specs = json.loads((BUILD / 'arm-art-edits.json').read_text())
    out = BUILD / 'candidate'; out.mkdir(exist_ok=True)
    receipts = []
    for direction, entries in specs.items():
        row = pack['bodyContract']['directions'].index(direction)
        for entry in entries:
            i = entry['frame']; x = i * 320; y = row * 320
            before = atlas.crop((x, y, x+320, y+320))
            sheet = Image.open(BUILD / entry['sheet']).convert('RGBA')
            slot = entry['slot']; sx = slot % 3 * 512; sy = slot // 3 * 512
            raw = sheet.crop((sx, sy, sx+512, sy+512))
            after, mask, joints, shift = replace_arm(before, raw, entry, heads[direction, i])
            after.save(out / f'{direction}-{i:02}.png')
            mask.save(out / f'{direction}-{i:02}-mask.png')
            receipts.append(dict(direction=direction, frame=i, joints=joints, shift=shift,
                                 sourceRGBA=hashlib.sha256(before.tobytes()).hexdigest(),
                                 repairedRGBA=hashlib.sha256(after.tobytes()).hexdigest(),
                                 maskPixels=int(np.count_nonzero(np.asarray(mask)))))
            atlas.paste(after, (x, y))
    atlas.save(out / 'body-basicattack.png')
    (out / 'normalization-receipt.json').write_text(json.dumps(dict(sharedGeneratedScale=SCALE, frames=receipts), indent=2)+'\n')
    print('Normalized', len(receipts), 'authored arm masks')

if __name__ == '__main__':
    run()
