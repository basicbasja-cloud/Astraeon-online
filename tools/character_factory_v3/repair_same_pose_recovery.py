"""Reuse a proven identical source body pose with bounded arrow-removal paint.

Requires all source bone matrices to match, plus loaded/unloaded arrow states.
No body deformation or independently generated limbs. Semantic masks and other
frame transitions still require review; this is not general motion interpolation.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

from normalize_fixed_viewport_batch import normalize_batch


ROLES = ['BodyCostume', 'HeadHair', 'Weapon']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def equivalent_body_pose(first_source, last_source):
    if not first_source['bones'] or set(first_source['bones']) != set(last_source['bones']):
        raise ValueError('Source skeleton differs or is empty')
    errors = []
    for name in first_source['bones']:
        matrices = [np.asarray(row['bones'][name]['world_matrix'], dtype=float)
                    for row in [first_source, last_source]]
        if any(matrix.shape != (4, 4) or not np.isfinite(matrix).all() for matrix in matrices):
            raise ValueError('Invalid source bone matrix')
        errors.append(float(np.abs(matrices[0]-matrices[1]).max()))
    error = max(errors)
    if error > 1e-5:
        raise ValueError('Body poses differ; same-pose reuse is forbidden')
    return error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['registered', 'replay', 'correction', 'annotation', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Use a fresh recovery destination')
    replay = json.loads(args.replay.read_text())
    annotation = json.loads(args.annotation.read_text())
    first_index, last_index = annotation['source_pose_indices']
    first_source, last_source = [replay['frames'][i] for i in [first_index, last_index]]
    error = equivalent_body_pose(first_source, last_source)
    if not first_source['source_weapon_guide']['arrow_visible'] or last_source['source_weapon_guide']['arrow_visible']:
        raise ValueError('Expected a loaded first pose and unloaded recovery')
    placement = json.loads((args.registered/'receipt.json').read_text())
    translations = {row['index']: row['translation'] for row in placement['frames']}
    delta = translations[first_index]
    frames, normalization = normalize_batch(Image.open(args.correction), annotation['correction_recipe'])
    correction = Image.new('RGBA', (768, 768))
    correction.alpha_composite(frames[0], tuple(delta))
    mask = Image.new('L', (768, 768))
    coordinates = annotation['paint_cell_to_frame']
    polygon = [tuple(np.array(point)*coordinates['scale']+coordinates['offset']+np.array(delta))
               for point in annotation['arrow_repair_polygon']]
    ImageDraw.Draw(mask).polygon(polygon, fill=255)
    selected = np.array(mask) > 0
    original_parts = {role: np.array(Image.open(args.registered/role/f'{first_index:03d}.png').convert('RGBA'))
                      for role in ROLES}
    before = np.array(Image.open(args.registered/'Master'/f'{first_index:03d}.png').convert('RGBA'))
    background_seed = np.zeros(before.shape[:2], dtype=bool)
    for point in annotation.get('shared_background_seeds', []):
        x, y = np.rint(np.array(point)*coordinates['scale']+coordinates['offset']+np.array(delta)).astype(int)
        if before[y, x, :3].min() < 242 or not before[y, x, 3]:
            raise ValueError('Explicit air-gap seed does not identify opaque white background')
        background_seed[y, x] = True
    shared_background = ndimage.binary_propagation(background_seed,
        mask=(before[:, :, :3].min(2) >= 242) & (before[:, :, 3] > 0))
    if np.any(original_parts['HeadHair'][shared_background, 3]):
        raise ValueError('Air-gap cleanup would erase head pixels')
    before[shared_background] = 0
    for pixels in original_parts.values():
        pixels[shared_background] = 0
    after = before.copy()
    after[selected] = np.array(correction)[selected]
    if np.any(after[~selected] != before[~selected]):
        raise ValueError('Protected body pixels changed')
    if np.any(original_parts['HeadHair'][selected, 3]):
        raise ValueError('Arrow repair would touch the head; refine its bounds')
    owner = np.zeros(selected.shape, dtype=np.uint8)
    for label, role in enumerate(ROLES, 1):
        owner[original_parts[role][:, :, 3] > 0] = label
    # Exposed bow pixels are Weapon; existing glove pixels stay with BodyCostume.
    owner[selected & (owner == 0)] = 3
    repaired_parts = {}
    for label, role in enumerate(ROLES, 1):
        pixels = original_parts[role].copy()
        pixels[selected] = 0
        assigned = selected & (owner == label)
        pixels[assigned] = after[assigned]
        repaired_parts[role] = Image.fromarray(pixels)
    merged = Image.new('RGBA', (768, 768))
    for role in ROLES:
        merged.alpha_composite(repaired_parts[role])
    if merged.tobytes() != Image.fromarray(after).tobytes():
        raise ValueError('Recovery parts do not reconstruct')
    args.output.mkdir(parents=True)
    for role in ['Master', *ROLES]:
        (args.output/role).mkdir()
        for i in range(len(placement['frames'])):
            destination = args.output/role/f'{i:03d}.png'
            if i == last_index:
                image = Image.fromarray(after) if role == 'Master' else repaired_parts[role]
                image.save(destination)
            elif i == first_index:
                image = Image.fromarray(before) if role == 'Master' else Image.fromarray(original_parts[role])
                image.save(destination)
            else:
                destination.write_bytes((args.registered/role/f'{i:03d}.png').read_bytes())
    previews = []
    for i in range(len(placement['frames'])):
        im = Image.open(args.output/'Master'/f'{i:03d}.png').convert('RGBA')
        background = Image.new('RGBA', im.size, '#dbdbd8')
        background.alpha_composite(im)
        preview = background.crop((260, 250, 530, 600)).convert('RGB')
        ImageDraw.Draw(preview).text((5, 5), f'SE / {i:02d} / DRAFT', fill='black')
        previews.append(preview)
    for name, speed in [('normal', 1), ('slow', 3)]:
        previews[0].save(args.output/f'{name}.gif', save_all=True, append_images=previews[1:],
                         duration=[80*speed]*15+[240*speed], loop=0, disposal=2)
    mask.save(args.output/'bounded-arrow-repair-mask.png')
    sheets = {}
    (args.output/'Sheets').mkdir()
    for role in ['Master', *ROLES]:
        sheet = Image.new('RGBA', (3072, 3072))
        for i in range(16):
            image = Image.open(args.output/role/f'{i:03d}.png').convert('RGBA')
            sheet.paste(image, (i % 4*768, i//4*768))
        path = args.output/'Sheets'/f'{role}.png'
        sheet.save(path)
        sheets[role] = {'path': str(path.relative_to(args.output)), 'sha256': sha(path),
                        'columns': 4, 'rows': 4, 'frame_size': [768, 768], 'frame_count': 16}
    changed = np.any(before != after, axis=2)
    receipt = {'status': 'SOURCE_IDENTICAL_BODY_RECOVERY_REUSE_WITH_LOCAL_ARROW_REPAIR',
               'source_pose_indices': [first_index, last_index], 'bone_count': len(first_source['bones']),
               'maximum_source_bone_matrix_error': error,
               'changed_pixels_in_reused_first_pose': int(changed.sum()),
               'explicit_shared_background_pixels_removed': int(shared_background.sum()),
               'protected_pixel_changes': int(changed[~selected].sum()),
               'head_pixels_identical_to_first': repaired_parts['HeadHair'].tobytes() == Image.fromarray(original_parts['HeadHair']).tobytes(),
               'lower_body_pixels_identical_to_first': bool(np.array_equal(after[annotation['protected_lower_body_y']:], before[annotation['protected_lower_body_y']:])),
               'source_replay_sha256': sha(args.replay), 'correction_sha256': sha(args.correction),
               'registered_receipt_sha256': sha(args.registered/'receipt.json'),
               'annotations_sha256': sha(args.annotation), 'implementation_sha256': sha(Path(__file__)),
               'normalization': normalization, 'recomposition_mismatches': 0,
               'sprite_sheets': sheets,
               'semantic_cutouts_approved': False, 'all_frame_smoothness_approved': False,
               'runtime_admitted': False}
    if not receipt['lower_body_pixels_identical_to_first']:
        raise ValueError('Recovery changed protected lower body')
    (args.output/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    (args.output/'annotations-source.json').write_bytes(args.annotation.read_bytes())
    (args.output/'repair-source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({k: receipt[k] for k in ['changed_pixels_in_reused_first_pose', 'protected_pixel_changes', 'maximum_source_bone_matrix_error']}))


if __name__ == '__main__':
    main()
