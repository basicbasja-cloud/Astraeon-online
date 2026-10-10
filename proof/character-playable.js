(async function(){
'use strict';
const $=id=>document.getElementById(id),params=new URLSearchParams(location.search);
if(!params.has('motion')||!params.has('appearance'))return;
const A=window.AstraeonCharacterAssembly,asset=await A.loadAssembly({motionUrl:params.get('motion'),appearanceUrl:params.get('appearance'),allowDev:true});
if(asset.compiled.pack.source?.ownerRejected)throw Error('Owner-rejected art cannot enter the new playable production test');
const player=window.AstraeonPlayableCharacter.create(asset.compiled,{x:500,y:340,appearance:asset.appearance});
const canvas=$('stage'),ctx=canvas.getContext('2d'),keys=new Set();let pointer=null,last=performance.now(),paused=false;
async function swap(patch){const applied=await asset.setAppearance(patch);if(applied)player.setAppearance(asset.appearance);return applied}
for(const [slot,definition]of Object.entries(asset.compiled.pack.slots)){
 const label=document.createElement('label');label.textContent=slot==='Head'?'Head + Hair':slot;
 const select=document.createElement('select');select.dataset.slot=slot;
 const values=Object.entries(asset.compiled.pack.parts).filter(([,part])=>part.slot===slot).map(([id])=>id);
 if(!definition.required)values.unshift('');
 for(const value of values){const option=document.createElement('option');option.value=value;option.textContent=value||'None';select.append(option)}
 select.value=asset.appearance[slot]||'';select.onchange=()=>swap({[slot]:select.value||null}).catch(fail);label.append(select);$('parts').append(label);
}
const controlKeys=['w','a','s','d','arrowup','arrowdown','arrowleft','arrowright',' '];
canvas.addEventListener('keydown',e=>{const key=e.key.toLowerCase();if(!controlKeys.includes(key))return;e.preventDefault();keys.add(key);if(key===' '&&!e.repeat)player.attack()});
canvas.addEventListener('keyup',e=>keys.delete(e.key.toLowerCase()));
function stop(){keys.clear();pointer=null;player.setMove(0,0)}
window.addEventListener('blur',stop);canvas.addEventListener('blur',stop);
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});
function point(e){const r=canvas.getBoundingClientRect();return {x:(e.clientX-r.left)*canvas.width/r.width,y:(e.clientY-r.top)*canvas.height/r.height}}
canvas.onpointerdown=e=>{canvas.focus();canvas.setPointerCapture(e.pointerId);pointer=point(e)};
canvas.onpointermove=e=>{if(pointer)pointer=point(e)};
canvas.onpointerup=canvas.onpointercancel=()=>{pointer=null};
$('attack').onclick=()=>player.attack();$('stop').onclick=stop;
function input(){let x=Number(keys.has('d')||keys.has('arrowright'))-Number(keys.has('a')||keys.has('arrowleft')),y=Number(keys.has('s')||keys.has('arrowdown'))-Number(keys.has('w')||keys.has('arrowup'));
 if(pointer){const s=player.snapshot(),dx=pointer.x-s.x,dy=pointer.y-s.y;if(Math.hypot(dx,dy)>5){x=dx;y=dy}else{x=y=0}}
 player.setMove(x,y);
}
function draw(){const s=player.snapshot();ctx.clearRect(0,0,canvas.width,canvas.height);ctx.strokeStyle='#38545d';ctx.lineWidth=1;
 for(let x=0;x<1000;x+=50){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,600);ctx.stroke()}
 for(let y=0;y<600;y+=50){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(1000,y);ctx.stroke()}
 A.drawAssembly(ctx,player.sample(),asset.images,{x:s.x,y:s.y,scale:1});
 $('status').textContent=asset.compiled.pack.packId+' · '+s.action+' · '+s.direction+' · '+asset.compiled.pack.status;
 $('diagnostics').textContent=JSON.stringify({...s,frame:player.sample().frameIndex,visualApproval:false},null,2);
}
function tick(now){const dt=Math.min(now-last,100);last=now;if(!paused){input();player.advance(dt)}draw();requestAnimationFrame(tick)}
window.characterPlayable={snapshot:()=>({...player.snapshot(),frame:player.sample().frameIndex}),setAppearance:swap,
 step:(dt,dx=0,dy=0)=>{paused=true;player.setMove(dx,dy);player.advance(dt);draw()},attack:()=>player.attack(),resume:()=>{paused=false},pause:()=>{paused=true}};
canvas.focus();draw();requestAnimationFrame(tick);
function fail(error){$('status').textContent=error.message;console.error(error)}
})().catch(error=>{document.getElementById('status').textContent=error.message;console.error(error)});
