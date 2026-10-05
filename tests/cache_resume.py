"""Fresh cache migration and saved-character offline reload in a disposable browser.

Creates only a test character via the ordinary UI. Does not alter a user's
browser, progress, runtime state or production assets.
"""
import argparse
import json
import os
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8011')
parser.add_argument('--output', type=Path, default=Path('/tmp/astraeon-cache-resume'))
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
    page.goto(args.url.rstrip('/') + '/index.html?qa=1', wait_until='networkidle')
    page.locator('#newname').fill('Cache Resume')
    page.locator('#create').click()
    page.wait_for_selector('#world')
    page.wait_for_function('window.AstraeonQA && AstraeonQA.snapshot().time>1')
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
    for filename in ['boot.js', 'style.css', 'world/v3/renderer.js', 'world/v3/wayfarer-spatial.json']:
        assert any(url.endswith('/' + filename + '?v=' + current_version) for url in version['urls']), filename
    before = page.evaluate('AstraeonQA.snapshot().save')
    context.set_offline(True)
    page.reload(wait_until='networkidle')
    page.wait_for_selector('#world')
    page.wait_for_function('window.AstraeonQA && AstraeonQA.snapshot().time>1')
    after = page.evaluate('AstraeonQA.snapshot().save')
    for field in ['name', 'cls', 'zone', 'x', 'y', 'lv', 'xp', 'inventory', 'equipment']:
        assert field in before and after[field] == before[field], (field, before.get(field), after.get(field))
    page.screenshot(path=str(args.output / 'offline-town.png'))
    report = {'cache': version['name'], 'precachedRequests': len(version['urls']),
              'legacyCacheRemoved': True, 'offlineTownLoaded': True,
              'savedCharacterRetained': True, 'errors': errors}
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    browser.close()
    assert not errors, errors
print('PASS cache migration, versioned precache and offline saved-character reload', flush=True)
