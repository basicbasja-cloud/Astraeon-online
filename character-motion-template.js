/* Numeric motion authority for painted 2D assembly. No appearance or gameplay. */
(function(scope){
'use strict';
const DIRECTIONS=Object.freeze(['S','SW','W','NW','N','NE','E','SE']);
const ANCHORS=Object.freeze(['root','head','mainHand','offHand','back','waist','footL','footR']);
const LAYERS=Object.freeze(['Shadow','GarmentBack','Body','HeadBase','HairBack','HairFront','HeadgearLower','HeadgearMiddle','HeadgearTop','MainHand','WeaponSlash','OffHand','GarmentFront','BackAccessory','CosmeticFX']);
const RO_PROOF_ACTIONS=Object.freeze(['Idle','Walk','BasicAttack']);
const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const object=o=>o!==null&&typeof o==='object'&&!Array.isArray(o);
const positive=n=>Number.isFinite(n)&&n>0;
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const named=s=>typeof s==='string'&&/^[A-Za-z][A-Za-z0-9_./-]*$/.test(s);
function freeze(o){if(o&&typeof o==='object'){Object.values(o).forEach(freeze);Object.freeze(o)}return o}
function copy(o){return JSON.parse(JSON.stringify(o))}
function validTransform(t){return object(t)&&Number.isFinite(t.x)&&Number.isFinite(t.y)&&Number.isFinite(t.rotation)&&positive(t.scale)&&Object.keys(t).every(k=>['x','y','rotation','scale'].includes(k))}
function validOrder(o){return Array.isArray(o)&&o.length===LAYERS.length&&new Set(o).size===o.length&&o.every(x=>LAYERS.includes(x))}
function sumDuration(frames){return frames.reduce((n,f)=>n+(f?.durationMs??NaN),0)}
function validateMotionTemplate(t){
 const errors=[],check=(ok,msg)=>{if(!ok)errors.push(msg)};
 if(!object(t))return ['MotionTemplate must be an object'];
 check(t.schemaVersion==='1.0','MotionTemplate schemaVersion must be 1.0');
 check(named(t.motionTemplateId),'Missing motionTemplateId');
 check(same(t.directions,DIRECTIONS),'Canonical direction order required');
 check(['DEV_ONLY','REQUIRES_OWNER_VISUAL_REVIEW','APPROVED'].includes(t.status),'MotionTemplate is not executable: reference data required');
 const synthetic=t.provenance?.kind==='SYNTHETIC_ENGINE_FIXTURE';
 check(synthetic||t.provenance?.kind==='RO1_DERIVED','Unknown motion provenance');
 if(synthetic)check(t.status==='DEV_ONLY','Synthetic fixture cannot be production motion');
 else check(/^[a-f0-9]{64}$/.test(t.provenance?.referenceManifestSHA256||''),'Missing reference manifest identity');
 const r=t.registration||{},canvas=r.canvas,root=r.root;
 check(Array.isArray(canvas)&&canvas.length===2&&canvas.every(n=>Number.isInteger(n)&&n>0),'Invalid shared canvas');
 check(validTransform(root)&&root.rotation===0&&root.scale===1,'Invalid explicit registered root');
 if(validTransform(root)&&Array.isArray(canvas))check(root.x>=0&&root.x<=canvas[0]&&root.y>=0&&root.y<=canvas[1],'Root outside canvas');
 check(r.mirroring==='none','Production direction mirroring prohibited');
 check(positive(r.referenceHeight)&&r.referenceHeight<=canvas?.[1],'Invalid referenceHeight');
 check(t.transformConvention==='canvas pixels; clockwise radians; uniform positive scale','Explicit transform convention required');
 const profiles=object(t.drawProfiles)?t.drawProfiles:{};
 check(Object.keys(profiles).length>0,'Missing draw profiles');
 for(const [id,order] of Object.entries(profiles))check(named(id)&&validOrder(order),'Invalid draw profile '+id);
 check(own(profiles,t.defaultDrawProfile),'Unknown default draw profile');
 const profile=(f,label)=>{
  if(own(f,'drawProfile'))check(own(profiles,f.drawProfile),'Unknown draw profile '+label);
  if(own(f,'drawOrder'))check(validOrder(f.drawOrder),'Invalid frame draw override '+label);
 };
 const actions=object(t.actions)?t.actions:{};
 check(Object.keys(actions).length>0,'No motion actions');
 const allIds=new Set();
 for(const [actionId,action] of Object.entries(actions)){
  check(named(actionId)&&object(action),'Invalid action '+actionId);if(!object(action))continue;
  if(!synthetic)check(RO_PROOF_ACTIONS.includes(actionId),'RO rescue action expansion requires owner approval');
  check(typeof action.loop==='boolean','Missing loop policy '+actionId);
  const dirs=object(action.directions)?action.directions:{};
  check(same(Object.keys(dirs),DIRECTIONS),'Missing or unordered action directions '+actionId);
  for(const direction of DIRECTIONS){
   const seq=dirs[direction],label=actionId+'/'+direction;
   if(!object(seq)){check(false,'Missing sequence '+label);continue}
   profile(seq,label);
   const frames=Array.isArray(seq.frames)?seq.frames:[],keys=Array.isArray(seq.referenceKeys)?seq.referenceKeys:[];
   check(frames.length>0&&keys.length>0,'Missing frame/key timeline '+label);
   check(Number.isSafeInteger(seq.totalDurationMs)&&seq.totalDurationMs>0,'Invalid total duration '+label);
   const validateFrame=(f,key=false)=>{
    if(!object(f)){check(false,'Invalid frame '+label);return}
    check(named(f.id),'Invalid frame ID '+label);
    check(Number.isSafeInteger(f.durationMs)&&f.durationMs>0,'Malformed frame timing '+f.id);
    check(['referenceKey','astraeonInbetween'].includes(f.role),'Invalid frame role '+f.id);
    check(validTransform(f.root)&&same(f.root,root),'Root drift or missing root '+f.id);
    const a=object(f.anchors)?f.anchors:{};
    check(ANCHORS.every(n=>own(a,n)),'Missing required anchors '+f.id);
    for(const [n,transform] of Object.entries(a))check(named(n)&&validTransform(transform),'Invalid attachment transform '+f.id+'/'+n);
    check(same(a.root,root),'Anchor root differs from registered root '+f.id);
    profile(f,f.id);
    check(Array.isArray(f.events)&&f.events.every(e=>object(e)&&named(e.name)&&e.authority==='presentation'),'Invalid visual events '+f.id);
    if(f.role==='referenceKey'){
     check(named(f.referencePhase),'Missing reference phase '+f.id);
     check(!own(f,'between')&&!own(f,'fraction'),'Reference key cannot be an in-between '+f.id);
     const intent=f.poseIntent||{};
     check(['bodyOrientation','limbPhase','footContact','attackPhase','silhouette'].every(k=>typeof intent[k]==='string'&&intent[k].length>0),'Missing key pose intent '+f.id);
     const s=f.source||{};
     if(synthetic)check(s.kind==='SYNTHETIC_ENGINE_FIXTURE','Fixture cannot claim RO keys '+f.id);
     else check(s.kind==='RO1_ACT'&&/^[a-f0-9]{64}$/.test(s.actSHA256||'')&&Number.isInteger(s.actionId)&&s.actionId>=0&&Number.isInteger(s.frameIndex)&&s.frameIndex>=0&&s.direction===direction,'Missing source-derived key identity '+f.id);
    }else{
     check(!key,'Reference catalog contains an in-between '+f.id);
     check(Array.isArray(f.between)&&f.between.length===2&&f.between.every(named)&&f.between[0]!==f.between[1],'Invalid in-between neighbors '+f.id);
     check(Number.isFinite(f.fraction)&&f.fraction>0&&f.fraction<1,'Invalid in-between fraction '+f.id);
     check(f.referencePhase===null&&!own(f,'source')&&!own(f,'poseIntent'),'In-between cannot claim a source pose '+f.id);
     check(Array.isArray(f.events)&&f.events.length===0,'In-between cannot introduce events '+f.id);
    }
   };
   keys.forEach(f=>validateFrame(f,true));frames.forEach(f=>validateFrame(f));
   for(const f of frames){if(!object(f))continue;check(!allIds.has(f.id),'Duplicate frame ID '+f.id);allIds.add(f.id)}
   const outputKeys=frames.filter(f=>f?.role==='referenceKey');
   check(same(outputKeys.map(f=>f.id),keys.map(f=>f?.id)),'Reference key sequence not preserved '+label);
   check(sumDuration(frames)===seq.totalDurationMs&&sumDuration(keys)===seq.totalDurationMs,'Total duration differs from source-key budget '+label);
   let keyTime=0;
   for(const key of keys){
    if(!object(key))continue;
    const i=frames.findIndex(f=>f?.id===key.id),out=frames[i];
    if(out){
     for(const field of ['role','referencePhase','root','anchors','poseIntent','source','events','drawProfile','drawOrder','bodyPose'])check(same(out[field],key[field]),'Reference key altered '+key.id+'/'+field);
     check(sumDuration(frames.slice(0,i))===keyTime,'Reference key timestamp altered '+key.id);
    }
    keyTime+=key.durationMs;
   }
   for(let i=0;i<frames.length;i++){
    const f=frames[i];if(f?.role!=='astraeonInbetween')continue;
    let left=i-1;while(left>=0&&frames[left]?.role!=='referenceKey')left--;
    let right=i+1;while(right<frames.length&&frames[right]?.role!=='referenceKey')right++;
    if(right===frames.length&&action.loop)right=frames.findIndex(k=>k?.role==='referenceKey');
    const l=frames[left],n=frames[right];
    check(left>=0&&right>=0&&right<frames.length&&same(f.between,[l?.id,n?.id]),'In-between must reference neighboring keys '+f.id);
    if(l&&Number.isFinite(f.fraction)){
     const key=keys.find(k=>k?.id===l.id);
     check(key&&sumDuration(frames.slice(left,i))===Math.round(key.durationMs*f.fraction),'In-between fraction/time mismatch '+f.id);
    }
   }
  }
 }
 return errors;
}
function interpolateTransform(a,b,f){
 if(!validTransform(a)||!validTransform(b)||!Number.isFinite(f)||f<=0||f>=1)throw Error('Invalid interpolation transform/fraction');
 let delta=((b.rotation-a.rotation+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI;
 return {x:a.x+(b.x-a.x)*f,y:a.y+(b.y-a.y)*f,rotation:a.rotation+delta*f,scale:a.scale+(b.scale-a.scale)*f};
}
// Explicit insertion schedule: no invented gait and no automatic frame doubling.
function smoothSequence(sequence,insertions={},loop=false){
 if(!object(sequence)||!Array.isArray(sequence.referenceKeys)||!sequence.referenceKeys.length||!object(insertions))throw Error('Invalid smoothing input');
 const keys=sequence.referenceKeys,frames=[];
 for(const id of Object.keys(insertions))if(!keys.some(k=>k.id===id))throw Error('Unknown insertion key '+id);
 for(let i=0;i<keys.length;i++){
  const left=keys[i],right=keys[i+1]||(loop?keys[0]:undefined),schedule=insertions[left.id]||[];
  if(!Array.isArray(schedule)||schedule.some((s,j)=>!object(s)||!named(s.id)||!Number.isFinite(s.at)||s.at<=0||s.at>=1||(j>0&&s.at<=schedule[j-1].at)))throw Error('Invalid ordered insertion schedule');
  if(schedule.length&&!right)throw Error('No neighboring recovery key');
  const times=[0,...schedule.map(s=>Math.round(left.durationMs*s.at)),left.durationMs];
  if(times.some((n,j)=>j>0&&n<=times[j-1]))throw Error('Insertion budget creates zero duration');
  frames.push({...copy(left),durationMs:times[1]-times[0]});
  for(let j=0;j<schedule.length;j++){
   const s=schedule[j],anchors=Object.fromEntries(Object.entries(left.anchors).map(([n,a])=>[n,interpolateTransform(a,right.anchors[n],s.at)]));
   // Root must remain exact rather than undergo floating-point interpolation.
   anchors.root=copy(left.root);
   const f={id:s.id,durationMs:times[j+2]-times[j+1],role:'astraeonInbetween',referencePhase:null,between:[left.id,right.id],fraction:s.at,root:copy(left.root),anchors,events:[]};
   if(own(left,'drawProfile'))f.drawProfile=left.drawProfile;
   if(own(left,'drawOrder'))f.drawOrder=copy(left.drawOrder);
   frames.push(f);
  }
 }
 return {...copy(sequence),frames};
}
function compileMotionTemplate(template){
 const errors=validateMotionTemplate(template);if(errors.length)throw Error(errors.join('\n'));
 const t=freeze(copy(template));
 function sequence(action,direction){if(!own(t.actions,action))throw Error('Unknown action '+action);if(!DIRECTIONS.includes(direction))throw Error('Unknown direction '+direction);return t.actions[action].directions[direction]}
 function sample(action,direction,elapsedMs=0,{frameIndex}={}){
  const seq=sequence(action,direction),a=t.actions[action];
  if(!Number.isFinite(elapsedMs)||elapsedMs<0)throw Error('Invalid animation time');
  let local=a.loop?elapsedMs%seq.totalDurationMs:Math.min(elapsedMs,seq.totalDurationMs),index=frameIndex,start=0;
  if(index===undefined){index=seq.frames.length-1;for(let i=0;i<seq.frames.length;i++){if(local<start+seq.frames[i].durationMs){index=i;break}start+=seq.frames[i].durationMs}}
  if(!Number.isInteger(index)||index<0||index>=seq.frames.length)throw Error('Invalid frame index');
  const frame=seq.frames[index],order=frame.drawOrder||t.drawProfiles[frame.drawProfile||seq.drawProfile||t.defaultDrawProfile];
  return {motionTemplateId:t.motionTemplateId,action,direction,frameIndex:index,elapsedMs,phase:Math.min(local/seq.totalDurationMs,1),totalDurationMs:seq.totalDurationMs,frame,drawOrder:order,registration:t.registration};
 }
 return Object.freeze({template:t,sample,duration:(action,direction)=>sequence(action,direction).totalDurationMs});
}
const api=Object.freeze({DIRECTIONS,ANCHORS,LAYERS,RO_PROOF_ACTIONS,validTransform,validOrder,validateMotionTemplate,compileMotionTemplate,smoothSequence,interpolateTransform,freeze,copy});
scope.AstraeonMotionTemplate=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
