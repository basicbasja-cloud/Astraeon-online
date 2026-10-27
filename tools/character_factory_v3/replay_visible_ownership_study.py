"""Replay saved visible-ownership study labels, without pretending BodyRest is a costume.

This is a study format, never a runtime intake receipt. It preserves native
canvas coordinates, visible pixels, and explicit role names. No SAM2 is needed.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

SCHEMA = 'astraeon.visible-ownership-study.v1'
ALLOWED = {'BodyRest', 'HeadHair', 'Weapon', 'WeaponHandOccluder'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def split(master, labels, role_ids):
    pixels = np.asarray(master.convert('RGBA'))
    ids = np.asarray(labels)
    mapping = {int(k): role for k, role in role_ids.items()}
    if not mapping or len(set(mapping.values())) != len(mapping) or not set(mapping.values()) <= ALLOWED or 0 in mapping:
        raise ValueError('Invalid explicit study roles')
    if ids.shape != pixels.shape[:2] or ids.dtype != np.uint8 or np.any(~np.isin(ids, [0, *mapping])):
        raise ValueError('Invalid native ownership labels')
    visible = pixels[:, :, 3] > 0
    if np.any((ids == 0) & visible) or np.any((ids != 0) & ~visible):
        raise ValueError('Every visible master pixel must have exactly one owner')
    parts = {}
    for value, role in mapping.items():
        array = pixels.copy()
        array[ids != value] = 0
        parts[role] = Image.fromarray(array)
    merged = Image.new('RGBA', master.size)
    for part in parts.values():
        merged.alpha_composite(part)
    result = np.asarray(merged)
    if not np.array_equal(result[visible], pixels[visible]) or not np.array_equal(result[:, :, 3], pixels[:, :, 3]):
        raise ValueError('Visible recomposition changed')
    return parts


def replay(recipe_path, output):
    if output.exists():
        raise ValueError('Use a fresh replay destination')
    recipe_path = Path(recipe_path)
    recipe_hash = sha(recipe_path)
    data = json.loads(recipe_path.read_text())
    if data.get('schema') != SCHEMA or data.get('runtime_admitted') is not False:
        raise ValueError('Expected a non-runtime ownership study')
    rows = data['frames']
    if not rows or len({r['id'] for r in rows}) != len(rows):
        raise ValueError('Missing or duplicate study frame ids')
    # Validate every pinned input before writing any output.
    for row in rows:
        for name in ['master', 'labels']:
            if sha(row[name]) != row[name + '_sha256']:
                raise ValueError('Pinned study input changed: ' + row[name])
        if Path(row['id']).is_absolute() or '..' in Path(row['id']).parts:
            raise ValueError('Unsafe output frame id')
    output.mkdir(parents=True)
    checks = []
    for row in rows:
        with Image.open(row['master']) as master, Image.open(row['labels']) as labels:
            parts = split(master, labels, data['role_ids'])
        for role, part in parts.items():
            expected = row['part_rgba_sha256'][role]
            actual = hashlib.sha256(part.tobytes()).hexdigest()
            if actual != expected:
                raise ValueError('Replayed part RGBA changed: ' + row['id'] + '/' + role)
            path = output / row['id'] / (role + '.png')
            path.parent.mkdir(parents=True, exist_ok=True)
            part.save(path)
            checks.append({'id': row['id'], 'role': role, 'rgba_sha256': actual, 'matches_saved_part': True})
    if sha(recipe_path) != recipe_hash or any(sha(row[name]) != row[name + '_sha256'] for row in rows for name in ['master', 'labels']):
        raise ValueError('Study inputs changed during replay')
    result = {'status': 'EXACT_VISIBLE_STUDY_REPLAY_NOT_RUNTIME_ACCEPTANCE', 'frames': len(rows), 'role_checks': checks,
              'recipe_sha256': recipe_hash, 'implementation_sha256': sha(__file__), 'requires_sam2': False,
              'requires_image_generation': False, 'runtime_admitted': False, 'visual_approval_implied': False,
              'BodyRest_contains_unseparated_weapon': 'BodyRest' in data['role_ids'].values()}
    (output / 'replay-receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recipe', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = replay(args.recipe, args.output)
    print(json.dumps({'frames': result['frames'], 'exact_role_checks': len(result['role_checks']), 'runtime_admitted': False}))
