/* Original plaza activity, using real existing collision and ordinary routes. */
const fs=require('fs'),crypto=require('crypto');global.window={};require('../navigation.js');require('../world/v3/spatial.js');
const manifest=JSON.parse(fs.readFileSync('world/v3/world-manifest.json')),zone=JSON.parse(fs.readFileSync(manifest.zones[manifest.defaultZone].url));
const source=JSON.parse(fs.readFileSync(zone.semantics.url)),spatial=window.AstraeonSpatialV3.compile(source);
const hash=crypto.createHash('sha256').update(fs.readFileSync('world/v3/wayfarer-spatial.json')).digest('hex');
if(hash!==zone.sourceSHA256)throw Error('Rebuild current city transport before planning activity');
const before=source.objects.flatMap(o=>o.walkers||[]),prefix='capital-plaza-life-';
if(before.some(a=>a.id.startsWith(prefix)))throw Error('Activity already exists');
const proposals=[
 ['south-watch','warrior','guild',0,.34,[[122,156],[125,157],[125,160],[122,159]]],
 ['north-watch','warrior','guild',14,.36,[[125,132],[129,130],[132,132],[128,133]]],
 ['herbalist-visitor','mage','market',76,.28,[[121,152],[122,153],[123,155],[121.8,155]]],
 ['academy-pilgrim','mage','shrine',235,.31,[[132,155],[134,157],[135,156],[134,154]]],
 ['market-courier','ranger','craft',118,.45,[[136,141],[137,138],[140,144],[137,146]]],
 ['inn-patron','ranger','inn',45,.30,[[120,142],[121,144],[120,146],[119,144]]],
 ['square-traveller','ranger','travel',184,.40,[[129,158],[129,162],[130,164],[131,160]]],
 ['archive-messenger','mage','guild',206,.38,[[132,127],[134,129],[134,133],[133,130]]]
];
let checked=0;const walkers=[];
for(const [role,archetype,kind,tint,pace,stops] of proposals){
 const route=[];for(let i=0;i<stops.length;i++){
  const p=stops[i],q=stops[(i+1)%stops.length];
  if(spatial.blocked(...p,.28)||spatial.blocked(...q,.28))throw Error('Blocked activity stop '+role+'/'+JSON.stringify([p,q]));
  const leg=window.AstraeonNavigation.route({x:p[0],y:p[1]},{x:q[0],y:q[1]},(x,y)=>spatial.blocked(x,y,.28),{bounds:spatial.bounds,reach:.05,step:.5});
  if(!leg)throw Error('Unreachable activity leg '+role);
  route.push(p,...leg.slice(0,-1).map(a=>[a.x,a.y]));
 }
 for(let i=0;i<route.length;i++){
  const p=route[i],q=route[(i+1)%route.length],steps=Math.max(1,Math.ceil(Math.hypot(q[0]-p[0],q[1]-p[1])/.1));
  for(let j=0;j<=steps;j++){const x=p[0]+(q[0]-p[0])*j/steps,y=p[1]+(q[1]-p[1])*j/steps;
   if(spatial.blocked(x,y,.28)||!spatial.containsGround(x,y))throw Error('Unsafe planned activity '+role);checked++;
  }
 }
 walkers.push({id:prefix+role,archetype,kind,tint,pace,route});
}
const plan={beforeSourceSHA256:hash,owner:'astral-fountain',beforeWalkerCount:before.length,afterWalkerCount:before.length+walkers.length,
 walkers,checkedPathSamples:checked,actorRadius:.28,existingActorArtwork:['warrior','mage','ranger'],additionalImages:0,
 purpose:'Local royal watch, visitors and couriers around the plaza and its frontages; original activity for Wayfarer, not copied NPC identities.',
 existingActorsUnchanged:true,additionalGameplayObstacles:0,additionalStaticTriangles:0};
fs.writeFileSync('docs/review/wayfarer-capital-v76/property-frontages/plaza-life-plan.json',JSON.stringify(plan,null,2)+'\n');
console.log(JSON.stringify({...plan,walkers:walkers.map(a=>({id:a.id,waypoints:a.route.length}))},null,2));
