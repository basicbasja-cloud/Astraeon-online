/* Quest observes evidence/ownership; existing authorities commit all rewards. */
(() => {
'use strict';
const D=window.AstraeonQuestDefinitions,S=window.AstraeonQuestState,freeze=window.AstraeonItemDefinitions.freeze;
const fail=code=>freeze({ok:false,code,blockedReason:code,committed:false});
function create(owner,{raw,definitions=D.definitions,catalog=window.AstraeonItemDefinitions,monsters,targets,isTalkEvidence=()=>false,isKillEvidence=()=>false}={}){
 const registry=D.createRegistry(definitions,{catalog,monsters,targets});if(!registry.ok)throw new TypeError(registry.code);
 let state=S.normalize(raw,registry),revision=0,epoch=0,busy=false;const tickets=new WeakMap(),seen=new WeakSet(),events=[];
 const record=e=>{events.push(e);if(events.length>64)events.shift()};
 const context=c=>c&&typeof c==='object'&&owner.getCurrentHP()>0&&!c.transitionPending&&!c.loading&&!c.retired&&!c.restricted;
 function inspect(id){const d=registry.getDefinition(id);return d?S.evaluate(state,d,owner.getInventory(),catalog):fail('UNKNOWN_QUEST')}
 function canAccept(id,c){if(!context(c))return fail('FORBIDDEN_QUEST_CONTEXT');const result=inspect(id);return !result.ok?result:result.status==='AVAILABLE'?result:fail(result.status==='COMPLETED'?'QUEST_COMPLETED':result.status==='LOCKED'?'QUEST_LOCKED':'QUEST_ALREADY_ACCEPTED')}
 function accept(id,c){if(busy)return fail('TRANSACTION_IN_PROGRESS');const result=canAccept(id,c);if(!result.ok)return result;const d=registry.getDefinition(id),progress=Object.fromEntries(d.objectives.filter(o=>o.type!=='COLLECT').map(o=>[o.id,0]));state=freeze({...state,entries:{...state.entries,[id]:{status:'ACTIVE',progress}}});revision++;const receipt=freeze({ok:true,questId:id,fromState:'AVAILABLE',...inspect(id)});record(receipt);return receipt}
 function observe(e,type,verify){
  if(busy)return fail('TRANSACTION_IN_PROGRESS');let authorized=false;try{authorized=!!e&&typeof e==='object'&&verify(e)===true&&e.type===type}catch{return fail('INVALID_QUEST_EVIDENCE')}if(!authorized)return fail('INVALID_QUEST_EVIDENCE');if(seen.has(e))return fail('DUPLICATE_QUEST_EVIDENCE');seen.add(e);
  const entries={...state.entries},changed=[];
  for(const id of registry.ids){const entry=entries[id];if(!entry||entry.status==='COMPLETED')continue;const d=registry.getDefinition(id),progress={...entry.progress};let touched=false;
   for(const o of d.objectives)if((o.type==='TALK'&&type==='NPC_INTERACTED'&&o.targetId===e.targetId||o.type==='KILL'&&type==='MONSTER_DIED'&&o.monsterDefinitionId===e.monsterDefinitionId)&&progress[o.id]<o.required){progress[o.id]++;touched=true}
   if(touched){entries[id]={...entry,progress};changed.push(id)}
  }
  if(changed.length){state=freeze({...state,entries});revision++}
  const result=freeze({ok:true,type,evidence:e,changedQuestIds:changed,revision});record(result);return result;
 }
 function plan(id,c){
  if(!context(c))return fail('FORBIDDEN_QUEST_CONTEXT');const result=inspect(id);if(!result.ok)return result;if(result.status!=='READY_TO_TURN_IN')return fail(result.status==='COMPLETED'?'QUEST_COMPLETED':'QUEST_NOT_READY');
  const d=registry.getDefinition(id);let permitted=false;try{permitted=isTalkEvidence(c.interaction)===true&&c.interaction.targetId===d.turnInTargetId}catch{}if(!permitted)return fail('WRONG_TURN_IN_TARGET');
  const amounts={};for(const o of d.objectives)if(o.type==='COLLECT'&&o.consumeOnTurnIn)amounts[o.itemId]=(amounts[o.itemId]||0)+o.required;
  const stackDebits=[],instanceDebits=[];for(const [itemId,quantity] of Object.entries(amounts)){
   const definition=catalog.getDefinition(itemId);if(definition.stackable)stackDebits.push({itemId,quantity});else{const candidates=Object.values(owner.getInventory().instances).filter(i=>i.definitionId===itemId&&!Object.values(owner.getEquipment()).includes(i.instanceId));if(candidates.length<quantity)return fail('ITEM_EQUIPPED');instanceDebits.push(...candidates.slice(0,quantity).map(i=>i.instanceId))}
  }
  const transaction={stackDebits,instanceDebits,itemRewards:d.rewards.items},preflight=owner.preflight(transaction,d.rewards);if(!preflight.ok)return preflight;
  return freeze({ok:true,questId:id,objectiveState:result,transaction,rewards:d.rewards,preflight});
 }
 function prepare(id,c){if(busy)return fail('TRANSACTION_IN_PROGRESS');busy=true;try{const p=plan(id,c);if(!p.ok)return p;const ticket=freeze({...p,type:'QUEST_TURN_IN'});tickets.set(ticket,{state,revision,epoch,inventory:owner.getInventory(),inventoryRevision:owner.getInventoryRevision(),rewardIdentity:owner.rewardIdentity(),used:false});return ticket}finally{busy=false}}
 function commit(ticket,c){
  const bound=ticket&&typeof ticket==='object'?tickets.get(ticket):null;if(!bound)return fail('INVALID_QUEST_TICKET');if(bound.used)return fail('ALREADY_COMMITTED');if(busy)return fail('TRANSACTION_IN_PROGRESS');
  if(bound.state!==state||bound.revision!==revision||bound.epoch!==epoch||bound.inventory!==owner.getInventory()||bound.inventoryRevision!==owner.getInventoryRevision()||bound.rewardIdentity!==owner.rewardIdentity())return fail('STALE_QUEST_TICKET');
  busy=true;try{
   const current=plan(ticket.questId,c);if(!current.ok)return current;
   const {type,...original}=ticket;if(JSON.stringify(current)!==JSON.stringify(original))return fail('STALE_QUEST_TICKET');
   const next=freeze({...state,entries:{...state.entries,[ticket.questId]:{...state.entries[ticket.questId],status:'COMPLETED'}}});
   const result=owner.commit(current.transaction,current.rewards,bound.inventory,bound.inventoryRevision,()=>{state=next;revision++;bound.used=true;epoch++;return true});
   if(result?.ok!==true)return result||fail('QUEST_REWARD_REJECTED');
   const receipt=freeze({...result,ok:true,committed:true,questId:ticket.questId,status:'COMPLETED',consumption:current.transaction,rewards:current.rewards});record(receipt);return receipt;
  }finally{busy=false}
 }
 return freeze({registry,getState:()=>state,inspect,list:()=>freeze(registry.ids.map(inspect)),canAccept,accept,observeTalk:e=>observe(e,'NPC_INTERACTED',isTalkEvidence),observeKill:e=>observe(e,'MONSTER_DIED',isKillEvidence),prepare,commit,turnIn:(id,c)=>{const p=prepare(id,c);return p.ok?commit(p,c):p},invalidate:()=>{if(busy)return fail('TRANSACTION_IN_PROGRESS');epoch++;return freeze({ok:true})},snapshot:()=>freeze({state,revision,epoch,events:[...events]})});
}
window.AstraeonQuestRuntime=freeze({create});
})();
