/* Runtime bridge: learned rank + existing authored action + one compatible Node. */
(() => {
'use strict';
const content=window.AstraeonSkillDefinitions;
const slotCount=window.AstraeonActionLoadout.slotCount;
function normalizeLoadout(raw){
 return window.AstraeonActionLoadout.normalize(raw);
}
function canUseSkill(learned,classId,id){const d=content.getDefinition(id);return !!(d&&d.classId===classId&&d.type==='active'&&(learned[id]||0)>0)}
function compile(id,rank,node=null,combo=1){
 const d=content.getDefinition(id);if(!d||d.type!=='active'||!Number.isSafeInteger(rank)||rank<1||rank>d.maxRank)return null;
 const result=window.AstraeonCombat.compile(d.metadata.legacyArchetype,d.metadata.legacySlot,combo,node);
 if(!result)return null;
 return {...result,learnedSkillId:id,learnedRank:rank,damage:result.damage*(1+(rank-1)*(d.runtimeRank?.damagePerRank||0))};
}
window.AstraeonSkillRuntime=Object.freeze({slotCount,normalizeLoadout,canUseSkill,compile});
})();
