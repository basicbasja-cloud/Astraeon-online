/* Authoring-only partial pose assembly. Reuses v1 motion and raster drawing. */
(function(scope){
'use strict';
const M=scope.AstraeonMotionTemplate||(typeof require==='function'?require('./character-motion-template.js'):null);
const A=scope.AstraeonCharacterAssembly||(typeof require==='function'?require('./character-assembly.js'):null);
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const REQUIRED=Object.freeze(['BodyCore','HeadBase','Face','Outfit','Hair']);
const SOURCE_LAYERS=Object.freeze(['BodyCore','HeadBase','Face','OutfitBack','OutfitFront','HairBack','HairFront','Weapon','OffHand','Headgear','CapeBack','CapeFront','BackAccessory','CosmeticFX']);

function validateSources(manifest,contract,template){
 const errors=[],check=(ok,msg)=>{if(!ok)errors.push(msg)};
 if(!manifest||!contract||!template)return ['Source manifest, pose contract and MotionTemplate required'];
 check(manifest.schemaVersion==='2.0-authoring','Unsupported source schema');
 check(manifest.status==='REQUIRES_OWNER_VISUAL_REVIEW','New source artwork requires owner review');
 check(manifest.ownerApproval==='PENDING','Authoring validator cannot grant owner approval');
 check(manifest.classId==='Swordsman'&&['male','female'].includes(manifest.bodyVariant),'Class and bodyVariant must be separate');
 check(manifest.classId===contract.classId&&manifest.bodyVariant===contract.bodyVariant,'Body variant differs from shared pose');
 check(same(manifest.directionOrder,M.DIRECTIONS),'Canonical direction order required');
 check(manifest.mirroring==='none','Runtime direction mirroring prohibited');
 check(same(manifest.registration,template.registration)&&same(contract.registration,template.registration),'Shared root/canvas/scale differs');
 check(manifest.motionTemplateId===template.motionTemplateId,'Wrong motion authority');
 check(manifest.poseId===contract.pose.poseId,'Source pose differs from shared authority');
 const pose=contract.pose,ref=template.actions[pose.action]?.directions[pose.direction]?.frames[pose.frameIndex];
 check(ref?.id===pose.poseId,'Shared pose does not identify an actual baseline frame');
 check(same(contract.pose.anchors.root,template.registration.root),'Calibrated root drift');
 for(const a of M.ANCHORS)check(M.validTransform(contract.pose.anchors[a]),'Missing/invalid shared socket '+a);
 check(manifest.authorship==='ISOLATED_COMPONENT_FROM_INCEPTION','Destructive character decomposition prohibited');
 check(manifest.authoritativeSources==='independent painted rasters','Preview/bake cannot become authoritative source');
 check(['VISUAL_REVIEW_PENDING','VISUAL_FAIL','DEV_VISUAL_PASS'].includes(manifest.gates?.south),'South state requires explicit visual review');
 check(Array.isArray(manifest.availablePoses)&&same(manifest.availablePoses,[pose.poseId]),'South proof cannot claim missing directions or actions');
 const slots=manifest.slots||{},parts=manifest.parts||{},defaults=manifest.defaultParts||{},assigned=new Set(),rawPaths=new Set();
 for(const slot of REQUIRED)check(slots[slot]?.required===true,'Missing independent required source slot '+slot);
 check(same(slots.Hair?.layers,['HairBack','HairFront']),'Hair requires independent front and back sources');
 for(const [slot,s] of Object.entries(slots)){
  check(typeof s.required==='boolean'&&Array.isArray(s.layers)&&s.layers.length>0,'Invalid source slot '+slot);
  for(const layer of s.layers||[]){check(SOURCE_LAYERS.includes(layer)&&!assigned.has(layer),'Duplicate/unknown source layer '+layer);assigned.add(layer)}
  check(own(defaults,slot),'Missing source default '+slot);
  const id=defaults[slot];
  if(id===null&&s.required)check(false,'Missing source coverage slot/'+slot);
  else check(id===null||parts[id]?.slot===slot,'Invalid source default '+slot);
 }
 check(Array.isArray(manifest.drawOrder)&&new Set(manifest.drawOrder).size===manifest.drawOrder.length&&manifest.drawOrder.length===assigned.size&&manifest.drawOrder.every(l=>assigned.has(l)),'Draw order must cover declared source layers exactly once');
 for(const [id,p] of Object.entries(parts)){
  const slot=slots[p.slot];check(!!slot,'Unknown source slot '+id);
  check(p.poseId===pose.poseId,'Part invented its own pose '+id);
  check(p.contractSHA256===manifest.contractSHA256,'Part guide identity differs '+id);
  check(p.authorship==='ISOLATED_COMPONENT_FROM_INCEPTION','Part was not independently authored '+id);
  for(const k of ['anchors','root','timing','durationMs','offset','equipmentLoadout'])check(!own(p,k),'Part overrides shared pose/gameplay '+id+'/'+k);
  check(Object.keys(p.layers||{}).every(l=>slot?.layers.includes(l)),'Part supplies unrelated source layers '+id);
  for(const l of slot?.layers||[])check(own(p.layers||{},l),'Missing source coverage '+id+'/'+l);
  for(const [layer,r] of Object.entries(p.layers||{})){
   check(typeof r.rawSource==='string'&&/^authoring\/characters\/(true-modular|appearance)\//.test(r.rawSource)&&!r.rawSource.split('/').includes('..'),'Invalid editable source path '+id);
   const sourceId=r.rawSource+JSON.stringify(r.sourceRegion||null);
   check(!rawPaths.has(sourceId),'One flattened raster cannot supply multiple independent parts '+id);rawPaths.add(sourceId);
   check(/^[a-f0-9]{64}$/.test(r.rawSHA256||'')&&/^[a-f0-9]{64}$/.test(r.rasterSHA256||''),'Source/raster identity missing '+id);
   check(typeof r.prompt==='string'&&/^[a-f0-9]{64}$/.test(r.promptSHA256||''),'Exact generation prompt missing '+id);
   check(['built-in ImageGen','built-in ImageGen (baseline reuse)'].includes(r.provider),'Missing first-party image provenance '+id);
   check(r.poseId===pose.poseId,'Layer pose mismatch '+id+'/'+layer);
   check(typeof r.file==='string'&&r.file.startsWith('assets/characters/swordsman-true-modular-v2/')&&!r.file.split('/').includes('..')&&!/[\\?#:]/.test(r.file),'Invalid normalized raster path '+id);
   check(same(r.canvas,template.registration.canvas),'Part canvas differs '+id);
  }
 }
 return errors;
}

function compileSources(manifest,contract,template,{diagnosticIncomplete=false}={}){
 const motion=M.compileMotionTemplate(template),errors=validateSources(manifest,contract,motion.template);
 const hardErrors=diagnosticIncomplete?errors.filter(e=>!e.startsWith('Missing source coverage ')):errors;
 if(hardErrors.length)throw Error(hardErrors.join('\n'));
 const src=M.freeze(M.copy(manifest)),pose=M.freeze(M.copy(contract.pose));
 function selection(patch={}){
  if(!patch||typeof patch!=='object'||Array.isArray(patch))throw Error('Invalid cosmetic selection');
  const selected={...src.defaultParts,...patch};
  for(const [slot,id] of Object.entries(selected)){
   if(!own(src.slots,slot))throw Error('Unknown cosmetic source slot '+slot);
   if(id===null){if(src.slots[slot].required&&!(diagnosticIncomplete&&src.defaultParts[slot]===null))throw Error('Required authoring source cannot be absent '+slot)}
   else if(src.parts[id]?.slot!==slot)throw Error('Incompatible source part '+id);
  }
  return Object.freeze(selected);
 }
 function sample(poseId=pose.poseId,{appearance={}}={}){
  if(!src.availablePoses.includes(poseId))throw Error('Pose has not been independently authored '+poseId);
  const base=motion.sample(pose.action,pose.direction,0,{frameIndex:pose.frameIndex}),chosen=selection(appearance),layers={};
  for(const [slot,id] of Object.entries(chosen))if(id!==null)for(const [layer,r] of Object.entries(src.parts[id].layers))
   layers[layer]={slot,partId:id,layer,space:'canvas',atlasId:r.file,rect:[0,0,...r.canvas],rasterSHA256:r.rasterSHA256,rawSHA256:r.rawSHA256};
  return {...base,format:'ASTRAEON_ASSEMBLY_V1',packId:src.packId,frame:{...base.frame,anchors:pose.anchors},appearance:chosen,
   layers:src.drawOrder.filter(l=>own(layers,l)).map(l=>layers[l]),authoringOnly:true,sourceCoverageComplete:errors.length===0,visualGate:src.gates.south};
 }
 return Object.freeze({manifest:src,pose,motion,selection,sample,draw:A.drawAssembly,sourceCoverageErrors:Object.freeze(errors)});
}
function assertSouthGatePassed(manifest,contract,template){
 const errors=validateSources(manifest,contract,template);
 if(errors.length)throw Error(errors.join('\n'));
 if(manifest.gates.south!=='DEV_VISUAL_PASS')throw Error('South visual gate has not passed; later production is blocked');
}
const api=Object.freeze({REQUIRED,SOURCE_LAYERS,validateSources,compileSources,assertSouthGatePassed});
scope.AstraeonSourceAuthoring=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
