/* Versioned raster assembly; MotionTemplate owns all body timing and poses. */
(function(scope){
'use strict';
const motion=scope.AstraeonMotionTemplate||(typeof require==='function'?require('./character-motion-template.js'):null);
if(!motion)throw Error('Load character-motion-template.js before character-assembly.js');
const {DIRECTIONS,LAYERS,validTransform,freeze,copy}=motion;
const MODES=Object.freeze(['BODY_SYNC','PHASE_SYNC','ANCHOR_HOLD','OWN_LOOP']);
const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const object=o=>o!==null&&typeof o==='object'&&!Array.isArray(o);
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const identity=()=>({x:0,y:0,rotation:0,scale:1});
const finiteTime=n=>Number.isFinite(n)&&n>=0;
function phaseIndex(entries,phase){let i=0;for(let n=1;n<entries.length;n++){if(entries[n].at<=phase)i=n;else break}return i}
function validateAppearancePack(pack,template){
 const errors=[],check=(ok,msg)=>{if(!ok)errors.push(msg)};
 if(!object(pack))return ['AppearancePack must be an object'];
 const t=template?.template||template;
 if(!t?.actions||!t.registration)return ['MotionTemplate must compile before appearance'];
 check(['1.0','1.1'].includes(pack.schemaVersion),'Unsupported appearance schema');
 check(typeof pack.packId==='string'&&/^[a-z][a-z0-9-]*$/.test(pack.packId),'Invalid appearance packId');
 check(Array.isArray(pack.compatibleMotionTemplates)&&pack.compatibleMotionTemplates.includes(t.motionTemplateId),'Appearance is incompatible with MotionTemplate');
 check(same(pack.registration,t.registration),'Appearance shared registration differs');
 check(pack.mirroring==='none','Appearance direction mirroring prohibited');
 check(['DEV_ONLY','REQUIRES_OWNER_VISUAL_REVIEW','APPROVED'].includes(pack.status),'Missing appearance review status');
 if(pack.status==='APPROVED')check(typeof pack.source?.approvedBy==='string'&&pack.source.approvedBy.length>0&&typeof pack.source?.reference==='string'&&pack.source.reference.length>0,'Approved appearance requires owner provenance');
 for(const field of ['actions','durations','durationMs','timing','anchors','motionTemplate'])check(!own(pack,field),'Appearance cannot override motion '+field);
 const slots=object(pack.slots)?pack.slots:{},parts=object(pack.parts)?pack.parts:{},atlases=object(pack.atlases)?pack.atlases:{},defaults=object(pack.defaultParts)?pack.defaultParts:{};
 const assigned=new Set();
 check(Object.keys(slots).length>0&&Object.values(slots).some(s=>s?.required&&s?.layers?.includes('Body')),'Required BodySpriteSet missing');
 if(pack.schemaVersion==='1.1'){
  const c=pack.bodyContract;
  check(slots.BodyWithOutfit?.required===true&&slots.Head?.required===true,'Production requires independent BodyWithOutfit and Head');
  check(!own(slots,'BodyCore')&&!own(slots,'Outfit'),'Production paper-doll body model prohibited');
  check(object(c)&&c.model==='BodyWithOutfit+Head'&&typeof c.contractId==='string','BodyWithOutfit contract missing');
  check(same(c?.registration,t.registration)&&same(c?.directions,DIRECTIONS),'BodyWithOutfit registration contract differs');
  check(same(c?.actions,Object.keys(t.actions)),'BodyWithOutfit action contract differs');
  check(same(c?.timeline,Object.fromEntries(Object.entries(t.actions).map(([a,v])=>[a,Object.fromEntries(DIRECTIONS.map(d=>[d,v.directions[d].frames.map(f=>f.durationMs)]))]))),'BodyWithOutfit frame timeline differs');
  check(['head','mainHand','offHand','back'].every(n=>c?.sockets?.includes(n)),'BodyWithOutfit semantic sockets missing');
  for(const [a,v]of Object.entries(t.actions))for(const d of DIRECTIONS){
   const entries=c?.anchorRegistration?.[a]?.[d];
   check(Array.isArray(entries)&&entries.length===v.directions[d].frames.length,'Missing BodyWithOutfit anchor registration '+a+'/'+d);
   for(const entry of entries||[])check(object(entry)&&['head','mainHand','offHand','back'].every(n=>validTransform(entry[n]))&&Object.keys(entry).every(n=>n!=='root'&&c.sockets.includes(n)&&validTransform(entry[n])),'Invalid BodyWithOutfit finite socket registration');
  }
  for(const part of Object.values(parts))if(part?.slot==='BodyWithOutfit')check(part.contractId===c?.contractId&&part.mode==='BODY_SYNC'&&part.space==='canvas','Incompatible BodyWithOutfit part');
 }
 for(const [slot,s] of Object.entries(slots)){
  if(!object(s)){check(false,'Invalid slot '+slot);continue}
  check(typeof s.required==='boolean'&&Array.isArray(s.layers)&&s.layers.length>0,'Invalid semantic slot '+slot);
  for(const layer of s.layers||[]){check(LAYERS.includes(layer)&&!assigned.has(layer),'Duplicate/unknown semantic layer '+layer);assigned.add(layer)}
  check(own(defaults,slot),'Missing default part '+slot);
  if(defaults[slot]===null)check(!s.required,'Required slot cannot be absent '+slot);
  else check(parts[defaults[slot]]?.slot===slot,'Invalid default part '+slot);
 }
 for(const slot of Object.keys(defaults))check(own(slots,slot),'Unknown default slot '+slot);
 for(const [id,a] of Object.entries(atlases)){
  check(object(a)&&typeof a.file==='string'&&a.file.startsWith('assets/characters/')&&!a.file.split('/').includes('..')&&!/[\\?#:]/.test(a.file),'Invalid atlas path '+id);
  check(Number.isSafeInteger(a?.width)&&a.width>0&&Number.isSafeInteger(a?.height)&&a.height>0,'Invalid atlas dimensions '+id);
 }
 for(const [id,part] of Object.entries(parts)){
  if(!object(part)){check(false,'Invalid part '+id);continue}
  const s=slots[part.slot],label=id;
  check(!!s,'Unknown part slot '+id);check(MODES.includes(part.mode),'Invalid layer sampling mode '+id);
  check(['canvas','attachment'].includes(part.space),'Invalid layer space '+id);
  if(part.space==='attachment'){
   if(part.parentLayer){
    const parent=Object.values(parts).find(p=>p!==part&&slots[p?.slot]?.layers?.includes(part.parentLayer));
    check(!!parent&&parent.slot==='Head'&&['Hair','Headgear'].includes(part.slot),'Invalid head-local parent '+id);
    check(typeof part.anchor==='string'&&Object.values(parent?.timelines||{}).every(dirs=>Object.values(dirs).every(seq=>(seq.frames||seq.phases||seq.views||[]).every(e=>e.layers[part.parentLayer]?.sockets?.[part.anchor]&&validTransform(e.layers[part.parentLayer].sockets[part.anchor])))),'Unavailable head-local socket '+id);
   }else check(typeof part.anchor==='string'&&Object.values(t.actions).every(a=>DIRECTIONS.every(d=>a.directions[d].frames.every(f=>own(f.anchors,part.anchor)))),'Unavailable attachment anchor '+id);
  }
  if(own(part,'defaultRegistration'))check(validTransform(part.defaultRegistration),'Invalid default registration '+id);
  if(own(part,'directionRegistration'))check(same(Object.keys(part.directionRegistration),DIRECTIONS)&&Object.values(part.directionRegistration).every(validTransform),'Invalid direction registration '+id);
  if(own(part,'actionPhaseRegistration'))for(const [a,entries]of Object.entries(part.actionPhaseRegistration)){
   check(own(t.actions,a)&&Array.isArray(entries)&&entries.length>0,'Invalid registration action '+id);
   for(const [i,e]of (Array.isArray(entries)?entries:[]).entries())check(Number.isFinite(e?.at)&&e.at>=0&&e.at<1&&(i===0?e.at===0:e.at>entries[i-1].at)&&validTransform(e?.transform),'Invalid registration phase '+id);
  }
  for(const field of ['durations','durationMs','timing','root','anchors','motionTemplate'])check(!own(part,field),'Part cannot override motion '+id+'/'+field);
  const ref=(entry)=>{
   if(!object(entry)||!object(entry.layers)){check(false,'Missing semantic samples '+label);return}
   check(Object.keys(entry.layers).length>0,'Empty part sample '+label);
   for(const [layer,f] of Object.entries(entry.layers)){
    check(s?.layers?.includes(layer),'Part supplies unrelated semantic layer '+label+'/'+layer);
    if(!object(f)){check(false,'Invalid raster sample '+label);continue}
    const a=atlases[f.atlasId],r=f.rect;
    check(!!a,'Missing atlas reference '+label+'/'+f.atlasId);
    check(Array.isArray(r)&&r.length===4&&r.every(Number.isSafeInteger)&&r[0]>=0&&r[1]>=0&&r[2]>0&&r[3]>0&&r[0]+r[2]<=a?.width&&r[1]+r[3]<=a?.height,'Raster exceeds atlas bounds '+label+'/'+layer);
    if(part.space==='canvas')check(r?.[2]===t.registration.canvas[0]&&r?.[3]===t.registration.canvas[1]&&!own(f,'localTransform'),'BODY canvas convention differs '+label);
    if(part.space==='attachment'){
     check(Array.isArray(f.pivot)&&f.pivot.length===2&&f.pivot.every(Number.isFinite),'Invalid attachment image pivot '+label);
     if(own(f,'localTransform'))check(validTransform(f.localTransform),'Invalid local transform '+label);
     if(pack.schemaVersion==='1.1'){
      check(Array.isArray(f.pivot)&&f.pivot[0]>=0&&f.pivot[1]>=0&&f.pivot[0]<=r?.[2]&&f.pivot[1]<=r?.[3],'Production pivot outside raster '+label);
      const trim=f.trim;
      check(object(trim)&&Array.isArray(trim.sourceSize)&&trim.sourceSize.length===2&&trim.sourceSize.every(Number.isSafeInteger)&&Array.isArray(trim.offset)&&trim.offset.length===2&&trim.offset.every(Number.isSafeInteger)&&trim.offset.every(n=>n>=0)&&trim.offset[0]+r?.[2]<=trim.sourceSize[0]&&trim.offset[1]+r?.[3]<=trim.sourceSize[1],'Missing/invalid explicit trim metadata '+label);
      if(part.slot==='Head')check(f.sockets&&['hair','headgear'].every(n=>validTransform(f.sockets[n])),'Head-local sockets required '+label);
     }
    }
    if(f.sockets)for(const socket of Object.values(f.sockets))check(validTransform(socket),'Invalid local socket '+label);
    for(const field of ['durationMs','timing','anchors','mirroring'])check(!own(f,field),'Raster cannot override motion '+label+'/'+field);
   }
  };
  const timelines=object(part.timelines)?part.timelines:{};
  check(Object.keys(timelines).length>0,'Missing part timeline '+id);
  for(const action of Object.keys(timelines))check(action==='*'||own(t.actions,action),'Unknown appearance action '+id+'/'+action);
  for(const action of Object.keys(t.actions)){
   const dirs=timelines[action]||timelines['*'];
   check(object(dirs)&&same(Object.keys(dirs),DIRECTIONS),'Missing authored direction samples '+id+'/'+action);
   for(const direction of DIRECTIONS){
    const seq=dirs?.[direction],body=t.actions[action].directions[direction];
    if(!object(seq)){check(false,'Missing part direction '+id+'/'+action+'/'+direction);continue}
    for(const field of ['durationMs','totalDurationMs','timing','anchors','root'])check(!own(seq,field),'Layer cannot override body timing/registration '+id);
    if(part.mode==='BODY_SYNC'){
     check(!own(timelines,'*'),'BODY_SYNC requires explicit action frames '+id);
     check(Array.isArray(seq.frames)&&seq.frames.length===body.frames.length,'BODY_SYNC frame count mismatch '+id+'/'+action+'/'+direction);
     (seq.frames||[]).forEach(ref);
    }else if(part.mode==='OWN_LOOP'){
     check(Array.isArray(seq.frames)&&seq.frames.length>0,'Missing independent loop '+id);
     for(const frame of seq.frames||[]){check(Number.isSafeInteger(frame?.durationMs)&&frame.durationMs>0,'Invalid independent cosmetic timing '+id);ref(frame)}
    }else{
     const entries=part.mode==='PHASE_SYNC'?seq.phases:seq.views;
     check(Array.isArray(entries)&&entries.length>0,'Missing held/phase samples '+id);
     for(const [i,e] of (entries||[]).entries()){
      check(Number.isFinite(e?.at)&&e.at>=0&&e.at<1&&(i===0?e.at===0:e.at>entries[i-1].at),'Invalid phase mapping '+id);
      ref(e);
     }
    }
   }
  }
 }
 if(pack.drawProfiles){
  for(const order of Object.values(pack.drawProfiles))check(motion.validOrder(order),'Invalid appearance draw profile');
  for(const [a,dirs]of Object.entries(pack.frameDrawProfiles||{})){
   check(own(t.actions,a)&&same(Object.keys(dirs),DIRECTIONS),'Invalid appearance draw direction mapping');
   for(const d of DIRECTIONS)check(Array.isArray(dirs[d])&&dirs[d].length===t.actions[a]?.directions[d].frames.length&&dirs[d].every(n=>own(pack.drawProfiles,n)),'Invalid appearance frame draw profile');
  }
 }
 return errors;
}
function composeTransform(a,b){
 const c=Math.cos(a.rotation),s=Math.sin(a.rotation);
 return {x:a.x+a.scale*(c*b.x-s*b.y),y:a.y+a.scale*(s*b.x+c*b.y),rotation:a.rotation+b.rotation,scale:a.scale*b.scale};
}
function compileAssembly(template,appearancePack){
 const compiledMotion=motion.compileMotionTemplate(template?.template||template);
 const errors=validateAppearancePack(appearancePack,compiledMotion);if(errors.length)throw Error(errors.join('\n'));
 const pack=freeze(copy(appearancePack));
 function selection(patch={}){
  if(!object(patch))throw Error('Invalid appearance selection');
  const result={...pack.defaultParts,...patch};
  for(const [slot,id] of Object.entries(result)){
   if(!own(pack.slots,slot))throw Error('Unknown appearance slot '+slot);
   if(id===null){if(pack.slots[slot].required)throw Error('Required layer cannot be absent '+slot)}
   else if(!own(pack.parts,id)||pack.parts[id].slot!==slot)throw Error('Incompatible appearance part '+id+' for '+slot);
  }
  return Object.freeze(result);
 }
 function sample(action,direction,elapsedMs=0,{frameIndex,appearance={},cosmeticTimeMs=elapsedMs}={}){
  if(!finiteTime(cosmeticTimeMs))throw Error('Invalid cosmetic clock');
  const body=compiledMotion.sample(action,direction,elapsedMs,{frameIndex}),chosen=selection(appearance),byLayer={};
  const corrections=pack.bodyContract?.anchorRegistration?.[action]?.[direction]?.[body.frameIndex]||{};
  const registeredAnchors=Object.fromEntries(Object.entries(body.frame.anchors).map(([n,a])=>[n,corrections[n]?composeTransform(a,corrections[n]):a]));
  for(const [slot,id] of Object.entries(chosen)){
   if(id===null)continue;
   const part=pack.parts[id],seq=(part.timelines[action]||part.timelines['*'])[direction];
   let entry,index;
   if(part.mode==='BODY_SYNC'){index=body.frameIndex;entry=seq.frames[index]}
   else if(part.mode==='OWN_LOOP'){
    let time=cosmeticTimeMs%seq.frames.reduce((n,f)=>n+f.durationMs,0);index=seq.frames.length-1;
    for(let i=0;i<seq.frames.length;i++){if(time<seq.frames[i].durationMs){index=i;break}time-=seq.frames[i].durationMs}entry=seq.frames[index];
   }else{
    const entries=part.mode==='PHASE_SYNC'?seq.phases:seq.views;
    // Explicit frame inspection uses the frame's start-time phase, independent
    // of the review clock. Playback uses continuous elapsed-time phase.
    const phase=frameIndex===undefined?body.phase:compiledMotion.template.actions[action].directions[direction].frames.slice(0,frameIndex).reduce((n,f)=>n+f.durationMs,0)/body.totalDurationMs;
    index=phaseIndex(entries,phase);entry=entries[index];
   }
   let registration=part.defaultRegistration||identity();
   registration=composeTransform(registration,part.directionRegistration?.[direction]||identity());
   const phases=part.actionPhaseRegistration?.[action];
   if(phases)registration=composeTransform(registration,phases[phaseIndex(phases,body.phase)].transform);
   for(const [layer,ref] of Object.entries(entry.layers))byLayer[layer]={...ref,slot,layer,partId:id,sampleIndex:index,mode:part.mode,space:part.space,parentLayer:part.parentLayer,anchor:part.anchor,registrationTransform:composeTransform(registration,ref.localTransform||identity())};
  }
  const resolving=new Set();
  function resolve(layer){
   const ref=byLayer[layer];if(ref.transform)return ref.transform;
   if(resolving.has(layer))throw Error('Cyclic attachment parent');resolving.add(layer);
   let anchor;
   if(ref.parentLayer){const parent=byLayer[ref.parentLayer];if(!parent?.sockets?.[ref.anchor])throw Error('Selected Head socket unavailable');anchor=composeTransform(resolve(ref.parentLayer),parent.sockets[ref.anchor])}
   else anchor=registeredAnchors[ref.anchor];
   ref.anchorTransform=anchor;
   ref.transform=ref.space==='attachment'?composeTransform(anchor,ref.registrationTransform):identity();
   resolving.delete(layer);return ref.transform;
  }
  Object.keys(byLayer).forEach(resolve);
  const profile=pack.frameDrawProfiles?.[action]?.[direction]?.[body.frameIndex],drawOrder=profile?pack.drawProfiles[profile]:body.drawOrder;
  return {...body,drawOrder,registeredAnchors,format:'ASTRAEON_ASSEMBLY_V1',packId:pack.packId,layers:drawOrder.filter(n=>own(byLayer,n)).map(n=>byLayer[n]),appearance:chosen};
 }
 return Object.freeze({motion:compiledMotion,pack,sample,selection});
}
function drawAssembly(ctx,sampled,images,{x=0,y=0,scale=1,visibleLayers}={}){
 if(!Number.isFinite(x)||!Number.isFinite(y)||!Number.isFinite(scale)||scale<=0)throw Error('Invalid assembly draw transform');
 const refs=sampled.layers.filter(f=>!visibleLayers||visibleLayers.includes(f.layer));
 const ready=refs.map(ref=>{const image=images[ref.atlasId];if(!image)throw Error('Atlas not loaded '+ref.atlasId);return {ref,image}});
 const root=sampled.registration.root,[w,h]=sampled.registration.canvas;
 ctx.save();
 try{
  ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
  for(const {ref,image} of ready){
   if(ref.space==='canvas')ctx.drawImage(image,...ref.rect,x-root.x*scale,y-root.y*scale,w*scale,h*scale);
   else{
    const t=ref.transform;
    ctx.save();try{ctx.translate(x+(t.x-root.x)*scale,y+(t.y-root.y)*scale);ctx.rotate(t.rotation);ctx.scale(t.scale*scale,t.scale*scale);ctx.drawImage(image,...ref.rect,-ref.pivot[0],-ref.pivot[1],ref.rect[2],ref.rect[3])}finally{ctx.restore()}
   }
  }
 }finally{ctx.restore()}
 return Object.fromEntries(Object.entries(sampled.registeredAnchors||sampled.frame.anchors).map(([name,t])=>[name,{x:x+(t.x-root.x)*scale,y:y+(t.y-root.y)*scale,rotation:t.rotation,scale:t.scale*scale}]));
}
function createController(compiled,{action=Object.keys(compiled.motion.template.actions)[0],direction='S',elapsedMs=0,cosmeticTimeMs=0,appearance={}}={}){
 let currentAction=action,currentDirection=direction,time=elapsedMs,cosmetic=cosmeticTimeMs,selected=compiled.selection(appearance);
 compiled.sample(action,direction,time,{appearance:selected,cosmeticTimeMs:cosmetic});
 return Object.freeze({
  sample:()=>compiled.sample(currentAction,currentDirection,time,{appearance:selected,cosmeticTimeMs:cosmetic}),
  advance:dt=>{if(!finiteTime(dt)||!Number.isFinite(time+dt)||!Number.isFinite(cosmetic+dt))throw Error('Invalid clock delta');time+=dt;cosmetic+=dt},
  setAppearance:patch=>{selected=compiled.selection({...selected,...patch})},
  setDirection:d=>{compiled.motion.sample(currentAction,d,time);currentDirection=d},
  setAction:a=>{compiled.motion.sample(a,currentDirection,0);currentAction=a;time=0},
  get elapsedMs(){return time},get cosmeticTimeMs(){return cosmetic},get appearance(){return selected}
 });
}
async function loadAssembly({motionUrl,appearanceUrl,allowDev=false,assetRoot=new URL('.',document.baseURI),appearance={}}){
 // Reuse the existing service-worker bypass for all explicit development input.
 const requestUrl=url=>{const u=new URL(url,document.baseURI);if(allowDev)u.searchParams.set('spriteDev','1');return u.href};
 const read=async url=>{const r=await fetch(requestUrl(url));if(!r.ok)throw Error('Cannot load assembly metadata '+url);return r.json()};
 const [template,pack]=await Promise.all([read(motionUrl),read(appearanceUrl)]);
 const compiled=compileAssembly(template,pack);
 if((template.status!=='APPROVED'||pack.status!=='APPROVED')&&!allowDev)throw Error('Unapproved assembly requires DEV_ONLY opt-in');
 const images={},pending={};let active=compiled.selection(appearance),revision=0;
 const imageFor=id=>images[id]?Promise.resolve():pending[id]??=(new Promise((resolve,reject)=>{
  const a=compiled.pack.atlases[id],im=new Image();
  im.onload=()=>{if(im.naturalWidth!==a.width||im.naturalHeight!==a.height){reject(Error('Atlas dimensions differ '+id));return}images[id]=im;resolve()};
  im.onerror=()=>reject(Error('Cannot load atlas '+id));im.src=requestUrl(new URL(a.file,assetRoot).href);
 })).catch(e=>{delete pending[id];throw e});
 async function preload(selected){
  const ids=new Set();
  for(const id of Object.values(selected)){if(id===null)continue;for(const dirs of Object.values(compiled.pack.parts[id].timelines))for(const seq of Object.values(dirs))for(const entry of seq.frames||seq.phases||seq.views)for(const ref of Object.values(entry.layers))ids.add(ref.atlasId)}
  await Promise.all([...ids].map(imageFor));
 }
 await preload(active);
 return Object.freeze({compiled,images,get appearance(){return active},sample:(action,direction,time,options={})=>compiled.sample(action,direction,time,{...options,appearance:active}),
  async setAppearance(patch){const next=compiled.selection({...active,...patch}),request=++revision;await preload(next);if(request!==revision)return false;active=next;return true}
 });
}
const api=Object.freeze({MODES,validateAppearancePack,compileAssembly,drawAssembly,createController,loadAssembly,composeTransform});
scope.AstraeonCharacterAssembly=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
