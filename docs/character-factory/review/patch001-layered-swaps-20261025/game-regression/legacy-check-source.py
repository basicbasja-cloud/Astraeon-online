import json
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path('/workspace/Astraeon-online/docs/character-factory/review/patch001-layered-swaps-20261025/game-regression');out.mkdir(exist_ok=True)
cases=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 for cls in [0,3,12]:
  context=browser.new_context(viewport={'width':1280,'height':800});context.add_init_script('if(!localStorage.getItem("astraeon-iso-v1"))localStorage.setItem("astraeon-iso-v1",'+json.dumps(json.dumps({'name':'Layered legacy check','cls':cls,'saveVersion':2})) +')')
  page=context.new_page();errors=[];resources=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:resources.append(str(r.status)+' '+r.url)if r.status>=400 else None)
  page.goto('http://127.0.0.1:8011/index.html?qa=1',wait_until='networkidle');page.wait_for_selector('#world',timeout=120000);page.wait_for_function('window.AstraeonQA && AstraeonQA.snapshot().time>1')
  before=page.evaluate('AstraeonQA.snapshot()');page.keyboard.down('d');page.wait_for_function('(time)=>AstraeonQA.snapshot().time>time+.5',arg=before['time']);page.keyboard.up('d');after=page.evaluate('AstraeonQA.snapshot()')
  assert after['player']['distance']>before['player']['distance']
  expected='cast' if cls==12 else 'attack'
  page.keyboard.press('f');page.wait_for_function('(state)=>AstraeonQA.snapshot().animation.state===state',arg=expected);page.wait_for_function('(state)=>AstraeonQA.snapshot().animation.state!==state',arg=expected)
  page.screenshot(path=str(out/f'legacy-class-{cls}.png'));assert not errors,errors;assert not resources,resources
  cases.append({'class_id':cls,'legacy_movement':True,'legacy_attack':True,'expected_basic_state':expected,'page_errors':errors,'resource_errors':resources});context.close()
 browser.close()
(out/'legacy-report.json').write_text(json.dumps({'scope':'Legacy save compatibility only, no new patch character or sex variant admitted','cases':cases},indent=2)+'\n')
print('PASS legacy movement and attack, classes 0, 3, 12')
