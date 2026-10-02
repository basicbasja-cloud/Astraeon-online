"""Review the Golden Warrior in the actual town through ordinary game input.

Captures the court, services, city gate, and action states across four viewports.
Read-only QA snapshots observe navigation; no runtime setters or teleports.
"""
import argparse
import json
import math
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8001')
parser.add_argument('--output', default='/tmp/astraeon-golden-qa')
parser.add_argument('--world', default='')
args = parser.parse_args()
out = Path(args.output)
out.mkdir(parents=True, exist_ok=True)
checks, errors, resources = [], [], []

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    context = browser.new_context(viewport={'width': 1280, 'height': 800})
    page = context.new_page()
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('response', lambda r: resources.append(f'{r.status} {r.url}') if r.status >= 400 else None)
    page.goto(args.url.rstrip('/') + '/index.html?qa=1' + ('&world='+args.world if args.world else ''), wait_until='networkidle')
    page.locator('#newname').fill('Golden Warrior')
    page.locator('#create').click()
    page.wait_for_selector('#world')

    def snap():
        return page.evaluate('AstraeonQA.snapshot()')

    def elapsed(seconds):
        page.wait_for_function('(time)=>AstraeonQA.snapshot().time>=time', arg=snap()['time'] + seconds)

    def point(x, y, lift=0):
        s = snap()
        r = page.locator('#world').bounding_box()
        v = s['view']
        return (r['x'] + r['width']/2 + (x*v['basis']['xx']+y*v['basis']['yx']-s['camera']['x'])*v['zoom'],
                r['y'] + r['height']*v['anchorY'] + (x*v['basis']['xy']+y*v['basis']['yy']-s['camera']['y']-lift)*v['zoom'])

    def click(x, y, lift=0):
        px, py = point(x, y, lift)
        r = page.locator('#world').bounding_box()
        assert r['x'] < px < r['x']+r['width'] and r['y'] < py < r['y']+r['height'], (x, y, px, py)
        page.mouse.click(px, py)

    def walk(x, y):
        click(x, y)
        page.wait_for_function('(g)=>{const p=AstraeonQA.snapshot().player.position;return Math.hypot(p.x-g[0],p.y-g[1])<.5}', arg=[x, y], timeout=20000)
        elapsed(.3)

    def capture(name):
        identity = snap()['save']['name']
        for width, height in [(1280, 800), (390, 844), (844, 390), (768, 1024)]:
            page.set_viewport_size({'width': width, 'height': height})
            elapsed(.2)
            assert snap()['save']['name'] == identity
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
            page.screenshot(path=str(out / f'{name}-{width}-{height}.png'))
        page.set_viewport_size({'width': 1280, 'height': 800})
        elapsed(.2)

    def passed(name, evidence):
        checks.append({'name': name, 'evidence': evidence})
        print('PASS', name, flush=True)

    elapsed(.3)
    capture('court')
    # Walking through the fountain's footprint must stop outside its physical core.
    click(14.5, 15)
    elapsed(2)
    pos = snap()['player']['position']
    assert not (13.4 < pos['x'] < 15.6 and 14.4 < pos['y'] < 15.7), pos
    walk(17, 18)
    walk(17, 13)
    walk(14.5, 13)
    walk(11, 16)
    passed('fountain collision and perimeter circulation', {'position': snap()['player']['position']})

    for name, menu in [('Guild Registrar', 'guild'), ('Quest Board', 'journal')]:
        npc = next(n for n in snap()['npcs'] if n['name'] == name)['transform']['position']
        click(npc['x'], npc['y'], 15)
        page.wait_for_selector('#modal:not([hidden])')
        assert page.locator('#window-title').inner_text()
        assert math.hypot(snap()['save']['x']-npc['x'], snap()['save']['y']-npc['y']) < 2.4
        page.keyboard.press('Escape')
    capture('consortium')
    passed('Consortium entrance and adjacent quest service', {'services': ['guild', 'journal']})

    walk(14.5, 18)
    # Eight movement headings retain artwork and grounded gait in the real court.
    for keys in [('s',), ('s', 'd'), ('d',), ('w', 'd'), ('w',), ('w', 'a'), ('a',), ('s', 'a')]:
        for key in keys:
            page.keyboard.down(key)
        elapsed(.35)
        assert snap()['player']['speed'] > .1
        page.screenshot(path=str(out / ('walk-' + ''.join(keys) + '.png')))
        for key in keys:
            page.keyboard.up(key)
        elapsed(.15)
        walk(14.5, 18)
    passed('eight movement headings in the Golden court', {'views': 8})

    # Capture real anticipation/contact and each existing skill, rather than an atlas preview.
    for degrees in [0, 90, 180, 270]:
        a = math.radians(degrees)
        page.mouse.move(*point(14.5+math.cos(a)*3, 18+math.sin(a)*3))
        page.keyboard.press('f')
        page.wait_for_function('AstraeonQA.snapshot().animation.state==="attack"')
        elapsed(.2)
        page.screenshot(path=str(out / f'attack-{degrees}.png'))
        elapsed(.7)
    for key in ['1', '2', '3', '4']:
        cost = page.evaluate('(slot)=>AstraeonCombat.definitions.warrior[slot].cost', 'skill' + key)
        page.wait_for_function('(cost)=>AstraeonQA.snapshot().save.energy>=cost', arg=cost)
        before = snap()['save']['energy']
        page.keyboard.press(key)
        page.wait_for_function('(v)=>AstraeonQA.snapshot().save.energy<v', arg=before)
        elapsed(.15)
        page.screenshot(path=str(out / f'skill-{key}.png'))
        elapsed(1)
    page.keyboard.down('d')
    elapsed(.15)
    page.keyboard.press('Space')
    elapsed(.1)
    assert snap()['animation']['state'] == 'dodge'
    page.screenshot(path=str(out / 'dodge.png'))
    page.keyboard.up('d')
    elapsed(.6)
    passed('directional attacks, existing skills and dodge feedback', {'attacks': 4, 'skills': 4})

    walk(22, 17.8)
    npc = next(n for n in snap()['npcs'] if n['name'] == 'Merchant')['transform']['position']
    click(npc['x'], npc['y'], 15)
    page.wait_for_selector('#modal:not([hidden])')
    assert page.locator('[data-buy]').count() > 0
    page.keyboard.press('Escape')
    capture('market')
    passed('market counter and merchant approach', {'merchant': npc})

    walk(29, 21)
    walk(34, 27.5)
    npc = next(n for n in snap()['npcs'] if n['name'] == 'Artisan')['transform']['position']
    click(npc['x'], npc['y'], 15)
    page.wait_for_selector('[data-craft]')
    page.keyboard.press('Escape')
    capture('workshop')
    passed('relocated Artisan remains reachable at the existing workshop', {'artisan': npc})

    walk(31, 30.4)
    npc = next(n for n in snap()['npcs'] if n['name'] == 'Housing Keeper')['transform']['position']
    click(npc['x'], npc['y'], 15)
    page.wait_for_selector('#rent-house')
    page.keyboard.press('Escape')
    passed('housing service remains reachable at the residential edge', {'keeper': npc})

    walk(31, 30.4)
    walk(39, 27)
    walk(39, 20)
    npc = next(n for n in snap()['npcs'] if n['name'] == 'Gatekeeper')['transform']['position']
    click(npc['x'], npc['y'], 15)
    page.wait_for_selector('[data-travel]')
    page.keyboard.press('Escape')
    capture('gate')
    walk(40.5, 16)
    click(42, 16, 17)
    page.wait_for_function('AstraeonQA.snapshot().save.zone===2')
    capture('field-threshold')
    passed('gate services and physical stone-to-field transition', {'zone': 2})

    page.evaluate('navigator.serviceWorker.ready')
    assert 'astraeon-static-v31' in page.evaluate('caches.keys()')
    saved = snap()['save']
    page.reload(wait_until='networkidle')
    page.wait_for_selector('#world')
    assert snap()['save']['name'] == saved['name']
    assert snap()['save']['zone'] == saved['zone']
    passed('v30 cache and save continuity', {'cache': 'v31'})
    context.close()
    browser.close()

report = {'checks': checks, 'runtime_errors': errors, 'resource_errors': resources}
(out / 'report.json').write_text(json.dumps(report, indent=2))
assert not errors and not resources, report
print(json.dumps({'passed': len(checks), 'artifacts': str(out), 'runtime_errors': errors, 'resource_errors': resources}, indent=2))
