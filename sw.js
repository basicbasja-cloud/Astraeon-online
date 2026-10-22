const CACHE = 'astraeon-static-v105';
const WORLD_CACHE='astraeon-world-v105',ASSET_CACHE='astraeon-assets-v105';
// Only application shell/runtime. Maps, atlases, audio and chunks are on demand.
const FILES = ["./index.html", "./manifest.webmanifest", "./icon.svg", "./style.css?v=105", "./animation.js?v=105", "./character-motion.js?v=105", "./character-renderer.js?v=105", "./modular-sprites.js?v=105", "./combat-vfx.js?v=105", "./combat.js?v=105", "./directional-art.js?v=105", "./directional-metadata.js?v=105", "./dungeon.js?v=105", "./enemy-combat.js?v=105", "./environment-metadata.js?v=105", "./environment.js?v=105", "./exploration.js?v=105", "./game.js?v=105", "./hero-registration.js?v=105", "./icons.js?v=105", "./input.js?v=105", "./navigation.js?v=105", "./save-state.js?v=105", "./scene.js?v=105", "./skill-nodes.js?v=105", "./sprite-motion.js?v=105", "./town-structure.js?v=105", "./warrior-gait.js?v=105", "./warrior-rig.js?v=105", "./world-content.js?v=105", "./world-systems.js?v=105", "./world-view.js?v=105", "./world/v3/locomotion.js?v=105", "./world/v3/spatial.js?v=105", "./world/v3/streaming.js?v=105", "./world/v3/town-import.js?v=105", "./world/v3/warrior-registration.js?v=105", "./world/v3/renderer.js?v=105", "./vendor/three/three.module.min.js", "./vendor/three/three.core.min.js", "./world/v3/warrior-animation.json?v=105", "./world/v3/warrior-painted-locomotion.json?v=105", "./boot.js?v=105"];
FILES.push('./patch001-characters.js?v=105','./wardrobe.js?v=105','./character-studio.js?v=105','./character-studio.css?v=105','./character-studio.html');
const LIMITS={[WORLD_CACHE]:{bytes:32*1024*1024,count:180},[ASSET_CACHE]:{bytes:64*1024*1024,count:100}};
const inflight=new Map(),writes=new Map(),inventories=new Map();
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(FILES)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>/^astraeon-(static|world|assets)-/.test(k)&&![CACHE,WORLD_CACHE,ASSET_CACHE].includes(k)).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
function putBounded(name,request,response,touchOnly=false){
 if(!touchOnly)response=response.clone(); // retain before the client consumes its body
 const prior=writes.get(name)||Promise.resolve(),job=prior.catch(()=>{}).then(async()=>{
  const cache=await caches.open(name),limit=LIMITS[name];let inventory=inventories.get(name);
  if(!inventory){inventory=new Map();for(const key of await cache.keys()){const hit=await cache.match(key);inventory.set(key.url,Number(hit.headers.get('x-astraeon-cache-bytes'))||0)}inventories.set(name,inventory)}
  let bytes=Number(response.headers.get('x-astraeon-cache-bytes')||response.headers.get('content-length'));
  if(!Number.isFinite(bytes)||bytes<=0||(!response.headers.has('x-astraeon-cache-bytes')&&response.headers.has('content-encoding')))bytes=(await response.clone().blob()).size;
  if(bytes>limit.bytes)return;
  if(touchOnly){inventory.delete(request.url);inventory.set(request.url,bytes);return}
  const headers=new Headers(response.headers);headers.set('x-astraeon-cache-bytes',String(bytes));
  const stored=new Response(response.clone().body,{status:response.status,statusText:response.statusText,headers});
  inventory.delete(request.url);
  try{if(!touchOnly)await cache.put(request,stored)}catch(error){if(error.name!=='QuotaExceededError')throw error;const oldest=inventory.keys().next().value;if(oldest){await cache.delete(oldest);inventory.delete(oldest)}return}
  inventory.set(request.url,bytes);let total=[...inventory.values()].reduce((sum,n)=>sum+n,0);
  while(total>limit.bytes||inventory.size>limit.count){const [url,size]=inventory.entries().next().value;total-=size;inventory.delete(url);await cache.delete(url)}
 });writes.set(name,job);return job;
}
self.addEventListener('fetch',event=>{
 const request=event.request,url=new URL(request.url);if(request.method!=='GET'||url.origin!==self.location.origin)return;
 // Review candidates must not consume or evict ordinary gameplay asset caches.
 if(url.searchParams.get('spriteDev')==='1')return;
 const shell=FILES.some(file=>new URL(file,self.location).href===url.href),name=shell?CACHE:/\/world\/v3\/(streamed\/|world-manifest\.json)/.test(url.pathname)?WORLD_CACHE:ASSET_CACHE;
 const oversized=/\/world\/v3\/wayfarer-spatial\.json$/.test(url.pathname);
 const network=()=>{if(!inflight.has(url.href)){const pending=fetch(request).finally(()=>inflight.delete(url.href));inflight.set(url.href,pending)}return inflight.get(url.href).then(response=>response.clone())};
 let resolveLifetime;const lifetime=new Promise(resolve=>resolveLifetime=resolve);event.waitUntil(lifetime);
 event.respondWith((async()=>{
  try{
   if(request.mode==='navigate'){
    // A development preview must never replace the offline game entry point.
    const entry=url.pathname===new URL('./',self.location).pathname||url.pathname===new URL('./index.html',self.location).pathname,key=entry?'./index.html':request;
    try{const response=await network();if(response.ok)await (await caches.open(CACHE)).put(key,response.clone());resolveLifetime();return response}catch(error){const cached=await caches.match(key);resolveLifetime();if(cached)return cached;throw error}
   }
   const cache=await caches.open(name),cached=await cache.match(request);
   if(cached){if(!shell&&!oversized)putBounded(name,request,cached,true).catch(()=>{}).finally(resolveLifetime);else resolveLifetime();return cached}
   const response=await network();if(response.ok&&!oversized){const write=shell?cache.put(request,response.clone()):putBounded(name,request,response);write.catch(()=>{}).finally(resolveLifetime)}else resolveLifetime();return response;
  }catch(error){resolveLifetime();throw error}
 })());
});
