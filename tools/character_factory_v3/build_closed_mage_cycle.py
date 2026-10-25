"""Capture a real closed Mage casting cycle before producing looping art.

Keeps all original 24 Enter/Shoot/Exit samples, adding four explicit joint-space
frames from Idle_A and four back to Idle_A. This is isolated research, not a
replacement or an admission of an existing patch job.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def finish_cycle(output):
    skeleton = output/'source-skeleton.json'
    target = output/'canonical-guide'
    donor = json.loads(skeleton.read_text())
    first, last = donor['frames'][0], donor['frames'][-1]
    world_error = max(abs(x-y) for name in first['bones']
                      for a, b in zip(first['bones'][name]['world_matrix'], last['bones'][name]['world_matrix'])
                      for x, y in zip(a, b))
    if world_error > 2e-6:
        raise ValueError('Native endpoints are not the same Idle_A pose')
    capture = json.loads((target/'pilot-receipt.json').read_text())
    checks = []
    for direction, view in capture['views'].items():
        a, b = view['frames'][0], view['frames'][-1]
        projected_error = max(abs(x-y) for name in a['landmarks'] for x, y in zip(a['landmarks'][name], b['landmarks'][name]))
        left = np.array(Image.open(target/direction/'000.png').convert('RGBA'))
        right = np.array(Image.open(target/direction/'031.png').convert('RGBA'))
        left[left[:, :, 3]==0] = 0
        right[right[:, :, 3]==0] = 0
        pixels = int(np.any(left!=right, axis=2).sum())
        if projected_error > .001:
            raise ValueError('Canonical endpoints move by more than numeric precision')
        checks.append({'direction': direction, 'maximum_endpoint_landmark_error_native_px': projected_error,
                       'visible_endpoint_changed_pixels': pixels})
    report = {'status': 'CLOSED_NATIVE_CYCLE_GEOMETRY_CHECKED_NOT_FINAL_ART',
              'original_action_samples_retained': 24, 'entry_transition_frames': 4,
              'exit_transition_frames': 4, 'frames': 32,
              'native_endpoint_world_matrix_error': world_error,
              'views': checks, 'runtime_admitted': False, 'painted_loop_approved': False}
    (output/'seam-report.json').write_text(json.dumps(report, indent=2)+'\n')
    (output/'progress.json').write_text(json.dumps({'stage': 'complete-research-capture', 'complete': True, 'runtime_admitted': False}, indent=2)+'\n')
    (output/'renderer-source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(report), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--finish-only', action='store_true', help='Verify an already completed capture without rendering again')
    parser.add_argument('--source-blender', default='/usr/bin/blender')
    parser.add_argument('--target-blender', default='/workspace/.tools/blender-5.2.2-linux-x64/blender')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    tools = root/'tools/character_factory_v3'
    base = root/'authoring/characters/factory-v3/patch-0.0.1'
    output = args.output.resolve()
    if args.finish_only:
        if not output.is_dir():
            raise ValueError('Completed capture directory is missing')
        job = json.loads((output/'job.json').read_text())
        source_capture = json.loads((output/'source-guide/manifest.json').read_text())
        if job.get('closed_cycle_profile') != 1 or job != source_capture['job']:
            raise ValueError('Closed-cycle capture lineage differs')
        subprocess.run([sys.executable, str(tools/'verify_canonical_pilot.py'), '--pilot', str(output/'canonical-guide'), '--skeleton', str(output/'source-skeleton.json'), '--rig', str(root/'authoring/characters/factory-v3/rigs/astraeon_humanoid_male_v1.blend'), '--output', str(output/'validation.json')], cwd=root, check=True)
        finish_cycle(output)
        return
    if output.exists():
        raise ValueError('Choose a new cycle capture')
    output.mkdir(parents=True)
    job = json.loads((base/'guide-jobs/ebac492fbc20b608880c.json').read_text())
    if job['frames'] != 24 or job.get('entry_transition') or job.get('exit_transition'):
        raise ValueError('Original Mage action layout differs')
    job.update({'frames': 32, 'entry_transition': {'frames': 4, 'action': 'Idle_A', 'source_frame': 0},
                'exit_transition': {'frames': 4, 'action': 'Idle_A', 'source_frame': 0},
                'uses': ['Research/MageClosedCastingCycle'], 'closed_cycle_profile': 1,
                'cycle_implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    job['id'] = digest({key: value for key, value in job.items() if key != 'id'})[:20]
    job_path = output/'job.json'
    job_path.write_text(json.dumps(job, indent=2)+'\n')
    source = output/'source-guide'
    skeleton = output/'source-skeleton.json'
    target = output/'canonical-guide'

    def run(stage, command):
        (output/'progress.json').write_text(json.dumps({'stage': stage, 'complete': False}, indent=2)+'\n')
        print('CLOSED_MAGE_CYCLE_STAGE', stage, flush=True)
        subprocess.run(command, cwd=root, check=True)

    run('native-source-capture', [args.source_blender, '-b', '-noaudio', '--python', str(tools/'render_frozen_patch001_guides.py'), '--', '--job', str(job_path), '--output', str(source)])
    run('checked-source-skeleton-export', [args.source_blender, '-b', '-noaudio', '--python', str(tools/'export_evaluated_guide_skeleton.py'), '--', '--source-guide', str(source), '--direction', 'NE', '--output', str(skeleton)])
    rig = root/'authoring/characters/factory-v3/rigs/astraeon_humanoid_male_v1.blend'
    run('canonical-rig-capture', [args.target_blender, '-b', '-noaudio', '--python', str(tools/'render_canonical_rig_pilot.py'), '--', '--skeleton', str(skeleton), '--rig', str(rig), '--output', str(target)])
    run('capture-verification', [sys.executable, str(tools/'verify_canonical_pilot.py'), '--pilot', str(target), '--skeleton', str(skeleton), '--rig', str(rig), '--output', str(output/'validation.json')])
    finish_cycle(output)



if __name__ == '__main__':
    main()
