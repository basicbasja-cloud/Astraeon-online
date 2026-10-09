/* Private canonical ownership and contained prototype compatibility/transactions. */
(() => {
'use strict';
const D=window.AstraeonItemDefinitions,I=window.AstraeonItemInventory,E=window.AstraeonItemEquipment,freeze=D.freeze;
const object=value=>!!value&&typeof value==='object'&&!Array.isArray(value);
class MigrationError extends Error{constructor(){super('Legacy equipment inventory exceeds the bounded import size. Original save has been preserved.');this.code='ITEM_MIGRATION_LIMIT'}}
function migrate(raw,catalog=D){
 const history=object(raw.itemHistory)?structuredClone(raw.itemHistory):{inventory:{},equipment:{}};
 let inventory,equipment;
 if(Object.hasOwn(raw,'itemInventory')){
  inventory=I.normalize(raw.itemInventory||{},catalog);const normalized=E.normalizeDetailed(inventory,raw.equippedItems,catalog);equipment=normalized.equipment;
  if(normalized.issues.length&&!history.equipmentSlotNormalization)history.equipmentSlotNormalization=normalized.issues;
 }else{
  history.inventory=structuredClone(raw.inventory||{});history.equipment=structuredClone(raw.equipment||{});
  inventory=I.normalize({},catalog);
  let imported=0;
  for(const [key,id] of Object.entries(D.legacyCounters)){
   const count=raw.inventory?.[key];if(!Number.isSafeInteger(count)||count<=0)continue;
   const d=catalog.getDefinition(id);if(d.stackable){const result=I.addStack(inventory,id,count,catalog);if(result.ok)inventory=result.inventory;continue}
   // Technical import guard, not a final gameplay slot/weight restriction.
   if(imported+count>10000)throw new MigrationError();imported+=count;
   for(let index=0;index<count;index++){const result=I.createInstance(inventory,id,{legacyCounter:key},catalog);if(!result.ok)throw new MigrationError();inventory=result.inventory}
  }
  equipment=Object.fromEntries(E.slots.map(slot=>[slot,null]));
  for(const slot of E.slots){
   const semantic=window.AstraeonEquipmentSlots.getDefinition(slot).semanticId,name=Object.hasOwn(raw.equipment||{},slot)?raw.equipment[slot]:raw.equipment?.[semantic],id=Object.hasOwn(D.legacyNames,name)?D.legacyNames[name]:null,d=catalog.getDefinition(id),checked=E.validateDefinition(d);
   if(!checked.ok||!checked.allowedSlots.includes(slot))continue;
   let owned=Object.values(inventory.instances).find(item=>item.definitionId===id&&!Object.values(equipment).includes(item.instanceId));
   if(!owned){const result=I.createInstance(inventory,id,{legacyEquippedOnly:true},catalog);if(!result.ok)throw new MigrationError();inventory=result.inventory;owned=result.instance}
   equipment[slot]=owned.instanceId;
  }
  equipment=E.normalizeSlots(inventory,equipment,catalog);
 }
 return freeze({itemInventory:inventory,equippedItems:equipment,itemHistory:history});
}
function legacyInventory(inventory,history={},catalog=D){
 const result={...(history.inventory||{})};
 for(const [key,id] of Object.entries(D.legacyCounters)){
  const d=catalog.getDefinition(id);result[key]=d.stackable?I.getQuantity(inventory,id):Object.values(inventory.instances).filter(item=>item.definitionId===id&&!item.metadata.legacyEquippedOnly).length;
 }
 return freeze(result);
}
function legacyEquipment(inventory,equipment,history={},catalog=D){
 const result={...(history.equipment||{})};
 for(const slot of E.legacySlots){const d=catalog.getDefinition(inventory.instances[equipment[slot]]?.definitionId),old=history.equipment?.[slot];result[slot]=d?.name||(typeof old==='string'&&old!=='None'&&!Object.hasOwn(D.legacyNames,old)?old:'None')}
 return freeze(result);
}
function installMirrors(state,normalized,catalog=D){Object.assign(state,normalized);state.inventory=legacyInventory(state.itemInventory,state.itemHistory,catalog);state.equipment=legacyEquipment(state.itemInventory,state.equippedItems,state.itemHistory,catalog);return state}
function create(raw,{catalog=D,onChange=()=>{},requirements=()=>true,getCapacityPolicy=()=>window.AstraeonInventoryCapacity.defaultPolicy}={}){
 const C=window.AstraeonInventoryCapacity;if(!C)throw new TypeError('Inventory capacity authority is required');
 const initial=migrate(raw,catalog);let inventory=initial.itemInventory,equipment=initial.equippedItems,history=initial.itemHistory,committing=false,revision=0;
 const capacityOptions=()=>{let policy;try{policy=getCapacityPolicy()}catch{policy=null}return {catalog,policy,equipment}};
 const preflight=transaction=>committing?I.fail('TRANSACTION_IN_PROGRESS'):C.evaluate(inventory,transaction,capacityOptions());
 function equipmentCheck(check){if(committing)return I.fail('TRANSACTION_IN_PROGRESS');committing=true;try{return check()}finally{committing=false}}
 function commit(result,nextEquipment=equipment,beforePublish){
  if(committing)return I.fail('TRANSACTION_IN_PROGRESS');
  if(!result.ok)return result;const nextInventory=result.inventory||inventory;
  const capacity=C.evaluateOwnership(inventory,nextInventory,capacityOptions());if(!capacity.ok)return capacity;
  committing=true;
  try{
   try{onChange(nextInventory,nextEquipment)}catch{return I.fail('INVALID_EQUIPMENT_MODIFIERS')}
   if(beforePublish){try{if(beforePublish()!==true)return I.fail('EFFECT_COMMIT_REJECTED')}catch{return I.fail('EFFECT_COMMIT_REJECTED')}}
   inventory=nextInventory;equipment=nextEquipment;revision++;return freeze({...result,inventory,equipment,capacity});
  }finally{committing=false}
 }
 function planRewards(start,rewards){
  if(!Array.isArray(rewards))return I.fail('INVALID_REWARD_PACKAGE');
  let next=start,units=0;const stackRewards=[],instanceRewards=[];
  for(const reward of rewards){
   const d=catalog.getDefinition(reward?.itemId),quantity=reward?.quantity;
   if(!d||!Number.isSafeInteger(quantity)||quantity<=0)return I.fail('INVALID_ITEM_REWARD');
   if(d.stackable){const before=I.getQuantity(next,d.id),r=I.addStack(next,d.id,quantity,catalog);if(!r.ok)return r;next=r.inventory;stackRewards.push({itemId:d.id,quantity,quantityBefore:before,quantityAfter:I.getQuantity(next,d.id)})}
   else{units+=quantity;if(units>10000)return I.fail('REWARD_SIZE_LIMIT');for(let i=0;i<quantity;i++){const r=I.createInstance(next,d.id,{},catalog);if(!r.ok)return r;next=r.inventory;instanceRewards.push(r.instance)}}
  }
  return {ok:true,inventory:next,stackRewards,instanceRewards,serialBefore:start.nextItemSerial,serialAfter:next.nextItemSerial};
 }
 const api={getInventory:()=>inventory,getEquipment:()=>E.legacyView(equipment),getEquipmentSlots:()=>equipment,getEquipmentSlotRegistry:()=>window.AstraeonEquipmentSlots.definitions,getHistory:()=>history,getRevision:()=>revision,
  getQuantity:id=>I.getQuantity(inventory,id),getInstance:id=>Object.hasOwn(inventory.instances,id)?inventory.instances[id]:null,
  getEquipped:slot=>equipment[window.AstraeonEquipmentSlots.canonical(slot)]??null,
  getEquipmentModifiers:()=>E.modifiers(inventory,equipment,catalog),getCarriedWeight:()=>{const result=C.snapshot(inventory,capacityOptions());return result.ok?freeze({ok:true,weight:result.totalWeight}):result},
  getInventoryCapacityState:()=>C.snapshot(inventory,capacityOptions()),canAcceptItemPackage:preflight,
  getEquipmentEffects:()=>E.effects(inventory,equipment,catalog),
  canAddStack:(id,count)=>{const checked=I.canAddStack(inventory,id,count,catalog);if(!checked.ok)return checked;const capacity=preflight({itemRewards:[{itemId:id,quantity:count}]});return capacity.ok?freeze({...checked,capacity}):capacity},canRemoveStack:(id,count)=>I.canRemoveStack(inventory,id,count,catalog),
  addStack:(id,count)=>commit(I.addStack(inventory,id,count,catalog)),removeStack:(id,count)=>commit(I.removeStack(inventory,id,count,catalog)),consumeStack:(id,count=1)=>commit(I.consumeStack(inventory,id,count,catalog)),
  consumeStackWithEffect(id,count,expectedInventory,apply){if(expectedInventory!==inventory)return I.fail('STALE_PACKAGE');if(typeof apply!=='function')return I.fail('EFFECT_COMMIT_REJECTED');return commit(I.consumeStack(inventory,id,count,catalog),equipment,apply)},
  grantItemPackage(rewards){const capacity=preflight({itemRewards:rewards});return capacity.ok?commit(planRewards(inventory,rewards)):capacity},
  commitItemTransaction(transaction,expectedInventory,expectedRevision,apply){
   if(committing)return I.fail('TRANSACTION_IN_PROGRESS');
   if(expectedInventory!==inventory||expectedRevision!==revision)return I.fail('STALE_PACKAGE');
   if(typeof apply!=='function')return I.fail('EFFECT_COMMIT_REJECTED');
   const capacity=preflight(transaction);if(!capacity.ok)return capacity;let next=inventory;
   for(const debit of transaction.stackDebits||[]){const result=I.removeStack(next,debit.itemId,debit.quantity,catalog);if(!result.ok)return result;next=result.inventory}
   for(const id of transaction.instanceDebits||[]){const result=I.deleteInstance(next,id,equipment,catalog);if(!result.ok)return result;next=result.inventory}
   return commit(planRewards(next,transaction.itemRewards||[]),equipment,apply);
  },
  commitRewards(rewards,apply){
   if(!Array.isArray(rewards)||typeof apply!=='function')return I.fail('INVALID_REWARD_PACKAGE');
   const capacity=preflight({itemRewards:rewards});if(!capacity.ok)return capacity;
   return commit(planRewards(inventory,rewards),equipment,apply);
  },
  canOpenable(source,bounds,preflight=()=>true){
   if(committing)return I.fail('TRANSACTION_IN_PROGRESS');
   if(!source||source.expectedInventory!==inventory||source.expectedRevision!==revision)return I.fail('STALE_PACKAGE');
   const debit=I.removeStack(inventory,source.itemId,source.count,catalog);if(!debit.ok)return debit;
   if(!bounds?.ok||!Array.isArray(bounds.maximumRewards)||!Number.isSafeInteger(bounds.maximumInstanceUnits)||bounds.maximumInstanceUnits<0)return I.fail('INVALID_REWARD_PACKAGE');
   for(const reward of bounds.maximumRewards){const d=catalog.getDefinition(reward.itemId);if(!d)return I.fail('UNKNOWN_ITEM');if(d.stackable){const checked=I.canAddStack(debit.inventory,d.id,reward.quantity,catalog);if(!checked.ok)return checked}}
   if(bounds.maximumInstanceUnits>10000)return I.fail('REWARD_SIZE_LIMIT');
   if(bounds.maximumInstanceUnits>Number.MAX_SAFE_INTEGER-inventory.nextItemSerial)return I.fail('SERIAL_EXHAUSTED');
   const capacity=C.envelope(inventory,source,bounds,capacityOptions());if(!capacity.ok)return capacity;
   // Deterministic failures for ANY supported outcome reject before entropy,
   // including after reload. This does not allocate speculative ItemInstances.
   committing=true;
   try{const accepted=preflight(freeze({source:{itemId:source.itemId,count:source.count},inventoryBefore:inventory,equipment,bounds,capacity}));return accepted===true?freeze({ok:true,capacity}):I.fail(typeof accepted?.code==='string'?accepted.code:'REWARD_PREFLIGHT_REJECTED')}
   catch{return I.fail('REWARD_PREFLIGHT_REJECTED')}finally{committing=false}
  },
  commitOpenable(source,resolve,preflight=()=>true){
   if(committing)return I.fail('TRANSACTION_IN_PROGRESS');
   if(!source||source.expectedInventory!==inventory||source.expectedRevision!==revision)return I.fail('STALE_PACKAGE');
   const d=catalog.getDefinition(source.itemId);if(!d?.stackable||!d.openable)return I.fail('NOT_OPENABLE');
   if(typeof resolve!=='function'||typeof preflight!=='function')return I.fail('INVALID_REWARD_PACKAGE');
   const debit=I.removeStack(inventory,source.itemId,source.count,catalog);if(!debit.ok)return debit;
   // Lock before RNG/acceptance callbacks. Plan against a local candidate; publish
   // source debit and ALL rewards together only after every validation succeeds.
   committing=true;
   try{
    let resolution;try{resolution=resolve()}catch{return I.fail('BOX_RESOLUTION_REJECTED')}
    if(resolution?.ok!==true)return I.fail(resolution?.code||'BOX_RESOLUTION_REJECTED');
    const capacity=C.evaluate(inventory,{stackDebits:[{itemId:source.itemId,quantity:source.count}],itemRewards:resolution.itemRewards},capacityOptions());if(!capacity.ok)return capacity;
    const result=planRewards(debit.inventory,resolution.itemRewards);if(!result.ok)return result;
    const proposal=freeze({...result,source:{itemId:source.itemId,count:source.count},inventoryBefore:inventory,equipment});
    let accepted;try{accepted=preflight(proposal)}catch{return I.fail('REWARD_PREFLIGHT_REJECTED')}
    if(accepted!==true)return I.fail(typeof accepted?.code==='string'?accepted.code:'REWARD_PREFLIGHT_REJECTED');
    try{onChange(result.inventory,equipment)}catch{return I.fail('INVALID_EQUIPMENT_MODIFIERS')}
    const quantityBefore=I.getQuantity(inventory,source.itemId);inventory=result.inventory;revision++;
    return freeze({...result,equipment,capacity,quantityBefore,quantityAfter:I.getQuantity(inventory,source.itemId)});
   }finally{committing=false}
  },
  createItemInstance(id,metadata={}){if(committing)return I.fail('TRANSACTION_IN_PROGRESS');const d=catalog.getDefinition(id);if(!d||d.stackable)return commit(I.createInstance(inventory,id,metadata,catalog));const capacity=preflight({itemRewards:[{itemId:id,quantity:1}]});return capacity.ok?commit(I.createInstance(inventory,id,metadata,catalog)):capacity},
  deleteItemInstance:id=>commit(I.deleteInstance(inventory,id,equipment,catalog)),
  canEquip:(id,slot)=>equipmentCheck(()=>E.canEquip(inventory,equipment,id,slot,catalog,requirements)),
  equip(id,slot){const result=equipmentCheck(()=>E.equip(inventory,equipment,id,slot,catalog,requirements));return result.ok?commit(result,result.equipment):result},
  unequip(slot){const result=E.unequip(inventory,equipment,slot,catalog);return result.ok?commit(result,result.equipment):result},
  acquireEquipment(id,slot,{reuse=false}={}){
   let item=reuse?Object.values(inventory.instances).find(i=>i.definitionId===id&&!Object.values(equipment).includes(i.instanceId)):null;
   if(!item){const capacity=preflight({itemRewards:[{itemId:id,quantity:1}]});if(!capacity.ok)return capacity}
   const created=item?{ok:true,instance:item,inventory}:I.createInstance(inventory,id,{},catalog);if(!created.ok)return created;
   const checked=equipmentCheck(()=>E.equip(created.inventory,equipment,created.instance.instanceId,slot,catalog,requirements));return checked.ok?commit(created,checked.equipment):checked;
  },
  reward(stacks){let next=inventory;for(const [id,count] of Object.entries(stacks)){const r=I.addStack(next,id,count,catalog);if(!r.ok)return r;next=r.inventory}return commit({ok:true,inventory:next})},
  craft(recipeId){
   const recipe=D.recipes.find(r=>r.id===recipeId);if(!recipe)return I.fail('UNKNOWN_RECIPE');let next=inventory;
   const capacity=preflight({stackDebits:Object.entries(recipe.inputs).map(([itemId,quantity])=>({itemId,quantity})),itemRewards:[{itemId:recipe.output,quantity:1}]});if(!capacity.ok)return capacity;
   for(const [id,count] of Object.entries(recipe.inputs)){const r=I.removeStack(next,id,count,catalog);if(!r.ok)return r;next=r.inventory}
   const d=catalog.getDefinition(recipe.output),r=d?.stackable?I.addStack(next,recipe.output,1,catalog):I.createInstance(next,recipe.output,{craftedRecipe:recipe.id},catalog);return commit(r);
  },
  buy(id,count=1){return trade(id,count,'buy')},sell(id,count=1){return trade(id,count,'sell')}
 };
 function trade(id,count,mode){
  const price=Object.hasOwn(D.merchant,id)?D.merchant[id][mode]:undefined;
  if(!Number.isSafeInteger(count)||count<=0||!Number.isSafeInteger(price))return I.fail('INVALID_TRADE');
  const total=price*count,gold=raw.gold;if(!Number.isSafeInteger(total)||!Number.isFinite(gold)||gold<0)return I.fail('INVALID_CURRENCY');
  if(mode==='buy'&&gold<total)return I.fail('INSUFFICIENT_GOLD');const nextGold=mode==='buy'?gold-total:gold+total;
  if(!Number.isFinite(nextGold)||nextGold>Number.MAX_SAFE_INTEGER)return I.fail('CURRENCY_OVERFLOW');
  const r=mode==='buy'?I.addStack(inventory,id,count,catalog):I.removeStack(inventory,id,count,catalog);if(!r.ok)return r;
  const result=commit(r);if(result.ok)raw.gold=nextGold;return result.ok?freeze({...result,gold:nextGold}):result;
 }
 // Counter views are read-only. The bounded historical name setter routes into
 // the same ownership/equipment state for old callers; production uses IDs.
 const gearView={};for(const key of Object.keys(history.equipment||{}))if(!E.slots.includes(key))gearView[key]=history.equipment[key];
 for(const slot of E.legacySlots)Object.defineProperty(gearView,slot,{enumerable:true,get:()=>legacyEquipment(inventory,equipment,history,catalog)[slot],set:name=>{
  const id=Object.hasOwn(D.legacyNames,name)?D.legacyNames[name]:null;
  if(id&&inventory.instances[equipment[slot]]?.definitionId===id)return;
  if(id){const result=api.acquireEquipment(id,slot,{reuse:true});if(!result.ok)throw Error(result.code)}
  else{const result=api.unequip(slot);if(!result.ok)throw Error(result.code);history=freeze({...history,equipment:{...history.equipment,[slot]:name}})}
 }});Object.freeze(gearView);
 for(const [key,get] of Object.entries({itemInventory:()=>inventory,equippedItems:()=>equipment,itemHistory:()=>history,inventory:()=>legacyInventory(inventory,history,catalog),equipment:()=>gearView}))Object.defineProperty(raw,key,{enumerable:true,get});
 return freeze(api);
}
window.AstraeonItemState=freeze({migrate,installMirrors,legacyInventory,legacyEquipment,create,MigrationError});
})();
