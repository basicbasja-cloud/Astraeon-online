/* Pose timing and subtle root motion for painted sprites. Does not change gameplay geometry. */
(() => {
'use strict';
const clamp=n=>Math.max(0,Math.min(1,n)),smooth=n=>{n=clamp(n);return n*n*(3-2*n)};
function sample(state,progress,impactAt=.45,gait=0,speed=0){
 let x=0,lift=0,lean=0,stretch=1;
 const p=clamp(progress),contact=Math.max(.08,Math.min(.85,impactAt));
 if(['walk','run','sprint','start'].includes(state)&&speed>.02){
  const cycle=gait*Math.PI*2,weight=Math.min(1,speed/2.3);
  lift=(1-Math.cos(cycle*2))*.5*weight;lean=Math.sin(cycle)*.012*weight;
 }else if(state==='attack'){
  if(p<contact){x=-1.3*smooth(p/contact);lean=-.025*smooth(p/contact)}
  else{const settle=smooth((p-contact)/(1-contact));x=3.2*(1-settle);lean=.035*(1-settle)}
 }else if(state==='cast'){lift=Math.sin(p*Math.PI)*1.4;stretch=1+Math.sin(p*Math.PI)*.012}
 else if(state==='dodge'){lift=Math.sin(p*Math.PI)*1.6;lean=.055*Math.sin(p*Math.PI)}
 else if(state==='hit'){x=-2*Math.sin(p*Math.PI);lean=-.035*Math.sin(p*Math.PI)}
 return {x,lift,lean,stretch};
}
function actionPose(state,progress,impactAt=.45){
 const contact=Math.max(.08,Math.min(.85,impactAt));
 if(state==='attack'||state==='cast')return progress<contact*.16?0:progress<contact?3:progress>contact+(1-contact)*.72?0:4;
 if(['dodge','hit','death','pickup'].includes(state))return 5;
 if(state==='interact')return 3;
 return 0;
}
window.AstraeonSpriteMotion={sample,actionPose};
})();
