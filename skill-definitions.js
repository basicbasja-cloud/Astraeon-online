/* Base-tree content. Recommended, tunable defaults; runtime payloads stay in combat.js. */
(() => {
'use strict';
const freeze=value=>{if(value&&typeof value==='object'){Object.values(value).forEach(freeze);Object.freeze(value)}return value};
const definitions={};
function define(id,classId,name,type,options={}){
 const definition={id,classId,name,key:`skill.${id}`,type,maxRank:5,
  jobLevelRequirement:[1,3,5,7,9],skillPointCostPerRank:[2,2,2,2,2],prerequisites:[],
  loadoutAssignable:type==='active',runtimeSkillId:type==='active'?id:null,
  compatibleNodeReference:type==='active'?id:null,tags:[classId,type],metadata:{tier:'base',balance:'provisional'},
  ...options};
 if(definitions[id])throw Error('Duplicate skill ID');definitions[id]=freeze(definition);
}
for(const [classId,skills] of Object.entries({
 swordsman:[['rising-edge','Rising Edge'],['iron-guard','Iron Guard'],['second-wind','Second Wind'],['jade-tempest','Jade Tempest']],
 mage:[['ember-bloom','Ember Bloom'],['frost-ward','Frost Ward'],['aether-mend','Aether Mend'],['tempest','Tempest']]
})){
 skills.forEach(([id,name],index)=>define(id,classId,name,'active',{
  jobLevelRequirement:[1+index*2,3+index*2,5+index*2,7+index*2,9+index*2],
  skillPointCostPerRank:index===0?[1,2,2,2,2]:[2,2,2,2,2],
  prerequisites:index===3?[{skillId:skills[0][0],rank:3}]:[],
  runtimeRank:{damagePerRank:.1},metadata:{tier:'base',balance:'provisional',legacyArchetype:classId==='swordsman'?'warrior':'mage',legacySlot:`skill${index+1}`}
 }));
}
define('sword-mastery','swordsman','Sword Mastery','passive',{passivePerRank:{add:{physicalATK:2}}});
define('swordsman-vitality','swordsman','Frontline Vitality','passive',{
 jobLevelRequirement:[3,5,7,9,11],prerequisites:[{skillId:'sword-mastery',rank:2}],passivePerRank:{multiply:{maxHP:.02}}
});
define('arcane-mastery','mage','Arcane Mastery','passive',{passivePerRank:{add:{magicATK:2,maxSP:3}}});
define('focused-casting','mage','Focused Casting','passive',{
 jobLevelRequirement:[3,5,7,9,11],prerequisites:[{skillId:'arcane-mastery',rank:2}],passivePerRank:{add:{castTimeModifier:-.02}}
});
const trees={};
for(const classId of ['swordsman','mage']){
 const skillIds=Object.values(definitions).filter(d=>d.classId===classId).map(d=>d.id);
 trees[classId]={id:`base-${classId}`,classId,tier:'base',skillIds,
  edges:skillIds.flatMap(id=>definitions[id].prerequisites.map(p=>({from:p.skillId,to:id,rank:p.rank}))),metadata:{balance:'provisional'}};
}
// Legacy class indices are an adapter, never an assumption in the tree algorithms.
function classIdFor(raw){return raw.cls===0?'swordsman':raw.cls===12?'mage':null}
window.AstraeonSkillDefinitions=freeze({definitions,trees,classIdFor});
})();
