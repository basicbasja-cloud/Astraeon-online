const CACHE = 'astraeon-static-v94';
const WORLD_CACHE='astraeon-world-v94',ASSET_CACHE='astraeon-assets-v94';
// Only application shell/runtime. Maps, atlases, audio and chunks are on demand.
const FILES = ["./index.html", "./manifest.webmanifest", "./icon.svg", "./style.css?v=94", "./animation.js?v=94", "./character-motion.js?v=94", "./character-renderer.js?v=94", "./combat-vfx.js?v=94", "./combat.js?v=94", "./directional-art.js?v=94", "./directional-metadata.js?v=94", "./dungeon.js?v=94", "./enemy-combat.js?v=94", "./environment-metadata.js?v=94", "./environment.js?v=94", "./exploration.js?v=94", "./game.js?v=94", "./hero-registration.js?v=94", "./icons.js?v=94", "./input.js?v=94", "./navigation.js?v=94", "./save-state.js?v=94", "./scene.js?v=94", "./skill-nodes.js?v=94", "./sprite-motion.js?v=94", "./town-structure.js?v=94", "./warrior-gait.js?v=94", "./warrior-rig.js?v=94", "./world-content.js?v=94", "./world-systems.js?v=94", "./world-view.js?v=94", "./world/v3/locomotion.js?v=94", "./world/v3/spatial.js?v=94", "./world/v3/streaming.js?v=94", "./world/v3/town-import.js?v=94", "./world/v3/warrior-registration.js?v=94", "./world/v3/renderer.js?v=94", "./vendor/three/three.module.min.js", "./vendor/three/three.core.min.js", "./world/v3/warrior-animation.json?v=94", "./world/v3/warrior-painted-locomotion.json?v=94", "./boot.js?v=94"];
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
 const shell=FILES.some(file=>new URL(file,self.location).href===url.href),name=shell?CACHE:/\/world\/v3\/(streamed\/|world-manifest\.json)/.test(url.pathname)?WORLD_CACHE:ASSET_CACHE;
 const oversized=/\/world\/v3\/wayfarer-spatial\.json$/.test(url.pathname);
 const network=()=>{if(!inflight.has(url.href)){const pending=fetch(request).finally(()=>inflight.delete(url.href));inflight.set(url.href,pending)}return inflight.get(url.href).then(response=>response.clone())};
 let resolveLifetime;const lifetime=new Promise(resolve=>resolveLifetime=resolve);event.waitUntil(lifetime);
 event.respondWith((async()=>{
  try{
   if(request.mode==='navigate'){try{const response=await network();if(response.ok)await (await caches.open(CACHE)).put('./index.html',response.clone());resolveLifetime();return response}catch(error){const cached=await caches.match('./index.html');resolveLifetime();if(cached)return cached;throw error}}
   const cache=await caches.open(name),cached=await cache.match(request);
   if(cached){if(!shell&&!oversized)putBounded(name,request,cached,true).catch(()=>{}).finally(resolveLifetime);else resolveLifetime();return cached}
   const response=await network();if(response.ok&&!oversized){const write=shell?cache.put(request,response.clone()):putBounded(name,request,response);write.catch(()=>{}).finally(resolveLifetime)}else resolveLifetime();return response;
  }catch(error){resolveLifetime();throw error}
 })());
});
