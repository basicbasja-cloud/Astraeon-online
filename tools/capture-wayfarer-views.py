"""Capture fixed playable Golden Wayfarer views for human art review.

Example: python3 tools/capture-wayfarer-views.py --views arrival,avenue,plaza
Requires the local game server and Playwright/Chromium already used for review.
"""
import argparse
import os
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
    'frontage-shop': (34.4, 25.3),
    'frontage-home': (40, 39.5),
    'town-edge': (34, 44),
    'overview': (27, 23.5),
    'hall-skyline': (36.5, 4.5),
    'river-bank': (6.5, 26.5),
    'river-falls': (7.25, 34.5),
    'gate-spillways': (21, 42.5),
    'hall-processional-view': (27, 40),
}


def capture(url, output, names, zoom=None, yaw=0, pitch=None, capture_scale=None, startup_timeout_ms=120000):
    output.mkdir(parents=True, exist_ok=True)
    records = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=os.environ.get('ASTRAEON_BROWSER', '/usr/bin/chromium'), headless=True,
            args=['--no-sandbox', '--enable-webgl', '--enable-gpu'] +
                 (['--use-angle=d3d11'] if os.name == 'nt' else
                  ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']))
        context = browser.new_context(viewport={'width': 1280, 'height': 800},
                                      device_scale_factor=1)
        first = context.new_page()
        first.set_default_timeout(startup_timeout_ms)
        first.goto(url, wait_until='domcontentloaded', timeout=startup_timeout_ms)
        first.locator('#create').wait_for(timeout=startup_timeout_ms)
        first.locator('#newname').fill('Golden Warrior')
        first.locator('#create').click(timeout=startup_timeout_ms)
        first.wait_for_function(
            'document.getElementById("world") && window.AstraeonQA && '
            'window.AstraeonQA.snapshot().renderer', timeout=startup_timeout_ms)
        template = first.evaluate('window.AstraeonQA.snapshot().save')
        first.close()
        for name in names:
            x, y = (v*2 for v in VIEWS[name])
            route=json.loads(Path('world/v3/wayfarer-spatial.json').read_text(encoding='utf-8'))['route']
            stop=next((a for a in route if a['name'].lower()==name),None)
            if stop:x,y=stop['position']
            if name=="hall-terrace":x,y=54,24
            if name=="hall-axis":x,y=54,42
            page = context.new_page()
            page.set_default_timeout(startup_timeout_ms)
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('console', lambda message: errors.append(message.text) if message.type=='error' else None)
            state = {**template, 'x': x, 'y': y}
            page.add_init_script('localStorage.setItem("astraeon-iso-v1",'
                                 'JSON.stringify(' + json.dumps(state) + '))')
            page.goto(url, wait_until='domcontentloaded', timeout=startup_timeout_ms)
            page.wait_for_function(
                'document.getElementById("world") && window.AstraeonQA && '
                'window.AstraeonQA.snapshot().renderer', timeout=startup_timeout_ms)
            page.wait_for_timeout(450)
            if zoom is not None:
                rect=page.locator('#world').bounding_box();pointer_x=rect['x']+rect['width']/2;pointer_y=rect['y']+rect['height']/2
                page.keyboard.down('Control');page.mouse.move(pointer_x,pointer_y);page.mouse.down(button='right');page.mouse.move(pointer_x,pointer_y-(zoom-125)/1.5,steps=8);page.mouse.up(button='right');page.keyboard.up('Control');page.wait_for_timeout(800)
            if yaw:
                rect=page.locator('#world').bounding_box();px=rect['x']+rect['width']/2;py=rect['y']+rect['height']/2
                page.mouse.move(px,py);page.mouse.down(button='right');page.mouse.move(px-yaw*rect['width']/720,py,steps=8);page.mouse.up(button='right');page.wait_for_timeout(800)
            if pitch is not None:
                rect=page.locator('#world').bounding_box();px=rect['x']+rect['width']/2;py=rect['y']+rect['height']/2
                page.keyboard.down('Shift');page.mouse.move(px,py);page.mouse.down(button='right');page.mouse.move(px,py+(pitch-46)*rect['height']/300,steps=8);page.mouse.up(button='right');page.keyboard.up('Shift');page.wait_for_timeout(800)
            if capture_scale is not None:
                page.evaluate('(ratio)=>AstraeonSpatialView.renderer.setPixelRatio(ratio)', capture_scale)
                page.wait_for_timeout(450)
            snap = page.evaluate('window.AstraeonQA.snapshot()')
            image = output / (name + '.png')
            page.screenshot(path=str(image))
            record = {'name': name, 'requested': [x, y],
                      'actual': [snap['save']['x'], snap['save']['y']],
                      'layout': snap['town']['layout'],
                      'actors': len(snap['renderer']['actors']),
                      'fadedBuildings': snap['renderer'].get('fadedBuildings', []),
                      'actorArtwork': {a['id']: a.get('motionSample', {}).get('frame') for a in snap['renderer']['actors']},
                      'renderCalls': snap['renderer']['calls'],
                      'frameMs': round(snap['renderer']['frameMs'], 2),
                      'device': snap['renderer'].get('device'),
                      'camera': snap['renderer'].get('cameraProfile'),
                      'captureScale': capture_scale,
                      'renderResolution': page.evaluate('({width:AstraeonSpatialView.canvas.width,height:AstraeonSpatialView.canvas.height,pixelRatio:AstraeonSpatialView.renderer.getPixelRatio()})'),
                      'errors': errors, 'image': str(image)}
            records.append(record)
            print(json.dumps(record), flush=True)
            page.close()
        browser.close()
    (output / 'views.json').write_text(json.dumps(records, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8011/?qa=1')
    parser.add_argument('--output', type=Path, default=Path('/tmp/wayfarer-golden-views'))
    parser.add_argument('--views', default=','.join(VIEWS))
    parser.add_argument('--zoom', type=float, help='Use ordinary Ctrl-right-drag zoom for a still review (65–325)')
    parser.add_argument('--yaw',type=float,default=0,help='Use ordinary right-drag orbit for architecture review')
    parser.add_argument('--pitch',type=float,help='Optional ordinary Shift-right-drag; default gameplay pitch remains 46')
    parser.add_argument('--capture-scale', type=float,
                        help='Still-image pixel ratio, independent of the runtime performance policy')
    parser.add_argument('--startup-timeout-ms', type=int, default=120000,
                        help='Bounded browser startup deadline; capture quality is unchanged')
    args = parser.parse_args()
    names = args.views.split(',')
    if any(name not in VIEWS for name in names):
        parser.error('Unknown view; choose from ' + ', '.join(VIEWS))
    if args.zoom is not None and not 65<=args.zoom<=325:parser.error('Zoom must be within classic RO limits, 65–325')
    if args.pitch is not None and not 10<=args.pitch<=89:parser.error('Pitch must be within gameplay limits, 10–89')
    if args.capture_scale is not None and not .5<=args.capture_scale<=3:parser.error('Capture scale must be within .5–3')
    capture(args.url, args.output, names,args.zoom,args.yaw,args.pitch,args.capture_scale,args.startup_timeout_ms)
