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
  inventory=I.normalize(raw.itemInventory||{},catalog);equipment=E.normalize(inventory,raw.equippedItems,catalog);
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
  equipment={weapon:null,armor:null,relic:null};
  for(const slot of E.slots){
   const name=raw.equipment?.[slot],id=Object.hasOwn(D.legacyNames,name)?D.legacyNames[name]:null,d=catalog.getDefinition(id);
   if(!d||!d.equipmentSlots.includes(slot))continue;
   let owned=Object.values(inventory.instances).find(item=>item.definitionId===id&&!Object.values(equipment).includes(item.instanceId));
   if(!owned){const result=I.createInstance(inventory,id,{legacyEquippedOnly:true},catalog);if(!result.ok)throw new MigrationError();inventory=result.inventory;owned=result.instance}
   equipment[slot]=owned.instanceId;
  }
  equipment=E.normalize(inventory,equipment,catalog);
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
 for(const slot of E.slots){const d=catalog.getDefinition(inventory.instances[equipment[slot]]?.definitionId),old=history.equipment?.[slot];result[slot]=d?.name||(typeof old==='string'&&old!=='None'&&!Object.hasOwn(D.legacyNames,old)?old:'None')}
 return freeze(result);
}
function installMirrors(state,normalized,catalog=D){Object.assign(state,normalized);state.inventory=legacyInventory(state.itemInventory,state.itemHistory,catalog);state.equipment=legacyEquipment(state.itemInventory,state.equippedItems,state.itemHistory,catalog);return state}
function create(raw,{catalog=D,onChange=()=>{},requirements=()=>true}={}){
 const initial=migrate(raw,catalog);let inventory=initial.itemInventory,equipment=initial.equippedItems,history=initial.itemHistory;
 function commit(result,nextEquipment=equipment){
  if(!result.ok)return result;const nextInventory=result.inventory||inventory;
  try{onChange(nextInventory,nextEquipment)}catch{return I.fail('INVALID_EQUIPMENT_MODIFIERS')}
  inventory=nextInventory;equipment=nextEquipment;return freeze({...result,inventory,equipment});
 }
 const api={getInventory:()=>inventory,getEquipment:()=>equipment,getHistory:()=>history,
  getQuantity:id=>I.getQuantity(inventory,id),getInstance:id=>Object.hasOwn(inventory.instances,id)?inventory.instances[id]:null,
  getEquipped:slot=>E.slots.includes(slot)?equipment[slot]:null,
  getEquipmentModifiers:()=>E.modifiers(inventory,equipment,catalog),getCarriedWeight:()=>I.carriedWeight(inventory,catalog),
  getEquipmentEffects:()=>E.effects(inventory,equipment,catalog),
  canAddStack:(id,count)=>I.canAddStack(inventory,id,count,catalog),canRemoveStack:(id,count)=>I.canRemoveStack(inventory,id,count,catalog),
  addStack:(id,count)=>commit(I.addStack(inventory,id,count,catalog)),removeStack:(id,count)=>commit(I.removeStack(inventory,id,count,catalog)),consumeStack:(id,count=1)=>commit(I.consumeStack(inventory,id,count,catalog)),
  createItemInstance:(id,metadata={})=>commit(I.createInstance(inventory,id,metadata,catalog)),
  deleteItemInstance:id=>commit(I.deleteInstance(inventory,id,equipment,catalog)),
  canEquip:(id,slot)=>E.canEquip(inventory,equipment,id,slot,catalog,requirements),
  equip(id,slot){const result=E.equip(inventory,equipment,id,slot,catalog,requirements);return result.ok?commit(result,result.equipment):result},
  unequip(slot){const result=E.unequip(inventory,equipment,slot,catalog);return result.ok?commit(result,result.equipment):result},
  acquireEquipment(id,slot,{reuse=false}={}){
   let item=reuse?Object.values(inventory.instances).find(i=>i.definitionId===id&&!Object.values(equipment).includes(i.instanceId)):null;
   const created=item?{ok:true,instance:item,inventory}:I.createInstance(inventory,id,{},catalog);if(!created.ok)return created;
   const checked=E.equip(created.inventory,equipment,created.instance.instanceId,slot,catalog,requirements);return checked.ok?commit(created,checked.equipment):checked;
  },
  reward(stacks){let next=inventory;for(const [id,count] of Object.entries(stacks)){const r=I.addStack(next,id,count,catalog);if(!r.ok)return r;next=r.inventory}return commit({ok:true,inventory:next})},
  craft(recipeId){
   const recipe=D.recipes.find(r=>r.id===recipeId);if(!recipe)return I.fail('UNKNOWN_RECIPE');let next=inventory;
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
 for(const slot of E.slots)Object.defineProperty(gearView,slot,{enumerable:true,get:()=>legacyEquipment(inventory,equipment,history,catalog)[slot],set:name=>{
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
