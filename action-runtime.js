/* Explicit time and one launch/commit boundary; no DOM, world, damage or clock reads. */
(() => {
'use strict';
const model=window.AstraeonActionLoadout;
const freeze=value=>{if(value&&typeof value==='object'){Object.values(value).forEach(freeze);Object.freeze(value)}return value};
const fail=(code,detail={})=>freeze({ok:false,code,...detail});
const finite=value=>Number.isFinite(value)&&value>=0;
// Extension hooks only. No new production global/group cooldown is enabled.
const defaults=freeze({globalCooldown:0,inCombatChange:'maxAuthoredDuration'});
function create(owner,config=defaults){
 config=freeze(structuredClone(config));
 const actions=new Map(),groups=new Map(),tickets=new WeakMap();let globalReadyAt=0,loadoutReadyAt=0,revision=0,inFlight=false;
 const configValid=finite(config?.globalCooldown)&&config?.inCombatChange==='maxAuthoredDuration';
 const compile=slot=>{
  const skillId=owner.getLoadout()[slot],definition=window.AstraeonSkillDefinitions.getDefinition(skillId);
  if(skillId!==null){
   if(!definition||definition.type!=='active'||!definition.loadoutAssignable)return {skillId,blockedReason:'INVALID_SKILL'};
   if(definition.classId!==owner.getClassId())return {skillId,sourceClass:definition.classId,learnedRank:owner.getRank(skillId),blockedReason:'WRONG_CLASS'};
   const rank=owner.getRank(skillId);if(!rank)return {skillId,sourceClass:definition.classId,learnedRank:0,blockedReason:'NOT_LEARNED'};
   const action=window.AstraeonSkillRuntime.compile(skillId,rank,owner.getNodes()[skillId]);
   return {skillId,sourceClass:definition.classId,learnedRank:rank,node:action?.node??null,source:'learned',action,blockedReason:action?null:'INVALID_RUNTIME'};
  }
  const action=owner.getLegacyAction?.(slot);
  return action?{skillId:action.id,source:'legacy',sourceClass:owner.getClassId(),learnedRank:null,node:action.node??null,action,blockedReason:null}:{skillId:null,source:null,learnedRank:0,node:null,blockedReason:'EMPTY_SLOT'};
 };
 const duration=action=>Math.max(action.cooldown,action.castTime+action.activeTime+action.recovery);
 const finiteData=value=>value&&typeof value==='object'?Object.values(value).every(finiteData):typeof value!=='number'||Number.isFinite(value);
 const validAction=action=>action&&finiteData(action)&&typeof action.id==='string'&&action.id&&['cost','cooldown','castTime','activeTime','recovery','range','damage'].every(key=>finite(action[key]))&&finite(duration(action))&&(action.cooldownGroup===undefined||typeof action.cooldownGroup==='string')&&(action.groupCooldown===undefined||finite(action.groupCooldown));
 function getSlotState(slot,context={}){
  if(!model.validSlot(slot))return fail('INVALID_SLOT');if(!configValid||!finite(context.now))return fail('INVALID_CONTEXT');
  if(!model.valid(owner.getLoadout()))return fail('INVALID_STATE');
  let value;try{value=compile(slot)}catch{return fail('INVALID_RUNTIME')};const action=value.action,now=context.now;
  const readyAt=Math.max(action?actions.get(action.id)||0:0,action?.cooldownGroup?groups.get(action.cooldownGroup)||0:0,globalReadyAt,loadoutReadyAt);
  const currentHP=owner.getCurrentHP(),resource=owner.getResource();
  let blockedReason=value.blockedReason;
  if(!blockedReason&&!validAction(action))blockedReason='INVALID_RUNTIME';
  if(!blockedReason&&(!finite(currentHP)||!finite(resource)))blockedReason='INVALID_RESOURCE';
  if(!blockedReason&&currentHP===0)blockedReason='DEAD';
  if(!blockedReason&&(context.actionActive||context.menuOpen||context.transitionPending||context.restricted||inFlight))blockedReason='FORBIDDEN_STATE';
  if(!blockedReason&&resource<action.cost)blockedReason='RESOURCE';
  if(!blockedReason&&now<readyAt)blockedReason='COOLDOWN';
  return freeze({ok:true,slot,...value,action:action?structuredClone(action):null,eligible:!blockedReason,blockedReason,readyAt,cooldownRemaining:Math.max(0,readyAt-now),cost:action?.cost??null,resourceAffordable:!!action&&finite(resource)&&resource>=action.cost});
 }
 function prepareAction(slot,context){
  const state=getSlotState(slot,context);if(!state.ok)return state;if(!state.eligible)return fail(state.blockedReason,{slot,state});
  const packageValue=freeze({ok:true,slot,skillId:state.skillId,source:state.source,learnedRank:state.learnedRank,node:state.node,action:state.action,cost:state.cost,preparedAt:context.now,cooldownDuration:duration(state.action)});
  tickets.set(packageValue,{revision,signature:JSON.stringify(state.action),classId:owner.getClassId(),used:false});return packageValue;
 }
 function commitAction(packageValue,context,launch,{castTime=packageValue?.action?.castTime}={}){
  const ticket=tickets.get(packageValue);if(!ticket)return fail('INVALID_PACKAGE');if(ticket.used)return fail('ALREADY_COMMITTED');if(inFlight)return fail('FORBIDDEN_STATE');
  if(ticket.revision!==revision||ticket.classId!==owner.getClassId())return fail('STALE_PACKAGE');
  const state=getSlotState(packageValue.slot,context);if(!state.ok)return state;if(!state.eligible)return fail(state.blockedReason,{slot:packageValue.slot});
  if(JSON.stringify(state.action)!==ticket.signature)return fail('STALE_PACKAGE');
  if(context.now<packageValue.preparedAt||!finite(castTime)||castTime<packageValue.action.castTime||typeof launch!=='function')return fail('INVALID_CONTEXT');
  const action=packageValue.action,cooldownDuration=Math.max(action.cooldown,castTime+action.activeTime+action.recovery),readyAt=context.now+cooldownDuration;
  const groupReadyAt=context.now+(action.groupCooldown??cooldownDuration),nextGlobal=context.now+config.globalCooldown;
  if(!finite(readyAt)||!finite(groupReadyAt)||!finite(nextGlobal))return fail('INVALID_CONTEXT');
  const resourceBefore=owner.getResource(),resourceAfter=resourceBefore-action.cost;
  let accepted;inFlight=true;try{accepted=launch(action)===true}catch{accepted=false}finally{inFlight=false}
  if(!accepted)return fail('LAUNCH_REJECTED');
  // The trusted synchronous launch adapter starts Timeline only. Private Character's
  // finite SP setter cannot fail here; no owner callback may spend resources itself.
  owner.setResource(resourceAfter);actions.set(action.id,readyAt);if(action.cooldownGroup)groups.set(action.cooldownGroup,groupReadyAt);globalReadyAt=Math.max(globalReadyAt,nextGlobal);ticket.used=true;
  return freeze({ok:true,slot:packageValue.slot,skillId:packageValue.skillId,source:packageValue.source,resourceBefore,resourceAfter,cost:action.cost,cooldownDuration,readyAt,action});
 }
 function requestAction(slot,context,launch,options){const prepared=prepareAction(slot,context);return prepared.ok?commitAction(prepared,context,launch,options):prepared}
 function configurationChanged(before,after,{now=0,inCombat=false}={}){
  if(inFlight)return fail('FORBIDDEN_STATE');if(!configValid||!finite(now)||typeof inCombat!=='boolean')return fail('INVALID_CONTEXT');
  if(!model.valid(before)||!model.valid(after))return fail('INVALID_STATE');
  let lockDuration=0;
  if(inCombat){
   // Authored maximum, not a newly invented fixed MMO cooldown value. Includes
   // emptied/dormant slots and cannot shorten an existing lock.
   try{for(const id of new Set([...before,...after])){if(id===null)continue;const action=window.AstraeonSkillRuntime.compile(id,Math.max(1,owner.getRank(id)),owner.getNodes()[id]);if(!validAction(action))return fail('INVALID_RUNTIME');lockDuration=Math.max(lockDuration,duration(action))}}catch{return fail('INVALID_RUNTIME')}
   if(!finite(now+lockDuration))return fail('INVALID_CONTEXT');
  }
  revision++;if(inCombat)loadoutReadyAt=Math.max(loadoutReadyAt,now+lockDuration);return freeze({ok:true,loadoutReadyAt,lockDuration});
 }
 function resetCooldowns(){if(inFlight)return fail('FORBIDDEN_STATE');actions.clear();groups.clear();globalReadyAt=0;loadoutReadyAt=0;revision++;return freeze({ok:true})}
 // Death/cancel/zone/class changes invalidate outstanding preparations; authored
 // cooldowns remain on the same simulation timeline. A reload creates fresh state.
 function invalidatePrepared(){if(inFlight)return fail('FORBIDDEN_STATE');revision++;return freeze({ok:true})}
 const snapshot=()=>freeze({actions:Object.fromEntries(actions),groups:Object.fromEntries(groups),globalReadyAt,loadoutReadyAt});
 return Object.freeze({getSlotState,prepareAction,commitAction,requestAction,configurationChanged,resetCooldowns,invalidatePrepared,snapshot});
}
window.AstraeonActionRuntime=Object.freeze({defaults,create});
})();
