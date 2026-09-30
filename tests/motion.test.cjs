const test=require('node:test');
const assert=require('node:assert/strict');
global.window={};
require('../character-motion.js');require('../combat.js');
const {CharacterTransform,wrap,cameraMovement,FacingMode}=window.AstraeonMotion;
const {contains,Timeline,compile}=window.AstraeonCombat;
const inverse=(x,y)=>({x:(31*x+10*y)/1558,y:(48*y-7*x)/1558});
for(const degrees of [0,17,45,90,135,180,225,247,270,315,359]){
 const angle=degrees*Math.PI/180,dir={x:Math.cos(angle),y:Math.sin(angle)};
 test(`world heading ${degrees}° converges with bounded rotation and forward hit geometry`,()=>{
  const t=new CharacterTransform(0,0);let x=0,y=0;
  for(let i=0;i<180;i++){x+=dir.x/60;y+=dir.y/60;const before=t.rotation;t.tick(x,y,1/60);assert.ok(Math.abs(wrap(t.rotation-before))<=9/60+1e-8)}
  assert.ok(Math.abs(wrap(t.rotation-angle))<.01);
  assert.ok(Math.abs(t.distance-3)<1e-8);
  const def=compile('warrior','attack');
  assert.ok(contains(def,t.position,dir,{x:x+dir.x*2,y:y+dir.y*2}));
  assert.ok(!contains(def,t.position,dir,{x:x-dir.x*2,y:y-dir.y*2}));
 });
 test(`dodge/attack-independent aim ${degrees}°`,()=>{
  const t=new CharacterTransform();t.face(dir.x,dir.y,FacingMode.Aim);
  for(let i=0;i<180;i++)t.tick(i/120,0,1/60,{archetype:'ranger',action:'attack'});
  assert.ok(Math.abs(wrap(t.rotation-angle))<.01);assert.equal(t.mode,FacingMode.Aim);
 });
}
test('camera-relative input preserves arbitrary angles, diagonal normalization and analog speed',()=>{
 for(const angle of [0,.3,.7,1.4,2.7,4.2,6.2])for(const magnitude of [.15,.4,1]){
  const x=Math.cos(angle)*magnitude,y=Math.sin(angle)*magnitude,v=cameraMovement(x,y,inverse);
  assert.ok(Math.abs(Math.hypot(v.x,v.y)-magnitude)<1e-9);
  const screen={x:v.x*48-v.y*10,y:v.x*7+v.y*31};
  assert.ok(Math.abs(wrap(Math.atan2(screen.y,screen.x)-angle))<1e-9);
 }
 assert.equal(cameraMovement(.04,.02,inverse).magnitude,0);
 assert.ok(Math.abs(Math.hypot(...Object.values(cameraMovement(1,1,inverse)).slice(0,2))-1)<1e-9);
});
test('stance feet remain planted in world space while the root moves',()=>{
 const t=new CharacterTransform(0,0,0);let contacts=0,swings=0;
 for(let i=0;i<240;i++){
  const before=t.snapshot();t.tick((i+1)*2/60,0,1/60);
  for(let j=0;j<2;j++){const a=before.feet[j],b=t.feet[j];if(a&&!a.swing&&!b.swing){assert.equal(a.x,b.x);assert.equal(a.y,b.y);contacts++}if(b.swing&&b.z>0)swings++}
 }
 assert.ok(contacts>100);assert.ok(swings>100);
});
test('teleport resets contacts without inventing movement; elevation is separate',()=>{
 const t=new CharacterTransform(0,0);t.tick(20,10,1/60,{elevation:1});assert.equal(t.speed,0);assert.equal(t.distance,0);assert.deepEqual(t.position,{x:20,y:10,z:1});
});
test('turning uses the shortest path across 359° / 0°',()=>{
 const t=new CharacterTransform(0,0,359*Math.PI/180);t.face(1,0);
 t.tick(0,0,1/60);assert.ok(t.angularVelocity>0);
 for(let i=0;i<60;i++)t.tick(0,0,1/60);
 assert.ok(Math.abs(wrap(t.rotation))<1e-5);
});
test('movement distance and gait are independent of update rate',()=>{
 const results=[30,60,120].map(rate=>{const t=new CharacterTransform(0,0,0);for(let i=0;i<rate*2;i++)t.tick((i+1)*3/rate,0,1/rate);return t});
 for(const t of results){assert.ok(Math.abs(t.distance-6)<1e-8);assert.ok(Math.abs(t.gait-6/.95)<1e-8)}
});
test('projectile collision uses swept travel and respects facing',()=>{
 const timeline=new Timeline(),def=compile('ranger','attack'),target={x:3,y:0,hp:10};assert.ok(timeline.start(def,{x:0,y:0},{x:1,y:0},0));
 const events=timeline.tick(.3,.3,[target]);assert.ok(events.some(e=>e.type==='release'));assert.ok(events.some(e=>e.target===target));
});
require('../dungeon.js');
const dungeon=window.AstraeonDungeon;
test('authored dungeon rooms unlock through contiguous traversable passages',()=>{
 assert.equal(dungeon.rooms.length,4);
 const paths=[[[8,20],[8,11]],[[8,9],[21,9]],[[21,9],[21,20]]];
 for(let wave=0;wave<3;wave++){
  const next=dungeon.rooms[wave+1].start;
  assert.ok(dungeon.blocked(...next,wave),'sealed next room must be inaccessible');
  const [a,b]=paths[wave];
  for(let step=0;step<=100;step++){const t=step/100,x=a[0]+(b[0]-a[0])*t,y=a[1]+(b[1]-a[1])*t;assert.ok(!dungeon.blocked(x,y,wave+1),`blocked passage at ${x},${y}`)}
 }
 assert.ok(dungeon.blocked(3,20,0),'wall collision');assert.ok(dungeon.blocked(14,20,3),'outside rooms');
});
require('../enemy-combat.js');
const threats=window.AstraeonEnemyCombat;
test('boss sweep excludes the rear, charge lanes exclude safe flanks, and seals lock their target',()=>{
 const entity={x:0,y:0,boss:true,pattern:0,phase:0},target={x:4,y:0};
 const sweep=threats.plan(entity,target,10);assert.ok(threats.contains(sweep,{x:2,y:0}));assert.ok(!threats.contains(sweep,{x:-1,y:0}));assert.ok(!threats.contains(sweep,{x:0,y:3}));
 entity.pattern=1;const charge=threats.plan(entity,target,10);assert.ok(charge.charge);assert.ok(threats.contains(charge,{x:4,y:0}));assert.ok(!threats.contains(charge,{x:4,y:2}));assert.ok(!threats.contains(charge,{x:7,y:0}));
 entity.pattern=2;const seal=threats.plan(entity,target,10);target.x=10;assert.equal(seal.x,4);assert.ok(seal.field);assert.ok(threats.contains(seal,{x:4,y:0}));assert.ok(!threats.contains(seal,{x:10,y:0}));
});
test('swept hostile travel catches contact between frames and misses a dodge beside the lane',()=>{
 assert.equal(threats.distanceToSegment({x:5,y:0},{x:0,y:0},{x:10,y:0}),0);assert.equal(threats.distanceToSegment({x:5,y:2},{x:0,y:0},{x:10,y:0}),2);
});
require('../exploration.js');
test('supply discoveries award once and remain claimed after save reload',()=>{
 const state={gold:10,inventory:{potion:0,shard:0},journal:[]},entry={id:'test-chest',kind:'chest',name:'Pilgrim chest'};
 assert.ok(window.AstraeonExploration.claim(entry,state).ok);assert.equal(state.gold,22);assert.equal(state.inventory.potion,1);
 const reloaded=JSON.parse(JSON.stringify(state));assert.ok(!window.AstraeonExploration.claim(entry,reloaded).ok);assert.equal(reloaded.gold,22);
});
require('../save-state.js');
test('legacy saves retain progression and class IDs while missing fields gain safe defaults',()=>{
 const legacy={name:'Returning hero',cls:20,gold:200,inventory:{ore:9},equipment:{weapon:'Astral Blade'},chapters:[0,1],discovered:[0,1,3],futureProgress:{relics:8}};
 const state=window.AstraeonSave.normalize(legacy);assert.equal(state.cls,20);assert.equal(state.inventory.ore,9);assert.equal(state.inventory.potion,0);assert.deepEqual(state.chapters,[0,1]);assert.deepEqual(state.futureProgress,{relics:8});assert.equal(state.equipment.weapon,'Astral Blade');assert.equal(state.equipment.armor,'Adventurer Garb');assert.equal(state.saveVersion,2);assert.deepEqual(window.AstraeonSave.normalize(JSON.parse(JSON.stringify(state))),state);
});
test('malformed save values cannot create invalid HUD indices, resources or coordinates',()=>{
 const state=window.AstraeonSave.normalize({name:'Hero',cls:90,race:-8,lv:-2,inventory:{ore:-5},hp:Infinity,maxHp:NaN,x:NaN,y:100,quest:{id:80},mail:[{},'letter']});assert.equal(state.cls,21);assert.equal(state.race,0);assert.equal(state.lv,1);assert.equal(state.inventory.ore,0);assert.equal(state.hp,100);assert.equal(state.x,14.5);assert.equal(state.y,25);assert.equal(state.quest,null);assert.deepEqual(state.mail,['letter']);assert.equal(window.AstraeonSave.normalize([]),null);
});
require('../navigation.js');
test('click navigation routes through authored passages without crossing walls or cutting corners',()=>{
 const start={x:8,y:22},goal={x:21,y:9},blocked=(x,y)=>dungeon.blocked(x,y,2),path=window.AstraeonNavigation.route(start,goal,blocked);assert.ok(path);let previous=start;
 for(const point of path){assert.ok(window.AstraeonNavigation.clear(previous,point,blocked));previous=point}assert.ok(Math.hypot(previous.x-goal.x,previous.y-goal.y)<.33);
 assert.equal(window.AstraeonNavigation.route(start,{x:21,y:20},(x,y)=>dungeon.blocked(x,y,0)),null);
});
test('click navigation can approach a sealed gate within the interaction radius',()=>{
 for(let wave=0;wave<3;wave++){const room=dungeon.rooms[wave],path=window.AstraeonNavigation.route({x:room.start[0],y:room.start[1]},room.door,(x,y)=>dungeon.blocked(x,y,wave),{reach:2.2});assert.ok(path);const end=path.at(-1);assert.ok(Math.hypot(end.x-room.door.x,end.y-room.door.y)<=2.225)}
});
test('player projectiles stop at walls before damaging a target behind them',()=>{
 const timeline=new Timeline(),def=compile('ranger','attack'),target={x:3,y:0,hp:10};timeline.start(def,{x:0,y:0},{x:3,y:0},0);const events=timeline.tick(.3,.3,[target],(x,y)=>x>=1.4&&x<=1.8);assert.ok(events.some(e=>e.type==='blocked'));assert.ok(!events.some(e=>e.target===target));assert.equal(timeline.projectiles.length,0);
});

test('projectile muzzle offset cannot skip a thin adjacent wall',()=>{
 const timeline=new Timeline(),def=compile('ranger','attack');timeline.start(def,{x:0,y:0},{x:3,y:0},0);const events=timeline.tick(.3,.3,[{x:1,y:0,hp:10}],x=>x>=.15&&x<=.35);assert.ok(events.some(e=>e.type==='blocked'));assert.ok(!events.some(e=>e.type==='projectileHit'));assert.equal(timeline.projectiles.length,0);
});
