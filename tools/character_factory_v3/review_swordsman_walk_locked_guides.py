"""Compare saved whole-sheet paintings with a replayed native Walk source.

One fixed crop transform maps every painting cell back to the canonical camera.
No measured foreground bounds, painted joints or desired score affect the fit.
Source bone origins are displayed as controls, not certified painted landmarks.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
CROP = (420, 520, 1116, 1216)
INSPECT = (176, 224, 592, 640)
KEYS = (0, 4, 8, 12)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_cells(path, columns):
    with Image.open(path) as image:
        if image.mode != 'RGBA' or image.width != image.height or image.getextrema()[3][0] == 255:
            raise ValueError('Expected a square RGBA painting with actual transparency')
        source = image.convert('RGBa')
    cell = source.width / columns
    result = []
    for index in range(columns * columns):
        col, row = index % columns, index // columns
        box = (col * cell, row * cell, (col + 1) * cell, (row + 1) * cell)
        # The 696-source-pixel crop occupies 348px of a 768px camera canvas.
        tile = source.transform((348, 348), Image.Transform.EXTENT, box,
                                Image.Resampling.BICUBIC).convert('RGBA')
        frame = Image.new('RGBA', (768, 768))
        frame.paste(tile, (210, 260))
        result.append(frame)
    return result, {'native_sheet_size': list(source.size), 'native_cell_extent': cell,
                    'common_cell_to_authoring_scale': 348 / cell,
                    'authoring_crop_origin': [210, 260],
                    'canonical_authoring_canvas': [768, 768],
                    'per_frame_fitting': False}


def flat(image, color='#ededed'):
    result = Image.new('RGBA', image.size, color)
    result.alpha_composite(image)
    return result.convert('RGB')


def controls(image, record):
    result = image.copy()
    draw = ImageDraw.Draw(result)
    points = {k: (v[0] / 2, v[1] / 2) for k, v in record['landmarks'].items()}
    for a, b in (('head', 'pelvis'), ('pelvis', 'foot_r'), ('pelvis', 'foot_l'),
                 ('pelvis', 'hand_r'), ('pelvis', 'hand_l')):
        draw.line((points[a], points[b]), fill='#00a8b5', width=1)
    for name, (x, y) in points.items():
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), outline='#00b8c8', width=2)
        draw.text((x + 4, y), name, fill='#006474')
    weapon = {k: (v[0] / 2, v[1] / 2) for k, v in record['weapon_guide'].items()}
    draw.line((weapon['grip'], weapon['tip']), fill='#d900bd', width=2)
    for name, (x, y) in weapon.items():
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), outline='#d900bd', width=2)
    return result


def panel(guide, painting, record, label):
    result = Image.new('RGB', (1248, 448), '#ededed')
    draw = ImageDraw.Draw(result)
    images = (flat(guide), flat(painting), controls(flat(painting), record))
    names = ('REPLAYED GUIDE', label, 'SOURCE BONE ORIGINS / PROP')
    for col, (image, name) in enumerate(zip(images, names)):
        result.paste(image.crop(INSPECT), (col * 416, 32))
        draw.text((col * 416 + 6, 8), f'SW/{record["frame"]:02} {name}', fill='black')
    return result


def loop_gif(frames, path, interval_ms):
    # Round cumulative sample times, avoiding systematic cadence shortening.
    durations = [round((i + 1) * interval_ms / 10) * 10 - round(i * interval_ms / 10) * 10
                 for i in range(len(frames))]
    montage = Image.new('RGB', (frames[0].width * 4, frames[0].height * ((len(frames) + 3) // 4)))
    for i, frame in enumerate(frames):
        montage.paste(frame, ((i % 4) * frame.width, (i // 4) * frame.height))
    palette = montage.quantize(colors=255)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=durations,
                    loop=0, optimize=False, disposal=2)
    return durations


def build(guide_folder, full_sheet, key_sheet, output):
    if output.exists() or output.is_symlink():
        raise ValueError('Choose a fresh output')
    manifest_path = guide_folder / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    job = manifest['job']
    if job['source_actions'] != ['Walk'] or job['frames'] != 16 or not job['loop']:
        raise ValueError('Unexpected Walk source job')
    from patch001_factory import receipt_valid
    if not receipt_valid(job, guide_folder):
        raise ValueError('Incomplete or mismatched eight-view guide replay')
    if sha(ROOT / job['source_file']) != job['source_sha256']:
        raise ValueError('Source GLB digest changed')
    guides = []
    hashes = {'guide_manifest': sha(manifest_path), 'full_sheet': sha(full_sheet), 'key_sheet': sha(key_sheet)}
    for index in range(16):
        path = guide_folder / 'SW' / f'{index:03}.png'
        with Image.open(path) as source:
            guides.append(source.convert('RGBA').resize((768, 768), Image.Resampling.LANCZOS))
        hashes[f'SW/{index:03}.png'] = sha(path)
    paintings, full_fit = canonical_cells(full_sheet, 4)
    keys, key_fit = canonical_cells(key_sheet, 2)
    records = manifest['views']['SW']['frames']
    step = records[1]['source_frame'] - records[0]['source_frame']
    if any(abs((b['source_frame'] - a['source_frame']) - step) > 1e-6
           for a, b in zip(records, records[1:])):
        raise ValueError('Nonuniform source sampling requires explicit timing')
    # The renderer fixes its source evaluation at 24fps; preserve that cadence.
    interval_ms = step * 1000 / 24
    full_panels = [panel(guide, painting, record, '16-POSE DRAFT / NOT APPROVED')
                   for guide, painting, record in zip(guides, paintings, records)]
    key_panels = [panel(guides[i], painting, records[i], 'KEY DRAFT / NOT APPROVED')
                  for i, painting in zip(KEYS, keys)]
    output.mkdir(parents=True)
    for index, image in enumerate(full_panels):
        image.save(output / f'full-{index:02}.png')
    for index, image in zip(KEYS, key_panels):
        image.save(output / f'key-{index:02}.png')
    timings = loop_gif(full_panels, output / 'full-normal.gif', interval_ms)
    loop_gif(full_panels, output / 'full-slow.gif', interval_ms * 3)
    loop_gif(key_panels, output / 'key-sampling.gif', interval_ms * 4)
    for index, image in enumerate(paintings):
        (output / 'draft-authoring').mkdir(exist_ok=True)
        image.save(output / 'draft-authoring' / f'{index:03}.png')
    for index, image in zip(KEYS, keys):
        (output / 'key-authoring').mkdir(exist_ok=True)
        image.save(output / 'key-authoring' / f'{index:03}.png')
    result = {
        'status': 'LOCKED_CAMERA_SOURCE_COMPARISON_NOT_POSE_APPROVAL',
        'implementation_sha256': sha(Path(__file__)), 'source_inputs_sha256': hashes,
        'source_job_id': job['id'], 'source_glb_sha256': job['source_sha256'],
        'replayed_guide_coverage': {'views': list(manifest['views']), 'frames_per_view': 16},
        'source_rig': manifest['source_rig'], 'camera': manifest['views']['SW']['camera'],
        'source_crop': list(CROP), 'inspection_crop_authoring_px': list(INSPECT),
        'full_sheet_fit': full_fit, 'key_sheet_fit': key_fit,
        'full_source_indices': list(range(16)), 'key_source_indices': list(KEYS),
        'source_frames': [r['source_frame'] for r in records], 'source_fps': 24,
        'full_gif_durations_ms': timings, 'full_gif_cycle_ms': sum(timings),
        'key_gif_is_sparse_pose_review_not_finished_walk': True,
        'complete_character_increment': 0, 'runtime_admitted': False,
        'limitations': [
            'Source head is the head-bone origin, not an annotated painted crown or face center.',
            'Foot bone origins are not certified sole contacts; hidden painted landmarks remain unresolved.',
            'This tool displays source controls; it does not infer or score painted joint positions.',
            'Full-sheet cell pixels are slightly enlarged; native source detail is not 768px per frame.',
            'The 4-key sheet has sufficient native pixel density but does not supply the twelve in-between poses.',
            'Inspection crops are diagnostic crops; exported draft frames retain the full locked 768px canvas.',
        ],
    }
    (output / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guide-folder', type=Path, required=True)
    parser.add_argument('--full-sheet', type=Path, required=True)
    parser.add_argument('--key-sheet', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.guide_folder, args.full_sheet, args.key_sheet, args.output)
    print(json.dumps({'status': result['status'], 'full_cycle_ms': result['full_gif_cycle_ms']}))
