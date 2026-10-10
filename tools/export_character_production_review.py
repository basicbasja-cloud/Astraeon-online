"""Export any compatible appearance pack through the shared browser renderer.

Run a local repository HTTP server first. This tool knows no character, gender,
costume, weapon design, or pose coordinates. Outputs are review evidence only.
"""
import argparse
import base64
import io
import json
from pathlib import Path
from urllib.parse import urlencode
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

MODES = ['Full composite', 'Body only', 'Weapon only', 'Body + Weapon', 'Grip debug']


def export(base, motion, appearance, action, out, size=256):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    url = base.rstrip('/') + '/character-production-review.html?' + urlencode(dict(motion=motion, appearance=appearance))
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel='msedge', headless=True)
        page = browser.new_page(viewport=dict(width=1200, height=900))
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(url)
        page.wait_for_function('window.characterProductionReview')
        info = page.evaluate('window.characterProductionReview.describe()')
        if action not in info['actions']:
            raise ValueError('Unknown action')
        directions = info['directions']
        sequences = info['actions'][action]['directions']
        counts = [len(sequences[d]['frames']) for d in directions]
        schedules = [[f['durationMs'] for f in sequences[d]['frames']] for d in directions]
        if len(set(counts)) != 1 or any(t != schedules[0] for t in schedules):
            raise ValueError('Grid export requires synchronized directional schedules; do not silently truncate frames')
        count = counts[0]
        header = 24
        for mode in MODES:
            by_direction = {}
            for direction in directions:
                frames = []
                for frame in range(count):
                    data = page.evaluate('(p)=>window.characterProductionReview.render(p)', dict(action=action, direction=direction, frame=frame, mode=mode))
                    im = Image.open(io.BytesIO(base64.b64decode(data.split(',', 1)[1]))).convert('RGBA')
                    im = im.resize((size, size), Image.Resampling.LANCZOS)
                    cell = Image.new('RGB', (size, size + header), '#253846')
                    cell.paste(im, (0, header), im)
                    ImageDraw.Draw(cell).text((8, 5), f'{direction} / {frame} / {mode}', fill='white')
                    frames.append(cell)
                by_direction[direction] = frames
                if mode == 'Full composite':
                    cols = min(4, count)
                    sheet = Image.new('RGB', (size * cols, (size + header) * ((count + cols - 1) // cols)), '#17232d')
                    for f, cell in enumerate(frames):
                        sheet.paste(cell, ((f % cols) * size, (f // cols) * (size + header)))
                    sheet.save(out / f'{action}-{direction}-frames.png')
            grid_frames = []
            for frame in range(count):
                grid = Image.new('RGB', (size * 4, (size + header) * 2), '#17232d')
                for i, direction in enumerate(directions):
                    grid.paste(by_direction[direction][frame], ((i % 4) * size, (i // 4) * (size + header)))
                grid_frames.append(grid)
            name = mode.lower().replace(' + ', '-').replace(' ', '-')
            # Exact APNG timing remains available; GIF duration units are 10 ms.
            grid_frames[0].save(out / f'{action}-{name}.apng', save_all=True, append_images=grid_frames[1:], duration=schedules[0], loop=0)
            for speed in [1, 0.5]:
                elapsed = previous = 0
                durations = []
                for duration in schedules[0]:
                    elapsed += duration / speed
                    rounded = round(elapsed / 10) * 10
                    if rounded <= previous:
                        raise ValueError('GIF cannot represent this timing; use exact APNG')
                    durations.append(rounded - previous)
                    previous = rounded
                suffix = 'normal' if speed == 1 else 'half-speed'
                grid_frames[0].save(out / f'{action}-{name}-{suffix}.gif', save_all=True, append_images=grid_frames[1:], duration=durations, loop=0, disposal=2)
        browser.close()
        if errors:
            raise RuntimeError('; '.join(errors))
    report = dict(packId=info['packId'], action=action, directions=directions,
                  frameCounts=counts, exactFrameDurationsMs=schedules[0], modes=MODES,
                  browserErrors=errors, visualApproval=False,
                  limitation='Exports and geometric validation do not certify anatomy, grip, perspective or occlusion.')
    (out / 'export-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8022')
    parser.add_argument('--motion', required=True)
    parser.add_argument('--appearance', required=True)
    parser.add_argument('--action', default='BasicAttack')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--size', default=256, type=int)
    args = parser.parse_args()
    if not 64 <= args.size <= 640:
        parser.error('--size must be 64..640')
    print(json.dumps(export(args.base_url, args.motion, args.appearance, args.action, args.output, args.size), indent=2))
