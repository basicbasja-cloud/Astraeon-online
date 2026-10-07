/* Owned execution tickets and explicit-time item/function/global cooldowns. */
(() => {
'use strict';
const D=window.AstraeonItemDefinitions,freeze=D.freeze,A=window.AstraeonActionItem,F=window.AstraeonItemEffects;
const fail=(code,detail={})=>freeze({ok:false,code,blockedReason:code,consumed:false,...detail});
const finite=value=>Number.isFinite(value)&&value>=0;
function create(owner,{catalog=D,config=window.AstraeonActionItemConfig,restrictions=()=>true}={}){
 config=freeze(structuredClone(config));const items=new Map(),groups=new Map(),tickets=new WeakMap();let globalReadyAt=0,lastCommitAt=0,revision=0,inFlight=false,checking=false;
 function getState(itemId,context={}){
  if(!context||typeof context!=='object'||!finite(context.now)||context.now<lastCommitAt)return fail('INVALID_CONTEXT');
  for(const key of ['actorPresent','menuOpen','transitionPending','restricted','actionActive'])if(context[key]!==undefined&&typeof context[key]!=='boolean')return fail('INVALID_CONTEXT');
  if(context.intent!==undefined&&!['action','inventory'].includes(context.intent)||context.state!==undefined&&!['town','field','dungeon'].includes(context.state))return fail('INVALID_CONTEXT');
  const compiled=A.compile(itemId,catalog,config);if(!compiled.ok)return fail(compiled.code);const descriptor=compiled.descriptor;
  const quantity=owner.getQuantity(itemId),resources=owner.getResources();
  const readyAt=Math.max(items.get(itemId)||0,descriptor.cooldownGroup?groups.get(descriptor.cooldownGroup)||0:0,globalReadyAt);
  let blockedReason=null,plan;
  if(!Number.isSafeInteger(quantity)||quantity<0)blockedReason='INVALID_INVENTORY';
  else if(quantity===0)blockedReason='INSUFFICIENT_ITEMS';
  else if(context.actorPresent===false||!resources)blockedReason='NO_ACTOR';
  else if(!F.validResources(resources))blockedReason='INVALID_RESOURCE';
  else if(resources.currentHP===0)blockedReason='DEAD';
  else if(inFlight||checking||context.transitionPending||context.restricted)blockedReason='FORBIDDEN_STATE';
  else if(context.menuOpen&&context.intent!=='inventory')blockedReason='MENU_OPEN';
  else if(!descriptor.usableStates.includes(context.state||'town'))blockedReason='UNUSABLE_STATE';
  else{
   checking=true;try{const result=restrictions(descriptor,freeze({...context}),freeze({...resources}));if(result!==true)blockedReason=typeof result?.code==='string'?result.code:'ITEM_RESTRICTION'}catch{blockedReason='ITEM_RESTRICTION'}finally{checking=false}
   if(!blockedReason){plan=F.plan(descriptor.effects,resources);if(!plan.ok)blockedReason=plan.code;else if(!plan.changed)blockedReason='FULL_RESOURCES';else if(context.now<readyAt)blockedReason='COOLDOWN'}
  }
  return freeze({ok:true,itemId,source:'actionItem',descriptor,quantity,eligible:!blockedReason,blockedReason,readyAt,cooldownRemaining:Math.max(0,readyAt-context.now),plan:plan||null});
 }
 function prepare(itemId,context){
  const state=getState(itemId,context);if(!state.ok)return state;if(!state.eligible)return fail(state.blockedReason,{state});
  const value=freeze({ok:true,itemId,source:'actionItem',descriptor:state.descriptor,preparedAt:context.now,quantityBefore:state.quantity,plan:state.plan});
  tickets.set(value,{revision,inventory:owner.getInventory(),signature:JSON.stringify([state.descriptor,state.plan]),used:false});return value;
 }
 function commit(value,context){
  const ticket=value&&typeof value==='object'?tickets.get(value):null;
  if(!ticket)return fail('INVALID_PACKAGE');if(ticket.used)return fail('ALREADY_COMMITTED');if(inFlight||checking)return fail('FORBIDDEN_STATE');
  if(ticket.revision!==revision||ticket.inventory!==owner.getInventory())return fail('STALE_PACKAGE');
  if(!context||!finite(context.now)||context.now<value.preparedAt)return fail('INVALID_CONTEXT');
  const state=getState(value.itemId,context);if(!state.ok)return state;if(!state.eligible)return fail(state.blockedReason);
  if(JSON.stringify([state.descriptor,state.plan])!==ticket.signature)return fail('STALE_PACKAGE');
  const d=value.descriptor,readyAt=context.now+d.cooldownDuration,groupReadyAt=context.now+d.groupCooldown,nextGlobal=context.now+config.globalCooldown;
  if(![readyAt,groupReadyAt,nextGlobal].every(finite))return fail('INVALID_CONTEXT');
  let result;inFlight=true;try{result=owner.commit(value.itemId,ticket.inventory,value.plan)}catch{result={ok:false,code:'EFFECT_COMMIT_REJECTED'}}finally{inFlight=false}
  if(result?.ok!==true)return fail(result?.code||'EFFECT_COMMIT_REJECTED');
  ticket.used=true;revision++;items.set(value.itemId,readyAt);if(d.cooldownGroup)groups.set(d.cooldownGroup,groupReadyAt);globalReadyAt=Math.max(globalReadyAt,nextGlobal);lastCommitAt=context.now;
  return freeze({ok:true,source:'actionItem',itemId:value.itemId,consumed:true,quantityBefore:value.quantityBefore,quantityAfter:value.quantityBefore-1,resourceBefore:value.plan.resourceBefore,resourceAfter:value.plan.resourceAfter,effectResults:value.plan.effectResults,cooldownGroup:d.cooldownGroup,cooldownStarted:true,readyAt,groupReadyAt,globalReadyAt,metadata:d.metadata});
 }
 const request=(itemId,context)=>{const value=prepare(itemId,context);return value.ok?commit(value,context):value};
 function invalidatePrepared(){if(inFlight||checking)return fail('FORBIDDEN_STATE');revision++;return freeze({ok:true})}
 function resetCooldowns(){const result=invalidatePrepared();if(!result.ok)return result;items.clear();groups.clear();globalReadyAt=0;return freeze({ok:true})}
 const snapshot=()=>freeze({source:'actionItem',items:Object.fromEntries(items),groups:Object.fromEntries(groups),globalReadyAt,lastCommitAt});
 return freeze({getState,prepare,commit,request,invalidatePrepared,resetCooldowns,snapshot});
}
window.AstraeonActionItemRuntime=freeze({create});
})();
