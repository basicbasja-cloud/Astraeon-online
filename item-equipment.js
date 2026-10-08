/* Pure owned references and slot transitions. Stats owns modifier calculations. */
(() => {
'use strict';
const defaults=window.AstraeonItemDefinitions,freeze=defaults.freeze,I=window.AstraeonItemInventory,R=window.AstraeonEquipmentSlots,slots=R.ids,legacySlots=Object.keys(R.legacy);
const plain=v=>!!v&&typeof v==='object'&&!Array.isArray(v)&&(Object.getPrototypeOf(v)===Object.prototype||Object.getPrototypeOf(v)===null);
function json(v,seen=new Set(),depth=0){if(depth>64)return false;if(v===null||['string','boolean'].includes(typeof v))return true;if(typeof v==='number')return Number.isFinite(v);if((!Array.isArray(v)&&!plain(v))||seen.has(v))return false;seen.add(v);try{return Object.values(v).every(x=>json(x,seen,depth+1))}catch{return false}finally{seen.delete(v)}}
function validateDefinition(d){
 try{
  if(!plain(d)||d.kind!=='equipment'||d.stackable!==false)return I.fail('NOT_EQUIPMENT');
  if(typeof d.id!=='string'||!d.id||d.maxStack!==1||!Array.isArray(d.equipmentSlots)||!d.equipmentSlots.length)return I.fail('INVALID_EQUIPMENT_DEFINITION');
  const allowed=d.equipmentSlots.map(R.canonical);if(allowed.some(s=>!s)||new Set(allowed).size!==allowed.length||!plain(d.requirements)||!json(d))return I.fail('INVALID_EQUIPMENT_DEFINITION');
  if(!Array.isArray(d.modifiers)||d.modifiers.some(m=>!plain(m)||['primary','add','multiply'].some(k=>Object.hasOwn(m,k)&&(!plain(m[k])||Object.values(m[k]).some(v=>typeof v!=='number'||!Number.isFinite(v))))))return I.fail('INVALID_EQUIPMENT_MODIFIERS');
  // Existing Stats validates its own grammar and finite arithmetic.
  try{window.AstraeonStats.calculate({equipmentModifiers:d.modifiers})}catch{return I.fail('INVALID_EQUIPMENT_MODIFIERS')}
  return freeze({ok:true,allowedSlots:allowed});
 }catch{return I.fail('INVALID_EQUIPMENT_DEFINITION')}
}
function normalizeDetailed(inventory,raw={},catalog=defaults){
 const equipment=Object.fromEntries(slots.map(s=>[s,null])),issues=[],seen=new Set();
 if(!plain(raw))return freeze({equipment,issues:[{code:'INVALID_EQUIPMENT'}]});
 // Stored IDs take precedence, including explicit null. Conflicts preserve ownership.
 for(const slot of slots){
  const alias=R.getDefinition(slot).semanticId,key=Object.hasOwn(raw,slot)?slot:alias,id=raw[key];
  const item=typeof id==='string'&&Object.hasOwn(inventory.instances,id)?inventory.instances[id]:null,d=catalog.getDefinition(item?.definitionId),checked=validateDefinition(d);
  if(item&&checked.ok&&checked.allowedSlots.includes(slot)&&!seen.has(id)){equipment[slot]=id;seen.add(id)}
  else if(id!==null&&id!==undefined)issues.push({slot,key,instanceId:typeof id==='string'?id:null,code:seen.has(id)?'ALREADY_EQUIPPED':checked.ok?'WRONG_EQUIPMENT_SLOT':'INVALID_EQUIPPED_REFERENCE'});
  if(alias!==slot&&Object.hasOwn(raw,slot)&&Object.hasOwn(raw,alias)&&raw[alias]!==raw[slot]&&raw[alias]!=null)issues.push({slot,key:alias,instanceId:typeof raw[alias]==='string'?raw[alias]:null,code:'SLOT_ALIAS_CONFLICT'});
 }
 for(const key of Object.keys(raw))if(!R.canonical(key))issues.push({key,instanceId:typeof raw[key]==='string'?raw[key]:null,code:'UNKNOWN_EQUIPMENT_SLOT'});
 return freeze({equipment,issues});
}
const normalizeSlots=(inventory,raw,catalog=defaults)=>normalizeDetailed(inventory,raw,catalog).equipment;
const legacyView=equipment=>freeze(Object.fromEntries(legacySlots.map(slot=>[slot,equipment[slot]??null])));
// Historical pure API keeps its three-key projection; live ownership uses normalizeSlots.
function normalize(inventory,raw={},catalog=defaults){const result=normalizeSlots(inventory,raw,catalog);return plain(raw)&&Object.keys(raw).every(k=>legacySlots.includes(k))?legacyView(result):result}
function valid(inventory,equipment,catalog=defaults){try{return I.valid(inventory,catalog)&&plain(equipment)&&JSON.stringify(normalize(inventory,equipment,catalog))===JSON.stringify(equipment)}catch{return false}}
function canEquip(inventory,equipment,id,requestedSlot,catalog=defaults,requirements=()=>true){
 const slot=R.canonical(requestedSlot);if(!slot)return I.fail('INVALID_EQUIPMENT_SLOT');if(!valid(inventory,equipment,catalog))return I.fail('INVALID_EQUIPMENT');
 const item=Object.hasOwn(inventory.instances,id)?inventory.instances[id]:null;if(!item)return I.fail('UNKNOWN_INSTANCE');const d=catalog.getDefinition(item.definitionId),checked=validateDefinition(d);if(!checked.ok)return checked;if(!checked.allowedSlots.includes(slot))return I.fail('WRONG_EQUIPMENT_SLOT');
 if(Object.entries(equipment).some(([s,value])=>s!==slot&&value===id))return I.fail('ALREADY_EQUIPPED');
 try{if(requirements(d.requirements,item,slot)!==true)return I.fail('EQUIPMENT_REQUIREMENTS')}catch{return I.fail('EQUIPMENT_REQUIREMENTS')}
 return freeze({ok:true,slot,semanticSlot:R.getDefinition(slot).semanticId,instanceId:id});
}
function equip(inventory,equipment,id,slot,catalog=defaults,requirements){const result=canEquip(inventory,equipment,id,slot,catalog,requirements);return result.ok?freeze({...result,equippedInstanceId:id,previousInstanceId:equipment[result.slot]??null,changed:equipment[result.slot]!==id,equipment:{...normalizeSlots(inventory,equipment,catalog),[result.slot]:id}}):result}
function unequip(inventory,equipment,requestedSlot,catalog=defaults){const slot=R.canonical(requestedSlot);if(!slot)return I.fail('INVALID_EQUIPMENT_SLOT');if(!valid(inventory,equipment,catalog))return I.fail('INVALID_EQUIPMENT');return freeze({ok:true,slot,equippedInstanceId:null,previousInstanceId:equipment[slot]??null,changed:equipment[slot]!=null,equipment:{...normalizeSlots(inventory,equipment,catalog),[slot]:null}})}
function modifiers(inventory,equipment,catalog=defaults){if(!valid(inventory,equipment,catalog))return freeze([]);return freeze(slots.flatMap(slot=>{const item=inventory.instances[equipment[slot]],d=catalog.getDefinition(item?.definitionId);return d?structuredClone(d.modifiers):[]}))}
function effects(inventory,equipment,catalog=defaults){if(!valid(inventory,equipment,catalog))return freeze({});const result={};for(const id of Object.values(equipment)){const d=catalog.getDefinition(inventory.instances[id]?.definitionId);for(const [key,value] of Object.entries(d?.effects||{}))if(Number.isFinite(value)&&value>=0)result[key]=(result[key]||0)+value}return freeze(result)}
window.AstraeonItemEquipment=freeze({slots,legacySlots,legacyView,validateDefinition,normalize,normalizeSlots,normalizeDetailed,valid,canEquip,equip,unequip,modifiers,effects});
})();
