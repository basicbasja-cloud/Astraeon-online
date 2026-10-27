"""Review saved masters against an evaluated, camera-matched source skeleton.

Writes diagnostic images only. It never registers, rescales, or edits a master.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
from PIL import Image, ImageDraw


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def project(point, camera, size=768):
    x, y, z = camera['rotation']
    rx = np.array([[1, 0, 0], [0, math.cos(x), -math.sin(x)], [0, math.sin(x), math.cos(x)]])
    ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    rz = np.array([[math.cos(z), -math.sin(z), 0], [math.sin(z), math.cos(z), 0], [0, 0, 1]])
    rotation = rz @ ry @ rx
    relative = np.asarray(point) - camera['location']
    return np.array([size / 2 + relative @ rotation[:, 0] * size / camera['ortho_scale'],
                     size / 2 - relative @ rotation[:, 1] * size / camera['ortho_scale']])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ['capture', 'skeleton', 'masters', 'output']:
        parser.add_argument('--' + flag, type=Path, required=True)
    parser.add_argument('--direction', default='SW')
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Use a fresh review output')
    manifest_path = args.capture / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    skeleton = json.loads(args.skeleton.read_text())
    view = manifest['views'][args.direction]
    frames = skeleton['frames']
    if len(frames) != len(view['frames']):
        raise ValueError('Source sequence length mismatch')
    if digest(manifest_path) != skeleton['source_manifest_sha256']:
        raise ValueError('Skeleton belongs to another capture manifest')
    records = []
    for frame, metadata in zip(frames, view['frames']):
        if frame['index'] != metadata['frame']:
            raise ValueError('Source pose index mismatch')
        points = {name: project(bone['head'], view['camera']) for name, bone in frame['bones'].items()}
        errors = {name: float(np.linalg.norm(points[name] - np.asarray(metadata['landmarks'][name]) / 2))
                  for name in ['head', 'pelvis', 'hand_r', 'hand_l', 'foot_r', 'foot_l']}
        if max(errors.values()) > .02:
            raise ValueError(f'Camera/source projection mismatch: {errors}')
        master_path = args.masters / f"{frame['index']:03d}.png"
        if Image.open(master_path).size != (768, 768):
            raise ValueError('Expected canonical authoring canvas')
        records.append({'index': frame['index'], 'master_sha256': digest(master_path),
                        'source_projection_error_author768': errors,
                        'joints_author768': {name: point.tolist() for name, point in points.items()}})
    args.output.mkdir(parents=True)
    (args.output / 'Overlays').mkdir()
    preview = []
    contact = Image.new('RGB', (384 * 6, 384 * math.ceil(len(frames) / 6)), '#ddd')
    chains = [['head', 'neck_01', 'spine_03', 'spine_02', 'spine_01', 'pelvis'],
              ['upperarm_r', 'lowerarm_r', 'hand_r'], ['upperarm_l', 'lowerarm_l', 'hand_l'],
              ['pelvis', 'thigh_r', 'calf_r', 'foot_r'], ['pelvis', 'thigh_l', 'calf_l', 'foot_l']]
    for record in records:
        index = record['index']
        master = Image.open(args.masters / f'{index:03d}.png').convert('RGBA')
        source = Image.open(args.capture / args.direction / f'{index:03d}.png').convert('RGBA').resize((768, 768), Image.Resampling.LANCZOS)
        overlay = master.copy()
        draw = ImageDraw.Draw(overlay)
        points = record['joints_author768']
        for chain, color in zip(chains, ['#00aaff', '#ff3020', '#aa36ff', '#ff3020', '#aa36ff']):
            coordinates = [tuple(points[name]) for name in chain]
            draw.line(coordinates, fill=color, width=1)
            for x, y in coordinates:
                draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=color)
        overlay.save(args.output / 'Overlays' / f'{index:03d}.png')
        contact_tile = Image.new('RGBA', (384, 384), '#ddd')
        contact_tile.alpha_composite(overlay.crop((192, 256, 576, 640)))
        ImageDraw.Draw(contact_tile).text((5, 5), f'{index}: source joints; art NOT accepted', fill='black')
        contact.paste(contact_tile.convert('RGB'), ((index % 6) * 384, (index // 6) * 384))
        tile = Image.new('RGBA', (1152, 408), '#ddd')
        for column, image in enumerate([source, master, overlay]):
            tile.alpha_composite(image.crop((192, 232, 576, 616)), (column * 384, 24))
        draw = ImageDraw.Draw(tile)
        for column, label in enumerate(['Actual Blender guide', 'Own-frame master — draft', 'Source joints over master']):
            draw.text((column * 384 + 5, 5), f'{index:02d} {label}', fill='black')
        preview.append(tile.convert('RGB'))
    contact.save(args.output / 'joint-contact.jpg', quality=97)
    durations = [(round((i + 1) * 100 / 24) - round(i * 100 / 24)) * 10 for i in range(len(preview))]
    for name, factor in [('normal', 1), ('slow', 3)]:
        timing = [d * factor for d in durations]
        timing[-1] += 200
        preview[0].save(args.output / f'{name}.gif', save_all=True, append_images=preview[1:], duration=timing, loop=0, disposal=2, optimize=False)
    result = {'status': 'SOURCE_JOINT_DIAGNOSTICS_NOT_ART_ACCEPTANCE', 'frames': records,
              'capture_manifest_sha256': digest(manifest_path), 'skeleton_sha256': digest(args.skeleton),
              'implementation_sha256': digest(__file__), 'master_files_modified': False,
              'new_artwork_or_runtime_coverage': 0,
              'preview_timing': {'source_fps': 24, 'normal_frame_durations_ms': durations,
                                 'review_end_hold_ms': 200, 'restart_is_review_only_not_runtime_transition': True},
              'limitations': 'No painted joint/contact annotation or anatomy acceptance is inferred from source projection checks.'}
    for record in records:
        if digest(args.masters / f"{record['index']:03d}.png") != record['master_sha256']:
            raise ValueError('Master changed during review')
    (args.output / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'frames': len(records), 'source_camera_projection_max_error': max(max(r['source_projection_error_author768'].values()) for r in records), 'masters_modified': False}))


if __name__ == '__main__':
    main()
