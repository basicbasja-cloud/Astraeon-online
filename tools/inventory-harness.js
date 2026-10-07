/* Presentation only. Shared canonical APIs own all validation and transactions. */
(() => {
'use strict';
const key='astraeon-inventory-dev-v1',$=id=>document.getElementById(id),D=window.AstraeonItemDefinitions;let state,player;
const show=(id,value)=>$(id).textContent=JSON.stringify(value,null,2);
function render(){
 const selected=$('instance').value,items=Object.values(player.getInventory().instances);
 $('instance').replaceChildren(...items.map(item=>{const option=document.createElement('option');option.value=item.instanceId;option.textContent=item.instanceId+' · '+item.definitionId;return option}));
 if(items.some(item=>item.instanceId===selected))$('instance').value=selected;
 show('definitions',D.definitions);show('inventory',player.getInventory());show('equipment',{slots:player.getEquipment(),modifiers:player.getEquipmentModifiers(),effects:player.getEquipmentEffects(),carriedWeight:player.getCarriedWeight()});show('derived',player.getDerivedStats());show('persistent',window.AstraeonSave.snapshot(state));
}
function load(){const stored=localStorage.getItem(key);state=window.AstraeonSave.normalize(stored?JSON.parse(stored):{name:'Inventory sandbox',saveVersion:5});player=window.AstraeonPlayer.attach(state);return {ok:true}}
function run(fn){try{const result=fn();render();$('status').textContent=JSON.stringify(result?.ok===false?result:{ok:true})}catch(error){$('status').textContent=error.message}}
for(const d of Object.values(D.definitions)){const option=document.createElement('option');option.value=d.id;option.textContent=d.id+' · '+d.name;$('definition').append(option)}
const actions={
 'add-stack':()=>player.addStack($('definition').value,Number($('amount').value)),
 'remove-stack':()=>player.removeStack($('definition').value,Number($('amount').value)),
 'create-instance':()=>player.createItemInstance($('definition').value),
 'delete-instance':()=>player.deleteItemInstance($('instance').value),
 equip:()=>player.equip($('instance').value,$('slot').value),unequip:()=>player.unequip($('slot').value),
 save:()=>localStorage.setItem(key,JSON.stringify(window.AstraeonSave.snapshot(state))),reload:load,
 'inspect-migration':()=>{show('migration-result',window.AstraeonSave.normalize(JSON.parse($('migration-input').value)));return {ok:true}}
};for(const [id,fn] of Object.entries(actions))$(id).onclick=()=>run(fn);
window.AstraeonInventoryHarness=Object.freeze({snapshot:()=>window.AstraeonSave.snapshot(state)});run(load);
})();
