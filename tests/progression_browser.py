"""Disposable browser acceptance for the Core Spine foundation and developer harness."""
import argparse
import json
import os
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8011')
parser.add_argument('--browser', default=os.environ.get('ASTRAEON_BROWSER',
    r'C:\Program Files\Google\Chrome\Application\chrome.exe' if os.name == 'nt' else '/usr/bin/chromium'))
parser.add_argument('--output', type=Path, default=Path(tempfile.gettempdir()) / 'astraeon-progression-browser')
parser.add_argument('--startup-timeout-ms', type=int, default=300000)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
checks, errors, http_errors = [], [], []
core = ['baseLevel', 'baseExp', 'baseJobLevel', 'baseJobExp', 'statPoints', 'skillPoints',
        'STR', 'AGI', 'VIT', 'INT', 'DEX', 'LUK', 'currentHP', 'maxHP', 'currentSP', 'maxSP', 'resourceBase']
preserved = ['inventory', 'equipment', 'gold', 'quest', 'worldClaims', 'discovered', 'skillNodes', 'zone', 'x', 'y']
def passed(name, evidence):
    checks.append({'name': name, 'evidence': evidence})
    print('PASS', name, flush=True)
def snap(page):
    return page.evaluate('AstraeonProgressionDev.snapshot()')
def elapsed(page, seconds):
    start = page.evaluate('AstraeonQA.snapshot().time')
    page.wait_for_function('(t)=>AstraeonQA.snapshot().time>=t', arg=start + seconds, timeout=60000)
def world_point(page, x, y):
    state = page.evaluate('AstraeonQA.snapshot()')
    box = page.locator('#world').bounding_box()
    view, camera = state['view'], state['camera']
    return (box['x'] + box['width']/2 + (x*view['basis']['xx'] + y*view['basis']['yx'] - camera['x'])*view['zoom'],
            box['y'] + box['height']*view['anchorY'] + (x*view['basis']['xy'] + y*view['basis']['yy'] - camera['y'])*view['zoom'])

