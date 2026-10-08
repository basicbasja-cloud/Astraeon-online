/* Derived ownership capacity. No inventory publication, RNG, clock or save fields. */
(() => {
'use strict';
const D=window.AstraeonItemDefinitions,I=window.AstraeonItemInventory,freeze=D.freeze;
const scale=1000; // Authored weights use at most three decimal places.
const integer=(n,min=0)=>Number.isSafeInteger(n)&&n>=min;
const plain=v=>!!v&&typeof v==='object'&&!Array.isArray(v)&&(Object.getPrototypeOf(v)===Object.prototype||Object.getPrototypeOf(v)===null);
function json(v,seen=new Set(),depth=0){if(depth>64)return false;if(v===null||['string','boolean'].includes(typeof v))return true;if(typeof v==='number')return Number.isFinite(v);if(!Array.isArray(v)&&!plain(v)||seen.has(v))return false;seen.add(v);const ok=Object.values(v).every(x=>json(x,seen,depth+1));seen.delete(v);return ok}
const fail=(code,detail={})=>freeze({ok:false,code,blockedReason:code,...detail});
function units(n){const scaled=n*scale,rounded=Math.round(scaled);return Number.isFinite(n)&&n>=0&&integer(rounded)&&Math.abs(scaled-rounded)<=1e-7?rounded:null}
const defaultPolicy=freeze({mode:'bounded',slotLimit:100,weightLimit:1000,overLimitPolicy:'no-worse',metadata:{balance:'provisional; preserves ordinary prototype loop',weightPrecision:3}});
function validatePolicy(policy){
 if(!plain(policy)||!json(policy)||Object.keys(policy).some(k=>!['mode','slotLimit','weightLimit','overLimitPolicy','metadata'].includes(k))||policy.overLimitPolicy!=='no-worse')return fail('INVALID_CAPACITY_POLICY');
 if(policy.mode==='unlimited'){if(policy.slotLimit!==null||policy.weightLimit!==null)return fail('INVALID_CAPACITY_POLICY')}
 else if(policy.mode!=='bounded'||!integer(policy.slotLimit)||units(policy.weightLimit)===null)return fail('INVALID_CAPACITY_POLICY');
 return freeze({ok:true,policy:structuredClone(policy)});
}
function counts(inventory,catalog){
 if(!I.valid(inventory,catalog))return fail('INVALID_INVENTORY');
 const stacks={...inventory.stacks},instances={};for(const item of Object.values(inventory.instances))instances[item.definitionId]=(instances[item.definitionId]||0)+1;
 return {ok:true,stacks,instances};
}
function measure(owned,policy,catalog,extraInstances=0,extraWeight=0){
 let stackSlots=0,instanceSlots=extraInstances,weightUnits=extraWeight;
 for(const [stack,map] of [[true,owned.stacks],[false,owned.instances]])for(const [id,count] of Object.entries(map)){
  if(!integer(count))return fail('INVALID_QUANTITY');if(!count)continue;
  const definition=catalog.getDefinition(id),unit=units(definition?.weight);if(unit===null)return fail('INVALID_WEIGHT',{itemId:id});
  const added=unit*count;if(!integer(added)||!integer(weightUnits+added))return fail('WEIGHT_OVERFLOW');weightUnits+=added;
  if(stack)stackSlots++;else instanceSlots+=count;
 }
 const occupiedSlots=stackSlots+instanceSlots;if(!integer(occupiedSlots))return fail('SLOT_OVERFLOW');
 const bounded=policy.mode==='bounded',limitUnits=bounded?units(policy.weightLimit):null;
 const isSlotOverLimit=bounded&&occupiedSlots>policy.slotLimit,isWeightOverLimit=bounded&&weightUnits>limitUnits;
 return freeze({ok:true,policy,slotLimit:policy.slotLimit,weightLimit:policy.weightLimit,occupiedSlots,stackSlots,instanceSlots,totalWeight:weightUnits/scale,currentWeight:weightUnits/scale,weightUnits,freeSlots:bounded?Math.max(0,policy.slotLimit-occupiedSlots):null,remainingWeight:bounded?Math.max(0,limitUnits-weightUnits)/scale:null,isSlotOverLimit,isWeightOverLimit,isOverLimit:isSlotOverLimit||isWeightOverLimit,isOverweight:isWeightOverLimit});
}
function snapshot(inventory,{policy=defaultPolicy,catalog=D}={}){const p=validatePolicy(policy);if(!p.ok)return p;const owned=counts(inventory,catalog);return owned.ok?measure(owned,p.policy,catalog):owned}
function compare(before,after){
 if(!before.ok)return before;if(!after.ok)return after;
 const result={before,after,delta:{slots:after.occupiedSlots-before.occupiedSlots,weight:(after.weightUnits-before.weightUnits)/scale},isOverLimitBefore:before.isOverLimit,isOverLimitAfter:after.isOverLimit};
 if(before.policy.mode==='bounded')for(const [dimension,value,prior,limit,code] of [['slots',after.occupiedSlots,before.occupiedSlots,before.slotLimit,'SLOT_LIMIT_EXCEEDED'],['weight',after.weightUnits,before.weightUnits,units(before.weightLimit),'WEIGHT_LIMIT_EXCEEDED']])if(value>Math.max(prior,limit))return fail(prior>limit?'OVER_LIMIT_WORSENED':code,{...result,dimension});
 return freeze({ok:true,...result});
}
function evaluateOwnership(beforeInventory,afterInventory,options={}){return compare(snapshot(beforeInventory,options),snapshot(afterInventory,options))}
// Ephemeral definition counts simulate final ownership without allocating IDs.
// envelope.maximumRewards may contain mutually exclusive possibilities: sum
// stack maxima/weights conservatively, but use its proven max instance count.
function evaluate(inventory,transaction={},options={}){
 const {policy=defaultPolicy,catalog=D,equipment={}}=options,before=snapshot(inventory,{policy,catalog});if(!before.ok)return before;
 if(!plain(transaction)||!json(transaction)||Object.keys(transaction).some(k=>!['stackDebits','instanceDebits','itemRewards'].includes(k)))return fail('INVALID_PACKAGE');
 const owned=counts(inventory,catalog);const debitStacks=Object.hasOwn(transaction,'stackDebits')?transaction.stackDebits:[],debitInstances=Object.hasOwn(transaction,'instanceDebits')?transaction.instanceDebits:[],rewards=Object.hasOwn(transaction,'itemRewards')?transaction.itemRewards:[];
 if(![debitStacks,debitInstances,rewards].every(Array.isArray))return fail('INVALID_PACKAGE');
 for(const debit of debitStacks){const d=catalog.getDefinition(debit?.itemId),n=debit?.quantity;if(!d?.stackable||!integer(n,1))return fail('INVALID_STACK_ITEM');if(n>(owned.stacks[d.id]||0))return fail('INSUFFICIENT_ITEMS');owned.stacks[d.id]-=n}
 const removed=new Set();for(const id of debitInstances){const item=inventory.instances[id];if(!item||removed.has(id))return fail('UNKNOWN_INSTANCE');if(Object.values(equipment).includes(id))return fail('ITEM_EQUIPPED');removed.add(id);owned.instances[item.definitionId]--}
 let instanceUnits=0,instanceWeight=0;
 for(const reward of rewards){const d=catalog.getDefinition(reward?.itemId),n=reward?.quantity;if(!d||!integer(n,1))return fail('INVALID_ITEM_REWARD');const unit=units(d.weight);if(unit===null)return fail('INVALID_WEIGHT',{itemId:d.id});
  if(d.stackable){const count=(owned.stacks[d.id]||0)+n;if(!integer(count)||count>d.maxStack)return fail('STACK_OVERFLOW');owned.stacks[d.id]=count}
  else{instanceUnits+=n;const added=unit*n;if(!integer(added)||!integer(instanceWeight+added))return fail('WEIGHT_OVERFLOW');instanceWeight+=added}
 }
 const envelope=options.maximumInstanceUnits;
 if(envelope!==undefined&&(!integer(envelope)||envelope>instanceUnits))return fail('INVALID_PACKAGE');
 const allocated=envelope??instanceUnits;if(allocated>10000)return fail('REWARD_SIZE_LIMIT');if(allocated>Number.MAX_SAFE_INTEGER-inventory.nextItemSerial)return fail('SERIAL_EXHAUSTED');
 return compare(before,measure(owned,before.policy,catalog,allocated,instanceWeight));
}
function envelope(inventory,source,bounds,options={}){
 if(!bounds?.ok||!Array.isArray(bounds.maximumRewards)||!integer(bounds.maximumInstanceUnits))return fail('INVALID_PACKAGE');
 return evaluate(inventory,{stackDebits:[{itemId:source?.itemId,quantity:source?.count}],itemRewards:bounds.maximumRewards},{...options,maximumInstanceUnits:bounds.maximumInstanceUnits});
}
window.AstraeonInventoryCapacity=freeze({scale,defaultPolicy,validatePolicy,snapshot,evaluate,evaluateOwnership,envelope});
})();
