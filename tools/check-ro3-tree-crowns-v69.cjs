/* Compare the native tree volume step to its exact preceding source checkpoint. */
const fs=require('fs'),assert=require('assert/strict');
const before=JSON.parse(fs.readFileSync(process.argv[2])),after=JSON.parse(fs.readFileSync('world/v3/wayfarer-spatial.json'));
assert.deepEqual(after.terrain,before.terrain,'tree work must preserve native floor');
let layers=0,crowns=0,preserved=0;
for(const old of before.objects){
 const current=after.objects.find(o=>o.id===old.id);assert(current);
 const {parts:oldParts,...oldData}=old,{parts:currentParts,...currentData}=current;assert.deepEqual(currentData,oldData);
 for(const p of oldParts){
  const q=currentParts.find(v=>v.id===p.id);assert(q);
  if(old.family!=='vegetation'||p.material!=='foliageCutout'){assert.deepEqual(q,p,p.id);preserved++;continue;}
  assert.equal(q.vertices.length,25);assert.equal(q.faces.length,16);assert.equal(q.role,p.role);assert.equal(q.shadow,p.shadow);assert.equal(q.material,p.material);
  assert(q.uvs.flat().every(v=>v.every(x=>x>=0&&x<=1)));layers++;
 }
 const foliage=oldParts.filter(p=>p.material==='foliageCutout'&&p.visible!==false).flatMap(p=>p.vertices);
 for(const p of currentParts.filter(p=>p.id.startsWith('tree69-'))){
  assert.equal(p.material,'foliageCutout');assert.equal(p.role,'overhead');assert.equal(p.shadow,true);assert.equal(p.vertices.length,25);assert.equal(p.faces.length,16);
  for(const v of p.vertices)for(let i=0;i<3;i++)assert(v[i]>=Math.min(...foliage.map(v=>v[i]))-.35&&v[i]<=Math.max(...foliage.map(v=>v[i]))+.35,p.id+'/crown extent');crowns++;
 }
}
assert(layers>100&&crowns>50);
const report={sourcePass:69,curvedLeafLayers:layers,roundedLeafTops:crowns,preservedParts:preserved,terrainAndOriginalRootsBranchesBuildingsPreserved:true};fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log('PASS native tree volume and retained source contacts',report);
