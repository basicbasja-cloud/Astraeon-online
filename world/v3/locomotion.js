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
 constructor(...args){super(...args);this.strategy='walk';this.activeStrategy='walk';this.profile=profiles.walk;this.flight=0}
 setStrategy(name){if(!profiles[name])throw Error('Unknown locomotion '+name);this.strategy=name}
 updateFeet(walked,dt,action){
  const moving=this.speed>.02&&!action;
  // Change strategy at the next contact so a mid-swing speed change never snaps an ankle.
  const previous=this.gait%1,next=(this.gait+walked/this.profile.cycleDistance)%1;
  if(this.strategy!==this.activeStrategy&&(!moving||next<previous||previous<.5&&next>=.5)){this.activeStrategy=this.strategy;this.profile=profiles[this.strategy]}
  const profile=this.profile,p=this.position,f=this.facingDirection,right={x:f.y,y:-f.x},dir=moving?{x:this.velocity.x/this.speed,y:this.velocity.y/this.speed}:f;
  this.gait+=walked/profile.cycleDistance;this.locomotionClip=profile.clip;
  for(let i=0;i<2;i++){
   const phase=(this.gait+i*.5)%1,side=i?1:-1,rest={x:p.x+right.x*side*.1,y:p.y+right.y*side*.1};let foot=this.feet[i];
   if(!foot){foot=this.feet[i]={...rest,z:0,swing:false,phase,from:{...rest},to:{...rest}}}
   if(!moving){const k=1-Math.exp(-14*dt);foot.x+=(rest.x-foot.x)*k;foot.y+=(rest.y-foot.y)*k;foot.z*=1-k;foot.swing=false;foot.phase=phase;continue}
   const swing=phase>=profile.duty;
   if(swing&&!foot.swing){foot.from={x:foot.x,y:foot.y};foot.to={x:rest.x+dir.x*profile.cycleDistance*profile.lead,y:rest.y+dir.y*profile.cycleDistance*profile.lead}}
   if(swing){const t=(phase-profile.duty)/(1-profile.duty),k=t*t*(3-2*t);foot.x=foot.from.x+(foot.to.x-foot.from.x)*k;foot.y=foot.from.y+(foot.to.y-foot.from.y)*k;foot.z=Math.sin(Math.PI*t)*profile.lift}
   if(foot.swing&&!swing){foot.x=foot.to.x;foot.y=foot.to.y;foot.z=0}foot.swing=swing;foot.phase=phase;
  }
  this.flight=moving&&this.feet.every(f=>f.swing)?Math.min(...this.feet.map(f=>f.z))*.25:0;
 }
 snapshot(){const {frames,...profile}=this.profile;return {...super.snapshot(),gait:this.gait,strategy:this.strategy,activeStrategy:this.activeStrategy,profile,flight:this.flight}}
}
window.AstraeonLocomotionV3={profiles,Locomotion,configure};
})();
