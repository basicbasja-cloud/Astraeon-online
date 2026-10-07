/* Small compatibility adapter between private character state and legacy game consumers. */
(() => {
'use strict';
function legacyModifiers(state,config=window.AstraeonProgressionConfig){
 const gear=state.equipment||{},equipmentModifiers=[];
 for(const key of ['weapon','armor'])if(Object.hasOwn(config.legacyEquipment[key],gear[key]))equipmentModifiers.push(config.legacyEquipment[key][gear[key]]);
 if(typeof gear.relic==='string'&&gear.relic!=='None')equipmentModifiers.push(config.legacyEquipment.relic);
 return {equipmentModifiers,passiveModifiers:state.party?.length?[config.legacyParty]:[]};
}
function attach(state,options={}){
 const getClassId=()=>options.classId??window.AstraeonSkillDefinitions.classIdFor(state);
 let runtime={equipmentModifiers:[],passiveModifiers:[],temporaryEffectModifiers:[]},lastSignature;
 const build=()=>{const legacy=legacyModifiers(state,options.config);return {equipmentModifiers:[...legacy.equipmentModifiers,...runtime.equipmentModifiers],passiveModifiers:[...legacy.passiveModifiers,...runtime.passiveModifiers],temporaryEffectModifiers:runtime.temporaryEffectModifiers}};
 const character=window.AstraeonCharacter.create(state,{...options,getClassId,modifiers:build()});
 function recalculate(){const mods=build(),signature=JSON.stringify([getClassId(),mods]);if(signature!==lastSignature){character.setModifiers(mods);lastSignature=signature}return character.getDerivedStats()}
 let actionLoadout=window.AstraeonSkillRuntime.normalizeLoadout(state.actionLoadout);
 let legacySkillControls=state.legacySkillControls===true;
 const loadouts=window.AstraeonActionLoadout;
 const actionRuntime=window.AstraeonActionRuntime.create({getLoadout:()=>actionLoadout,getClassId,getRank:character.getSkillRank,getNodes:()=>state.skillNodes||{},getCurrentHP:()=>character.getValue('currentHP'),getResource:()=>character.getValue('currentSP'),setResource:character.setCurrentSP,getLegacyAction:slot=>{
  if(slot>=4||(!legacySkillControls&&getClassId()))return null;
  const archetype=options.getLegacyArchetype?.()||window.AstraeonAnimation?.archetype(state.cls)||(state.cls===12?'mage':state.cls===3?'ranger':'warrior');
  const base=window.AstraeonCombat.definitions[archetype]?.[`skill${slot+1}`];return base?window.AstraeonCombat.compile(archetype,`skill${slot+1}`,1,state.skillNodes?.[base.id]):null;
 }},options.actionConfig);
 const commitLoadout=(result,context)=>{
  if(!result.ok||!result.changed)return result;
  const runtimeResult=actionRuntime.configurationChanged(actionLoadout,result.loadout,context);if(!runtimeResult.ok)return runtimeResult;
  actionLoadout=result.loadout;return Object.freeze({...result,...runtimeResult});
 };
 Object.defineProperty(state,'actionLoadout',{enumerable:true,get:()=>Object.freeze([...actionLoadout])});
 Object.defineProperty(state,'legacySkillControls',{enumerable:true,get:()=>legacySkillControls});
 for(const key of ['learnedSkills','skillPointSpending','statPointSpending'])Object.defineProperty(state,key,{enumerable:true,get:()=>character.snapshot()[key]});
 const keys=[...window.AstraeonCharacter.progressionKeys,...window.AstraeonProgressionConfig.primary.keys,'resourceBase','currentHP','currentSP','maxHP','maxSP'];
 const aliases={lv:'baseLevel',xp:'baseExp',hp:'currentHP',maxHp:'maxHP',energy:'currentSP',maxEnergy:'maxSP'};
 for(const [key,canonical] of [...keys.map(key=>[key,key]),...Object.entries(aliases)]){
  const descriptor={enumerable:true,configurable:false,get:()=>character.getValue(canonical)};
  if(canonical==='currentHP')descriptor.set=value=>character.setCurrentHP(value);
  if(canonical==='currentSP')descriptor.set=value=>character.setCurrentSP(value);
  Object.defineProperty(state,key,descriptor);
 }
 const api={recalculate,getDerivedStats:()=>recalculate(),getPrimaryStats:character.getPrimaryStats,snapshot:()=>{recalculate();return character.snapshot()},getBaseExpRequirement:character.getBaseExpRequirement,getJobExpRequirement:character.getJobExpRequirement,
  getClassId,getSkillTree:()=>window.AstraeonSkillDefinitions.trees[getClassId()]||null,
  getActionLoadout:()=>state.actionLoadout,
  getLoadout:()=>state.actionLoadout,getSlot:slot=>loadouts.getSlot(actionLoadout,slot),
  canAssignSkill:(slot,id)=>loadouts.canAssignSkill(actionLoadout,character.snapshot(),getClassId(),slot,id),
  clearSlot:(slot,context)=>commitLoadout(loadouts.clearSlot(actionLoadout,character.snapshot(),getClassId(),slot),context),
  swapSlots:(a,b,context)=>commitLoadout(loadouts.swapSlots(actionLoadout,a,b),context),
  moveSkill:(from,to,context)=>commitLoadout(loadouts.moveSkill(actionLoadout,from,to),context),
  getActionSlotState:actionRuntime.getSlotState,prepareAction:actionRuntime.prepareAction,commitAction:actionRuntime.commitAction,requestAction:actionRuntime.requestAction,
  getActionRuntime:actionRuntime.snapshot,resetActionCooldowns:actionRuntime.resetCooldowns,invalidatePreparedActions:actionRuntime.invalidatePrepared,
  canUseSkill:id=>window.AstraeonSkillRuntime.canUseSkill(character.getLearnedSkills(),getClassId(),id),
  isSkillAssigned:id=>!!window.AstraeonSkillDefinitions.getDefinition(id)&&actionLoadout.includes(id),
  setSkillNode(id,node){
   if(!Object.hasOwn(window.AstraeonSkillNodes.compatibility,id)||(node!==null&&!window.AstraeonSkillNodes.compatibility[id].includes(node)))return Object.freeze({ok:false,code:'INCOMPATIBLE_NODE'});
   state.skillNodes={...(state.skillNodes||{})};if(node===null)delete state.skillNodes[id];else state.skillNodes[id]=node;
   return Object.freeze({ok:true,skillId:id,node});
  },
  assignSkill(slot,id,context){
   const result=loadouts.assignSkill(actionLoadout,character.snapshot(),getClassId(),slot,id);
   // Preserve the existing public error code; canAssignSkill exposes detailed causes.
   if(!result.ok&&['UNKNOWN_SKILL','NOT_ASSIGNABLE','WRONG_CLASS','NOT_LEARNED'].includes(result.code))return Object.freeze({ok:false,code:'NOT_USABLE',reason:result.code});
   return commitLoadout(result,context);
  },
  compileAction(slot,combo=1){if(!Number.isSafeInteger(slot)||slot<0||slot>=window.AstraeonSkillRuntime.slotCount)return null;const id=actionLoadout[slot];return api.canUseSkill(id)?window.AstraeonSkillRuntime.compile(id,character.getSkillRank(id),state.skillNodes?.[id],combo):null},
  resetSkills(){const safe=actionRuntime.invalidatePrepared();if(!safe.ok)return safe;recalculate();const result=character.resetSkills();if(result.ok){actionLoadout=loadouts.normalize(null);legacySkillControls=false}return result},
  setCurrentHP:character.setCurrentHP,setCurrentSP:character.setCurrentSP,
  setModifiers(value){
   for(const key of Object.keys(value))if(!Object.hasOwn(runtime,key))throw new TypeError(`Unknown modifier group: ${key}`);
   const before=runtime;runtime=window.AstraeonStats.freeze(structuredClone({equipmentModifiers:[],passiveModifiers:[],temporaryEffectModifiers:[],...value}));
   try{return recalculate()}catch(error){runtime=before;throw error}
  }
 };
 for(const key of ['grantBaseExp','grantJobExp','setBaseLevel','setBaseJobLevel','addStatPoints','addSkillPoints','allocateStat','resetStats','getSkillRank','getLearnedSkills','getPassiveSkillModifiers','canLearnSkill','learnSkill','rankUpSkill','canRefundSkill','getAvailableSkills'])api[key]=(...args)=>{recalculate();return character[key](...args)};
 recalculate();return Object.freeze(api);
}
window.AstraeonPlayer=Object.freeze({legacyModifiers,attach});
})();
