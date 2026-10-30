"""Render an inspectable contact sheet; markers are annotations, not validation."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/basic-attack-simple'

def render(output):
    if output.exists() or output.is_symlink():
        raise ValueError('choose a fresh output')
    sheet = Image.new('RGB', (1280, 1120), '#e0e0e0')
    draw = ImageDraw.Draw(sheet)
    for row, direction in enumerate(('SW', 'NW', 'NE', 'SE')):
        annotations = json.loads((SOURCE / direction / 'annotations.generated.json').read_text())['frames']
        for col, frame in enumerate((5, 6, 7, 8, 9)):
            with Image.open(SOURCE / direction / 'Master' / f'{frame:03}.png') as source:
                image = source.convert('RGBA').resize((256, 256), Image.Resampling.LANCZOS)
            x, y = col * 256, row * 280 + 24
            sheet.paste(image, (x, y), image)
            for name, color in (('weapon_grip', 'red'), ('weapon_tip', 'cyan')):
                px, py = annotations[frame][name]
                px, py = x + px / 2, y + py / 2
                draw.ellipse((px - 4, py - 4, px + 4, py + 4), outline=color, width=2)
            draw.text((x + 3, y - 20), f'{direction} frame {frame}  red grip / cyan tip', fill='black')
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    render(parser.parse_args().output)
