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
