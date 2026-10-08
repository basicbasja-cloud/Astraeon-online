/* Authored gameplay slots. Existing v5 storage IDs retain their inspected meaning. */
(() => {
'use strict';
const freeze=window.AstraeonItemDefinitions.freeze;
const definitions=freeze([
 {id:'weapon',semanticId:'mainHand',name:'Main Hand',role:'offense'},
 {id:'offHand',semanticId:'offHand',name:'Off Hand',role:'equipment'},
 {id:'armor',semanticId:'body',name:'Body',role:'defense'},
 {id:'shoes',semanticId:'shoes',name:'Shoes',role:'equipment'},
 {id:'relic',semanticId:'accessory',name:'Accessory',role:'equipment'}
]);
const ids=freeze(definitions.map(d=>d.id)),legacy=freeze({weapon:'weapon',armor:'armor',relic:'relic'});
const aliases=freeze(Object.fromEntries(definitions.map(d=>[d.semanticId,d.id])));
const canonical=id=>typeof id==='string'?(ids.includes(id)?id:Object.hasOwn(aliases,id)?aliases[id]:null):null;
const getDefinition=id=>definitions.find(d=>d.id===canonical(id))||null;
function validate(registry){
 if(!Array.isArray(registry)||!registry.length)return freeze({ok:false,code:'INVALID_SLOT_REGISTRY'});
 const seen=new Set();for(const d of registry){if(!d||!ids.includes(d.id)||seen.has(d.id)||getDefinition(d.id).semanticId!==d.semanticId||typeof d.name!=='string'||!d.name)return freeze({ok:false,code:'INVALID_SLOT_REGISTRY'});seen.add(d.id)}
 return freeze({ok:true});
}
// New active IDs require an authored registry extension; unknown future IDs reject.
window.AstraeonEquipmentSlots=freeze({definitions,ids,legacy,aliases,canonical,getDefinition,validate});
})();
