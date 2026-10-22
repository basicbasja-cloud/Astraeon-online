'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const P=require('../patch001-characters.js');
global.AstraeonPatch001Characters=P;
const W=require('../wardrobe.js');
function definition(index,body){const c=P.classFor(index),character=P.characterFor(index,body);return {characterId:character.id,classId:c.name,bodyVariant:body,canvas:{...P.policy.anatomy,referenceHeight:88},mirroring:'none',layerMode:'visible-cutout',clips:Object.fromEntries(Object.entries(c.actions).map(([id,a])=>[id,{durations:Array(a.frames).fill(50),loop:a.loop,authoredDirections:a.directions,directionMap:a.directionMap}]))}}
test('patch names map to existing gameplay IDs without changing combat class IDs',()=>{
 assert.deepEqual([0,12,3].map(W.classId),['swordsman','mage','archer']);assert.equal(W.classId(4),null);
 assert.equal(P.actionClip(3,'thorn-snare'),'TrapPlace');assert.equal(P.actionClip(3,'arrow-rain'),'ArrowRain');assert.equal(P.actionClip(0,'jade-tempest'),'SpinAttack');assert.equal(W.actionClip('attack',12),'BasicAttack');
});
test('all six class/body packages have distinct identities and the shared padded canvas',()=>{
 const ids=new Set();for(const index of [0,12,3])for(const body of ['male','female']){const d=definition(index,body);ids.add(d.characterId);assert.deepEqual(P.validatePackage(d,index,body),[]);assert.equal(d.canvas.frameWidth,240);assert.equal(d.canvas.rootAnchorY,172)}assert.equal(ids.size,6);
 assert.equal(P.characterFor(3,'other'),null);assert.ok(Object.isFrozen(P.policy.classes[3].actions.BasicAttack.directions));
});
test('complete class-specific action requirements do not require another class mobility',()=>{
 assert.ok(W.clipsFor(3).includes('TrapPlace'));assert.ok(W.clipsFor(0).includes('SpinAttack'));assert.ok(W.clipsFor(12).includes('Blink'));assert.ok(!W.clipsFor(12).includes('Dash'));assert.ok(!W.clipsFor(3).includes('Blink'));
});
test('package gate rejects missing motion, wrong sex, old canvas and wrong real directions',()=>{
 for(const edit of [d=>delete d.clips.Walk,d=>d.bodyVariant='female',d=>d.canvas.frameWidth=160,d=>d.clips.BasicAttack.authoredDirections=P.policy.classes[3].actions.Walk.directions,d=>d.clips.CastChannel.directionMap={S:'S'},d=>d.clips.Run.tags=['PENDING_PRODUCTION']]){const d=definition(3,'male');edit(d);assert.ok(P.validatePackage(d,3,'male').length)}
});
test('wardrobe loads the factory package and requests whole-head and whole-costume cosmetics',async()=>{
 const calls=[];global.AstraeonModularSprites={load:async(url,options)=>{calls.push({url,options});const match=Object.entries(P.policy.characters).find(([,v])=>v.definition===url);const [name,body]=match[0].split('/'),index=Object.keys(P.policy.classes).find(i=>P.classFor(i).id===name);return {compiled:{definition:definition(index,body)}}}};
 for(const index of [0,12,3])for(const bodyVariant of ['male','female'])await W.load({...W.defaults(),bodyVariant},index,['Idle']);
 assert.equal(calls.length,6);for(const call of calls){assert.match(call.url,/-patch001\/sprite.json$/);assert.ok(call.options.cosmeticLoadout.HeadHair);assert.ok(call.options.cosmeticLoadout.BodyCostume);assert.equal(call.options.cosmeticLoadout.Hair,undefined)}
});
test('a complete-looking metadata object with missing action remains rejected',async()=>{
 global.AstraeonModularSprites={load:async()=>{const d=definition(3,'male');delete d.clips.ArrowRain;return {compiled:{definition:d}}}};await assert.rejects(W.load(W.defaults(),3),/Missing animation ArrowRain/);
});

test('actual skill1..skill4 hotbar definitions resolve by semantic skill ID',()=>{
 global.window=global;require('../combat.js');
 assert.equal(W.actionClip('skill4',0,AstraeonCombat.definitions.warrior.skill4),'SpinAttack');
 assert.equal(W.actionClip('skill2',3,AstraeonCombat.definitions.ranger.skill2),'TrapPlace');
 assert.equal(W.actionClip('skill4',3,AstraeonCombat.definitions.ranger.skill4),'ArrowRain');
 assert.equal(W.actionClip('attack',12,AstraeonCombat.definitions.mage.attack),'BasicAttack');
});
test('class-specific projectile clips align their declared release event to gameplay impact',async()=>{
 const d=definition(3,'male');d.clips.ArrowRain.events=[{name:'projectileRelease',phase:.25,timeMs:200,frameIndex:4}];
 const visual={compiled:{definition:d,sample:()=>({layers:[]}),duration:id=>d.clips[id].durations.reduce((a,b)=>a+b,0)},images:{},appearance:{},ensure:async()=>{},keepAnimations:()=>{}};
 global.AstraeonModularSprites={load:async()=>visual};await W.select(W.defaults(),3);
 const anim={state:'cast',clipId:'ArrowRain',started:0,duration:1,until:1,impactAt:.5};
 assert.equal(W.visualFor(3,anim,{},.5).elapsedMs,200);assert.equal(W.visualFor(3,anim,{},.75).elapsedMs,500);
});
