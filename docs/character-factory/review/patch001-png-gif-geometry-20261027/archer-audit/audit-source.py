"""Compare decoded GIF geometry to its exact fixed-viewport PNG source.

A palette error is not a translation. Alpha bounds measure all visible art,
including weapons; they must not be presented as anatomical body height.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageChops


def compare(expected, actual):
    a, b = np.asarray(expected.convert('RGB'), dtype=np.int16), np.asarray(actual.convert('RGB'), dtype=np.int16)
    if a.shape != b.shape:
        raise ValueError('Decoded GIF and source dimensions differ')
    errors = []
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            region = b[1+dy:b.shape[0]-1+dy, 1+dx:b.shape[1]-1+dx]
            error = float(np.abs(a[1:-1, 1:-1]-region).mean())
            errors.append((error, dx, dy))
    error, dx, dy = min(errors, key=lambda row: (row[0], abs(row[1])+abs(row[2])))
    return {'best_decode_translation_xy': [dx, dy], 'mean_absolute_palette_error_255': error,
            'zero_translation_error_255': next(e for e, x, y in errors if x == y == 0)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--masters', type=Path, required=True)
    p.add_argument('--previews', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    recipe = json.loads((args.previews/'receipt.json').read_text())['recipe']
    left, top, right, bottom = recipe['viewport']; width, height = right-left, bottom-top
    if args.output.exists():
        raise ValueError('Preserve earlier geometry audits')
    args.output.mkdir(parents=True)
    records = []
    for sex in recipe['identities']:
        gif = Image.open(args.previews/f'{sex}-normal.gif')
        if gif.n_frames != recipe['frame_count']:
            raise ValueError('GIF frame merging requires an explicit frame mapping')
        sheets = {view: Image.new('RGBA', (width*4, height*((gif.n_frames+3)//4))) for view in recipe['directions']}
        for index in range(gif.n_frames):
            gif.seek(index); decoded = gif.convert('RGB')
            if decoded.size != (width*len(recipe['directions']), height+28):
                raise ValueError('GIF layout differs from its fixed-viewport recipe')
            for col, view in enumerate(recipe['directions']):
                source = args.masters/sex/view/'Master'/f'{index:03d}.png'
                master = Image.open(source).convert('RGBA'); cropped = master.crop((left, top, right, bottom))
                expected = Image.new('RGB', cropped.size, '#dcdcd8'); expected.paste(cropped, (0, 0), cropped)
                actual = decoded.crop((col*width, 28, (col+1)*width, 28+height))
                result = compare(expected, actual)
                opaque = master.getchannel('A').point(lambda v: 255 if v > 245 else 0).getbbox()
                records.append({'identity': sex, 'view': view, 'index': index,
                                'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                                'opaque_art_bbox': opaque, 'viewport_clips_visible_pixels':
                                ImageChops.difference(master.getchannel('A'),
                                  Image.fromarray(np.pad(np.asarray(cropped.getchannel('A')), ((top,master.height-bottom),(left,master.width-right))))).getbbox() is not None,
                                'opaque_art_height_includes_weapon': opaque[3]-opaque[1],
                                'gif_duration_ms': gif.info['duration'], **result})
                sheets[view].paste(cropped, ((index%4)*width, (index//4)*height))
        for view, sheet in sheets.items():
            sheet.save(args.output/f'{sex}-{view}-native.png')
    report = {'status': 'SOURCE_VS_GIF_GEOMETRY_DIAGNOSTIC_NOT_ART_ACCEPTANCE',
              'recipe': recipe, 'frames': records, 'all_decode_best_offsets_zero': all(r['best_decode_translation_xy']==[0,0] for r in records),
              'clipped_viewport_frames': sum(r['viewport_clips_visible_pixels'] for r in records),
              'anatomical_body_height_measured': False,
              'note': 'Native sprite geometry is unchanged by PNG playback. Palette/timing can affect appearance. Foreground bounds include staff, arms, coat, and are not body-height approval.'}
    (args.output/'geometry-audit.json').write_text(json.dumps(report, indent=2)+'\n')
    (args.output/'audit-source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({k:report[k] for k in ['all_decode_best_offsets_zero','clipped_viewport_frames']}))


if __name__ == '__main__':
    main()
