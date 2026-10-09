/* Small compatibility adapter between private character state and legacy game consumers. */
(() => {
'use strict';
function legacyModifiers(state,config=window.AstraeonProgressionConfig){
 const equipmentModifiers=window.AstraeonItemEquipment.modifiers(state.itemInventory,state.equippedItems);
 return {equipmentModifiers,passiveModifiers:state.party?.length?[config.legacyParty]:[]};
}
function attach(state,options={}){
 const getClassId=()=>options.classId??window.AstraeonSkillDefinitions.classIdFor(state);
 let runtime={equipmentModifiers:[],passiveModifiers:[],temporaryEffectModifiers:[]},lastSignature;
 const items=window.AstraeonItemState.create(state,{catalog:options.itemCatalog,requirements:options.equipmentRequirements,getCapacityPolicy:options.getCapacityPolicy,onChange:(inventory,equipment)=>{const mods=build(inventory,equipment);character.setModifiers(mods);lastSignature=JSON.stringify([getClassId(),mods])}});
 const build=(inventory=items.getInventory(),equipment=items.getEquipmentSlots())=>({equipmentModifiers:[...window.AstraeonItemEquipment.modifiers(inventory,equipment,options.itemCatalog),...runtime.equipmentModifiers],passiveModifiers:[...(state.party?.length?[(options.config||window.AstraeonProgressionConfig).legacyParty]:[]),...runtime.passiveModifiers],temporaryEffectModifiers:runtime.temporaryEffectModifiers});
 const character=window.AstraeonCharacter.create(state,{...options,getClassId,modifiers:build()});
 function recalculate(){const mods=build(),signature=JSON.stringify([getClassId(),mods]);if(signature!==lastSignature){character.setModifiers(mods);lastSignature=signature}return character.getDerivedStats()}
 let rewardQuest=state.quest,questGeneration=0;
 function trackRewardQuest(){if(state.quest!==rewardQuest){rewardQuest=state.quest;questGeneration++}return questGeneration}
 const getItemResources=()=>{recalculate();return Object.fromEntries(['currentHP','currentSP','maxHP','maxSP'].map(key=>[key,character.getValue(key)]))};
 const itemRuntime=window.AstraeonActionItemRuntime.create({getInventory:items.getInventory,getQuantity:items.getQuantity,getResources:getItemResources,commit:(id,inventory,plan)=>items.consumeStackWithEffect(id,1,inventory,()=>{if(JSON.stringify(getItemResources())!==JSON.stringify(plan.resourceBefore))return false;character.setCurrentResources(plan.resourceAfter);return true})},{catalog:options.itemCatalog,config:options.itemActionConfig,restrictions:options.itemRestrictions});
 const boxRuntime=window.AstraeonMonsterBoxRuntime?.create({getInventory:items.getInventory,getRevision:items.getRevision,getQuantity:items.getQuantity,getCurrentHP:()=>character.getValue('currentHP'),preflight:(source,bounds)=>items.canOpenable(source,bounds,options.boxEnvelopePreflight),commit:(source,resolve)=>items.commitOpenable(source,resolve,options.boxPreflight)},{catalog:options.itemCatalog,tables:options.boxTables,getRng:options.getBoxRng||(()=>window.AstraeonCombatRuntime.productionRng()),restrictions:options.boxRestrictions});
 const {consumeStackWithEffect,commitRewards,commitItemTransaction,canOpenable,commitOpenable,...itemMethods}=items;
 let quests=null;
 const questContext=value=>value??options.getQuestContext?.()??{};
 const rewardIdentity=()=>{const {currentHP,currentSP,...durable}=character.snapshot();return JSON.stringify([durable,state.gold])};
 function questPreflight(transaction,rewards){
  recalculate();const capacity=items.canAcceptItemPackage(transaction);if(!capacity.ok)return capacity;
  const descriptor=Object.getOwnPropertyDescriptor(state,'gold');
  if(descriptor?(!Object.hasOwn(descriptor,'value')||!descriptor.writable):!Object.isExtensible(state))return Object.freeze({ok:false,code:'INVALID_CURRENCY'});
  const gold=state.gold;if(!Number.isFinite(gold)||gold<0||!Number.isSafeInteger(rewards.gold)||rewards.gold<0||!Number.isFinite(gold+rewards.gold)||gold+rewards.gold>Number.MAX_SAFE_INTEGER)return Object.freeze({ok:false,code:'CURRENCY_OVERFLOW'});
  const progression=character.prepareRewards(rewards.baseExp,rewards.jobExp);return progression.ok?window.AstraeonItemDefinitions.freeze({ok:true,capacity,progression,currencyBefore:gold,currencyAfter:gold+rewards.gold}):progression;
 }
 function commitQuestReward(transaction,rewards,inventory,revision,publish){
  const checked=questPreflight(transaction,rewards);if(!checked.ok)return checked;
  const result=items.commitItemTransaction(transaction,inventory,revision,()=>{if(!character.commitPreparedRewards(checked.progression))return false;state.gold=checked.currencyAfter;return publish()});
  return result.ok?window.AstraeonItemDefinitions.freeze({...result,currencyBefore:checked.currencyBefore,currencyAfter:state.gold,currencyGranted:rewards.gold,baseExp:rewards.baseExp,jobExp:rewards.jobExp,baseLevelsGained:checked.progression.baseLevelsGained,jobLevelsGained:checked.progression.jobLevelsGained}):result;
 }
 const boxCall=(method,...args)=>boxRuntime?boxRuntime[method](...args):Object.freeze({ok:false,code:'BOX_RUNTIME_UNAVAILABLE'});
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
  ...itemMethods,
  getQuestState:()=>quests?.getState(),getQuests:()=>quests?.list(),getQuest:id=>quests?.inspect(id),getQuestRuntime:()=>quests?.snapshot(),
  canAcceptQuest:(id,c)=>quests?.canAccept(id,questContext(c)),acceptQuest:(id,c)=>quests?.accept(id,questContext(c)),
  observeQuestTalk:e=>quests?.observeTalk(e),observeQuestKill:e=>quests?.observeKill(e),
  prepareQuestTurnIn:(id,c)=>quests?.prepare(id,questContext(c)),commitQuestTurnIn:(ticket,c)=>quests?.commit(ticket,questContext(c)),turnInQuest:(id,c)=>quests?.turnIn(id,questContext(c)),invalidatePreparedQuests:()=>quests?.invalidate(),
  getMonsterRewardContext:zone=>window.AstraeonItemDefinitions.freeze({zone,quest:state.quest?{...state.quest}:null,questGeneration:trackRewardQuest()}),
  commitMonsterRewards(resolution,profileId,contracts=[]){
   recalculate();const context=resolution?.questGeneration!==undefined&&resolution.questGeneration!==trackRewardQuest()?{...resolution,quest:null}:resolution;
   const rewards=window.AstraeonMonsterRewards.plan(state,context,profileId,contracts,(options.config||window.AstraeonProgressionConfig).progression.activityJobExpRatio);if(!rewards.ok)return rewards;
   // These existing compatibility fields must be plain writable local state.
   // All fallible planning is complete before the contained synchronous publisher.
   for(const key of Object.keys(rewards.fields)){const d=Object.getOwnPropertyDescriptor(state,key);if(d?(!Object.hasOwn(d,'value')||!d.writable):!Object.isExtensible(state))return Object.freeze({ok:false,code:'INVALID_REWARD_STATE'})}
   const progression=character.prepareRewards(rewards.baseExp,rewards.jobExp);if(!progression.ok)return progression;
   const currencyBefore=state.gold,fields=structuredClone(rewards.fields);
   const result=items.commitRewards(rewards.itemRewards,()=>{if(!character.commitPreparedRewards(progression))return false;Object.assign(state,fields);return true});
   if(result.ok)rewardQuest=state.quest;
   return result.ok?window.AstraeonItemDefinitions.freeze({...result,currencyBefore,currencyAfter:state.gold,currencyGranted:rewards.currencyGranted,baseExp:rewards.baseExp,jobExp:rewards.jobExp,baseLevelsGained:progression.baseLevelsGained,jobLevelsGained:progression.jobLevelsGained,questCredit:rewards.questCredit,completedQuest:rewards.completedQuest,killCredit:rewards.killCredit}):result;
  },
  getActionItemState:itemRuntime.getState,prepareActionItem:itemRuntime.prepare,commitActionItem:itemRuntime.commit,requestActionItem:itemRuntime.request,getActionItemRuntime:itemRuntime.snapshot,resetActionItemCooldowns:itemRuntime.resetCooldowns,invalidatePreparedActionItems:itemRuntime.invalidatePrepared,
  useConsumable:(id,context)=>itemRuntime.request(id,context??options.getItemContext?.()??{now:0,intent:'inventory'}),
  getInventoryRevision:items.getRevision,
  getMonsterBoxState:(id,count=1,context)=>boxCall('getState',id,count,context??options.getItemContext?.()??{intent:'inventory'}),
  prepareMonsterBoxOpen:(id,count=1,context)=>boxCall('prepare',id,count,context??options.getItemContext?.()??{intent:'inventory'}),
  commitMonsterBoxOpen:(ticket,context)=>boxCall('commit',ticket,context??options.getItemContext?.()??{intent:'inventory'}),
  openMonsterBoxes:(id,count=1,context)=>boxCall('request',id,count,context??options.getItemContext?.()??{intent:'inventory'}),
  getMonsterBoxRuntime:()=>boxCall('snapshot'),invalidatePreparedMonsterBoxes:()=>boxCall('invalidatePrepared'),
  getClassId,getSkillTree:()=>window.AstraeonSkillDefinitions.trees[getClassId()]||null,
  getActionLoadout:()=>state.actionLoadout,
  getLoadout:()=>state.actionLoadout,getSlot:slot=>loadouts.getSlot(actionLoadout,slot),
  canAssignSkill:(slot,id)=>loadouts.canAssignSkill(actionLoadout,character.snapshot(),getClassId(),slot,id),
  clearSlot:(slot,context)=>commitLoadout(loadouts.clearSlot(actionLoadout,character.snapshot(),getClassId(),slot),context),
  swapSlots:(a,b,context)=>commitLoadout(loadouts.swapSlots(actionLoadout,a,b),context),
  moveSkill:(from,to,context)=>commitLoadout(loadouts.moveSkill(actionLoadout,from,to),context),
  getActionSlotState:actionRuntime.getSlotState,prepareAction:actionRuntime.prepareAction,commitAction:actionRuntime.commitAction,requestAction:actionRuntime.requestAction,
  getActionRuntime:actionRuntime.snapshot,resetActionCooldowns:actionRuntime.resetCooldowns,invalidatePreparedActions(){const result=actionRuntime.invalidatePrepared();if(!result.ok)return result;quests?.invalidate();const itemResult=itemRuntime.invalidatePrepared();return itemResult.ok&&boxRuntime?boxRuntime.invalidatePrepared():itemResult},
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
 if(window.AstraeonQuestRuntime){
  quests=window.AstraeonQuestRuntime.create({getInventory:items.getInventory,getInventoryRevision:items.getRevision,getEquipment:items.getEquipmentSlots,getCurrentHP:()=>character.getValue('currentHP'),preflight:questPreflight,commit:commitQuestReward,rewardIdentity},{raw:state.questState,definitions:options.questDefinitions,catalog:options.itemCatalog,monsters:options.questMonsters,targets:options.questTargets,isTalkEvidence:options.isQuestTalkEvidence,isKillEvidence:options.isQuestKillEvidence});
  Object.defineProperty(state,'questState',{enumerable:true,get:quests.getState});
 }
 recalculate();return Object.freeze(api);
}
window.AstraeonPlayer=Object.freeze({legacyModifiers,attach});
})();
