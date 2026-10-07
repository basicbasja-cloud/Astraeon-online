"""Read-only disposable-browser boot profile; no gameplay/time/quality setters."""
import argparse, json, re, time, threading, http.server, functools
from pathlib import Path
from playwright.sync_api import sync_playwright

p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8011/?qa=1');p.add_argument('--output',type=Path,required=True);p.add_argument('--mobile',action='store_true');p.add_argument('--audit-local-network',action='store_true',help='Serve the unchanged project on a disposable local port and count actual HTTP body writes, including service worker traffic');p.add_argument('--fail-chunk-attempts',type=int,default=0,help='Inject this many503 responses for a spawn chunk on the disposable audit server');a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
root=Path(__file__).resolve().parents[1]
body_writes=[];network_requests=[];injected_failures=[];audit_server=None
assert 0<=a.fail_chunk_attempts<=2 and (not a.fail_chunk_attempts or a.audit_local_network)
if a.audit_local_network:
 class AuditedHandler(http.server.SimpleHTTPRequestHandler):
  def log_message(self,*args):pass
  def do_GET(self):
   network_requests.append({'url':self.path,'startEpochMs':time.time()*1000})
   if 'c0_4-' in self.path and self.path.endswith('.bin.gz') and len(injected_failures)<a.fail_chunk_attempts:
    injected_failures.append(self.path);data=b'transient chunk failure';self.send_response(503);self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);body_writes.append({'url':self.path,'epochMs':time.time()*1000,'bytes':len(data)});return
   super().do_GET()
  def copyfile(self,source,outputfile):
   while data:=source.read(65536):
    outputfile.write(data);body_writes.append({'url':self.path,'epochMs':time.time()*1000,'bytes':len(data)})
 audit_server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(AuditedHandler,directory=str(root)))
 threading.Thread(target=audit_server.serve_forever,daemon=True).start();a.url=f'http://127.0.0.1:{audit_server.server_port}/?qa=1'
sw=(root/'sw.js').read_text();urls=json.loads(sw.split('const FILES =',1)[1].split(';',1)[0]) if 'const FILES =' in sw else []
precache=[{'url':u,'bytes':(root/u.split('?')[0]).stat().st_size} for u in urls if (root/u.split('?')[0]).is_file()]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--enable-precise-memory-info'])
 c=b.new_context(**(pw.devices['iPhone 13'] if a.mobile else {'viewport':{'width':910,'height':512}}));page=c.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.add_init_script('''(()=>{
 window.bootProfile={json:[],parses:[],stages:[],longTasks:[],memory:[]};
 const parse=JSON.parse;JSON.parse=function(input,reviver){const start=performance.now();try{return parse.call(this,input,reviver)}finally{if(typeof input==='string'&&input.length>4096)bootProfile.parses.push({characters:input.length,start,duration:performance.now()-start})}};
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
 observed_epoch_ms=time.time()*1000
 result=page.evaluate('''()=>({timeOrigin:performance.timeOrigin,profile:bootProfile,resources:performance.getEntriesByType('resource').map(e=>({name:e.name,start:e.startTime,duration:e.duration,transfer:e.transferSize,encoded:e.encodedBodySize,decoded:e.decodedBodySize})),renderer:AstraeonQA.snapshot().renderer,streaming:window.AstraeonWorldStreaming?.snapshot?.(),uniqueChunkMeshes:!window.AstraeonSpatialView?.chunkNodes||(()=>{const names=[...AstraeonSpatialView.chunkNodes.values()].flat().map(m=>m.name);return names.length===new Set(names).size})()})''')
 result.update({'url':a.url,'mobileEmulation':a.mobile,'uiReadyMs':ui_ms,'firstPlayableMs':first_ms,'errors':errors,'precache':precache,'precacheBytes':sum(x['bytes'] for x in precache),'physicalIPhone':'PENDING'})
 page.wait_for_timeout(2000)
 result['cache']=page.evaluate('''async()=>{const out=[];for(const name of await caches.keys()){const c=await caches.open(name);out.push({name,requests:(await c.keys()).map(r=>r.url)})}return out}''')
 if audit_server:
  marker=result.get('streaming',{}).get('firstPlayable',{});cutoff=result['timeOrigin']+marker['at'] if isinstance(marker,dict) and 'at' in marker else observed_epoch_ms
  critical=[w for w in body_writes if w['epochMs']<=cutoff];observed=[w for w in body_writes if w['epochMs']<=observed_epoch_ms]
  paths={w['url'] for w in critical};result['httpBodyAudit']={'scope':'All local server response body writes, including service worker install/runtime fetches; no HTTP header bytes or physical network timing','cutoff':'runtime spawn-visible-ready marker' if marker else 'observed first gameplay frame','cutoffEpochMs':cutoff,'bytesBeforeReady':sum(w['bytes'] for w in critical),'bytesBeforeObservedFrame':sum(w['bytes'] for w in observed),'criticalURLs':sorted(paths),'requestsStartedBeforeReady':[r for r in network_requests if r['startEpochMs']<=cutoff],'monolithicWorldRequested':any('wayfarer-spatial.json' in r['url'] for r in network_requests)}
  audit_server.shutdown()
  result['injectedChunkFailures']=injected_failures
  if a.fail_chunk_attempts:assert len(injected_failures)==a.fail_chunk_attempts and result['streaming']['retries']>=a.fail_chunk_attempts and not result['streaming']['failures'] and result['uniqueChunkMeshes'] and not errors,result
 a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'firstPlayableMs':first_ms,'uiReadyMs':ui_ms,'requests':len(result['resources']),'transferBytes':sum(r['transfer'] for r in result['resources']),'encodedResourceBytes':sum(r['encoded'] for r in result['resources']),'precacheBytes':result['precacheBytes'],'peakObservedHeap':max((m['heap'] for m in result['profile']['memory']),default=None),'json':result['profile']['json'],'stages':result['profile']['stages'],'errors':errors},indent=2),flush=True);b.close()
