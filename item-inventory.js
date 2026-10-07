/* Pure inventory transitions. Identity is persisted; no RNG, clock or storage. */
(() => {
'use strict';
const defaults=window.AstraeonItemDefinitions,freeze=defaults.freeze;
const fail=code=>freeze({ok:false,code});
const amount=value=>Number.isSafeInteger(value)&&value>0;
const plain=value=>!!value&&typeof value==='object'&&!Array.isArray(value)&&(Object.getPrototypeOf(value)===Object.prototype||Object.getPrototypeOf(value)===null);
function data(value,ancestors=new Set()){
 if(value===null||['string','boolean'].includes(typeof value))return true;
 if(typeof value==='number')return Number.isFinite(value);
 if(!Array.isArray(value)&&!plain(value)||ancestors.has(value))return false;
 ancestors.add(value);const accepted=Object.values(value).every(child=>data(child,ancestors));ancestors.delete(value);return accepted;
}
const serial=id=>{const match=typeof id==='string'?/^item-([1-9][0-9]*)$/.exec(id):null;return match&&Number.isSafeInteger(Number(match[1]))?Number(match[1]):0};
function normalize(raw={},catalog=defaults){
 raw=plain(raw)?raw:{};
 const stacks={},instances={},history=plain(raw.history)&&data(raw.history)?structuredClone(raw.history):{};
 for(const [id,value] of Object.entries(plain(raw.stacks)?raw.stacks:{})){const d=catalog.getDefinition(id);if(d?.stackable&&Number.isSafeInteger(value)&&value>=0&&value<=d.maxStack){if(value)stacks[id]=value}else history.stacks={...history.stacks,[id]:data(value)?structuredClone(value):null}}
 let highest=0;
 for(const [id,value] of Object.entries(plain(raw.instances)?raw.instances:{})){
  highest=Math.max(highest,serial(id));const d=catalog.getDefinition(value?.definitionId);
  if(serial(id)&&plain(value)&&value.instanceId===id&&d&&!d.stackable&&(value.metadata===undefined||plain(value.metadata)&&data(value.metadata)))instances[id]={instanceId:id,definitionId:d.id,metadata:structuredClone(value.metadata||{})};
  else history.instances={...history.instances,[id]:data(value)?structuredClone(value):null};
 }
 // A discarded malformed ID still consumes its serial; exhaustion never wraps.
 const nextItemSerial=Math.max(amount(raw.nextItemSerial)?raw.nextItemSerial:1,highest===Number.MAX_SAFE_INTEGER?highest:highest+1);
 return freeze({stacks,instances,nextItemSerial,history});
}
function valid(state,catalog=defaults){try{return plain(state)&&JSON.stringify(normalize(state,catalog))===JSON.stringify(state)}catch{return false}}
const getQuantity=(state,id)=>Object.hasOwn(state.stacks,id)?state.stacks[id]:0;
function canAddStack(state,id,count,catalog=defaults){if(!valid(state,catalog))return fail('INVALID_INVENTORY');const d=catalog.getDefinition(id);if(!d)return fail('UNKNOWN_ITEM');if(!d.stackable)return fail('NOT_STACKABLE');if(!amount(count))return fail('INVALID_AMOUNT');const quantity=getQuantity(state,id)+count;if(!Number.isSafeInteger(quantity)||quantity>d.maxStack)return fail('STACK_OVERFLOW');return freeze({ok:true,quantity})}
function addStack(state,id,count,catalog=defaults){const result=canAddStack(state,id,count,catalog);return result.ok?freeze({...result,inventory:{...state,stacks:{...state.stacks,[id]:result.quantity}}}):result}
function canRemoveStack(state,id,count,catalog=defaults){const d=catalog.getDefinition(id);if(!valid(state,catalog))return fail('INVALID_INVENTORY');if(!d)return fail('UNKNOWN_ITEM');if(!d.stackable)return fail('NOT_STACKABLE');if(!amount(count))return fail('INVALID_AMOUNT');return getQuantity(state,id)<count?fail('INSUFFICIENT_ITEMS'):freeze({ok:true,quantity:getQuantity(state,id)-count})}
function removeStack(state,id,count,catalog=defaults){const result=canRemoveStack(state,id,count,catalog);if(!result.ok)return result;const stacks={...state.stacks};if(result.quantity)stacks[id]=result.quantity;else delete stacks[id];return freeze({...result,inventory:{...state,stacks}})}
function createInstance(state,id,metadata={},catalog=defaults){
 if(!valid(state,catalog))return fail('INVALID_INVENTORY');const d=catalog.getDefinition(id);if(!d)return fail('UNKNOWN_ITEM');if(d.stackable)return fail('NOT_INSTANCE_ITEM');if(!plain(metadata)||!data(metadata))return fail('INVALID_METADATA');
 const n=state.nextItemSerial,instanceId=`item-${n}`;if(n>=Number.MAX_SAFE_INTEGER||Object.hasOwn(state.instances,instanceId))return fail('SERIAL_EXHAUSTED');
 const instance={instanceId,definitionId:id,metadata:structuredClone(metadata)};return freeze({ok:true,instance,inventory:{...state,instances:{...state.instances,[instanceId]:instance},nextItemSerial:n+1}});
}
function deleteInstance(state,id,equipment={},catalog=defaults){if(!valid(state,catalog))return fail('INVALID_INVENTORY');if(!Object.hasOwn(state.instances,id))return fail('UNKNOWN_INSTANCE');if(Object.values(equipment).includes(id))return fail('ITEM_EQUIPPED');const instances={...state.instances};delete instances[id];return freeze({ok:true,inventory:{...state,instances}})}
function carriedWeight(state,catalog=defaults){if(!valid(state,catalog))return fail('INVALID_INVENTORY');let weight=0;for(const [id,count] of Object.entries(state.stacks))weight+=catalog.getDefinition(id).weight*count;for(const item of Object.values(state.instances))weight+=catalog.getDefinition(item.definitionId).weight;return Number.isFinite(weight)?freeze({ok:true,weight}):fail('WEIGHT_OVERFLOW')}
window.AstraeonItemInventory=freeze({normalize,valid,getQuantity,canAddStack,addStack,canRemoveStack,removeStack,consumeStack:removeStack,createInstance,deleteInstance,carriedWeight,fail});
})();
