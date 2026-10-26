"""Report real per-character imports and capacity without producing or admitting art."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import statistics

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'authoring/characters/factory-v3/patch-0.0.1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def report(base=BASE):
    config = json.loads((base / 'factory.json').read_text())
    ledger = json.loads((base / 'ledger.json').read_text())
    characters = []
    missing_positions = 0
    imported_jobs = set()
    for character in config['characters']:
        rows = []
        for name, action in config['classes'][character['class']]['actions'].items():
            jobs = [j for j in ledger['paint_jobs'].values()
                    if j['character'] == character['id'] and name in j['actions']]
            expected = {(d, i) for d in action['authored_directions']
                        for i in range(action['frames'])}
            row = {'action': name, 'directions': action['authored_directions'],
                   'frame_count': action['frames'], 'expected_poses': len(expected),
                   'import_present': False, 'coverage_complete': False}
            if len(jobs) == 1:
                job = jobs[0]
                row['paint_job'] = job['id']
                folder = base / 'cutouts' / job['id']
                receipt_file = folder / 'import-receipt.json'
                bindings_file = folder / 'bindings.json'
                if receipt_file.is_file() and bindings_file.is_file():
                    receipt = json.loads(receipt_file.read_text())
                    bindings = json.loads(bindings_file.read_text())
                    actual = {(f['direction'], f['index']) for f in bindings['frames']}
                    valid = (receipt.get('paint_job') == job['id']
                             and bindings.get('paint_job') == job['id']
                             and bindings.get('character') == character['id']
                             and receipt.get('guide_job') == job['guide_job']
                             and receipt.get('all_frames_present') is True
                             and receipt.get('recomposition_mismatches') == 0
                             and len(actual) == len(bindings['frames']))
                    row.update(import_present=True, coverage_complete=valid and expected <= actual,
                               imported_poses=len(actual),
                               bindings_sha256=digest(bindings_file),
                               import_receipt_sha256=digest(receipt_file))
                    if row['coverage_complete']:
                        imported_jobs.add(job['id'])
            if not row['coverage_complete']:
                missing_positions += len(expected)
            rows.append(row)
        characters.append({'id': character['id'], 'class': character['class'],
                           'sex': character['body_variant'], 'actions': rows,
                           'covered_actions': sum(r['coverage_complete'] for r in rows),
                           'required_actions': len(rows),
                           'all_imports_present': all(r['coverage_complete'] for r in rows),
                           'runtime_admitted': character.get('runtime_admitted') is True,
                           'visual_approval_implied': False})
    usage = shutil.disk_usage(base)
    sample = base / 'review/mage-painted-native-walk-v4-20261026'
    pose_bytes = []
    for master in sorted((sample / 'Master').glob('*.png')):
        paths = [sample / role / master.name for role in
                 ['Master', 'BodyCostume', 'HeadHair', 'Weapon', 'WeaponHandOccluder']]
        if all(p.is_file() for p in paths):
            pose_bytes.append(sum(p.stat().st_size for p in paths))
    mean_bytes = statistics.mean(pose_bytes) if pose_bytes else None
    projected = round(mean_bytes * missing_positions) if mean_bytes else None
    return {'status': 'INCOMPLETE_NOT_PLAYABLE', 'characters': characters,
            'imported_paint_jobs': len(imported_jobs),
            'required_paint_jobs': len(ledger['paint_jobs']),
            'complete_admitted_characters': sum(c['all_imports_present'] and c['runtime_admitted']
                                                for c in characters),
            'missing_action_pose_positions_before_reuse': missing_positions,
            'capacity': {'free_bytes': usage.free, 'total_bytes': usage.total,
                         'observed_native_pose_bytes': pose_bytes,
                         'mean_observed_native_pose_bytes': mean_bytes,
                         'illustrative_remaining_pose_bytes_before_reuse': projected,
                         'estimate_is_not_a_lower_bound': True,
                         'estimate_excludes_raw_generation_editor_sheets_atlases_replay_and_git': True,
                         'space_below_one_measured_16_pose_output_plus_replay':
                         usage.free < 2 * sum(pose_bytes) if pose_bytes else None},
            'source_sha256': {n: digest(base / n) for n in ['factory.json', 'ledger.json']},
            'notes': ['Coverage is measured from actual receipts and bindings, not draft GIFs.',
                      'Timings, anatomy, layer ownership and runtime acceptance are separate gates.',
                      'Storage estimate scales the current five-role Mage NE study; reuse and differing classes can change it.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Choose a new readiness report path')
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in
                      ['status', 'imported_paint_jobs', 'required_paint_jobs', 'complete_admitted_characters']}))
    print(json.dumps(result['capacity']))


if __name__ == '__main__':
    main()
