"""Golden proof QA through normal inputs + read-only snapshots. Record video,
depth/visibility evidence and render-time samples; no actor teleport setters.
"""
import argparse,json,math
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8010');parser.add_argument('--output',default='/tmp/astraeon-v3-review');args=parser.parse_args();out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
checks=[];errors=[]
def snapshot(page):return page.evaluate('AstraeonProof.snapshot()')
def elapsed(page,seconds):page.wait_for_function('(time)=>AstraeonProof.snapshot().time>=time',arg=snapshot(page)['time']+seconds,timeout=30000)
def check(name,fn):
 evidence=fn();checks.append({'name':name,'evidence':evidence});print('PASS',name,flush=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 def open_scene(width=1280,height=800,video=False):
  opts={'viewport':{'width':width,'height':height},'has_touch':width<700}
  if video:opts.update(record_video_dir=str(out/'video'),record_video_size={'width':width,'height':height})
  context=browser.new_context(**opts);page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:errors.append(str(r.status)+' '+r.url) if r.status>=400 else None);page.goto(args.url+'/proof.html');page.wait_for_function('window.AstraeonProof');elapsed(page,.8);return context,page
 context,page=open_scene(video=True)
 def traverse():
  page.locator('#tools-toggle').click();page.select_option('#strategy','run');page.locator('#tools-toggle').click()
  result=[]
  for name,x,y in [('Through passage',4,8),('Hall approach',9,6.65),('Rear service',12.1,2.6),('Canopy approach',9.5,8.5),('Outside gate',4,12.2)]:
   page.locator('[data-stop="'+name+'"]').click();page.wait_for_function('AstraeonProof.snapshot().goal===null',timeout=45000);s=snapshot(page);pos=s['player']['position'];assert math.hypot(pos['x']-x,pos['y']-y)<.32,(name,pos);page.screenshot(path=str(out/(name.lower().replace(' ','-')+'.png')));result.append({'stop':name,'position':pos,'hidden':s['view']['occlusion'],'interaction':s['lastInteraction']})
  assert result[1]['interaction']=='hall-entrance',result;assert result[3]['hidden'],result
  return result
 check('authored circulation and genuine gate passage',traverse)
 def collision():
  # Click a pillar: rejected from the same shared solid used by navigation.
  before=snapshot(page)['player']['position'];point=page.evaluate('AstraeonProof.screen(2.6,10)');page.mouse.click(point['x'],point['y']);elapsed(page,.2);assert page.locator('#state').inner_text().startswith('Solid structure');assert snapshot(page)['player']['position']==before
  # Camera-relative keyboard movement drives the actor through open ground.
  page.keyboard.down('w');elapsed(page,.55);page.keyboard.up('w');elapsed(page,.15);after=snapshot(page)['player']['position'];assert math.hypot(after['x']-before['x'],after['y']-before['y'])>.4
  return {'pillarRejected':True,'keyboardDisplacement':after}
 check('collision rejection and camera-relative keyboard',collision)
 def occlusion():
  page.locator('[data-stop="Canopy approach"]').click();page.wait_for_function('AstraeonProof.snapshot().goal===null',timeout=45000);elapsed(page,.5);s=snapshot(page);assert s['view']['alphas']['canopy']<.25,s['view'];assert s['view']['alphas']['trunk']==1
  original=s['view']['shadowPolygons'];page.locator('[data-stop="Rear service"]').click();page.wait_for_function('AstraeonProof.snapshot().goal===null',timeout=45000);elapsed(page,.5);s2=snapshot(page);assert s2['view']['shadowPolygons']==original;assert s2['view']['alphas']['canopy']>.95;assert s2['view']['alphas']['hall-body']==1
  point=page.evaluate('AstraeonProof.screen(9,1.75)');page.mouse.click(point['x'],point['y']);page.wait_for_function('AstraeonProof.snapshot().goal===null',timeout=45000);elapsed(page,.5);roof=snapshot(page);assert roof['view']['alphas']['hall-roof']<.25,roof['view'];assert roof['view']['alphas']['hall-body']==1;page.screenshot(path=str(out/'roof-selective.png'))
  # Depth evidence: behind the tree sorts earlier than trunk, in front later.
  assert s['view']['actorDepth']<s['view']['partDepths']['trunk'];assert s['view']['actorDepth']<s['view']['partDepths']['canopy']
  page.locator('[data-stop="Outside gate"]').click();page.wait_for_function('AstraeonProof.snapshot().goal===null',timeout=45000);s3=snapshot(page);assert s3['view']['actorDepth']>s3['view']['partDepths']['open-span']
  return {'canopyAlpha':s['view']['alphas']['canopy'],'trunkAlpha':1,'shadowsStable':True,'actorSharesDepth':True}
 check('selective overhead visibility, shared depth and persistent shadows',occlusion)
 def contact_views():
  page.locator('#tools-toggle').click()
  for name in ['collision','navigation','occlusion','lighting']:page.locator('[data-overlay="'+name+'"]').check()
  page.screenshot(path=str(out/'shared-geometry-overlays.png'))
  page.locator('#scrub-enable').check();clips=[]
  for mode in ['walk','run','sprint']:
   page.select_option('#strategy',mode)
   for row in range(8):
    page.select_option('#facing',str(row))
    for phase in [0,.25,.5,.75]:
     page.locator('#phase').fill(str(phase));elapsed(page,.05);s=snapshot(page);assert s['frame']['row']==row;assert s['frame']['column']==int(phase*8);assert all(math.isfinite(v) for f in s['player']['feet'] for v in [f['x'],f['y'],f['z']]);assert s['frame']['clip']==s['player']['profile']['clip']
   clips.append(snapshot(page)['frame']['clip']);page.screenshot(path=str(out/('contact-'+mode+'.png')))
  assert len(set(clips))==3;page.locator('#scrub-enable').uncheck();page.locator('#tools-toggle').click();page.keyboard.down('d');elapsed(page,.45);playing=snapshot(page);page.keyboard.up('d');assert playing['player']['mode']=='movement';assert playing['player']['speed']>0;assert playing['frame']['row']==2
  return {'directions':8,'strategies':3,'sampledContacts':96,'clips':clips}
 check('animation/contact scrubber and derived overlays',contact_views)
 def performance():
  elapsed(page,3);samples=snapshot(page)['frameMs'][-120:];samples.sort();return {'renderer':snapshot(page)['renderer'],'samples':len(samples),'medianFrameMs':round(samples[len(samples)//2],2),'p95FrameMs':round(samples[int(len(samples)*.95)],2),'scope':'Headless Chromium cloud/software rendering; physical-device approval pending'}
 check('local renderer performance evidence',performance)
 page.screenshot(path=str(out/'desktop.png'));context.close()
 def responsive():
  results=[]
  for width,height in [(390,844),(844,390),(768,1024)]:
   c,page=open_scene(width,height);page.locator('[data-stop="Through passage"]').click();page.wait_for_function('AstraeonProof.snapshot().goal===null',timeout=45000);s=snapshot(page);assert abs(s['player']['position']['y']-8)<.3;assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(out/(str(width)+'x'+str(height)+'.png')));results.append({'width':width,'height':height,'passageReachable':True});c.close()
  return results
 check('portrait, landscape and tablet traversal',responsive)
 browser.close()
assert not errors,errors
(out/'report.json').write_text(json.dumps({'checks':checks,'errors':errors},indent=2)+'\n')
print('PASS',len(checks),'browser scenarios; screenshots and traversal/contact video:',out)
