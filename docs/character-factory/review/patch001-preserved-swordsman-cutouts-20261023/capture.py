from pathlib import Path
import json
from playwright.sync_api import sync_playwright

out=Path('docs/character-factory/review/patch001-preserved-swordsman-cutouts-20261023')
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1320,'height':1000});errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto('http://127.0.0.1:8011/'+str(out)+'/index.html')
    page.wait_for_function('window.preservedSwordsmanReport!==undefined',timeout=180000)
    report=page.evaluate('window.preservedSwordsmanReport')
    if report['status']!='FAIL':
        page.wait_for_function('window.setPreservedSwordsmanFrame!==undefined')
        page.evaluate("window.setPreservedSwordsmanFrame('BasicAttack','SE',7)")
        page.screenshot(path=str(out/'browser-basicattack.png'),full_page=True)
        page.evaluate("window.setPreservedSwordsmanFrame('SkillOverhead','SE',4)")
        page.screenshot(path=str(out/'browser-skilloverhead.png'),full_page=True)
        page.locator('#weapon').uncheck();page.locator('#head').uncheck()
        page.wait_for_timeout(100)
        page.screenshot(path=str(out/'head-weapon-removed.png'),full_page=True)
    report['page_errors']=errors
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    browser.close()
    print(json.dumps({k:v for k,v in report.items()if k!='checks'}))
    assert report['status']=='ACTUAL_PRESERVED_ART_COMPOSITOR_PASS_NOT_FULL_CHARACTER_ACCEPTANCE' and not errors
