"""Current normal gameplay and development-review cache isolation.

The base checkpoint already lacks the default Swordsman -001 definition.
Record that failure; exercise the existing Mage through normal UI instead.
This does not certify the unavailable production Swordsman proof.
"""
import argparse
import json
import os
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--url', default='http://127.0.0.1:8011')
parser.add_argument('--output', type=Path, default=Path('/tmp/astraeon-assembly-game'))
args = parser.parse_args(); args.output.mkdir(parents=True, exist_ok=True)
BASE = 'c258c5034a49462381d15f425f103eddf85242c9'
protected = ['game.js', 'combat.js', 'input.js', 'wardrobe.js', 'character-studio.js',
             'index.html', 'boot.js', 'sw.js', 'world', 'maps', 'blender']
subprocess.run(['git', 'diff', '--exit-code', BASE, '--', *protected], check=True,
               stdout=subprocess.PIPE)
missing = 'assets/characters/swordsman-male-001/sprite.json'
assert not subprocess.check_output(['git', 'ls-tree', BASE, missing])
assert not Path(missing).exists()
errors = []; resources = []
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=os.environ.get('ASTRAEON_BROWSER', '/usr/bin/chromium'),
        headless=True, args=['--no-sandbox', '--enable-gpu', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    context = browser.new_context(viewport={'width':1280, 'height':800})
    page = context.new_page(); page.set_default_timeout(60000)
    page.on('pageerror', lambda e:errors.append(str(e)))
    page.on('response', lambda r:resources.append(f'{r.status} {r.url}') if r.status >= 400 else None)
    page.goto(args.url.rstrip('/')+'/index.html?qa=1', wait_until='networkidle')
    page.wait_for_function("document.querySelector('#creation-studio')?.innerText.includes('Cannot load sprite definition')")
    assert page.locator('#create').is_disabled()
    baseline = {'status':'PREEXISTING_BLOCKED_DEFAULT_SWORDSMAN_CREATOR', 'base':BASE,
        'missingAsset':missing, 'ui':page.locator('#creation-studio').inner_text(),
        'resourceErrors':list(resources)}
    page.screenshot(path=str(args.output/'default-creator-baseline.png'))
    errors.clear(); resources.clear()
    page.select_option('#newclass', '12')
    page.wait_for_function("!document.querySelector('#create').disabled")
    page.locator('#newname').fill('Assembly Regression')
    page.locator('#create').click(); page.wait_for_selector('#world')
    page.wait_for_function('window.AstraeonQA && AstraeonQA.snapshot().time>1')
    assert not page.evaluate('!!window.AstraeonCharacterAssembly || !!window.AstraeonMotionTemplate')
    before = page.evaluate('AstraeonQA.snapshot()')
    page.keyboard.down('d')
    page.wait_for_function('(start)=>AstraeonQA.snapshot().time>start+.4', arg=before['time'])
    page.keyboard.up('d')
    moved = page.evaluate('AstraeonQA.snapshot()')
    assert moved['player']['distance'] > before['player']['distance']
    page.keyboard.press('f')
    page.wait_for_function('AstraeonQA.snapshot().action!==null')
    active = page.evaluate('AstraeonQA.snapshot()')
    assert active['action']['end'] > active['action']['impact']
    page.wait_for_function('AstraeonQA.snapshot().action===null')
    ordinary = page.evaluate('AstraeonQA.snapshot()')
    assert ordinary['save']['cls'] == 12
    for key in ['appearance', 'classId', 'anatomy']:
        assert ordinary['appearance'][key] == before['appearance'][key]
    page.screenshot(path=str(args.output/'mage-normal-gameplay.png'))
    page.wait_for_function('navigator.serviceWorker.controller!==null')
    review = context.new_page()
    review.goto(args.url.rstrip('/')+'/character-review.html', wait_until='networkidle')
    review.wait_for_function('window.AstraeonCharacterReview')
    review.evaluate('AstraeonCharacterReview.prepareVariants()')
    cache_state = review.evaluate('''async()=>{
      const entries=[];let entry='';
      for(const name of await caches.keys()){
        const cache=await caches.open(name);
        entries.push(...(await cache.keys()).map(k=>({name,url:k.url})));
        if(name.startsWith('astraeon-static-v'))entry=await (await cache.match('./index.html')).text();
      }
      return {debugEntries:entries.filter(k=>k.url.includes('assembly-debug')||k.url.includes('appearance/debug-')||k.url.includes('spriteDev=1')),
        gameEntryIntact:entry.includes('id="app"')&&!entry.includes('Character assembly review')};
    }''')
    assert cache_state['debugEntries'] == [] and cache_state['gameEntryIntact'], cache_state
    review.close(); context.set_offline(True)
    page.goto(args.url.rstrip('/')+'/index.html?qa=1', wait_until='networkidle')
    page.wait_for_selector('#world')
    page.wait_for_function('window.AstraeonQA && AstraeonQA.snapshot().time>1')
    offline = page.evaluate('AstraeonQA.snapshot()')
    assert offline['save']['name'] == 'Assembly Regression'
    assert offline['save']['cls'] == 12
    for key in ['appearance', 'classId', 'anatomy']:
        assert offline['appearance'][key] == ordinary['appearance'][key]
    assert not page.evaluate('!!window.AstraeonCharacterAssembly || !!window.AstraeonMotionTemplate')
    assert not errors, errors
    assert not resources, resources
    page.screenshot(path=str(args.output/'offline-after-character-review.png'))
    report = {'defaultCreator':baseline, 'protectedPathsUnchanged':protected,
        'ordinaryMageBoot':True, 'ordinaryMovement':True, 'combatAuthority':active['action'],
        'ordinaryAttack':True, 'newAssemblyAbsentFromGameBoot':True,
        'developmentCacheIsolation':cache_state, 'offlineGameAfterReview':True,
        'roProductionProof':False, 'errors':errors, 'unexpectedResourceErrors':resources}
    (args.output/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    browser.close()
print('PASS normal Mage boot/movement/Combat and offline cache isolation; default Swordsman blocked at base')
