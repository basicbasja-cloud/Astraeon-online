#!/usr/bin/env python3
"""Contact-sheet preparation only; original source rasters are immutable."""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'authoring/characters/builds/swordsman-basicattack-anatomy-v1'
PACK = json.loads((ROOT / 'authoring/characters/appearance/swordsman-bodywithoutfit/appearance-pack.json').read_text())
IMAGES = {key: Image.open(ROOT / value['file']).convert('RGBA') for key, value in PACK['atlases'].items() if key in ['body-basicattack', 'head-basicattack']}

def restored(direction, index):
    refs = [(part, layer) for part, layer in [('swordsman-body-default', 'Body'), ('swordsman-head', 'HeadBase')]]
    canvas = Image.new('RGBA', (320, 320))
    for part, layer in refs:
        ref = PACK['parts'][part]['timelines']['BasicAttack'][direction]['frames'][index]['layers'][layer]
        x, y, w, h = ref['rect']
        tile = IMAGES[ref['atlasId']].crop((x, y, x+w, y+h))
        canvas.alpha_composite(tile, tuple(ref.get('trim', {}).get('offset', [0, 0])))
    return canvas

def sheet(direction, indices, name):
    canvas = Image.new('RGBA', (1536, 1024))
    for slot, index in enumerate(indices):
        canvas.alpha_composite(restored(direction, index).resize((512, 512), Image.Resampling.LANCZOS), (slot % 3 * 512, slot // 3 * 512))
    canvas.save(BUILD / name)

if __name__ == '__main__':
    BUILD.mkdir(parents=True, exist_ok=True)
    for direction in PACK['bodyContract']['directions']:
        indices = {'SW': [4, 6, 7, 9, 14, 15], 'W': [3, 6, 7, 10, 14, 15], 'NW': [4, 6, 7, 9, 14, 15]}.get(direction, [3, 6, 7, 9, 14, 15])
        sheet(direction, indices, direction + '-repair-input.png')
        restored(direction, 0).resize((768, 768), Image.Resampling.LANCZOS).save(BUILD / (direction + '-ready-reference.png'))
    sheet('W', [4, 5, 8, 9, 11, 12], 'W-continuity-input.png')
    sheet('SW', [5, 8, 10, 11, 12, 13], 'SW-continuity-input.png')
    sheet('NW', [5, 8, 10, 11, 12, 13], 'NW-continuity-input.png')
