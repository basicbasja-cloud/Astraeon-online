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
    parser.add_argument('--frame-size', type=int, default=768)
    parser.add_argument('--action', default='CastRelease')
    parser.add_argument('--loop', action='store_true', help='Requires exactly matching first and last visible poses')
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Choose a new pilot package')
    receipt = json.loads((args.source/'receipt.json').read_text())
    count = len(receipt['frames'])
    if not count or [r['index'] for r in receipt['frames']] != list(range(count)):
        raise ValueError('Expected a nonempty dense ordered pose sequence')
    if not 16 <= args.frame_size <= 768:
        raise ValueError('Frame size must be between 16 and 768; pages cannot exceed 3072 pixels')
    if args.loop:
        first = Image.open(args.masters/'000.png').convert('RGBA')
        last = Image.open(args.masters/f'{count-1:03d}.png').convert('RGBA')
        if first.size != last.size or first.tobytes() != last.tobytes():
            raise ValueError('Loop endpoints differ; do not conceal a visible seam')
        for role in ROLES:
            first_part = Image.open(args.source/role/'000.png').convert('RGBA')
            last_part = Image.open(args.source/role/f'{count-1:03d}.png').convert('RGBA')
            if first_part.size != last_part.size or first_part.tobytes() != last_part.tobytes():
                raise ValueError('Loop part ownership differs: '+role)
    args.output.mkdir(parents=True)
    names = ['Master', *ROLES, 'WeaponLightBack', 'WeaponLightFront']
    size = args.frame_size
    page_count = (count+15)//16
    sheets = {role: [Image.new('RGBA', (4*size, 4*size)) for _ in range(page_count)] for role in names}
    preview, records = [], []
    for row in receipt['frames']:
        index = row['index']
        master_path = args.masters/f'{index:03d}.png'
        if sha(master_path) != row['master_sha256']:
            raise ValueError('Registered proposal master changed')
        master = Image.open(master_path).convert('RGBA')
        parts = [Image.open(args.source/role/f'{index:03d}.png').convert('RGBA') for role in ROLES]
        master, cuts = normalize(master, parts, size)
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
            sheets[role][index//16].alpha_composite(im, ((index%4)*size, ((index%16)//4)*size))
            paths[role] = {'path': str(path.relative_to(args.output)), 'sha256': sha(path)}
        bg = Image.new('RGBA', master.size, '#eee')
        bg.alpha_composite(master)
        preview.append(bg.convert('RGB'))
        records.append({'index': index, 'root': [size/2, size*(550.4/768)], 'duration_ms': 80,
                        'sheet_page': index//16, 'sheet_box':[(index%4)*size, ((index%16)//4)*size, size, size],
                        'files': paths, 'recomposition_changed_pixels': 0})
    pages = {}
    for role, role_pages in sheets.items():
        pages[role] = []
        for page, sheet in enumerate(role_pages):
            filename = role+'-sheet.png' if page_count == 1 else f'{role}-sheet-{page:03d}.png'
            path = args.output/filename
            sheet.save(path)
            pages[role].append({'page':page,'path':filename,'sha256':sha(path)})
    # CastRelease is a one-shot excerpt. Do not manufacture a looping seam by
    # jumping from the lowered hand back to a raised casting hand.
    gif_name = 'cycle-loop.gif' if args.loop else 'castrelease-once.gif'
    gif_options = {'loop':0} if args.loop else {}
    preview[0].save(args.output/gif_name, save_all=True, append_images=preview[1:], duration=80, **gif_options)
    result = {'status': 'EXACT_VISIBLE_PILOT_PACKAGE_NOT_REGISTERED_CHARACTER',
              'direction': 'NE', 'action': args.action, 'loop': args.loop,
              'source_receipt_sha256': sha(args.source/'receipt.json'),
              'implementation_sha256': sha(__file__), 'canvas': [size, size],
              'sheet_grid': [4, 4], 'sheet_size': [4*size, 4*size], 'pages':pages, 'frames': records,
              'whole_character_fit_per_frame': False, 'hidden_anatomy_authored': False,
              'effect_layers_authored': False, 'owner_approved': False,
              'runtime_admitted': False, 'full_character_complete': False}
    (args.output/'package.json').write_text(json.dumps(result, indent=2)+'\n')
    (args.output/'renderer-source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'poses': count, 'separate_sheets': 6*page_count, 'master_sheet': page_count,
                      'recomposition_changed_pixels': 0, 'runtime_admitted': False}))


if __name__ == '__main__':
    main()
