const test=require('node:test'),assert=require('node:assert/strict');
global.window={};require('../navigation.js');require('../world/v3/spatial.js');
const scene=require('../world/v3/wayfarer-spatial.json'),world=window.AstraeonSpatialV3.compile(scene);
test('expanded town supports long trips between opposite districts and arrival',()=>{
 const services=scene.objects.flatMap(o=>o.services||[]);
 const shrine=services.find(s=>s.kind==='shrine').position,inn=services.find(s=>s.kind==='inn').position;
 for(const [a,b] of [[shrine,scene.spawn],[inn,shrine],[scene.spawn,scene.route.find(r=>r.name==='Hall').position]]){
  const path=world.route({x:a[0],y:a[1]},{x:b[0],y:b[1]});assert(path,'cross-town route');let before={x:a[0],y:a[1]};
  for(const p of path){assert(window.AstraeonNavigation.clear(before,p,world.blocked),'route segment crosses a physical solid');before=p}
 }
});
test('nearby collision/elevation queries agree with exact full geometry scans',()=>{
 const bounds=scene.terrain.bounds,r=scene.navigation.actorRadius;
 const onLand=(x,y)=>[scene.terrain.walkablePolygon,...scene.terrain.surfaces.filter(s=>s.walkable).map(s=>s.polygon)].some(p=>window.AstraeonSpatialV3.pointIn({x,y},p));
 for(let i=0;i<360;i++){
  const x=((i*31.13)%bounds.maxX),y=((i*17.73)%bounds.maxY);
  const exact=x<bounds.minX+r||x>bounds.maxX-r||y<bounds.minY+r||y>bounds.maxY-r||!onLand(x,y)||world.solids.some(p=>window.AstraeonSpatialV3.touches({x,y},p.footprint,r));
  assert.equal(world.blocked(x,y),exact,`broad phase at ${x},${y}`);
 }
});

function overlaps(a,b){
 for(const p of [a,b])for(let i=0;i<p.length;i++){
  const q=p[(i+1)%p.length],n=[q[1]-p[i][1],p[i][0]-q[0]],aa=a.map(v=>v[0]*n[0]+v[1]*n[1]),bb=b.map(v=>v[0]*n[0]+v[1]*n[1]);
  if(Math.min(...aa)>=Math.max(...bb)-.01||Math.min(...bb)>=Math.max(...aa)-.01)return false;
 }return true;
}
test('full-width streets and individually owned frontage lots remain free of building intersections',()=>{
 const lots=scene.objects.filter(o=>o.id.startsWith('frontage-')||o.family==='residential'||['east-inn','artisan-workshop','guild-hall','moon-shrine'].includes(o.id));
 const bodies=o=>o.parts.filter(p=>p.role==='solid'&&p.visible!==false&&Math.max(...p.vertices.map(v=>v[2]))>2).map(p=>window.AstraeonSpatialV3.hull(p.vertices.map(v=>v.slice(0,2))));
 for(let i=0;i<lots.length;i++)for(let j=i+1;j<lots.length;j++)assert(!bodies(lots[i]).some(a=>bodies(lots[j]).some(b=>overlaps(a,b))),lots[i].id+' / '+lots[j].id);
 for(const road of scene.terrain.surfaces.filter(s=>s.centerline))for(const lot of lots)assert(!bodies(lot).some(p=>overlaps(road.polygon,p)),road.id+' / '+lot.id);
});
test('every ambient patrol segment, including its closing leg, clears exact scene geometry',()=>{
 for(const actor of scene.objects.flatMap(o=>o.walkers||[]))for(let i=0;i<actor.route.length;i++){
  const a=actor.route[i],b=actor.route[(i+1)%actor.route.length];
  assert(window.AstraeonNavigation.clear({x:a[0],y:a[1]},{x:b[0],y:b[1]},world.blocked),actor.id+' / '+i);
 }
});
test('raised civic precinct has physical boundaries and three usable tread flights',()=>{
 assert(world.elevationAt(54,33)>1.4);assert(world.elevationAt(54,40)<.1);
 assert(world.blocked(38,35),'retaining edge needs a physical barrier');
 for(const [x,top,bottom] of [[54,35,39.3],[26.3,35,38.7],[74,33.3,37]]){
  let previous=world.elevationAt(x,bottom);
  for(let y=bottom;y>=top-.1;y-=.08){assert(!world.blocked(x,y),'stair axis must stay clear');const h=world.elevationAt(x,y);assert(h>=previous-.01&&h-previous<.21,'tread contact must rise by one step');previous=h}
  assert(previous>1.4);assert(world.route({x,y:bottom},{x,y:top-1}));
 }
});
test('visible river bank has no open seams above the waterline',()=>{
 const parts=scene.objects.flatMap(o=>o.parts).filter(p=>p.id.startsWith('bank-v49-')&&p.visible!==false);
 assert(parts.length>100,'continuous bank must be present');
 const water=scene.terrain.surfaces.find(s=>s.role==='water'),waterZ=water.vertices[0][2],edges=new Map();
 const key=v=>v.map(n=>n.toFixed(4)).join('/');
 for(const p of parts){
  assert(Math.min(...p.vertices.map(v=>v[2]))<waterZ,'rock feet must extend below water');
  for(const f of p.faces)for(let i=0;i<f.length;i++){
   const a=p.vertices[f[i]],b=p.vertices[f[(i+1)%f.length]],k=[key(a),key(b)].sort().join('|');
   const e=edges.get(k)||{count:0,a,b};e.count++;edges.set(k,e);
  }
 }
 for(const e of edges.values()){
  assert(e.count<=2,'bank must not overlap itself');
  if(e.count===1)assert(e.a[2]<waterZ&&e.b[2]<waterZ||Math.abs(e.a[2])<.001&&Math.abs(e.b[2])<.001,'open edge inside exposed cliff face');
 }
});

test('merchant court entrances climb their actual floor without crossing retaining solids',()=>{
 assert(world.elevationAt(82,58)>.7);assert(world.elevationAt(70,59)<.1);
 assert(world.blocked(73,63),'retaining edge must prevent a sideways height jump');
 for(const [a,b] of [[[70.4,59],[74,59]],[[70.4,67],[74,67]],[[88.5,52.4],[88.5,56]],[[79,81.6],[79,78]]]){
  let height=world.elevationAt(...a);
  for(let i=1;i<=48;i++){
   const x=a[0]+(b[0]-a[0])*i/48,y=a[1]+(b[1]-a[1])*i/48,h=world.elevationAt(x,y);
   assert(!world.blocked(x,y),'market approach must be walkable: '+[x,y]);
   assert(h>=height-.01&&h-height<.15,'market tread must rise by at most one step');height=h;
  }
  assert(height>.7);assert(world.route({x:a[0],y:a[1]},{x:b[0],y:b[1]}));
 }
 for(const id of ['market-spices','market-textiles','market-supplies','food-market']){
  const counter=scene.objects.find(o=>o.id===id).parts.find(p=>p.id===id+'-counter');
  const center=counter.vertices.reduce((a,v)=>[a[0]+v[0]/counter.vertices.length,a[1]+v[1]/counter.vertices.length],[0,0]);
  assert(Math.abs(Math.min(...counter.vertices.map(v=>v[2]))+.045-world.elevationAt(...center))<.01,id+' counter must follow its court floor');
 }
});
