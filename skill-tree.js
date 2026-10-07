/* Pure learning transitions, persistent normalization and passive evaluation. */
(() => {
'use strict';
const content=window.AstraeonSkillDefinitions;
const freeze=window.AstraeonStats.freeze;
const validObject=value=>value&&typeof value==='object'&&!Array.isArray(value);
const fail=(code,detail={})=>freeze({ok:false,code,...detail});
function normalize(raw={}){
 const learnedSkills={},skillPointSpending={};
 if(validObject(raw.learnedSkills))for(const [id,rank] of Object.entries(raw.learnedSkills)){
  const d=content.getDefinition(id);
  if(d&&Number.isSafeInteger(rank)&&rank>0&&rank<=d.maxRank){
   learnedSkills[id]=rank;
   const spent=raw.skillPointSpending?.[id],ceiling=d.skillPointCostPerRank.slice(0,rank).reduce((a,b)=>a+b,0);
   // Imported ranks without a paid ledger are preserved but never mint refunds.
   skillPointSpending[id]=Number.isSafeInteger(spent)&&spent>=0&&spent<=ceiling?spent:0;
  }
 }
 return {learnedSkills,skillPointSpending};
}
function validate(state){
 if(!validObject(state))return false;
 if(!Number.isSafeInteger(state.skillPoints)||state.skillPoints<0||!Number.isSafeInteger(state.baseJobLevel)||state.baseJobLevel<1)return false;
 if(!validObject(state.learnedSkills)||!validObject(state.skillPointSpending))return false;
 for(const [id,rank] of Object.entries(state.learnedSkills)){
  const d=content.getDefinition(id),spent=state.skillPointSpending[id];
  if(!d||!Number.isSafeInteger(rank)||rank<1||rank>d.maxRank||!Number.isSafeInteger(spent)||spent<0||spent>d.skillPointCostPerRank.slice(0,rank).reduce((a,b)=>a+b,0))return false;
 }
 return Object.keys(state.skillPointSpending).every(id=>Object.hasOwn(state.learnedSkills,id));
}
function canLearnSkill(state,classId,id,mode='either'){
 if(!validate(state))return fail('INVALID_STATE');
 const d=content.getDefinition(id);if(!d)return fail('UNKNOWN_SKILL');
 if(d.classId!==classId)return fail('WRONG_CLASS');
 const rank=state.learnedSkills[id]||0;
 if(mode==='learn'&&rank)return fail('ALREADY_LEARNED');
 if(mode==='rank'&&!rank)return fail('NOT_LEARNED');
 if(rank>=d.maxRank)return fail('MAX_RANK');
 const cost=d.skillPointCostPerRank[rank],jobLevel=d.jobLevelRequirement[rank];
 if(!Number.isSafeInteger(cost)||cost<0||!Number.isSafeInteger(jobLevel)||jobLevel<1)return fail('INVALID_DEFINITION');
 if(state.baseJobLevel<jobLevel)return fail('JOB_LEVEL',{required:jobLevel});
 for(const prerequisite of d.prerequisites)if((state.learnedSkills[prerequisite.skillId]||0)<prerequisite.rank)return fail('PREREQUISITE',{prerequisite});
 if(state.skillPoints<cost)return fail('SKILL_POINTS',{required:cost});
 return freeze({ok:true,skillId:id,rank:rank+1,cost});
}
function learn(state,classId,id,mode){
 const result=canLearnSkill(state,classId,id,mode);if(!result.ok)return result;
 const spent=(state.skillPointSpending[id]||0)+result.cost;
 if(!Number.isSafeInteger(spent))return fail('INVALID_STATE');
 return freeze({...result,state:{...state,skillPoints:state.skillPoints-result.cost,
  learnedSkills:{...state.learnedSkills,[id]:result.rank},skillPointSpending:{...state.skillPointSpending,[id]:spent}}});
}
function canRefundSkill(state,id){
 if(!validate(state))return fail('INVALID_STATE');
 if(!content.getDefinition(id))return fail('UNKNOWN_SKILL');
 if(!state.learnedSkills[id])return fail('NOT_LEARNED');
 return freeze({ok:true,skillId:id,refund:state.skillPointSpending[id]});
}
function reset(state){
 if(!validate(state))return fail('INVALID_STATE');
 const refund=Object.values(state.skillPointSpending).reduce((a,b)=>a+b,0),balance=state.skillPoints+refund;
 if(!Number.isSafeInteger(balance))return fail('INVALID_STATE');
 return freeze({ok:true,refund,state:{...state,skillPoints:balance,learnedSkills:{},skillPointSpending:{}}});
}
function passiveModifiers(learned,classId){
 const modifiers=[];
 for(const id of Object.keys(learned).sort()){
  const d=content.getDefinition(id),rank=learned[id];if(!d||d.type!=='passive'||d.classId!==classId)continue;
  const modifier={id:`learned:${id}`};
  for(const [operation,values] of Object.entries(d.passivePerRank||{}))modifier[operation]=Object.fromEntries(Object.entries(values).map(([key,value])=>[key,value*rank]));
  modifiers.push(modifier);
 }
 return freeze(modifiers);
}
window.AstraeonSkillTree=freeze({normalize,validate,canLearnSkill,learn,canRefundSkill,reset,passiveModifiers});
})();
