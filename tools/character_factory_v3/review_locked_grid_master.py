"""Inspect a complete paintover against a locked guide without fitting frames.

All poses use the same source crop and canvas transform. Outputs are candidates;
this tool cannot approve anatomy, planted contacts, equipment or gameplay.
"""
import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def on_background(image, color):
    background = Image.new('RGBA', image.size, color)
    background.alpha_composite(image)
    return background.convert('RGB')


def native_duration(manifest, guide_path):
    root = Path(__file__).resolve().parents[2]
    job = manifest['job']
    if not job['loop'] or len(job['source_actions']) != 1:
        raise ValueError('Explicit review timing required for this action')
    source = root / job['source_file']
    if sha(source) != job['source_sha256']:
        raise ValueError('Source motion hash changed')
    raw = source.read_bytes()
    if struct.unpack_from('<III', raw) != (0x46546c67, 2, len(raw)):
        raise ValueError('Expected complete GLB')
    length, kind = struct.unpack_from('<II', raw, 12)
    if kind != 0x4e4f534a:
        raise ValueError('Expected GLB JSON chunk')
    doc = json.loads(raw[20:20 + length])
    animation = next(a for a in doc['animations'] if a['name'] == job['source_actions'][0])
    begin = min(doc['accessors'][s['input']]['min'][0] for s in animation['samplers'])
    end = max(doc['accessors'][s['input']]['max'][0] for s in animation['samplers'])
    count = manifest['frame_count']
    # The pinned guide renderer uses 24fps scene coordinates. Verify each actual
    # sample rather than assuming that sixteen slots mean sixteen source frames.
    for i, frame in enumerate(manifest['views']['SW']['frames']):
        expected = (begin + (end - begin) * i / count) * 24
        if abs(expected - frame['source_frame']) > 1e-4:
            raise ValueError('Guide timing differs; specify reviewed timing explicitly')
    return (end - begin) * 1000 / count


def build(sheet_path, guide_path, output, duration_ms):
    if output.exists() or output.is_symlink():
        raise ValueError('Fresh review output required')
    manifest = json.loads(guide_path.read_text())
    if manifest['frame_count'] != 16 or 'SW' not in manifest['views']:
        raise ValueError('Expected sixteen actual SW source poses')
    timing_basis = 'explicit diagnostic frame duration'
    if duration_ms is None:
        duration_ms = native_duration(manifest, guide_path)
        timing_basis = 'native GLB seconds; all guide samples verified at renderer 24fps'
    with Image.open(sheet_path) as source:
        if source.mode != 'RGBA' or source.width != source.height:
            raise ValueError('Expected square RGBA 4x4 paintover')
        source = source.copy()
    output.mkdir(parents=True)
    (output / 'masters').mkdir()
    frames, panels, rows = [], [], []
    # This is one fixed crop of the original 1536 guide, halved to authoring.
    crop = (420, 520, 1116, 1216)
    destination = (210, 260)
    tile_size = 348
    step = source.width / 4
    for index in range(16):
        box = (index % 4 * step, index // 4 * step,
               (index % 4 + 1) * step, (index // 4 + 1) * step)
        tile = source.transform((tile_size, tile_size), Image.Transform.EXTENT,
                                box, Image.Resampling.BICUBIC)
        master = Image.new('RGBA', (768, 768))
        master.alpha_composite(tile, destination)
        path = output / 'masters' / f'{index:03}.png'
        master.save(path)
        alpha = np.asarray(master.getchannel('A'))
        y, x = np.where(alpha >= 128)
        if not len(x):
            raise ValueError('Empty painted pose')
        bbox = [int(x.min()), int(y.min()), int(x.max() + 1), int(y.max() + 1)]
        rows.append({'frame': index, 'source_frame': manifest['views']['SW']['frames'][index]['source_frame'],
                     'bbox_alpha128': bbox, 'foreground_height_authoring_px': bbox[3] - bbox[1],
                     'master_sha256': sha(path), 'alpha_touches_canvas': bool(
                         alpha[0].any() or alpha[-1].any() or alpha[:, 0].any() or alpha[:, -1].any())})
        painted = on_background(master, '#c9c9c9').resize((512, 512), Image.Resampling.LANCZOS)
        frames.append(painted)
        guide = Image.open(guide_path.parent / 'SW' / f'{index:03}.png').convert('RGBA')
        guide = on_background(guide, '#c9c9c9').resize((512, 512), Image.Resampling.LANCZOS)
        panel = Image.new('RGB', (1024, 544), '#e8e8e8')
        panel.paste(guide, (0, 32)); panel.paste(painted, (512, 32))
        draw = ImageDraw.Draw(panel)
        draw.text((8, 8), f'Native Mesh2Motion Walk SW {index:02}', fill='black')
        draw.text((520, 8), 'Whole painted master - acceptance pending', fill='black')
        panels.append(panel)
        if index in (0, 3, 8, 15):
            panel.save(output / f'key{index:02}.png')
    gif_durations = {}
    for name, images, duration in [('normal.gif', frames, duration_ms),
                                    ('slow.gif', frames, duration_ms * 3),
                                    ('guide-comparison.gif', panels, duration_ms * 3)]:
        # Distribute centisecond rounding over the whole cycle; PIL would
        # otherwise truncate every frame independently and speed up playback.
        durations = [(round((i+1)*duration/10)-round(i*duration/10))*10 for i in range(16)]
        images[0].save(output / name, save_all=True, append_images=images[1:],
                       duration=durations, loop=0, optimize=False)
        gif_durations[name] = durations
    backgrounds = Image.new('RGB', (1536, 512))
    first = Image.open(output / 'masters/000.png').convert('RGBA')
    for i, color in enumerate(('#f3f3f3', '#999999', '#132530')):
        backgrounds.paste(on_background(first, color).resize((512, 512), Image.Resampling.LANCZOS), (512 * i, 0))
    backgrounds.save(output / 'alpha-backgrounds.png')
    result = {'status': 'COMPLETE_SW_MASTER_CANDIDATE_NOT_ACCEPTED', 'frames': rows,
              'sheet_size': list(source.size), 'native_tile_size': step,
              'guide_sha256': sha(guide_path), 'sheet_sha256': sha(sheet_path),
              'script_sha256': sha(Path(__file__)), 'authoring_canvas': [768, 768],
              'source_crop': list(crop), 'shared_destination': list(destination),
              'shared_tile_size': tile_size, 'runtime_root': [120, 172],
              'review_frame_ms': duration_ms,
              'timing_basis': timing_basis, 'gif_durations_ms': gif_durations,
              'limitations': ['Native source tiles are not integer-sized; a single shared fractional-grid transform is used.',
                             'Canvas enlargement does not add painted detail.',
                             'Bounding boxes include hair, cloth and weapon; they are not anatomical or contact measurements.',
                             'Native motion timing is not a gameplay walk-speed or stride-distance contract.',
                             'No per-frame scale, registration, limb deformation or frozen part is used.',
                             'Semantic cutouts, verified contacts, loop continuity, other directions and gameplay remain pending.']}
    (output / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'frames': len(rows), 'clipped_frames': sum(r['alpha_touches_canvas'] for r in rows),
                      'native_tile_size': step, 'status': result['status']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sheet', type=Path, required=True)
    parser.add_argument('--guide', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--frame-ms', type=float)
    args = parser.parse_args()
    if args.frame_ms is not None and (not math.isfinite(args.frame_ms) or not 10 <= args.frame_ms <= 1000):
        parser.error('Review frame duration outside bounded range')
    build(args.sheet, args.guide, args.output, args.frame_ms)
