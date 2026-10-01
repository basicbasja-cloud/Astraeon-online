"""Capture quiet districts through normal navigation, with no runtime mutation."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json, argparse
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8001');parser.add_argument('--output',default='/tmp/astraeon-district-review');args=parser.parse_args()
out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox']);page=b.new_page(viewport={'width':1280,'height':800});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(args.url.rstrip('/')+'/index.html?qa=1');page.locator('#newname').fill('Golden Warrior');page.locator('#create').click();page.wait_for_selector('#world')
 def snap():return page.evaluate('AstraeonQA.snapshot()')
 def walk(x,y):
  s=snap();r=page.locator('#world').bounding_box();v=s['view'];px=r['x']+r['width']/2+(x*v['basis']['xx']+y*v['basis']['yx']-s['camera']['x'])*v['zoom'];py=r['y']+r['height']*v['anchorY']+(x*v['basis']['xy']+y*v['basis']['yy']-s['camera']['y'])*v['zoom'];page.mouse.click(px,py);page.wait_for_function('(g)=>{let p=AstraeonQA.snapshot().player.position;return Math.hypot(p.x-g[0],p.y-g[1])<.5}',arg=[x,y],timeout=20000);page.wait_for_timeout(300)
 page.wait_for_timeout(700)
 for name,path in [('plaza',[]),('shrine',[(10.2,21),(10.2,28),(6.4,29),(6.4,35.9),(3.3,36)]),('residential',[(6.4,35.9),(6.4,29),(10.2,28),(14.5,28.6),(24,28.6),(29,29)]),('inn',[(31,30.4),(32,36.7),(36,36.7)]),('workshop',[(32,36.7),(31,30.4),(34,27.5)])]:
  for x,y in path:walk(x,y)
  for width,height in [(1280,800),(390,844),(844,390),(768,1024)]:
   page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(250);page.screenshot(path=str(out/f'{name}-{width}-{height}.png'))
  page.set_viewport_size({'width':1280,'height':800});page.wait_for_timeout(250)
 print(json.dumps({'errors':errors,'out':str(out)}));b.close()
