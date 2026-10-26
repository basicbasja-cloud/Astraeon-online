"""Correct recovery on complete masters before cutting any semantic parts.

Only source-identical body poses can reuse a painted master. A local generated
patch may remove the arrow inside explicit source-cell bounds. No per-limb
assembly, body fitting, or inferred in-between poses are permitted.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from normalize_fixed_viewport_batch import normalize_batch
from repair_same_pose_recovery import equivalent_body_pose


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Preserve previous complete-master repairs')
    plan = json.loads(args.plan.read_text())
    replay_path = Path(plan['source_replay'])
    replay = json.loads(replay_path.read_text())
    first, last = plan['source_pose_indices']
    error = equivalent_body_pose(replay['frames'][first], replay['frames'][last])
    if not replay['frames'][first]['source_weapon_guide']['arrow_visible'] or replay['frames'][last]['source_weapon_guide']['arrow_visible']:
        raise ValueError('Expected loaded first pose and unloaded recovery')
    args.output.mkdir(parents=True)
    records = []
    for row in plan['rows']:
        source = Path(row['masters'])
        correction_path = Path(row['correction'])
        source_image = Image.open(source/f'{first:03d}.png').convert('RGBA')
        if source_image.size != (512, 512):
            raise ValueError('Expected the recorded 512-pixel native paint canvas')
        recipe = {'grid': [1, 1], 'source_size': [512, 512],
                  'viewport': row['correction_viewport'], 'source_pose_indices': [first]}
        corrections, normalization = normalize_batch(Image.open(correction_path), recipe)
        mask = Image.new('L', source_image.size)
        transform = plan['paint_cell_to_frame']
        ImageDraw.Draw(mask).polygon([tuple(np.array(point)*transform['scale']+transform['offset'])
                                      for point in row['arrow_repair_polygon']], fill=255)
        selected = np.array(mask) > 0
        original = np.array(source_image)
        repaired = original.copy()
        repaired[selected] = np.array(corrections[0])[selected]
        changed = np.any(original != repaired, axis=2)
        if changed[~selected].any():
            raise ValueError('Protected master pixels changed')
        if changed[plan['protected_lower_body_y']:].any():
            raise ValueError('Projectile repair touches the protected lower body')
        folder = args.output/row['sex']/row['view']/'Master'
        folder.mkdir(parents=True)
        inputs = []
        for i in range(plan['frames']):
            source_path = source/f'{i:03d}.png'
            destination = folder/source_path.name
            if i == last:
                Image.fromarray(repaired).save(destination)
            else:
                destination.write_bytes(source_path.read_bytes())
            inputs.append({'index': i, 'input_sha256': sha(source_path),
                           'output_sha256': sha(destination), 'reused_painted_pose': first if i == last else None})
        mask.save(folder.parent/'bounded-arrow-repair-mask.png')
        record = {'sex': row['sex'], 'view': row['view'], 'inputs': inputs,
                  'correction_sha256': sha(correction_path), 'normalization': normalization,
                  'source_bone_matrix_error': error,
                  'changed_pixels_relative_to_reused_pose': int(changed.sum()),
                  'protected_pixel_changes': 0, 'lower_body_endpoint_identical': True,
                  'same_frame_semantic_cutouts_available': False,
                  'intermediate_pose_joins_approved': False, 'runtime_admitted': False}
        (folder.parent/'receipt.json').write_text(json.dumps(record, indent=2)+'\n')
        records.append(record)
    report = {'status': 'COMPLETE_MASTER_RECOVERY_REPAIR_NOT_FULL_ANIMATION_ACCEPTANCE',
              'source_replay_sha256': sha(replay_path), 'plan_sha256': sha(args.plan),
              'implementation_sha256': sha(Path(__file__)), 'source_pose_indices': [first, last],
              'source_bones_compared': len(replay['frames'][first]['bones']),
              'source_matrix_error': error, 'records': records,
              'source_body_deformation': False, 'runtime_admitted': False}
    (args.output/'receipt.json').write_text(json.dumps(report, indent=2)+'\n')
    (args.output/'plan-source.json').write_bytes(args.plan.read_bytes())
    (args.output/'repair-source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'groups': len(records), 'frames': plan['frames']*len(records),
                      'source_matrix_error': error, 'protected_pixel_changes': 0}))


if __name__ == '__main__':
    main()
