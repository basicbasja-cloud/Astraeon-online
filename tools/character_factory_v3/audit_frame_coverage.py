"""Audit per-frame source and imported bindings without implying art approval."""
import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from build_action_inventory import build_inventory

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'authoring/characters/factory-v3/patch-0.0.1'
CORE_ROLES = ('BodyCostume', 'HeadHair', 'Weapon')


def read(path):
    return json.loads(path.read_text())


def audit(base):
    config, ledger = read(base / 'factory.json'), read(base / 'ledger.json')
    inventory = build_inventory(config, ledger, base)
    store = read(base / 'cutout-store/index.json')
    bindings = {}
    for job in {row['paint_job'] for row in inventory['rows']}:
        path = base / 'cutouts' / job / 'bindings.json'
        if not path.is_file():
            continue
        raw = read(path)
        if raw.get('paint_job') != job:
            raise ValueError(f'Bindings identify a different paint job: {job}')
        indexed = {}
        for frame in raw.get('frames', []):
            key = (frame['direction'], frame['index'])
            if key in indexed:
                raise ValueError(f'Duplicate frame binding: {job} {key}')
            indexed[key] = frame
        bindings[job] = indexed
    rows = []
    for action in inventory['rows']:
        for direction in action['directions']:
            for index in range(action['frames']):
                guide = base / 'guides' / action['guide_job'] / direction / f'{index:03d}.png'
                binding = bindings.get(action['paint_job'], {}).get((direction, index))
                issues = []
                if binding:
                    for role in CORE_ROLES:
                        asset = store.get('assets', {}).get(binding.get('assets', {}).get(role))
                        if not asset:
                            issues.append(f'{role}:missing_asset')
                            continue
                        if asset.get('role') != role:
                            issues.append(f'{role}:wrong_role')
                        if asset.get('pose_id') != binding.get('pose_id'):
                            issues.append(f'{role}:pose_mismatch')
                        if asset.get('camera_id') != binding.get('camera_id'):
                            issues.append(f'{role}:camera_mismatch')
                        object_id = asset.get('object')
                        if object_id not in store.get('objects', {}):
                            issues.append(f'{role}:missing_object_record')
                rows.append({'character': action['character'], 'action': action['action'],
                             'direction': direction, 'frame': index,
                             'guide_job': action['guide_job'], 'paint_job': action['paint_job'],
                             'guide_png_present': guide.is_file(), 'binding_present': bool(binding),
                             'core_metadata_issues': '|'.join(issues),
                             'technical_import_receipt': action['import_receipt_coverage'],
                             'visual_approved': False, 'runtime_approved': False})
    counts = Counter()
    for row in rows:
        counts['frame_views'] += 1
        counts['source_pngs_present'] += row['guide_png_present']
        counts['bindings_present'] += row['binding_present']
        counts['bound_frames_with_metadata_issues'] += bool(row['binding_present'] and row['core_metadata_issues'])
    return {'status': 'FRAME_INVENTORY_NOT_ART_OR_RUNTIME_APPROVAL', 'counts': dict(counts),
            'rows': rows, 'note': 'Source and metadata presence do not certify file pixels, hidden surfaces, grip, visual quality or gameplay.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=BASE)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Choose a fresh output directory')
    result = audit(args.base)
    args.output.mkdir(parents=True)
    (args.output / 'summary.json').write_text(json.dumps({k: v for k, v in result.items() if k != 'rows'}, indent=2) + '\n')
    with (args.output / 'frames.csv').open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=list(result['rows'][0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(result['rows'])
    print(json.dumps(result['counts']))


if __name__ == '__main__':
    main()
