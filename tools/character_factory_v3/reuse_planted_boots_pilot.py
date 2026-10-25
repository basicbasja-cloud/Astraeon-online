"""Prototype reusable illustrated boots on a nearly planted casting stance.

One fixed pair of visible painted boot cutouts follows the captured foot joints
and projected toe angles. No whole-character fitting, scaling or synthesized
hidden anatomy. This bounded pilot is not a generic gait/death adapter.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def angle(landmarks, side):
    ankle = landmarks['Foot.' + side]
    toe = landmarks['Toe.' + side]
    return math.atan2(toe[1]-ankle[1], toe[0]-ankle[0])


def rigid_slot(image, source, target, radians):
    if max(abs(x-y) for x, y in zip(source, target)) < 1e-8 and abs(radians) < 1e-8:
        return image.copy()
    cosine, sine = math.cos(radians), math.sin(radians)
    # PIL wants output -> input mapping, the inverse of the socket transform.
    tx = source[0] - cosine * target[0] - sine * target[1]
    ty = source[1] + sine * target[0] - cosine * target[1]
    return image.convert('RGBa').transform(image.size, Image.Transform.AFFINE,
        (cosine, sine, tx, -sine, cosine, ty), Image.Resampling.BILINEAR).convert('RGBA')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--paint', type=Path, required=True)
    parser.add_argument('--guide', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Use a new pilot output')
    capture = json.loads((args.guide / 'pilot-receipt.json').read_text())
    if capture['weapon'] != 'staff':
        raise ValueError('This pilot is bounded to the planted caster stance')
    rows = capture['views']['NE']['frames']
    first = Image.open(args.paint / 'frames/000.png').convert('RGBA')
    if first.size != (1536, 1536) or len(rows) != 16:
        raise ValueError('Unexpected pilot canvas or timeline')
    original = np.array(first)
    templates = {}
    for side, left, right in [('L', 610, 800), ('R', 800, 980)]:
        pixels = np.zeros_like(original)
        pixels[985:, left:right] = original[985:, left:right]
        templates[side] = Image.fromarray(pixels)
    args.output.mkdir(parents=True)
    for side, im in templates.items():
        im.save(args.output / f'boot-{side}-source.png')
    records, preview = [], []
    for row in rows:
        index = row['index']
        source_path = args.paint / 'frames' / f'{index:03d}.png'
        master = Image.open(source_path).convert('RGBA')
        pixels = np.array(master)
        # Preserve all upper-body paint. The overlap begins inside the trouser
        # cuff, above the old boot silhouette, for a visible seam review.
        pixels[995:, 600:990] = 0
        body = Image.fromarray(pixels)
        boots = Image.new('RGBA', master.size)
        attachments = {}
        for side in ['L', 'R']:
            source = rows[0]['landmarks']['Foot.' + side]
            target = row['landmarks']['Foot.' + side]
            radians = math.atan2(math.sin(angle(row['landmarks'], side)-angle(rows[0]['landmarks'], side)),
                                 math.cos(angle(row['landmarks'], side)-angle(rows[0]['landmarks'], side)))
            travel = math.dist(source, target)
            if travel > 12 or abs(radians) > math.radians(6):
                raise ValueError('Foot motion exceeds the bounded visible boot-reuse pilot')
            boots.alpha_composite(rigid_slot(templates[side], source, target, radians))
            attachments[side] = {'source_socket': source, 'target_socket': target,
                                  'translation_px': travel, 'rotation_rad': radians, 'scale': 1}
        combined = Image.alpha_composite(body, boots)
        folder = args.output / 'frames'
        folder.mkdir(exist_ok=True)
        for role, im in [('Master', combined), ('UpperBody', body), ('Boots', boots)]:
            (folder / role).mkdir(exist_ok=True)
            im.save(folder / role / f'{index:03d}.png')
        bg = Image.new('RGBA', (768, 768), '#eee')
        bg.alpha_composite(combined.resize(bg.size, Image.Resampling.LANCZOS))
        preview.append(bg.convert('RGB'))
        records.append({'index': index, 'original_master_sha256': sha(source_path),
                        'attachments': attachments, 'per_frame_fitting': False})
    preview[0].save(args.output / 'normal.gif', save_all=True, append_images=preview[1:], duration=80, loop=0)
    receipt = {'status': 'VISIBLE_BOOT_REUSE_PILOT_SEAM_REVIEW_REQUIRED',
               'implementation_sha256': sha(__file__), 'guide_receipt_sha256': sha(args.guide / 'pilot-receipt.json'),
               'source_master_sha256': sha(args.paint / 'frames/000.png'), 'frames': records,
               'whole_body_transform': False, 'source_pose_changed': False,
               'hidden_anatomy_reconstructed': False, 'semantic_approval': False, 'runtime_admitted': False}
    (args.output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
