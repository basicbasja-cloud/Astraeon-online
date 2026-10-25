"""Invert a recorded shared paint viewport; never fit individual silhouettes.

Supports rectangular cells and fractional grid boundaries. This produces review
candidates only: source-pose, semantic cutout and runtime approval are separate.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


def unmatte_white_edges(pixels, background):
    """Remove white spill in a two-pixel outer band using nearby opaque color.

    Interior and enclosed whites are protected. Thin isolated lines without a
    nearby color reference are retained. This is an estimate, not new drawing.
    """
    result = pixels.copy()
    foreground = ~background
    distance = ndimage.distance_transform_edt(foreground)
    rgb = pixels[:, :, :3].astype(float)
    core = foreground & ((distance >= 3) | (rgb.max(axis=2) < 160))
    if not core.any():
        return result, 0
    core_distance, nearest = ndimage.distance_transform_edt(~core, return_indices=True)
    reference = rgb[nearest[0], nearest[1]]
    direction = 255-reference
    denominator = np.sum(direction*direction, axis=2)
    alpha = np.clip(np.sum((255-rgb)*direction, axis=2)/np.maximum(denominator, 1), 0, 1)
    selected = foreground & (distance <= 2) & (core_distance <= 3) & (denominator > 1000) & (alpha < .97)
    recovered = np.clip(255+(rgb-255)/np.maximum(alpha[:, :, None], .01), 0, 255)
    result[selected, :3] = np.rint(recovered[selected]).astype(np.uint8)
    result[selected, 3] = np.rint(alpha[selected]*255).astype(np.uint8)
    result[result[:, :, 3] == 0] = 0
    return result, int(selected.sum())


def normalize_batch(source, recipe, aspect_tolerance=0.005, white_edge_unmatting=False):
    columns, rows = recipe['grid']
    canvas_width, canvas_height = recipe['source_size']
    left, top, right, bottom = recipe['viewport']
    indices = recipe['source_pose_indices']
    values = [columns, rows, canvas_width, canvas_height, left, top, right, bottom, *indices]
    if any(isinstance(v, bool) or not isinstance(v, int) for v in values):
        raise ValueError('Grid, canvas, viewport and pose indices must be integers')
    if min(columns, rows, canvas_width, canvas_height) <= 0:
        raise ValueError('Invalid grid or source canvas')
    if not 0 <= left < right <= canvas_width or not 0 <= top < bottom <= canvas_height:
        raise ValueError('Viewport lies outside the source canvas')
    if len(indices) != columns * rows or len(set(indices)) != len(indices) or min(indices) < 0:
        raise ValueError('One unique source pose index is required per cell')
    width, height = right-left, bottom-top
    expected_aspect = columns*width/(rows*height)
    aspect_error = abs(source.width/source.height/expected_aspect - 1)
    if aspect_error > aspect_tolerance:
        raise ValueError(f'Sheet aspect differs from recorded viewport by {aspect_error:.2%}; do not stretch poses')
    source = source.convert('RGBA')
    frames, records = [], []
    for slot, index in enumerate(indices):
        x, y = slot % columns, slot // columns
        box = (x*source.width/columns, y*source.height/rows,
               (x+1)*source.width/columns, (y+1)*source.height/rows)
        if all(v == int(v) for v in box) and box[2]-box[0] == width and box[3]-box[1] == height:
            cell = source.crop(tuple(int(v) for v in box))
        else:
            cell = source.convert('RGBa').transform((width, height), Image.Transform.EXTENT,
                                                    box, Image.Resampling.BICUBIC).convert('RGBA')
        pixels = np.array(cell)
        unmatted_pixels = 0
        if pixels[:, :, 3].min() == 255:
            candidate = pixels[:, :, :3].min(axis=2) >= 242
            border = np.zeros(candidate.shape, dtype=bool)
            border[[0, -1], :] = candidate[[0, -1], :]
            border[:, [0, -1]] = candidate[:, [0, -1]]
            background = ndimage.binary_propagation(border, mask=candidate)
            if white_edge_unmatting:
                pixels, unmatted_pixels = unmatte_white_edges(pixels, background)
            pixels[background] = 0
        pixels[pixels[:, :, 3] == 0] = 0
        cell = Image.fromarray(pixels)
        frame = Image.new('RGBA', (canvas_width, canvas_height))
        frame.alpha_composite(cell, (left, top))
        alpha = np.array(cell)[:, :, 3] > 16
        edges = bool(alpha[0].any() or alpha[-1].any() or alpha[:, 0].any() or alpha[:, -1].any())
        frames.append(frame)
        records.append({'source_pose_index': index, 'source_box': box,
                        'alpha_bbox': frame.getbbox(), 'touches_viewport_edge': edges,
                        'white_edge_pixels_unmatted': unmatted_pixels})
    return frames, {'status': 'FIXED_VIEWPORT_REVIEW_CANDIDATE_NOT_ACCEPTED_ART',
                    'frame_space':recipe.get('frame_space','unspecified-source-canvas'),
                    'canonical_root':recipe.get('canonical_root'),
                    'aspect_error': aspect_error, 'shared_viewport': recipe['viewport'],
                    'source_size': recipe['source_size'], 'frames': records,
                    'production_blockers':[{'source_pose_index':r['source_pose_index'],'reason':'Paint touches the shared viewport edge; inspect clipping before admission'}for r in records if r['touches_viewport_edge']],
                    'per_frame_figure_fitting': False, 'source_pose_registered': False,
                    'semantic_cutouts_approved': False, 'runtime_admitted': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sheet', type=Path, required=True)
    parser.add_argument('--recipe', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--unmatte-white-edges', action='store_true')
    args = parser.parse_args()
    recipe = json.loads(args.recipe.read_text())
    with Image.open(args.sheet) as source:
        frames, receipt = normalize_batch(source, recipe, white_edge_unmatting=args.unmatte_white_edges)
    receipt['white_edge_unmatting'] = args.unmatte_white_edges
    args.output.mkdir(parents=True, exist_ok=True)
    for frame, record in zip(frames, receipt['frames']):
        frame.save(args.output/f"{record['source_pose_index']:03d}.png")
    receipt['inputs'] = {name: {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                         for name, path in [('sheet', args.sheet), ('recipe', args.recipe)]}
    (args.output/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
