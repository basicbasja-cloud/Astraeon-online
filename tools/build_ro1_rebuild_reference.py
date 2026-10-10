"""Build a private RO1 parts workbench and publish only numeric registration evidence.

Inputs are pinned public fixture ACT/SPR plus captured public assembled renders.
No source pixels are copied into committed review or runtime directories.
"""
import hashlib
import json
import struct
from pathlib import Path
from PIL import Image, ImageDraw
from extract_ro1_reference import inspect_act

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / 'authoring/characters/private-ro-reference'
OUT = PRIVATE / 'rebuild-ro1'
REVIEW = ROOT / 'docs/review/character-ro1-rebuild-v2'
DIRECTIONS = ['S', 'SW', 'W', 'NW', 'N', 'NE', 'E', 'SE']


def sprites(path):
    data = path.read_bytes()
    assert data[:2] == b'SP'
    version, count = struct.unpack_from('<HH', data, 2)
    truecolor = struct.unpack_from('<H', data, 6)[0] if version >= 0x200 else 0
    assert truecolor == 0, 'This fixture decoder deliberately rejects unimplemented RGBA SPR.'
    offset = 8 if version >= 0x200 else 6
    palette = data[-1024:]
    images = []
    for _ in range(count):
        width, height = struct.unpack_from('<HH', data, offset)
        offset += 4
        length = struct.unpack_from('<H', data, offset)[0] if version >= 0x201 else width * height
        if version >= 0x201:
            offset += 2
        encoded = data[offset:offset + length]
        offset += length
        indices = []
        i = 0
        while i < length:
            value = encoded[i]
            i += 1
            if value == 0 and version >= 0x201:
                indices.extend([0] * encoded[i])
                i += 1
            else:
                indices.append(value)
        assert len(indices) == width * height
        rgba = bytes(v for index in indices for v in (*palette[index * 4:index * 4 + 3], 255 if index else 0))
        images.append(Image.frombytes('RGBA', (width, height), rgba))
    assert offset == len(data) - 1024
    return images


def draw_frame(images, frame, delta=(0, 0)):
    result = Image.new('RGBA', (192, 192))
    for layer in frame['layers']:
        index = layer['imageIndex']
        if index < 0:
            continue
        assert layer['imageType'] == 0
        assert layer['tintRGBA'] == [255, 255, 255, 255]
        im = images[index]
        if layer['mirrorFlag']:
            im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        scale = layer['scale']
        if scale != [1, 1]:
            im = im.resize(tuple(max(1, round(a * b)) for a, b in zip(im.size, scale)))
        if layer['rotationDegrees']:
            im = im.rotate(-layer['rotationDegrees'], expand=True)
        result.alpha_composite(im, (round(96 + delta[0] + layer['x'] - im.width // 2),
                                   round(160 + delta[1] + layer['y'] - im.height // 2)))
    return result


def main():
    bodypath = PRIVATE / 'true8dir/swordsman-male'
    headpath = OUT / 'raw/head-1'
    bodies = sprites(bodypath.with_suffix('.spr'))
    heads = sprites(headpath.with_suffix('.spr'))
    body = inspect_act(bodypath.with_suffix('.act').read_bytes(), 25)
    head = inspect_act(headpath.with_suffix('.act').read_bytes(), 25)
    records = []
    for action, base in [('idle', 0), ('walk', 8), ('ready', 32), ('attack', 80)]:
        target = OUT / 'parts' / action
        target.mkdir(parents=True, exist_ok=True)
        for d, direction in enumerate(DIRECTIONS):
            ba = body['actions'][base + d]
            ha = head['actions'][base + d]
            for f, bf in enumerate(ba['frames']):
                # Straight head for stand; walk/attack have explicit synchronized records.
                hf = ha['frames'][0 if action == 'idle' else f % ha['frameCount']]
                bp = bf['actAnchors'][0]
                hp = hf['actAnchors'][0]
                delta = [bp['x'] - hp['x'], bp['y'] - hp['y']]
                b = draw_frame(bodies, bf)
                h = draw_frame(heads, hf, delta)
                combined = Image.alpha_composite(b, h)
                for name, im in [('body', b), ('head', h), ('body-head', combined)]:
                    im.save(target / f'{direction}-{f:02}-{name}.png')
                records.append(dict(action=action, direction=direction, actionId=base + d,
                                    frame=f, bodyAnchor=bp, headAnchor=hp, headPlacementDelta=delta,
                                    bodyImageIndices=[l['imageIndex'] for l in bf['layers']],
                                    headImageIndices=[l['imageIndex'] for l in hf['layers']],
                                    bodyPixelHash=hashlib.sha256(b.tobytes()).hexdigest(),
                                    headPixelHash=hashlib.sha256(h.tobytes()).hexdigest()))
    evidence = dict(status='REFERENCE_ONLY; new original art not accepted',
                    sourceRevision='4de4fa747431979d35c747d7edd549a872efd9e1',
                    bodyACTSHA256=body['sha256'], headACTSHA256=head['sha256'],
                    classification='CONFIRMED_FORMAT + explicitly implemented renderer attachment formula',
                    limitation='No raw sword ACT/SPR. Sword and slash are visible only in captured assembled renderer references. Anatomical joints are not ACT anchors.',
                    records=records)
    REVIEW.mkdir(parents=True, exist_ok=True)
    (REVIEW / 'ro1-part-registration.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(f'Decoded {len(records)} body/head pairs into ignored storage; numeric registration exported.')


if __name__ == '__main__':
    main()
