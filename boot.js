/* Ordered classic scripts preserve the current globals. Only the review URL
 * imports native court data before consumers capture town content. */
(async()=>{
'use strict';
const version='36';
function load(files){return Promise.all(files.map(file=>new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=file+'?v='+version;script.async=false;script.onload=resolve;script.onerror=()=>reject(Error('Could not load '+file));document.body.appendChild(script)})))}
try{
 await load(['icons.js','world-view.js','world-content.js']);
 {
  await load(['world/v3/spatial.js','world/v3/town-import.js']);const worldFile=new URLSearchParams(location.search).get('world')==='court-legacy'?'wayfarer-court':'wayfarer-spatial';const response=await fetch('world/v3/'+worldFile+'.json?v='+version);if(!response.ok)throw Error('Could not load authored court data');const data=await response.json();window.AstraeonContent=AstraeonTownImportV3.content(data,window.AstraeonContent);
 }
 await load(['environment-metadata.js','environment.js','town-structure.js','scene.js','input.js','character-motion.js','directional-metadata.js','hero-registration.js','warrior-gait.js','world/v3/locomotion.js','world/v3/warrior-registration.js','sprite-motion.js','warrior-rig.js','directional-art.js','character-renderer.js','animation.js','skill-nodes.js','combat.js','navigation.js','exploration.js','enemy-combat.js','dungeon.js','world-systems.js','save-state.js','combat-vfx.js']);
 const animation=await fetch('world/v3/warrior-animation.json?v='+version);if(!animation.ok)throw Error('Could not load Warrior animation');const animationData=await animation.json();window.AstraeonLocomotionV3.configure(animationData);window.AstraeonDirectionalArt.configureReactions(animationData.reactions);
 await import('./world/v3/renderer.js?v='+version);
 if(window.AstraeonSpatialView)await window.AstraeonSpatialView.whenReady;
 await load(['game.js']);
}catch(error){const app=document.getElementById('app');app.textContent='The game could not load. Reload to retry. '+error.message;console.error(error)}
})();
