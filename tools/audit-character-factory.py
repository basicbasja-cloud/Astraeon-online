"""Inventory existing production evidence without promoting candidate approval."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.pack / 'MANIFEST.json').read_text())
    pack_checks = {name: digest(args.pack / name) == expected
                   for name, expected in manifest['files'].items()}
    if not all(pack_checks.values()):
        raise ValueError('Supplied pack differs from its manifest')
    source = ROOT / 'authoring/characters/swordsman-production'
    records = []
    for path in sorted(source.rglob('provenance.json')):
        value = json.loads(path.read_text())
        records.append({'file': path.relative_to(ROOT).as_posix(),
                        'sha256': digest(path), 'evidence': value})
    definition = json.loads((ROOT / 'assets/characters/swordsman-male-candidate/sprite.json').read_text())
    sources = ['docs/MODULAR_SPRITES.md', 'RAGNAROK_REFERENCE.md', 'STYLE_GUIDE.md',
               'CURRENT_HANDOFF.md', 'README.md', 'MASTER_PLAN.md', 'ASSET_LICENSES.md',
               'authoring/characters/swordsman-production/README.md',
               'docs/review/swordsman-production-v0.1/README.md',
               'authoring/characters/gait-rig-v50/approved-warrior-seed.png',
               'authoring/characters/swordsman-production/reference/approved-warrior-seed.png',
               'authoring/characters/swordsman-production/reference/identity-lock.json',
               'authoring/characters/swordsman-production/rig-walk/candidate-03/walk-proof.blend',
               'tools/build-swordsman-production.py', 'tools/build-swordsman-walk-rig.py',
               'tools/normalize-modular-strip.py', 'tools/pack-modular-sprites.py',
               'tools/validate-sprites.py', 'modular-sprites.js', 'animation.js',
               'wardrobe.js', 'docs/CHARACTERS_PATCH_001.md',
               'authoring/characters/true-modular/swordsman/male/README.md',
               'authoring/characters/true-modular/swordsman/male/blueprint.json',
               'authoring/characters/true-modular/swordsman/male/provenance/identity-lock.json',
               'tools/build_true_modular_swordsman.py', 'tools/modular_character_engine.py']
    report = {'status': 'AUDIT_ONLY', 'ownerApproval': 'NOT_GRANTED_BY_AUDIT',
              'packManifest': pack_checks,
              'sources': {name: digest(ROOT / name) for name in sources},
              'registration': definition['canvas'], 'directions': definition['directions'],
              'sourceApproval': definition['source'], 'slots': definition['slots'],
              'defaultParts': definition['defaultParts'], 'drawOrder': definition['drawOrder'],
              'clips': {name: {'framesPerDirection': len(clip['durations']),
                               'durations': clip['durations'], 'loop': clip['loop'],
                               'tags': clip.get('tags', []), 'cycleDistance': clip.get('cycleDistance')}
                        for name, clip in definition['clips'].items()},
              'candidateProvenance': records}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'PASS: {len(pack_checks)} pack hashes, {len(records)} provenance records; {args.output}')


if __name__ == '__main__':
    main()
