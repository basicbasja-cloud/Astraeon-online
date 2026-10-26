"""Remove explicitly seeded enclosed white background, protecting costume whites.

Background removal changes alpha. Optional white spill correction also changes
RGB within the outer two pixels. Neither operation certifies mask semantics.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['frames', 'annotations', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Use a fresh cleaned-master destination')
    data = json.loads(args.annotations.read_text())
    args.output.mkdir(parents=True)
    records = []
    for item in data['frames']:
        path = args.frames/f"{item['index']:03d}.png"
        before = np.array(Image.open(path).convert('RGBA'))
        white = (before[:, :, :3].min(2) >= 242) & (before[:, :, 3] > 0)
        seed = np.zeros(white.shape, bool)
        decisions = []
        for point in item['background_seeds']:
            x, y = np.rint(np.array(point)*data['cell_to_frame']['scale']+data['cell_to_frame']['offset']).astype(int)
            # A seed outside visible enclosed white can already be transparent;
            # record it rather than manufacturing an arbitrary nearby seed.
            selected = bool(white[y, x])
            seed[y, x] = selected
            decisions.append({'point': [int(x), int(y)], 'enclosed_white_selected': selected})
        if item.get('background_regions'):
            region = Image.new('L', (white.shape[1], white.shape[0]))
            draw = ImageDraw.Draw(region)
            for polygon in item['background_regions']:
                draw.polygon([tuple(np.array(point)*data['cell_to_frame']['scale']+data['cell_to_frame']['offset']) for point in polygon], fill=255)
            labels, count = ndimage.label(white)
            sizes = np.bincount(labels.ravel())
            selected = {int(i) for i in np.unique(labels[np.array(region) > 0]) if i and sizes[i] >= 20}
            seed |= np.isin(labels, list(selected)) & (np.array(region) > 0)
        removed = ndimage.binary_propagation(seed, mask=white)
        after = before.copy()
        after[removed] = 0
        if np.any(after[~removed] != before[~removed]):
            raise ValueError('Protected source pixels changed')
        edge_changes = 0
        if data.get('unmatte_outer_two_pixels'):
            from normalize_fixed_viewport_batch import unmatte_white_edges
            background = after[:, :, 3] == 0
            cleaned, edge_changes = unmatte_white_edges(after, background)
            protected = ndimage.distance_transform_edt(~background) > 2
            if np.any(cleaned[protected] != after[protected]):
                raise ValueError('White-spill cleanup changed protected interior')
            after = cleaned
        Image.fromarray(after).save(args.output/path.name)
        records.append({'index': item['index'], 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'removed_pixels': int(removed.sum()), 'outer_edge_pixels_unmatted': edge_changes,
                        'protected_interior_pixel_changes': 0, 'seeds': decisions})
    receipt = {'status': 'ANCHORED_BACKGROUND_MASK_REPAIR_REQUIRES_VISUAL_REVIEW',
               'annotations_sha256': hashlib.sha256(args.annotations.read_bytes()).hexdigest(),
               'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'frames': records, 'anatomy_redrawn': False, 'source_pose_registered': False}
    (args.output/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    (args.output/'annotations-source.json').write_bytes(args.annotations.read_bytes())
    (args.output/'cleaner-source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'frames': len(records), 'removed_pixels': sum(r['removed_pixels'] for r in records)}))


if __name__ == '__main__':
    main()
