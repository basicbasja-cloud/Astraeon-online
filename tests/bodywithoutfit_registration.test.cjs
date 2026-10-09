'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto');
const A=require('../character-assembly.js'),M=require('../character-motion-template.js');
const read=p=>JSON.parse(fs.readFileSync(p)),clone=structuredClone;
const t=read('authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json'),p=read('authoring/characters/appearance/swordsman-bodywithoutfit/appearance-pack.json'),c=A.compileAssembly(t,p);
const first=p=>p.parts['swordsman-head'].timelines.Idle.S.frames[0].layers.HeadBase;
test('production contract requires dressed bodies and independent Head with the shared canvas/timeline',()=>{assert.deepEqual(A.validateAppearancePack(p,t),[]);assert.equal(p.bodyContract.model,'BodyWithOutfit+Head');assert.ok(p.slots.BodyWithOutfit.required&&p.slots.Head.required);assert.ok(!p.slots.BodyCore&&!p.slots.Outfit);assert.deepEqual(p.bodyContract.directions,M.DIRECTIONS);assert.deepEqual(p.bodyContract.actions,['Idle','Walk','BasicAttack'])});
for(const [action,v]of Object.entries(t.actions))test(action+' renders every frame in all eight directions with finite deterministic registered anchors/pivots',()=>{
 for(const d of M.DIRECTIONS)for(let frameIndex=0;frameIndex<v.directions[d].frames.length;frameIndex++){
  const s=c.sample(action,d,42,{frameIndex});assert.deepEqual(s,c.sample(action,d,42,{frameIndex}));assert.deepEqual(s.frame,t.actions[action].directions[d].frames[frameIndex]);
  for(const a of Object.values(s.registeredAnchors))assert.ok(M.validTransform(a));
  for(const r of s.layers){assert.ok(M.validTransform(r.transform));if(r.space==='attachment')assert.ok(r.pivot.every(Number.isFinite)&&r.trim)}
  for(const [layer,socket]of [['HeadBase','head'],['MainHand','mainHand'],['OffHand','offHand']]){const ref=s.layers.find(r=>r.layer===layer);if(ref){assert.deepEqual(ref.transform,s.registeredAnchors[socket])}}
 }
});
test('BodyWithOutfit A/B preserves action, direction, frame, animation and cosmetic clocks through every pose',()=>{
 for(const [action,v]of Object.entries(t.actions))for(const d of M.DIRECTIONS)for(let i=0,time=0;i<v.directions[d].frames.length;time+=v.directions[d].frames[i++].durationMs){
  const ctl=A.createController(c,{action,direction:d,elapsedMs:time+1,cosmeticTimeMs:900,appearance:{OffHand:'offhand',Headgear:'headgear'}}),before=ctl.sample();
  ctl.setAppearance({BodyWithOutfit:'swordsman-body-royal-proof'});const after=ctl.sample();
  assert.equal(after.action,action);assert.equal(after.direction,d);assert.equal(after.frameIndex,before.frameIndex);assert.equal(ctl.elapsedMs,time+1);assert.equal(ctl.cosmeticTimeMs,900);assert.deepEqual(after.frame,before.frame);assert.deepEqual(after.registeredAnchors,before.registeredAnchors);
  assert.deepEqual(after.layers.filter(r=>r.slot!=='BodyWithOutfit'),before.layers.filter(r=>r.slot!=='BodyWithOutfit'));assert.notEqual(after.appearance.BodyWithOutfit,before.appearance.BodyWithOutfit);
 }
});
for(const slot of ['Head','Hair','MainHand','OffHand','Headgear','Garment'])test('costume replacement preserves independent '+slot,()=>{
 const ctl=A.createController(c,{action:'Walk',direction:'SW',elapsedMs:277,appearance:{OffHand:'offhand',Headgear:'headgear'}}),before=ctl.sample();ctl.setAppearance({BodyWithOutfit:'swordsman-body-royal-proof'});const after=ctl.sample();assert.equal(after.appearance[slot],before.appearance[slot]);assert.deepEqual(after.layers.filter(r=>r.slot===slot),before.layers.filter(r=>r.slot===slot));
});
test('Hair A/B and Headgear inherit the selected Head local sockets on all 328 poses',()=>{
 for(const [a,v]of Object.entries(t.actions))for(const d of M.DIRECTIONS)for(let frameIndex=0;frameIndex<v.directions[d].frames.length;frameIndex++)for(const Hair of ['hair-a','hair-b']){
  const s=c.sample(a,d,0,{frameIndex,appearance:{Hair,Headgear:'headgear'}}),head=s.layers.find(r=>r.slot==='Head');
  for(const slot of ['Hair','Headgear']){const r=s.layers.find(r=>r.slot===slot);assert.equal(r.parentLayer,'HeadBase');assert.deepEqual(r.anchorTransform,A.composeTransform(head.transform,head.sockets[r.anchor]))}
 }
});
test('Weapon A/B retain the same explicit grip transform while replacing only sword source pixels',()=>{
 for(const [a,v]of Object.entries(t.actions))for(const d of M.DIRECTIONS)for(let frameIndex=0;frameIndex<v.directions[d].frames.length;frameIndex++){
  const x=c.sample(a,d,0,{frameIndex}),y=c.sample(a,d,0,{frameIndex,appearance:{MainHand:'weapon-b'}});assert.deepEqual(x.layers.filter(r=>r.slot!=='MainHand'),y.layers.filter(r=>r.slot!=='MainHand'));const r=x.layers.find(r=>r.slot==='MainHand'),s=y.layers.find(r=>r.slot==='MainHand');assert.deepEqual(r.transform,s.transform);assert.equal(r.pivotSemantic,'grip');assert.notEqual(r.atlasId,s.atlasId);
 }
});
test('cape shares its back pivot in front/back passes and is sampled from the body phase without an independent clock',()=>{
 for(const d of M.DIRECTIONS)for(let frameIndex=0;frameIndex<16;frameIndex++){
  const s=c.sample('BasicAttack',d,0,{frameIndex}),g=s.layers.filter(r=>r.slot==='Garment');assert.ok(g.length);for(const r of g){assert.equal(r.mode,'BODY_SYNC');assert.equal(r.pivotSemantic,'upper-back');assert.deepEqual(r.anchorTransform,s.registeredAnchors.back)}
  if(g.length===2){assert.deepEqual(g[0].transform,g[1].transform);assert.ok(s.drawOrder.indexOf('GarmentBack')<s.drawOrder.indexOf('Body'));assert.ok(s.drawOrder.indexOf('GarmentFront')<s.drawOrder.indexOf('MainHand'))}
 }
});
for(const [name,edit]of [
 ['Head pivot missing',p=>delete first(p).pivot],['Head pivot outside raster',p=>first(p).pivot[0]=-1],['Head anchor nonfinite',p=>p.bodyContract.anchorRegistration.Idle.S[0].head.x=NaN],
 ['Head phase mapping invalid',p=>p.parts['swordsman-head'].mode='PHASE_SYNC'],['Hair pivot invalid',p=>p.parts['hair-a'].timelines.Idle.S.frames[0].layers.HairFront.pivot=[Infinity,0]],
 ['weapon grip missing',p=>delete p.parts['weapon-a'].timelines.Idle.S.frames[0].layers.MainHand.pivot],['cape attachment invalid',p=>p.parts.garment.anchor='missingBack'],
 ['trim metadata omitted',p=>delete first(p).trim],['trim source overrun',p=>first(p).trim.offset=[300,300]],['finite transform rejected',p=>first(p).localTransform.rotation=Infinity],
 ['invalid phase reference',p=>p.parts['hair-a'].actionPhaseRegistration={Walk:[{at:.2,transform:{x:0,y:0,rotation:0,scale:1}}]}],
 ['missing direction mapping',p=>delete p.parts['swordsman-head'].timelines.Walk.NE],['missing registered body direction',p=>delete p.bodyContract.anchorRegistration.Walk.SE],
 ['contract timeline differs',p=>p.bodyContract.timeline.Walk.S[0]=10],['root override',p=>p.bodyContract.anchorRegistration.Idle.S[0].root={x:1,y:1,rotation:0,scale:1}],
 ['costume contract incompatible',p=>p.parts['swordsman-body-royal-proof'].contractId='other'],['Head socket invalid',p=>first(p).sockets.hair.scale=-1],['independent Outfit primary',p=>p.slots.Outfit={layers:['BackAccessory'],required:false}],
 ['head-local parent unrelated',p=>p.parts['hair-a'].parentLayer='MainHand'],['required Head removed',p=>p.defaultParts.Head=null]
])test('strict production validation rejects '+name,()=>{const bad=clone(p);edit(bad);assert.throws(()=>A.compileAssembly(t,bad))});
test('legacy motion and source atlases retain their baseline bytes, approval cannot be inferred',()=>{
 const r=read('authoring/characters/builds/swordsman-registration-v1/salvage-receipt.json'),hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
 assert.equal(hash('authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json'),r.motionTemplateSHA256);const legacy=read('authoring/characters/appearance/swordsman-male-painted/appearance-pack.json');for(const [id,a]of Object.entries(legacy.atlases))assert.equal(hash(a.file),r.sourceAtlases[id]);assert.equal(p.status,'REQUIRES_OWNER_VISUAL_REVIEW');assert.equal(r.ownerVisualApproval,'PENDING');assert.equal(r.faceRedrawn,false);
});
