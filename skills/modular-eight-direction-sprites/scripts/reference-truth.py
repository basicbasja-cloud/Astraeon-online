"""Verify captured evidence and locked-key experiments without certifying art.

The capture receipt is immutable input. Observations, reconstructed joints and
authored inbetweens cannot be promoted to recovered game skeletons. This gate
checks provenance/timeline contracts, not whether a drawing is anatomically true.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bound_file(entry, root):
    path = root / entry['path']
    if sha(path) != entry['sha256']:
        raise ValueError('Changed bound evidence: ' + entry['path'])
    return path


def positive(value):
    return isinstance(value, (float, int)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


def audit(spec, root):
    root = Path(root)
    capture_path = bound_file(spec['capture'], root)
    capture = json.loads(capture_path.read_text())
    expected = capture['frames']
    if not expected or len(spec['observed_frames']) != len(expected):
        raise ValueError('Missing captured exposures')
    if spec['source_kind'] not in ('community_rendered_game', 'native_script_atlas', 'developer_gif', 'gameplay_video'):
        raise ValueError('Undeclared source kind')
    for frame, original in zip(spec['observed_frames'], expected):
        path = bound_file(frame, root)
        if path.resolve() != (capture_path.parent / original['file']).resolve():
            raise ValueError('Captured frame path/order changed')
        if frame['sha256'] != original['sha256'] or frame['index'] != original['index']:
            raise ValueError('Captured frame hash/order changed')
        if frame['time_ms'] != original['time_ms'] or frame['duration_ms'] != original['duration_ms']:
            raise ValueError('Captured clock changed')
        with Image.open(path) as image:
            if list(image.size) != capture['canvas']:
                raise ValueError('Changed source canvas')
    if spec.get('recovered_hidden_skeleton') or spec.get('recovered_world_contact'):
        raise ValueError('Pixel captures do not recover hidden skeleton/world contact')
    for observation in spec.get('observations', []):
        if observation['kind'] not in ('visible_surface', 'inferred_pose'):
            raise ValueError('An observed sprite is not source-known bone evidence')
        i = observation['frame_index']
        if not isinstance(i, int) or not 0 <= i < len(expected):
            raise ValueError('Observation has no captured frame')
        if observation['image_sha256'] != expected[i]['sha256']:
            raise ValueError('Observation belongs to different pixels')
        if observation['kind'] == 'visible_surface' and observation.get('visibility') != 'visible':
            raise ValueError('Hidden point cannot be a visible measurement')
        if not positive(observation.get('uncertainty_px')):
            raise ValueError('Observation uncertainty is missing')
    experiment = spec.get('experiment')
    inserted = 0
    if experiment:
        keys = experiment['keys']
        if len(keys) != len(expected):
            raise ValueError('Key coverage changed')
        for key in keys:
            bound_file(key, root)
        sequence = experiment['sequence']
        factor = 2 if experiment['mode'] == 'locked_keys_with_midpoints' else 1
        if experiment['mode'] not in ('key_paintover', 'locked_keys_with_midpoints') or len(sequence) != factor * len(keys):
            raise ValueError('Wrong experiment sequence')
        duration = experiment['cycle_ms']
        if not positive(duration):
            raise ValueError('Invalid experiment clock')
        source_duration = sum(f['duration_ms'] for f in expected)
        if not positive(source_duration) or any(not positive(f['duration_ms']) for f in expected):
            raise ValueError('This experiment needs a known positive source clock')
        clock_ratio = duration / source_duration
        if duration != source_duration and experiment.get('clock_scope') != 'explicit_retimed_control':
            raise ValueError('Changed clock must be labeled a retimed control')
        elapsed = 0
        for i, frame in enumerate(sequence):
            path = bound_file(frame, root)
            with Image.open(path) as image:
                if list(image.size) != experiment['canvas']:
                    raise ValueError('Changed authored canvas')
            if not positive(frame['duration_ms']) or abs(frame['time_ms'] - elapsed) > 1e-7:
                raise ValueError('Authored clock has a gap/overlap')
            elapsed += frame['duration_ms']
            key_index = i // factor
            key_time = (expected[key_index]['time_ms'] - expected[0]['time_ms']) * clock_ratio
            half_exposure = expected[key_index]['duration_ms'] * clock_ratio / factor
            intended_time = key_time + (i % factor) * half_exposure
            if abs(frame['time_ms'] - intended_time) > 1e-7 or abs(frame['duration_ms'] - half_exposure) > 1e-7:
                raise ValueError('Authored phase moved away from its source key/midpoint')
            if i % factor == 0:
                if frame['role'] != 'authored_key' or frame['source_index'] != key_index or frame['sha256'] != keys[key_index]['sha256']:
                    raise ValueError('Protected authored key/order changed')
            else:
                inserted += 1
                if frame['role'] != 'authored_inbetween' or frame['source_pair'] != [key_index, (key_index + 1) % len(keys)] or frame.get('recovered_from_game') is not False:
                    raise ValueError('Inbetween must name its source pair and remain authored')
        if abs(elapsed - duration) > 1e-7:
            raise ValueError('Experiment cycle mismatch')
    return {'schema': 'reference-truth-report-v1', 'source_kind': spec['source_kind'],
            'evidence_status': 'BOUND_PIXELS_AND_DECLARED_CLOCK_VERIFIED',
            'captured_exposures': len(expected), 'authored_inbetweens': inserted,
            'experiment_contract_verified': bool(experiment),
            'hidden_skeleton_recovered': False, 'world_contact_recovered': False,
            'painted_anatomy_status': 'REVIEW_REQUIRED', 'natural_motion_approved': False,
            'complete_replaceable_painted_parts': False, 'production_ready': False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--contract', type=Path, required=True)
    p.add_argument('--root', type=Path, default=Path.cwd())
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--require-production', action='store_true')
    a = p.parse_args()
    report = audit(json.loads(a.contract.read_text()), a.root)
    report['contract_sha256'] = sha(a.contract)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['evidence_status'], '/ art and production remain unapproved')
    if a.require_production:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
