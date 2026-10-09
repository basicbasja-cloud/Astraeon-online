'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto');
const A=require('../character-assembly.js'),M=require('../character-motion-template.js');
const read=p=>JSON.parse(fs.readFileSync(p));const motion=read('authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json'),pack=read('authoring/characters/appearance/swordsman-true8dir/appearance-pack.json'),c=A.compileAssembly(motion,pack);
const world=(r,p)=>A.composeTransform(r.transform,{x:p[0]-r.pivot[0],y:p[1]-r.pivot[1],rotation:0,scale:1});
test('candidate has complete unique directions, explicit phases and no mirrored fallback',()=>{
 assert.deepEqual(A.validateAppearancePack(pack,motion),[]);assert.equal(pack.mirroring,'none');assert.equal(pack.status,'REQUIRES_OWNER_VISUAL_REVIEW');
 for(const id of ['weapon-a','weapon-b']){assert.equal(pack.parts[id].weaponDefinition.perspectiveVariants.length,4);assert.deepEqual(Object.keys(pack.parts[id].timelines.BasicAttack),M.DIRECTIONS);}
 const sequences=M.DIRECTIONS.map(d=>JSON.stringify(pack.parts['weapon-a'].timelines.BasicAttack[d]));assert.equal(new Set(sequences).size,8);
 for(const atlas of Object.values(pack.atlases))assert.ok(fs.existsSync(atlas.file),atlas.file);
});
test('attachment and visible grip are distinct and both swords meet measured hand contact deterministically',()=>{
 for(const d of M.DIRECTIONS)for(let i=0;i<16;i++)for(const id of ['weapon-a','weapon-b']){
  const o={frameIndex:i,appearance:{MainHand:id}},s=c.sample('BasicAttack',d,0,o),r=s.layers.find(l=>l.layer==='MainHand'),f=r.weaponPoseFrame,g=world(r,f.gripContactPoint),tip=world(r,f.weaponTip);
  assert.notDeepEqual(f.equipmentAnchor,f.gripContactPoint);assert.ok(Math.hypot(g.x-f.handContactPoint[0],g.y-f.handContactPoint[1])<.001);assert.ok(Number.isFinite(tip.x)&&Number.isFinite(tip.y));assert.equal(f.drawProfile,pack.frameDrawProfiles.BasicAttack[d][i]);assert.deepEqual(s,c.sample('BasicAttack',d,0,o));
 }
});
test('invalid weapon phase, anchor, tip, perspective or profile is rejected',()=>{
 for(const [key,value]of [['phase','missing'],['equipmentAnchor',[NaN,0]],['weaponTip',[]],['gripContactPoint',null],['perspectiveVariant','missing'],['drawProfile','missing']]){
  const p=structuredClone(pack);p.parts['weapon-a'].timelines.BasicAttack.S.frames[7].layers.MainHand.weaponPoseFrame[key]=value;assert.ok(A.validateAppearancePack(p,motion).length,key);
 }
});
test('costume, sword and combined head swaps preserve action direction frame and both clocks',()=>{
 for(const d of M.DIRECTIONS)for(let i=0;i<16;i++){
  const t=motion.actions.BasicAttack.directions[d].frames.slice(0,i).reduce((n,f)=>n+f.durationMs,0)+1;const ctl=A.createController(c,{action:'BasicAttack',direction:d,elapsedMs:t,cosmeticTimeMs:777});const before=ctl.sample();
  for(const change of [{BodyWithOutfit:'swordsman-body-royal-proof'},{MainHand:'weapon-b'},{Head:'head-style-b'}]){ctl.setAppearance(change);const after=ctl.sample();assert.equal(after.frameIndex,before.frameIndex);assert.equal(after.direction,d);assert.equal(after.action,'BasicAttack');assert.equal(ctl.elapsedMs,t);assert.equal(ctl.cosmeticTimeMs,777);assert.deepEqual(after.frame,before.frame);}
 }
 assert.equal(pack.headAppearanceModel,'HeadIncludesHair');assert.ok(!pack.slots.Hair);assert.equal(pack.parts['head-style-a'].slot,'Head');
});
test('timing remains 450ms with contact at 170ms and all body directions are separate source cells',()=>{
 for(const d of M.DIRECTIONS){const f=motion.actions.BasicAttack.directions[d].frames;assert.equal(f.reduce((n,x)=>n+x.durationMs,0),450);assert.equal(f.slice(0,7).reduce((n,x)=>n+x.durationMs,0),170);}
 const rows=M.DIRECTIONS.map(d=>pack.parts['swordsman-body-default'].timelines.BasicAttack[d].frames[7].layers.Body.rect[1]);assert.equal(new Set(rows).size,8);
});
