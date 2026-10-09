(async function(){
'use strict';
const M=window.AstraeonMotionTemplate,A=window.AstraeonCharacterAssembly,$=id=>document.getElementById(id);
let loaded,time=0,cosmetic=0,playing=true,forcedFrame,last=performance.now();
const layers=new Map();
function current(){const seq=loaded.compiled.motion.template.actions[$('action').value].directions[$('direction').value];return loaded.sample($('action').value,$('direction').value,time%seq.totalDurationMs,{frameIndex:forcedFrame,cosmeticTimeMs:cosmetic})}
function paint(canvas,sample,zoom,visibleLayers,overlay=false){
 const ctx=canvas.getContext('2d');ctx.clearRect(0,0,canvas.width,canvas.height);
 const scale=70/sample.registration.referenceHeight*zoom;
 const anchors=A.drawAssembly(ctx,sample,loaded.images,{x:canvas.width/2,y:canvas.height*.825,scale,visibleLayers});
 if(overlay)for(const [name,p] of Object.entries(anchors)){ctx.strokeStyle=name==='root'?'#ff789a':'#c6e8f3';ctx.beginPath();ctx.moveTo(p.x-3,p.y);ctx.lineTo(p.x+3,p.y);ctx.moveTo(p.x,p.y-3);ctx.lineTo(p.x,p.y+3);ctx.stroke()}
}
function render(){
 if(!loaded)return;const s=current(),zoom=Number($('scale').value);
 $('hero').width=$('hero').height=128*zoom;
 for(const [id,z] of [['hero',zoom],['gameplay',1],['review',2]])paint($(id),s,z,undefined,$('anchors').value==='1');
 $('status').textContent=`${s.action==='BasicAttack'?'Basic Attack':s.action} · ${s.direction} · ${playing?'Playing':'Paused'} · ${s.frameIndex+1}/${loaded.compiled.motion.template.actions[s.action].directions[s.direction].frames.length}`;
 $('frame').max=loaded.compiled.motion.template.actions[s.action].directions[s.direction].frames.length-1;$('frame').value=s.frameIndex;$('frame-label').textContent=s.frameIndex;
 for(const b of $('directions').children)b.setAttribute('aria-pressed',b.textContent===s.direction);
 if(document.querySelector('details').open){
  for(const layer of s.layers)if(!layers.has(layer.layer)){const label=document.createElement('label'),canvas=document.createElement('canvas');label.append(layer.layer,canvas);canvas.width=canvas.height=128;$('layers').append(label);layers.set(layer.layer,canvas)}
  for(const [layer,canvas]of layers)paint(canvas,s,1,[layer]);
  $('metadata').textContent=JSON.stringify({role:s.frame.role,evidenceClass:s.frame.evidenceClass,referencePhase:s.frame.referencePhase,between:s.frame.between,durationMs:s.frame.durationMs,totalDurationMs:s.totalDurationMs,root:s.frame.root,anchors:s.frame.anchors,events:s.frame.events,drawOrder:s.layers.map(l=>l.layer),sampling:s.layers.map(l=>({part:l.partId,mode:l.mode,sample:l.sampleIndex}))},null,2);
 }
}
function fail(e){$('status').className='error';$('status').textContent=e.message;console.error(e)}
try{
 loaded=await A.loadAssembly({motionUrl:'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json',appearanceUrl:'authoring/characters/appearance/swordsman-male-painted/appearance-pack.json',allowDev:true});
 for(const d of M.DIRECTIONS){const b=document.createElement('button');b.textContent=d;b.onclick=()=>{$('direction').value=d;render()};$('directions').append(b)}
 for(const [id,slot]of [['hair','Hair'],['weapon','MainHand'],['offhand','OffHand'],['headgear','Headgear'],['garment','Garment']])$(id).onchange=async()=>{try{await loaded.setAppearance({[slot]:$(id).value||null});render()}catch(e){fail(e)}};
 $('action').onchange=()=>{time=0;forcedFrame=undefined;render()};$('direction').onchange=render;$('scale').onchange=render;$('anchors').onchange=render;
 $('play').onclick=()=>{playing=!playing;forcedFrame=undefined;$('play').textContent=playing?'Pause':'Play';render()};
 $('frame').oninput=()=>{forcedFrame=Number($('frame').value);playing=false;$('play').textContent='Play';time=loaded.compiled.motion.template.actions[$('action').value].directions[$('direction').value].frames.slice(0,forcedFrame).reduce((n,f)=>n+f.durationMs,0);render()};
 const api={snapshot:()=>({...current(),playing,time,cosmetic}),get loaded(){return loaded},
  async prepareVariants(){const previous=loaded.appearance;await loaded.setAppearance({Hair:'hair-b',MainHand:'weapon-b',OffHand:'offhand',Headgear:'headgear'});await loaded.setAppearance(previous)},
  renderPose:({action='Walk',direction='S',frameIndex=0,appearance=loaded.appearance,visibleLayers,scale=1}={})=>{const seq=loaded.compiled.motion.template.actions[action].directions[direction];const t=seq.frames.slice(0,frameIndex).reduce((n,f)=>n+f.durationMs,0);const s=loaded.compiled.sample(action,direction,t,{frameIndex,appearance,cosmeticTimeMs:t});const c=document.createElement('canvas');c.width=c.height=128*scale;paint(c,s,scale,visibleLayers);return c.toDataURL('image/png')},
  setReviewPose:({action='Walk',direction='S',frameIndex,play=true,timeMs=0}={})=>{$('action').value=action;$('direction').value=direction;time=timeMs;forcedFrame=frameIndex;playing=play;$('play').textContent=play?'Pause':'Play';render()},render};
 window.AstraeonCharacterReview=Object.freeze(api);
 function tick(now){const dt=Math.min(now-last,100);last=now;if(playing){time+=dt*Number($('speed').value);cosmetic+=dt*Number($('speed').value);forcedFrame=undefined;render()}requestAnimationFrame(tick)}
 render();requestAnimationFrame(tick);
}catch(e){fail(e)}
})();
