'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
global.window={};
const api=require('../modular-sprites.js');
const read=name=>JSON.parse(fs.readFileSync(path.join(__dirname,'../assets/characters/'+name+'-proof/sprite.json'),'utf8'));
const sword=read('swordsman'),mage=read('mage'),clone=()=>structuredClone(sword);
for(const definition of [sword,mage])test(definition.classId+' resolves every clip, direction and synchronized part',()=>{
 const compiled=api.compile(definition);
 assert.deepEqual(definition.directions,['S','SW','W','NW','N','NE','E','SE']);
 for(const [animation,clip] of Object.entries(definition.clips))for(const direction of api.DIRECTIONS)for(let frameIndex=0;frameIndex<clip.durations.length;frameIndex++){
  const frame=compiled.sample(animation,direction,0,{frameIndex});
  assert.equal(frame.layers.length,6);assert.equal(frame.frameIndex,frameIndex);assert.equal(frame.duration,clip.durations[frameIndex]);
  assert.deepEqual(frame.sockets.root,[160,264]);assert.equal(frame.canvas.frameWidth,320);
  for(const layer of frame.layers){assert.ok(layer.frameId.endsWith(`_${animation}_${direction}_${String(frameIndex).padStart(2,'0')}`));assert.equal(layer.rect[2],320);assert.equal(layer.rect[3],320)}
 }
 assert.equal(new Set(Object.values(definition.clips).map(c=>c.durations.length)).size,3);
});
test('one clip clock handles unequal durations, loop boundaries and non-looping holds',()=>{
 const c=api.compile(sword);
 for(const [t,i] of [[0,0],[349,0],[350,1],[799,1],[800,0],[1150,1]])assert.equal(c.sample('Idle','S',t).frameIndex,i);
 for(const [t,i] of [[159,0],[160,1],[229,1],[230,2],[460,2],[1e6,2]])assert.equal(c.sample('BasicAttack','S',t).frameIndex,i);
 assert.throws(()=>c.sample('Idle','S',-1));assert.throws(()=>c.sample('Idle','S',NaN));assert.throws(()=>c.sample('Idle','South',0));assert.throws(()=>c.sample('Idle','S',0,{frameIndex:2}));
});
test('swapping a weapon changes one part while preserving shared pose, handedness and timing',()=>{
 const c=api.compile(sword),a=c.sample('Walk','SW',130),b=c.sample('Walk','SW',130,{appearance:{Weapon:'weapon-alt'}});
 assert.equal(a.frameIndex,b.frameIndex);assert.equal(a.duration,b.duration);assert.deepEqual(a.sockets,b.sockets);
 assert.deepEqual(a.layers.filter(l=>l.slot!=='Weapon'),b.layers.filter(l=>l.slot!=='Weapon'));
 assert.equal(b.layers.find(l=>l.slot==='Weapon').partId,'weapon-alt');
 assert.throws(()=>c.sample('Idle','S',0,{appearance:{Hair:'weapon-alt'}}));
 assert.throws(()=>c.sample('Idle','S',0,{appearance:{Weapon:null}}));
 assert.throws(()=>c.sample('Idle','S',0,{appearance:{Unknown:'weapon'}}));
});
test('direction and individual attack frame override default draw order',()=>{
 const c=api.compile(sword),order=(a,d,i)=>c.sample(a,d,0,{frameIndex:i}).layers.map(l=>l.slot);
 assert.deepEqual(order('Walk','S',0),['BackAccessory','BaseBody','Outfit','Hair','Weapon','Headgear']);
 assert.deepEqual(order('Walk','N',0),['BackAccessory','Weapon','BaseBody','Outfit','Hair','Headgear']);
 assert.deepEqual(order('BasicAttack','N',1),['BackAccessory','BaseBody','Outfit','Hair','Headgear','Weapon']);
});
test('all screen headings resolve by named direction; legacy table indices are never reused',()=>{
 for(let row=0;row<8;row++){
  const angle=Math.PI/2+row*Math.PI/4;
  assert.equal(api.directionFromHeading(angle,(x,y)=>({x,y})),api.DIRECTIONS[row]);
  assert.equal(api.directionFromHeading(angle+Math.PI*2,(x,y)=>({x,y})),api.DIRECTIONS[row]);
 }
 require('../world-view.js');
 for(let row=0;row<8;row++){
  const a=Math.PI/2+row*Math.PI/4,v=window.AstraeonView.inverse(Math.cos(a),Math.sin(a));
  assert.equal(api.directionFromHeading(Math.atan2(v.y,v.x),window.AstraeonView.project),api.DIRECTIONS[row]);
 }
});
const edits=[
 ['missing direction',d=>delete d.clips.Walk.directions.NE],
 ['wrong direction order',d=>d.directions.reverse()],
 ['unordered clip rows',d=>d.clips.Idle.directions=Object.fromEntries(Object.entries(d.clips.Idle.directions).reverse())],
 ['missing canonical frame',d=>d.clips.Walk.directions.S.frames.pop()],
 ['duplicate frame index',d=>d.clips.Walk.directions.S.frames[1].frameIndex=0],
 ['missing layer frame',d=>delete d.parts.hair.frames[Object.keys(d.parts.hair.frames)[0]]],
 ['invalid frame naming',d=>{const f=d.parts.hair.frames,k=Object.keys(f)[0];f.bad=f[k];delete f[k]}],
 ['canvas mismatch',d=>d.parts.hair.frames[Object.keys(d.parts.hair.frames)[0]].rect[2]=319],
 ['missing required layer',d=>delete d.slots.Hair],
 ['invalid root',d=>d.canvas.rootAnchorX=-1],
 ['root drift',d=>d.clips.Walk.directions.S.frames[1].sockets.root[0]++],
 ['invalid socket',d=>d.clips.Idle.directions.S.frames[0].sockets.hand_R=[Infinity,1]],
 ['missing socket',d=>delete d.clips.Idle.directions.S.frames[0].sockets.head],
 ['layer timing override',d=>d.parts.hair.durations=[1,2]],
 ['frame timing override',d=>d.parts.hair.frames[Object.keys(d.parts.hair.frames)[0]].frameDuration=1],
 ['invalid shared duration',d=>d.clips.Idle.durations[0]=0],
 ['missing atlas',d=>d.parts.hair.frames[Object.keys(d.parts.hair.frames)[0]].atlasId='absent'],
 ['out of atlas',d=>d.parts.hair.frames[Object.keys(d.parts.hair.frames)[0]].rect[0]=100000],
 ['duplicate draw slot',d=>d.drawOrder[1]=d.drawOrder[0]],
 ['mirroring',d=>d.mirroring='horizontal'],
 ['missing proof tag',d=>d.tags=[]],
 ['false approval',d=>d.source.status='APPROVED']
];
for(const [label,edit] of edits)test('validation rejects '+label,()=>{const d=clone();edit(d);assert.ok(api.validateDefinition(d).length);assert.throws(()=>api.compile(d))});
test('compiled metadata cannot be edited by a caller after validation',()=>{
 const d=clone(),c=api.compile(d);d.canvas.rootAnchorX=1;assert.equal(c.sample('Idle','S').canvas.rootAnchorX,160);
 assert.ok(Object.isFrozen(c.definition.parts.weapon.frames));assert.throws(()=>c.definition.clips.Idle.durations[0]=1);
});
test('additional sockets and split weapon slots extend the same contract',()=>{
 const d=clone();d.slots.WeaponBack='Weapon';d.defaultParts.WeaponBack='weapon-back';d.drawOrder.unshift('WeaponBack');
 const old=d.parts.weapon;d.parts['weapon-back']={slot:'WeaponBack',frames:Object.fromEntries(Object.entries(old.frames).map(([id,ref])=>[id.replace('_weapon_','_weapon-back_'),ref]))};
 for(const clip of Object.values(d.clips))for(const sequence of Object.values(clip.directions)){
  if(sequence.drawOrder)sequence.drawOrder.unshift('WeaponBack');for(const frame of sequence.frames){frame.sockets.weapon_tip=[160,100];if(frame.drawOrder)frame.drawOrder.unshift('WeaponBack')}
 }
 const c=api.compile(d),frame=c.sample('Idle','N');assert.equal(frame.layers.filter(l=>l.layer==='Weapon').length,2);assert.deepEqual(frame.sockets.weapon_tip,[160,100]);
});
function context(){const calls=[];return {calls,save(){calls.push(['save'])},restore(){calls.push(['restore'])},drawImage(...args){calls.push(['drawImage',...args])}}}
test('compositor draws every part with one stable root/scale and returns registered sockets',()=>{
 const frame=api.compile(sword).sample('Walk','SW',130),ctx=context(),images=Object.fromEntries(Object.keys(sword.atlases).map(id=>[id,{id}]));
 const sockets=api.draw(ctx,frame,images,{x:400,y:500,scale:.5}),draws=ctx.calls.filter(c=>c[0]==='drawImage');
 assert.equal(draws.length,6);for(const call of draws)assert.deepEqual(call.slice(-4),[320,368,160,160]);
 assert.deepEqual(sockets.root,{x:400,y:500});assert.deepEqual(sockets.hand_R,{x:320+frame.sockets.hand_R[0]*.5,y:368+frame.sockets.hand_R[1]*.5});
 const missing=context();delete images[frame.layers[3].atlasId];assert.throws(()=>api.draw(missing,frame,images));assert.equal(missing.calls.length,0);
});
test('existing player adapter keeps equipment and socket contracts, and modular visuals require opt-in',()=>{
 require('../animation.js');require('../character-renderer.js');require('../world-view.js');
 const ctx=context(),t={position:{x:2,y:3,z:0},facingDirection:{x:1,y:0},rotation:0,state:'idle',stateTime:0,speed:0},equipment={weapon:'existing item'};
 let legacy;window.AstraeonDirectionalArt={humanoid(...args){legacy=args[3];return {RightHand:[2,3,1.2]}}};
 // Shadows are suppressed inside the same Canvas assembly path used by WebGL actors.
 window.AstraeonSpatialView={assemblingActor:true};
 const iso=(x,y,z)=>({x:x*48-y*32,y:x*14+y*22-z});
 window.AstraeonAnimation.player(ctx,0,{state:'idle',started:0,duration:1},t,iso,0,equipment);
 assert.equal(legacy.equipment,equipment);assert.equal(legacy.modular,undefined);
 const modular={compiled:api.compile(sword),images:Object.fromEntries(Object.keys(sword.atlases).map(id=>[id,{}]))};
 assert.throws(()=>window.AstraeonAnimation.player(ctx,0,{state:'idle',started:0,duration:1},t,iso,0,equipment,modular),/not approved/);
 modular.allowDev=true;const result=window.AstraeonAnimation.player(ctx,0,{state:'idle',started:0,duration:1},t,iso,0,equipment,modular);
 assert.deepEqual(result.RightHand,[2,2.78,1.2]);assert.deepEqual(result.spriteSockets.root,iso(2,3,0));
 assert.throws(()=>api.drawHumanoid(ctx,iso,t,{modular,archetype:'mage'}),/class differs/);
});
test('atlas loading respects repository prefixes, preloads only selected clips and retries failures',async()=>{
 const original={fetch:global.fetch,Image:global.Image,document:global.document};
 const requests=[],failed=new Set();
 global.document={baseURI:'https://test.invalid/Astraeon-online/sprite-preview.html'};
 global.fetch=async()=>({ok:true,json:async()=>structuredClone(sword)});
 global.Image=class {
  set src(url){
   requests.push(url);const id=new URL(url).pathname.split('/').at(-1).replace('.png',''),atlas=sword.atlases[id];
   assert.ok(url.startsWith('https://test.invalid/Astraeon-online/assets/characters/'));
   this.naturalWidth=atlas.width;this.naturalHeight=atlas.height;
   queueMicrotask(()=>{if(id==='weapon-run'&&!failed.has(id)){failed.add(id);this.onerror()}else this.onload()});
  }
 };
 try{
  await assert.rejects(api.load('./assets/characters/swordsman-proof/sprite.json'),/DEV_ONLY/);assert.equal(requests.length,0);
  const visual=await api.load('./assets/characters/swordsman-proof/sprite.json',{allowDev:true});
  assert.equal(Object.keys(visual.images).length,7);assert.ok(Object.keys(visual.images).every(id=>id.endsWith('-idle')));
  await Promise.all([visual.ensure('Walk'),visual.ensure('Walk')]);assert.equal(requests.length,14);
  await assert.rejects(visual.ensure('Run'),/Cannot load atlas/);await visual.ensure('Run');
  assert.equal(Object.keys(visual.images).length,21);assert.equal(requests.filter(url=>url.endsWith('/weapon-run.png')).length,2);
 }finally{for(const [key,value] of Object.entries(original)){if(value===undefined)delete global[key];else global[key]=value}}
});
test('movement parts sample the existing gait, while all skill VFX can share SkillAction',()=>{
 const c=api.compile(mage),ctx=context(),images=Object.fromEntries(Object.keys(mage.atlases).map(id=>[id,{}]));
 window.AstraeonSpatialView={assemblingActor:true};require('../world-view.js');
 const t={position:{x:0,y:0,z:0},facingDirection:{x:1,y:0},rotation:0,state:'walk',stateTime:500,speed:1,gait:.5};
 const visual={compiled:c,images,allowDev:true};const iso=()=>({x:200,y:300});
 api.drawHumanoid(ctx,iso,t,{modular:visual,archetype:'mage'});assert.equal(window.AstraeonSpatialView.sampledPose.column,2);
 for(const effect of ['Fire','Ice']){api.drawHumanoid(ctx,iso,t,{modular:{...visual,effect},state:'cast',archetype:'mage',progress:.4});assert.equal(window.AstraeonSpatialView.sampledPose.column,1)}
});
