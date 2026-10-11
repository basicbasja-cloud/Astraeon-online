// Original diagnostic study. No game character images or third-party code used.
export const DIRECTIONS = ['S','SE','E','NE','N','NW','W','SW'];
export const STRIDE = .68;
export const DUTY = .6;
export const PERIOD = .8;
export function clipDuration(action) {return action==='attack'?.72:PERIOD;}
const timelineCache=new Map();
export function poseTimeline(action,mode) {
  const key=action+':'+mode;
  if(timelineCache.has(key))return timelineCache.get(key);
  const duration=clipDuration(action),count=mode==='eight'?8:Math.ceil(duration*Number(mode));
  if(!(count>0))throw new Error('Invalid pose rate');
  const times=Array.from({length:count},(_,i)=>i*duration/count);
  // High-rate production candidates retain authored attack landmarks exactly.
  // The eight-pose diagnostic intentionally remains a uniform sparse sample.
  if(action==='attack'&&mode!=='eight')for(const phase of [.28,.36,.42])times.push(phase*duration);
  const timeline=Object.freeze([...new Set(times)].sort((a,b)=>a-b));
  timelineCache.set(key,timeline);return timeline;
}
export function sampleTime(action,elapsed,mode='continuous') {
  if(mode==='continuous')return elapsed;
  const duration=clipDuration(action),cycle=Math.floor(elapsed/duration),local=elapsed-cycle*duration;
  const timeline=poseTimeline(action,mode);let sample=0;
  for(const t of timeline)if(t<=local)sample=t;
  return cycle*duration+sample;
}
export const mod = (x,n=1) => {const r=x%n;return r<0?r+n:r;};
export const add = (a,b) => a.map((v,i)=>v+b[i]);
export const sub = (a,b) => a.map((v,i)=>v-b[i]);
export const mul = (a,k) => a.map(v=>v*k);
export const dot = (a,b) => a.reduce((s,v,i)=>s+v*b[i],0);
export const length = a => Math.hypot(...a);
export const unit = a => mul(a,1/length(a));
const mix = (a,b,t) => a+(b-a)*t;
const smooth = t => t*t*(3-2*t);
const hermite = (a,b,da,db,t) => (2*t**3-3*t*t+1)*a+(-2*t**3+3*t*t)*b+(t**3-2*t*t+t)*da+(t**3-t*t)*db;

// y is forward, z is up. During stance local foot velocity is -root velocity.
// Hermite endpoint velocities keep the swing continuous with stance.
export function footAt(cycle, side) {
  const p=mod(cycle+(side==='left'?0:.5));
  const x=side==='left'?-.15:.15;
  if(p<DUTY) return {point:[x,STRIDE*(DUTY/2-p),0],contact:true,phase:p};
  const u=(p-DUTY)/(1-DUTY);
  const y=hermite(-STRIDE*DUTY/2,STRIDE*DUTY/2,-STRIDE*(1-DUTY),-STRIDE*(1-DUTY),u);
  return {point:[x,y,.13*Math.sin(Math.PI*u)**2],contact:false,phase:p};
}

// Plane-constrained two-bone construction from triangle geometry.
// Unreachable targets are reported, never hidden by lengthening the limb.
export function solveLimb(start,target,l1,l2,preferred=[0,1,0]) {
  if(!(l1>0&&l2>0)) throw new Error('Positive bone lengths required');
  const delta=sub(target,start), raw=length(delta);
  const u=raw>1e-12?mul(delta,1/raw):[0,0,-1];
  const d=Math.max(Math.abs(l1-l2)+1e-9,Math.min(l1+l2-1e-9,raw));
  let bend=sub(preferred,mul(u,dot(preferred,u)));
  if(length(bend)<1e-9) {
    const axis=Math.abs(u[0])<.8?[1,0,0]:[0,1,0];
    bend=sub(axis,mul(u,dot(axis,u)));
  }
  bend=unit(bend);
  const a=(l1*l1-l2*l2+d*d)/(2*d);
  const h=Math.sqrt(Math.max(0,l1*l1-a*a));
  return {start,joint:add(start,add(mul(u,a),mul(bend,h))),end:add(start,mul(u,d)),reachable:Math.abs(d-raw)<1e-8};
}

