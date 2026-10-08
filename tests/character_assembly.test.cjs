'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const M=require('../character-motion-template.js'),A=require('../character-assembly.js');
const root=path.join(__dirname,'..'),read=p=>JSON.parse(fs.readFileSync(path.join(root,p)));
const template=read('authoring/characters/motion-templates/assembly-debug/motion-template.json');
const pack=read('authoring/characters/appearance/debug-blue/appearance-pack.json'),second=read('authoring/characters/appearance/debug-coral/appearance-pack.json');
const clone=o=>structuredClone(o),assembly=A.compileAssembly(template,pack),seq=t=>t.actions.Walk.directions.S;
test('canonical named direction order and required anatomical anchor names',()=>{
 assert.deepEqual(M.DIRECTIONS,['S','SW','W','NW','N','NE','E','SE']);
 assert.deepEqual(M.ANCHORS,['root','head','mainHand','offHand','back','waist','footL','footR']);
});
test('synthetic MotionTemplate and both appearance packs validate independently',()=>{
 assert.deepEqual(M.validateMotionTemplate(template),[]);
 for(const p of [pack,second])assert.deepEqual(A.validateAppearancePack(p,template),[]);
});
for(const action of ['Idle','Walk','BasicAttack'])test(action+' fixture has eight authored directions, preserved keys and separate in-betweens',()=>{
 assert.deepEqual(Object.keys(template.actions[action].directions),M.DIRECTIONS);
 for(const d of M.DIRECTIONS){const s=template.actions[action].directions[d];assert.ok(s.referenceKeys.length);assert.ok(s.frames.some(f=>f.role==='astraeonInbetween'));assert.deepEqual(s.frames.filter(f=>f.role==='referenceKey').map(f=>f.id),s.referenceKeys.map(f=>f.id));assert.ok(s.frames.every(f=>f.source?.kind!=='RO1_ACT'))}
});
test('unknown action rejects instead of idle fallback',()=>assert.throws(()=>assembly.sample('Run','S'),/Unknown action/));
test('unknown direction rejects instead of mirroring',()=>assert.throws(()=>assembly.sample('Walk','south'),/Unknown direction/));
const edits=[
 ['noncanonical direction order',t=>t.directions.reverse()],
 ['missing eighth direction',t=>delete t.actions.Idle.directions.NE],
 ['malformed zero frame timing',t=>seq(t).frames[0].durationMs=0],
 ['nonfinite frame timing',t=>seq(t).frames[0].durationMs=Infinity],
 ['fractional millisecond frame timing',t=>seq(t).frames[0].durationMs=.1],
 ['missing explicit root',t=>delete seq(t).frames[0].root],
 ['nonfinite root coordinates',t=>seq(t).frames[0].root.x=NaN],
 ['root drift',t=>seq(t).frames[1].root.x++],
 ['missing required foot anchor',t=>delete seq(t).frames[0].anchors.footL],
 ['nonfinite anchor coordinates',t=>seq(t).frames[0].anchors.head.y=Infinity],
 ['nonfinite attachment rotation',t=>seq(t).frames[0].anchors.mainHand.rotation=NaN],
 ['nonfinite attachment scale',t=>seq(t).frames[0].anchors.head.scale=Infinity],
 ['negative attachment scale',t=>seq(t).frames[0].anchors.offHand.scale=-1],
 ['duplicate frame ID',t=>seq(t).frames[1].id=seq(t).frames[0].id],
 ['unclassified frame role',t=>seq(t).frames[1].role='pose'],
 ['in-between refers to non-neighboring keys',t=>seq(t).frames[1].between[1]=seq(t).referenceKeys[2].id],
 ['in-between invents a source phase',t=>seq(t).frames[1].referencePhase='newTechnique'],
 ['in-between phase fraction disagrees with timestamp',t=>seq(t).frames[1].fraction=.6],
 ['reference pose orientation changed',t=>seq(t).frames[0].poseIntent.bodyOrientation='N'],
 ['reference key metadata removed',t=>delete seq(t).frames[0].poseIntent],
 ['reference key source mislabeled RO',t=>seq(t).frames[0].source.kind='RO1_ACT'],
 ['synthetic fixture promoted to production',t=>t.status='APPROVED'],
 ['key catalog contains invented in-between',t=>seq(t).referenceKeys[0].role='astraeonInbetween'],
 ['unknown default draw profile',t=>t.defaultDrawProfile='absent'],
 ['invalid direction draw profile',t=>t.actions.Walk.directions.N.drawProfile='absent'],
 ['invalid frame draw profile',t=>seq(t).frames[0].drawProfile='absent'],
 ['invalid frame draw override',t=>seq(t).frames[0].drawOrder=['Body','Body']],
 ['invalid draw profile permutation',t=>t.drawProfiles.front[0]='Body'],
 ['production direction mirroring flag',t=>t.registration.mirroring='horizontal'],
 ['visual event claims Combat authority',t=>seq(t).frames[0].events=[{name:'damage',authority:'combat'}]],
 ['null malformed frame',t=>seq(t).frames[0]=null]
];
for(const [name,edit] of edits)test('MotionTemplate rejects '+name,()=>{const t=clone(template);edit(t);assert.ok(M.validateMotionTemplate(t).length);assert.throws(()=>M.compileMotionTemplate(t))});
test('RO draft with unknown source facts is deliberately non-executable',()=>{
 const draft=read('authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json');assert.equal(draft.status,'REFERENCE_DATA_REQUIRED');assert.throws(()=>M.compileMotionTemplate(draft),/reference data required/);
 const manifest=read('authoring/characters/motion-templates/ro1-swordsman-male/reference-manifest.json');assert.equal(manifest.rawAssetsInspected.length,0);assert.equal(manifest.unknowns.keyPoseSequence.value,null);
});
test('source-derived templates require manifest hash and real key source identities',()=>{
 const t=clone(template);t.provenance={kind:'RO1_DERIVED'};assert.throws(()=>M.compileMotionTemplate(t),/reference manifest identity/);
 t.provenance.referenceManifestSHA256='a'.repeat(64);assert.throws(()=>M.compileMotionTemplate(t),/source-derived key identity/);
});
test('action duration is deterministic through loops and nonloop terminal holds',()=>{
 const c=assembly.motion;assert.equal(c.duration('Walk','SW'),800);assert.equal(c.sample('Walk','SW',800).frameIndex,0);assert.equal(c.sample('Walk','SW',1610).frameIndex,c.sample('Walk','SW',10).frameIndex);
 assert.equal(c.sample('BasicAttack','S',10000).frameIndex,template.actions.BasicAttack.directions.S.frames.length-1);
});
test('selective smoothing preserves total time, key times and exact reference metadata',()=>{
 const t=clone(template),s=seq(t),k=s.referenceKeys;
 const sm=M.smoothSequence({...s,frames:k},{[k[0].id]:[{id:'test/ib1',at:.25},{id:'test/ib2',at:.75}]},true);
 assert.equal(sm.frames.length,k.length+2);assert.equal(sm.frames.reduce((n,f)=>n+f.durationMs,0),800);
 assert.deepEqual(sm.frames.slice(0,3).map(f=>f.durationMs),[40,80,40]);
 t.actions.Walk.directions.S=sm;assert.deepEqual(M.validateMotionTemplate(t),[]);
 assert.deepEqual(sm.frames[0].poseIntent,k[0].poseIntent);assert.deepEqual(sm.frames[0].anchors,k[0].anchors);
});
test('additional frames cannot silently add total duration',()=>{const t=clone(template);seq(t).frames[1].durationMs+=30;assert.throws(()=>M.compileMotionTemplate(t),/duration|timestamp/)});
test('smoothing does not double every frame without an insertion schedule',()=>{const s=seq(template);const out=M.smoothSequence(s,{},true);assert.deepEqual(out.frames,s.referenceKeys)});
test('smoothing rejects unknown, unordered, zero-budget and terminal insertions',()=>{
 const s=seq(template),key=s.referenceKeys[0].id;
 for(const [schedule,loop] of [[{unknown:[{id:'x',at:.5}]},true],[{[key]:[{id:'x',at:.6},{id:'y',at:.5}]},true],[{[key]:[{id:'x',at:.00001}]},true],[{[s.referenceKeys.at(-1).id]:[{id:'x',at:.5}]},false]])assert.throws(()=>M.smoothSequence(s,schedule,loop));
});
test('attachment smoothing takes shortest rotation arc and linear scale',()=>{
 const t=M.interpolateTransform({x:0,y:0,rotation:170*Math.PI/180,scale:1},{x:10,y:20,rotation:-170*Math.PI/180,scale:2},.5);
 assert.ok(Math.abs(t.rotation-Math.PI)<1e-12);assert.deepEqual([t.x,t.y,t.scale],[5,10,1.5]);
});
test('BODY_SYNC samples exact expanded body frame without affecting timing',()=>{const s=assembly.sample('Walk','SW',430);assert.equal(s.frameIndex,5);assert.equal(s.layers.find(l=>l.layer==='Body').sampleIndex,5);assert.equal(s.totalDurationMs,800)});
test('PHASE_SYNC uses time thresholds rather than frame-index ratios',()=>{
 for(const [time,expected] of [[0,0],[319,0],[320,1],[599,1],[600,2]])assert.equal(assembly.sample('Walk','S',time).layers.find(l=>l.layer==='HairFront').sampleIndex,expected);
});
test('explicit frame inspection maps PHASE_SYNC from frame start timestamp',()=>{
 const s=assembly.sample('Walk','S',0,{frameIndex:5});assert.equal(s.layers.find(l=>l.layer==='HairFront').sampleIndex,1);
});
test('ANCHOR_HOLD reuses a raster sample while attachment transforms advance',()=>{
 const a=assembly.sample('Walk','S',0).layers.find(l=>l.layer==='MainHand'),b=assembly.sample('Walk','S',400).layers.find(l=>l.layer==='MainHand');
 assert.equal(a.sampleIndex,0);assert.equal(b.sampleIndex,0);assert.deepEqual(a.rect,b.rect);assert.notDeepEqual(a.transform,b.transform);
});
test('ANCHOR_HOLD can select a perspective-critical authored phase view',()=>{
 const p=clone(pack),seq=p.parts['weapon-a'].timelines['*'].S;
 seq.views.push({at:.5,layers:{MainHand:clone(p.parts['weapon-b'].timelines['*'].S.views[0].layers.MainHand)}});
 const c=A.compileAssembly(template,p);assert.equal(c.sample('Walk','S',500).layers.find(l=>l.layer==='MainHand').sampleIndex,1);
});
test('OWN_LOOP follows independent cosmetic clock across action changes',()=>{
 for(const action of ['Idle','Walk','BasicAttack'])assert.equal(assembly.sample(action,'S',0,{cosmeticTimeMs:100}).layers.find(l=>l.layer==='CosmeticFX').sampleIndex,1);
 assert.equal(assembly.sample('Walk','S',700,{cosmeticTimeMs:360}).layers.find(l=>l.layer==='CosmeticFX').sampleIndex,0);
 const c=A.createController(assembly,{cosmeticTimeMs:100});c.setAction('BasicAttack');assert.equal(c.cosmeticTimeMs,100);
});
test('direction order resolves semantic profiles and frame override takes precedence',()=>{
 const layers=s=>s.layers.map(l=>l.layer),front=layers(assembly.sample('Walk','S',0)),rear=layers(assembly.sample('Walk','N',0));
 assert.ok(front.indexOf('MainHand')>front.indexOf('Body'));assert.ok(rear.indexOf('MainHand')<rear.indexOf('Body'));assert.ok(rear.indexOf('OffHand')<rear.indexOf('Body'));
 const attack=layers(assembly.sample('BasicAttack','S',200));assert.ok(attack.indexOf('MainHand')<attack.indexOf('Body'));
 const t=clone(template),f=t.actions.BasicAttack.directions.N.frames.find(f=>f.role==='referenceKey'&&f.referencePhase==='debugKey1'),k=t.actions.BasicAttack.directions.N.referenceKeys[1];
 f.drawOrder=[...M.LAYERS];k.drawOrder=[...M.LAYERS];const out=layers(A.compileAssembly(t,pack).sample('BasicAttack','N',200));assert.ok(out.indexOf('MainHand')>out.indexOf('Body'));
});
test('absent optional layers produce no transparent-atlas requirements',()=>{
 const p=clone(pack);p.defaultParts.OffHand=null;delete p.parts.offhand;delete p.atlases.offhand;
 const c=A.compileAssembly(template,p);assert.ok(!c.sample('Walk','S',0).layers.some(l=>l.layer==='OffHand'));
});
const swaps=[['Hair','hair-b',['HairBack','HairFront']],['MainHand','weapon-b',['MainHand']],['OffHand',null,['OffHand']],['Headgear',null,['HeadgearTop']],['Headgear','headgear-b',['HeadgearTop']],['Garment',null,['GarmentBack','GarmentFront']]];
for(const [slot,value,changed] of swaps)test(slot+' swap '+value+' isolates every unrelated source across all actions/directions/frames',()=>{
 for(const [action,a] of Object.entries(template.actions))for(const d of M.DIRECTIONS)for(let i=0;i<a.directions[d].frames.length;i++){
  const options={frameIndex:i,cosmeticTimeMs:100};const before=assembly.sample(action,d,430,options),after=assembly.sample(action,d,430,{...options,appearance:{[slot]:value}});
  assert.equal(after.frameIndex,before.frameIndex);assert.strictEqual(after.frame,before.frame);assert.equal(after.elapsedMs,before.elapsedMs);
  assert.deepEqual(after.layers.filter(l=>!changed.includes(l.layer)),before.layers.filter(l=>!changed.includes(l.layer)));
  assert.notDeepEqual(after.layers.filter(l=>changed.includes(l.layer)),before.layers.filter(l=>changed.includes(l.layer)));
 }
});
test('appearance swap preserves Walk/SW/frame5, time, direction and external gameplay state',()=>{
 const gameplay=Object.freeze({position:Object.freeze({x:12,y:31}),collision:'capsule',targetId:'enemy-9',combatPhase:'recovery',inventoryAuthority:'external'}),state=clone(gameplay);
 const c=A.createController(assembly,{action:'Walk',direction:'SW',elapsedMs:430,cosmeticTimeMs:100});
 for(const [slot,value] of swaps){c.setAppearance({[slot]:value});assert.equal(c.sample().frameIndex,5);assert.equal(c.elapsedMs,430);assert.equal(c.sample().action,'Walk');assert.equal(c.sample().direction,'SW');assert.deepEqual(gameplay,state)}
});
test('same BodySpriteSet atlas identity survives both Hair and weapon alternatives',()=>{
 const get=appearance=>assembly.sample('Walk','SW',430,{appearance}).layers.find(l=>l.layer==='Body');
 assert.deepEqual(get({}),get({Hair:'hair-b'}));assert.deepEqual(get({}),get({MainHand:'weapon-b'}));
});
test('second dummy appearance uses the exact same immutable MotionTemplate without class branches',()=>{
 const other=A.compileAssembly(template,second);const a=assembly.sample('Walk','NE',430),b=other.sample('Walk','NE',430);
 assert.equal(a.motionTemplateId,b.motionTemplateId);assert.deepEqual(a.frame,b.frame);assert.notEqual(a.layers.find(l=>l.layer==='Body').atlasId,b.layers.find(l=>l.layer==='Body').atlasId);
 for(const file of ['character-assembly.js','character-motion-template.js'])assert.ok(!/classId|Swordsman|Mage/.test(fs.readFileSync(path.join(root,file),'utf8')));
});
const appearanceEdits=[
 ['arbitrary body timing',p=>p.durationMs=2000],['part body timing',p=>p.parts['hair-a'].timing=[1]],
 ['per-raster body timing',p=>p.parts['weapon-a'].timelines['*'].S.views[0].layers.MainHand.durationMs=1],
 ['shared canvas mismatch',p=>p.registration.canvas[0]++],['unknown sampling mode',p=>p.parts['hair-a'].mode='RESIZE'],
 ['BODY_SYNC count mismatch',p=>p.parts['body-blue'].timelines.Walk.S.frames.pop()],
 ['invalid phase mapping',p=>p.parts['hair-a'].timelines['*'].S.phases[1].at=0],
 ['missing authored direction',p=>delete p.parts['head'].timelines['*'].NE],
 ['invalid own-loop delay',p=>p.parts.fx.timelines['*'].S.frames[0].durationMs=0],
 ['nonfinite local attachment',p=>p.parts['hair-a'].timelines['*'].S.phases[0].layers.HairBack.localTransform.rotation=Infinity],
 ['missing atlas reference',p=>delete p.atlases['weapon-a']],['out-of-atlas rect',p=>p.parts['weapon-a'].timelines['*'].S.views[0].layers.MainHand.rect[0]=99999],
 ['production mirroring',p=>p.mirroring='horizontal'],['required Body removed',p=>p.defaultParts.Body=null],
 ['unrelated semantic layer',p=>p.parts['weapon-a'].timelines['*'].S.views[0].layers.Body=p.parts['weapon-a'].timelines['*'].S.views[0].layers.MainHand],
 ['unknown motion compatibility',p=>p.compatibleMotionTemplates=['other']],['atlas traversal',p=>p.atlases['head'].file='assets/characters/../../secret.png']
];
for(const [name,edit] of appearanceEdits)test('AppearancePack rejects '+name,()=>{const p=clone(pack);edit(p);assert.ok(A.validateAppearancePack(p,template).length);assert.throws(()=>A.compileAssembly(template,p))});
test('immutable compilation isolates source metadata and appearance selections',()=>{
 const t=clone(template),p=clone(pack),c=A.compileAssembly(t,p);p.defaultParts.Hair='hair-b';t.actions.Walk.directions.S.frames[0].durationMs=1;
 assert.equal(c.sample('Walk','S',0).appearance.Hair,'hair-a');assert.equal(c.motion.duration('Walk','S'),800);assert.ok(Object.isFrozen(c.pack.parts));assert.ok(Object.isFrozen(c.motion.template.actions.Walk));
});
test('appearance selection rejects unknown/incompatible slot and required-layer absence',()=>{
 for(const p of [{Unknown:'hair-a'},{Hair:'weapon-a'},{Body:null}])assert.throws(()=>assembly.selection(p));
});
test('invalid clocks and frame indices reject',()=>{
 for(const n of [-1,Infinity,NaN])assert.throws(()=>assembly.sample('Walk','S',n));
 assert.throws(()=>assembly.sample('Walk','S',0,{cosmeticTimeMs:NaN}));assert.throws(()=>assembly.sample('Walk','S',0,{frameIndex:500}));
});
test('raster draw applies anchor rotation/scale and resolves all assets before drawing',()=>{
 const calls=[],ctx={save(){calls.push(['save'])},restore(){calls.push(['restore'])},translate(...a){calls.push(['translate',...a])},rotate(...a){calls.push(['rotate',...a])},scale(...a){calls.push(['scale',...a])},drawImage(...a){calls.push(['drawImage',...a])}};
 const images=Object.fromEntries(Object.keys(pack.atlases).map(id=>[id,{}])),s=assembly.sample('Walk','SW',430);
 const anchors=A.drawAssembly(ctx,s,images,{x:200,y:300,scale:1});assert.deepEqual(anchors.root,{x:200,y:300,rotation:0,scale:1});assert.ok(calls.some(c=>c[0]==='rotate'&&c[1]!==0));
 calls.length=0;delete images[s.layers.at(-1).atlasId];assert.throws(()=>A.drawAssembly(ctx,s,images),/Atlas not loaded/);assert.equal(calls.length,0);
});
test('legacy modular API exposes v1 extension without replacing old definitions',()=>{const legacy=require('../modular-sprites.js');assert.equal(legacy.compileAssembly,A.compileAssembly);assert.equal(typeof legacy.compile,'function');assert.equal(typeof legacy.drawHumanoid,'function')});
test('protected gameplay, world, Blender and boot sources unchanged from clean parent',()=>{
 const diff=cp.execFileSync('git',['diff','c258c5034a49462381d15f425f103eddf85242c9','--name-only','--','world','authoring/*.blend','game.js','combat.js','character-motion.js','navigation.js','save-state.js','wardrobe.js','boot.js','index.html','sw.js','character-renderer.js'],{cwd:root,encoding:'utf8'});assert.equal(diff.trim(),'');
});
test('visual events do not become Combat authority',()=>{for(const a of Object.values(template.actions))for(const s of Object.values(a.directions))for(const f of s.frames)for(const e of f.events)assert.equal(e.authority,'presentation');assert.ok(!/AstraeonCombat|damage|collision|targeting/.test(fs.readFileSync(path.join(root,'character-assembly.js'),'utf8')))});
