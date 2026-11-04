"""Overlay Blender-selected skin points on an entire fixed-grid walk draft.

These are selected skin vertices, not verified soles or measurements of contact.
The same source-crop transform is used for the guide and artwork; no per-frame
registration or scaling is performed.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
GUIDE_MANIFEST = ROOT / 'authoring/characters/factory-v3/patch-0.0.1/guides/4e519e1eadc69aaf28a2/manifest.json'
PROJECTION = ROOT / 'authoring/characters/factory-v3/patch-0.0.1/research/swordsman-walk-feet-projection-20261029/receipt.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tiles(path):
    with Image.open(path) as im:
        sheet = im.convert('RGB').resize((1536, 1536), Image.Resampling.LANCZOS)
    return [sheet.crop(((i % 4)*384, (i//4)*384, (i%4+1)*384, (i//4+1)*384)) for i in range(16)]


def build(source, output):
    if output.exists() or output.is_symlink():
        raise ValueError('Choose a fresh output directory')
    data = json.loads(PROJECTION.read_text())
    if data['status'] != 'SOURCE_SKIN_POINT_PROJECTION_NOT_CONTACT_APPROVAL' or data['guide_sha256'] != digest(GUIDE_MANIFEST):
        raise ValueError('Projection does not match source guide')
    if [f['frame'] for f in data['frames']] != list(range(16)):
        raise ValueError('Expected all sixteen ordered source frames')
    paths = [source/'guide-contact.png', source/'generated-sheet.png']
    sheets = [tiles(p) for p in paths]
    output.mkdir(parents=True)
    panels = []
    for i in range(16):
        panel = Image.new('RGB', (768, 412), 'white')
        d = ImageDraw.Draw(panel)
        for col, label in enumerate(('guide', 'draft')):
            im = sheets[col][i].copy()
            draw = ImageDraw.Draw(im)
            for side, color in (('l', '#00aaff'), ('r', '#ff9a00')):
                x, y = data['frames'][i]['feet'][side]['source_guide_xy']
                x, y = (x-420)*384/696, (y-520)*384/696
                draw.ellipse((x-5, y-5, x+5, y+5), outline=color, width=2)
                draw.text((x+6, y-8), side, fill=color)
            panel.paste(im, (384*col, 28))
            d.text((384*col+4, 5), f'{label} {i:02} / source selected vertices', fill='black')
        panel.save(output/f'frame{i:02}.png')
        panels.append(panel)
    panels[0].save(output/'overlay-slow.gif', save_all=True, append_images=panels[1:], duration=200, loop=0, optimize=False)
    receipt = {'status': 'SOURCE_SKIN_OVERLAY_NOT_CONTACT_APPROVAL', 'projection_sha256': digest(PROJECTION),
               'guide_manifest_sha256': digest(GUIDE_MANIFEST), 'input_sha256': {p.name: digest(p) for p in paths},
               'script_sha256': digest(Path(__file__)), 'frames': 16,
               'limitations': ['Selected vertices can change between poses and are not verified anatomical soles.',
                               'No correction for character design differences or manual art landmarks is implied.',
                               'This is a visual overlay, not a foot-contact, scale, continuity, or gameplay approval.']}
    (output/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.source, args.output)
