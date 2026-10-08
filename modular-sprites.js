/* Synchronized painted 2D character parts. Classic-script API, also usable by Node tooling. */
(function (scope) {
'use strict';
const DIRECTIONS = Object.freeze(['S','SW','W','NW','N','NE','E','SE']);
const REQUIRED_LAYERS = Object.freeze(['BaseBody','Hair','Outfit','Weapon','Headgear','BackAccessory']);
const OPTIONAL_LAYERS = Object.freeze(['Face','Offhand','Cape','CosmeticFX','Aura','ShoulderAccessory']);
const SOCKETS = Object.freeze(['root','head','hand_R','hand_L','back','waist']);
const SHARED_CLIPS = Object.freeze(['Idle','Walk','Run','BasicAttack','SkillAction','Hit','Death']);
const CLASS_CLIPS = Object.freeze({Swordsman:['Guard','Dash'],Mage:['CastChannel','Blink']});
const slug = /^[a-z][a-z0-9-]*$/;
const own = (o,k) => Object.prototype.hasOwnProperty.call(o,k);
const same = (a,b) => JSON.stringify(a) === JSON.stringify(b);
const positive = n => Number.isFinite(n) && n > 0;
const frameId = (characterId,partId,animationId,direction,index) => `${characterId}_${partId}_${animationId}_${direction}_${String(index).padStart(2,'0')}`;
const poseKey = (animationId,direction,index) => `${animationId}/${direction}/${index}`;
function validateDefinition(d) {
 const errors=[];
 const check=(ok,message)=>{if(!ok)errors.push(message)};
 if(!d || typeof d!=='object' || Array.isArray(d)) return ['Definition must be an object'];
 check(d.version==='0.1','Unsupported sprite version');
 check(slug.test(d.characterId||''),'Invalid characterId');
 check(own(CLASS_CLIPS,d.classId),'Unsupported classId');
 // Body identity belongs to presentation, never to gameplay class/equipment.
 if(own(d,'bodyVariant'))check(typeof d.bodyVariant==='string'&&slug.test(d.bodyVariant),'Invalid bodyVariant');
 check(same(d.directions,DIRECTIONS),'Direction order must be '+DIRECTIONS.join(','));
 const c=d.canvas||{}, w=c.frameWidth,h=c.frameHeight;
 check(Number.isInteger(w)&&positive(w)&&Number.isInteger(h)&&positive(h),'Invalid canvas dimensions');
 const point=p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite)&&p[0]>=0&&p[0]<=w&&p[1]>=0&&p[1]<=h;
 check(point([c.rootAnchorX,c.rootAnchorY]),'Invalid ground root anchor');
 check(positive(c.referenceHeight)&&c.referenceHeight<=h,'Invalid referenceHeight');
 check(d.mirroring==='none','Runtime mirroring is prohibited');
 check(['DEV_ONLY','APPROVED'].includes(d.source?.status),'Missing source approval status');
 if(d.source?.status==='APPROVED')check(typeof d.source.reference==='string'&&d.source.reference.length>0&&typeof d.source.approvedBy==='string'&&d.source.approvedBy.length>0,'Approved source needs reference and approvedBy');
 if(d.source?.status==='DEV_ONLY')for(const tag of ['DEV_ONLY','PLACEHOLDER','NOT_FINAL_ART'])check(d.tags?.includes(tag),'Missing placeholder tag '+tag);
 check(typeof d.source?.camera==='string'&&d.source.camera.length>0,'Missing source camera');
 check(['right','left'].includes(d.source?.handedness),'Invalid handedness');
 const slots=d.slots||{}, defaults=d.defaultParts||{}, parts=d.parts||{}, atlases=d.atlases||{}, clips=d.clips||{};
 check(Object.keys(parts).length>0,'Missing parts');
 check(Object.keys(atlases).length>0,'Missing atlases');
 for(const layer of REQUIRED_LAYERS)check(Object.values(slots).includes(layer),'Missing required layer '+layer);
 for(const [slot,layer] of Object.entries(slots)){
  check([...REQUIRED_LAYERS,...OPTIONAL_LAYERS].includes(layer),'Invalid layer '+slot);
  check(own(defaults,slot),'Missing default part for '+slot);
  const part=parts[defaults[slot]];check(part?.slot===slot,'Invalid default part for '+slot);
 }
 for(const slot of Object.keys(defaults))check(own(slots,slot),'Unknown default slot '+slot);
 const order=(list,label)=>check(Array.isArray(list)&&list.length===Object.keys(slots).length&&new Set(list).size===list.length&&list.every(s=>own(slots,s)),'Invalid draw order '+label);
 order(d.drawOrder,'default');
 for(const [id,a] of Object.entries(atlases)){
  check(slug.test(id),'Invalid atlas id '+id);
  check(typeof a.file==='string'&&a.file.startsWith('assets/characters/')&&!a.file.split('/').includes('..')&&!/[\\?#]/.test(a.file),'Invalid atlas path '+id);
  check(Number.isInteger(a.width)&&positive(a.width)&&Number.isInteger(a.height)&&positive(a.height),'Invalid atlas dimensions '+id);
 }
 for(const id of [...SHARED_CLIPS,...(CLASS_CLIPS[d.classId]||[])])check(own(clips,id),'Missing clip '+id);
 const poses=[];
 for(const [animationId,clip] of Object.entries(clips)){
  check(/^[A-Z][A-Za-z0-9]*$/.test(animationId),'Invalid animationId '+animationId);
  check(typeof clip.loop==='boolean','Missing loop policy '+animationId);
  check(Array.isArray(clip.durations)&&clip.durations.length>0&&clip.durations.every(positive),'Invalid timing '+animationId);
  check(same(Object.keys(clip.directions||{}),DIRECTIONS),'Missing or unordered clip directions '+animationId);
  for(const direction of DIRECTIONS){
   const sequence=clip.directions?.[direction];
   check(sequence?.frames?.length===clip.durations?.length,'Missing frames '+animationId+'/'+direction);
   if(sequence?.drawOrder)order(sequence.drawOrder,animationId+'/'+direction);
   for(const [index,frame] of (sequence?.frames||[]).entries()){
    const label=poseKey(animationId,direction,index);
    check(frame.frameIndex===index,'Non-contiguous frame index '+label);
    // Timing and canvas belong to the shared clip; a layer cannot override them.
    check(!own(frame,'duration')&&!own(frame,'canvas'),'Per-frame timing/canvas override '+label);
    const sockets=frame.sockets||{};
    for(const socket of SOCKETS)check(own(sockets,socket),'Missing socket '+socket+' '+label);
    for(const [socket,p] of Object.entries(sockets))check(/^[a-z][a-zA-Z0-9_]*$/.test(socket)&&point(p),'Invalid socket '+socket+' '+label);
    check(same(sockets.root,[c.rootAnchorX,c.rootAnchorY]),'Root drift '+label);
    if(frame.drawOrder)order(frame.drawOrder,label);
    poses.push({animationId,direction,index});
   }
  }
 }
 const ids=new Set(),cosmetics=new Set();
 for(const [partId,part] of Object.entries(parts)){
  check(slug.test(partId),'Invalid partId '+partId);
  check(own(slots,part.slot),'Unknown part slot '+partId);
  if(own(part,'cosmeticId')){
   check(typeof part.cosmeticId==='string'&&slug.test(part.cosmeticId),'Invalid cosmeticId '+partId);
   const key=part.slot+'/'+part.cosmeticId;
   check(!cosmetics.has(key),'Ambiguous cosmetic '+key);cosmetics.add(key);
  }
  check(!own(part,'durations')&&!own(part,'canvas')&&!own(part,'rootAnchor'),'Layer timing/canvas/anchor override '+partId);
  const frames=part.frames||{};
  check(Object.keys(frames).length===poses.length,'Layer frame count mismatch '+partId);
  for(const {animationId,direction,index} of poses){
   const id=frameId(d.characterId,partId,animationId,direction,index),ref=frames[id],atlas=atlases[ref?.atlasId];
   check(!ids.has(id),'Duplicate frame ID '+id);ids.add(id);
   check(!!ref,'Missing layer frame '+id);if(!ref)continue;
   check(!own(ref,'duration')&&!own(ref,'frameDuration')&&!own(ref,'sockets'),'Layer timing/socket override '+id);
   check(!!atlas,'Missing atlas reference '+id);
   const r=ref.rect;
   check(Array.isArray(r)&&r.length===4&&r.every(Number.isInteger)&&r[0]>=0&&r[1]>=0&&r[2]===w&&r[3]===h&&r[0]+r[2]<=atlas?.width&&r[1]+r[3]<=atlas?.height,'Invalid canvas/atlas rect '+id);
  }
  for(const id of Object.keys(frames))check(ids.has(id)&&id.startsWith(d.characterId+'_'+partId+'_'),'Unexpected/naming-invalid frame '+id);
 }
 return errors;
}
function compile(definition) {
 const errors=validateDefinition(definition);if(errors.length)throw Error(errors.join('\n'));
 // Freeze a private copy so edits cannot invalidate a compiled production contract.
 const d=JSON.parse(JSON.stringify(definition));
 function freeze(o){if(o&&typeof o==='object'){Object.values(o).forEach(freeze);Object.freeze(o)}return o}freeze(d);
 const totals=Object.fromEntries(Object.entries(d.clips).map(([id,c])=>[id,c.durations.reduce((a,b)=>a+b,0)]));
 function sample(animationId,direction,elapsedMs=0,{frameIndex,appearance={}}={}) {
  const clip=d.clips[animationId];if(!clip)throw Error('Unknown animation '+animationId);
  if(!DIRECTIONS.includes(direction))throw Error('Unknown direction '+direction);
  if(!Number.isFinite(elapsedMs)||elapsedMs<0)throw Error('Invalid elapsedMs');
  if(!appearance||typeof appearance!=='object'||Array.isArray(appearance))throw Error('Invalid appearance');
  for(const slot of Object.keys(appearance))if(!own(d.slots,slot))throw Error('Unknown appearance slot '+slot);
  let index=frameIndex;
  if(index===undefined){
   let time=clip.loop?elapsedMs%totals[animationId]:Math.min(elapsedMs,totals[animationId]-Number.EPSILON);
   index=clip.durations.length-1;for(let i=0;i<clip.durations.length;i++){if(time<clip.durations[i]){index=i;break}time-=clip.durations[i]}
  }
  if(!Number.isInteger(index)||index<0||index>=clip.durations.length)throw Error('Invalid frame index');
  const sequence=clip.directions[direction],frame=sequence.frames[index],order=frame.drawOrder||sequence.drawOrder||d.drawOrder;
  const layers=[];
  for(const slot of order){
   const partId=own(appearance,slot)?appearance[slot]:d.defaultParts[slot];
   if(partId===null){if(REQUIRED_LAYERS.includes(d.slots[slot]))throw Error('Cannot remove required layer '+slot);continue}
   const part=d.parts[partId];if(!part||part.slot!==slot)throw Error('Incompatible part '+partId+' for '+slot);
   const id=frameId(d.characterId,partId,animationId,direction,index),ref=part.frames[id];
   layers.push({slot,layer:d.slots[slot],partId,frameId:id,...ref});
  }
  return {characterId:d.characterId,classId:d.classId,bodyVariant:d.bodyVariant||'default',animationId,direction,frameIndex:index,duration:clip.durations[index],canvas:d.canvas,sockets:frame.sockets,layers};
 }
 return Object.freeze({definition:d,sample,duration:animationId=>totals[animationId]});
}
// The legacy tables are clockwise. Project headings directly to the new named order.
function directionFromHeading(angle,project) {
 if(!Number.isFinite(angle)||typeof project!=='function')throw Error('Heading needs a projection');
 const p=project(Math.cos(angle),Math.sin(angle));
 const row=((Math.round((Math.atan2(p.y,p.x)-Math.PI/2)/(Math.PI/4))%8)+8)%8;
 return DIRECTIONS[row];
}
function draw(ctx,sampled,images,{x=0,y=0,scale=1}={}) {
 if(!positive(scale))throw Error('Invalid sprite scale');
 // Resolve every image first: missing parts never leave a partly painted character.
 const layers=sampled.layers.map(ref=>{const image=images[ref.atlasId];if(!image)throw Error('Atlas not loaded '+ref.atlasId);return {ref,image}});
 const c=sampled.canvas,left=x-c.rootAnchorX*scale,top=y-c.rootAnchorY*scale;
 ctx.save();try{ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';for(const {ref,image} of layers)ctx.drawImage(image,...ref.rect,left,top,c.frameWidth*scale,c.frameHeight*scale)}finally{ctx.restore()}
 return Object.fromEntries(Object.entries(sampled.sockets).map(([id,p])=>[id,{x:left+p[0]*scale,y:top+p[1]*scale}]));
}
function resolveCosmetics(definition,cosmeticLoadout={}) {
 if(!cosmeticLoadout||typeof cosmeticLoadout!=='object'||Array.isArray(cosmeticLoadout))throw Error('Invalid cosmeticLoadout');
 const appearance={};
 for(const [slot,cosmeticId] of Object.entries(cosmeticLoadout)){
  if(!own(definition.slots,slot))throw Error('Unknown cosmetic slot '+slot);
  const candidates=Object.entries(definition.parts).filter(([,part])=>part.slot===slot&&part.cosmeticId===cosmeticId);
  if(candidates.length!==1)throw Error('Unavailable cosmetic '+cosmeticId+' for '+slot+' / '+(definition.bodyVariant||'default'));
  appearance[slot]=candidates[0][0];
 }
 return appearance;
}
async function load(url,{allowDev=false,animationIds=['Idle'],bodyVariant,appearance={},cosmeticLoadout={}}={}) {
 const response=await fetch(url);if(!response.ok)throw Error('Cannot load sprite definition '+url);
 const compiled=compile(await response.json());
 if(compiled.definition.source.status==='DEV_ONLY'&&!allowDev)throw Error('DEV_ONLY sprites require explicit development opt-in');
 if(bodyVariant!==undefined&&bodyVariant!==(compiled.definition.bodyVariant||'default'))throw Error('Sprite bodyVariant differs from requested presentation');
 function selection(parts,cosmetics){
  if(!parts||typeof parts!=='object'||Array.isArray(parts))throw Error('Invalid appearance');
  const result={...parts,...resolveCosmetics(compiled.definition,cosmetics)};
  compiled.sample('Idle','S',0,{appearance:result});
  return Object.freeze(result);
 }
 let active=selection(appearance,cosmeticLoadout),revision=0;
 const activeClips=new Set();
 const images={},pending={};
 // Atlas paths are repository-relative; metadata lives in assets/characters/<character>/.
 const root=new URL('../../../',new URL(url,document.baseURI));
 function atlasImage(id){
  if(images[id])return Promise.resolve();
  return pending[id]??=new Promise((resolve,reject)=>{
   const atlas=compiled.definition.atlases[id],image=new Image();
   image.onload=()=>{if(image.naturalWidth!==atlas.width||image.naturalHeight!==atlas.height){reject(Error('Atlas size mismatch '+id));return}images[id]=image;resolve()};
   image.onerror=()=>reject(Error('Cannot load atlas '+id));image.src=new URL(atlas.file,root).href;
  }).catch(error=>{delete pending[id];throw error});
 }
 async function preload(animationId,selected=active){
  const clip=compiled.definition.clips[animationId];if(!clip)throw Error('Unknown animation '+animationId);
  const ids=new Set();
  for(const direction of DIRECTIONS)for(let i=0;i<clip.durations.length;i++)for(const layer of compiled.sample(animationId,direction,0,{frameIndex:i,appearance:selected}).layers)ids.add(layer.atlasId);
  await Promise.all([...ids].map(atlasImage));
 }
 async function ensure(animationId){
  activeClips.add(animationId);
  let selected;do{selected=active;await preload(animationId,selected)}while(selected!==active);
 }
 async function setAppearance(parts={}, {cosmeticLoadout={},animationIds=[...activeClips]}={}){
  const next=selection(parts,cosmeticLoadout),request=++revision;
  const ready=new Set();
  // Include clips requested while this appearance was preloading.
  for(;;){const required=new Set([...animationIds,...activeClips]);await Promise.all([...required].filter(id=>!ready.has(id)).map(async id=>{await preload(id,next);ready.add(id)}));if([...activeClips].every(id=>ready.has(id)))break}
  // Failed or superseded requests retain the previous complete appearance.
  if(request!==revision)return false;
  active=next;animationIds.forEach(id=>activeClips.add(id));return true;
 }
 await Promise.all(animationIds.map(ensure));
 return Object.freeze({compiled,images,allowDev,ensure,setAppearance,get appearance(){return active}});
}
const STATE_CLIPS=Object.freeze({idle:'Idle',turn:'Idle',stop:'Idle',start:'Walk',walk:'Walk',run:'Run',sprint:'Run',attack:'BasicAttack',cast:'SkillAction',hit:'Hit',death:'Death',guard:'Guard',dodge:'Dash',dash:'Dash',channel:'CastChannel',blink:'Blink'});
function drawHumanoid(ctx,iso,t,{modular,scale=1,state=t.state,progress=0,archetype='warrior'}={}) {
 const {compiled,images}=modular,definition=compiled.definition;
 if(definition.source.status==='DEV_ONLY'&&!modular.allowDev)throw Error('Development sprites are not approved runtime art');
 if(({warrior:'Swordsman',mage:'Mage'})[archetype]!==definition.classId)throw Error('Sprite class differs from gameplay archetype');
 let animationId=modular.animationId||STATE_CLIPS[state];
 if(state==='dodge'&&definition.classId==='Mage')animationId='Blink';
 if(!definition.clips[animationId])throw Error('Missing runtime clip '+animationId);
 const view=scope.AstraeonView,walking=['start','walk','run','sprint'].includes(state)&&t.speed>.02;
 const heading=walking&&t.mode==='movement'&&Math.hypot(t.velocity?.x||0,t.velocity?.y||0)>.02?Math.atan2(t.velocity.y,t.velocity.x):t.rotation;
 const direction=modular.direction||directionFromHeading(heading,view.project);
 const duration=compiled.duration(animationId),movingClock=['Walk','Run'].includes(animationId)&&Number.isFinite(t.gait);
 const elapsedMs=modular.elapsedMs??(movingClock?((t.gait%1+1)%1)*duration:definition.clips[animationId].loop?(t.stateTime||0)*1000:Math.max(0,Math.min(1,progress))*duration);
 const sampled=compiled.sample(animationId,direction,elapsedMs,{appearance:modular.appearance||{}});
 if(scope.AstraeonSpatialView?.assemblingActor)scope.AstraeonSpatialView.sampledPose={clip:'modular/'+definition.characterId,row:DIRECTIONS.indexOf(direction),column:sampled.frameIndex,bounds:[0,0,definition.canvas.frameWidth,definition.canvas.frameHeight]};
 const foot=iso(t.position.x,t.position.y,((t.position.z||0)+(t.flight||0))*35);
 const unit=70*((view.scale.humanoid||103)/76)*scale/definition.canvas.referenceHeight*(view.zoom||1);
 const spriteSockets=draw(ctx,sampled,images,{x:foot.x,y:foot.y,scale:unit});
 // Keep the existing world-space presentation socket aliases. Canonical pose
 // sockets are returned separately in rendered pixels, never fed into combat.
 const p=t.position,f=t.facingDirection;
 return {RightHand:[p.x+f.y*.22,p.y-f.x*.22,p.z+1.2],LeftHand:[p.x-f.y*.22,p.y+f.x*.22,p.z+1.2],Back:[p.x-f.x*.2,p.y-f.y*.2,p.z+1.2],Hip:[p.x,p.y,p.z+.8],spriteSockets};
}
const api={DIRECTIONS,REQUIRED_LAYERS,OPTIONAL_LAYERS,SOCKETS,SHARED_CLIPS,CLASS_CLIPS,frameId,validateDefinition,compile,resolveCosmetics,directionFromHeading,draw,load,drawHumanoid,STATE_CLIPS};
scope.AstraeonModularSprites=Object.freeze(api);
if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
