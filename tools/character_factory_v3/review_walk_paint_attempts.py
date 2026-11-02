"""Expose source-control and preservation failures of retained paint experiments.

Visible blade-tip estimates are manual review annotations with uncertainty.
They are not painted sole contacts, a contact pass, or automatic art approval.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from review_swordsman_walk_locked_guides import ROOT, KEYS, canonical_cells, panel, flat

BASE = ROOT / 'authoring/characters/factory-v3/patch-0.0.1/painted-candidates'
ORIGINAL = BASE / 'swordsman-male-walk-sw-keyposes-20261102/generated-sheet.png'
MARKED = BASE / 'swordsman-walk-4keys-marked-20261102/generated-sheet.png'
SINGLE = BASE / 'swordsman-walk-sw12-single-20261102/generated-sheet.png'
WEAPON = BASE / 'swordsman-walk-4keys-weapon-edit-20261102/generated-sheet.png'
# Manually inspected visible blade core endpoints in the fifth raw output.
# This intentionally does not pretend antialiased outermost pixels are exact.
TIPS = ((439, 225), (1064, 267), (389, 980), (1040, 993))
UNCERTAINTY = 3.0


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(guide_folder, output):
    if output.exists() or output.is_symlink():
        raise ValueError('Choose a fresh output')
    manifest_path = guide_folder / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    records = manifest['views']['SW']['frames']
    guides = []
    for index in KEYS:
        with Image.open(guide_folder / 'SW' / f'{index:03}.png') as source:
            guides.append(source.convert('RGBA').resize((768, 768), Image.Resampling.LANCZOS))
    output.mkdir(parents=True)
    for name, path in (('marked-key', MARKED), ('weapon-edit-key', WEAPON)):
        paintings, _ = canonical_cells(path, 2)
        for index, guide, painting in zip(KEYS, guides, paintings):
            panel(guide, painting, records[index], name.upper() + ' / NOT APPROVED').save(output / f'{name}-{index:02}.png')
    with Image.open(SINGLE) as source:
        if source.size != (1254, 1254) or source.mode != 'RGBA':
            raise ValueError('Unexpected single-frame result')
        crop = source.convert('RGBa').resize((320, 320), Image.Resampling.BICUBIC).convert('RGBA')
    single = Image.new('RGBA', (768, 768))
    single.paste(crop, (224, 288))
    panel(guides[3], single, records[12], 'SINGLE EDIT / NOT APPROVED').save(output / 'single-edit-12.png')
    with Image.open(ORIGINAL) as source:
        before = np.asarray(source.convert('RGBA'))
    with Image.open(WEAPON) as source:
        after = np.asarray(source.convert('RGBA'))
    if before.shape != after.shape or before.shape != (1254, 1254, 4):
        raise ValueError('The edit changed the whole-sheet canvas')
    visible = (before[:, :, 3] > 0) | (after[:, :, 3] > 0)
    changed = np.any(before != after, axis=2) & visible
    # Deliberately generous review windows, not final semantic/underpaint masks.
    windows = ((275, 190, 475, 400), (875, 230, 1100, 400),
               (200, 940, 460, 1020), (835, 945, 1120, 1030))
    allowed = np.zeros(changed.shape, dtype=bool)
    for x0, y0, x1, y1 in windows:
        allowed[y0:y1, x0:x1] = True
    mask = np.zeros_like(before)
    mask[changed & allowed] = [30, 150, 255, 255]
    mask[changed & ~allowed] = [255, 40, 70, 255]
    Image.fromarray(mask).save(output / 'weapon-edit-change-map.png')
    estimates = []
    with Image.open(WEAPON) as raw:
        backdrop = flat(raw.convert('RGBA'), '#777777')
    board = Image.new('RGB', (1536, 360), '#eeeeee')
    draw = ImageDraw.Draw(board)
    scale_to_runtime = 348 / 627 * 0.3125
    for n, (index, observed) in enumerate(zip(KEYS, TIPS)):
        sx, sy = records[index]['weapon_guide']['tip']
        target = (n % 2 * 627 + (sx - 420) * 627 / 696,
                  n // 2 * 627 + (sy - 520) * 627 / 696)
        distance = math.dist(target, observed)
        estimates.append({'source_index': index, 'source_tip_on_raw_sheet': list(target),
                          'painted_visible_core_tip_estimate': list(observed),
                          'manual_uncertainty_radius_raw_px': UNCERTAINTY,
                          'endpoint_distance_runtime_px': distance * scale_to_runtime,
                          'uncertainty_interval_runtime_px': [max(0, distance - UNCERTAINTY) * scale_to_runtime,
                                                              (distance + UNCERTAINTY) * scale_to_runtime],
                          'approved': False})
        left, top = math.floor(target[0]) - 48, math.floor(target[1]) - 40
        tile = backdrop.crop((left, top, left + 96, top + 80)).resize((384, 320), Image.Resampling.NEAREST)
        mark = ImageDraw.Draw(tile)
        for point, color in ((target, '#ff008a'), (observed, '#00ffff')):
            x, y = (point[0] - left) * 4, (point[1] - top) * 4
            mark.ellipse((x - 8, y - 8, x + 8, y + 8), outline=color, width=2)
        board.paste(tile, (n * 384, 40))
        draw.text((n * 384 + 5, 6), f'SW/{index:02} pink source / cyan manual core tip', fill='black')
        draw.text((n * 384 + 5, 22), f'estimate {distance * scale_to_runtime:.2f} runtime px; NOT foot contact', fill='black')
    board.save(output / 'weapon-tip-target-comparison.png')
    receipt = {
        'status': 'PAINT_CONTROLS_UNRESOLVED_NO_PRODUCTION_ADMISSION',
        'implementation_sha256': sha(Path(__file__)),
        'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in (ORIGINAL, MARKED, SINGLE, WEAPON)},
        'source_manifest_sha256': sha(manifest_path),
        'manual_tip_annotation_basis': 'Visible core endpoints inspected in nearest-neighbor native-pixel crops; antialiased outer tips have a 3px uncertainty radius.',
        'tip_estimates': estimates,
        'weapon_edit_review_windows_raw_px': windows,
        'visible_rgba_pixel_changes_outside_generous_weapon_windows': int((changed & ~allowed).sum()),
        'single_edit_applied_to_original_master': False,
        'key12_ankle_correction': 'Earlier lateral-boot diagnosis is withdrawn: the prominent right-side feature is a knee/shin, and the ankle is occluded. Neither a large ankle error nor a <=1px contact pass is certified.',
        'source_manipulated_to_pass': False, 'limbs_warped_or_frozen': False,
        'runtime_admitted': False, 'accepted_actions_added': 0,
        'limitations': [
            'Weapon endpoint estimates demonstrate guide mismatch; the plan\'s <=1 runtime pixel sole-contact gate is a separate criterion and is not scored here.',
            'A local-mask compositor could protect outside pixels, but it cannot repair the remaining pose or endpoint error inside the edit region.',
            'No failed image is segmented or expanded into other views/actions.',
        ],
    }
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guide-folder', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.guide_folder, args.output)
    print(json.dumps({'status': result['status'], 'outside_changes': result['visible_rgba_pixel_changes_outside_generous_weapon_windows'],
                      'tip_estimates_runtime_px': [round(r['endpoint_distance_runtime_px'], 2) for r in result['tip_estimates']]}))
