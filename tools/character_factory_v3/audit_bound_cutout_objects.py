"""Verify bound cutout object pixel hashes; this does not approve artwork."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'authoring/characters/factory-v3/patch-0.0.1'


def audit(base, root=ROOT):
    store = json.loads((base / 'cutout-store/index.json').read_text())
    assets, objects = store['assets'], store['objects']
    referenced = set()
    errors = []
    frames = 0
    for file in sorted((base / 'cutouts').glob('*/bindings.json')):
        data = json.loads(file.read_text())
        for row in data['frames']:
            frames += 1
            for asset_id in row['assets'].values():
                if asset_id not in assets:
                    errors.append({'id': asset_id, 'issue': 'missing_asset_record'})
                    continue
                referenced.add(assets[asset_id]['object'])
    checked = 0
    for object_id in sorted(referenced):
        obj = objects.get(object_id)
        if obj is None:
            errors.append({'id': object_id, 'issue': 'missing_object_record'})
            continue
        path = (root / obj['file']).resolve()
        if not path.is_relative_to(root.resolve()):
            errors.append({'id': object_id, 'issue': 'object_path_outside_repository'})
            continue
        try:
            with Image.open(path) as src:
                image = src.convert('RGBA')
                digest = hashlib.sha256(image.tobytes()).hexdigest()
                if list(image.size) != obj['canvas']:
                    errors.append({'id': object_id, 'issue': 'canvas_mismatch'})
                if digest != obj['rgba_sha256'] or digest != object_id:
                    errors.append({'id': object_id, 'issue': 'rgba_hash_mismatch'})
                checked += 1
        except (OSError, ValueError) as exc:
            errors.append({'id': object_id, 'issue': type(exc).__name__})
    return {'status': 'CUTOUT_OBJECT_INTEGRITY_NOT_VISUAL_APPROVAL',
            'binding_frames': frames, 'unique_bound_objects': len(referenced),
            'objects_read': checked, 'errors': errors, 'art_approved': False,
            'runtime_approved': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Choose a fresh output path')
    result = audit(BASE)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'errors'}), 'errors:', len(result['errors']))
    if result['errors']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
