/* Verify decorative facade depth fits existing occupied ground; plants root outside it. */
const fs=require('fs'),assert=require('assert/strict');
global.window={};require('../navigation.js');require('../world/v3/spatial.js');
const before=JSON.parse(fs.readFileSync(process.argv[2]));
const source=JSON.parse(fs.readFileSync('world/v3/wayfarer-spatial.json'));
const withGoods=structuredClone(before);
const newColliders=source.objects.flatMap(o=>o.parts.filter(p=>p.id.startsWith('goods69-')&&p.role==='solid').map(p=>({owner:o.id,part:p})));
for(const {owner,part} of newColliders)withGoods.objects.find(o=>o.id===owner).parts.push(part);
const addedFloors=source.terrain.surfaces.filter(s=>s.id.startsWith('lot69-')||s.id.startsWith('roadrim69-'));
withGoods.terrain.surfaces.push(...addedFloors);
const old=window.AstraeonSpatialV3.compile(before),expected=window.AstraeonSpatialV3.compile(withGoods),world=window.AstraeonSpatialV3.compile(source);
const bodyHeight=70*(92/76)/35;
let unexpectedBlockedChanges=0,unexpectedElevationChanges=0;
let samples=0,blockedChanges=0,elevationChanges=0,vertices=0,parts=0;
const violations=[];
for(let y=.125;y<128;y+=.25)for(let x=.125;x<112;x+=.25){
 samples++;
 unexpectedBlockedChanges+=expected.blocked(x,y)!==world.blocked(x,y);
 blockedChanges+=old.blocked(x,y)!==world.blocked(x,y);
 unexpectedElevationChanges+=Math.abs(expected.elevationAt(x,y)-world.elevationAt(x,y))>1e-5;
 elevationChanges+=Math.abs(old.elevationAt(x,y)-world.elevationAt(x,y))>1e-5;
}
for(const p of world.parts){
 if(!['ro3-v69-','life69-','goods69-','wing69-','roof69-','lot69-'].some(prefix=>p.id.startsWith(prefix))||p.visible===false||['grass','vergeGroundcover','vergeGroundcoverShade'].includes(p.material))continue;
 let low=false;
 for(const v of p.vertices){
  if(v[2]-world.elevationAt(v[0],v[1])>=bodyHeight)continue;
  vertices++;low=true;
  if(!world.blocked(v[0],v[1]))violations.push({id:p.id,vertex:v});
 }
 parts+=low;
}
for(const key of ['navigation','spawn','route','districts','safeSpawn'])assert.deepEqual(source[key],before[key],key);
for(const o of before.objects){
 const current=source.objects.find(p=>p.id===o.id);assert(current,o.id);
 for(const key of ['services','presentation','lights','portals','walkers'])assert.deepEqual(current[key],o[key],o.id+'/'+key);
 // Every original solid remains at exactly its saved vertices and role.
 for(const p of o.parts.filter(p=>p.role==='solid')){
  const currentPart=current.parts.find(q=>q.id===p.id);assert(currentPart,p.id);
  assert.deepEqual(currentPart.vertices,p.vertices,p.id+'/collision');
  assert.equal(currentPart.role,'solid');
 }
}
const report={sourcePass:69,baseline:'source68',bodyHeight,samples,blockedChanges,unexpectedBlockedChanges,elevationChanges,unexpectedElevationChanges,newHouseFloorSurfaces:addedFloors.filter(s=>s.id.startsWith('lot69-')).length,newRoadCurbSurfaces:addedFloors.filter(s=>s.id.startsWith('roadrim69-')).length,newFloorSurfaces:addedFloors.length,newGroundColliders:newColliders.length,
 checkedLowFacadeParts:parts,checkedLowFacadeVertices:vertices,violations,
 preserved:['all original solid vertices','services','actors','lights','portals','walkers','navigation','spawn','route','districts','safeSpawn'],
 plantContactCheck:'native Blender check-ro3-street-v69.py'};
fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
assert.equal(unexpectedBlockedChanges,0);assert.equal(unexpectedElevationChanges,0);
assert(!violations.length,JSON.stringify(violations.slice(0,12)));
console.log('PASS source69 contact, explicit accessory collision and preserved actors/routes');
