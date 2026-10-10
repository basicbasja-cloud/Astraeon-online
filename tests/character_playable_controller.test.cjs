'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const A=require('../character-assembly.js'),P=require('../character-playable-controller.js');
const motion=JSON.parse(fs.readFileSync('authoring/characters/motion-templates/assembly-debug/motion-template.json'));
const pack=JSON.parse(fs.readFileSync('authoring/characters/appearance/debug-blue/appearance-pack.json'));
const compiled=A.compileAssembly(motion,pack);
test('movement selects all eight directions at equal speed',()=>{
 for(const [x,y,d]of [[0,1,'S'],[-1,1,'SW'],[-1,0,'W'],[-1,-1,'NW'],[0,-1,'N'],[1,-1,'NE'],[1,0,'E'],[1,1,'SE']]){
  const p=P.create(compiled,{x:0,y:0});p.setMove(x,y);p.advance(1000);const s=p.snapshot();
  assert.equal(s.action,'Walk');assert.equal(s.direction,d);assert.ok(Math.abs(Math.hypot(s.x,s.y)-120)<1e-8);
  p.setMove(0,0);p.advance(10);assert.equal(p.snapshot().action,'Idle');
 }
});
test('attack locks facing and translation then carries remaining time into locomotion',()=>{
 const p=P.create(compiled,{x:0,y:0});p.attack();p.setMove(1,0);p.advance(50);
 assert.equal(p.snapshot().x,0);assert.equal(p.snapshot().direction,'S');assert.equal(p.attack(),false);
 const duration=compiled.motion.duration('BasicAttack','S');p.advance(duration-50+100);
 const s=p.snapshot();assert.equal(s.action,'Walk');assert.equal(s.direction,'E');assert.equal(s.x,12);
 assert.equal(s.elapsedMs,100);assert.equal(s.cosmeticTimeMs,duration+100);
});
test('appearance swaps preserve movement, attack frame and both clocks',()=>{
 const p=P.create(compiled);p.attack();p.advance(123);const before=p.snapshot(),frame=p.sample().frameIndex;
 const alternatives=Object.entries(pack.parts).filter(([,part])=>part.slot==='Hair');
 for(const [id]of alternatives){p.setAppearance({Hair:id});const after=p.snapshot();
  for(const key of ['x','y','action','direction','attacking','elapsedMs','cosmeticTimeMs'])assert.equal(after[key],before[key]);
  assert.equal(p.sample().frameIndex,frame);
 }
});
test('attack finishes at exact boundary and invalid inputs do not mutate clocks',()=>{
 const p=P.create(compiled);p.attack();p.advance(compiled.motion.duration('BasicAttack','S'));
 assert.equal(p.snapshot().action,'Idle');assert.equal(p.snapshot().elapsedMs,0);
 const before=p.snapshot();for(const dt of [-1,NaN,Infinity])assert.throws(()=>p.advance(dt));
 assert.deepEqual(p.snapshot(),before);assert.throws(()=>p.setMove(NaN,0));
});
test('incomplete neutral study cannot masquerade as playable',()=>{
 assert.throws(()=>P.create({motion:{template:{actions:{Idle:{}}}}}),/requires Walk/);
});
