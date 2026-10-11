// Original kinematic blocking study. Public artwork is not sampled into this rig.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {solveLimb,add,sub,mul,length,unit,dot,rotate,project} from '../motion-lab/motion.mjs';
const OUT=new URL('.',import.meta.url);
const times=[0,.08,.18,.28,.34,.40,.52,.66];
const duration=.8;
const phases=['ready','load_rear_leg','coil','drive','cut','follow_through','recover','ready'];
const data={
  hipY:[0,-.06,-.12,.04,.15,.20,.025,0],
  hipZ:[.65,.59,.56,.68,.68,.60,.635,.65],
  pelvisTwist:[0,-.08,-.20,.10,.24,.28,.04,0],
  chestTwist:[0,-.20,-.42,.18,.45,.48,.08,0],
  lean:[-.02,-.06,-.09,.10,.18,.22,.04,-.02],
  heelPitch:[0,0,.04,.27,.40,.43,.08,0],
  rightHand:[[-.30,.02,.15],[-.29,-.07,.32],[-.19,-.07,.68],[-.25,.32,.56],[-.22,.43,.20],[-.23,.39,.16],[-.30,.10,.19],[-.30,.02,.15]],
  leftHand:[[.32,.05,.16],[.31,.10,.19],[.31,.16,.22],[.29,-.16,.21],[.29,-.22,.21],[.29,-.15,.17],[.32,.04,.17],[.32,.05,.16]],
  sword:[[0,.55,-.85],[0,-.12,.99],[0,-.38,.92],[0,.95,.32],[0,.82,-.57],[0,.40,-.916],[0,.58,-.82],[0,.55,-.85]]
};
function sample(values,t){
  let i=0;for(let k=0;k<times.length;k++)if(t>=times[k])i=k;
  if(i===times.length-1)return values[i];
  const u=Math.max(0,Math.min(1,(t-times[i])/(times[i+1]-times[i]))),s=u*u*(3-2*u);
  const mix=(a,b)=>a+(b-a)*s;
  return Array.isArray(values[i])?values[i].map((a,k)=>mix(a,values[i+1][k])):mix(values[i],values[i+1]);
}
function pitch(p,a){const c=Math.cos(a),s=Math.sin(a);return [p[0],p[1]*c+p[2]*s,-p[1]*s+p[2]*c];}
function pose(t){
  const hip=[0,sample(data.hipY,t),sample(data.hipZ,t)];
  const pelvisTwist=sample(data.pelvisTwist,t),chestTwist=sample(data.chestTwist,t),lean=sample(data.lean,t),heelPitch=sample(data.heelPitch,t);
  const frontToe=[.24,.28,0],frontHeel=[.24,.02,0];
  const rearToe=[-.24,.015,0],rearHeel=add(rearToe,pitch([0,-.26,0],heelPitch));
  const feet={left:{toe:frontToe,heel:frontHeel,ankle:[.24,.15,.085],contact:'sole'},right:{toe:rearToe,heel:rearHeel,ankle:add(rearToe,pitch([0,-.095,.085],heelPitch)),contact:heelPitch>.02?'toe':'sole'}};
  const legs={},arms={};
  for(const side of ['right','left']){
    const sign=side==='right'?-1:1;
    const hipJoint=add(hip,rotate([sign*.13,0,0],pelvisTwist));
    legs[side]=solveLimb(hipJoint,feet[side].ankle,.34,.34,[0,1,0]);
    const shoulder=add(hip,rotate([sign*.28,lean,.43],chestTwist));
    const hand=add(hip,rotate(sample(data[side+'Hand'],t),chestTwist));
    arms[side]=solveLimb(shoulder,hand,.31,.31,[sign*.25,-.35,-.3]);
  }
  const head=add(hip,[0,lean*1.35,.84]);
  const swordDirection=unit(rotate(sample(data.sword,t),chestTwist));
  const swordTip=add(arms.right.end,mul(swordDirection,.72));
  return {time:t,hip,pelvisTwist,chestTwist,lean,head,feet,legs,arms,swordDirection,swordTip,root:[0,0,0]};
}
function angle(limb){const a=unit(sub(limb.start,limb.joint)),b=unit(sub(limb.end,limb.joint));return Math.acos(Math.max(-1,Math.min(1,dot(a,b))))*180/Math.PI;}
const samples=Array.from({length:401},(_,i)=>pose(i*duration/400));
const initial=pose(0);let maximumPlantDrift=0,maximumBoneLengthError=0,unreachable=[];
for(const p of samples){
  assert.deepEqual(p.root,[0,0,0]);
  for(const side of ['right','left']){
    maximumPlantDrift=Math.max(maximumPlantDrift,length(sub(p.feet[side].toe,initial.feet[side].toe)));
    if(side==='left')maximumPlantDrift=Math.max(maximumPlantDrift,length(sub(p.feet.left.heel,initial.feet.left.heel)));
    for(const [family,bone] of [['legs',.34],['arms',.31]]){
      const l=p[family][side];if(!l.reachable)unreachable.push([p.time,family,side]);
      maximumBoneLengthError=Math.max(maximumBoneLengthError,Math.abs(length(sub(l.start,l.joint))-bone),Math.abs(length(sub(l.end,l.joint))-bone));
    }
  }
  assert.ok(Math.abs(length(sub(p.swordTip,p.arms.right.end))-.72)<1e-8);
  assert.ok(p.swordTip[2] >= 0, 'Blade penetrates ground');
}
const range=values=>Math.max(...values)-Math.min(...values);
const report={scope:'Original kinematic motion blocking, not final sprite art or measured dynamics',samples:samples.length,
  maximumPlantedToeOrFrontHeelDrift_world:maximumPlantDrift,maximumBoneLengthError_world:maximumBoneLengthError,
  unreachableTargetCount:unreachable.length,unreachableExamples:unreachable.slice(0,8),
  hipForwardRange_world:range(samples.map(p=>p.hip[1])),hipVerticalRange_world:range(samples.map(p=>p.hip[2])),
  rearKneeAngleRange_degrees:range(samples.map(p=>angle(p.legs.right))),frontKneeAngleRange_degrees:range(samples.map(p=>angle(p.legs.left))),
  pelvisRotationRange_degrees:range(samples.map(p=>p.pelvisTwist))*180/Math.PI,
  shoulderRotationRange_degrees:range(samples.map(p=>p.chestTwist))*180/Math.PI,
  maximumRearHeelLift_world:Math.max(...samples.map(p=>p.feet.right.heel[2])),
  projectedDirections:8,handedness:'Right hand remains anatomical right; no mirrored facing substitution',
  limitations:['No center-of-mass dynamics, ground reaction forces or force simulation','Kinematic reach/contact checks cannot establish acting quality or production art acceptance']};