report = {}
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.browser, headless=True,
            args=['--no-sandbox', '--enable-gpu'] + (['--use-angle=d3d11'] if os.name == 'nt'
                else ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']))
        def open_page(path, fixture=None):
            context = browser.new_context(viewport={'width':1280, 'height':800})
            if fixture:
                context.add_init_script('if(!localStorage.getItem("astraeon-iso-v1"))localStorage.setItem("astraeon-iso-v1",'
                                        + json.dumps(json.dumps(fixture)) + ')')
            page = context.new_page()
            page.set_default_timeout(args.startup_timeout_ms)
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('console', lambda m: errors.append({'text':m.text, 'location':m.location}) if m.type == 'error' else None)
            page.on('response', lambda r: http_errors.append(f'{r.status} {r.url}') if r.status >= 400 else None)
            page.goto(args.url.rstrip('/') + path, wait_until='load', timeout=args.startup_timeout_ms)
            return context, page

        context, page = open_page('/?qa=1&dev=1')
        page.wait_for_selector('#create')
        page.locator('#newname').fill('Core Spine smoke')
        page.locator('#newclass').select_option('12')
        page.locator('#create').click()
        page.wait_for_selector('#world')
        initial = snap(page)
        assert initial['baseLevel'] == initial['baseJobLevel'] == 1
        assert initial['baseExp'] == initial['baseJobExp'] == 0
        assert all(initial[key] == 1 for key in ['STR','AGI','VIT','INT','DEX','LUK'])
        passed('game boots and creates a playable canonical character', {'saveVersion':initial['saveVersion']})

        # Ordinary quest, travel, movement and combat. QA is used only for observation.
        page.locator('[data-open="journal"]').click()
        page.locator('[data-quest="2"]').click()
        page.locator('[data-open="map"]').click()
        page.locator('[data-travel="2"]').click()
        page.wait_for_function('AstraeonQA.snapshot().save.zone===2')
        before = snap(page)
        page.keyboard.down('d')
        elapsed(page, .5)
        page.keyboard.up('d')
        after = snap(page)
        assert abs(after['x']-before['x']) + abs(after['y']-before['y']) > .2
        passed('ordinary map transition and movement work', {'zone':after['zone']})
        page.mouse.click(*world_point(page, 14.5, 22))
        page.wait_for_function('Math.hypot(AstraeonQA.snapshot().save.x-14.5,AstraeonQA.snapshot().save.y-22)<.5', timeout=60000)
        before = snap(page)
        button = page.locator('[data-action="attack"]').bounding_box()
        page.mouse.move(button['x']+button['width']/2, button['y']+button['height']/2)
        page.mouse.down()
        try:
            page.wait_for_function('(kills)=>AstraeonQA.snapshot().save.kills>kills', arg=before['kills'], timeout=60000)
        finally:
            page.mouse.up()
        after = snap(page)
        assert after['baseLevel'] > before['baseLevel'] or after['baseExp'] > before['baseExp']
        assert after['baseJobLevel'] > before['baseJobLevel'] or after['baseJobExp'] > before['baseJobExp']
        assert after['gold'] > before['gold']
        assert after['quest']['progress'] > before['quest']['progress']
        page.screenshot(path=str(args.output/'field-combat.png'))
        passed('ordinary combat grants independent Base/Job EXP, loot and quest credit', {'killsAdded':after['kills']-before['kills']})

        page.locator('[data-open="map"]').click()
        page.locator('[data-travel="0"]').click()
        page.wait_for_function('AstraeonQA.snapshot().save.zone===0')
        page.locator('[data-open="character"]').click()  # Pause resources/movement for parity.
        page.evaluate('''()=>{const d=AstraeonProgressionDev;d.grantBaseExp(270);d.grantJobExp(180);d.allocateStat('STR',2);d.allocateStat('VIT',1);d.allocateStat('INT',1);const s=d.snapshot();d.setCurrentHP(s.maxHP);d.setCurrentSP(s.maxSP);d.save()}''')
        expected = snap(page)
        derived = page.evaluate('AstraeonProgressionDev.getDerivedStats()')
        stored = page.evaluate('JSON.parse(localStorage.getItem("astraeon-iso-v1"))')
        for key in core + preserved:
            assert stored[key] == expected[key], key
        page.reload(wait_until='load')
        page.wait_for_selector('#world')
        page.locator('[data-open="character"]').click()
        restored = snap(page)
        for key in core + preserved:
            assert restored[key] == expected[key], (key, restored[key], expected[key])
        assert page.evaluate('AstraeonProgressionDev.getDerivedStats()') == derived
        passed('live game developer API save/reload preserves progression, stats and world state', {'baseLevel':restored['baseLevel'],'jobLevel':restored['baseJobLevel']})
        context.close()

        legacy = {'name':'Legacy smoke','saveVersion':3,'lv':5,'xp':18,'hp':180,'maxHp':500,
            'energy':80,'maxEnergy':200,'gold':234,'cls':12,'zone':0,'x':14.5,'y':18,
            'inventory':{'ore':9,'potion':2,'token':4},'equipment':{'weapon':'Astral Blade','armor':'Warden Plate','relic':'Moonveil Sigil'},
            'quest':{'id':2,'progress':4},'worldClaims':{'supply':True},'skillNodes':{'tempest':'ice'},'discovered':[0,1,2],
            'futureProgress':{'kept':True},'techniques':[{'name':'Historical'}]}
        context, page = open_page('/?qa=1&dev=1', legacy)
        page.wait_for_selector('#world')
        page.locator('[data-open="character"]').click()
        migrated = snap(page)
        assert migrated['baseLevel'] == 5 and migrated['baseExp'] == 18
        assert migrated['maxHP'] == 500 and migrated['maxSP'] == 200
        assert migrated['statPoints'] == migrated['skillPoints'] == 0
        for key in ['equipment','quest','worldClaims','skillNodes','futureProgress','techniques','gold','discovered']:
            assert migrated[key] == legacy[key], key
        for key, value in legacy['inventory'].items():
            assert migrated['inventory'][key] == value
        page.evaluate('AstraeonProgressionDev.save()')
        page.reload(wait_until='load')
        page.wait_for_selector('#world')
        page.locator('[data-open="character"]').click()
        again = snap(page)
        for key in core:
            if key not in ['currentSP']:
                assert again[key] == migrated[key], key
        passed('legacy playable save migrates without lost inventory, gear or quests', {'maxHP':again['maxHP'],'maxSP':again['maxSP']})
        context.close()

        context, page = open_page('/tools/progression.html')
        page.wait_for_function('window.AstraeonProgressionHarness?.snapshot()?.baseLevel===1')
        page.locator('#base-exp').fill('145')
        page.locator('#grant-base').click()
        page.locator('#job-exp').fill('100')
        page.locator('#grant-job').click()
        for key in ['STR','AGI','VIT','INT','DEX','LUK']:
            page.locator('[data-stat="'+key+'"]').click()
        current = page.evaluate('AstraeonProgressionHarness.snapshot()')
        assert current['baseLevel'] == 3 and current['baseExp'] == 10
        assert current['baseJobLevel'] == 3 and current['baseJobExp'] == 10
        assert current['statPoints'] == 0 and current['skillPoints'] == 2
        assert all(current[key] == 2 for key in ['STR','AGI','VIT','INT','DEX','LUK'])
        page.locator('#reset-stats').click()
        page.locator('#reset-stats').click()
        assert page.evaluate('AstraeonProgressionHarness.snapshot().statPoints') == 6
        page.locator('[data-stat="VIT"]').click()
        expected = page.evaluate('AstraeonProgressionHarness.snapshot()')
        page.locator('#allocation').fill('-1')
        page.locator('[data-stat="STR"]').click()
        assert page.locator('#status').inner_text() != 'OK'
        assert page.evaluate('AstraeonProgressionHarness.snapshot()') == expected
        page.locator('#save').click()
        page.locator('#reload').click()
        assert page.evaluate('AstraeonProgressionHarness.snapshot()') == expected
        page.screenshot(path=str(args.output/'developer-harness.png'))
        page.reload(wait_until='load')
        assert page.evaluate('AstraeonProgressionHarness.snapshot()') == expected
        assert page.evaluate('localStorage.getItem("astraeon-iso-v1")') is None
        passed('developer harness uses shared APIs, rejects invalid allocation and persists its isolated save', {'stats':6})
        context.close()

        context, page = open_page('/?qa=1')
        page.wait_for_selector('#create')
        assert page.evaluate('typeof AstraeonProgressionDev') == 'undefined'
        passed('developer mutation API is absent on ordinary game URLs', {})
        context.close()
        browser.close()
    assert not errors and not http_errors, (errors, http_errors)
    report['result'] = 'passed'
except Exception as error:
    report['result'] = 'failed'
    report['failure'] = str(error)
    raise
finally:
    report.update(checks=checks, runtimeErrors=errors, httpErrors=http_errors)
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
