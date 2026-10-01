"""Compare identical viewport and spawn using actual runtime frame telemetry."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import json,statistics,argparse
parser=argparse.ArgumentParser();parser.add_argument('--before-url',default='http://127.0.0.1:8006');parser.add_argument('--after-url',default='http://127.0.0.1:8005');parser.add_argument('--output',default='/tmp/astraeon-performance');args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
results={}
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for name,url in [('before',args.before_url),('after',args.after_url)]:
  c=b.new_context(viewport={'width':1280,'height':800});page=c.new_page();page.add_init_script('window.frameReports=[];addEventListener("message",e=>{if(e.data.type==="astraeon-qa")frameReports.push(e.data)})');page.goto(url.rstrip('/')+'/index.html?qa=1');page.locator('#newname').fill('Golden Warrior');page.locator('#create').click();page.wait_for_selector('#world');page.wait_for_timeout(2500);page.evaluate('frameReports=[]');page.wait_for_timeout(7000);r=page.evaluate('frameReports');results[name]={'fps_median':statistics.median(x['fps'] for x in r),'p95_ms_median':statistics.median(float(x['p95']) for x in r),'samples':r};page.screenshot(path=str(out/f'{name}.png'));c.close()
 b.close()
(out/'report.json').write_text(json.dumps(results,indent=2));print(json.dumps({k:{a:b for a,b in v.items() if a!='samples'} for k,v in results.items()},indent=2))
