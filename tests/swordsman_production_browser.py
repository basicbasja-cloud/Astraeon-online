#!/usr/bin/env python3
"""Capture actual modular preview output; technical evidence, not visual approval."""
import argparse,json,base64,io,datetime
from pathlib import Path
from PIL import Image,ImageDraw
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('clip');parser.add_argument('candidate');parser.add_argument('--url',default='http://127.0.0.1:8011');parser.add_argument('--output',type=Path);args=parser.parse_args()
out=args.output or Path(__file__).resolve().parents[1]/'authoring/characters/swordsman-production/male/motion-candidates'/args.clip/args.candidate/'browser';out.mkdir(parents=True,exist_ok=True);errors=[];report={}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1100,'height':900});page.on('pageerror',lambda e:errors.append(str(e)));page.clock.install(time=datetime.datetime(2026,10,8,tzinfo=datetime.timezone.utc));page.clock.pause_at(datetime.datetime(2026,10,8,0,0,1,tzinfo=datetime.timezone.utc));page.goto(args.url.rstrip('/')+'/sprite-preview.html',wait_until='networkidle');page.wait_for_function('window.AstraeonSpritePreview');page.select_option('#character','swordsman-male-candidate');page.wait_for_function('document.getElementById("status").textContent.includes("swordsman-male-candidate / Idle")');page.select_option('#animation',args.clip);page.wait_for_function('(clip)=>document.getElementById("status").textContent.includes(" / "+clip+" /")',arg=args.clip);page.locator('#sockets').uncheck();count=page.evaluate('Number(document.getElementById("frame").max)+1');timeline=page.evaluate('AstraeonSpritePreview.timeline()');step=min(timeline['durations']);ticks=round(timeline['totalMs']/(step/3))+3
 sheet=Image.new('RGB',(count*320,8*280),(31,48,60));sampled={}
 for row,d in enumerate(['S','SW','W','NW','N','NE','E','SE']):
  page.select_option('#direction',d)
  for frame in range(count):
   page.locator('#frame').fill(str(frame));snap=page.evaluate('AstraeonSpritePreview.snapshot()');assert snap['sockets']['root']==[160,264];assert snap['bodyVariant']=='male';assert snap['classId']=='Swordsman'
   data=page.locator('#sprite').evaluate('(c)=>c.toDataURL().split(",")[1]');im=Image.open(io.BytesIO(base64.b64decode(data))).crop((190,150,530,455)).resize((290,260));sheet.paste(im,(frame*320,row*280));ImageDraw.Draw(sheet).text((frame*320+5,row*280+264),f'{d}/{frame}',fill='white')
  for speed in ['1','0.25']:
   page.locator('#frame').fill('0');page.select_option('#playback',speed);indices=[]
   for tick in range(ticks):
    page.clock.run_for(round(step/float(speed)/3));indices.append(page.evaluate('AstraeonSpritePreview.snapshot().frameIndex'))
   sampled[d+'/'+speed]=indices;assert len(set(indices))==count,(d,speed,indices);
   if not timeline['loop']:
    page.clock.run_for(round(timeline['totalMs']/float(speed)));assert page.evaluate('AstraeonSpritePreview.snapshot().frameIndex')==count-1
   page.select_option('#playback','0')
  page.locator('#gameplay-scale').check();page.screenshot(path=str(out/f'{d}-gameplay-size.png'));page.locator('#gameplay-scale').uncheck()
 sheet.save(out/'frames.png');page.select_option('#direction','S');page.screenshot(path=str(out/'preview.png'));assert not errors,errors
 (out/'results.json').write_text(json.dumps({'normalQuarterSamples':sampled,'timeline':timeline,'errors':errors,'directions':8,'framesPerDirection':count,'root':[160,264],'gameplayHeightPixels':70*92/76},indent=2)+'\n');b.close()
print('PASS',args.clip,'browser all frames, normal/quarter playback, directions and gameplay size')
