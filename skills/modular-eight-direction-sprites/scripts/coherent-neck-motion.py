#!/usr/bin/env python3
"""Bound surface diagnostics for coherent body + complete head exports.

Receiver endpoints and support ROIs are reviewed observations, never inferred
hidden joints. Reports preserve failed gates; diagnostic exit zero is not approval.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def transform(matrix, point):
    a, b, c, d, x, y = matrix
    return np.array([a * point[0] + c * point[1] + x,
                     b * point[0] + d * point[1] + y])


def uniform_positive(matrix, scale):
    a, b, c, d = matrix[:4]
    return bool(abs(a*d-b*c-scale*scale) < 1e-9 and
                abs(a*a+b*b-scale*scale) < 1e-9 and
                abs(a*c+b*d) < 1e-9)


def neck_metrics(row, contract, passes):
    body_points = [transform(row['body_matrix'], p)
                   for p in row['body_collar_lip_points_native']]
    head_points = [transform(row['head_matrix'], p)
                   for p in contract['head_insertion_points_native']]
    residual = max(float(np.linalg.norm(a-b)) for a, b in zip(body_points, head_points))
    center = sum(body_points) / 2
    tangent = body_points[1] - body_points[0]
    tangent /= np.linalg.norm(tangent)
    normal = np.array([-tangent[1], tangent[0]])

    def sample(image, p):
        x, y = np.rint(p).astype(int)
        return image[y, x, 3] if 0 <= y < image.shape[0] and 0 <= x < image.shape[1] else 0

    bridge = min(int(sample(passes['full'], center+normal*k)) for k in range(-4, 6))
    head_above = int(sample(passes['head'], center-normal*4))
    body_below = int(sample(passes['body'], center+normal*5))
    # A fully opaque collar-pass pixel is independently owned by original body.
    interior = passes['collar'][:, :, 3] == 255
    count = int(interior.sum())
    wrong = int(np.count_nonzero(np.any(passes['full'][interior] != passes['body'][interior], axis=1)))
    return dict(endpoint_residual_px=residual, bridge_alpha_min=bridge,
                head_above_alpha=head_above, body_below_alpha=body_below,
                opaque_collar_pixels=count, wrong_collar_pixels=wrong,
                pass_=bool(residual <= contract['receiver_endpoint_budget_px'] and
                           bridge >= 240 and head_above >= 240 and body_below >= 240 and
                           count >= 20 and wrong == 0))


def extrema(image, roi):
    x0, y0, x1, y1 = map(int, roi)
    if x0 < 0 or y0 < 0 or x1 > image.shape[1] or y1 > image.shape[0]:
        raise ValueError('Support ROI is outside actual image')
    ys, xs = np.nonzero(image[y0:y1, x0:x1, 3] >= 128)
    if not len(xs):
        raise ValueError('No visible support surface: unknown, never pass')
    return [float(xs.min()+x0), float(ys.max()+y0)]


def support_metrics(rows, contract, root, bodies):
    output = {}
    scale = contract['body_uniform_rest_matrix'][0]
    for name, roi in contract['forefoot_observation_rois_native'].items():
        raw, rendered = [], []
        for row, body in zip(rows, bodies):
            raw.append(extrema(np.array(Image.open(root/row['body']['path']).convert('RGBA')), roi))
            lo = np.floor(transform(row['body_matrix'], roi[:2])).astype(int)
            hi = np.ceil(transform(row['body_matrix'], roi[2:])).astype(int)
            rendered.append(extrema(body, [*lo, *hi]))
        native_range = np.ptp(np.array(raw), axis=0)*scale
        raster_range = np.ptp(np.array(rendered), axis=0)
        output[name] = dict(raw_surface_xy=raw, rendered_surface_xy=rendered,
                            raw_range_at_display_scale_px=native_range.tolist(),
                            rendered_range_px=raster_range.tolist(),
                            pass_=bool(max(*native_range, *raster_range) <= contract['planted_surface_budget_px']))
    return output


def phase_metrics(rows, source, contract):
    source_y = np.array([f['points']['head']['xy'][1] for f in source['frames']])
    observed_y = np.array([r['observed_receiver_surface_xy'][1] for r in rows])
    # Two declared calibration samples (rest/deepest); all remaining samples held out.
    peak = int(np.argmax(source_y))
    expected = (source_y-source_y[0])/(source_y[peak]-source_y[0])
    actual = (observed_y-observed_y[0])/(observed_y[peak]-observed_y[0])
    held_out = [i for i in range(len(rows)) if i not in [0, peak]]
    error = float(max(abs(actual[i]-expected[i]) for i in held_out))
    overshoot = float(max(0, observed_y[0]-min(observed_y[peak:])))
    return dict(calibration_indices=[0, peak], held_out_indices=held_out,
                source_normalized=expected.tolist(), observed_normalized=actual.tolist(),
                held_out_max_phase_error=error, recovery_overshoot_px=overshoot,
                pass_=bool(error <= contract['phase_warning_fraction'] and
                           overshoot <= contract['recovery_overshoot_budget_px']))


def audit(contract, root, render_root):
    checks = {}
    bindings = [contract['source'], contract['head']]
    for rows in contract['variants'].values():
        for row in rows:
            bindings.extend([row['body'], row['raw_sheet']])
    checks['input_hashes'] = all(digest(root/b['path']) == b['sha256'] for b in bindings)
    source = json.loads((root/contract['source']['path']).read_text())
    checks['source_glb_hash'] = digest(root/source['source_file']) == source['source_sha256']
    checks['no_false_production_declaration'] = not contract['full_factory_production_pass']
    checks['one_clock_and_explicit_holds'] = all(
        len(clock) == 8 and clock[-1] == contract['terminal_hold_ms'] and min(clock) > 0
        for clock in contract['clocks'].values())
    variants = {}
    for name, rows in contract['variants'].items():
        passes = [{mode: np.array(Image.open(render_root/name/mode/f'{i:02}.png').convert('RGBA'))
                   for mode in ['full', 'body', 'head', 'collar']} for i in range(len(rows))]
        constant = all(row['body_matrix'] == contract['body_uniform_rest_matrix'] for row in rows)
        positive = all(uniform_positive(row['head_matrix'], contract['head_scale']) for row in rows)
        clocks = [r['source_time_seconds'] for r in rows] == [f['source_time_seconds'] for f in source['frames']]
        crops = all(np.array_equal(np.array(Image.open(root/r['body']['path'])),
                    np.array(Image.open(root/r['raw_sheet']['path']).crop(
                    ((r['raw_art_index']%4)*384, (r['raw_art_index']//4)*512,
                     (r['raw_art_index']%4+1)*384, (r['raw_art_index']//4+1)*512)))) for r in rows)
        neck = [neck_metrics(row, contract, p) for row, p in zip(rows, passes)]
        support = support_metrics(rows, contract, root, [p['body'] for p in passes])
        phase = phase_metrics(rows, source, contract)
        unique = len({r['body']['sha256'] for r in rows})
        geometry = bool(constant and positive and clocks and crops and
                        unique >= contract['minimum_distinct_body_drawings'])
        neck_pass = geometry and all(n['pass_'] for n in neck)
        contact_pass = all(s['pass_'] for s in support.values())
        variants[name] = dict(common_body_transform=constant, positive_fixed_head_scale=positive,
                              exact_source_times=clocks, exact_raw_grid_crops=crops,
                              distinct_body_drawings=unique, neck=neck, neck_pass=neck_pass,
                              support=support, contact_pass=contact_pass, phase=phase,
                              motion_metrics_pass=bool(all(checks.values()) and neck_pass and contact_pass and phase['pass_']),
                              production_pass=False)
    return dict(scope='Reviewed visible surfaces only; no automatic anatomy, limb-side or acting certification',
                integrity_checks=checks, variants=variants, production_pass=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--render-root', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--require-motion', action='store_true')
    args = parser.parse_args()
    report = audit(json.loads(args.contract.read_text()), args.root, args.render_root)
    args.report.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({name: {k: v for k, v in row.items() if k in ['neck_pass','contact_pass','motion_metrics_pass']}
                      for name, row in report['variants'].items()}))
    if args.require_motion and not report['variants']['review']['motion_metrics_pass']:
        raise SystemExit(1)
