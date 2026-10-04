"""Measure sound-on RAF timing and visible root continuity during normal input.

This detects whole-body holds between atlas poses. It does not certify the
anatomy, leg alternation or planted-foot motion of the painted artwork.
"""
import argparse,json,os,math
from pathlib import Path
from playwright.sync_api import sync_playwright
ap=argparse.ArgumentParser();ap.add_argument('--url',default='http://127.0.0.1:8011/?qa=1');ap.add_argument('--output',type=Path,default=Path('docs/review/wayfarer-v48/performance.json'));args=ap.parse_args()
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=os.environ.get('ASTRAEON_BROWSER',r'C:\Program Files\Google\Chrome\Application\chrome.exe'),headless=True,args=['--enable-gpu','--use-angle=d3d11'])
 page=b.new_page(viewport={'width':1280,'height':800});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(args.url);page.locator('#newname').fill('Sound-on performance');page.locator('#create').click();page.wait_for_function('window.AstraeonQA?.performance');page.wait_for_timeout(3000)
 page.evaluate('''()=>{window.costs=[];window.addEventListener('astraeon-frame',()=>{const q=AstraeonQA.performance();costs.push({intervalMs:q.intervalMs,updateMs:q.updateMs,drawMs:q.drawMs,occlusionMs:q.renderer.occlusionMs,renderMs:q.renderer.renderMs,assemblyMs:q.renderer.assemblyMs,actors:[...AstraeonSpatialView.actors].filter(([,a])=>a.mesh.visible&&a.motionSample).map(([id,a])=>({id,...structuredClone(a.motionSample)}))})})}''')
 page.keyboard.down('w');page.wait_for_timeout(6500);page.keyboard.up('w')
 samples=page.evaluate('costs');intervals=sorted(s['intervalMs'] for s in samples);previous={};actors={}
 for sample in samples:
  for a in sample['actors']:
   report=actors.setdefault(a['id'],{'samples':0,'movingFrames':0,'frozenBodyFrames':0,'columns':set(),'clips':set()});report['samples']+=1
   if a.get('frame'):report['columns'].add(a['frame']['column']);report['clips'].add(a['frame']['clip'])
   old=previous.get(a['id'])
   if old and math.dist(old['root'][:2],a['root'][:2])>1e-5:
    report['movingFrames']+=1
    if math.dist(old['renderedRoot'][:2],a['renderedRoot'][:2])<1e-5:report['frozenBodyFrames']+=1
   previous[a['id']]=a
 for a in actors.values():a['columns']=sorted(a['columns']);a['clips']=sorted(a['clips'])
 slow_frames=[{'index':i,'intervalMs':s['intervalMs'],'updateMs':s['updateMs'],'drawMs':s['drawMs'],'previousUpdateMs':samples[i-1]['updateMs'] if i else None,'previousDrawMs':samples[i-1]['drawMs'] if i else None,'previousOcclusionMs':samples[i-1]['occlusionMs'] if i else None,'previousRenderMs':samples[i-1]['renderMs'] if i else None,'previousAssemblyMs':samples[i-1]['assemblyMs'] if i else None} for i,s in enumerate(samples) if s['intervalMs']>30]
 report={'sound':'on','fps':1000/(sum(intervals)/len(intervals)),'p95Ms':intervals[int(len(intervals)*.95)],'maxMs':max(intervals),'updateMs':sum(s['updateMs'] for s in samples)/len(samples),'drawMs':sum(s['drawMs'] for s in samples)/len(samples),'actors':actors,'slowFrames':slow_frames,'device':page.evaluate('AstraeonQA.performance().renderer.device'),'errors':errors}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));b.close()
 assert not errors
 assert report['fps']>55 and report['p95Ms']<25 and report['maxMs']<80,report
 assert actors['player']['movingFrames']>100 and actors['player']['frozenBodyFrames']==0,report
 assert all(a['frozenBodyFrames']==0 for a in actors.values()),report
 assert all(len(a['columns'])>1 for a in actors.values() if a['movingFrames']>100),report
