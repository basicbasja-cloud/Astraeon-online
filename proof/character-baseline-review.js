(async function(){
'use strict';
const $=id=>document.getElementById(id),dirs=['S','SW','W','NW','N','NE','E','SE'];
const root='authoring/characters/private-ro-reference/rebuild-ro1/';
const images=new Map();
function load(url){if(!images.has(url))images.set(url,new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>resolve(image);image.onerror=()=>reject(Error('Missing local reference: '+url));image.src=url}));return images.get(url)}
const evidence=await fetch('docs/review/character-ro1-rebuild-v2/ro1-part-registration.json').then(r=>r.json());
const rendered=await fetch(root+'metadata.json').then(r=>{if(!r.ok)throw Error('Private reference capture unavailable; run the documented acquisition step locally');return r.json()});
let frame=0,playing=true,last=performance.now(),elapsed=0,generation=0;
const action=()=>$('action').value,direction=()=>$('direction').value;
const record=()=>rendered.records.find(r=>r.action===action()&&r.direction===direction());
async function draw(){
 const current=++generation,a=action(),d=direction(),r=record(),count=r.frameCount;
 frame=(frame+count)%count;$('frame').max=count-1;$('frame').value=frame;
 const decoded=evidence.records.filter(v=>v.action===a&&v.direction===d);
 const raw=decoded[frame%decoded.length];
 const paths={assembled:`${root}${a}/${d}-${String(frame).padStart(2,'0')}.png`,body:`${root}parts/${a}/${d}-${String(raw.frame).padStart(2,'0')}-body.png`,head:`${root}parts/${a}/${d}-${String(raw.frame).padStart(2,'0')}-head.png`,candidate:'authoring/characters/builds/swordsman-ro1-rebuild-v2/normalized-neutral/atlas.png'};
 try{
  const loaded=await Promise.all(Object.entries(paths).map(async([key,url])=>[key,await load(url)]));
  if(current!==generation)return;
  for(const[key,image]of loaded){const canvas=$(key),ctx=canvas.getContext('2d');ctx.clearRect(0,0,384,384);ctx.imageSmoothingEnabled=key==='candidate';if(key==='candidate')ctx.drawImage(image,0,dirs.indexOf(d)*320,320,320,0,0,384,384);else ctx.drawImage(image,0,0,384,384)}
  $('status').textContent=`${a} · ${d} · RO frame ${frame+1}/${count} · ${playing?'playing':'paused'} · new ASTRAEON panel remains a neutral study`;
  $('metadata').textContent=JSON.stringify({sourceAction:r.actionId,renderedFrame:frame,decodedBodyFrame:raw.frame,bodyAnchor:raw.bodyAnchor,headAnchor:raw.headAnchor,headPlacementDelta:raw.headPlacementDelta,referenceClass:'RAW_BODY_HEAD + RENDERED_COMPOSITE',masterApproved:false},null,2);
 }catch(error){$('status').textContent=error.message;playing=false;$('play').textContent='Play'}
}
function select(){frame=0;elapsed=0;draw()}
$('action').onchange=select;$('direction').onchange=select;
$('play').onclick=()=>{playing=!playing;$('play').textContent=playing?'Pause':'Play';elapsed=0;draw()};
function step(delta){playing=false;$('play').textContent='Play';frame+=delta;elapsed=0;draw()}
$('previous').onclick=()=>step(-1);$('next').onclick=()=>step(1);
$('frame').oninput=()=>{playing=false;$('play').textContent='Play';frame=Number($('frame').value);elapsed=0;draw()};
function tick(now){const delta=Math.min(100,now-last);last=now;if(playing){elapsed+=delta*Number($('speed').value);const delay=record().renderedDelaysMs[frame]||100;if(elapsed>=delay){elapsed%=delay;frame++;draw()}}requestAnimationFrame(tick)}
await draw();requestAnimationFrame(tick);
window.characterBaselineReview={getState:()=>({action:action(),direction:direction(),frame,playing,masterApproved:false})};
})().catch(error=>{document.getElementById('status').textContent=error.message;console.error(error)});
