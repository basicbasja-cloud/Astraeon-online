/* Distance-driven strategies. Duty factor and flight distinguish locomotion;
 * clips and authored contacts come from the same manifest as the foot solver. */
(() => {
'use strict';
const profiles={
 walk:{speed:1.3,cycleDistance:.95,duty:.62,lift:.10,lead:.69,clip:'warrior-walk-v3',torso:'warrior-walk-torso-v3',bodyPitch:0},
 run:{speed:2.7,cycleDistance:1.45,duty:.46,lift:.21,lead:.77,clip:'warrior-run-v3',torso:'warrior-run-torso-v3',bodyPitch:3},
 sprint:{speed:4.1,cycleDistance:1.95,duty:.38,lift:.32,lead:.81,clip:'warrior-sprint-v3',torso:'warrior-sprint-torso-v3',bodyPitch:6}
};
function configure(manifest){for(const mode of ['walk','run','sprint']){const clip=manifest.clips[mode];if(!clip||clip.cycleDistance<=0||clip.duty<=0||clip.duty>=1||clip.frames.length!==64)throw Error('Invalid locomotion manifest '+mode);profiles[mode]={...clip}}}
class Locomotion extends window.AstraeonMotion.CharacterTransform{
 constructor(...args){super(...args);this.strategy='walk';this.activeStrategy='walk';this.profile=profiles.walk;this.flight=0;this.posePitch=0;this.settlingFoot=null}
 tick(x,y,dt,options={}){
  this.groundAt=options.groundAt||(()=>options.elevation??this.position.z??0);
  this.golden=(options.archetype||'warrior')==='warrior';
  if(this.golden&&options.autoStrategy){const speed=Math.hypot(x-this.position.x,y-this.position.y)/(dt||1);this.setStrategy(options.sprint&&speed>1.8?'sprint':speed>1.8?'run':'walk')}
  super.tick(x,y,dt,options);
  this.posePitch+=((this.speed>.02&&!options.action?this.profile.bodyPitch:0)-this.posePitch)*(1-Math.exp(-14*dt));
 }
 setStrategy(name){if(!profiles[name])throw Error('Unknown locomotion '+name);this.strategy=name}
 teleport(...args){super.teleport(...args);this.settlingFoot=null;this.flight=0;this.posePitch=0}
 settleFeet(dt){
  const p=this.position,f=this.facingDirection,right={x:f.y,y:-f.x};
  const rests=[-1,1].map(side=>({x:p.x+right.x*side*.1,y:p.y+right.y*side*.1}));
  for(let i=0;i<2;i++)this.feet[i]??={...rests[i],z:0,groundZ:this.groundAt(rests[i].x,rests[i].y),swing:false,phase:0};
  if(this.settlingFoot===null){
   const distances=this.feet.map((foot,i)=>Math.hypot(foot.x-rests[i].x,foot.y-rests[i].y)+(foot.z||0));
   if(Math.max(...distances)>.015){const i=distances[0]>=distances[1]?0:1,foot=this.feet[i];this.settlingFoot=i;foot.replant={from:{x:foot.x,y:foot.y,z:foot.z||0,groundZ:foot.groundZ??p.z},to:{...rests[i],groundZ:this.groundAt(rests[i].x,rests[i].y)},time:0}}
  }
  for(let i=0;i<2;i++){
   const foot=this.feet[i];foot.swing=i===this.settlingFoot;
   if(!foot.swing){foot.z=0;continue}const step=foot.replant;step.time+=dt;const u=Math.min(1,step.time/.13),k=u*u*(3-2*u);
   foot.x=step.from.x+(step.to.x-step.from.x)*k;foot.y=step.from.y+(step.to.y-step.from.y)*k;foot.z=step.from.z*(1-u)+Math.sin(Math.PI*u)*.06;foot.groundZ=step.from.groundZ+(step.to.groundZ-step.from.groundZ)*k;
   if(u===1){foot.z=0;foot.swing=false;this.settlingFoot=null;delete foot.replant}
  }
 }
 updateFeet(walked,dt,action){
  if(this.golden===false){this.locomotionClip=null;return super.updateFeet(walked,dt,action)}
  const moving=this.speed>.02&&!action;
  // Change strategy at the next contact so a mid-swing speed change never snaps an ankle.
  const previous=this.gait%1,next=(this.gait+walked/this.profile.cycleDistance)%1;
  if(this.strategy!==this.activeStrategy&&(!moving||next<previous||previous<.5&&next>=.5)){this.activeStrategy=this.strategy;this.profile=profiles[this.strategy]}
  const profile=this.profile,p=this.position,f=this.facingDirection,right={x:f.y,y:-f.x},dir=moving?{x:this.velocity.x/this.speed,y:this.velocity.y/this.speed}:f;
  this.gait+=walked/profile.cycleDistance;this.locomotionClip=profile.clip;
  if(!moving){this.settleFeet(dt);this.flight=0;return}
  if(this.settlingFoot!==null){this.settlingFoot=null;for(const foot of this.feet)if(foot){foot.swing=false;foot.z=0;delete foot.replant}}
  for(let i=0;i<2;i++){
   const phase=(this.gait+i*.5)%1,side=i?1:-1,rest={x:p.x+right.x*side*.1,y:p.y+right.y*side*.1};let foot=this.feet[i];
   if(!foot){foot=this.feet[i]={...rest,z:0,groundZ:this.groundAt(rest.x,rest.y),swing:false,phase,from:{...rest},to:{...rest}}}
   const swing=phase>=profile.duty;
   if(swing&&!foot.swing){foot.from={x:foot.x,y:foot.y,groundZ:foot.groundZ??p.z};foot.to={x:rest.x+dir.x*profile.cycleDistance*profile.lead,y:rest.y+dir.y*profile.cycleDistance*profile.lead};foot.to.groundZ=this.groundAt(foot.to.x,foot.to.y)}
   if(swing){const t=(phase-profile.duty)/(1-profile.duty),k=t*t*(3-2*t);foot.x=foot.from.x+(foot.to.x-foot.from.x)*k;foot.y=foot.from.y+(foot.to.y-foot.from.y)*k;foot.z=Math.sin(Math.PI*t)*profile.lift;foot.groundZ=foot.from.groundZ+(foot.to.groundZ-foot.from.groundZ)*k}
   if(foot.swing&&!swing){foot.x=foot.to.x;foot.y=foot.to.y;foot.z=0;foot.groundZ=foot.to.groundZ}foot.swing=swing;foot.phase=phase;
  }
  this.flight=moving&&this.feet.every(f=>f.swing)?Math.min(...this.feet.map(f=>f.z))*.25:0;
 }
 snapshot(){const {frames,...profile}=this.profile;return {...super.snapshot(),feet:this.feet.map(f=>f?{x:f.x,y:f.y,z:f.z,groundZ:f.groundZ,swing:f.swing}:null),gait:this.gait,strategy:this.strategy,activeStrategy:this.activeStrategy,profile,flight:this.flight}}
}
window.AstraeonLocomotionV3={profiles,Locomotion,configure};
})();
