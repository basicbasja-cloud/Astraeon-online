"""Extract annotated ranged-weapon parts from complete same-frame paintings.

Visible-only masks; no generated limbs, no hidden-surface or pose approval.
Annotations use the recorded common paint-cell coordinate system.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_frame(master, annotation, transform):
    rgba = np.array(master.convert('RGBA'))
    visible = rgba[:, :, 3] > 0
    scale, offset = transform['scale'], np.array(transform['offset'])

    def xy(point):
        return tuple(np.array(point)*scale+offset)

    head = Image.new('L', master.size)
    ImageDraw.Draw(head).polygon([xy(p) for p in annotation['head_polygon']], fill=255)
    head = (np.array(head) > 0) & visible
    weapon = Image.new('L', master.size)
    draw = ImageDraw.Draw(weapon)
    for path in annotation['weapon_paths']:
        draw.line([xy(p) for p in path['points']], fill=255,
                  width=max(1, round(path['width']*scale)), joint='curve')
    for polygon in annotation.get('weapon_polygons', []):
        draw.polygon([xy(p) for p in polygon], fill=255)
    protect = Image.new('L', master.size)
    pd = ImageDraw.Draw(protect)
    for polygon in annotation.get('hand_polygons', []):
        pd.polygon([xy(p) for p in polygon], fill=255)
    hand = (np.array(protect) > 0) & visible & ~head
    weapon = (np.array(weapon) > 0) & visible & ~head & ~hand
    masks = {'HeadHair': head, 'Weapon': weapon,
             'BodyCostume': visible & ~head & ~weapon}
    parts = {}
    for role, mask in masks.items():
        pixels = rgba.copy()
        pixels[~mask] = 0
        parts[role] = Image.fromarray(pixels)
    merged = Image.new('RGBA', master.size)
    for role in ['BodyCostume', 'HeadHair', 'Weapon']:
        merged.alpha_composite(parts[role])
    actual = np.array(merged)
    if not np.array_equal(actual[visible], rgba[visible]) or not np.array_equal(actual[:, :, 3], rgba[:, :, 3]):
        raise ValueError('Same-frame pixel reconstruction changed')
    labels = np.zeros(visible.shape, np.uint8)
    for i, role in enumerate(['BodyCostume', 'HeadHair', 'Weapon'], 1):
        labels[masks[role]] = i
    return parts, Image.fromarray(labels), {
        'recomposition_mismatches': 0,
        'pixels_by_role': {r: int(m.sum()) for r, m in masks.items()},
        'required_part_empty': [r for r, m in masks.items() if not m.any()],
        'protected_hand_pixels': int(hand.sum()),
        'semantic_boundaries_approved': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['frames', 'annotations', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Choose a fresh visible-cutout proposal destination')
    data = json.loads(args.annotations.read_text())
    args.output.mkdir(parents=True)
    sheets = {r: Image.new('RGBA', (2048, 2048)) for r in ['BodyCostume', 'HeadHair', 'Weapon']}
    head_review = Image.new('RGB', (1200, 600), '#343a43')
    part_review = Image.new('RGB', (1200, 1200), '#343a43')
    records = []
    for item in data['frames']:
        i = item['index']
        source = args.frames/f'{i:03d}.png'
        master = Image.open(source).convert('RGBA')
        parts, labels, record = split_frame(master, item, data['cell_to_frame'])
        for role, image in parts.items():
            folder = args.output/role
            folder.mkdir(exist_ok=True)
            image.save(folder/f'{i:03d}.png')
            sheets[role].alpha_composite(image, ((i % 4)*512, (i//4)*512))
        folder = args.output/'Labels'
        folder.mkdir(exist_ok=True)
        labels.save(folder/f'{i:03d}.png')
        box = parts['HeadHair'].getbbox()
        if box:
            # Review-only crop, never an exported part placement transform.
            crop = parts['HeadHair'].crop((box[0]-3, box[1]-3, box[2]+3, box[3]+3))
            crop.thumbnail((140, 140))
            head_review.paste(crop, ((i % 8)*150, (i//8)*300+25), crop)
        review = Image.new('RGBA', master.size, '#343a43')
        review.alpha_composite(parts['BodyCostume'])
        review.alpha_composite(parts['Weapon'])
        review = review.crop((160, 90, 430, 410)).resize((270, 320))
        review.thumbnail((280, 280))
        part_review.paste(review, ((i % 4)*300, (i//4)*300+15), review)
        records.append({'index': i, 'source_sha256': sha(source), **record})
    for role, sheet in sheets.items():
        sheet.save(args.output/(role+'-sheet.png'))
    head_review.save(args.output/'head-boundaries.jpg', quality=97)
    part_review.save(args.output/'body-weapon-boundaries.jpg', quality=97)
    receipt = {'status': 'SAME_FRAME_VISIBLE_CUTOUT_PROPOSALS_REQUIRE_SEMANTIC_REVIEW',
               'frames': records, 'annotations_sha256': sha(args.annotations),
               'implementation_sha256': sha(Path(__file__)), 'painted_pixels_redrawn': False,
               'limb_templates_used': False, 'source_pose_registered': False,
               'hidden_surfaces_authored': False, 'runtime_admitted': False}
    (args.output/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    (args.output/'extractor-source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'frames': len(records), 'status': receipt['status']}))


if __name__ == '__main__':
    main()
