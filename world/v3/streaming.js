/* Immutable authored chunks. Gameplay metadata stays stable while render buffers
 * have bounded, explicit ownership. No quality, density or simulation changes. */
(() => {
'use strict';
const sha=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');
async function read(url,expected){
 const started=performance.now(),controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),20000);
 try{const response=await fetch(url,{signal:controller.signal});if(!response.ok)throw Error('World request failed: '+response.status);const bytes=await response.arrayBuffer();if(expected&&(bytes.byteLength!==expected.bytes||await sha(bytes)!==expected.sha256))throw Error('World content integrity failed: '+url);return {bytes,ms:performance.now()-started}}finally{clearTimeout(timeout)}
}
async function json(url,expected){const result=await read(url,expected);return JSON.parse(new TextDecoder().decode(result.bytes))}
const near=(bounds,p,r)=>bounds[0]<=p.x+r&&bounds[3]>=p.x-r&&bounds[1]<=p.y+r&&bounds[4]>=p.y-r;
class ZoneStream{
 constructor(zone){this.active=false;this.zone=zone;this.loaded=new Map();this.inflight=new Map();this.pins=new Map();this.failures=new Map();this.queue=[];this.running=0;this.generation=0;this.required=new Set();this.retained=new Set();this.firstPlayable=false;this.readyForMovement=true;this.metrics={loads:0,unloads:0,reloads:0,retries:0,downloadBytes:0,decodedBytes:0,peakDecodedBytes:0,events:[]};this.visited=new Set();this.decoderSupported=typeof DecompressionStream==='function';}
 getChunkForPosition(x,y){return 'c'+Math.floor(x/this.zone.cellSize)+'_'+Math.floor(y/this.zone.cellSize)}
 retain(id){this.pins.set(id,(this.pins.get(id)||0)+1);let released=false;return ()=>{if(released)return;released=true;const n=this.pins.get(id)-1;if(n)this.pins.set(id,n);else this.pins.delete(id)}}
 async ensureRenderer(){if(this.renderer)return this.renderer;if(!this.rendererPromise)this.rendererPromise=Promise.resolve().then(()=>this.createRenderer()).then(renderer=>this.renderer=renderer).catch(error=>{this.rendererPromise=null;throw error});return this.rendererPromise}
 async loadChunk(id,priority=false){
  if(this.loaded.has(id))return this.loaded.get(id);if(this.inflight.has(id))return this.inflight.get(id);
  const record=this.zone.chunks.find(c=>c.id===id);if(!record)throw Error('Unknown world chunk '+id);
  const job=new Promise((resolve,reject)=>{const task={record,resolve,reject};priority?this.queue.unshift(task):this.queue.push(task);this.pump()}).finally(()=>this.inflight.delete(id));this.inflight.set(id,job);return job;
 }
 pump(){while(this.running<2&&this.queue.length){const task=this.queue.shift();this.running++;this.install(task.record).then(task.resolve,task.reject).finally(()=>{this.running--;this.pump()})}}
 async install(record){
  let error;for(let attempt=0;attempt<3;attempt++){
   try{if(!this.decoderSupported)throw Error('This browser needs gzip streaming support. Please update Safari.');const manifest=await json(record.url,record),download=await read(manifest.binary.url,manifest.binary),blob=new Blob([download.bytes]),bytes=await new Response(blob.stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer();if(bytes.byteLength!==manifest.binary.decodedBytes)throw Error('Invalid decoded world buffer');
    if(!this.active&&!this.pins.has(record.id))return null;const renderer=await this.ensureRenderer();await renderer.addChunk(manifest,bytes);const entry={record,manifest,loadedAt:performance.now(),lastUsed:performance.now()};this.loaded.set(record.id,entry);this.failures.delete(record.id);this.metrics.loads++;if(this.visited.has(record.id))this.metrics.reloads++;this.visited.add(record.id);this.metrics.downloadBytes+=download.bytes.byteLength;this.metrics.decodedBytes+=bytes.byteLength;this.metrics.peakDecodedBytes=Math.max(this.metrics.peakDecodedBytes,this.metrics.decodedBytes);this.event('load',record.id);return entry;
   }catch(e){error=e;if(attempt<2&&this.decoderSupported){this.metrics.retries++;await new Promise(resolve=>setTimeout(resolve,300*(attempt+1)))}else break}
  }this.failures.set(record.id,{message:error.message,at:performance.now()});this.event('failure',record.id);throw error;
 }
 event(type,id){this.metrics.events.push({type,id,at:performance.now()});if(this.metrics.events.length>150)this.metrics.events.shift()}
 unloadChunk(id){if(this.pins.has(id)||this.required.has(id)||this.retained.has(id)||!this.loaded.has(id))return false;const entry=this.loaded.get(id);this.renderer.removeChunk(id);this.loaded.delete(id);this.metrics.decodedBytes-=entry.manifest.binary.decodedBytes;this.metrics.unloads++;this.event('unload',id);return true}
 prefetchChunk(id){if(this.failures.has(id)&&performance.now()-this.failures.get(id).at<5000)return;return this.loadChunk(id).catch(()=>null)}
 prefetchNeighbors(point){for(const c of this.zone.chunks)if(c.id==='global'||near(c.bounds,point,48))this.prefetchChunk(c.id)}
 async ensureAt(point){
  this.active=true;const renderer=await this.ensureRenderer(),generation=++this.generation,needed=this.zone.chunks.filter(c=>c.id==='global'||near(c.bounds,point,38)),releases=needed.map(c=>this.retain(c.id));
  try{await Promise.all(needed.map(c=>this.loadChunk(c.id,true)));await renderer.whenReady;if(generation===this.generation){this.required=new Set(needed.map(c=>c.id));this.retained=new Set(this.required);this.readyForMovement=true}return true}finally{for(const release of releases)release()}
 }
 tick(frustum,point,boxFor){
  const now=performance.now(),view=this.zone.chunks.filter(c=>c.id==='global'||frustum.intersectsBox(boxFor(c.bounds))),needed=this.zone.chunks.filter(c=>c.id==='global'||near(c.bounds,point,24)||view.includes(c)),retained=this.zone.chunks.filter(c=>c.id==='global'||near(c.bounds,point,64)||view.includes(c));
  this.required=new Set(needed.map(c=>c.id));this.retained=new Set(retained.map(c=>c.id));
  for(const c of needed){const entry=this.loaded.get(c.id);if(entry)entry.lastUsed=now;else if(!this.failures.has(c.id)||now-this.failures.get(c.id).at>5000)this.loadChunk(c.id,true).catch(()=>null)}
  this.readyForMovement=view.every(c=>this.loaded.has(c.id));this.status(!this.readyForMovement);
  if(this.firstPlayable){for(const c of retained)if(near(c.bounds,point,48))this.prefetchChunk(c.id);for(const [id,entry] of this.loaded)if(!this.retained.has(id)&&now-entry.lastUsed>3000)this.unloadChunk(id)}
  return this.readyForMovement;
 }
 markFirstPlayable(){if(this.firstPlayable)return;this.firstPlayable=true;this.metrics.firstPlayable={at:performance.now(),chunks:[...this.loaded.keys()],downloadBytes:this.metrics.downloadBytes,decodedBytes:this.metrics.decodedBytes};}
 suspend(){if(this.pins.size)return;this.active=false;this.required.clear();this.retained.clear();this.readyForMovement=true;this.status(false);for(const id of this.loaded.keys())this.unloadChunk(id)}
 status(show){const stage=document.querySelector('.stage');if(!stage)return;if(!this.overlay){this.overlay=document.createElement('div');this.overlay.className='transition-overlay';this.overlay.setAttribute('role','status');stage.append(this.overlay)}this.overlay.style.display=show?'grid':'none';if(show){const failed=[...this.required].some(id=>this.failures.has(id));this.overlay.textContent=failed?'Nearby streets could not load. Retrying…':'Preparing nearby streets…'}}
 snapshot(){return {zone:this.zone.id,sourceSHA256:this.zone.sourceSHA256,firstPlayable:this.firstPlayable,loaded:[...this.loaded.keys()],inflight:[...this.inflight.keys()],required:[...this.required],pins:[...this.pins],failures:[...this.failures],readyForMovement:this.readyForMovement,...structuredClone(this.metrics)}}
}
window.AstraeonWorldStreaming={ZoneStream,async open(url){const world=await json(url);if(world.version!==1||!world.zones[world.defaultZone])throw Error('Invalid world manifest');const ref=world.zones[world.defaultZone],zone=await json(ref.url,ref);if(zone.version!==1||!zone.chunks?.length||new Set(zone.chunks.map(c=>c.id)).size!==zone.chunks.length)throw Error('Invalid zone manifest');const semantics=await json(zone.semantics.url,zone.semantics);if(semantics.streaming?.sourceSHA256!==zone.sourceSHA256)throw Error('Mismatched world semantics');const stream=new ZoneStream(zone);window.AstraeonWorldStreaming=stream;return semantics}};
})();
