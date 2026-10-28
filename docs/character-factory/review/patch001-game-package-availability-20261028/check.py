"""Read-only browser probe against a running local server; captures package absence."""
import argparse,json,subprocess
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError
from playwright.sync_api import sync_playwright
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8011');p.add_argument('--output',type=Path,default=Path(__file__).resolve().parent);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);base=a.url.rstrip('/');packages=[]
for klass in ['swordsman','mage','archer']:
 for sex in ['male','female']:
  path=f'/assets/characters/{klass}-{sex}-patch001/sprite.json'
  try:
   with urlopen(base+path) as response: status=response.status
  except HTTPError as error:status=error.code
  tracked = subprocess.run(['git','cat-file','-e','HEAD:'+path.lstrip('/')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode == 0
  packages.append({'class':klass,'sex':sex,'path':path,'http_status':status,'present_in_head_tree':tracked})
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']);page=browser.new_page(viewport={'width':1280,'height':800});page.set_default_timeout(120000);errors=[];responses=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:responses.append({'url':r.url,'status':r.status}) if r.status>=400 else None);page.goto(base+'/index.html?qa=1',wait_until='networkidle');classes=[]
 for name,value in [('Swordsman','0'),('Mage','12'),('Archer','3')]:
  page.locator('#newclass').select_option(value);page.wait_for_timeout(3000);page.screenshot(path=str(a.output/(name.lower()+'-creation.png')));classes.append({'class':name,'selected':page.locator('#newclass').input_value(),'create_disabled':page.locator('#create').is_disabled(),'hint':page.locator('#classhint').inner_text()})
 browser.close()
result={'status':'GAME_CREATION_PACKAGE_AVAILABILITY_DIAGNOSTIC','repository_checkout':'sparse checkout; HEAD tree inspected individually for each requested path','packages':packages,'classes':classes,'http_errors':responses,'page_errors':errors,'gameplay_tested':False,'visual_acceptance':False,'runtime_admitted':False};(a.output/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
