"""Capture fixed playable Golden Wayfarer views for human art review.

Example: python3 tools/capture-wayfarer-views.py --views arrival,avenue,plaza
Requires the local game server and Playwright/Chromium already used for review.
"""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


VIEWS = {
    'gate': (27, 44),
    'arrival': (27, 47.1),
    'avenue': (27, 36),
    'plaza': (27, 29),
    'hall-axis': (27, 17),
    'hall-terrace': (27, 15),
    'market': (42, 27),
    'inn': (11.5, 23.5),
    'blacksmith': (13, 31.5),
    'shrine': (43, 16),
    'residential': (38, 39),
    'town-edge': (34, 44),
}


def capture(url, output, names):
    output.mkdir(parents=True, exist_ok=True)
    records = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path='/usr/bin/chromium', headless=True,
            args=['--no-sandbox', '--enable-webgl', '--use-gl=angle',
                  '--use-angle=swiftshader'])
        context = browser.new_context(viewport={'width': 1280, 'height': 800},
                                      device_scale_factor=1)
        first = context.new_page()
        first.goto(url, wait_until='domcontentloaded', timeout=60000)
        first.locator('#create').wait_for(timeout=60000)
        first.locator('#newname').fill('Golden Warrior')
        first.locator('#create').click()
        first.wait_for_function(
            'document.getElementById("world") && window.AstraeonQA && '
            'window.AstraeonQA.snapshot().renderer', timeout=60000)
        template = first.evaluate('window.AstraeonQA.snapshot().save')
        first.close()
        for name in names:
            x, y = VIEWS[name]
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            state = {**template, 'x': x, 'y': y}
            page.add_init_script('localStorage.setItem("astraeon-iso-v1",'
                                 'JSON.stringify(' + json.dumps(state) + '))')
            page.goto(url, wait_until='domcontentloaded', timeout=60000)
            page.wait_for_function(
                'document.getElementById("world") && window.AstraeonQA && '
                'window.AstraeonQA.snapshot().renderer', timeout=60000)
            page.wait_for_timeout(450)
            snap = page.evaluate('window.AstraeonQA.snapshot()')
            image = output / (name + '.png')
            page.screenshot(path=str(image))
            record = {'name': name, 'requested': [x, y],
                      'actual': [snap['save']['x'], snap['save']['y']],
                      'layout': snap['town']['layout'],
                      'actors': len(snap['renderer']['actors']),
                      'renderCalls': snap['renderer']['calls'],
                      'frameMs': round(snap['renderer']['frameMs'], 2),
                      'errors': errors, 'image': str(image)}
            records.append(record)
            print(json.dumps(record), flush=True)
            page.close()
        browser.close()
    (output / 'views.json').write_text(json.dumps(records, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8014/?qa=1&camera=tilt55')
    parser.add_argument('--output', type=Path, default=Path('/tmp/wayfarer-golden-views'))
    parser.add_argument('--views', default=','.join(VIEWS))
    args = parser.parse_args()
    names = args.views.split(',')
    if any(name not in VIEWS for name in names):
        parser.error('Unknown view; choose from ' + ', '.join(VIEWS))
    capture(args.url, args.output, names)
