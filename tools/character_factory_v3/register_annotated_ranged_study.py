"""Register every same-frame part with one explicitly observed body anchor.

No deformation, per-part fitting or motion approval. Manual observations and
rounding are retained; source-guide agreement beyond the anchor stays open.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def anchor_translation(observation, annotation, source_row):
    """Apply the same rigid placement to every part; never infer an anatomy fit."""
    observed_key = annotation.get('observed_anchor', 'ankle')
    source_key = annotation.get('source_anchor', 'foot_l')
    observed = np.asarray(observation[observed_key], dtype=float)
    offset = np.asarray(annotation['paint_cell_offset'], dtype=float)
    target = np.asarray(source_row['landmarks'][source_key], dtype=float)
    if observed.shape != (2,) or target.shape != (2,) or offset.shape != (2,):
        raise ValueError('Anchors and offsets must be two dimensional')
    scale = float(annotation['paint_cell_scale'])
    projection_scale = float(annotation.get('source_projection_scale', .5))
    if not np.isfinite([*observed, *target, *offset, scale, projection_scale]).all():
        raise ValueError('Anchor values must be finite')
    if scale <= 0 or projection_scale <= 0:
        raise ValueError('Coordinate scales must be positive')
    observed = observed*scale+offset
    target = target*projection_scale
    delta = np.rint(target-observed).astype(int)
    return observed, target, delta


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['masters', 'parts', 'guide', 'annotations', 'output']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Preserve earlier registrations')
    annotation = json.loads(args.annotations.read_text())
    guide = json.loads(args.guide.read_text())
    direction = annotation['direction']
    source_rows = guide['views'][direction]['frames']
    args.output.mkdir(parents=True)
    records = []
    previews = []
    sheet_frames = {role: [] for role in ['Master', 'BodyCostume', 'HeadHair', 'Weapon']}
    for observation in annotation['frames']:
        i = observation['index']
        observed, target, delta = anchor_translation(observation, annotation, source_rows[i])
        images = {'Master': Image.open(args.masters/f'{i:03d}.png').convert('RGBA')}
        images.update({role: Image.open(args.parts/role/f'{i:03d}.png').convert('RGBA')
                       for role in ['BodyCostume', 'HeadHair', 'Weapon']})
        outputs = {}
        for role, image in images.items():
            output = Image.new('RGBA', (768, 768))
            output.alpha_composite(image, tuple(delta))
            if np.array(output)[:, :, 3].sum() != np.array(image)[:, :, 3].sum():
                raise ValueError('Registration clips source pixels')
            folder = args.output/role
            folder.mkdir(exist_ok=True)
            output.save(folder/f'{i:03d}.png')
            outputs[role] = output
            sheet_frames[role].append(output)
        merged = Image.new('RGBA', (768, 768))
        for role in ['BodyCostume', 'HeadHair', 'Weapon']:
            merged.alpha_composite(outputs[role])
        if merged.tobytes() != outputs['Master'].tobytes():
            raise ValueError('Registration changed part reconstruction')
        background = Image.new('RGBA', (768, 768), '#dbdbd8')
        background.alpha_composite(merged)
        # Fixed review crop for all frames, not an asset fitting operation.
        preview = background.crop((260, 250, 530, 600)).convert('RGB')
        ImageDraw.Draw(preview).text((5, 5), f'{direction} / {i:02d} / DRAFT', fill='black')
        previews.append(preview)
        records.append({'index': i, 'translation': delta.tolist(),
                        'observed_anchor': observed.tolist(), 'source_anchor': target.tolist(),
                        'rounding_residual_px': float(np.linalg.norm(observed+delta-target)),
                        'master_input_sha256': sha(args.masters/f'{i:03d}.png'),
                        'master_output_sha256': sha(args.output/'Master'/f'{i:03d}.png'),
                        'recomposition_mismatches': 0})
    for name, multiplier in [('normal.gif', 1), ('slow.gif', 3)]:
        duration = [80*multiplier]*(len(previews)-1)+[240*multiplier]
        previews[0].save(args.output/name, save_all=True, append_images=previews[1:],
                         duration=duration, loop=0, disposal=2)
    sheets = {}
    sheet_directory = args.output/'Sheets'
    sheet_directory.mkdir()
    for role, frames in sheet_frames.items():
        rows = (len(frames)+3)//4
        sheet = Image.new('RGBA', (768*4, 768*rows))
        for slot, frame in enumerate(frames):
            # Copy RGBA pixels, including partial alpha, without blending twice.
            sheet.paste(frame, ((slot % 4)*768, (slot//4)*768))
        sheet_path = sheet_directory/f'{role}.png'
        sheet.save(sheet_path)
        sheets[role] = {'path': str(sheet_path.relative_to(args.output)),
                        'sha256': sha(sheet_path), 'columns': 4, 'rows': rows,
                        'frame_size': [768, 768], 'frame_count': len(frames)}
    first = np.array(Image.open(args.output/'Master/000.png'))
    last = np.array(Image.open(args.output/'Master'/f'{len(previews)-1:03d}.png'))
    receipt = {'status': 'WHOLE_POSE_REGISTERED_STUDY_NOT_SMOOTHNESS_OR_SEMANTIC_APPROVAL',
               'direction': direction, 'frames': records,
               'guide_sha256': sha(args.guide), 'annotations_sha256': sha(args.annotations),
               'implementation_sha256': sha(Path(__file__)),
               'observed_anchor': annotation.get('observed_anchor', 'ankle'),
               'source_anchor': annotation.get('source_anchor', 'foot_l'),
               'source_projection_scale': annotation.get('source_projection_scale', .5), 'canvas': [768, 768],
               'per_part_translation': False, 'pose_deformation': False,
               'endpoint_master_changed_pixels': int(np.any(first != last, axis=2).sum()),
               'sprite_sheets': sheets,
               'preview_note': 'GIF repeats a one-shot action for inspection; not a certified seamless loop.',
               'source_pose_registered': False, 'runtime_admitted': False}
    (args.output/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    (args.output/'annotations-source.json').write_bytes(args.annotations.read_bytes())
    (args.output/'registration-source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({'frames': len(records), 'endpoint_changed_pixels': receipt['endpoint_master_changed_pixels']}))


if __name__ == '__main__':
    main()
