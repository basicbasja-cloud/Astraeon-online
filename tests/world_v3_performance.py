"""Isolated Canvas proof frame-time sample, normal and inspected views.
No threshold here substitutes for physical-device acceptance.
"""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8010');parser.add_argument('--output',default='/tmp/astraeon-v3-performance.json');args=parser.parse_args()
results=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=browser.new_page(viewport={'width':1280,'height':800});page.goto(args.url+'/proof.html');page.wait_for_function('window.AstraeonProof')
 for inspected in [False,True]:
  if inspected:
   page.locator('#tools-toggle').click()
   for name in ['collision','navigation','occlusion','lighting']:page.locator('[data-overlay="'+name+'"]').check()
  start=page.evaluate('AstraeonProof.snapshot().time');page.wait_for_function('(start)=>AstraeonProof.snapshot().time>=start+6',arg=start,timeout=25000)
  samples=sorted(page.evaluate('AstraeonProof.snapshot().frameMs').copy()[-180:]);results.append({'mode':'all-debug-overlays' if inspected else 'normal','samples':len(samples),'medianMs':round(samples[len(samples)//2],2),'p95Ms':round(samples[int(len(samples)*.95)],2)})
 browser.close()
report={'renderer':'Canvas2D','viewport':[1280,800],'scope':'One isolated headless Chromium session in cloud/software rendering. Physical mobile hardware and public deployment remain unverified.','results':results}
Path(args.output).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
