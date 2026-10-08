/* Presentation only. Shared canonical APIs own all validation and transactions. */
(() => {
'use strict';
const key='astraeon-inventory-dev-v1',$=id=>document.getElementById(id),D=window.AstraeonItemDefinitions;let state,player,testTime=0,ticket;
const show=(id,value)=>$(id).textContent=JSON.stringify(value,null,2);
function render(){
 const selected=$('instance').value,items=Object.values(player.getInventory().instances);
 $('instance').replaceChildren(...items.map(item=>{const option=document.createElement('option');option.value=item.instanceId;option.textContent=item.instanceId+' · '+item.definitionId;return option}));
 if(items.some(item=>item.instanceId===selected))$('instance').value=selected;
 show('definitions',D.definitions);show('inventory',player.getInventory());show('equipment',{slots:player.getEquipment(),activeSlots:player.getEquipmentSlots(),registry:player.getEquipmentSlotRegistry(),legacyMapping:window.AstraeonEquipmentSlots.legacy,capacity:player.getInventoryCapacityState(),eligibility:player.canEquip($('instance').value,$('slot').value),modifiers:player.getEquipmentModifiers(),effects:player.getEquipmentEffects(),carriedWeight:player.getCarriedWeight()});show('derived',player.getDerivedStats());show('persistent',window.AstraeonSave.snapshot(state));
 show('action-item-state',{now:testTime,authoredEffects:D.getDefinition($('action-item').value).effects,state:player.getActionItemState($('action-item').value,{now:testTime,intent:'inventory'}),runtime:player.getActionItemRuntime()});$('item-time').value=testTime;
}
function load(){const stored=localStorage.getItem(key);state=window.AstraeonSave.normalize(stored?JSON.parse(stored):{name:'Inventory sandbox',saveVersion:5});testTime=0;ticket=null;player=window.AstraeonPlayer.attach(state,{getItemContext:()=>({now:testTime,intent:'inventory'})});return {ok:true}}
function run(fn){try{const result=fn();render();$('status').textContent=JSON.stringify(result??{ok:true});show('equipment-result',result??{ok:true})}catch(error){$('status').textContent=error.message}}
for(const d of Object.values(D.definitions)){const option=document.createElement('option');option.value=d.id;option.textContent=d.id+' · '+d.name;$('definition').append(option)}
const actions={
 'add-stack':()=>player.addStack($('definition').value,Number($('amount').value)),
 'remove-stack':()=>player.removeStack($('definition').value,Number($('amount').value)),
 'create-instance':()=>player.createItemInstance($('definition').value),
 'delete-instance':()=>player.deleteItemInstance($('instance').value),
 equip:()=>player.equip($('instance').value,$('slot').value),unequip:()=>player.unequip($('slot').value),
 save:()=>localStorage.setItem(key,JSON.stringify(window.AstraeonSave.snapshot(state))),reload:load,
 'give-consumable':()=>player.addStack($('action-item').value,1),
 'use-consumable':()=>itemResult(player.useConsumable($('action-item').value)),
 'prepare-consumable':()=>itemResult(ticket=player.prepareActionItem($('action-item').value,{now:testTime,intent:'inventory'})),
 'commit-consumable':()=>itemResult(player.commitActionItem(ticket,{now:testTime,intent:'inventory'})),
 'set-item-resources':()=>{player.setCurrentHP(Number($('item-hp').value));player.setCurrentSP(Number($('item-sp').value));return {ok:true}},
 'full-item-resources':()=>{const s=player.snapshot();player.setCurrentHP(s.maxHP);player.setCurrentSP(s.maxSP);return {ok:true}},
 'set-item-time':()=>setTime(Number($('item-time').value)),
 'advance-item-time':()=>setTime(testTime+Number($('item-time-step').value)),
 'reset-item-cooldowns':()=>player.resetActionItemCooldowns(),
 'inspect-migration':()=>{show('migration-result',window.AstraeonSave.normalize(JSON.parse($('migration-input').value)));return {ok:true}}
};for(const [id,fn] of Object.entries(actions))$(id).onclick=()=>run(fn);
function itemResult(result){show('action-item-result',result);return result}
function setTime(value){if(!Number.isFinite(value)||value<testTime)throw Error('Test time must advance monotonically');testTime=value;return {ok:true}}
$('action-item').onchange=()=>run(()=>({ok:true}));
window.AstraeonInventoryHarness=Object.freeze({snapshot:()=>window.AstraeonSave.snapshot(state),inspect:()=>({registry:player.getEquipmentSlotRegistry(),equipment:player.getEquipmentSlots(),inventory:player.getInventory(),stats:player.getDerivedStats(),capacity:player.getInventoryCapacityState()}),give:id=>player.createItemInstance(id),equip:(id,slot)=>player.equip(id,slot),unequip:slot=>player.unequip(slot),normalize:raw=>window.AstraeonSave.normalize(raw)});run(load);
})();
