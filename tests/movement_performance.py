"""Measure complete RAF intervals with sound on, without cloning the full QA world.

Normal keyboard movement only. Rendered sole coordinates refer to pixels in the
registered artwork; the old procedural-foot tests cannot establish this contact.
"""
import argparse,json,os
from pathlib import Path
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8011/?qa=1');ap.add_argument('--output',type=Path,default=Path('docs/review/wayfarer-v44/performance-final.json'));args=ap.parse_args()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('ASTRAEON_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe'),headless=True,args=['--enable-gpu','--use-angle=d3d11'])
 page=b.new_page(viewport={'width':1280,'height':800});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(args.url);page.locator('#newname').fill('Sound-on performance');page.locator('#create').click();page.wait_for_function('window.AstraeonQA?.performance');page.wait_for_timeout(3000)
 page.evaluate('''()=>{window.costs=[];window.addEventListener('astraeon-frame',()=>{const q=AstraeonQA.performance(),a=AstraeonSpatialView.actors.get('player');costs.push({intervalMs:q.intervalMs,updateMs:q.updateMs,drawMs:q.drawMs,contact:a?.paintedContact})})}''')
 page.keyboard.down('w');page.wait_for_timeout(6500);page.keyboard.up('w')
 samples=page.evaluate('costs');intervals=sorted(s['intervalMs'] for s in samples);contacts=[s['contact'] for s in samples if s.get('contact')];drift=[]
 for a,c in zip(contacts,contacts[1:]):
  if a['key']==c['key']:drift.append(sum((x-y)**2 for x,y in zip(a['actual'],c['actual']))**.5)
 report={'sound':'on','fps':1000/(sum(intervals)/len(intervals)),'p95Ms':intervals[int(len(intervals)*.95)],'maxMs':max(intervals),'updateMs':sum(s['updateMs'] for s in samples)/len(samples),'drawMs':sum(s['drawMs'] for s in samples)/len(samples),'renderedSoleSamples':len(contacts),'maxSoleErrorWorld':max(c['error'] for c in contacts),'maxStanceDriftWorld':max(drift or [0]),'device':page.evaluate('AstraeonQA.performance().renderer.device'),'errors':errors}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));b.close()
 assert not errors
 assert report['fps']>55 and report['p95Ms']<25 and report['maxMs']<80,report
 assert report['renderedSoleSamples']>100 and report['maxSoleErrorWorld']<.025 and report['maxStanceDriftWorld']<.025,report
