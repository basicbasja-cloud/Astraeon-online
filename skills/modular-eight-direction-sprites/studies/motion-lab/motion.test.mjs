import test from 'node:test';
import assert from 'node:assert/strict';
import {DIRECTIONS,STRIDE,DUTY,PERIOD,footAt,pose,solveLimb,sub,add,length,rotate,project,viewIndex,mapPhase,createState,swapAppearance,sampleTime,clipDuration,poseTimeline} from './motion.mjs';
const near=(a,b,tol=1e-8)=>assert.ok(Math.abs(a-b)<=tol,`${a} differs from ${b}`);
const vectorNear=(a,b,tol=1e-8)=>a.forEach((v,i)=>near(v,b[i],tol));

test('World-space stance feet stay planted across four gait cycles, both sides and eight directions',()=>{
  let comparisons=0,maxDrift=0;
  for(const side of ['left','right'])for(let i=0;i<4000;i++){
    const c=i/1000,dc=.00001,a=footAt(c,side),b=footAt(c+dc,side),offset=side==='left'?0:.5;
    if(!a.contact||!b.contact||Math.floor(c+offset)!==Math.floor(c+dc+offset))continue;
    const wa=add(a.point,[0,STRIDE*c,0]),wb=add(b.point,[0,STRIDE*(c+dc),0]);
    for(let d=0;d<8;d++){const drift=length(sub(rotate(wa,d*Math.PI/4),rotate(wb,d*Math.PI/4)));maxDrift=Math.max(maxDrift,drift);assert.ok(drift<1e-9);comparisons++;}
  }
  assert.ok(comparisons>30000);
});

test('Toe-off and landing are position/velocity continuous; ground penetration absent',()=>{
  const h=1e-6;
  for(const side of ['left','right'])for(const boundary of [DUTY,1]){
    const offset=side==='left'?0:.5,c=boundary-offset;
    const a=footAt(c-h,side).point,b=footAt(c,side).point,e=footAt(c+h,side).point;
    near((b[1]-a[1])/h,-STRIDE,2e-5);near((e[1]-b[1])/h,-STRIDE,2e-5);
    near((b[2]-a[2])/h,0,2e-5);near((e[2]-b[2])/h,0,2e-5);
  }
  for(let i=0;i<2000;i++)for(const side of ['left','right'])assert.ok(footAt(i/1000,side).point[2]>=0);
});

test('All clips keep fixed bone lengths and reachable feet/hands in dense samples',()=>{
  for(const action of ['idle','walk','attack'])for(let i=0;i<1000;i++){
    const p=pose(action,i/1000*(action==='attack'?.72:PERIOD));
    for(const side of ['left','right'])for(const [limb,segment] of [[p.legs[side],.34],[p.arms[side],.27]]){
      assert.ok(limb.reachable,`${action} ${side} at ${i}`);
      near(length(sub(limb.start,limb.joint)),segment);near(length(sub(limb.end,limb.joint)),segment);
    }
    for(const side of ['left','right'])vectorNear(p.legs[side].end,add(p.feet[side].point,[0,0,.065]));
  }
});

test('Two-bone solver reports unreachable targets and handles collinear bend hints',()=>{
  for(const [target,l1,l2] of [[[0,0,3],1,1],[[0,0,.1],1,.5]]){
    const l=solveLimb([0,0,0],target,l1,l2,[0,0,1]);assert.equal(l.reachable,false);
    near(length(sub(l.start,l.joint)),l1);near(length(sub(l.end,l.joint)),l2);
    assert.ok(l.joint.every(Number.isFinite));
  }
  assert.throws(()=>solveLimb([0,0,0],[1,0,0],0,1));
});

test('Walk animates hip, torso, head, both arms and both legs; attack feet remain fixed',()=>{
  const a=pose('walk',.07),b=pose('walk',.27);
  for(const key of ['hip','head'])assert.ok(length(sub(a[key],b[key]))>.002);
  assert.ok(Math.abs(a.twist-b.twist)>.002);
  for(const side of ['left','right']) {
    assert.ok(length(sub(a.arms[side].end,b.arms[side].end))>.01);
    assert.ok(length(sub(a.legs[side].joint,b.legs[side].joint))>.01);
    const initial=pose('attack',0).feet[side].point;
    for(let i=0;i<1000;i++)vectorNear(initial,pose('attack',i*.00072).feet[side].point);
  }
});

