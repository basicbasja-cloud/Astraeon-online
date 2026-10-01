/* World-space transforms and locomotion. No DOM, renderer, clock, or save dependency. */
(() => {
'use strict';
const TAU=Math.PI*2;
const wrap=a=>Math.atan2(Math.sin(a),Math.cos(a));
const profiles={warrior:{turnSpeed:9,turnAcceleration:48},mage:{turnSpeed:10,turnAcceleration:55},ranger:{turnSpeed:12,turnAcceleration:65}};
const FacingMode=Object.freeze({Movement:'movement',Target:'target',Aim:'aim',Locked:'locked'});
class CharacterTransform {
 constructor(x=0,y=0,heading=Math.PI/2){
  this.position={x,y,z:0};this.rotation=heading;this.desiredRotation=heading;
  this.facingDirection={x:Math.cos(heading),y:Math.sin(heading)};
  this.velocity={x:0,y:0};this.angularVelocity=0;this.mode=FacingMode.Movement;
  this.distance=0;this.speed=0;this.state='idle';this.transition=1;this.stateTime=0;
  this.feet=[null,null];this.gait=0;this.grounded=true;
 }
 face(x,y,mode=FacingMode.Target){if(Math.hypot(x,y)<1e-6)return;this.desiredRotation=Math.atan2(y,x);this.mode=mode}
 snapFacing(x,y,mode=FacingMode.Locked){this.face(x,y,mode);this.rotation=this.desiredRotation;this.angularVelocity=0;this.facingDirection={x:Math.cos(this.rotation),y:Math.sin(this.rotation)}}
 teleport(x,y,z=0){this.position={x,y,z};this.velocity={x:0,y:0};this.speed=0;this.feet=[null,null];this.gait=0}
 tick(x,y,dt,{archetype='warrior',action=null,sprint=false,elevation=0}={}){
  if(dt<=0)return;
  const dx=x-this.position.x,dy=y-this.position.y,walked=Math.hypot(dx,dy);
  // A zone transition is not locomotion, even if it occurs during a simulation tick.
  if(walked>2){this.teleport(x,y,elevation);return}
  this.velocity={x:dx/dt,y:dy/dt};this.speed=walked/dt;this.distance+=walked;
  if(this.mode===FacingMode.Movement&&walked>1e-5)this.desiredRotation=Math.atan2(dy,dx);
  const profile=profiles[archetype]||profiles.warrior,error=wrap(this.desiredRotation-this.rotation);
  if(this.mode!==FacingMode.Locked){
   const wanted=Math.sign(error)*Math.min(profile.turnSpeed,Math.sqrt(2*profile.turnAcceleration*Math.abs(error))),delta=wanted-this.angularVelocity;
   this.angularVelocity+=Math.max(-profile.turnAcceleration*dt,Math.min(profile.turnAcceleration*dt,delta));
   const step=this.angularVelocity*dt;
   if(Math.abs(step)>=Math.abs(error)&&Math.sign(step)===Math.sign(error)){this.rotation=this.desiredRotation;this.angularVelocity=0}else this.rotation=wrap(this.rotation+step);
  }
  this.facingDirection={x:Math.cos(this.rotation),y:Math.sin(this.rotation)};
  this.position={x,y,z:elevation};
  let state=action||(this.speed>.02?(sprint?'sprint':this.speed<1.8?'walk':'run'):Math.abs(error)>.08?'turn':'idle');
  if(!action&&this.speed>.02&&['idle','turn','stop'].includes(this.state))state='start';
  if(!action&&this.speed<=.02&&['walk','run','sprint','start'].includes(this.state))state='stop';
  if(this.state===state){this.stateTime+=dt;this.transition=Math.min(1,this.transition+dt*10)}else{this.state=state;this.stateTime=0;this.transition=0}
  this.updateFeet(walked,dt,action);
 }
 updateFeet(walked,dt,action){
  const p=this.position,f=this.facingDirection,right={x:f.y,y:-f.x},moving=this.speed>.02&&action!=='dodge',stride=.95;
  const dir=moving?{x:this.velocity.x/this.speed,y:this.velocity.y/this.speed}:f;
  this.gait+=walked/stride;
  for(let i=0;i<2;i++){
   const side=i?1:-1,phase=(this.gait+i*.5)%1;
   const rest={x:p.x+right.x*side*.10,y:p.y+right.y*side*.10,z:0};
   let foot=this.feet[i];
   if(!foot){foot=this.feet[i]={...rest,phase,swing:false,from:rest,to:rest};continue}
   if(!moving){
    // Replant after stopping, turning, knockback, or dodge; never translate a stance foot with the root.
    const k=1-Math.exp(-14*dt);foot.x+=(rest.x-foot.x)*k;foot.y+=(rest.y-foot.y)*k;foot.z*=1-k;foot.swing=false;foot.phase=phase;continue;
   }
   const swing=phase>=.5;
   if(swing&&!foot.swing){foot.from={x:foot.x,y:foot.y};foot.to={x:rest.x+dir.x*stride*.725,y:rest.y+dir.y*stride*.725};}
   if(swing){const t=(phase-.5)/.5,s=t*t*(3-2*t);foot.x=foot.from.x+(foot.to.x-foot.from.x)*s;foot.y=foot.from.y+(foot.to.y-foot.from.y)*s;foot.z=Math.sin(t*Math.PI)*.18}
   // During stance, x/y are deliberately unchanged in world coordinates.
   if(foot.swing&&!swing){foot.x=foot.to.x;foot.y=foot.to.y;foot.z=0}foot.swing=swing;foot.phase=phase;
  }
 }
 snapshot(){return{position:{...this.position},rotation:this.rotation,desiredRotation:this.desiredRotation,facingDirection:{...this.facingDirection},velocity:{...this.velocity},angularVelocity:this.angularVelocity,mode:this.mode,speed:this.speed,state:this.state,distance:this.distance,feet:this.feet.map(f=>f?{x:f.x,y:f.y,z:f.z,swing:f.swing}:null)}}
}
// Convert camera-relative axes using the inverse ground projection, retain analog magnitude.
function cameraMovement(x,y,unproject){const magnitude=Math.min(1,Math.hypot(x,y));if(magnitude<.08)return{x:0,y:0,magnitude:0};const v=unproject(x,y),n=Math.hypot(v.x,v.y);return{x:v.x/n*magnitude,y:v.y/n*magnitude,magnitude}}
window.AstraeonMotion={CharacterTransform,FacingMode,profiles,wrap,cameraMovement,TAU};
})();
