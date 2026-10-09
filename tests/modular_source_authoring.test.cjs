const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto');
const S=require('../character-source-authoring.js');
const root='authoring/characters/true-modular/swordsman-male-v2/';
const read=p=>JSON.parse(fs.readFileSync(p)),clone=o=>JSON.parse(JSON.stringify(o));
const m=read(root+'source-manifest.json'),c=read(root+'pose-contract.json'),t=read(c.pose.motionTemplate);
const compile=()=>S.compileSources(m,c,t,{diagnosticIncomplete:true});
test('incomplete Hair cannot masquerade as a complete authoring pack',()=>{
 assert.deepEqual(S.validateSources(m,c,t),['Missing source coverage slot/Hair']);
 assert.throws(()=>S.compileSources(m,c,t),/Missing source coverage/);
 assert.throws(()=>S.assertSouthGatePassed(m,c,t),/Missing source coverage/);
 const s=compile().sample();assert.equal(s.sourceCoverageComplete,false);assert.equal(s.visualGate,'VISUAL_FAIL');
 assert.ok(!s.layers.some(l=>l.layer.startsWith('Hair')));
});
test('source raw rasters, normalized rasters, prompts and pose contract match actual digests',()=>{
 const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
 assert.equal(hash(root+'pose-contract.json'),m.contractSHA256);
 for(const p of Object.values(m.parts))for(const r of Object.values(p.layers)){
  assert.equal(hash(r.rawSource),r.rawSHA256);assert.equal(hash(r.file),r.rasterSHA256);assert.equal(hash(r.prompt),r.promptSHA256);
 }
});
test('weapon hide leaves every BodyCore HeadBase Face and Outfit source identity unchanged',()=>{
 const a=compile(),before=a.sample(),after=a.sample(undefined,{appearance:{Weapon:null}});
 assert.deepEqual(after.layers,before.layers.filter(l=>l.slot!=='Weapon'));
 assert.strictEqual(after.frame.anchors,before.frame.anchors);assert.equal(after.frameIndex,before.frameIndex);
 assert.equal(after.direction,before.direction);assert.equal(after.elapsedMs,before.elapsedMs);
});
test('unproduced directions or actions are rejected rather than mirrored or duplicated',()=>{
 const a=compile();for(const id of ['Idle/SW/key0','Walk/S/key0','BasicAttack/S/key0'])assert.throws(()=>a.sample(id),/not been independently authored/);
 const bad=clone(m);bad.availablePoses.push('Idle/N/key0');assert.throws(()=>S.compileSources(bad,c,t,{diagnosticIncomplete:true}),/missing directions or actions/);
});
test('shared registration and anatomical socket authority cannot be overridden by parts',()=>{
 for(const [field,value] of [['offset',[10,20]],['anchors',{mainHand:[10,20]}],['durationMs',500],['equipmentLoadout',{sword:'fire'}]]){
  const bad=clone(m);bad.parts['outfit-a'][field]=value;assert.throws(()=>S.compileSources(bad,c,t,{diagnosticIncomplete:true}),/overrides shared pose\/gameplay/);
 }
 const bad=clone(c);bad.pose.anchors.root.y++;assert.throws(()=>S.compileSources(m,bad,t,{diagnosticIncomplete:true}),/root drift/);
});
test('body, head and outfit cannot claim the same flattened authoritative raster',()=>{
 const bad=clone(m);bad.parts.headbase.layers.HeadBase.rawSource=bad.parts.bodycore.layers.BodyCore.rawSource;
 assert.throws(()=>S.compileSources(bad,c,t,{diagnosticIncomplete:true}),/flattened raster/);
 const bad2=clone(m);bad2.parts.face.authorship='CUT_FROM_COMPLETE_CHARACTER';assert.throws(()=>S.compileSources(bad2,c,t,{diagnosticIncomplete:true}),/independently authored/);
});
test('duplicate source draw order and invented layer identities are rejected',()=>{
 const bad=clone(m);bad.drawOrder[0]='Weapon';assert.throws(()=>S.compileSources(bad,c,t,{diagnosticIncomplete:true}),/Draw order/);
 const bad2=clone(m);bad2.parts.face.layers.Clothes=bad2.parts.face.layers.Face;assert.throws(()=>S.compileSources(bad2,c,t,{diagnosticIncomplete:true}),/unrelated/);
});
test('diagnostic opt-in cannot bypass invalid registration, mirroring or owner approval',()=>{
 for(const mutate of [x=>x.registration.root.x++,x=>x.mirroring='horizontal',x=>x.ownerApproval='APPROVED',x=>x.status='APPROVED',x=>x.poseId='Idle/S/key1']){
  const bad=clone(m);mutate(bad);assert.throws(()=>S.compileSources(bad,c,t,{diagnosticIncomplete:true}));
 }
 assert.throws(()=>compile().selection({BodyCore:null}),/Required/);
});
test('class semantics and body variant are distinct and source assembly is immutable',()=>{
 const a=compile();assert.equal(a.manifest.classId,'Swordsman');assert.equal(a.manifest.bodyVariant,'male');assert.ok(Object.isFrozen(a.manifest.parts));
 const bad=clone(m);bad.classId='SwordsmanMale';assert.throws(()=>S.compileSources(bad,c,t,{diagnosticIncomplete:true}),/separate/);
});
