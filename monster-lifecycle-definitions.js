/* Mechanical lifecycle data. All coefficients are prototype / NON-FINAL. */
(() => {
'use strict';
const freeze=window.AstraeonItemDefinitions.freeze;
const legacySpecies=[
 {name:'Leafmane Fox',speed:1.3,reach:1.4,windup:.55,radius:1.25,hp:.8},
 {name:'Mossback Boar',speed:.85,reach:2.1,windup:.9,radius:1.65,hp:1.4},
 {name:'Amber Beetle',speed:.55,reach:1.5,windup:.7,radius:1.3,hp:1.05},
 {name:'Caravan Outlaw',speed:.8,reach:5,windup:.85,radius:1.1,hp:1},
 {name:'Sporeling',speed:.65,reach:3.8,windup:1,radius:1.5,hp:1},
 {name:'Lanternwood Spirit',speed:.75,reach:4.6,windup:.8,radius:1.3,hp:1.1},
 {name:'Moonstone Sentinel',speed:.5,reach:2.2,windup:1.15,radius:2,hp:1.65},
 {name:'Veil Serpent',speed:1.5,reach:1.6,windup:.65,radius:1.35,hp:.9}
];
const make=(id,rewardDefinitionId,{hpBase=32,hpPerLevel=4,hpScale=1,speed=1,detect=8,attackRange=1.8,windup=.55,cadence=2.8,respawn=12}={})=>({
 id,rewardDefinitionId,stats:{hpBase,hpPerLevel,hpScale},movement:{speed,returnSpeed:speed,homeTolerance:.15},
 perception:{detectRange:detect},combat:{attackRange,windup,cadence,initialDelay:1.8},
 lifecycle:{leashRange:12,respawnDelay:respawn,returnHP:'retain'},tags:['prototype'],metadata:{balance:'non-final'}
});
const definitions={};
legacySpecies.forEach((s,i)=>{const id=window.AstraeonMonsterDefinitions.speciesIds[i];definitions[id]=make(id,id,{hpScale:s.hp,speed:s.speed,attackRange:i===1?4.8:s.reach+.4,windup:window.AstraeonEnemyCombat.normal[i].duration})});
definitions['moonveil-guardian']=make('moonveil-guardian','moonveil-guardian',{hpBase:270,hpPerLevel:25,speed:.7,attackRange:6.6,windup:.9,cadence:2.4});
definitions['arena-sparring']=make('arena-sparring','arena-sparring');
const fixtureIds=['lifecycle-normal-a','lifecycle-normal-b','lifecycle-normal-c','lifecycle-tough-a'];
definitions[fixtureIds[0]]=make(fixtureIds[0],'proof-material',{hpBase:20,hpPerLevel:0,speed:1,detect:6,attackRange:1.5,windup:.5,cadence:2,respawn:4});
definitions[fixtureIds[1]]=make(fixtureIds[1],'proof-consumable',{hpBase:24,hpPerLevel:0,speed:1.2,detect:7,attackRange:1.8,windup:.6,cadence:2.4,respawn:5});
definitions[fixtureIds[2]]=make(fixtureIds[2],'proof-none',{hpBase:28,hpPerLevel:0,speed:.8,detect:5,attackRange:2,windup:.7,cadence:2.8,respawn:6});
definitions[fixtureIds[3]]=make(fixtureIds[3],'proof-equipment',{hpBase:60,hpPerLevel:0,speed:.7,detect:8,attackRange:2.2,windup:.9,cadence:3,respawn:8});
for(const id of fixtureIds)definitions[id].metadata.fixture=true;
freeze(definitions);freeze(legacySpecies);
function validate(value){
 const fail=path=>freeze({ok:false,code:'INVALID_MONSTER_DEFINITION',path});
 try{
  if(!value||typeof value!=='object'||typeof value.id!=='string'||!value.id.trim())return fail('id');
  if(!window.AstraeonMonsterDefinitions.getDefinition(value.rewardDefinitionId))return fail('rewardDefinitionId');
  const groups={stats:['hpBase','hpPerLevel','hpScale'],movement:['speed','returnSpeed','homeTolerance'],perception:['detectRange'],combat:['attackRange','windup','cadence','initialDelay'],lifecycle:['leashRange','respawnDelay']};
  for(const [group,keys] of Object.entries(groups))for(const key of keys){const n=value[group]?.[key];if(!Number.isFinite(n)||n<0)return fail(`${group}.${key}`)}
  if(value.stats.hpBase<=0||value.stats.hpScale<=0||value.combat.cadence<=0||value.movement.homeTolerance<=0||value.lifecycle.leashRange<value.combat.attackRange||value.lifecycle.returnHP!=='retain')return fail('policy');
  // Reuse the authored plain-data validator; do not accept runtime functions/cycles.
  const json=window.AstraeonLootResolution.validate({id:'lifecycle-validation',entries:[],metadata:value});
  return json.ok?freeze({ok:true,definition:freeze(structuredClone(value))}):fail('metadata');
 }catch{return fail('definition')}
}
function maxHP(definition,level=1,scale=1){const checked=validate(definition);if(!checked.ok||!Number.isFinite(level)||level<1||!Number.isFinite(scale)||scale<=0)return freeze({ok:false,code:'INVALID_MONSTER_STATS'});const s=definition.stats,hp=(s.hpBase+s.hpPerLevel*level)*s.hpScale*scale;return Number.isFinite(hp)&&hp>0?freeze({ok:true,maxHP:hp}):freeze({ok:false,code:'INVALID_MONSTER_STATS'})}
// Temporary bounded coexistence of the existing replacement population and
// per-life respawns. No approved final spawn density is expressed here.
const population=freeze({initialCount:7,maxActors:8,maxAlive:8,replacementThreshold:7,replacementInterval:12});
window.AstraeonMonsterLifecycleDefinitions=freeze({definitions,legacySpecies,fixtureIds,population,validate,maxHP,getDefinition:id=>Object.hasOwn(definitions,id)?definitions[id]:null});
})();
