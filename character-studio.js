/* Same 2D compositor in creation, wardrobe and the all-motion review page. */
(()=>{
'use strict';
const W=window.AstraeonWardrobe,A=window.AstraeonModularSprites;
function mount(root,{cls=0,appearance=W.defaults(),onChange=()=>{},onReady=()=>{},gallery=false}={}){
 root.innerHTML=`<div class="character-customizer"><div class="sprite-stage"><canvas data-studio="canvas" width="640" height="430" aria-label="Animated character appearance"></canvas><span class="sprite-stage-label">ASTRAEON · 0.0.1</span></div><div class="studio-fields"><label>Body<select data-studio="body">${W.CATALOG.bodies.map(id=>`<option value="${id}">${id[0].toUpperCase()+id.slice(1)}</option>`).join('')}</select></label><label>Hair<select data-studio="hair">${W.CATALOG.hair.map(v=>`<option value="${v.id}">${v.name}</option>`).join('')}</select></label><label>Costume<select data-studio="outfit">${W.CATALOG.outfit.map(v=>`<option value="${v.id}">${v.name}</option>`).join('')}</select></label></div><div class="studio-motion"><label>Motion<select data-studio="motion">${W.CLIPS.map(id=>`<option>${id}</option>`).join('')}</select></label><label>Speed<select data-studio="speed"><option value="1">Normal</option><option value="0.25">Quarter speed</option><option value="0">Paused</option></select></label><button type="button" data-studio="size">Game size</button></div><div class="studio-directions" aria-label="Facing direction">${A.DIRECTIONS.map(d=>`<button type="button" data-direction="${d}" aria-pressed="${d==='S'}">${d}</button>`).join('')}</div><label class="studio-scrub">Frame<input data-studio="frame" type="range" min="0" value="0" max="7"><output data-studio="frame-label">0 / 7</output></label><p data-studio="status" class="studio-status" role="status">Loading your character…</p>${gallery?'<canvas data-studio="gallery" class="studio-gallery" width="896" height="252" aria-label="All eight character directions"></canvas><fieldset class="studio-layers"><legend>Inspect layers</legend>'+A.REQUIRED_LAYERS.map(layer=>`<label><input type="checkbox" data-layer="${layer}" checked>${layer}</label>`).join('')+'</fieldset><details class="studio-data"><summary>Frame registration</summary><pre data-studio="data"></pre></details>':''}</div>`;
 const get=name=>root.querySelector(`[data-studio="${name}"]`),canvas=get('canvas'),ctx=canvas.getContext('2d');
 const fields=['body','hair','outfit','motion','speed','frame'].map(get);let config=W.normalize(appearance)||W.defaults(),sprite=null,direction='S',elapsed=0,last=0,ticket=0,ready=false,small=false,destroyed=false,frame=null,error=null;
 get('body').value=config.bodyVariant;get('hair').value=config.hair;get('outfit').value=config.outfit;
 const disabled=()=>[...root.querySelectorAll('input[data-layer]:not(:checked)')].map(input=>input.dataset.layer);
 const filtered=f=>({...f,layers:f.layers.filter(l=>!disabled().includes(l.layer))});
 function draw(){
  if(!sprite||!ready)return;
  const id=get('motion').value;frame=sprite.compiled.sample(id,direction,elapsed,{appearance:sprite.appearance,...(get('speed').value==='0'?{frameIndex:Number(get('frame').value)}:{})});
  ctx.clearRect(0,0,640,430);const bg=ctx.createRadialGradient(320,250,15,320,210,350);bg.addColorStop(0,'#344b4a');bg.addColorStop(1,'#101f2a');ctx.fillStyle=bg;ctx.fillRect(0,0,640,430);
  ctx.strokeStyle='#c8b87b55';ctx.lineWidth=1;ctx.beginPath();ctx.ellipse(320,357,126,32,0,0,Math.PI*2);ctx.stroke();
  A.draw(ctx,filtered(frame),sprite.images,{x:320,y:355,scale:small?70*92/76/W.ANATOMY.referenceHeight:3.1});
  get('frame').value=frame.frameIndex;get('frame-label').textContent=`${frame.frameIndex} / ${get('frame').max}`;
  get('status').textContent=error||`${sprite.compiled.definition.classId} · ${config.bodyVariant} · ${id} · ${direction} · ${frame.duration} ms`;
  const gc=get('gallery');if(gc){const g=gc.getContext('2d');g.clearRect(0,0,896,252);g.fillStyle='#12232d';g.fillRect(0,0,896,252);g.font='12px system-ui';g.textAlign='center';
   for(let i=0;i<8;i++){const d=A.DIRECTIONS[i],f=sprite.compiled.sample(id,d,elapsed,{appearance:sprite.appearance,frameIndex:frame.frameIndex}),x=i%4*224+112,y=Math.floor(i/4)*126+104;A.draw(g,filtered(f),sprite.images,{x,y,scale:70*92/76/W.ANATOMY.referenceHeight});g.fillStyle='#d9c895';g.fillText(d,x,y+17)}
   get('data').textContent=JSON.stringify({anatomy:W.ANATOMY,characterId:frame.characterId,clip:id,direction,frame:frame.frameIndex,sockets:frame.sockets,drawOrder:frame.layers.map(l=>l.slot+':'+l.partId)},null,2);
  }
 }
 async function choose(){
  const request=++ticket;ready=false;error=null;onReady(false);fields.forEach(field=>field.disabled=true);get('status').textContent='Preparing synchronized artwork…';
  try{
   const next={version:1,bodyVariant:get('body').value,hair:get('hair').value,outfit:get('outfit').value};
   const visual=await W.load(next,cls,[get('motion').value]);if(destroyed||request!==ticket)return;
   sprite=visual;config=next;elapsed=0;get('frame').value=0;get('frame').max=sprite.compiled.definition.clips[get('motion').value].durations.length-1;ready=true;fields.forEach(field=>field.disabled=false);onChange({...config});onReady(true);draw();
  }catch(failure){if(request!==ticket)return;error=failure.message;get('status').textContent=error;fields.forEach(field=>field.disabled=false);onReady(false);console.error(failure)}
 }
 async function chooseClip(){
  if(!sprite||!ready)return;const request=++ticket;ready=false;onReady(false);fields.forEach(field=>field.disabled=true);get('status').textContent='Loading motion…';
  try{await sprite.ensure(get('motion').value);if(destroyed||request!==ticket)return;sprite.keepAnimations([get('motion').value]);elapsed=0;get('frame').value=0;get('frame').max=sprite.compiled.definition.clips[get('motion').value].durations.length-1;ready=true;fields.forEach(field=>field.disabled=false);onReady(true);draw()}
  catch(failure){if(request!==ticket)return;error=failure.message;get('status').textContent=error;fields.forEach(field=>field.disabled=false);onReady(false);console.error(failure)}
 }
 for(const name of ['body','hair','outfit'])get(name).addEventListener('change',choose);
 get('motion').addEventListener('change',chooseClip);get('speed').addEventListener('change',()=>{if(sprite)elapsed=sprite.compiled.definition.clips[get('motion').value].durations.slice(0,Number(get('frame').value)).reduce((a,b)=>a+b,0);draw()});
 get('frame').addEventListener('input',()=>{get('speed').value='0';draw()});get('size').addEventListener('click',()=>{small=!small;get('size').textContent=small?'Inspect size':'Game size';draw()});
 root.querySelectorAll('[data-direction]').forEach(button=>button.addEventListener('click',()=>{direction=button.dataset.direction;root.querySelectorAll('[data-direction]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));draw()}));root.querySelector('.studio-layers')?.addEventListener('change',draw);
 function tick(time){if(destroyed)return;if(!root.isConnected){destroyed=true;return}if(ready&&last&&Number(get('speed').value)>0){elapsed+=(time-last)*Number(get('speed').value);const clip=sprite.compiled.definition.clips[get('motion').value],total=sprite.compiled.duration(get('motion').value);if(!clip.loop&&elapsed>total+700)elapsed=0;draw()}last=time;requestAnimationFrame(tick)}
 const whenReady=choose();requestAnimationFrame(tick);
 return {whenReady,config:()=>({...config}),setClass(value){cls=value;return choose()},snapshot:()=>frame,destroy(){destroyed=true;ticket++}};
}
window.AstraeonCharacterStudio=Object.freeze({mount});
if(document.getElementById('character-studio')){
 const root=document.getElementById('character-studio'),select=document.getElementById('studio-class'),params=new URLSearchParams(location.search);select.value=params.get('class')==='mage'?'12':'0';const studio=mount(root,{gallery:true,cls:Number(select.value),appearance:W.normalize({bodyVariant:params.get('body'),hair:params.get('hair'),outfit:params.get('outfit')})});select.addEventListener('change',()=>studio.setClass(Number(select.value)));window.AstraeonCharacterReview=Object.freeze({snapshot:()=>studio.snapshot(),appearance:()=>studio.config()});
}
})();
