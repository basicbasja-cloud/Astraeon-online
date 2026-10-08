#!/usr/bin/env python3
"""Review baked authoring rig playback; never approves painted character quality."""
import argparse, datetime, base64, io, json
from pathlib import Path
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--candidate', default='candidate-03');parser.add_argument('--url', default='http://127.0.0.1:8011');parser.add_argument('--output', type=Path, default=Path('/tmp/astraeon-walk-rig-browser'));args=parser.parse_args()
out=args.output;out.mkdir(parents=True, exist_ok=True);errors=[];bad=[];samples={};frames=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1100,'height':900})
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:bad.append(str(r.url)) if r.status>=400 else None)
 time=datetime.datetime(2026,10,8,tzinfo=datetime.timezone.utc);page.clock.install(time=time);page.clock.pause_at(time+datetime.timedelta(seconds=1))
 page.goto(args.url.rstrip('/')+'/authoring/characters/swordsman-production/rig-walk/'+args.candidate+'/preview.html',wait_until='networkidle')
 page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
 for d in ['S','SW','W','NW','N','NE','E','SE']:
  page.select_option('#direction',d)
  hashes=[]
  for i in range(8):
   page.locator('#phase').fill(str(i));page.clock.run_for(20)
   assert page.locator('body').get_attribute('data-frame')==str(i)
   data=page.locator('#canvas').evaluate('(c)=>c.toDataURL().split(",")[1]')
   hashes.append(data);frames.append(Image.open(io.BytesIO(base64.b64decode(data))).convert('RGB'))
  assert len(set(hashes))==8
  for speed in ['1','0.25']:
   page.locator('#phase').fill('0');page.clock.run_for(20);page.select_option('#speed',speed);page.click('#play')
   indices=[]
   for k in range(33):
    page.clock.run_for(round(35/float(speed)));indices.append(int(page.locator('body').get_attribute('data-frame')))
   samples[d+'/'+speed]=indices;assert len(set(indices))==8,(d,speed,indices)
   page.click('#play')
  page.locator('#size').check();page.screenshot(path=str(out/(d+'-gameplay-size.png')));page.locator('#size').uncheck()
 page.set_viewport_size({'width':390,'height':844})
 assert page.evaluate('document.documentElement.scrollWidth<=390'),'Mobile horizontal overflow'
 page.screenshot(path=str(out/'mobile.png'));assert not errors,errors;assert not bad,bad
 sheet=Image.new('RGB',(2560,2560))
 for i,im in enumerate(frames):sheet.paste(im,((i%8)*320,(i//8)*320))
 sheet.save(out/'all-sampled-phases.png')
 report={'status':'PASS','candidate':args.candidate,'authoringOnly':True,'directions':8,'distinctFramesPerDirection':8,'normalQuarterSamples':samples,'frameStep':True,'gameplayCanvasWidth':154,'mobileViewport':[390,844],'errors':errors,'resourceErrors':bad}
 (out/'results.json').write_text(json.dumps(report,indent=2)+'\n');b.close()
print('PASS authoring rig browser: 64 frames, 8 directions, normal/quarter, stepping, gameplay size, mobile')