fs.writeFileSync(new URL('motion-proof-report.json',OUT),JSON.stringify(report,null,2)+'\n');
assert.equal(unreachable.length,0,JSON.stringify(report));assert.ok(maximumPlantDrift<1e-10);assert.ok(maximumBoneLengthError<1e-8);
assert.ok(report.rearKneeAngleRange_degrees>15);assert.ok(report.frontKneeAngleRange_degrees>15);
assert.ok(report.hipForwardRange_world>.25);assert.ok(report.maximumRearHeelLift_world>.08);
const keys=times.map((t,i)=>({...pose(t),phase:phases[i],duration_ms:Math.round(((times[i+1]??duration)-t)*1000)}));
const projected=Array.from({length:8},(_,d)=>keys.map(p=>({...p,direction:d,projected:{
  hip:project(p.hip,d,30),head:project(p.head,d,30),swordTip:project(p.swordTip,d,30),
  legs:Object.fromEntries(Object.entries(p.legs).map(([s,l])=>[s,Object.fromEntries(['start','joint','end'].map(k=>[k,project(l[k],d,30)]))])),
  arms:Object.fromEntries(Object.entries(p.arms).map(([s,l])=>[s,Object.fromEntries(['start','joint','end'].map(k=>[k,project(l[k],d,30)]))])),
  feet:Object.fromEntries(Object.entries(p.feet).map(([s,f])=>[s,Object.fromEntries(['toe','heel','ankle'].map(k=>[k,project(f[k],d,30)]))]))
}})));
fs.writeFileSync(new URL('motion-proof-poses.json',OUT),JSON.stringify({duration_ms:800,keys,directions:projected},null,2)+'\n');
console.log(JSON.stringify(report,null,2));
