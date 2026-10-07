const CACHE = 'astraeon-static-v87';
const WORLD_CACHE='astraeon-world-v87',ASSET_CACHE='astraeon-assets-v87';
// Only application shell/runtime. Maps, atlases, audio and chunks are on demand.
const FILES = ["./index.html", "./manifest.webmanifest", "./icon.svg", "./style.css?v=87", "./animation.js?v=87", "./character-motion.js?v=87", "./character-renderer.js?v=87", "./combat-vfx.js?v=87", "./combat.js?v=87", "./directional-art.js?v=87", "./directional-metadata.js?v=87", "./dungeon.js?v=87", "./enemy-combat.js?v=87", "./environment-metadata.js?v=87", "./environment.js?v=87", "./exploration.js?v=87", "./game.js?v=87", "./hero-registration.js?v=87", "./icons.js?v=87", "./input.js?v=87", "./navigation.js?v=87", "./save-state.js?v=87", "./scene.js?v=87", "./skill-nodes.js?v=87", "./sprite-motion.js?v=87", "./town-structure.js?v=87", "./warrior-gait.js?v=87", "./warrior-rig.js?v=87", "./world-content.js?v=87", "./world-systems.js?v=87", "./world-view.js?v=87", "./world/v3/locomotion.js?v=87", "./world/v3/spatial.js?v=87", "./world/v3/streaming.js?v=87", "./world/v3/town-import.js?v=87", "./world/v3/warrior-registration.js?v=87", "./world/v3/renderer.js?v=87", "./vendor/three/three.module.min.js", "./vendor/three/three.core.min.js", "./world/v3/warrior-animation.json?v=87", "./world/v3/warrior-painted-locomotion.json?v=87", "./boot.js?v=87"];
const LIMITS={[WORLD_CACHE]:{bytes:32*1024*1024,count:180},[ASSET_CACHE]:{bytes:64*1024*1024,count:100}};
const inflight=new Map(),writes=new Map();
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(FILES)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',event=>{event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>/^astraeon-(static|world|assets)-/.test(k)&&![CACHE,WORLD_CACHE,ASSET_CACHE].includes(k)).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
function putBounded(name,request,response){
 const prior=writes.get(name)||Promise.resolve(),job=prior.catch(()=>{}).then(async()=>{
  const cache=await caches.open(name),limit=LIMITS[name];let bytes=Number(response.headers.get('content-length'));
  if(!Number.isFinite(bytes)||bytes<=0)bytes=(await response.clone().blob()).size;
  if(bytes>limit.bytes)return;
  const headers=new Headers(response.headers);headers.set('x-astraeon-cache-bytes',String(bytes));
  const stored=new Response(response.clone().body,{status:response.status,statusText:response.statusText,headers});
  await cache.delete(request);try{await cache.put(request,stored)}catch(error){if(error.name!=='QuotaExceededError')throw error;const oldest=(await cache.keys())[0];if(oldest)await cache.delete(oldest);return}
  const keys=await cache.keys();let total=0;for(const key of keys){const hit=await cache.match(key);total+=Number(hit.headers.get('x-astraeon-cache-bytes'))||0}
  let count=keys.length;for(const key of keys){if(total<=limit.bytes&&count<=limit.count)break;const hit=await cache.match(key);total-=Number(hit.headers.get('x-astraeon-cache-bytes'))||0;count--;await cache.delete(key)}
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
   if(cached){if(!shell&&!oversized)putBounded(name,request,cached).catch(()=>{}).finally(resolveLifetime);else resolveLifetime();return cached}
   const response=await network();if(response.ok&&!oversized){const write=shell?cache.put(request,response.clone()):putBounded(name,request,response);write.catch(()=>{}).finally(resolveLifetime)}else resolveLifetime();return response;
  }catch(error){resolveLifetime();throw error}
 })());
});
