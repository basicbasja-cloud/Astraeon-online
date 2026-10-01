/* Golden proof entry: existing save/combat/game entry is deliberately independent.
 * All routes (including inspect buttons) use the production A* and collision path. */
(async()=>{
'use strict';
const $=id=>document.getElementById(id),state=$('state');
try{
 const [data,manifest]=await Promise.all(['world/v3/golden-proof.json','world/v3/warrior-animation.json'].map(async path=>{const r=await fetch(path);if(!r.ok)throw Error('Missing '+path);return r.json()}));
 AstraeonLocomotionV3.configure(manifest);for(const clip of Object.values(manifest.clips))AstraeonHeroRegistration[clip.clip].frames=clip.frames;
 const world=AstraeonSpatialV3.compile(data),canvas=document.createElement('canvas');$('scene').appendChild(canvas);
 const view=new AstraeonCanvasV3.WorldView(canvas,world),warrior=new AstraeonCanvasV3.WarriorView(manifest);await warrior.load();
 const actor=new AstraeonLocomotionV3.Locomotion(...data.spawn.slice(0,2));actor.tick(actor.position.x,actor.position.y,.016);
 let route=[],goal=null,lastInteraction='',scrub=false,totalTime=0,steps=0,frames=[],inspectTime=0;const keys=new Set();
 function navigate(x,y){if(scrub)return;if(world.blocked(x,y)){state.textContent='Solid structure — choose clear ground';return}const path=world.route(actor.position,{x,y});if(!path){state.textContent='No traversable route';return}route=path;goal={x,y};lastInteraction='';state.textContent='Following authored circulation'}
 for(const stop of data.route){const b=document.createElement('button');b.textContent=stop.name;b.dataset.stop=stop.name;b.onclick=()=>navigate(...stop.position);$('route').appendChild(b)}
 $('tools-toggle').onclick=()=>{$('tools').hidden=!$('tools').hidden;$('tools-toggle').setAttribute('aria-expanded',String(!$('tools').hidden))};document.querySelectorAll('[data-overlay]').forEach(e=>e.onchange=()=>view.setDebug(e.dataset.overlay,e.checked));
 $('strategy').onchange=()=>actor.setStrategy($('strategy').value);
 $('scrub-enable').onchange=()=>{scrub=$('scrub-enable').checked;route=[];goal=null;keys.clear();if(!scrub){actor.mode=AstraeonMotion.FacingMode.Movement;actor.feet=[null,null];actor.flight=0}document.querySelectorAll('#route button').forEach(b=>b.disabled=scrub)};
 const interactive=e=>e.target.closest('input,select,textarea,[contenteditable="true"]');
 addEventListener('keydown',e=>{if(interactive(e))return;if(['w','a','s','d','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Shift'].includes(e.key)){e.preventDefault();keys.add(e.key)}});addEventListener('keyup',e=>keys.delete(e.key));addEventListener('blur',()=>keys.clear());
 canvas.addEventListener('pointerdown',e=>{const r=canvas.getBoundingClientRect(),p=view.screenToWorld(e.clientX-r.left,e.clientY-r.top);navigate(p.x,p.y)});
 let last=performance.now();function loop(time){
  const frameMs=time-last;last=time;const dt=Math.min(.035,frameMs/1000);totalTime+=dt;frames.push(frameMs);if(frames.length>600)frames.shift();
  if(scrub){actor.activeStrategy=actor.strategy;actor.profile=AstraeonLocomotionV3.profiles[actor.strategy];actor.gait=+$('phase').value;actor.flight=0;const angle=Math.PI/2-(+$('facing').value)*Math.PI/4,dir=AstraeonView.inverse(Math.cos(angle),Math.sin(angle)),n=Math.hypot(dir.x,dir.y);actor.snapFacing(dir.x/n,dir.y/n);const row=+$('facing').value,col=Math.floor(actor.gait*8),frame=manifest.clips[actor.strategy].frames[row*8+col];actor.feet=frame.contacts.map(c=>{const local=AstraeonView.inverse((c.foot[0]-frame.footAnchorX)*.5,(c.foot[1]-frame.footAnchorY)*.5);return{x:actor.position.x+local.x,y:actor.position.y+local.y,z:0,swing:!c.stance,phase:c.gaitPhase}})}
  else{
   const ix=(keys.has('d')||keys.has('ArrowRight')?1:0)-(keys.has('a')||keys.has('ArrowLeft')?1:0),iy=(keys.has('s')||keys.has('ArrowDown')?1:0)-(keys.has('w')||keys.has('ArrowUp')?1:0);let direction=null;
   actor.setStrategy(keys.has('Shift')?'sprint':$('strategy').value);
   if(ix||iy){route=[];goal=null;direction=AstraeonMotion.cameraMovement(ix,iy,AstraeonView.inverse)}
   else if(route.length){const target=route[0],dx=target.x-actor.position.x,dy=target.y-actor.position.y,length=Math.hypot(dx,dy);if(length<.08)route.shift();else direction={x:dx/length,y:dy/length,magnitude:Math.min(1,length/(actor.profile.speed*dt))}}
   let x=actor.position.x,y=actor.position.y;if(direction){const speed=AstraeonLocomotionV3.profiles[actor.strategy].speed,dx=direction.x*speed*dt*(direction.magnitude||1),dy=direction.y*speed*dt*(direction.magnitude||1);if(!world.blocked(x+dx,y+dy)){x+=dx;y+=dy}else if(!world.blocked(x+dx,y)){x+=dx}else if(!world.blocked(x,y+dy)){y+=dy}else route=[]}
   actor.tick(x,y,dt,{sprint:actor.strategy==='sprint',elevation:world.elevationAt(x,y)});if(actor.speed>.02)steps++;
  }
  view.update(actor,warrior.draw(actor,{scrub}),dt);
  if(!scrub&&goal&&!route.length){const interaction=world.interactionAt(actor.position.x,actor.position.y);lastInteraction=interaction?.id||'';state.textContent=interaction?'Reached '+interaction.id:'Route complete';goal=null}
  inspectTime+=dt;if(inspectTime>.12){inspectTime=0;$('telemetry').textContent=`${actor.activeStrategy} · ${actor.state}\nclip ${warrior.frame.clip}\nview ${manifest.directions[warrior.frame.row]} · frame ${warrior.frame.column}\ncycle ${actor.profile.cycleDistance.toFixed(2)} units\ncontact ${actor.feet.map((f,i)=>f&&!f.swing?(i?'right':'left'):'').filter(Boolean).join(' + ')||'flight'}\noccluded: ${view.occlusion.join(', ')||'none'}\n${(1000/(frames.reduce((a,b)=>a+b,0)/frames.length)).toFixed(0)} fps · ${world.parts.length} mesh parts`}
  requestAnimationFrame(loop);
 }requestAnimationFrame(loop);
 // Read-only diagnostic interface. Input and inspector use exactly the same paths.
 window.AstraeonProof=Object.freeze({snapshot:()=>({version:3,time:totalTime,player:actor.snapshot(),frame:structuredClone(warrior.frame),route:structuredClone(route),goal:goal?{...goal}:null,lastInteraction,steps,view:view.snapshot(),renderer:'Canvas2D',frameMs:[...frames],solids:world.solids.map(p=>({id:p.id,footprint:p.footprint})),navCells:world.navCells.length}),screen:(x,y)=>view.worldToScreen(x,y)});
 state.textContent='Ready · click clear ground or choose a route';
}catch(error){state.textContent='Proof could not start: '+error.message;console.error(error)}
})();
