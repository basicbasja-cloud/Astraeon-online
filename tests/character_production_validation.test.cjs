'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const V=require('../character-production-validation.js');
const layer=()=>({layer:'MainHand',pivot:[10,10],transform:{x:50,y:60,rotation:Math.PI/2,scale:2},weaponPoseFrame:{equipmentAnchor:[10,10],gripContactPoint:[10,15],weaponTip:[10,-30],handContactPoint:[40,60],perspectiveVariant:'edge'}});
test('visible grip is transformed independently of the equipment pivot',()=>{
 const result=V.inspectGrip({layers:[layer()]},.001);
 assert.deepEqual(result.equipment,[50,60]);assert.deepEqual(result.grip,[40,60]);
 assert.ok(Math.abs(result.tip[0]-130)<1e-9);assert.equal(result.status,'GEOMETRY_WITHIN_TOLERANCE');assert.equal(result.visualApproval,false);
});
test('misplaced painted-hand annotation fails even when equipment root is registered',()=>{
 const l=layer();l.weaponPoseFrame.handContactPoint=[50,60];const r=V.inspectGrip({layers:[l]});assert.equal(r.status,'INVALID');assert.equal(r.distancePixels,10);
});
test('missing metadata never silently counts as a valid grip',()=>{
 assert.equal(V.inspectGrip({layers:[]}).status,'NOT_EQUIPPED');
 assert.equal(V.inspectGrip({layers:[{layer:'MainHand'}]}).status,'UNMEASURED');
 const l=layer();l.weaponPoseFrame.weaponTip=[NaN,0];assert.equal(V.inspectGrip({layers:[l]}).status,'INVALID');
 assert.throws(()=>V.inspectGrip({layers:[]},NaN));
});

test('independently authored socket and grip may occupy the same pixel',()=>{
 const l=layer();l.weaponPoseFrame.gripContactPoint=[10,10];l.weaponPoseFrame.handContactPoint=[50,60];
 const r=V.inspectGrip({layers:[l]});
 assert.equal(r.status,'GEOMETRY_WITHIN_TOLERANCE');assert.equal(r.visualApproval,false);
});
test('large tip jumps produce review diagnostics without editing source frames',()=>{
 const source=[layer(),layer()];source[1].transform.x+=100;
 const assembly={motion:{template:{actions:{BasicAttack:{directions:{S:{frames:[{durationMs:50},{durationMs:50}]}}}}}},sample:(a,d,t,o)=>({layers:[source[o.frameIndex]]})};
 const before=structuredClone(source),r=V.auditSequence(assembly,'BasicAttack','S');
 assert.equal(r.warnings.length,1);assert.deepEqual(source,before);assert.equal(r.visualApproval,false);
});
