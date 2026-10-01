/* Ordered classic scripts preserve the current globals. Only the review URL
 * imports native court data before consumers capture town content. */
(async()=>{
'use strict';
const version='30';
function load(files){return Promise.all(files.map(file=>new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=file+'?v='+version;script.async=false;script.onload=resolve;script.onerror=()=>reject(Error('Could not load '+file));document.body.appendChild(script)})))}
try{
 await load(['icons.js','world-view.js','world-content.js']);
 if(new URLSearchParams(location.search).get('world')==='court-v3'){
  await load(['world/v3/spatial.js','world/v3/town-import.js']);const response=await fetch('world/v3/wayfarer-court.json?v='+version);if(!response.ok)throw Error('Could not load authored court data');const data=await response.json();window.AstraeonContent=AstraeonTownImportV3.content(data,window.AstraeonContent);
 }
 await load(['environment-metadata.js','environment.js','town-structure.js','scene.js','input.js','character-motion.js','directional-metadata.js','hero-registration.js','warrior-gait.js','sprite-motion.js','warrior-rig.js','directional-art.js','character-renderer.js','animation.js','skill-nodes.js','combat.js','navigation.js','exploration.js','enemy-combat.js','dungeon.js','world-systems.js','save-state.js','combat-vfx.js','game.js']);
}catch(error){const app=document.getElementById('app');app.textContent='The game could not load. Reload to retry. '+error.message;console.error(error)}
})();
