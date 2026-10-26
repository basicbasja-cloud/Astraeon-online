"""Register complete master frames for a demonstrably planted-foot source.

Calibrate placement on the first painted sole, then follow the guide's relative
foot displacement. One integer translation moves the entire frame. This does
not change body proportions, warp boots, or certify other pose correspondence.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


def source_foot_ranges(rows, limit=2.):
    ranges = {}
    for name in ['foot_l', 'foot_r']:
        points = np.asarray([row['landmarks'][name] for row in rows], dtype=float)
        if not len(points) or points.shape[1:] != (2,) or not np.isfinite(points).all():
            raise ValueError('Invalid projected source foot points')
        ranges[name] = float(np.linalg.norm(points-points[0], axis=1).max())
    if max(ranges.values()) > limit:
        raise ValueError('Source feet are not sufficiently planted for this automatic registration')
    return ranges


def observed_sole(image, hint_x=None, threshold=245, band=18):
    alpha = np.array(image.convert('RGBA'))[:, :, 3]
    mask = alpha > threshold
    ys, xs = np.nonzero(mask)
    if not len(xs):
        raise ValueError('No sufficiently opaque painted sole')
    mask[:max(0, int(ys.max())-band)] = False
    labels, count = ndimage.label(mask, structure=np.ones((3, 3)))
    candidates = []
    for label in range(1, count+1):
        y, x = np.nonzero(labels == label)
        if len(x) < 32 or x.max()-x.min()+1 < 8:
            continue  # A narrow staff shaft is not a boot.
        bottom = int(y.max())
        sole_x = float(np.median(x[y >= bottom-1]))
        candidates.append({'point': [sole_x, float(bottom)], 'pixels': int(len(x)),
                           'bbox': [int(x.min()), int(y.min()), int(x.max()+1), bottom+1]})
    if not candidates:
        raise ValueError('No unambiguous boot-sized component in the lower foot band')
    if hint_x is None:
        selected = max(candidates, key=lambda row: (row['point'][1], row['pixels']))
    else:
        selected = min(candidates, key=lambda row: (abs(row['point'][0]-hint_x), -row['pixels']))
        if abs(selected['point'][0]-hint_x) > 32:
            raise ValueError('Painted sole drift is too large for automatic foot association')
    return np.array(selected['point']), candidates


def rigid_translation(image, delta):
    pixels = np.array(image.convert('RGBA'))
    output = np.zeros_like(pixels)
    ys, xs = np.nonzero(pixels[:, :, 3] > 0)
    x, y = xs+delta[0], ys+delta[1]
    if (x < 0).any() or (x >= image.width).any() or (y < 0).any() or (y >= image.height).any():
        raise ValueError('Whole-frame translation would clip visible source pixels')
    output[y, x] = pixels[ys, xs]
    if not np.array_equal(output[y, x], pixels[ys, xs]):
        raise ValueError('Rigid translation changed source colors or alpha')
    return Image.fromarray(output)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['masters', 'guide', 'recipe', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--direction', required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Use a fresh planted-foot registration destination')
    guide = json.loads(args.guide.read_text())
    recipe = json.loads(args.recipe.read_text())
    rows = guide['views'][args.direction]['frames']
    excursions = source_foot_ranges(rows, recipe['maximum_source_foot_excursion_px'])
    viewport = recipe['source_guide_viewport']
    scale = recipe['native_cell'][0]/(viewport[2]-viewport[0])
    if abs(scale-recipe['native_cell'][1]/(viewport[3]-viewport[1])) > 1e-9:
        raise ValueError('Guide and native cell scales must be uniform')
    first_path = args.masters/'000.png'
    first_sole, _ = observed_sole(Image.open(first_path))
    first_points = rows[0]['landmarks']
    if abs(first_points['foot_l'][0]-first_points['foot_r'][0]) < 20:
        support = max(['foot_l', 'foot_r'], key=lambda name: first_points[name][1])
    else:
        support = min(['foot_l', 'foot_r'], key=lambda name: abs(
            recipe['paint_offset'][0]+(first_points[name][0]-viewport[0])*scale-first_sole[0]))
    source_first = np.array(first_points[support])
    (args.output/'Master').mkdir(parents=True)
    records = []
    before_points, after_points = [], []
    for index, row in enumerate(rows):
        path = args.masters/f'{index:03d}.png'
        image = Image.open(path).convert('RGBA')
        if image.size != tuple(recipe['canvas']):
            raise ValueError('Unexpected master canvas')
        source_delta = (np.array(row['landmarks'][support])-source_first)*scale
        expected = first_sole+source_delta
        observed, candidates = observed_sole(image, float(expected[0]))
        delta = np.rint(expected-observed).astype(int)
        output = rigid_translation(image, delta)
        measured, _ = observed_sole(output, float(expected[0]))
        residual = float(np.linalg.norm(measured-expected))
        if residual > .75:
            raise ValueError('Independent sole measurement does not confirm rigid registration')
        destination = args.output/'Master'/path.name
        output.save(destination)
        records.append({'index': index, 'translation': delta.tolist(), 'observed_sole': observed.tolist(),
                        'expected_sole': expected.tolist(), 'measured_output_sole': measured.tolist(),
                        'output_sole_error_px': residual, 'candidate_boots': candidates,
                        'source_sha256': sha(path), 'output_sha256': sha(destination)})
        before_points.append(observed.tolist())
        after_points.append(measured.tolist())
    receipt = {'status': 'RELATIVE_PLANTED_FOOT_WHOLE_MASTER_REGISTRATION_NOT_ART_ACCEPTANCE',
               'direction': args.direction, 'support_foot_reference': support,
               'source_foot_excursions_px': excursions, 'first_painted_sole': first_sole.tolist(),
               'source_to_native_scale': scale, 'frames': records,
               'before_observed_sole_span_xy': np.ptp(before_points, axis=0).tolist(),
               'after_observed_sole_span_xy': np.ptp(after_points, axis=0).tolist(),
               'guide_sha256': sha(args.guide), 'recipe_sha256': sha(args.recipe),
               'implementation_sha256': sha(Path(__file__)), 'source_pixels_redrawn_or_scaled': False,
               'pose_naturalness_or_other_landmarks_approved': False, 'runtime_admitted': False,
               'note': 'Placement is calibrated to the first painting; this does not claim absolute joint registration or correct changing boot silhouettes.'}
    (args.output/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    (args.output/'recipe-source.json').write_bytes(args.recipe.read_bytes())
    (args.output/'registrar-source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({k: receipt[k] for k in ['direction', 'before_observed_sole_span_xy', 'after_observed_sole_span_xy']}))


if __name__ == '__main__':
    main()
