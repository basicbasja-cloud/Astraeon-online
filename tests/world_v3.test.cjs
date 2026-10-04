const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
global.window={};for(const file of ['world-view.js','navigation.js','character-motion.js','world/v3/spatial.js','world/v3/locomotion.js'])require('../'+file);
const source=JSON.parse(fs.readFileSync(path.join(__dirname,'../world/v3/golden-proof.json'))),manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'../world/v3/warrior-animation.json'))),spatial=window.AstraeonSpatialV3;
window.AstraeonLocomotionV3.configure(manifest);
test('Warrior fall transition covers all eight reactions before the death fade',()=>{
 const transition=manifest.reactions.fallTransition,directions=['S','SE','E','NE','N','NW','W','SW'];
 assert(transition);assert(transition.blendStart>0);assert(transition.blendStart<transition.motionEnd);assert(transition.motionEnd<transition.blendEnd);assert(transition.blendEnd<.65);
 assert.deepEqual(transition.profiles.map(p=>p.direction),directions);for(const p of transition.profiles){assert(Number.isFinite(p.rotationDegrees));assert(p.scale.every(n=>Number.isFinite(n)&&n>0));assert(p.offset.every(Number.isFinite))}
});
test('gate collision contains pillars, not overhead span or passage',()=>{const w=spatial.compile(source);assert(w.blocked(2.6,10));assert(w.blocked(5.4,10));for(let y=8;y<=12;y+=.05)assert(!w.blocked(4,y));assert(w.route({x:4,y:12.2},{x:4,y:8}));});
test('authored route and entrances are reachable with actor clearance',()=>{const w=spatial.compile(source);let start={x:source.spawn[0],y:source.spawn[1]};for(const stop of source.route){const goal={x:stop.position[0],y:stop.position[1]},route=w.route(start,goal);assert(route,'unreachable '+stop.name);for(const waypoint of route)assert(!w.blocked(waypoint.x,waypoint.y));start=goal}for(const p of w.portals)assert(!w.blocked(...p.approach.slice(0,2)));});
test('one edited mesh moves visuals, collision, navigation and shadow together',()=>{const before=spatial.compile(source),changed=structuredClone(source),pillar=changed.objects.find(o=>o.id==='west-gate').parts.find(p=>p.id==='west-pillar');pillar.vertices.forEach(v=>v[0]-=1);const after=spatial.compile(changed);assert(before.blocked(2.6,10));assert(!after.blocked(2.6,10));assert(after.blocked(1.6,10));assert.notDeepEqual(after.shadowPolygons.find(p=>p.id===pillar.id),before.shadowPolygons.find(p=>p.id===pillar.id));assert.notDeepEqual(after.navCells,before.navCells);assert.deepEqual(after.parts.find(p=>p.id===pillar.id).vertices,pillar.vertices);});
test('roof/canopy are selective layers and remain independent shadow casters',()=>{const w=spatial.compile(source);for(const id of ['hall-roof','canopy','open-span']){assert(w.overheads.some(p=>p.id===id));assert(w.shadowPolygons.some(p=>p.id===id));assert(!w.solids.some(p=>p.id===id))}assert(w.solids.some(p=>p.id==='hall-body'));assert(w.solids.some(p=>p.id==='trunk'));});
test('shared schema rejects invalid/duplicate mesh identifiers and invalid indices',()=>{for(const edit of [s=>s.objects.push(s.objects[0]),s=>s.objects[0].parts[0].vertices[0][0]=NaN,s=>s.objects[0].parts[0].faces[0][0]=999]){const s=structuredClone(source);edit(s);assert.throws(()=>spatial.compile(s))}});
test('baked lighting must align with every face corner and contain bounded factors',()=>{
 const s=structuredClone(source),p=s.objects[0].parts[0];p.bakedLighting=p.faces.map(f=>f.map(()=>[.8,1]));assert.doesNotThrow(()=>spatial.validate(s));
 for(const edit of [p=>p.bakedLighting.pop(),p=>p.bakedLighting[0].pop(),p=>p.bakedLighting[0][0][1]=NaN,p=>p.bakedLighting[0][0][0]=1.1]){
  const broken=structuredClone(s);edit(broken.objects[0].parts[0]);assert.throws(()=>spatial.validate(broken),/Invalid baked lighting/);
 }
});
for(const mode of ['walk','run','sprint']){
 test(mode+' simulation displacement, duty and foot metadata agree in all eight directions',()=>{const p=manifest.clips[mode];for(let row=0;row<8;row++){const angle=row*Math.PI/4,t=new window.AstraeonLocomotionV3.Locomotion(0,0,angle);t.setStrategy(mode);t.tick(0,0,.01);for(let tick=0;tick<240;tick++){const old=structuredClone(t.feet),gait=t.gait,d=.008*p.speed;t.tick(t.position.x+Math.cos(angle)*d,t.position.y+Math.sin(angle)*d,.008,{sprint:mode==='sprint'});assert(Math.abs(t.gait-gait-d/p.cycleDistance)<1e-8);for(let i=0;i<2;i++){const foot=t.feet[i];assert.equal(foot.swing,foot.phase>=p.duty);if(old[i]&&!old[i].swing&&!foot.swing){assert.equal(foot.x,old[i].x);assert.equal(foot.y,old[i].y)}assert(foot.z>=0)}}for(let col=0;col<8;col++){const frame=p.frames[row*8+col];assert.equal(frame.contacts[0].stance,(col/8)%1<p.duty);assert.equal(frame.contacts[1].stance,(col/8+.5)%1<p.duty);assert(frame.durationMs>0);assert.equal(frame.footAnchorY,204);assert.deepEqual(frame.contacts.map(c=>c.leg),['left','right'])}}});
}
test('three locomotion strategies have separate atlas geometry, stride and duty',()=>{const clips=Object.values(manifest.clips);for(const key of ['atlas','cycleDistance','duty','bodyPitch'])assert.equal(new Set(clips.map(c=>c[key])).size,3);for(const c of clips){assert(fs.existsSync(path.join(__dirname,'../'+c.atlas)));assert(c.frames.some(f=>f.events.includes('left-contact')));assert(c.frames.some(f=>f.events.includes('right-contact')))}assert.notDeepEqual(clips[0].frames[2].contacts,clips[1].frames[2].contacts)});
test('simulation contact metadata cancels root travel at the gameplay projection and scale',()=>{for(const p of Object.values(manifest.clips))for(let row=0;row<8;row++){const angle=Math.PI/2-row*Math.PI/4,heading=window.AstraeonView.inverse(Math.cos(angle),Math.sin(angle)),length=Math.hypot(heading.x,heading.y),root=window.AstraeonView.project(heading.x/length*p.cycleDistance/8,heading.y/length*p.cycleDistance/8),a=p.frames[row*8].contacts[0].foot,b=p.frames[row*8+1].contacts[0].foot;assert(Math.abs((b[0]-a[0])*.5+root.x)<1e-8);assert(Math.abs((b[1]-a[1])*.5+root.y)<1e-8)}});
test('start, stop, turn and strategy changes settle without teleports',()=>{const t=new window.AstraeonLocomotionV3.Locomotion(4,12);t.tick(4,12,.01);t.tick(4,11.98,.016);assert.equal(t.state,'start');t.setStrategy('sprint');for(let i=0;i<90;i++)t.tick(4,t.position.y-.02,.016,{sprint:true});assert.equal(t.activeStrategy,'sprint');t.tick(4,t.position.y,.016);assert.equal(t.state,'stop');t.face(1,0);for(let i=0;i<80;i++)t.tick(4,t.position.y,.016);assert.equal(t.state,'idle');assert(t.feet.every(f=>!f.swing&&f.z<.001));assert(Math.abs(t.rotation)<.001)});
test('default Golden import derives services, patrols, masks and polygons from the authored town',()=>{
 require('../world-content.js');require('../world/v3/town-import.js');const data=require('../world/v3/wayfarer-court.json'),content=window.AstraeonTownImportV3.content(data,window.AstraeonContent),w=content.nativeWorld.spatial;
 assert.equal(content.nativeWorld.layoutId,'wayfarer-golden-v1');assert.equal(content.services.length,6);assert.equal(content.walkers.length,3);assert.equal(content.transitions.length,2);
 for(const service of content.services)assert(!w.blocked(service.x,service.y),service.id);
 for(const walker of content.walkers)for(let i=0;i<walker.route.length;i++){const a=walker.route[i],b=walker.route[(i+1)%walker.route.length];assert(window.AstraeonNavigation.clear({x:a[0],y:a[1]},{x:b[0],y:b[1]},w.blocked),walker.id)}
 assert(!w.blocked(6.95,22));assert(w.blocked(5.7,22.6));assert(w.blocked(8.6,21.7));assert(Object.values(content.structures).some(s=>s.layers.some(l=>l.visibility==='selective-overhead')));
});
test('off-grid movement destinations remain reachable around an obstacle',()=>{
 const w=spatial.compile(require('../world/v3/wayfarer-court.json')),start={x:28.82,y:22.83},goal={x:33.75,y:30.25},route=window.AstraeonNavigation.route(start,goal,w.blocked,{bounds:w.bounds,reach:.3});assert(route);assert.deepEqual(route.at(-1),goal);let previous=start;for(const point of route){assert(window.AstraeonNavigation.clear(previous,point,w.blocked));previous=point}
});
test('stationary turns replant one foot while retaining the other support',()=>{
 const t=new window.AstraeonLocomotionV3.Locomotion(20,24,0);t.tick(20,24,.016);t.face(0,1);let planted=0;
 for(let i=0;i<80;i++){const before=t.snapshot();t.tick(20,24,.016);assert(t.feet.filter(f=>f.swing).length<=1);for(let j=0;j<2;j++)if(before.feet[j]&&!before.feet[j].swing&&!t.feet[j].swing){assert.equal(before.feet[j].x,t.feet[j].x);assert.equal(before.feet[j].y,t.feet[j].y);planted++}}
 assert(planted>60);assert(t.feet.every(f=>!f.swing&&f.z===0));
});
test('spatial town routes, water boundaries, stairs and mesh-owned services agree',()=>{
 require('../world-content.js');require('../world/v3/town-import.js');const data=require('../world/v3/wayfarer-spatial.json'),content=window.AstraeonTownImportV3.content(data,window.AstraeonContent),w=content.nativeWorld.spatial;
 let start={x:data.spawn[0],y:data.spawn[1]};for(const stop of data.route){const goal={x:stop.position[0],y:stop.position[1]},path=w.route(start,goal);assert(path,stop.name);for(const point of path)assert(!w.blocked(point.x,point.y));start=goal}
 assert(w.blocked(2,25),'Water must not be walkable');const arrival=data.route.find(p=>p.name==='Arrival').position,avenue=data.route.find(p=>p.name==='South avenue').position;
 assert(window.AstraeonNavigation.clear({x:arrival[0],y:arrival[1]},{x:avenue[0],y:avenue[1]},w.blocked),'Gate passage must remain open');
 const hall=data.objects.find(o=>o.id==='guild-hall').portals[0];assert(Math.abs(w.elevationAt(...hall.approach)-hall.approach[2])<.001,'Hall terrace contacts must match the authored entrance');
 assert.equal(content.services.length,8);const board=content.services.find(s=>s.kind==='journal');assert.equal(board.objectId,'guild-board');for(const service of content.services)assert(!w.blocked(service.x,service.y),service.id);
});
test('stance feet retain their absolute planted elevation while climbing',()=>{
 const groundAt=(x,y)=>x*.2,t=new window.AstraeonLocomotionV3.Locomotion(0,0,0);t.tick(0,0,.016,{groundAt,elevation:0});let grounded=0;
 for(let i=0;i<160;i++){const before=t.snapshot();const x=t.position.x+.02;t.tick(x,0,.016,{groundAt,elevation:groundAt(x,0)});for(let j=0;j<2;j++)if(!before.feet[j].swing&&!t.feet[j].swing){assert.equal(t.feet[j].groundZ,before.feet[j].groundZ);assert.equal(t.feet[j].x,before.feet[j].x);grounded++}}
 assert(grounded>100);assert(t.position.z>.5);assert(t.feet.some(f=>f.groundZ>.4));
});
test('town stair contacts meet the visible tread tops and the shrine entry',()=>{
 const data=require('../world/v3/wayfarer-spatial.json'),w=spatial.compile(data);
 for(const [id,prefix,count] of [['guild-hall','civic-processional-step-',4],['moon-shrine','shrine-step-',3]]){
  const object=data.objects.find(o=>o.id===id);
  for(let j=0;j<count;j++){
   const step=object.parts.find(p=>p.id===prefix+j),xs=step.vertices.map(v=>v[0]),ys=step.vertices.map(v=>v[1]),height=Math.max(...step.vertices.map(v=>v[2]));
   const x=(Math.min(...xs)+Math.max(...xs))/2,y=(Math.min(...ys)+Math.max(...ys))/2;
   assert(!w.blocked(x,y),'tread must be approachable '+step.id);
   assert(Math.abs(w.elevationAt(x,y)-height)<.00001,'feet sink into '+step.id);
  }
 }
 const shrine=data.objects.find(o=>o.id==='moon-shrine'),entry=shrine.portals.find(p=>p.id==='moon-shrine-entrance'),door=shrine.parts.find(p=>p.id==='moon-shrine-door');
 assert(Math.abs(entry.anchor[0]-door.vertices.reduce((sum,v)=>sum+v[0],0)/door.vertices.length)<.00001,'main approach must face its actual door');
 assert(Math.abs(entry.anchor[2]-w.elevationAt(...entry.anchor))<.00001,'entry height must agree with its tread');
});
