"""Reproduce the exact reference canvases used for the Walk paint experiments."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw
from review_swordsman_walk_locked_guides import canonical_cells, CROP, KEYS


def build(guide_folder, key_sheet, output):
    if output.exists() or output.is_symlink():
        raise ValueError('Choose a fresh output')
    manifest = json.loads((guide_folder / 'manifest.json').read_text())
    if manifest['job']['source_actions'] != ['Walk'] or manifest['frame_count'] != 16:
        raise ValueError('Unexpected source capture')
    records = manifest['views']['SW']['frames']
    guides = {}
    for index in range(16):
        with Image.open(guide_folder / 'SW' / f'{index:03}.png') as image:
            if image.size != (1536, 1536):
                raise ValueError('Unexpected source camera canvas')
            guides[index] = image.convert('RGBA')
    output.mkdir(parents=True)
    for count, indices, cell, name in ((4, KEYS, 768, 'guide-keyposes.png'),
                                        (16, range(16), 384, 'full-guide-contact.png')):
        columns = 2 if count == 4 else 4
        sheet = Image.new('RGBA', (1536, 1536), 'white')
        for n, index in enumerate(indices):
            image = guides[index].crop(CROP).resize((cell, cell), Image.Resampling.LANCZOS)
            sheet.alpha_composite(image, ((n % columns) * cell, (n // columns) * cell))
        sheet.convert('RGB').save(output / name)
    marked = Image.open(output / 'guide-keyposes.png').convert('RGB')
    draw = ImageDraw.Draw(marked)
    for n, index in enumerate(KEYS):
        record = records[index]
        for name, color in (('foot_r', '#0077ff'), ('foot_l', '#00ad32'), ('hand_l', '#c900d4')):
            sx, sy = record['landmarks'][name]
            x = n % 2 * 768 + (sx - 420) * 768 / 696
            y = n // 2 * 768 + (sy - 520) * 768 / 696
            draw.ellipse((x - 10, y - 10, x + 10, y + 10), outline=color, width=4)
            draw.text((x + 12, y - 12), name, fill=color, stroke_width=1, stroke_fill='white')
        for name in ('grip', 'tip'):
            sx, sy = record['weapon_guide'][name]
            x = n % 2 * 768 + (sx - 420) * 768 / 696
            y = n // 2 * 768 + (sy - 520) * 768 / 696
            draw.ellipse((x - 8, y - 8, x + 8, y + 8), outline='#ef002b', width=3)
    marked.save(output / 'guide-keyposes-controls.png')
    key_frames, _ = canonical_cells(key_sheet, 2)
    crop = (224, 288, 544, 608)
    key_frames[3].crop(crop).resize((1280, 1280), Image.Resampling.LANCZOS).save(output / 'frame12-art-crop.png')
    guide = guides[12].resize((768, 768), Image.Resampling.LANCZOS).crop(crop).resize((1280, 1280), Image.Resampling.LANCZOS)
    background = Image.new('RGBA', guide.size, 'white')
    background.alpha_composite(guide)
    background.convert('RGB').save(output / 'frame12-guide-crop.png')
    draw = ImageDraw.Draw(background)
    for name, color in (('foot_r', '#0077ff'), ('foot_l', '#00ad32')):
        sx, sy = records[12]['landmarks'][name]
        x, y = (sx / 2 - 224) * 4, (sy / 2 - 288) * 4
        draw.ellipse((x - 20, y - 20, x + 20, y + 20), outline=color, width=6)
        draw.text((x + 22, y), name, fill=color, stroke_width=1, stroke_fill='white')
    background.convert('RGB').save(output / 'frame12-guide-controls.png')
    with Image.open(key_sheet) as image:
        weapon_targets = image.convert('RGBA')
    if weapon_targets.size != (1254, 1254):
        raise ValueError('This recorded experiment uses a 1254px key sheet')
    draw = ImageDraw.Draw(weapon_targets)
    for n, index in enumerate(KEYS):
        points = []
        for name in ('grip', 'tip'):
            sx, sy = records[index]['weapon_guide'][name]
            x, y = n % 2 * 627 + (sx - 420) * 627 / 696, n // 2 * 627 + (sy - 520) * 627 / 696
            points.append((x, y))
            draw.ellipse((x - 6, y - 6, x + 6, y + 6), outline='#ff008a', width=3)
        draw.line(points, fill='#ff008a', width=2)
    weapon_targets.save(output / 'key-weapon-targets.png')
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    receipt = {'status': 'REFERENCE_CANVASES_NOT_ART', 'implementation_sha256': sha(Path(__file__)),
               'guide_manifest_sha256': sha(guide_folder / 'manifest.json'), 'key_sheet_sha256': sha(key_sheet),
               'key_source_indices': list(KEYS), 'source_crop': list(CROP),
               'single_frame_crop_authoring': list(crop), 'single_frame_reference_canvas': [1280, 1280],
               'images_sha256': {p.name: sha(p) for p in sorted(output.glob('*.png'))}}
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guide-folder', type=Path, required=True)
    parser.add_argument('--key-sheet', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = build(args.guide_folder, args.key_sheet, args.output)
    print(json.dumps({'status': result['status'], 'images': len(result['images_sha256'])}))