export function rotate(p,angle) {
  const c=Math.cos(angle),s=Math.sin(angle);
  return [p[0]*c+p[1]*s,-p[0]*s+p[1]*c,p[2]];
}
export function project(p,direction=0,pitch=46,cameraYaw=0) {
  const q=rotate(p,(direction-cameraYaw)*Math.PI/4),a=pitch*Math.PI/180;
  return [q[0],q[1]*Math.sin(a)-q[2]*Math.cos(a),q[1]*Math.cos(a)+q[2]*Math.sin(a)];
}
export function viewIndex(worldDirection,cameraYaw) {return mod(Math.round(worldDirection-cameraYaw),8);}

// Explicit held-frame map: a part may have fewer source images than the body.
export function mapPhase(phase,keys) {
  if(!keys.length||keys[0].at!==0) throw new Error('Phase map must start at zero');
  for(let i=1;i<keys.length;i++) if(keys[i].at<=keys[i-1].at||keys[i].at>=1) throw new Error('Invalid phase map');
  let found=keys[0];
  for(const k of keys) if(mod(phase)>=k.at) found=k;
  return found.image;
}

export function pose(action,elapsed) {
  const cycle=elapsed/PERIOD,p=mod(cycle),a=mod(elapsed/.72);
  let hip=[.015*Math.sin(p*2*Math.PI),0,.66-.018*Math.cos(p*4*Math.PI)];
  let twist=.05*Math.sin(p*2*Math.PI),lean=.015,attackAngle=.1;
  if(action==='idle') {hip=[0,0,.65+.004*Math.sin(p*2*Math.PI)];twist=0;lean=0;}
  if(action==='attack') {
    // Deliberate anticipation, fast strike, recovery; both feet remain planted.
    const k=a<.28?smooth(a/.28):a<.42?smooth((a-.28)/.14):smooth((a-.42)/.58);
    attackAngle=a<.28?mix(.1,-1.0,k):a<.42?mix(-1.0,1.9,k):mix(1.9,.1,k);
    twist=a<.28?mix(0,-.28,k):a<.42?mix(-.28,.32,k):mix(.32,0,k);
    lean=.025*Math.sin(Math.PI*a)**2;
    hip=[.035*Math.sin(attackAngle),.025*Math.sin(Math.PI*a)**2,.64-.012*Math.sin(Math.PI*a)**2];
  }
  const feet={};const legs={};const arms={};
  for(const side of ['left','right']) {
    const sign=side==='left'?-1:1;
    feet[side]=action==='walk'?footAt(cycle,side):{point:[sign*.15,side==='right'&&action==='attack'?.07:0,0],contact:true,phase:0};
    const hipJoint=add(hip,[sign*.14,0,0]);
    legs[side]=solveLimb(hipJoint,add(feet[side].point,[0,0,.065]),.34,.34);
    const shoulder=add(hip,rotate([sign*.3,lean,.42],twist));
    const swing=action==='walk'?-sign*.17*Math.sin(p*2*Math.PI):0;
    const hand=action==='attack'&&side==='right'?
      add(hip,rotate([.36,.20*Math.sin(attackAngle),.18+.16*Math.cos(attackAngle)],twist)):
      add(hip,rotate([sign*.34,swing,.045],twist));
    arms[side]=solveLimb(shoulder,hand,.27,.27,[-sign*.3,-.4,-.5]);
  }
  const head=add(hip,[0,lean,.87]);
  const swordDirection=action==='attack'?rotate([0,Math.sin(attackAngle),Math.cos(attackAngle)],twist):[0,.16,.98];
  return {action,phase:action==='attack'?a:p,hip,head,twist,lean,feet,legs,arms,swordDirection,
    root:action==='walk'?[0,STRIDE*cycle,0]:[0,0,0]};
}

export function createState() {return {action:'walk',elapsed:0,speed:1,running:true,appearance:{hat:'cap',coat:'blue',weapon:'sword',shield:'round'}};}
export function swapAppearance(state,slot,item) {
  if(!Object.hasOwn(state.appearance,slot)) throw new Error('Unknown appearance slot');
  state.appearance={...state.appearance,[slot]:item};
}
