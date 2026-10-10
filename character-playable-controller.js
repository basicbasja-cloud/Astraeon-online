/* Presentation-only input controller. Combat and damage remain outside this module. */
(function(scope){
'use strict';
const A=scope.AstraeonCharacterAssembly||(typeof require==='function'?require('./character-assembly.js'):null);
const dirs=['E','SE','S','SW','W','NW','N','NE'];
function facing(x,y){return dirs[(Math.round(Math.atan2(y,x)/(Math.PI/4))+8)%8]}
function create(compiled,{x=400,y=300,speed=120,direction='S',appearance={}}={}){
 if(![x,y,speed].every(Number.isFinite)||speed<=0)throw Error('Invalid movement configuration');
 for(const action of ['Idle','Walk','BasicAttack'])if(!compiled.motion.template.actions[action])throw Error('Playable character requires '+action);
 const animation=A.createController(compiled,{action:'Idle',direction,appearance});
 let action='Idle',facingDirection=direction,moveX=0,moveY=0,attacking=false;
 const switchAction=next=>{if(next!==action){animation.setAction(next);action=next}};
 function move(dt){
  const length=Math.hypot(moveX,moveY);
  switchAction(length?'Walk':'Idle');
  if(length){facingDirection=facing(moveX,moveY);animation.setDirection(facingDirection);x+=moveX/length*speed*dt/1000;y+=moveY/length*speed*dt/1000;}
  animation.advance(dt);
 }
 return Object.freeze({
  setMove:(dx,dy)=>{if(![dx,dy].every(Number.isFinite))throw Error('Invalid input');moveX=dx;moveY=dy},
  attack:()=>{if(attacking)return false;attacking=true;switchAction('BasicAttack');return true},
  advance:dt=>{
   if(!Number.isFinite(dt)||dt<0)throw Error('Invalid elapsed time');
   if(attacking){
    const remaining=Math.max(0,compiled.motion.duration('BasicAttack',facingDirection)-animation.elapsedMs);
    const consumed=Math.min(dt,remaining);animation.advance(consumed);dt-=consumed;
    if(consumed===remaining){attacking=false;move(dt)}
   }else move(dt);
  },
  setAppearance:patch=>animation.setAppearance(patch),
  sample:()=>animation.sample(),
  snapshot:()=>({x,y,action,direction:facingDirection,attacking,elapsedMs:animation.elapsedMs,cosmeticTimeMs:animation.cosmeticTimeMs,appearance:animation.appearance})
 });
}
const api=Object.freeze({create,facing});scope.AstraeonPlayableCharacter=api;
if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
