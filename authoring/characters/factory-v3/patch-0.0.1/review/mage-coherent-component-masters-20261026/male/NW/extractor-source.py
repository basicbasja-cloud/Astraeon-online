"""Extract complete transparent sprites across nominal grid boundaries.

Connected figures keep their original pixels and fixed grid origins. A sprite
may spill into a neighboring cell without losing its boot or receiving that
neighbor's staff tip. No figure fitting, scaling, warping or limb assembly.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


def extract(image, grid, canvas, offset, minimum_figure_area=1000, fragment_distance=8):
    rgba = np.array(image.convert('RGBA'))
    columns, rows = grid
    height, width = rgba.shape[:2]
    if min(columns, rows) <= 0 or width % columns or height % rows:
        raise ValueError('Source must have an exact integer grid stride')
    if min(canvas) <= 0 or len(offset) != 2:
        raise ValueError('Invalid output canvas or common origin offset')
    cell_width, cell_height = width//columns, height//rows
    visible = rgba[:, :, 3] > 0
    labels, count = ndimage.label(visible, structure=np.ones((3, 3)))
    sizes = np.bincount(labels.ravel())
    majors = [label for label in range(1, count+1) if sizes[label] >= minimum_figure_area]
    if len(majors) != columns*rows:
        raise ValueError(f'Expected {columns*rows} separate whole figures; found {len(majors)}')
    centers = ndimage.center_of_mass(rgba[:, :, 3], labels, majors)
    lookup = np.zeros(count+1, dtype=np.int32)
    assigned_slots = set()
    for label, (y, x) in zip(majors, centers):
        column, row = int(x//cell_width), int(y//cell_height)
        slot = row*columns+column
        if not (0 <= column < columns and 0 <= row < rows) or slot in assigned_slots:
            raise ValueError('Whole-figure centers do not map uniquely to the nominal source cells')
        assigned_slots.add(slot)
        lookup[label] = slot+1
    major_mask = lookup[labels] > 0
    distance, nearest = ndimage.distance_transform_edt(~major_mask, return_indices=True)
    nearest_owner = lookup[labels[nearest[0], nearest[1]]]
    omitted = []
    for label, region in enumerate(ndimage.find_objects(labels), 1):
        if lookup[label] or region is None:
            continue
        local = labels[region] == label
        distances = np.where(local, distance[region], np.inf)
        point = np.unravel_index(distances.argmin(), distances.shape)
        gap = float(distances[point])
        if gap <= fragment_distance:
            lookup[label] = int(nearest_owner[region][point])
        else:
            omitted.append({'label': label, 'pixels': int(sizes[label]),
                            'maximum_alpha': int(rgba[region][:, :, 3][local].max()),
                            'distance_to_figure_px': gap})
    owners = lookup[labels]
    outputs, records = [], []
    reconstructed = np.zeros_like(rgba)
    for slot in range(columns*rows):
        y, x = np.nonzero(owners == slot+1)
        local_x = x-(slot % columns)*cell_width
        local_y = y-(slot//columns)*cell_height
        output_x, output_y = local_x+offset[0], local_y+offset[1]
        if (output_x < 0).any() or (output_x >= canvas[0]).any() or (output_y < 0).any() or (output_y >= canvas[1]).any():
            raise ValueError('The common output canvas clips assigned source pixels')
        output = np.zeros((canvas[1], canvas[0], 4), dtype=np.uint8)
        output[output_y, output_x] = rgba[y, x]
        reconstructed[y, x] = output[output_y, output_x]
        spill = (local_x < 0) | (local_x >= cell_width) | (local_y < 0) | (local_y >= cell_height)
        records.append({'index': slot, 'assigned_pixels': int(len(x)),
                        'spill_pixels_preserved': int(spill.sum()),
                        'source_cell_origin': [(slot % columns)*cell_width, (slot//columns)*cell_height],
                        'shared_output_offset': offset,
                        'local_alpha_bbox': [int(local_x.min()), int(local_y.min()), int(local_x.max()+1), int(local_y.max()+1)]})
        outputs.append(Image.fromarray(output))
    kept = owners > 0
    mismatches = int(np.any(reconstructed[kept] != rgba[kept], axis=1).sum())
    if mismatches:
        raise ValueError('Assigned source pixels changed during extraction')
    border = np.zeros(visible.shape, dtype=bool)
    border[[0, -1], :] = True
    border[:, [0, -1]] = True
    blockers = [{'reason': 'Unassigned visible component may be meaningful', **row}
                for row in omitted if row['maximum_alpha'] > 32 and row['pixels'] >= 3]
    if (border & kept & (rgba[:, :, 3] > 128)).any():
        blockers.append({'reason': 'Assigned opaque pixels touch the full source-sheet boundary; inspect possible source clipping'})
    return outputs, {'status': 'COMPLETE_CONNECTED_SPRITE_EXTRACTION_REQUIRES_POSE_AND_MATTE_REVIEW',
                     'grid': grid, 'native_cell_stride': [cell_width, cell_height],
                     'canvas': canvas, 'offset': offset, 'whole_figures': len(majors),
                     'assigned_pixel_recomposition_mismatches': mismatches,
                     'spill_pixels_preserved': sum(row['spill_pixels_preserved'] for row in records),
                     'omitted_components': omitted, 'production_blockers': blockers,
                     'per_figure_scaling_or_fitting': False, 'frames': records,
                     'runtime_admitted': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['source', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--grid', type=int, nargs=2, required=True)
    parser.add_argument('--canvas', type=int, nargs=2, default=[512, 512])
    parser.add_argument('--offset', type=int, nargs=2, default=[128, 128])
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Use a fresh complete-sprite extraction destination')
    frames, receipt = extract(Image.open(args.source), args.grid, args.canvas, args.offset)
    (args.output/'Master').mkdir(parents=True)
    for index, frame in enumerate(frames):
        path = args.output/'Master'/f'{index:03d}.png'
        frame.save(path)
        receipt['frames'][index]['output_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    receipt['source_sha256'] = hashlib.sha256(args.source.read_bytes()).hexdigest()
    receipt['implementation_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (args.output/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    (args.output/'extractor-source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({key: receipt[key] for key in ['whole_figures', 'spill_pixels_preserved', 'production_blockers']}))


if __name__ == '__main__':
    main()
