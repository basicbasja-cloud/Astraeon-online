'use strict';
/* Synthetic motion fixture only. Never an RO or Swordsman choreography source. */
const fs=require('node:fs'),path=require('node:path');
const M=require('../character-motion-template.js');
const out=process.argv[2]||path.join(__dirname,'../authoring/characters/motion-templates/assembly-debug');
const root={x:64,y:112,rotation:0,scale:1},T=(x,y,rotation=0,scale=1)=>({x,y,rotation,scale});
const front=[...M.LAYERS],rear=[...M.LAYERS];
rear.splice(rear.indexOf('OffHand'),1);rear.splice(rear.indexOf('Body'),0,'OffHand');
rear.splice(rear.indexOf('MainHand'),1);rear.splice(rear.indexOf('Body'),0,'MainHand');
const frameOrder=[...front];frameOrder.splice(frameOrder.indexOf('MainHand'),1);frameOrder.splice(frameOrder.indexOf('Body'),0,'MainHand');
const t={schemaVersion:'1.0',motionTemplateId:'assembly-debug-motion-v1',status:'DEV_ONLY',provenance:{kind:'SYNTHETIC_ENGINE_FIXTURE',description:'Engineering shape motion, not RO keys, not gait, not sword choreography.'},directions:[...M.DIRECTIONS],registration:{canvas:[128,128],root,referenceHeight:70,mirroring:'none'},transformConvention:'canvas pixels; clockwise radians; uniform positive scale',drawProfiles:{front,rear,frameCross:frameOrder},defaultDrawProfile:'front',actions:{}};
const configs={Idle:{loop:true,durations:[240,360],inserts:[[.5],[.5]]},Walk:{loop:true,durations:[160,240,160,240],inserts:[[.35,.7],[.5],[.5],[.5]]},BasicAttack:{loop:false,durations:[200,120,280],inserts:[[.4],[.5],[]]}};
for(const [action,c] of Object.entries(configs)){
 const directions={};
 for(const [di,direction] of M.DIRECTIONS.entries()){
  const keys=c.durations.map((durationMs,i)=>{
   const offset=[0,-2,0,2][i],angle=[-.3,.2,.6,-.1][i];
   // Direction-specific, asymmetric calibration markers. No mirrored views.
   const horizontal=[-15,-13,-18,-13,15,13,18,13][di];
   const anchors={root:{...root},head:T(64,43+offset),mainHand:T(64+horizontal,75+offset,angle+di*.16),offHand:T(64-horizontal,75-offset,-angle,.9),back:T(64,61+offset,0),waist:T(64,85+offset),footL:T(58,112),footR:T(70,112),weaponTip:T(64+horizontal,51+offset),fxOrigin:T(64,91)};
   const f={id:`${action}/${direction}/key${i}`,durationMs,role:'referenceKey',referencePhase:`debugKey${i}`,root:{...root},anchors,events:[],poseIntent:{bodyOrientation:direction,limbPhase:'synthetic calibration',footContact:'static markers; not a reference gait',attackPhase:'no sword choreography',silhouette:'geometric fixture'},source:{kind:'SYNTHETIC_ENGINE_FIXTURE'}};
   if(action==='BasicAttack'&&i===1){f.drawProfile='frameCross';f.events=[{name:'debugMarker',authority:'presentation'}]}
   return f;
  });
  let seq={totalDurationMs:c.durations.reduce((a,b)=>a+b,0),referenceKeys:keys,frames:keys};
  if(['W','NW','N','NE'].includes(direction))seq.drawProfile='rear';
  const schedule={};c.inserts.forEach((arr,i)=>{if(arr.length)schedule[keys[i].id]=arr.map((at,j)=>({id:`${action}/${direction}/between${i}-${j}`,at}))});
  directions[direction]=M.smoothSequence(seq,schedule,c.loop);
 }
 t.actions[action]={loop:c.loop,directions};
}
M.compileMotionTemplate(t);
fs.mkdirSync(out,{recursive:true});fs.writeFileSync(path.join(out,'motion-template.json'),JSON.stringify(t,null,2)+'\n');
console.log('Built synthetic assembly motion fixture',t.motionTemplateId);
