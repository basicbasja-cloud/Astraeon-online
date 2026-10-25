"""Check raw generated cells before normalization, cutout or runtime admission.

Read-only extraction gate. Passing this gate does not approve anatomy, motion,
semantic ownership, resolution or swaps. Never repair clipping by cropping it.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image


def audit(image, grid, padding_fraction=.025, minimum_alpha=32):
    columns, rows = grid
    if any(isinstance(v, bool) or not isinstance(v, int) or v < 1 for v in grid):
        raise ValueError('Positive integer sheet grid required')
    if not 0 <= padding_fraction < .25 or not 1 <= minimum_alpha <= 255:
        raise ValueError('Invalid alpha or margin gate')
    rgba = np.array(image.convert('RGBA'))
    records = []
    # Rounded common boundaries partition every source pixel once, including
    # sheets whose cell boundaries fall between pixels.
    xs = [round(i*image.width/columns) for i in range(columns+1)]
    ys = [round(i*image.height/rows) for i in range(rows+1)]
    if min(np.diff(xs)) < 2 or min(np.diff(ys)) < 2:
        raise ValueError('Cells are too small')
    for index in range(columns*rows):
        x, y = index % columns, index // columns
        cell = rgba[ys[y]:ys[y+1], xs[x]:xs[x+1]]
        foreground = cell[:, :, 3] >= minimum_alpha
        yy, xx = np.where(foreground)
        reasons = []
        bounds = None
        if not len(xx):
            reasons.append('empty_cell')
        else:
            bounds = [int(xx.min()), int(yy.min()), int(xx.max()+1), int(yy.max()+1)]
            height, width = foreground.shape
            px, py = max(1, round(width*padding_fraction)), max(1, round(height*padding_fraction))
            if bounds[0] < px or bounds[1] < py or bounds[2] > width-px or bounds[3] > height-py:
                reasons.append('foreground_enters_cell_padding')
        # Gross saturated red halos are absent from this Mage design. Report
        # their count, but do not reject generic red costumes or erase them.
        rgb = cell[:, :, :3].astype(float)
        red = foreground & (rgb[:, :, 0] > 170) & (rgb[:, :, 1] < 45) & (rgb[:, :, 2] < 45)
        records.append({'index':index, 'source_box':[xs[x],ys[y],xs[x+1],ys[y+1]],
                        'foreground_bbox':bounds, 'saturated_red_pixels':int(red.sum()),
                        'extraction_gate_passed':not reasons, 'blockers':reasons})
    return {'status':'RAW_SHEET_EXTRACTION_CHECK_ONLY', 'grid':grid,
            'source_size':list(image.size), 'minimum_alpha':minimum_alpha,
            'padding_fraction':padding_fraction, 'frames':records,
            'extraction_gate_passed':all(r['extraction_gate_passed'] for r in records),
            'paint_alignment_approved':False, 'semantic_cutouts_approved':False,
            'runtime_admitted':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sheet',type=Path,required=True)
    parser.add_argument('--grid',type=int,nargs=2,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    with Image.open(args.sheet) as image:
        report = audit(image,args.grid)
    report['sheet_sha256'] = hashlib.sha256(args.sheet.read_bytes()).hexdigest()
    report['implementation_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'extraction_gate_passed':report['extraction_gate_passed'],
                      'blocked_frames':sum(not f['extraction_gate_passed'] for f in report['frames'])}))


if __name__ == '__main__':
    main()
