"""Exercise all 64 native study poses through the actual game compositor."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path(__file__).resolve().parent
with sync_playwright()as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1280,'height':1000});errors=[];resources=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.on('response',lambda response:resources.append({'status':response.status,'url':response.url})if response.status>=400 else None)
    page.goto('http://127.0.0.1:8011/docs/character-factory/review/patch001-native-walk-20261026/index.html',wait_until='networkidle')
    report=page.evaluate('window.factoryAudit')
    assert report['status']=='COMPOSITOR_PASS_NOT_ART_APPROVAL',report
    assert report['poses']==32 and report['comparisons']==64,report
    for role in ['head','weapon']:
        page.locator('#'+role).uncheck();page.wait_for_timeout(100);page.locator('#'+role).check()
    page.locator('#variant').select_option('female');page.locator('#play').click()
    page.screenshot(path=str(out/'browser.png'),full_page=True)
    assert not errors,errors
    assert not resources,resources
    report.update({'page_errors':errors,'resource_errors':resources,'head_and_weapon_toggles_exercised':True})
    (out/'browser-report.json').write_text(json.dumps(report,indent=2)+'\n')
    browser.close()
print(json.dumps(report))
