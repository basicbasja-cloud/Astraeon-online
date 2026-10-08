/* Ordered classic scripts preserve the current globals. Only the review URL
 * imports native court data before consumers capture town content. */
(async()=>{
'use strict';
const version='102';
function load(files){return Promise.all(files.map(file=>new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=file+'?v='+version;script.async=false;script.onload=resolve;script.onerror=()=>reject(Error('Could not load '+file));document.body.appendChild(script)})))}
try{
 await load(['icons.js','world-view.js','world-content.js']);
 {
  await load(['world/v3/spatial.js','world/v3/town-import.js']);
  const legacy=new URLSearchParams(location.search).get('world')==='court-legacy',canvas=new URLSearchParams(location.search).get('renderer')==='canvas';let data;
  if(legacy||canvas){const response=await fetch('world/v3/'+(legacy?'wayfarer-court':'wayfarer-spatial')+'.json?v='+version);if(!response.ok)throw Error('Could not load authored world');data=await response.json()}
  else{await load(['world/v3/streaming.js']);if('serviceWorker' in navigator){await Promise.race([navigator.serviceWorker.ready.then(()=>navigator.serviceWorker.controller?Promise.resolve():new Promise(resolve=>navigator.serviceWorker.addEventListener('controllerchange',resolve,{once:true}))),new Promise(resolve=>setTimeout(resolve,5000))])}data=await window.AstraeonWorldStreaming.open('world/v3/world-manifest.json?v='+version)}
  window.AstraeonContent=AstraeonTownImportV3.content(data,window.AstraeonContent);
 }
 await load(['environment-metadata.js','environment.js','town-structure.js','scene.js','input.js','character-motion.js','directional-metadata.js','hero-registration.js','warrior-gait.js','world/v3/locomotion.js','world/v3/warrior-registration.js','sprite-motion.js','warrior-rig.js','directional-art.js','modular-sprites.js','character-renderer.js','animation.js','skill-nodes.js','combat.js','navigation.js','exploration.js','enemy-combat.js','dungeon.js','world-systems.js','save-state.js','combat-vfx.js']);
 const animation=await fetch('world/v3/warrior-animation.json?v='+version);if(!animation.ok)throw Error('Could not load Warrior animation');const animationData=await animation.json();window.AstraeonLocomotionV3.configure(animationData);window.AstraeonDirectionalArt.configureReactions(animationData.reactions);
 const painted=await fetch('world/v3/warrior-painted-locomotion.json?v='+version);if(!painted.ok)throw Error('Could not load full-body Warrior animation');const paintedData=await painted.json();window.AstraeonLocomotionV3.configurePainted(paintedData);await window.AstraeonDirectionalArt.configurePaintedLocomotion(paintedData);
 await import('./world/v3/renderer.js?v='+version);
 if(window.AstraeonContent.nativeWorld.spatial.scene.streaming){
  const stream=window.AstraeonWorldStreaming;stream.createRenderer=()=>new window.AstraeonSpatialRenderer.SpatialRenderer(window.AstraeonContent.nativeWorld.spatial.scene);
  const original=stream.ensureRenderer.bind(stream);stream.ensureRenderer=async()=>{const renderer=await original();window.AstraeonSpatialView=renderer;return renderer};
  let saved;try{saved=window.AstraeonSave.normalize(JSON.parse(localStorage.getItem('astraeon-iso-v1')))}catch{}
  if(!saved||saved.zone===0){const world=window.AstraeonContent.nativeWorld;let point=saved&&saved.worldLayout===world.layoutId?[saved.x,saved.y]:world.spawn;if(world.spatial.blocked(...point))point=world.safeSpawn;await stream.ensureAt({x:point[0],y:point[1]})}
 }
 if(window.AstraeonSpatialView)await window.AstraeonSpatialView.whenReady;
 const developmentBody=new URLSearchParams(location.search).get('swordsman');
 if(developmentBody){await load(['proof/swordsman-development.js']);await window.AstraeonSwordsmanDevelopmentInit(developmentBody)}
 await load(['wardrobe.js','character-studio.js']);
 let savedAppearance;try{savedAppearance=window.AstraeonSave.normalize(JSON.parse(localStorage.getItem('astraeon-iso-v1')))}catch{}
 if(savedAppearance?.appearance){await window.AstraeonWardrobe.select(savedAppearance.appearance,savedAppearance.cls);await Promise.all(['Hit','Death','Respawn'].map(id=>window.AstraeonWardrobe.prepare(id)))}
 await load(['game.js']);
}catch(error){const app=document.getElementById('app');app.textContent='The game could not load. Reload to retry. '+error.message;console.error(error)}
})();
