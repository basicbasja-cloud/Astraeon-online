"""Package exact visible pilot cutouts at one fixed authoring resolution.

Uniform resampling is shared by every frame. Final master RGBA is assigned to
one visible owner per pixel, so separate PNGs recompose exactly after resizing.
This does not register a character or approve hidden surfaces and equipment swaps.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

ROLES = ['BodyCostume', 'HeadHair', 'Weapon', 'WeaponHandOccluder']
DIRECTIONS = ['S','SW','W','NW','N','NE','E','SE']


def resolve_direction(receipt, requested=None):
    recorded = receipt.get('direction')
    if recorded is not None and recorded not in DIRECTIONS:
        raise ValueError('Invalid recorded camera direction')
    if requested is not None and requested not in DIRECTIONS:
        raise ValueError('Invalid requested camera direction')
    if recorded is not None and requested is not None and recorded != requested:
        raise ValueError('Requested direction differs from captured source')
    return recorded or requested or 'NE'


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


def validate_native_loop(source,receipt):
    """Admit only the reproducible small-motion template loop certificate.

    Half-open native cycles need not duplicate the initial pose at the end.
    Their seam must remain smaller than ordinary source-driven motion.
    """
    if (receipt.get('status')!='BOUNDED_NATIVE_HOLD_REUSE_NOT_ADMITTED'
        or receipt.get('one_illustrated_template') is not True
        or receipt.get('per_frame_generation') is not False
        or receipt.get('whole_character_bbox_fit') is not False):
        raise ValueError('A bounded native-loop reuse receipt is required')
    if sha(source/'renderer-source.py')!=receipt['implementation_sha256']:
        raise ValueError('Native loop implementation snapshot changed')
    if not receipt.get('input_sha256'):
        raise ValueError('Native loop has no frozen inputs')
    for path,digest in receipt['input_sha256'].items():
        if sha(path)!=digest:
            raise ValueError('Native loop input changed')
    evidence = receipt['loop_evidence']
    seam,adjacent = [evidence[key] for key in ['field_seam_max_px','largest_adjacent_field_change_px']]
    if (evidence.get('checked') is not True or evidence.get('native_source_loop') is not True
        or not all(math.isfinite(v) and v>=0 for v in [seam,adjacent]) or seam>1.25*adjacent+1e-6):
        raise ValueError('Native loop seam is unverified')
    for row in receipt['frames']:
        deformation = row['deformation']
        flow,low,high,error = [deformation[k] for k in ['maximum_inverse_displacement_px','minimum_jacobian',
                                                       'maximum_jacobian','maximum_control_interpolation_error_px']]
        staff = row['maximum_staff_axis_inverse_error_px']
        if (not all(math.isfinite(v) for v in [flow,low,high,error,staff]) or not 0<=flow<=32
            or not .75<=low<=high<=1.35 or not 0<=error<=.75 or not 0<=staff<=.75):
            raise ValueError('Native loop deformation exceeds bounded reuse')
        for role in ROLES:
            if sha(source/role/f"{row['index']:03d}.png")!=row['part_sha256'][role]:
                raise ValueError('Native loop part changed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['source', 'masters', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--frame-size', type=int, default=768)
    parser.add_argument('--action', default='CastRelease')
    parser.add_argument('--direction', choices=DIRECTIONS, help='Must agree with the captured source direction')
    loops = parser.add_mutually_exclusive_group()
    loops.add_argument('--loop', action='store_true', help='Requires exactly matching first and last visible poses')
    loops.add_argument('--native-loop', action='store_true', help='Requires a frozen bounded-native-hold reuse certificate')
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Choose a new pilot package')
    receipt = json.loads((args.source/'receipt.json').read_text())
    direction = resolve_direction(receipt,args.direction)
    count = len(receipt['frames'])
    if not count or [r['index'] for r in receipt['frames']] != list(range(count)):
        raise ValueError('Expected a nonempty dense ordered pose sequence')
    if not 16 <= args.frame_size <= 768:
        raise ValueError('Frame size must be between 16 and 768; pages cannot exceed 3072 pixels')
    if args.native_loop:
        validate_native_loop(args.source,receipt)
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
    is_loop = args.loop or args.native_loop
    gif_name = 'cycle-loop.gif' if is_loop else 'castrelease-once.gif'
    gif_options = {'loop':0} if is_loop else {}
    preview[0].save(args.output/gif_name, save_all=True, append_images=preview[1:], duration=80, **gif_options)
    result = {'status': 'EXACT_VISIBLE_PILOT_PACKAGE_NOT_REGISTERED_CHARACTER',
              'direction': direction, 'action': args.action, 'loop': is_loop,
              'loop_policy': 'bounded-native-cycle' if args.native_loop else ('identical-endpoints' if args.loop else 'once'),
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
