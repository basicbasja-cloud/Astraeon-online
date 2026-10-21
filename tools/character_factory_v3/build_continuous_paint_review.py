"""Assemble a whole-sheet animation study at source cadence, without pose fitting."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from assemble_mesh2motion_paint_review import cut_white


def save_one_shot(path, images, durations):
    # Intentionally omit the GIF loop extension: recovery is not a raised guard.
    images[0].save(path, save_all=True, append_images=images[1:],
                   duration=durations, disposal=2, optimize=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folder', type=Path)
    args = parser.parse_args()
    root = args.folder
    plan = json.loads((root / 'plan.json').read_text())
    source = root / 'clean-white-sheet.png'
    raw = Image.open(source)
    master, matte = cut_white(raw)
    size = 512
    # The generated sheet does not obey equal row heights. Extract complete
    # connected figures first so boots/blades cannot leak into adjacent cells.
    # Four explicitly recorded row translations correct sheet packing only;
    # there is no independent figure bbox scale or per-frame anchor fit.
    rgba = np.asarray(master)
    labels, _ = ndimage.label(rgba[:, :, 3] > 0)
    counts = np.bincount(labels.ravel())
    components = []
    for label in np.flatnonzero(counts > 1000):
        if label == 0:
            continue
        yy, xx = np.nonzero(labels == label)
        components.append({'label': int(label), 'bbox': [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1]})
    if len(components) != 16:
        raise ValueError(f'Expected 16 complete figures; found {len(components)}')
    rows = []
    row_baselines = [336, 665, 953, 1229]
    row_boundaries = [0, 350, 700, 965, raw.height]
    for row in range(4):
        entries = [entry for entry in components if row_boundaries[row] <= entry['bbox'][1] < row_boundaries[row + 1]]
        entries.sort(key=lambda entry: entry['bbox'][0])
        if len(entries) != 4:
            raise ValueError(f'Expected four figures in row {row}')
        rows.extend(entries)
    output = root / 'frames'
    output.mkdir(exist_ok=True)
    beauty = []
    comparisons = []
    frame_audit = []
    for index, source_frame in enumerate(plan['source_frames']):
        entry = rows[index]
        row, column = index // 4, index % 4
        pixels = np.zeros_like(rgba)
        pixels[labels == entry['label']] = rgba[labels == entry['label']]
        cut = Image.fromarray(pixels).crop(tuple(entry['bbox']))
        x = round(entry['bbox'][0] - column * raw.width / 4 + (size - raw.width / 4) / 2)
        y = round(entry['bbox'][1] + 432 - row_baselines[row])
        frame = Image.new('RGBA', (size, size))
        frame.alpha_composite(cut, (x, y))
        frame.save(output / f'{index:03d}.png')
        bg = Image.new('RGBA', frame.size, '#ececec')
        bg.alpha_composite(frame)
        beauty.append(bg.convert('RGB'))
        guide = Image.open(root.parent / 'eight-direction-guides' / 'SE' / f'{source_frame:03d}.png')
        guide = guide.convert('RGBa').resize(frame.size, Image.Resampling.LANCZOS).convert('RGBA')
        left = Image.new('RGBA', frame.size, '#ececec')
        left.alpha_composite(guide)
        pair = Image.new('RGB', (size * 2, size + 32), '#ececec')
        pair.paste(left.convert('RGB'), (0, 32))
        pair.paste(bg.convert('RGB'), (size, 32))
        draw = ImageDraw.Draw(pair)
        draw.text((8, 8), f'Mesh2Motion source {source_frame:03d}', fill='black')
        draw.text((size + 8, 8), f'Paint review {index:02d} / NOT FINAL', fill='black')
        comparisons.append(pair)
        alpha = np.asarray(frame.getchannel('A')) > 8
        frame_audit.append({'frame': index, 'source_frame': source_frame,
                            'source_bbox': entry['bbox'], 'packing_translation': [x - entry['bbox'][0], y - entry['bbox'][1]],
                            'visible_pixels': int(alpha.sum()),
                            'edge_touch': bool(alpha[0].any() or alpha[-1].any() or alpha[:, 0].any() or alpha[:, -1].any())})
    ids = plan['source_frames']
    timestamps = [round(frame * 100 / plan['source_fps']) * 10 for frame in ids]
    durations = [timestamps[i + 1] - timestamps[i] for i in range(len(ids) - 1)] + [700]
    slow = [duration * 3 for duration in durations[:-1]] + [1000]
    save_one_shot(root / 'no-cloak-attack-one-shot.gif', beauty, durations)
    save_one_shot(root / 'no-cloak-attack-slow.gif', beauty, slow)
    save_one_shot(root / 'guide-vs-paint-slow.gif', comparisons, slow)
    sheet = Image.new('RGB', (4 * size, 4 * (size + 24)), '#ececec')
    draw = ImageDraw.Draw(sheet)
    for index, frame in enumerate(beauty):
        x, y = index % 4 * size, index // 4 * (size + 24)
        sheet.paste(frame, (x, y + 24))
        draw.text((x + 8, y + 6), f'{index:02d} / source {ids[index]:03d}', fill='black')
    sheet.save(root / 'paint-contact.png')
    audit = {'status': 'OWNER_REVIEW_ONLY_NOT_PRODUCTION_APPROVED',
             'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
             'source_sheet_size': list(raw.size), 'frame_count': len(beauty),
             'output_frame_size': [size, size],
             'normalization': 'complete connected figures; native painted pixel scale shared by all frames; common horizontal slot offsets and four documented row packing translations; no independent figure fitting, deformation, duplication or temporal interpolation',
             'row_packing_baselines_raw_px': row_baselines,
             'row_packing_target_baseline_px': 432,
             'matte': matte, 'durations_ms': durations, 'slow_durations_ms': slow,
             'playback': 'one-shot with recovery hold; no loop/reset extension',
             'limitations': ['Sixteen painted poses sample a sixty-pose source; this is not sixty separately painted poses.', 'Generated sheet row packing required four common row translations; this is not proven source root registration.', 'Source blade and body landmark agreement still require visual review.', 'No WeaponLight overlay: painted blade registration is unapproved.', 'Full-character frames are not independently interchangeable equipment.'],
             'frames': frame_audit}
    (root / 'assembly-audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    for name in ['no-cloak-attack-one-shot.gif', 'no-cloak-attack-slow.gif', 'guide-vs-paint-slow.gif']:
        gif = Image.open(root / name)
        if gif.n_frames != len(beauty) or 'loop' in gif.info:
            raise ValueError(f'Unexpected frame count or loop extension: {name}')
    print(json.dumps({'frames': len(beauty), 'edge_touch_frames': [f['frame'] for f in frame_audit if f['edge_touch']], 'loop_extension': False}))


if __name__ == '__main__':
    main()
