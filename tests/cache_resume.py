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
    page = context.new_page()
    page.set_default_timeout(60000)
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(args.url.rstrip('/') + '/icon.svg')
    page.evaluate('''async({cache,version})=>{
      const old=await caches.open(cache);
      await old.put('./boot.js?v='+version,new Response('stale boot'));
    }''', {'cache': previous_cache, 'version': previous_version})
    page.goto(args.url.rstrip('/') + '/index.html?qa=1', wait_until='networkidle', timeout=args.startup_timeout_ms)
    page.locator('#newname').fill('Cache Resume')
    page.locator('#create').click(timeout=args.startup_timeout_ms)
    page.wait_for_selector('#world', timeout=args.startup_timeout_ms)
    page.wait_for_function('document.getElementById("world") && window.AstraeonQA && AstraeonQA.snapshot().time>1')
    page.evaluate('navigator.serviceWorker.ready')
    page.wait_for_function('navigator.serviceWorker.controller')
    version = page.evaluate('''async()=>{
      const keys=await caches.keys();
      const name=keys.find(k=>k.startsWith('astraeon-static-'));
      const cache=await caches.open(name);
      const allUrls=[];for(const key of keys)allUrls.push(...(await (await caches.open(key)).keys()).map(r=>r.url));return {keys,name,urls:(await cache.keys()).map(r=>r.url),allUrls};
    }''')
    assert previous_cache not in version['keys'], version
    assert version['name'] == current_cache, version
    for filename in ['boot.js', 'style.css', 'world/v3/renderer.js', 'world/v3/streaming.js']:
        assert any(url.endswith('/' + filename + '?v=' + current_version) for url in version['urls']), filename
    world = json.loads((ROOT / 'world/v3/wayfarer-spatial.json').read_text())
    assert not any('/streamed/' in url or '/assets/' in url or 'wayfarer-spatial.json' in url for url in version['urls']), 'Static precache contains world assets'
    assert not any('wayfarer-spatial.json' in url for url in version['allUrls']), 'Monolithic world cached'
    art = set(page.evaluate("""()=>[...new Set([...AstraeonSpatialView.chunkNodes.values()].flat().map(m=>AstraeonSpatialView.source.materials[m.userData.materialName]?.texture?.file).filter(Boolean))]"""))
    art.add(world['lighting']['groundShadow']['file'])
    page.wait_for_function("""async files=>{const urls=[];for(const name of await caches.keys())urls.push(...(await (await caches.open(name)).keys()).map(r=>r.url));return files.every(file=>urls.some(url=>url.endsWith('/'+file)))}""",arg=sorted(art),timeout=30000)
    version['allUrls']=page.evaluate("""async()=>{const urls=[];for(const name of await caches.keys())urls.push(...(await (await caches.open(name)).keys()).map(r=>r.url));return urls}""")
    (args.output/'cache-inventory.json').write_text(json.dumps({'version':version,'activeArt':sorted(art)},indent=2)+'\n')
    for filename in art:
        assert any(url.endswith('/' + filename) for url in version['allUrls']), ('uncached active town material', filename)
    assert any('/streamed/' in url and url.endswith('.bin.gz') for url in version['allUrls']), 'No on-demand chunks cached'
    before = page.evaluate('AstraeonQA.snapshot().save')
    legacy_migration = None
    blocked_save_recovery = None
    if world['layoutId'] == 'wayfarer-regional-capital-v75':
        # Seed an isolated source74 save, then let the ordinary load path move
        # it to the reorganized city's arrival while retaining progression.
        legacy = {**before, 'worldLayout': 'wayfarer-concept-terraced-town-v49', 'x': 54, 'y': 58}
        page.add_init_script('if(!sessionStorage.getItem("cache-legacy-fixture")){localStorage.setItem("astraeon-iso-v1",'+json.dumps(json.dumps(legacy))+');sessionStorage.setItem("cache-legacy-fixture","done")}')
        page.reload(wait_until='networkidle', timeout=args.startup_timeout_ms)
        page.wait_for_function('document.getElementById("world") && window.AstraeonQA && AstraeonQA.snapshot().renderer', timeout=args.startup_timeout_ms)
        before = page.evaluate('AstraeonQA.snapshot().save')
        for field in ['name', 'cls', 'zone', 'lv', 'xp', 'inventory', 'equipment']:
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
        page.add_init_script('if(!sessionStorage.getItem("cache-blocked-fixture")){localStorage.setItem("astraeon-iso-v1",'+json.dumps(json.dumps(revised))+');sessionStorage.setItem("cache-blocked-fixture","done")}')
        page.reload(wait_until='networkidle', timeout=args.startup_timeout_ms)
        page.wait_for_function('document.getElementById("world") && window.AstraeonQA && AstraeonQA.snapshot().renderer', timeout=args.startup_timeout_ms)
        before = page.evaluate('AstraeonQA.snapshot().save')
        for field in ['name','cls','zone','lv','xp','inventory','equipment','gold','house','guild','quest','skillNodes']:
            assert before[field] == revised[field], ('blocked save lost progression',field)
        assert [before['x'],before['y']] == world['safeSpawn'][:2], ('blocked save did not recover',before['x'],before['y'])
        blocked_save_recovery = {'layout':world['layoutId'],'oldGap':[217.74,220.0925],
                                 'safeArrival':[before['x'],before['y']],'progressRetained':True}
    context.set_offline(True)
    page.reload(wait_until='networkidle', timeout=args.startup_timeout_ms)
    page.wait_for_selector('#world', timeout=args.startup_timeout_ms)
    page.wait_for_function('document.getElementById("world") && window.AstraeonQA && AstraeonQA.snapshot().time>1')
    after = page.evaluate('AstraeonQA.snapshot().save')
    for field in ['name', 'cls', 'zone', 'x', 'y', 'lv', 'xp', 'inventory', 'equipment']:
        assert field in before and after[field] == before[field], (field, before.get(field), after.get(field))
    ground = world['lighting']['groundShadow']
    ground_size = page.evaluate('''async file=>{
      const response=await fetch(file);
      const image=await createImageBitmap(await response.blob());
      const size=[image.width,image.height];image.close();return size;
    }''', ground['file'])
    assert ground_size == [ground['resolution']] * 2, ('stale offline shadow atlas', ground_size, ground)
    manifest = json.loads((ROOT/'world/v3/world-manifest.json').read_text())
    zone = json.loads((ROOT/manifest['zones'][manifest['defaultZone']]['url']).read_text())
    offline_digests = page.evaluate("""async files=>{
      const result={};for(const [name,url] of Object.entries(files)){
        const response=await fetch(url);if(!response.ok)throw Error('Offline asset missing: '+url);
        const digest=await crypto.subtle.digest('SHA-256',await response.arrayBuffer());
        result[name]=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
      }return result;
    }""", {'semantics': zone['semantics']['url'], 'ground': ground['file']})
    for name,filename in [('semantics',zone['semantics']['url']),('ground',ground['file'])]:
        with (ROOT/filename).open('rb') as f:
            expected=hashlib.file_digest(f,'sha256').hexdigest()
        assert offline_digests[name]==expected,('stale offline content',name,offline_digests[name],expected)
    page.screenshot(path=str(args.output / 'offline-town.png'))
    report = {'cache': version['name'], 'precachedRequests': len(version['urls']),
              'legacyCacheRemoved': True, 'offlineTownLoaded': True,
              'savedCharacterRetained': True, 'townMaterialFiles': sorted(art),
              'legacyTownSaveMigration': legacy_migration,
              'sameLayoutBlockedSaveRecovery': blocked_save_recovery,
              'offlineGroundSize': ground_size, 'offlineSemanticSHA256': offline_digests['semantics'],
              'authoredSourceSHA256': zone['sourceSHA256'],
              'onDemandWorldURLs': [u for u in version['allUrls'] if '/streamed/' in u],
              'fullWorldAbsentFromCache': True,
              'offlineGroundSHA256': offline_digests['ground'], 'errors': errors}
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    browser.close()
    assert not errors, errors
print('PASS shell-only precache, on-demand chunk cache, migration and offline saved-character reload', flush=True)
