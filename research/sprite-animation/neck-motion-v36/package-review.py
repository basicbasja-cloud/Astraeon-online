"""Only contact sheets, enlarged inspection crops and timed review exports."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).resolve().parent
ROOT = P.parents[2]
D = json.loads((P/'motion-contract.json').read_text())
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)


def back(image):
    result = Image.new('RGBA', image.size, '#344351')
    result.alpha_composite(image.convert('RGBA'))
    return result.convert('RGB')


board = Image.new('RGB', (1536, 1100), '#1d2935')
draw = ImageDraw.Draw(board)
necks = Image.new('RGB', (1280, 520), '#1d2935')
nd = ImageDraw.Draw(necks)
for i, row in enumerate(D['variants']['review']):
    im = back(Image.open(P/f'renders/review/full/{i:02}.png'))
    x, y = (i % 4)*384, (i//4)*550
    board.paste(im, (x, y+30))
    draw.text((x+8, y+5), f'Key {i+1} / source {row["source_time_seconds"]:.3f}s / art {row["raw_art_index"]}', font=FONT, fill='white')
    cx, cy = row['observed_receiver_surface_xy']
    crop = im.crop((int(cx)-40, int(cy)-48, int(cx)+40, int(cy)+62)).resize((240, 330))
    # 4x2 board with context around actual seam; no pose registration edits.
    xx, yy = (i % 4)*320, (i//4)*260
    crop = crop.resize((160, 220))
    necks.paste(crop, (xx+80, yy+30))
    nd.text((xx+10, yy+5), f'Key {i+1}', font=FONT, fill='white')
board.save(P/'motion-contact-sheet.png')
necks.save(P/'motion-neck-detail.png')

old = back(Image.open(P.parent/'body-outfit-v35/preview/original.png'))
new = back(Image.open(P/'neck-both.png'))
comparison = Image.new('RGB', (1000, 570), '#1d2935')
cd = ImageDraw.Draw(comparison)
for j, (name, image) in enumerate([('v35 / user-rejected neck', old), ('v36 / single skin neck + body-owned collar', new)]):
    comparison.paste(image.crop((170, 90, 330, 280)).resize((420, 500)), (j*500+40, 40))
    cd.text((j*500+10, 10), name, font=FONT, fill='white')
comparison.save(P/'neck-before-after-detail.png')

receipt = {}
for variant in D['variants']:
    for clock, durations in D['clocks'].items():
        frames = [back(Image.open(P/f'renders/{variant}/full/{i:02}.png')) for i in range(8)]
        palette = frames[0].quantize(colors=255)
        frames = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in frames]
        path = P/f'{variant}-{clock}.gif'
        frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations, loop=0, disposal=1, optimize=False)
        decoded = Image.open(path)
        actual = []
        for i in range(decoded.n_frames):
            decoded.seek(i)
            actual.append(decoded.info['duration'])
        assert sum(actual) == sum(durations)
        receipt[path.name] = dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                 logical_exposures=8, distinct_body_drawings=len({r['body']['sha256'] for r in D['variants'][variant]}),
                                 logical_durations_ms=durations, encoded_frames=decoded.n_frames,
                                 decoded_durations_ms=actual, total_ms=sum(actual), terminal_rest_ms=600,
                                 duplicate_hold_merge='GIF encoder can merge adjacent identical frames; logical timeline preserved')
(P/'playback-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
print('PACKAGED_ACTUAL_RENDERED_REVIEW_AND_RETAINED_RAW_CONTROL')
