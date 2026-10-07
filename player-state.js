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
 let runtime={equipmentModifiers:[],passiveModifiers:[],temporaryEffectModifiers:[]},lastSignature;
 const build=()=>{const legacy=legacyModifiers(state,options.config);return {equipmentModifiers:[...legacy.equipmentModifiers,...runtime.equipmentModifiers],passiveModifiers:[...legacy.passiveModifiers,...runtime.passiveModifiers],temporaryEffectModifiers:runtime.temporaryEffectModifiers}};
 const character=window.AstraeonCharacter.create(state,{...options,modifiers:build()});
 function recalculate(){const mods=build(),signature=JSON.stringify(mods);if(signature!==lastSignature){character.setModifiers(mods);lastSignature=signature}return character.getDerivedStats()}
 const keys=[...window.AstraeonCharacter.progressionKeys,...window.AstraeonProgressionConfig.primary.keys,'resourceBase','currentHP','currentSP','maxHP','maxSP'];
 const aliases={lv:'baseLevel',xp:'baseExp',hp:'currentHP',maxHp:'maxHP',energy:'currentSP',maxEnergy:'maxSP'};
 for(const [key,canonical] of [...keys.map(key=>[key,key]),...Object.entries(aliases)]){
  const descriptor={enumerable:true,configurable:false,get:()=>character.getValue(canonical)};
  if(canonical==='currentHP')descriptor.set=value=>character.setCurrentHP(value);
  if(canonical==='currentSP')descriptor.set=value=>character.setCurrentSP(value);
  Object.defineProperty(state,key,descriptor);
 }
 const api={recalculate,getDerivedStats:()=>recalculate(),getPrimaryStats:character.getPrimaryStats,snapshot:()=>{recalculate();return character.snapshot()},getBaseExpRequirement:character.getBaseExpRequirement,getJobExpRequirement:character.getJobExpRequirement,
  setCurrentHP:character.setCurrentHP,setCurrentSP:character.setCurrentSP,
  setModifiers(value){
   for(const key of Object.keys(value))if(!Object.hasOwn(runtime,key))throw new TypeError(`Unknown modifier group: ${key}`);
   const before=runtime;runtime=window.AstraeonStats.freeze(structuredClone({equipmentModifiers:[],passiveModifiers:[],temporaryEffectModifiers:[],...value}));
   try{return recalculate()}catch(error){runtime=before;throw error}
  }
 };
 for(const key of ['grantBaseExp','grantJobExp','setBaseLevel','setBaseJobLevel','addStatPoints','addSkillPoints','allocateStat','resetStats'])api[key]=(...args)=>{recalculate();return character[key](...args)};
 recalculate();return Object.freeze(api);
}
window.AstraeonPlayer=Object.freeze({legacyModifiers,attach});
})();