test('Loop boundaries return the same body-relative pose for every action',()=>{
  for(const action of ['idle','walk','attack']){
    const duration=action==='attack'?.72:PERIOD,a=pose(action,0),b=pose(action,duration);
    vectorNear(a.hip,b.hip);vectorNear(a.head,b.head);near(a.twist,b.twist);
    for(const side of ['left','right']){vectorNear(a.feet[side].point,b.feet[side].point);vectorNear(a.arms[side].end,b.arms[side].end);}
  }
});

test('Projection preserves anatomy and changes view with camera yaw across all directions',()=>{
  assert.equal(DIRECTIONS.length,8);
  const p=[.23,.41,.85];
  for(let d=0;d<8;d++)for(let yaw=0;yaw<8;yaw++)for(const pitch of [10,46,89]){
    vectorNear(project(p,d,pitch,yaw),project(p,viewIndex(d,yaw),pitch,0));
    near(length(rotate(p,d*Math.PI/4)),length(p));
    assert.ok(project(p,d,pitch,yaw).every(Number.isFinite));
  }
});

test('Mid-clip appearance replacement preserves action, exact time, phase, pose, and other slots',()=>{
  for(const action of ['idle','walk','attack'])for(let i=0;i<50;i++){
    const s=createState();s.action=action;s.elapsed=i*.0173;const before=structuredClone(s),p=pose(s.action,s.elapsed);
    swapAppearance(s,'hat','crest');assert.deepEqual({...s,appearance:before.appearance},before);
    assert.deepEqual(pose(s.action,s.elapsed),p);assert.equal(s.appearance.coat,before.appearance.coat);
  }
});

test('Explicit part phase maps support fewer images without independent clocks',()=>{
  const map=[{at:0,image:'neutral'},{at:.28,image:'lean'},{at:.42,image:'neutral'}];
  assert.equal(mapPhase(.27,map),'neutral');assert.equal(mapPhase(.28,map),'lean');assert.equal(mapPhase(.419,map),'lean');assert.equal(mapPhase(.42,map),'neutral');assert.equal(mapPhase(1.28,map),'lean');
  assert.throws(()=>mapPhase(.2,[{at:.1,image:'broken'}]));
});

test('Eight held walk poses expose the quantization error instead of disguising it',()=>{
  const speed=STRIDE/PERIOD,hold=PERIOD/8;
  // Just before a pose update, root motion has advanced while its foot image has not.
  const sampled=pose('walk',0),live=pose('walk',hold-1e-6);
  const heldWorld=add(sampled.feet.left.point,live.root),correctWorld=add(live.feet.left.point,live.root);
  near(length(sub(heldWorld,correctWorld)),speed*(hold-1e-6));
  assert.ok(speed*hold>.08); // This study is NOT proof that eight held sprites look grounded.
});

test('Higher pose-rate targets reduce held-foot error while keeping the same action duration',()=>{
  let prior=Infinity;
  for(const mode of ['eight','30','60']){
    let maxError=0;
    for(let i=0;i<24000;i++){
      const t=i/24000*PERIOD,live=pose('walk',t),held=pose('walk',sampleTime('walk',t,mode));
      if(live.feet.left.contact&&held.feet.left.contact)maxError=Math.max(maxError,length(sub(live.feet.left.point,held.feet.left.point)));
    }
    assert.ok(maxError<prior,`${mode}: ${maxError} versus ${prior}`);prior=maxError;
    for(const action of ['idle','walk','attack']){
      const duration=clipDuration(action);
      near(sampleTime(action,duration,mode),duration);
      assert.ok(sampleTime(action,duration-.00001,mode)<duration);
    }
  }
  // A fixed 0.8s gait has 24 source poses at 30 FPS, 48 at 60 FPS.
  near(STRIDE/24*132,3.74);near(STRIDE/48*132,1.87);
});

test('High-rate attack timelines retain exact anticipation, contact and recovery landmarks',()=>{
  for(const mode of ['30','60']){
    const timeline=poseTimeline('attack',mode),duration=clipDuration('attack');
    for(const phase of [.28,.36,.42]){
      const time=phase*duration;assert.ok(timeline.includes(time));near(sampleTime('attack',time,mode),time);
    }
    for(let i=0;i<timeline.length;i++)assert.ok((timeline[i+1]??duration)-timeline[i]<=1/Number(mode)+1e-9);
  }
});
