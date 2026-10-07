/* Pure equipment identity/slot validation. Stats owns all modifier calculations. */
(() => {
'use strict';
const defaults=window.AstraeonItemDefinitions,freeze=defaults.freeze,I=window.AstraeonItemInventory;
const slots=freeze(['weapon','armor','relic']);
function normalize(inventory,raw={},catalog=defaults){const seen=new Set();return freeze(Object.fromEntries(slots.map(slot=>{const id=raw?.[slot],item=inventory.instances[id],d=catalog.getDefinition(item?.definitionId),accepted=typeof id==='string'&&item&&d?.kind==='equipment'&&d.equipmentSlots.includes(slot)&&!seen.has(id);if(accepted)seen.add(id);return [slot,accepted?id:null]})))}
const valid=(inventory,equipment,catalog=defaults)=>I.valid(inventory,catalog)&&JSON.stringify(normalize(inventory,equipment,catalog))===JSON.stringify(equipment);
function canEquip(inventory,equipment,id,slot,catalog=defaults,requirements=()=>true){
 if(!slots.includes(slot))return I.fail('INVALID_EQUIPMENT_SLOT');if(!valid(inventory,equipment,catalog))return I.fail('INVALID_EQUIPMENT');
 const item=Object.hasOwn(inventory.instances,id)?inventory.instances[id]:null;if(!item)return I.fail('UNKNOWN_INSTANCE');const d=catalog.getDefinition(item.definitionId);if(d?.kind!=='equipment')return I.fail('NOT_EQUIPMENT');if(!d.equipmentSlots.includes(slot))return I.fail('WRONG_EQUIPMENT_SLOT');
 if(Object.entries(equipment).some(([s,value])=>s!==slot&&value===id))return I.fail('ALREADY_EQUIPPED');
 try{if(requirements(d.requirements,item,slot)!==true)return I.fail('EQUIPMENT_REQUIREMENTS')}catch{return I.fail('EQUIPMENT_REQUIREMENTS')}
 return freeze({ok:true,slot,instanceId:id});
}
function equip(inventory,equipment,id,slot,catalog=defaults,requirements){const result=canEquip(inventory,equipment,id,slot,catalog,requirements);return result.ok?freeze({...result,equipment:{...equipment,[slot]:id}}):result}
function unequip(inventory,equipment,slot,catalog=defaults){if(!slots.includes(slot))return I.fail('INVALID_EQUIPMENT_SLOT');if(!valid(inventory,equipment,catalog))return I.fail('INVALID_EQUIPMENT');return freeze({ok:true,equipment:{...equipment,[slot]:null}})}
function modifiers(inventory,equipment,catalog=defaults){if(!valid(inventory,equipment,catalog))return freeze([]);return freeze(slots.flatMap(slot=>{const item=inventory.instances[equipment[slot]],d=catalog.getDefinition(item?.definitionId);return d?structuredClone(d.modifiers):[]}))}
function effects(inventory,equipment,catalog=defaults){if(!valid(inventory,equipment,catalog))return freeze({});const result={};for(const id of Object.values(equipment)){const d=catalog.getDefinition(inventory.instances[id]?.definitionId);for(const [key,value] of Object.entries(d?.effects||{}))if(Number.isFinite(value)&&value>=0)result[key]=(result[key]||0)+value}return freeze(result)}
window.AstraeonItemEquipment=freeze({slots,normalize,valid,canEquip,equip,unequip,modifiers,effects});
})();
