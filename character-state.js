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
 state.resourceBase={maxHP:Number.isFinite(raw.resourceBase?.maxHP)?raw.resourceBase.maxHP:0,maxSP:Number.isFinite(raw.resourceBase?.maxSP)?raw.resourceBase.maxSP:0};
 return state;
}
function create(raw={},options={}){
 const config=stats.freeze(structuredClone(options.config||window.AstraeonProgressionConfig));
 let state=normalize(raw,config),modifiers=stats.freeze(structuredClone(options.modifiers||{}));
 const conversionHooks=Object.freeze([...(options.conversionHooks||[])]);
 const derive=(next,mods=modifiers)=>{
  for(const key of Object.keys(mods))if(!['equipmentModifiers','passiveModifiers','temporaryEffectModifiers'].includes(key))throw new TypeError(`Unknown modifier group: ${key}`);
  return stats.calculate({baseLevel:next.baseLevel,primaryStats:Object.fromEntries(config.primary.keys.map(key=>[key,next[key]])),characterBase:next.resourceBase,equipmentModifiers:mods.equipmentModifiers,passiveModifiers:mods.passiveModifiers,temporaryEffectModifiers:mods.temporaryEffectModifiers,conversionHooks},config);
 };
 let derived=derive(state);
 const clampResource=(value,max)=>{if(!Number.isFinite(value))throw new RangeError('Resource must be finite');return Math.max(0,Math.min(max,value))};
 let currentHP=clampResource(Number.isFinite(raw.currentHP)?raw.currentHP:derived.maxHP,derived.maxHP),currentSP=clampResource(Number.isFinite(raw.currentSP)?raw.currentSP:derived.maxSP,derived.maxSP);
 const commit=next=>{const calculated=derive(next);state=next;derived=calculated;currentHP=Math.min(currentHP,derived.maxHP);currentSP=Math.min(currentSP,derived.maxSP)};
 const snapshot=()=>stats.freeze({...state,resourceBase:{...state.resourceBase},currentHP,currentSP,maxHP:derived.maxHP,maxSP:derived.maxSP});
 const grant=(track,amount)=>{const result=p.grant(state,track,amount,config.progression);commit(result.state);return {...result,state:snapshot()}};
 const set=(track,level)=>{commit(p.setLevel(state,track,level,config.progression));return snapshot()};
 const addPoints=(track,amount)=>{commit(p.addPoints(state,track,amount));return snapshot()};
 return Object.freeze({
  snapshot,getValue(key){if(key==='currentHP')return currentHP;if(key==='currentSP')return currentSP;if(key==='maxHP'||key==='maxSP')return derived[key];if(progressionKeys.includes(key)||config.primary.keys.includes(key))return state[key];if(key==='resourceBase')return stats.freeze({...state.resourceBase});throw new TypeError('Unknown character field')},
  getPrimaryStats:()=>stats.freeze(Object.fromEntries(config.primary.keys.map(key=>[key,state[key]]))),getDerivedStats:()=>derived,
  getBaseExpRequirement:(level=state.baseLevel)=>p.getBaseExpRequirement(level,config.progression),getJobExpRequirement:(level=state.baseJobLevel)=>p.getJobExpRequirement(level,config.progression),
  grantBaseExp:amount=>grant('base',amount),grantJobExp:amount=>grant('job',amount),setBaseLevel:level=>set('base',level),setBaseJobLevel:level=>set('job',level),addStatPoints:amount=>addPoints('base',amount),addSkillPoints:amount=>addPoints('job',amount),
  allocateStat(stat,amount=1){
   if(!config.primary.keys.includes(stat))throw new TypeError(`Unknown primary stat: ${stat}`);
   p.integer(amount,'allocation',1);const cost=p.integer(amount*config.primary.pointCost,'allocation cost',1);
   if(cost>state.statPoints)throw new RangeError('Insufficient Stat Points');
   const value=p.integer(state[stat]+amount,stat,config.primary.initial,config.primary.cap);
   commit({...state,[stat]:value,statPoints:state.statPoints-cost});return snapshot();
  },
  resetStats(){
   const refund=config.primary.keys.reduce((total,key)=>total+(state[key]-config.primary.initial)*config.primary.pointCost,0);
   const next={...state,statPoints:p.integer(state.statPoints+refund,'point balance')};for(const key of config.primary.keys)next[key]=config.primary.initial;
   commit(next);return snapshot();
  },
  setCurrentHP(value){currentHP=clampResource(value,derived.maxHP);return currentHP},setCurrentSP(value){currentSP=clampResource(value,derived.maxSP);return currentSP},
  setModifiers(next){const copy=stats.freeze(structuredClone(next)),calculated=derive(state,copy);modifiers=copy;derived=calculated;currentHP=Math.min(currentHP,derived.maxHP);currentSP=Math.min(currentSP,derived.maxSP);return derived}
 });
}
window.AstraeonCharacter=Object.freeze({create,normalize,progressionKeys:Object.freeze(progressionKeys)});
})();
