(async function(){
'use strict';
const $=id=>document.getElementById(id),params=new URLSearchParams(location.search),A=window.AstraeonCharacterAssembly,V=window.AstraeonProductionValidation;
if(!params.has('motion')||!params.has('appearance'))return;
const asset=await A.loadAssembly({motionUrl:params.get('motion'),appearanceUrl:params.get('appearance'),allowDev:true});
const pack=asset.compiled.pack,template=asset.compiled.motion.template,canvas=$('stage'),ctx=canvas.getContext('2d');
const options=(select,items)=>{for(const [value,label]of items){const o=document.createElement('option');o.value=value;o.textContent=label;select.append(o)}};
options($('action'),Object.keys(template.actions).map(a=>[a,a]));options($('direction'),template.directions.map(d=>[d,d]));
let action=$('action').value,direction='S',time=0,cosmeticTime=0,playing=true,forcedFrame=null,last=performance.now(),pendingSelection=0;
const visible=new Set(Object.keys(pack.slots));
for(const [slot,definition]of Object.entries(pack.slots)){
 const label=document.createElement('label');label.textContent=slot==='Head'&&pack.headAppearanceModel==='HeadIncludesHair'?'Head + Hair style':slot;
 const select=document.createElement('select');select.dataset.slot=slot;
 if(!definition.required)options(select,[['','None']]);options(select,Object.entries(pack.parts).filter(([,p])=>p.slot===slot).map(([id])=>[id,id]));select.value=asset.appearance[slot]||'';label.append(select);$('appearance').append(label);
 select.onchange=async()=>{const request=++pendingSelection;try{await asset.setAppearance({[slot]:select.value||null});if(request===pendingSelection)draw()}catch(e){$('status').textContent=e.message;select.value=asset.appearance[slot]||''}};
 const toggle=document.createElement('label');toggle.className='toggle';const check=document.createElement('input');check.type='checkbox';check.checked=true;toggle.append(check,document.createTextNode(slot));$('visibility').append(toggle);check.onchange=()=>{check.checked?visible.add(slot):visible.delete(slot);draw()};
}
function sample(){return asset.sample(action,direction,time,{frameIndex:forcedFrame===null?undefined:forcedFrame,cosmeticTimeMs:cosmeticTime})}
function draw(){
 const s=sample(),mode=$('mode').value,body=new Set(['Body']),weapon=new Set(['MainHand']);
 let layers=s.layers.filter(l=>visible.has(l.slot));if(mode==='Body only')layers=layers.filter(l=>body.has(l.layer));if(mode==='Weapon only')layers=layers.filter(l=>weapon.has(l.layer));if(mode==='Body + Weapon'||mode==='Grip debug')layers=layers.filter(l=>body.has(l.layer)||weapon.has(l.layer));
 ctx.clearRect(0,0,canvas.width,canvas.height);const scale=Math.min(canvas.width/template.registration.canvas[0],canvas.height/template.registration.canvas[1]);
 A.drawAssembly(ctx,s,asset.images,{x:template.registration.root.x*scale,y:template.registration.root.y*scale,scale,visibleLayers:layers.map(l=>l.layer)});
 const grip=V.inspectGrip(s);
 if($('debug').checked||mode==='Grip debug'){
  const dots={equipment:grip.equipment,hand:grip.hand,grip:grip.grip,tip:grip.tip};
  for(const [name,a]of Object.entries(s.registeredAnchors))dots[name]=[a.x,a.y];
  for(const[name,p]of Object.entries(dots)){if(!p)continue;ctx.fillStyle=name==='grip'?'#77ff99':'#ffe07c';ctx.beginPath();ctx.arc(p[0]*scale,p[1]*scale,4,0,Math.PI*2);ctx.fill();ctx.font='12px system-ui';ctx.fillText(name,p[0]*scale+6,p[1]*scale-6)}
 }
 $('status').textContent=`${pack.packId} · ${action} · ${direction} · frame ${s.frameIndex} · ${playing?'playing':'paused'}`;
 $('diagnostics').textContent=JSON.stringify({frame:s.frameIndex,elapsedMs:time,cosmeticTimeMs:cosmeticTime,drawOrder:s.drawOrder,grip,visualApproval:false},null,2);
 return s;
}
$('action').onchange=()=>{action=$('action').value;time=0;forcedFrame=null;draw()};$('direction').onchange=()=>{direction=$('direction').value;forcedFrame=null;draw()};
$('play').onclick=()=>{playing=!playing;forcedFrame=null;$('play').textContent=playing?'Pause':'Play';draw()};
function step(delta){playing=false;$('play').textContent='Play';const s=sample(),frames=template.actions[action].directions[direction].frames;forcedFrame=(s.frameIndex+delta+frames.length)%frames.length;time=frames.slice(0,forcedFrame).reduce((n,f)=>n+f.durationMs,0);draw()}
$('previous').onclick=()=>step(-1);$('next').onclick=()=>step(1);$('mode').onchange=draw;$('debug').onchange=draw;
function tick(now){const dt=Math.min(now-last,100);last=now;if(playing){const elapsed=dt*Number($('speed').value);time+=elapsed;cosmeticTime+=elapsed;draw()}requestAnimationFrame(tick)}
window.characterProductionReview={
 describe:()=>({packId:pack.packId,actions:template.actions,directions:template.directions,slots:pack.slots,parts:Object.keys(pack.parts),registration:template.registration}),
 getState:()=>({action,direction,time,cosmeticTime,frame:sample().frameIndex,appearance:asset.appearance,playing,debug:$('debug').checked}),
 setAppearance:async patch=>{await asset.setAppearance(patch);draw()},
 render:({action:a,direction:d,frame=0,mode='Full composite'})=>{if(!template.actions[a]?.directions[d])throw Error('Unknown action/direction');playing=false;action=a;direction=d;forcedFrame=frame;$('action').value=a;$('direction').value=d;$('mode').value=mode;draw();return canvas.toDataURL('image/png')}
};
draw();requestAnimationFrame(tick);
})().catch(e=>{document.getElementById('status').textContent=e.message;console.error(e)});
