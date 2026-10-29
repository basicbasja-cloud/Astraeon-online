"""Review a draft SW walk loop and its locked guide using fixed whole-sheet scaling."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'authoring/characters/factory-v3/patch-0.0.1/painted-candidates/swordsman-male-walk-sw-fixed-crop-20261029'


def read_tiles(path):
    # Resize the complete sheet once, never independently fit its frames.
    with Image.open(path) as original:
        sheet = original.convert('RGB').resize((1536, 1536), Image.Resampling.LANCZOS)
    return [sheet.crop(((i % 4) * 384, (i // 4) * 384,
                        (i % 4 + 1) * 384, (i // 4 + 1) * 384)) for i in range(16)]


def difference(a, b):
    a = np.asarray(a, dtype=np.int16)
    b = np.asarray(b, dtype=np.int16)
    # Foreground union deliberately includes sword/costume and is only a warning.
    fg = (np.min(a, axis=2) < 230) | (np.min(b, axis=2) < 230)
    if not np.any(fg):
        raise ValueError('Empty comparison')
    return float(np.abs(a - b).mean(axis=2)[fg].mean()), int(fg.sum())


def build(output):
    if output.exists() or output.is_symlink():
        raise ValueError('Choose fresh output')
    inputs = [SOURCE / 'guide-contact.png', SOURCE / 'generated-sheet.png']
    sheets = [read_tiles(p) for p in inputs]
    comparisons = []
    for i in range(16):
        j = (i + 1) % 16
        row = {'from': i, 'to': j}
        for kind, tiles in zip(('guide', 'draft'), sheets):
            mean, area = difference(tiles[i], tiles[j])
            row[kind] = {'union_mean_rgb_delta': round(mean, 3), 'foreground_union_px': area}
        comparisons.append(row)
    output.mkdir(parents=True)
    images = []
    # Make both fixed-frame loop and same-frame guide comparison available.
    for i in range(16):
        canvas = Image.new('RGB', (768, 416), 'white')
        canvas.paste(sheets[0][i], (0, 32))
        canvas.paste(sheets[1][i], (384, 32))
        draw = ImageDraw.Draw(canvas)
        draw.text((4, 7), f'GUIDE SW WALK {i:02}', fill='black')
        draw.text((388, 7), f'DRAFT SW WALK {i:02} — NOT APPROVED', fill='black')
        images.append(canvas)
    for name, duration in [('normal.gif', 85), ('slow.gif', 200)]:
        images[0].save(output / name, save_all=True, append_images=images[1:], duration=duration, loop=0, optimize=False)
    # Compare the loop seam and adjacent steps on the same fixed pixel grid.
    board = Image.new('RGB', (1152, 832), 'white')
    draw = ImageDraw.Draw(board)
    for row, tiles in enumerate(sheets):
        for col, index in enumerate((15, 0, 1)):
            x, y = col * 384, row * 416
            board.paste(tiles[index], (x, y + 32))
            draw.text((x + 4, y + 7), f'{"guide" if row == 0 else "draft"} {index:02}', fill='black')
    board.save(output / 'loop-seam.png')
    receipt = {'status': 'DRAFT_NOT_ACCEPTED', 'measurements': comparisons,
               'input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
               'limitations': ['Pixel differences include texture, limb movement, sword, and generated changes; they cannot identify anatomical drift.',
                               'The guide crop is a review crop, not the authoring or runtime canvas.',
                               'Contact, grip, temporal continuity, exact alpha and in-game behavior require further review.']}
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    print(json.dumps(build(parser.parse_args().output)))
