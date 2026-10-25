"""Package exact visible pilot cutouts at one fixed authoring resolution.

Uniform resampling is shared by every frame. Final master RGBA is assigned to
one visible owner per pixel, so separate PNGs recompose exactly after resizing.
This does not register a character or approve hidden surfaces and equipment swaps.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROLES = ['BodyCostume', 'HeadHair', 'Weapon', 'WeaponHandOccluder']


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalize(master, parts, size):
    check = Image.new('RGBA', master.size)
    for part in parts:
        check.alpha_composite(part)
    if check.tobytes() != master.tobytes():
        raise ValueError('Native visible cuts do not reconstruct master')
    target = master.resize((size, size), Image.Resampling.LANCZOS)
    values = np.array(target)
    values[values[:, :, 3]==0] = 0
    target = Image.fromarray(values)
    scores = np.stack([np.array(part.getchannel('A').resize((size, size), Image.Resampling.LANCZOS)) for part in parts])
    owner = scores.argmax(axis=0)
    result = []
    for index in range(len(parts)):
        pixels = np.zeros_like(values)
        pixels[owner==index] = values[owner==index]
        result.append(Image.fromarray(pixels))
    check = Image.new('RGBA', target.size)
    for part in result:
        check.alpha_composite(part)
    if check.tobytes() != target.tobytes():
        raise ValueError('Authoring cuts do not reconstruct resized master')
    return target, result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['source', 'masters', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Choose a new pilot package')
    receipt = json.loads((args.source/'receipt.json').read_text())
    if len(receipt['frames']) != 16:
        raise ValueError('Expected the complete sixteen-pose NE pilot')
    args.output.mkdir(parents=True)
    names = ['Master', *ROLES, 'WeaponLightBack', 'WeaponLightFront']
    sheets = {role: Image.new('RGBA', (3072, 3072)) for role in names}
    preview, records = [], []
    for row in receipt['frames']:
        index = row['index']
        master_path = args.masters/f'{index:03d}.png'
        if sha(master_path) != row['master_sha256']:
            raise ValueError('Registered proposal master changed')
        master = Image.open(master_path).convert('RGBA')
        parts = [Image.open(args.source/role/f'{index:03d}.png').convert('RGBA') for role in ROLES]
        master, cuts = normalize(master, parts, 768)
        images = dict(zip(ROLES, cuts))
        images['Master'] = master
        for role in ['WeaponLightBack', 'WeaponLightFront']:
            images[role] = Image.new('RGBA', master.size)
        paths = {}
        for role, im in images.items():
            folder = args.output/role
            folder.mkdir(exist_ok=True)
            path = folder/f'{index:03d}.png'
            im.save(path)
            sheets[role].alpha_composite(im, ((index%4)*768, (index//4)*768))
            paths[role] = {'path': str(path.relative_to(args.output)), 'sha256': sha(path)}
        bg = Image.new('RGBA', master.size, '#eee')
        bg.alpha_composite(master)
        preview.append(bg.convert('RGB'))
        records.append({'index': index, 'root': [384, 550.4], 'duration_ms': 80,
                        'files': paths, 'recomposition_changed_pixels': 0})
    for role, sheet in sheets.items():
        sheet.save(args.output/(role+'-sheet.png'))
    # CastRelease is a one-shot excerpt. Do not manufacture a looping seam by
    # jumping from the lowered hand back to a raised casting hand.
    preview[0].save(args.output/'castrelease-once.gif', save_all=True, append_images=preview[1:], duration=80)
    result = {'status': 'EXACT_VISIBLE_PILOT_PACKAGE_NOT_REGISTERED_CHARACTER',
              'direction': 'NE', 'action': 'CastRelease', 'loop': False,
              'source_receipt_sha256': sha(args.source/'receipt.json'),
              'implementation_sha256': sha(__file__), 'canvas': [768, 768],
              'sheet_grid': [4, 4], 'sheet_size': [3072, 3072], 'frames': records,
              'whole_character_fit_per_frame': False, 'hidden_anatomy_authored': False,
              'effect_layers_authored': False, 'owner_approved': False,
              'runtime_admitted': False, 'full_character_complete': False}
    (args.output/'package.json').write_text(json.dumps(result, indent=2)+'\n')
    (args.output/'renderer-source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'poses': 16, 'separate_sheets': 6, 'master_sheet': 1,
                      'recomposition_changed_pixels': 0, 'runtime_admitted': False}))


if __name__ == '__main__':
    main()
