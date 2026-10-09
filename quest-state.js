/* Durable accepted/completed state; Collect and readiness always derive. */
(() => {
'use strict';
const D=window.AstraeonQuestDefinitions,freeze=window.AstraeonItemDefinitions.freeze;
const statuses=freeze(['LOCKED','AVAILABLE','ACTIVE','READY_TO_TURN_IN','COMPLETED']);
function normalize(raw,registry){
 const entries={},history=D.plain(raw?.history)&&D.json(raw.history)?structuredClone(raw.history):{};
 for(const [id,value] of Object.entries(D.plain(raw?.entries)?raw.entries:{})){
  const def=registry.getDefinition(id);
  if(!def||!D.plain(value)||!['ACTIVE','COMPLETED'].includes(value.status)){if(D.json(value))Object.defineProperty(history,id,{value:structuredClone(value),enumerable:true,writable:true,configurable:true});continue}
  const progress={};for(const o of def.objectives)if(o.type!=='COLLECT')progress[o.id]=Number.isSafeInteger(value.progress?.[o.id])&&value.progress[o.id]>=0?Math.min(o.required,value.progress[o.id]):0;
  entries[id]={status:value.status,progress};
 }
 return freeze({schema:1,entries,history});
}
function evaluate(state,definition,inventory,catalog=window.AstraeonItemDefinitions){
 const entry=state.entries[definition.id],prerequisites=definition.prerequisites.every(id=>state.entries[id]?.status==='COMPLETED');
 const pools={},objectives=definition.objectives.map(o=>{
  let owned=null,progress=entry?.progress[o.id]||0;
  if(o.type==='COLLECT'){
   const d=catalog.getDefinition(o.itemId);owned=d.stackable?(inventory.stacks[o.itemId]||0):Object.values(inventory.instances).filter(i=>i.definitionId===o.itemId).length;
   if(o.consumeOnTurnIn){if(!Object.hasOwn(pools,o.itemId))pools[o.itemId]=owned;progress=Math.min(o.required,pools[o.itemId]);pools[o.itemId]-=progress}else progress=Math.min(o.required,owned);
  }
  return {...o,progress,owned,complete:progress>=o.required};
 });
 const status=entry?.status==='COMPLETED'?'COMPLETED':entry?objectives.every(o=>o.complete)?'READY_TO_TURN_IN':'ACTIVE':prerequisites?'AVAILABLE':'LOCKED';
 return freeze({ok:true,questId:definition.id,status,prerequisitesSatisfied:prerequisites,objectives});
}
function canTransition(from,to){return ({LOCKED:['AVAILABLE'],AVAILABLE:['ACTIVE'],ACTIVE:['READY_TO_TURN_IN'],READY_TO_TURN_IN:['ACTIVE','COMPLETED'],COMPLETED:[]})[from]?.includes(to)||false}
window.AstraeonQuestState=freeze({statuses,normalize,evaluate,canTransition});
})();
