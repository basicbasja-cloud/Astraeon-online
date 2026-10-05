"""Original repeatable stone, brick and groundcover artwork from RO3 observations.

No reference pixels are sampled. Keep editable lossless masters and measured
linear means so the native palette owns hue without washing out stone joints.
"""
import hashlib
import json
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'authoring/materials'
OUT.mkdir(exist_ok=True)
rng = random.Random(69045)


def save(name, picture, world_size, detail, alpha=False):
    master = OUT / (name + '-source.png')
    asset = ROOT / 'assets' / (name + '.webp')
    picture.save(master)
    picture.save(asset, lossless=True, method=6)
    a = np.asarray(picture.convert('RGB'), dtype=float) / 255
    linear = np.where(a <= .04045, a / 12.92, ((a + .055) / 1.055) ** 2.4)
    spec = {'file': asset.relative_to(ROOT).as_posix(), 'grid': [1, 1], 'tile': 0,
            'worldSize': world_size, 'paletteDetail': detail,
            'meanLinearRGB': (np.average(linear.reshape(-1,3), axis=0, weights=np.asarray(picture.getchannel("A")).reshape(-1)+1e-6) if alpha else linear.mean(axis=(0,1))).round(7).tolist()}
    if alpha:
        spec.update(alphaCutoff=.14,alphaBlend=True)
    return {'texture': spec, 'master': master.relative_to(ROOT).as_posix(),
            'size': list(picture.size), 'sha256': hashlib.sha256(asset.read_bytes()).hexdigest()}


# Mixed rectangular ashlar, including rotated long stones. Whole cells tile
# exactly; a joint bisects each outer boundary just like the interior joints.
stone = Image.new('RGB', (2048, 2048), '#756f5d')
draw = ImageDraw.Draw(stone)
used = set()
for y in range(16):
    for x in range(16):
        if (x, y) in used:
            continue
        choices = [(1, 1), (2, 1), (1, 2), (2, 1), (1, 2), (3, 1)]
        valid = [(w, h) for w, h in choices if x+w <= 16 and y+h <= 16
                 and not any((xx, yy) in used for yy in range(y, y+h) for xx in range(x, x+w))]
        w, h = rng.choice(valid)
        used.update((xx, yy) for yy in range(y, y+h) for xx in range(x, x+w))
        l, t, r, b = x*128+6, y*128+6, (x+w)*128-6, (y+h)*128-6
        chip = rng.randint(5, 12)
        poly = [(l+chip,t),(r-chip,t),(r,t+chip),(r,b-chip),
                (r-chip,b),(l+chip,b),(l,b-chip),(l,t+chip)]
        v = rng.randint(-14, 15)
        color = (179+v, 173+v, 153+v)
        draw.polygon(poly, fill=color)
        draw.line(poly[:4], fill=tuple(c+19 for c in color), width=3)
        draw.line(poly[3:]+poly[:1], fill=tuple(c-22 for c in color), width=4)
        for _ in range(int(w*h*160)):
            xx, yy = rng.randint(l+9,r-9), rng.randint(t+9,b-9)
            dv = rng.randint(-7, 7)
            draw.line((xx,yy,xx+rng.randint(1,5),yy), fill=tuple(c+dv for c in color))
        if rng.random() < .23:
            xx, yy = rng.randint(l+12,r-12), rng.randint(t+12,b-12)
            draw.line((l+2,yy,xx,yy+rng.randint(-8,8)), fill=tuple(c-14 for c in color), width=1)

brick = Image.new('RGB', (1024, 1024), '#938978')
draw = ImageDraw.Draw(brick)
for row in range(8):
    for col in range(-1, 5):
        x, y = col*256+(row%2)*128, row*128
        v = rng.randint(-13, 14)
        color = (180+v, 161+v, 132+v)
        chip=rng.randint(4,11)
        poly=[(x+6+chip,y+6),(x+250-chip,y+6),(x+250,y+6+chip),(x+250,y+122-chip),(x+250-chip,y+122),(x+6+chip,y+122),(x+6,y+122-chip),(x+6,y+6+chip)]
        draw.polygon(poly, fill=color)
        draw.line((x+7,y+6,x+250,y+6), fill=tuple(c+19 for c in color), width=4)
        draw.line((x+250,y+9,x+250,y+121,x+8,y+121), fill=tuple(c-21 for c in color), width=4)
        for _ in range(100):
            xx, yy = rng.randint(x+9,x+245), rng.randint(y+12,y+115)
            dv = rng.randint(-10, 10)
            draw.line((xx,yy,xx+rng.randint(1,8),yy), fill=tuple(c+dv for c in color))

# Visible mineral mottling survives gameplay mip levels. Periodic fields keep
# the repeat seamless; fine pores alone would average into clean flat blocks.
def weather(picture, seed, strength):
    noise_rng=np.random.default_rng(seed)
    broad=noise_rng.integers(0,256,(24,24),dtype=np.uint8)
    n=picture.width
    field=np.asarray(Image.fromarray(np.tile(broad,(3,3))).resize((n*3,n*3),Image.Resampling.BICUBIC),dtype=float)[n:n*2,n:n*2]/255-.5
    grain=np.asarray(picture,dtype=float)
    return Image.fromarray(np.clip(grain+field[:,:,None]*strength,0,255).astype('uint8'))
stone=weather(stone,690451,22)
brick=weather(brick,690452,35)

# Sparse overlapping leaf tips and moss specks over a transparent field. The
# native patch boundary supplies its shape; alpha supplies a broken plant edge.
green = Image.new('RGBA', (2048, 2048))
draw = ImageDraw.Draw(green)
for _ in range(34000):
    x, y = rng.randrange(2048), rng.randrange(2048)
    v = rng.randrange(-15, 16)
    color = (105+v, 133+v, 61+v, rng.randrange(160, 256))
    draw.ellipse((x-5,y-3,x+5,y+3), fill=color)
    if rng.random() < .5:
        draw.line((x,y+4,x+rng.randint(-5,5),y-8), fill=(143+v,164+v,78+v,255), width=2)

# One native UV island per foundation strip. A wavy outward edge and tapered
# ends blend grass into the paving; the wall side stays dense. Actual rooted
# blade clumps supply vertical growth instead of an opaque polygon silhouette.
green = Image.alpha_composite(Image.new('RGBA',green.size,(100,148,50,185)),green)
a = np.asarray(green).copy()
yy,xx = np.mgrid[0:2048,0:2048]
edge = 560+240*np.sin(xx/310)+130*np.sin(xx/106+.6)
fadeOut = np.clip((yy-edge)/320,0,1)
fadeEnds = np.clip(np.minimum(xx,2047-xx)/200,0,1)
a[:,:,3] = (a[:,:,3]*fadeOut*fadeEnds).astype('uint8')
green = Image.fromarray(a)

records = {
    'paving': save('wayfarer-pavers-v69', stone, 8, .80),
    'brick': save('wayfarer-brick-v69', brick, 2.4, .85),
    'groundcover': save('wayfarer-groundcover-v69', green, 1.8, .78, True),
}
(OUT / 'wayfarer-street-v69.json').write_text(json.dumps({
    'sourcePass': 69, 'method': 'deterministic original procedural artwork',
    'references': ['04_08_45: mixed rectangular paving and irregular foundation grass',
                   '04_08_39/34: brick ground floors, joints and shuttered side windows'],
    'referencePixelsUsed': False, 'materials': records,
}, indent=2)+'\n')
print('Painted original 2048 stone, 1024 brick and alpha groundcover masters')
