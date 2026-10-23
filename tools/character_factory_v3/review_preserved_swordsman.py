"""Preserve the earlier illustrated Swordsman; propose bounded edge cleanup.

No generation, animation deformation, pose translation or source overwrite.
The three original visible ownership masks are reapplied to the cleaned master.
This is an art-review workspace, not patch coverage or runtime admission.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from normalize_fixed_viewport_batch import unmatte_white_edges
from build_fixed_grid_sequence_review import gif

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT/'authoring/characters/factory-v3/configs/layered_action_catalog.json'
CORE = ['BodyCostume', 'HeadHair', 'Weapon']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_frame(master, parts):
    original = np.array(master.convert('RGBA'))
    composed = Image.new('RGBA', master.size)
    masks = {}
    ownership = np.zeros(original.shape[:2], dtype=np.uint8)
    for role in CORE:
        array = np.array(parts[role].convert('RGBA'))
        mask = array[:, :, 3] > 0
        if np.any(ownership[mask]):
            raise ValueError('Baseline core layers overlap; inspect before edge cleanup')
        ownership[mask] += 1
        masks[role] = mask
        composed.alpha_composite(parts[role])
    actual = np.array(composed)
    visible = original[:, :, 3] > 0
    if not np.array_equal(actual[:, :, 3], original[:, :, 3]) or not np.array_equal(actual[visible], original[visible]):
        raise ValueError('Baseline parts do not reconstruct the preserved master')
    cleaned, count = unmatte_white_edges(original, ~visible)
    changed = np.any(cleaned != original, axis=2)
    from scipy.ndimage import distance_transform_edt
    band = distance_transform_edt(visible) <= 2
    if np.any(changed & ~band):
        raise ValueError('Edge cleanup changed protected interior pixels')
    result = {}
    for role, mask in masks.items():
        array = cleaned.copy(); array[~mask] = 0
        result[role] = Image.fromarray(array)
    recomposed = Image.new('RGBA', master.size)
    for role in CORE:
        recomposed.alpha_composite(result[role])
    if recomposed.tobytes() != Image.fromarray(cleaned).tobytes():
        raise ValueError('Cleaned cutouts changed same-frame recomposition')
    return Image.fromarray(cleaned), result, {'edge_pixels_unmatted': count,
                                             'protected_interior_pixel_changes': 0,
                                             'recomposition_mismatch_pixels': 0}


def build(output):
    if output.exists():
        raise ValueError('Choose a fresh output; preserve earlier review results')
    catalog = json.loads(CATALOG.read_text())
    output.mkdir(parents=True)
    baseline = {}; actions = []
    for name, action in catalog['actions'].items():
        source = ROOT/action['directory']; target = output/name
        target.mkdir()
        timing = json.loads((source/'assembly-audit.json').read_text())['durations_ms']
        views = []
        for direction in catalog['directions']:
            before_frames = []; after_frames = []; comparisons = []; rows = []
            for i in range(action['poses_per_direction']):
                master_path = source/direction/'Master'/f'{i:03d}.png'
                paths = {r: source/direction/r/f'{i:03d}.png' for r in CORE}
                master = Image.open(master_path).convert('RGBA')
                parts = {r: Image.open(p).convert('RGBA') for r,p in paths.items()}
                cleaned, cutouts, record = clean_frame(master, parts)
                for role, image in {'Master': cleaned, **cutouts}.items():
                    folder = target/direction/role; folder.mkdir(parents=True, exist_ok=True)
                    image.save(folder/f'{i:03d}.png')
                for path in [master_path, *paths.values()]:
                    baseline[str(path.relative_to(ROOT))] = sha(path)
                # FX are retained byte-for-byte; not regenerated or re-timed.
                for role in ['WeaponLightBack', 'WeaponLightFront', 'WeaponHandOccluder']:
                    path = source/direction/role/f'{i:03d}.png'
                    if path.exists(): baseline[str(path.relative_to(ROOT))] = sha(path)
                before_frames.append(master); after_frames.append(cleaned)
                canvas = Image.new('RGBA', (1024, 544), '#252a34')
                canvas.alpha_composite(master, (0,32)); canvas.alpha_composite(cleaned, (512,32))
                draw = ImageDraw.Draw(canvas)
                draw.text((12,10), f'{name} {direction}/{i:02d} PRESERVED ORIGINAL', fill='white')
                draw.text((524,10), 'EDGE CLEANUP PROPOSAL - SAME POSE/PIXEL POSITIONS', fill='white')
                comparisons.append(canvas)
                rows.append({'index': i, **record})
            gif(comparisons, target/f'{direction}-before-after-slow.gif', [t*3 for t in timing])
            gif(after_frames, target/f'{direction}-cleaned-normal.gif', timing)
            # Core-only sheet: FX/hand overlays remain independent retained sources.
            for role in ['Master', *CORE]:
                sheet = Image.new('RGBA', (2048,2048))
                for i in range(16):
                    sheet.alpha_composite(Image.open(target/direction/role/f'{i:03d}.png'), ((i%4)*512,(i//4)*512))
                sheet.save(target/f'{direction}-{role}-sheet.png')
            views.append({'direction': direction, 'frames': rows})
        actions.append({'action': name, 'views': views, 'source_directory': action['directory'],
                        'durations_ms_unchanged': timing, 'trail_source_unchanged': True})
    for relative, digest in baseline.items():
        if sha(ROOT/relative) != digest: raise ValueError('Preserved source changed while processing')
    receipt = {'status': 'PRESERVED_SWORDSMAN_BASELINE_AND_EDGE_CLEANUP_PROPOSAL',
               'owner_direction': 'Earlier Swordsman is visually okay; retain that work as the baseline.',
               'baseline_scope': 'Both earlier BasicAttack and SkillOverhead retained; no blanket approval of every cutout/motion/runtime gate.',
               'baseline_files': baseline, 'actions': actions, 'source_art_overwritten': False,
               'pose_scale_translation_or_warp': False, 'semantic_boundary_approved': False,
               'runtime_admitted': False, 'patch_coverage_increment': 0,
               'limitations': ['White-edge recovery estimates foreground color from nearby opaque paint; inspect bright blade highlights.',
                              'Original semantic ownership is retained, not certified by recomposition.',
                              'The old action camera and timeline are not silently relabeled as current patch guide jobs.',
                              'New masters and three core cutouts only; existing hand and FX layers remain separate unchanged references.']}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    r = build(a.output)
    print(json.dumps({'output': str(a.output), 'preserved_files': len(r['baseline_files']),
                      'reviewed_poses': sum(len(v['frames']) for a in r['actions'] for v in a['views']),
                      'runtime_admitted': False}))
