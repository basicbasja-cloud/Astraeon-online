import {pathToFileURL} from 'node:url';
import path from 'node:path';
// Structural batch checks and deliberately invalid item fixtures. No art approval.
import {readFile,writeFile} from 'node:fs/promises';
const out=process.env.SPRITE_OUTPUT_ROOT ? pathToFileURL(path.resolve(process.env.SPRITE_OUTPUT_ROOT)+path.sep) : new URL('../../../../research/sprite-animation/silver-scarf/rig-proof-v4/',import.meta.url);
const manifest=JSON.parse(await readFile(new URL('rig-manifest.json',out),'utf8'));
const expected=['S','SE','E','NE','N','NW','W','SW'];
function validate(m){
 const errors=[];
 if(JSON.stringify(m.directions)!==JSON.stringify(expected))errors.push('direction-order');
 const c=m.clips.attack;
 if(c.keys!==8||c.frame_delays_ms.length!==8||c.frame_delays_ms.some(t=>!Number.isFinite(t)||t<=0)||c.frame_delays_ms.reduce((a,b)=>a+b,0)!==c.duration_ms)errors.push('timeline');
 for(const d of expected)for(let i=0;i<8;i++){
  const matches=m.poses.filter(p=>p.direction===d&&p.index===i);
  if(matches.length!==1)errors.push('pose-coverage');
  else if(matches[0].weapon_owner!=='anatomical_right'||matches[0].grip_error_world>1e-5)errors.push('hand-owner');
 }
 for(const [id,p]of Object.entries(m.parts)){
  if(!p.source_is_complete)errors.push('hidden-content:'+id);
  if(p.rig_family!==m.rig_family)errors.push('rig-family:'+id);
  if(p.is_mirrored!==false)errors.push('mirrored-asymmetry:'+id);
  if(JSON.stringify(p.directions)!==JSON.stringify(expected)||p.attack_keys!==8)errors.push('item-coverage:'+id);
  if(id.startsWith('weapon.')&&(p.attached_bones.length!==1||p.attached_bones[0]!=='weapon.right'))errors.push('weapon-socket:'+id);
 }
 for(const ids of Object.values(m.slots))for(const id of ids)if(id&&!m.parts[id])errors.push('unresolved-slot:'+id);
 if(!m.coverage_rules['headgear.helm']?.hides_slots.includes('hair'))errors.push('helmet-coverage');
 return errors;
}
const baseline=validate(manifest);if(baseline.length)throw Error(baseline.join('\n'));
const fixtures=[
 ['wrong-hand weapon',m=>m.parts['weapon.straight'].attached_bones=['left.hand'],'weapon-socket:weapon.straight'],
 ['missing diagonal hair',m=>m.parts['hair.silver'].directions=m.parts['hair.silver'].directions.filter(d=>d!=='NE'),'item-coverage:hair.silver'],
 ['incompatible body family',m=>m.parts['torso.travel'].rig_family='unrelated-proportions','rig-family:torso.travel'],
 ['mirrored asymmetrical weapon',m=>m.parts['weapon.falchion'].is_mirrored=true,'mirrored-asymmetry:weapon.falchion'],
 ['incomplete hidden head',m=>m.parts['head.base'].source_is_complete=false,'hidden-content:head.base'],
 ['missing pose key',m=>m.poses.pop(),'pose-coverage']
];
const rejected=[];for(const [name,mutate,expectedError]of fixtures){const m=structuredClone(manifest);mutate(m);const errors=validate(m);if(!errors.includes(expectedError))throw Error('Fixture escaped: '+name);rejected.push({fixture:name,expected_error:expectedError,rejected:true})}
let count=0;for(const part of Object.keys(manifest.parts))for(const d of expected)for(const suffix of ['.png','.depth.png']){
 const bytes=await readFile(new URL(`strips/${part}/${d}${suffix}`,out));
 if(!bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))||bytes.readUInt32BE(16)!==2048||bytes.readUInt32BE(20)!==256)throw Error('Invalid strip '+part+d+suffix);
 count++;
}
const report={baseline:'PASS',strips_checked:count,negative_fixtures:rejected,scope:'Manifest coverage and actual strip PNG headers. Source hierarchy/weights/baked keys are independently checked by check-source.py. No visual or game acceptance implied.'};
await writeFile(new URL('contract-check.json',out),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));
