const {test}=require('node:test'),assert=require('node:assert/strict');
global.window={};require('../character-motion.js');require('../world/v3/locomotion.js');
const painted=require('../world/v3/warrior-painted-locomotion.json');
window.AstraeonLocomotionV3.configurePainted(painted);
const {Locomotion,profiles}=window.AstraeonLocomotionV3;
for(const rate of [30,60,120])for(const from of ['walk','run','sprint'])for(const to of ['walk','run','sprint'])if(from!==to){
 test(`${from}→${to} queues at a contact and conserves displacement at ${rate}Hz`,()=>{
  const t=new Locomotion(0,0,0);t.setStrategy(from);t.tick(0,0,1/rate);
  for(let i=0;i<12;i++)t.tick(t.position.x+profiles[from].speed/rate,0,1/rate);
  const initial=t.gait,contact=Math.floor(initial*2+1)/2,oldDistance=(contact-initial)*profiles[from].cycleDistance;
  t.setStrategy(to);assert.equal(t.activeStrategy,from);let travel=0;
  while(t.activeStrategy===from){const d=profiles[to].speed/rate;travel+=d;t.tick(t.position.x+d,0,1/rate);assert(travel<10)}
  const event=t.snapshot().strategyTransition;assert.equal(event.reason,'contact');assert.equal(event.from,from);assert.equal(event.to,to);
  assert(Math.abs(event.gait-contact)<1e-9);assert(Math.abs(t.gait-(contact+(travel-oldDistance)/profiles[to].cycleDistance))<1e-9);
  const root=t.position.x;for(let i=0;i<rate;i++)t.tick(t.position.x+profiles[to].speed/rate,0,1/rate);
  assert(Math.abs(t.position.x-root-profiles[to].speed)<1e-9);
 });
}
test('a cancelled request keeps the active gait; stationary requests apply on the next tick',()=>{
 const t=new Locomotion();t.tick(0,0,.016);t.tick(.01,0,.016);t.tick(.02,0,.016);
 const phase=t.gait;t.setStrategy('sprint');t.setStrategy('walk');t.tick(.03,0,.016);
 assert.equal(t.activeStrategy,'walk');assert(Math.abs(t.gait-phase-.01/profiles.walk.cycleDistance)<1e-9);
 t.tick(.03,0,.016);t.setStrategy('run');assert.equal(t.activeStrategy,'walk');t.tick(.03,0,.016);
 assert.equal(t.activeStrategy,'run');assert.equal(t.snapshot().strategyTransition.reason,'stationary');
 assert.equal(typeof t.snapshot().stateTime,'number');assert.equal(typeof t.snapshot().transition,'number');
});
