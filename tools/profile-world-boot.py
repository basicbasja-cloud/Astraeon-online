"""Read-only disposable-browser boot profile; no gameplay/time/quality setters."""
import argparse, json, re, time
from pathlib import Path
from playwright.sync_api import sync_playwright

p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8011/?qa=1');p.add_argument('--output',type=Path,required=True);p.add_argument('--mobile',action='store_true');a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[1]
sw=(root/'sw.js').read_text();urls=json.loads(sw.split('const FILES =',1)[1].split(';',1)[0]) if 'const FILES =' in sw else []
precache=[{'url':u,'bytes':(root/u.split('?')[0]).stat().st_size} for u in urls if (root/u.split('?')[0]).is_file()]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--enable-precise-memory-info'])
 c=b.new_context(**(pw.devices['iPhone 13'] if a.mobile else {'viewport':{'width':910,'height':512}}));page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.add_init_script('''(()=>{
 window.bootProfile={json:[],stages:[],longTasks:[],memory:[]};
 new PerformanceObserver(list=>bootProfile.longTasks.push(...list.getEntries().map(e=>({start:e.startTime,duration:e.duration})))).observe({type:'longtask',buffered:true});
 Response.prototype.json=async function(){const start=performance.now(),text=await this.text(),downloadEnd=performance.now(),value=JSON.parse(text),end=performance.now();bootProfile.json.push({url:this.url,start,duration:end-start,bodyReadMs:downloadEnd-start,parseMs:end-downloadEnd});return value};
 const wrap=(obj,name)=>{if(!obj||obj[name]?.profiled)return;const fn=obj[name];if(!fn)return;obj[name]=function(...args){const start=performance.now();try{return fn.apply(this,args)}finally{bootProfile.stages.push({name,start,duration:performance.now()-start})}};obj[name].profiled=true};
 Object.defineProperty(window,'AstraeonSpatialRenderer',{configurable:true,set(value){Object.defineProperty(window,'AstraeonSpatialRenderer',{value,writable:true,configurable:true});wrap(value.SpatialRenderer.prototype,'mount');wrap(value.SpatialRenderer.prototype,'warmFadeMeshes')}});
 new MutationObserver(list=>{for(const r of list)for(const el of r.addedNodes)if(el.tagName==='SCRIPT')el.addEventListener('load',()=>{wrap(window.AstraeonSpatialV3,'compile');wrap(window.AstraeonTownImportV3,'content')})}).observe(document,{childList:true,subtree:true});
 setInterval(()=>{if(performance.memory)bootProfile.memory.push({at:performance.now(),heap:performance.memory.usedJSHeapSize})},100);
 })()''')
 started=time.monotonic();page.goto(a.url,wait_until='domcontentloaded',timeout=300000)
 page.locator('#newname').fill('Boot profile',timeout=300000);ui_ms=(time.monotonic()-started)*1000;page.locator('#create').click(timeout=300000)
 page.wait_for_function('document.getElementById("world") && window.AstraeonQA?.snapshot().time>0',timeout=300000);first_ms=(time.monotonic()-started)*1000
 result=page.evaluate('''()=>({profile:bootProfile,resources:performance.getEntriesByType('resource').map(e=>({name:e.name,start:e.startTime,duration:e.duration,transfer:e.transferSize,encoded:e.encodedBodySize,decoded:e.decodedBodySize})),renderer:AstraeonQA.snapshot().renderer,streaming:window.AstraeonWorldStreaming?.snapshot?.()})''')
 result.update({'url':a.url,'mobileEmulation':a.mobile,'uiReadyMs':ui_ms,'firstPlayableMs':first_ms,'errors':errors,'precache':precache,'precacheBytes':sum(x['bytes'] for x in precache),'physicalIPhone':'PENDING'})
 page.wait_for_timeout(2000)
 result['cache']=page.evaluate('''async()=>{const out=[];for(const name of await caches.keys()){const c=await caches.open(name);out.push({name,requests:(await c.keys()).map(r=>r.url)})}return out}''')
 a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'firstPlayableMs':first_ms,'uiReadyMs':ui_ms,'requests':len(result['resources']),'transferBytes':sum(r['transfer'] for r in result['resources']),'encodedResourceBytes':sum(r['encoded'] for r in result['resources']),'precacheBytes':result['precacheBytes'],'peakObservedHeap':max((m['heap'] for m in result['profile']['memory']),default=None),'json':result['profile']['json'],'stages':result['profile']['stages'],'errors':errors},indent=2),flush=True);b.close()
