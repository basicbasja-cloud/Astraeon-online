"""Verify separate canonical-rig pilot evidence without approving final art."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify(pilot, skeleton, rig):
    capture = json.loads((pilot / 'pilot-receipt.json').read_text())
    source = json.loads(skeleton.read_text())
    if capture['status'] != 'CANONICAL_RIG_RETARGET_PILOT_GUIDE_NOT_FINAL_ART':
        raise ValueError('Not a canonical pilot capture')
    if capture['source_skeleton_sha256'] != sha(skeleton) or capture['rig_sha256'] != sha(rig):
        raise ValueError('Capture input changed')
    if capture['implementation_sha256'] != sha(pilot / 'renderer-source.py'):
        raise ValueError('Missing exact pilot implementation snapshot')
    if source['implementation_sha256'] != sha(skeleton.with_suffix('.renderer.py')):
        raise ValueError('Missing exact source replay implementation snapshot')
    if sha(source['source_file']) != source['source_sha256']:
        raise ValueError('Original motion changed')
    if capture['old_actions_used'] or capture['source_modified'] or capture['runtime_admitted']:
        raise ValueError('Unexpected pilot admission or source mutation')
    reference = next(iter(capture['views'].values()))['frames']
    errors, floors, world_errors, images = [], [], [], []
    for direction, view in capture['views'].items():
        if len(view['frames']) != len(source['frames']):
            raise ValueError('Incomplete native pose sequence')
        for row, original, expected in zip(view['frames'], source['frames'], reference):
            if (row['source_action'], row['source_frame']) != (original['action'], original['source_frame']):
                raise ValueError('Source action/sample changed')
            path = pilot / direction / f"{row['index']:03d}.png"
            if sha(path) != row['image_sha256']:
                raise ValueError('Captured pilot pixels changed')
            alpha = np.array(Image.open(path).getchannel('A'))
            if not alpha.any() or any(x.any() for x in [alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1]]):
                raise ValueError('Empty or clipped pilot image')
            errors.append(row['maximum_world_rotation_error_rad'])
            floors.append(abs(row['corrected_floor_m']))
            keys = ['grip_world', 'staff_tip_world']
            if capture['weapon'] == 'bow':
                keys += ['bow_grip_world', 'string_nock_world']
                visible = original.get('source_weapon_guide', {}).get('arrow_visible')
                if visible is None or row['arrow_visible'] != visible:
                    raise ValueError('Bow arrow release visibility differs from native guide')
            world_errors += [abs(x-y) for key in keys for x, y in zip(row[key], expected[key])]
            images.append(str(path))
    if max(errors) > 1e-3 or max(floors) > 2e-5 or max(world_errors) > 1e-6:
        raise ValueError('Canonical pilot transfer/contact/cross-view geometry differs')
    return {'status': 'PILOT_GEOMETRY_AND_CAPTURE_CHECKED_NOT_ART_ACCEPTANCE',
            'captured_images': len(images), 'mapped_bones': len(capture['bone_map']),
            'maximum_world_rotation_error_rad': max(errors),
            'maximum_floor_error_m': max(floors),
            'maximum_cross_view_prop_world_error_m': max(world_errors),
            'source_and_rig_unchanged': True, 'exact_implementation_snapshots': True,
            'paint_alignment_approved': False, 'anatomy_approved': False,
            'owner_approved': False, 'runtime_admitted': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', type=Path, required=True)
    parser.add_argument('--skeleton', type=Path, required=True)
    parser.add_argument('--rig', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.pilot, args.skeleton, args.rig)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
