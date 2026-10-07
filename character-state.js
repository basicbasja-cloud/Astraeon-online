/* Authoritative progression/stat/resource state is private to this controller. */
(() => {
'use strict';
const p=window.AstraeonProgression,stats=window.AstraeonStats;
const progressionKeys=['baseLevel','baseExp','baseJobLevel','baseJobExp','statPoints','skillPoints'];
const sane=(value,fallback,min=0,max=Number.MAX_SAFE_INTEGER)=>Number.isFinite(value)?Math.max(min,Math.min(max,Math.floor(value))):fallback;
function normalize(raw={},config=window.AstraeonProgressionConfig){
 const c=config.progression,primary=config.primary;
 const state={baseLevel:sane(raw.baseLevel,c.base.initialLevel,1,c.storedLevelLimit),baseExp:sane(raw.baseExp,0),baseJobLevel:sane(raw.baseJobLevel,c.job.initialLevel,1,c.job.cap),baseJobExp:sane(raw.baseJobExp,0),statPoints:sane(raw.statPoints,c.base.initialPoints),skillPoints:sane(raw.skillPoints,c.job.initialPoints)};
 for(const key of primary.keys)state[key]=sane(raw[key],primary.initial,primary.initial,primary.cap);
 // v4 and earlier used initial=1, cost=1. Never infer a refund using today's tuned cost.
 const historicalPaid=primary.keys.reduce((sum,key)=>sum+Math.max(0,state[key]-1),0);
 state.statPointSpending=historicalPaid===0?0:Object.hasOwn(raw,'statPointSpending')?(Number.isSafeInteger(raw.statPointSpending)&&raw.statPointSpending>=0?raw.statPointSpending:0):historicalPaid;
 Object.assign(state,window.AstraeonSkillTree.normalize(raw));
 state.resourceBase={maxHP:Number.isFinite(raw.resourceBase?.maxHP)?raw.resourceBase.maxHP:0,maxSP:Number.isFinite(raw.resourceBase?.maxSP)?raw.resourceBase.maxSP:0};
 return state;
}
function create(raw={},options={}){
 const config=stats.freeze(structuredClone(options.config||window.AstraeonProgressionConfig));
 let state=normalize(raw,config),modifiers=stats.freeze(structuredClone(options.modifiers||{}));
 const conversionHooks=Object.freeze([...(options.conversionHooks||[])]);
 const getClassId=options.getClassId||(()=>options.classId??window.AstraeonSkillDefinitions.classIdFor(raw));
 const derive=(next,mods=modifiers)=>{
  for(const key of Object.keys(mods))if(!['equipmentModifiers','passiveModifiers','temporaryEffectModifiers'].includes(key))throw new TypeError(`Unknown modifier group: ${key}`);
  return stats.calculate({baseLevel:next.baseLevel,primaryStats:Object.fromEntries(config.primary.keys.map(key=>[key,next[key]])),characterBase:next.resourceBase,equipmentModifiers:mods.equipmentModifiers,passiveModifiers:[...(mods.passiveModifiers||[]),...window.AstraeonSkillTree.passiveModifiers(next.learnedSkills,getClassId())],temporaryEffectModifiers:mods.temporaryEffectModifiers,conversionHooks},config);
 };
 let derived=derive(state);
 const clampResource=(value,max)=>{if(!Number.isFinite(value))throw new RangeError('Resource must be finite');return Math.max(0,Math.min(max,value))};
 let currentHP=clampResource(Number.isFinite(raw.currentHP)?raw.currentHP:derived.maxHP,derived.maxHP),currentSP=clampResource(Number.isFinite(raw.currentSP)?raw.currentSP:derived.maxSP,derived.maxSP);
 const commit=next=>{const calculated=derive(next);state=next;derived=calculated;currentHP=Math.min(currentHP,derived.maxHP);currentSP=Math.min(currentSP,derived.maxSP)};
 const snapshot=()=>stats.freeze({...state,learnedSkills:{...state.learnedSkills},skillPointSpending:{...state.skillPointSpending},resourceBase:{...state.resourceBase},currentHP,currentSP,maxHP:derived.maxHP,maxSP:derived.maxSP});
 const grant=(track,amount)=>{const result=p.grant(state,track,amount,config.progression);commit(result.state);return {...result,state:snapshot()}};
 const set=(track,level)=>{commit(p.setLevel(state,track,level,config.progression));return snapshot()};
 const addPoints=(track,amount)=>{commit(p.addPoints(state,track,amount));return snapshot()};
 const skillTransition=result=>{if(!result.ok)return result;commit(result.state);return stats.freeze({...result,state:snapshot()})};
 const rewardPlans=new WeakMap();
 function prepareRewards(baseExp,jobExp){
  try{
   const base=p.grant(state,'base',baseExp,config.progression),job=p.grant(base.state,'job',jobExp,config.progression),calculated=derive(job.state);
   const plan=stats.freeze({ok:true,baseExp,jobExp,baseLevelsGained:base.levelsGained,jobLevelsGained:job.levelsGained});
   rewardPlans.set(plan,{before:state,mods:JSON.stringify(modifiers),next:job.state,calculated});return plan;
  }catch{return stats.freeze({ok:false,code:'INVALID_PROGRESSION_REWARD'})}
 }
 function commitPreparedRewards(plan){
  const prepared=rewardPlans.get(plan);if(!prepared||prepared.before!==state||prepared.mods!==JSON.stringify(modifiers))return false;
  state=prepared.next;derived=prepared.calculated;currentHP=plan.baseLevelsGained?derived.maxHP:Math.min(currentHP,derived.maxHP);currentSP=plan.baseLevelsGained?derived.maxSP:Math.min(currentSP,derived.maxSP);rewardPlans.delete(plan);return true;
 }
 return Object.freeze({
  prepareRewards,commitPreparedRewards,
  getSkillRank:id=>Object.hasOwn(state.learnedSkills,id)?state.learnedSkills[id]:0,
  getLearnedSkills:()=>stats.freeze({...state.learnedSkills}),
  getPassiveSkillModifiers:()=>window.AstraeonSkillTree.passiveModifiers(state.learnedSkills,getClassId()),
  canLearnSkill:id=>window.AstraeonSkillTree.canLearnSkill(state,getClassId(),id),
  learnSkill:id=>skillTransition(window.AstraeonSkillTree.learn(state,getClassId(),id,'learn')),
  rankUpSkill:id=>skillTransition(window.AstraeonSkillTree.learn(state,getClassId(),id,'rank')),
  canRefundSkill:id=>window.AstraeonSkillTree.canRefundSkill(state,id),
  resetSkills:()=>skillTransition(window.AstraeonSkillTree.reset(state)),
  getAvailableSkills:()=>stats.freeze((window.AstraeonSkillDefinitions.trees[getClassId()]?.skillIds||[]).map(id=>({definition:window.AstraeonSkillDefinitions.definitions[id],rank:state.learnedSkills[id]||0,learning:window.AstraeonSkillTree.canLearnSkill(state,getClassId(),id)}))),
  snapshot,getValue(key){if(key==='currentHP')return currentHP;if(key==='currentSP')return currentSP;if(key==='maxHP'||key==='maxSP')return derived[key];if(progressionKeys.includes(key)||config.primary.keys.includes(key))return state[key];if(key==='resourceBase')return stats.freeze({...state.resourceBase});throw new TypeError('Unknown character field')},
  getPrimaryStats:()=>stats.freeze(Object.fromEntries(config.primary.keys.map(key=>[key,state[key]]))),getDerivedStats:()=>derived,
  getBaseExpRequirement:(level=state.baseLevel)=>p.getBaseExpRequirement(level,config.progression),getJobExpRequirement:(level=state.baseJobLevel)=>p.getJobExpRequirement(level,config.progression),
  grantBaseExp:amount=>grant('base',amount),grantJobExp:amount=>grant('job',amount),setBaseLevel:level=>set('base',level),setBaseJobLevel:level=>set('job',level),addStatPoints:amount=>addPoints('base',amount),addSkillPoints:amount=>addPoints('job',amount),
  allocateStat(stat,amount=1){
   if(!config.primary.keys.includes(stat))throw new TypeError(`Unknown primary stat: ${stat}`);
   p.integer(amount,'allocation',1);const cost=p.integer(amount*config.primary.pointCost,'allocation cost',1);
   if(cost>state.statPoints)throw new RangeError('Insufficient Stat Points');
   const value=p.integer(state[stat]+amount,stat,config.primary.initial,config.primary.cap);
   commit({...state,[stat]:value,statPoints:state.statPoints-cost,statPointSpending:p.integer(state.statPointSpending+cost,'stat expenditure')});return snapshot();
  },
  resetStats(){
   const refund=state.statPointSpending;
   const next={...state,statPointSpending:0,statPoints:p.integer(state.statPoints+refund,'point balance')};for(const key of config.primary.keys)next[key]=config.primary.initial;
   commit(next);return snapshot();
  },
  setCurrentHP(value){currentHP=clampResource(value,derived.maxHP);return currentHP},setCurrentSP(value){currentSP=clampResource(value,derived.maxSP);return currentSP},
  setCurrentResources(value){const hp=clampResource(value.currentHP,derived.maxHP),sp=clampResource(value.currentSP,derived.maxSP);currentHP=hp;currentSP=sp;return stats.freeze({currentHP,currentSP,maxHP:derived.maxHP,maxSP:derived.maxSP})},
  setModifiers(next){const copy=stats.freeze(structuredClone(next)),calculated=derive(state,copy);modifiers=copy;derived=calculated;currentHP=Math.min(currentHP,derived.maxHP);currentSP=Math.min(currentSP,derived.maxSP);return derived}
 });
}
window.AstraeonCharacter=Object.freeze({create,normalize,progressionKeys:Object.freeze(progressionKeys)});
})();
