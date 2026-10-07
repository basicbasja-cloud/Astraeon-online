/* Pure configuration transitions. Learning, Nodes and combat belong to their owners. */
(() => {
'use strict';
const slotCount=8,content=window.AstraeonSkillDefinitions;
const freeze=value=>{if(value&&typeof value==='object'){Object.values(value).forEach(freeze);Object.freeze(value)}return value};
const validSlot=slot=>Number.isSafeInteger(slot)&&slot>=0&&slot<slotCount;
const fail=(code,detail={})=>freeze({ok:false,code,...detail});
function normalize(raw){
 const seen=new Set();return freeze(Array.from({length:slotCount},(_,slot)=>{
  const id=Array.isArray(raw)?raw[slot]:null,d=content.getDefinition(id);
  if(!d||d.type!=='active'||!d.loadoutAssignable||seen.has(id))return null;
  seen.add(id);return id;
 }));
}
function valid(loadout){if(!Array.isArray(loadout)||loadout.length!==slotCount)return false;const canonical=normalize(loadout);return Array.from({length:slotCount},(_,slot)=>Object.hasOwn(loadout,slot)&&loadout[slot]===canonical[slot]).every(Boolean)}
function getSlot(loadout,slot){return validSlot(slot)&&valid(loadout)?loadout[slot]:null}
function canAssignSkill(loadout,character,classId,slot,id){
 if(!validSlot(slot))return fail('INVALID_SLOT');
 if(!valid(loadout)||!window.AstraeonSkillTree.validate(character))return fail('INVALID_STATE');
 if(id===null)return freeze({ok:true,slot,skillId:null});
 const d=content.getDefinition(id);if(!d)return fail('UNKNOWN_SKILL');
 if(d.type!=='active'||!d.loadoutAssignable)return fail('NOT_ASSIGNABLE');
 if(d.classId!==classId)return fail('WRONG_CLASS');
 if(!(character.learnedSkills[id]>0))return fail('NOT_LEARNED');
 if(loadout.some((value,index)=>index!==slot&&value===id))return fail('ALREADY_ASSIGNED');
 return freeze({ok:true,slot,skillId:id});
}
function transition(loadout,next,detail={}){return freeze({ok:true,changed:next.some((id,slot)=>id!==loadout[slot]),loadout:next,...detail})}
function assignSkill(loadout,character,classId,slot,id){const check=canAssignSkill(loadout,character,classId,slot,id);return check.ok?transition(loadout,loadout.map((v,index)=>index===slot?id:v),{slot,skillId:id}):check}
function clearSlot(loadout,character,classId,slot){return assignSkill(loadout,character,classId,slot,null)}
function swapSlots(loadout,a,b){
 if(!validSlot(a)||!validSlot(b))return fail('INVALID_SLOT');if(!valid(loadout))return fail('INVALID_STATE');
 const next=[...loadout];[next[a],next[b]]=[next[b],next[a]];return transition(loadout,next,{from:a,to:b});
}
function moveSkill(loadout,from,to){
 if(!validSlot(from)||!validSlot(to))return fail('INVALID_SLOT');if(!valid(loadout))return fail('INVALID_STATE');
 if(loadout[from]===null)return fail('EMPTY_SLOT');if(from!==to&&loadout[to]!==null)return fail('TARGET_OCCUPIED');
 return swapSlots(loadout,from,to);
}
window.AstraeonActionLoadout=freeze({slotCount,validSlot,normalize,valid,getSlot,canAssignSkill,assignSkill,clearSlot,swapSlots,moveSkill});
})();
