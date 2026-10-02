"""Remove legacy painted boots and bake exactly two legs into each existing gait.

The v3 contact manifest and costume views are the authority. This only updates
the Warrior's three saved locomotion atlases; no world geometry is regenerated.
"""
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
CELL = 256
SCALE = 3
manifest = json.loads((ROOT / 'world/v3/warrior-animation.json').read_text())
base_torso = Image.open(ROOT / 'assets/warrior-torso-v1.webp').convert('RGBA')

# Each source costume view still has one painted lower leg. Keep the cloak,
# tunic and sword, and remove only that old boot before baking the new pair.
old_boot = [
    [(145, 164), (182, 164), (182, 205), (144, 205)],
    [(159, 163), (200, 163), (200, 205), (159, 205)],
    [(152, 163), (198, 163), (198, 203), (152, 203)],
    [(89, 162), (116, 162), (117, 202), (88, 202)],
    [(76, 168), (114, 168), (114, 210), (76, 210)],
    [(156, 163), (188, 163), (188, 205), (156, 205)],
    [(124, 165), (155, 165), (155, 205), (124, 205)],
    [(66, 171), (97, 171), (97, 205), (66, 205)],
]


def draw_leg(draw, a, b, width, color):
    draw.line([(round(a[0] * SCALE), round(a[1] * SCALE)),
               (round(b[0] * SCALE), round(b[1] * SCALE))],
              fill=color, width=round(width * SCALE), joint='curve')


for mode in ('walk', 'run', 'sprint'):
    clip = manifest['clips'][mode]
    torso_path = ROOT / 'assets' / f'warrior-{mode}-torso-v3.webp'
    clean_sheet = Image.new('RGBA', (CELL, CELL * 8))
    atlas = Image.new('RGBA', (CELL * 8, CELL * 8))
    for row in range(8):
        angle = math.pi / 2 - row * math.pi / 4
        offset_x = 32 + round(math.cos(angle) * clip['bodyPitch'])
        offset_y = 30 + round(math.sin(angle) * clip['bodyPitch'] * .3)
        costume = Image.new('RGBA', (CELL, CELL))
        costume.alpha_composite(base_torso.crop((0, row * 192, 192, (row + 1) * 192)),
                                (offset_x, offset_y))
        alpha = costume.getchannel('A')
        ImageDraw.Draw(alpha).polygon(old_boot[row], fill=0)
        costume.putalpha(alpha)
        clean_sheet.alpha_composite(costume, (0, row * CELL))
        large_costume = costume.resize((CELL * SCALE, CELL * SCALE), Image.Resampling.LANCZOS)
        for column in range(8):
            frame = clip['frames'][row * 8 + column]
            painted = Image.new('RGBA', (CELL * SCALE, CELL * SCALE))
            draw = ImageDraw.Draw(painted)
            # Rear foot first, front foot last, matching the registered view.
            for contact in sorted(frame['contacts'], key=lambda leg: leg['foot'][1]):
                hip, knee, foot = (contact[k] for k in ('hip', 'knee', 'foot'))
                draw_leg(draw, hip, knee, 16, '#302b28')
                draw_leg(draw, hip, knee, 12, '#62564a')
                draw_leg(draw, (hip[0]-2, hip[1]), (knee[0]-2, knee[1]), 2, '#b59d67')
                draw_leg(draw, knee, foot, 14, '#282c2b')
                draw_leg(draw, knee, foot, 11, '#444541')
                draw_leg(draw, (knee[0]-2, knee[1]), (foot[0]-2, foot[1]-3), 2, '#807454')
                kx, ky = knee
                draw.ellipse(((kx-6)*SCALE, (ky-4)*SCALE,
                              (kx+6)*SCALE, (ky+5)*SCALE),
                             fill='#756a50', outline='#b3a173', width=SCALE)
                fx, fy = foot
                forward = fx - hip[0]
                toe = max(-5, min(5, forward * .2))
                draw.polygon([((fx-5)*SCALE, (fy-6)*SCALE),
                              ((fx+4)*SCALE, (fy-6)*SCALE),
                              ((fx+6+toe)*SCALE, (fy-1)*SCALE),
                              ((fx+5+toe)*SCALE, (fy+2)*SCALE),
                              ((fx-5)*SCALE, (fy+2)*SCALE)], fill='#32332e')
            painted.alpha_composite(large_costume)
            atlas.alpha_composite(painted.resize((CELL, CELL), Image.Resampling.LANCZOS),
                                  (column * CELL, row * CELL))
    clean_sheet.save(torso_path, lossless=True)
    atlas.save(ROOT / clip['atlas'], lossless=True)
    print(mode, '64 complete two-leg frames')
