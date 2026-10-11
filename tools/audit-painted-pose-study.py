"""Read-only raster/provenance audit; no image edits or automatic art approval."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'authoring/characters/swordsman-production/paint-finish-01'


def inspect(path):
    with Image.open(path) as image:
        rgba = np.asarray(image.convert('RGBA'))
        width, height = image.size
        mode = image.mode
    alpha = rgba[:, :, 3]

    def bounds(threshold):
        yy, xx = np.where(alpha >= threshold)
        if not len(xx):
            return None
        return [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1]

    opaque = bounds(224)
    return {
        'file': path.relative_to(ROOT).as_posix(),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'canvas': [width, height], 'mode': mode,
        'alphaBounds': bounds(1), 'opaqueBoundsAlpha224': opaque,
        'normalizedOpaqueBounds': [round(v / (width if i % 2 == 0 else height), 6)
                                  for i, v in enumerate(opaque)],
        'faintPixelsAlpha1To15': int(((alpha >= 1) & (alpha <= 15)).sum()),
        'transparentPixels': int((alpha == 0).sum()),
    }


def main():
    guide = json.loads((OUT / 'pose-guide.json').read_text(encoding='utf-8'))
    assert abs(guide['gripForearmDegrees'] - 90) < .05
    assert guide['neutralWrist'] and guide['sourceNativeUnchanged']
    for path_key, sha_key in [('guideNative', 'guideNativeSHA256')]:
        assert hashlib.sha256((ROOT / guide[path_key]).read_bytes()).hexdigest() == guide[sha_key]
    source = ROOT / '.character-tools/checkpoints/fantasy-base-01-native.blend'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == guide['sourceNativeSHA256']
    paths = [ROOT / 'authoring/characters/swordsman-production/fresh-2d/candidate-01/candidate.png']
    paths += sorted([*OUT.glob('ro-idle-guide-*.png'), *OUT.glob('painted-*.png')])
    images = {path.name: inspect(path) for path in paths}
    reference = images['ro-idle-guide-SE.png']
    reference_box = reference['normalizedOpaqueBounds']
    comparisons = {}
    for name in ['painted-se-style-pilot.png', 'painted-se-ro-pose-pilot.png', 'painted-se-registration-pilot.png']:
        if name not in images:
            continue
        box = images[name]['normalizedOpaqueBounds']
        comparisons[name] = {
            'opaqueHeightRatioToROGuide': round((box[3] - box[1]) / (reference_box[3] - reference_box[1]), 6),
            'opaqueTopDeltaCanvasFraction': round(box[1] - reference_box[1], 6),
            'opaqueBottomDeltaCanvasFraction': round(box[3] - reference_box[3], 6),
            'note': 'Silhouette measurements only. They do not establish joint, grip, identity or layer correctness.',
        }
    report = {
        'status': 'PAINTED_POSE_STUDY_NOT_PRODUCTION',
        'ownerApproved': False, 'runtimeAdmitted': False,
        'generator': 'Built-in image_gen; no API CLI or paid third-party job.',
        'inputRoles': {
            'registrationCorrection': {'editTarget': 'painted-se-ro-pose-pilot.png', 'layoutReference': 'ro-idle-guide-SE.png'},
            'roPosePaint': {'editTarget': 'ro-idle-guide-SE.png', 'identityAndPaintReference': 'candidate.png'},
            'stylePilot': {'poseReference': 'Fitted fantasy-source SE Idle 640px bake; exact source path not retained in first prompt.',
                           'identityAndPaintReference': 'candidate.png'},
        },
        'images': images, 'silhouetteComparisons': comparisons,
        'guideAssertions': {'sourceNativeUnchanged': True, 'gripForearmDegrees': guide['gripForearmDegrees'],
                            'neutralWrist': True, 'directions': list(guide['directions'])},
        'paintedRegistrationEstablished': False,
        'paintedModularLayersEstablished': False,
        'paintedAnimationConsistencyEstablished': False,
    }
    for prompt_name in ['style-pilot-prompt.txt', 'ro-pose-paint-prompt.txt', 'registration-correction-prompt.txt']:
        report.setdefault('prompts', {})[prompt_name] = hashlib.sha256((OUT / prompt_name).read_bytes()).hexdigest()
    (OUT / 'paint-study-audit.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'images': len(images), 'comparisons': comparisons, 'productionApproved': False}, indent=2))


if __name__ == '__main__':
    main()
