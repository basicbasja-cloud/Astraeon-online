/* Development compositor: same lookup, draw order and Canvas path as the actor adapter. */
(async()=>{
'use strict';
const api=window.AstraeonModularSprites,$=id=>document.getElementById(id),canvas=$('sprite'),ctx=canvas.getContext('2d');
let sprite,elapsed=0,last=0,loading=0,ready=false;
for(const d of api.DIRECTIONS)$('direction').add(new Option(d,d));
for(const layer of api.REQUIRED_LAYERS){const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.checked=true;input.dataset.layer=layer;label.append(input,layer);$('layers').append(label)}
function options(){return {frameIndex:Number($('frame').value),appearance:sprite.appearance}}
function sampled(){return sprite.compiled.sample($('animation').value,$('direction').value,elapsed,$('playback').value==='0'?options():{appearance:options().appearance})}
function render(){
 if(!sprite||!ready)return;
 const frame=sampled(),disabled=[...$('layers').querySelectorAll('input:not(:checked)')].map(i=>i.dataset.layer);
 const display={...frame,layers:frame.layers.filter(l=>!disabled.includes(l.layer))};
 ctx.clearRect(0,0,canvas.width,canvas.height);ctx.fillStyle='#1f303c';ctx.fillRect(0,0,canvas.width,canvas.height);
 const scale=$('gameplay-scale').checked?70*((window.AstraeonView?.scale.humanoid||92)/76)/frame.canvas.referenceHeight:1.45,x=canvas.width/2,y=430;
 ctx.strokeStyle='#526c79';ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(canvas.width,y);ctx.moveTo(x,0);ctx.lineTo(x,canvas.height);ctx.stroke();
 const sockets=api.draw(ctx,display,sprite.images,{x,y,scale});
 if($('sockets').checked){ctx.font='12px system-ui';for(const [id,p] of Object.entries(sockets)){ctx.fillStyle=id==='root'?'#ffffff':'#ffa98f';ctx.beginPath();ctx.arc(p.x,p.y,3,0,Math.PI*2);ctx.fill();ctx.fillText(id,p.x+7,p.y-5)}}
 $('frame').value=frame.frameIndex;$('frame-label').value=frame.frameIndex;
 $('status').textContent=`${frame.characterId} / ${frame.animationId} / ${frame.direction} / ${frame.frameIndex}\nClass: ${frame.classId} · Body variant: ${frame.bodyVariant} · ${sprite.compiled.definition.source.status} · ${sprite.compiled.definition.clips[frame.animationId].tags?.join(', ')||'contract proof'}\nDuration: ${frame.duration} ms · Canvas: ${frame.canvas.frameWidth}×${frame.canvas.frameHeight} · Root: ${frame.canvas.rootAnchorX}, ${frame.canvas.rootAnchorY}\nDraw order: ${frame.layers.map(l=>l.slot+':'+l.partId).join(' → ')}`;
}
function resetClip(){elapsed=0;$('frame').value=0;$('frame').max=sprite.compiled.definition.clips[$('animation').value].durations.length-1;render()}
async function chooseCharacter(){
 const ticket=++loading;ready=false;$('status').textContent='Loading modular proof…';
 try{const loaded=await api.load(`./assets/characters/${$('character').value}/sprite.json`,{allowDev:true,isolateDevelopmentCache:true});if(ticket!==loading)return;sprite=loaded;$('weapon').replaceChildren();for(const [id,part] of Object.entries(sprite.compiled.definition.parts))if(part.slot==='Weapon')$('weapon').add(new Option(part.cosmeticId||id,id));$('weapon').value=sprite.compiled.definition.defaultParts.Weapon;$('animation').replaceChildren();for(const [id,clip] of Object.entries(sprite.compiled.definition.clips)){const pending=clip.tags?.includes('PENDING_PRODUCTION'),option=new Option(id+(pending?' (pending production)':''),id);option.disabled=!!pending;$('animation').add(option)}ready=true;resetClip()}
 catch(error){$('status').textContent=error.message;console.error(error)}
}
async function chooseClip(){const ticket=++loading;ready=false;$('status').textContent='Loading animation…';try{await sprite.ensure($('animation').value);if(ticket!==loading)return;sprite.keepAnimations([$('animation').value]);ready=true;resetClip()}catch(error){$('status').textContent=error.message;console.error(error)}}
async function chooseWeapon(){const ticket=++loading;ready=false;$('status').textContent='Preloading cosmetic…';try{await sprite.setAppearance({Weapon:$('weapon').value});if(ticket!==loading)return;sprite.keepAnimations([$('animation').value]);ready=true;render()}catch(error){$('weapon').value=sprite.appearance.Weapon||sprite.compiled.definition.defaultParts.Weapon;ready=true;render();$('status').textContent+='\n'+error.message}}
$('controls').addEventListener('submit',e=>e.preventDefault());$('character').addEventListener('change',chooseCharacter);$('animation').addEventListener('change',chooseClip);
$('frame').addEventListener('input',()=>{$('playback').value='0';render()});$('weapon').addEventListener('change',chooseWeapon);for(const id of ['direction','sockets','gameplay-scale'])$(id).addEventListener('change',render);$('layers').addEventListener('change',render);
$('playback').addEventListener('change',()=>{if(sprite){const c=sprite.compiled.definition.clips[$('animation').value];elapsed=c.durations.slice(0,Number($('frame').value)).reduce((a,b)=>a+b,0)}render()});
function tick(time){if(last&&sprite&&ready&&$('playback').value!=='0'){elapsed+=(time-last)*Number($('playback').value);render()}last=time;requestAnimationFrame(tick)}
await chooseCharacter();requestAnimationFrame(tick);
// Read-only QA exposes the sampled frame; it does not mutate gameplay or saves.
window.AstraeonSpritePreview=Object.freeze({snapshot:()=>sampled(),timeline:()=>{const c=sprite.compiled.definition.clips[$('animation').value];return {durations:c.durations,loop:c.loop,totalMs:sprite.compiled.duration($('animation').value),loadedAtlasIds:Object.keys(sprite.images)}}});
})();
