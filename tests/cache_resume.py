"""Fresh cache migration and saved-character offline reload in a disposable browser.

Creates only a test character via the ordinary UI. Does not alter a user's
browser, progress, runtime state or production assets.
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8011')
parser.add_argument('--output', type=Path, default=Path('/tmp/astraeon-cache-resume'))
parser.add_argument('--startup-timeout-ms', type=int, default=120000, help='Bounded online/offline startup deadline')
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
ROOT = Path(__file__).resolve().parents[1]
version_match = re.search(r"const version='(\d+)'", (ROOT / 'boot.js').read_text())
assert version_match, 'Boot cache version is missing'
current_version = version_match.group(1)
current_cache = 'astraeon-static-v' + current_version
previous_version = str(int(current_version) - 1)
previous_cache = 'astraeon-static-v' + previous_version
errors = []
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=os.environ.get('ASTRAEON_BROWSER', '/usr/bin/chromium'), headless=True,
        args=['--no-sandbox', '--enable-gpu'] + (['--use-angle=d3d11'] if os.name == 'nt'
             else ['--use-angle=swiftshader', '--enable-unsafe-swiftshader']))
    context = browser.new_context(viewport={'width': 1280, 'height': 800})
    # Apply disposable fixtures on the next document, after the previous game's
    # pagehide autosave. Writing localStorage immediately before reload races it.
    context.add_init_script('''
      if(location.protocol==='http:'||location.protocol==='https:'){
        const fixture=sessionStorage.getItem('astraeon-cache-test-fixture');
        if(fixture){localStorage.setItem('astraeon-iso-v1',fixture);
          sessionStorage.removeItem('astraeon-cache-test-fixture');}
      }
    ''')
    page = context.new_page()
    page.set_default_timeout(60000)
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(args.url.rstrip('/') + '/icon.svg')
    page.evaluate('''async({cache,version})=>{
      const old=await caches.open(cache);
      await old.put('./boot.js?v='+version,new Response('stale boot'));
    }''', {'cache': previous_cache, 'version': previous_version})
    page.goto(args.url.rstrip('/') + '/index.html?qa=1&dev=1', wait_until='networkidle', timeout=args.startup_timeout_ms)
    page.locator('#newname').fill('Cache Resume')
    page.locator('#create').click(timeout=args.startup_timeout_ms)
    page.wait_for_selector('#world', timeout=args.startup_timeout_ms)
    page.wait_for_function('window.AstraeonQA && AstraeonQA.snapshot().time>1')
    page.evaluate('''()=>{const d=AstraeonProgressionDev;d.grantJobExp(30);d.addSkillPoints(4);
      if(!d.learnSkill('rising-edge').ok||!d.learnSkill('sword-mastery').ok)throw Error('Skill fixture learning failed');
      if(!d.assignSkill(0,'rising-edge').ok||!d.setSkillNode('rising-edge','qi').ok)throw Error('Skill fixture assignment failed');d.save();}''')
    page.evaluate('navigator.serviceWorker.ready')
    page.wait_for_function('navigator.serviceWorker.controller')
    version = page.evaluate('''async()=>{
      const keys=await caches.keys();
      const name=keys.find(k=>k.startsWith('astraeon-static-'));
      const cache=await caches.open(name);
      return {keys,name,urls:(await cache.keys()).map(r=>r.url)};
    }''')
    assert previous_cache not in version['keys'], version
    assert version['name'] == current_cache, version
    for filename in ['boot.js', 'style.css', 'world/v3/renderer.js', 'world/v3/wayfarer-spatial.json',
                     'progression-config.js', 'progression.js', 'stats.js', 'character-state.js',
                     'player-state.js', 'save-state.js', 'skill-definitions.js', 'skill-tree.js', 'skill-runtime.js',
                     'combat-resolution-config.js', 'combat-resolution.js', 'combat-runtime.js']:
        assert any(url.endswith('/' + filename + '?v=' + current_version) for url in version['urls']), filename
    world = json.loads((ROOT / 'world/v3/wayfarer-spatial.json').read_text())
    art = {material['texture']['file'] for material in world['materials'].values()
           if material.get('texture')}
    art.add(world['lighting']['groundShadow']['file'])
    for filename in art:
        assert any(url.endswith('/' + filename) for url in version['urls']), ('uncached town material', filename)
    before = page.evaluate('AstraeonQA.snapshot().save')
    legacy_migration = None
    blocked_save_recovery = None
    if world['layoutId'] == 'wayfarer-regional-capital-v75':
        # Seed an isolated source74 save, then let the ordinary load path move
        # it to the reorganized city's arrival while retaining progression.
        legacy = {**before, 'worldLayout': 'wayfarer-concept-terraced-town-v49', 'x': 54, 'y': 58}
        page.evaluate('(save)=>sessionStorage.setItem("astraeon-cache-test-fixture",JSON.stringify(save))', legacy)
        page.reload(wait_until='networkidle', timeout=args.startup_timeout_ms)
        page.wait_for_selector('#world', timeout=args.startup_timeout_ms)
        page.wait_for_function('window.AstraeonQA && AstraeonQA.snapshot().renderer', timeout=args.startup_timeout_ms)
        before = page.evaluate('AstraeonQA.snapshot().save')
        for field in ['name', 'cls', 'zone', 'lv', 'xp', 'inventory', 'equipment', 'learnedSkills', 'skillPointSpending', 'actionLoadout', 'skillPoints']:
            assert before[field] == legacy[field], ('legacy progress lost', field)
        assert before['worldLayout'] == world['layoutId'], before['worldLayout']
        assert [before['x'], before['y']] == world['spawn'][:2], ('legacy arrival', before['x'], before['y'])
        legacy_migration = {'from': legacy['worldLayout'], 'to': before['worldLayout'], 'arrival': [before['x'], before['y']], 'progressRetained': True}
    if world.get('architectureRevision') == 76:
        # The same street layout now consolidates paired houses. A save in a
        # former gap must use the ordinary blocked-position recovery, retaining
        # progression rather than leaving the character inside a new building.
        revised = {**before, 'x': 217.74, 'y': 220.0925}
        assert page.evaluate('p=>AstraeonContent.nativeWorld.spatial.blocked(p.x,p.y)', revised)
        page.evaluate('(save)=>sessionStorage.setItem("astraeon-cache-test-fixture",JSON.stringify(save))', revised)
        page.reload(wait_until='networkidle', timeout=args.startup_timeout_ms)
        page.wait_for_selector('#world', timeout=args.startup_timeout_ms)
        page.wait_for_function('window.AstraeonQA && AstraeonQA.snapshot().renderer', timeout=args.startup_timeout_ms)
        before = page.evaluate('AstraeonQA.snapshot().save')
        for field in ['name','cls','zone','lv','xp','inventory','equipment','gold','house','guild','quest','skillNodes','learnedSkills','skillPointSpending','actionLoadout','skillPoints']:
            assert before[field] == revised[field], ('blocked save lost progression',field)
        assert [before['x'],before['y']] == world['safeSpawn'][:2], ('blocked save did not recover',before['x'],before['y'])
        blocked_save_recovery = {'layout':world['layoutId'],'oldGap':[217.74,220.0925],
                                 'safeArrival':[before['x'],before['y']],'progressRetained':True}
    context.set_offline(True)
    page.reload(wait_until='networkidle', timeout=args.startup_timeout_ms)
    page.wait_for_selector('#world', timeout=args.startup_timeout_ms)
    page.wait_for_function('window.AstraeonQA && AstraeonQA.snapshot().time>1')
    after = page.evaluate('AstraeonQA.snapshot().save')
    for field in ['name', 'cls', 'zone', 'x', 'y', 'lv', 'xp', 'inventory', 'equipment',
                  'baseLevel', 'baseExp', 'baseJobLevel', 'baseJobExp', 'statPoints', 'skillPoints',
                  'STR', 'AGI', 'VIT', 'INT', 'DEX', 'LUK', 'maxHP', 'maxSP', 'resourceBase',
                  'learnedSkills', 'skillPointSpending', 'statPointSpending', 'actionLoadout', 'skillNodes', 'legacySkillControls']:
        assert field in before and after[field] == before[field], (field, before.get(field), after.get(field))
    assert page.evaluate('AstraeonProgressionDev.compileAction(0).node') == 'qi'
    ground = world['lighting']['groundShadow']
    ground_size = page.evaluate('''async file=>{
      const response=await fetch(file);
      const image=await createImageBitmap(await response.blob());
      const size=[image.width,image.height];image.close();return size;
    }''', ground['file'])
    assert ground_size == [ground['resolution']] * 2, ('stale offline shadow atlas', ground_size, ground)
    offline_digests = page.evaluate("""async files=>{
      const result={};for(const [name,url] of Object.entries(files)){
        const response=await fetch(url);if(!response.ok)throw Error('Offline asset missing: '+url);
        const digest=await crypto.subtle.digest('SHA-256',await response.arrayBuffer());
        result[name]=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
      }return result;
    }""", {'source': 'world/v3/wayfarer-spatial.json?v='+current_version, 'ground': ground['file']})
    for name,filename in [('source','world/v3/wayfarer-spatial.json'),('ground',ground['file'])]:
        with (ROOT/filename).open('rb') as f:
            expected=hashlib.file_digest(f,'sha256').hexdigest()
        assert offline_digests[name]==expected,('stale offline content',name,offline_digests[name],expected)
    page.screenshot(path=str(args.output / 'offline-town.png'))
    report = {'cache': version['name'], 'precachedRequests': len(version['urls']),
              'legacyCacheRemoved': True, 'offlineTownLoaded': True,
              'savedCharacterRetained': True, 'townMaterialFiles': sorted(art),
              'legacyTownSaveMigration': legacy_migration,
              'sameLayoutBlockedSaveRecovery': blocked_save_recovery,
              'offlineGroundSize': ground_size, 'offlineSourceSHA256': offline_digests['source'],
              'offlineGroundSHA256': offline_digests['ground'], 'errors': errors}
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    browser.close()
    assert not errors, errors
print('PASS cache migration, versioned precache and offline saved-character reload', flush=True)
