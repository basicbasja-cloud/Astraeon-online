'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const A=require('../character-assembly.js'),M=require('../character-motion-template.js');
const read=p=>JSON.parse(fs.readFileSync(p));
const motion=read('authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json');
const pack=read('authoring/characters/appearance/swordsman-basicattack-anatomy/appearance-pack.json');
const receipt=read('authoring/characters/builds/swordsman-basicattack-anatomy-v1/packaging-receipt.json');
const compiled=A.compileAssembly(motion,pack);
test('anatomy candidate compiles the same three actions and eight directions without mirroring',()=>{
 assert.deepEqual(A.validateAppearancePack(pack,motion),[]);
 assert.deepEqual(pack.bodyContract.actions,['Idle','Walk','BasicAttack']);
 assert.deepEqual(pack.bodyContract.directions,M.DIRECTIONS);
 assert.equal(pack.bodyContract.registration.mirroring,'none');
 assert.equal(pack.status,'REQUIRES_OWNER_VISUAL_REVIEW');
});
test('all 128 attack poses retain exact MotionTemplate frames, root, contact and presentation timing',()=>{
 for(const direction of M.DIRECTIONS){let elapsed=0;const frames=motion.actions.BasicAttack.directions[direction].frames;
  assert.equal(frames.slice(0,7).reduce((n,f)=>n+f.durationMs,0),170);
  for(let frameIndex=0;frameIndex<frames.length;frameIndex++){
   const sample=compiled.sample('BasicAttack',direction,elapsed+1);
   assert.equal(sample.frameIndex,frameIndex);assert.deepEqual(sample.frame,frames[frameIndex]);
   assert.deepEqual(sample.registration.root,motion.registration.root);
   if(frameIndex===7)assert.ok(sample.frame.events.some(e=>e.name==='attackContact'&&e.authority==='presentation'));
   elapsed+=frames[frameIndex].durationMs;
  }assert.equal(elapsed,450);
 }
});
test('two sword identities share painted hand transforms and exact blade tip through all attack frames',()=>{
 for(const entry of receipt.hands)for(const MainHand of ['weapon-a','weapon-b']){
  const s=compiled.sample('BasicAttack',entry.direction,0,{frameIndex:entry.frame,appearance:{MainHand}});
  const r=s.layers.find(l=>l.layer==='MainHand');
  assert.ok(Math.abs(r.transform.x-entry.grip[0])<.001);assert.ok(Math.abs(r.transform.y-entry.grip[1])<.001);
  assert.deepEqual(r.pivot,[24,98]);assert.equal(r.atlasId,MainHand+'-attack-grip');
  const tip=A.composeTransform(r.transform,{x:r.bladeTip[0]-24,y:r.bladeTip[1]-98,rotation:0,scale:1});
  assert.ok(Math.abs(tip.x-s.registeredAnchors.weaponTip.x)<.001);assert.ok(Math.abs(tip.y-s.registeredAnchors.weaponTip.y)<.001);
  if(entry.frame===15)assert.equal(r.weaponPhase,'readyReturn');
 }
});
test('costume replacement retains every attachment and both clocks at each repaired attack phase',()=>{
 for(const direction of M.DIRECTIONS){let elapsed=0;
  for(const frame of motion.actions.BasicAttack.directions[direction].frames){
   const ctl=A.createController(compiled,{action:'BasicAttack',direction,elapsedMs:elapsed+1,cosmeticTimeMs:777,appearance:{OffHand:'offhand',Headgear:'headgear'}}),before=ctl.sample();
   ctl.setAppearance({BodyWithOutfit:'swordsman-body-royal-proof'});const after=ctl.sample();
   assert.equal(ctl.elapsedMs,elapsed+1);assert.equal(ctl.cosmeticTimeMs,777);assert.equal(after.frameIndex,before.frameIndex);
   assert.deepEqual(after.frame,before.frame);assert.deepEqual(after.registeredAnchors,before.registeredAnchors);
   assert.deepEqual(after.layers.filter(l=>l.slot!=='BodyWithOutfit'),before.layers.filter(l=>l.slot!=='BodyWithOutfit'));
   elapsed+=frame.durationMs;
  }
 }
});
test('review-only joints never enter sampled gameplay motion or equipment',()=>{
 const joints=read('authoring/characters/builds/swordsman-basicattack-anatomy-v1/joint-review.json');
 assert.equal(joints.status,'REVIEW_ONLY_NOT_GAMEPLAY_AUTHORITY');
 for(const direction of M.DIRECTIONS){assert.equal(joints.frames[direction].length,16);assert.ok(joints.frames[direction].every(e=>e.joints.length===4));}
 assert.equal(JSON.stringify(pack).includes('joint-review'),false);assert.equal(JSON.stringify(motion).includes('joint-review'),false);
});
test('ready-return blade angle agrees with next ready while body recovery is independently painted',()=>{
 for(const direction of M.DIRECTIONS){const a=compiled.sample('BasicAttack',direction,0,{frameIndex:15}).registeredAnchors.mainHand.rotation,b=compiled.sample('BasicAttack',direction,0,{frameIndex:0}).registeredAnchors.mainHand.rotation;
  assert.ok(Math.abs(Math.atan2(Math.sin(a-b),Math.cos(a-b)))<.00001);
 }
});
