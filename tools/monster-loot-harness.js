/* Isolated developer authority. No localStorage or production save access. */
(() => {
'use strict';
const $=id=>document.getElementById(id),show=(id,value)=>$(id).textContent=JSON.stringify(value,null,2);
const state=window.AstraeonSave.normalize({name:'Loot disposable sandbox',cls:0}),player=window.AstraeonPlayer.attach(state);
const runtime=window.AstraeonMonsterLootRuntime.create({commit:(r,id)=>player.commitMonsterRewards(r,id)});
let actor=null,claim=null;
for(const d of Object.values(window.AstraeonMonsterDefinitions.definitions).filter(d=>d.metadata?.fixture))$('fixture').add(new Option(d.id,d.id));
$('fixture').value='proof-multi';
const snapshot=()=>({save:window.AstraeonSave.snapshot(state),inventory:player.getInventory(),gold:state.gold,identity:actor?runtime.inspect(actor):null,runtime:runtime.snapshot()});
function render(){const d=window.AstraeonMonsterDefinitions.getDefinition($('fixture').value);show('definition',{monster:d,table:window.AstraeonDropTables.getDefinition(d.dropTableId),validation:window.AstraeonLootResolution.validateReference(d.dropTableId)});show('state',snapshot())}
function resolve(newLife=false){
 const values=$('rolls').value.split(',').filter(v=>v.trim()).map(Number);
 if(newLife&&actor){actor.hp=1;const r=runtime.newLife(actor);if(!r.ok){show('result',r);return}}
 else{actor={hp:1};const r=runtime.register(actor,$('fixture').value);if(!r.ok){show('result',r);return}}
 actor.hp=0;claim=runtime.prepareDeath(actor,{zone:2,quest:null},window.AstraeonCombatRuntime.sequenceRng(values));show('claim',claim);render();
}
$('validate').onclick=render;$('fixture').onchange=render;$('resolve').onclick=()=>resolve();$('new-life').onclick=()=>resolve(true);
for(const id of ['commit','duplicate'])$(id).onclick=()=>{show('result',runtime.commit(claim));render()};
window.AstraeonMonsterLootHarness=Object.freeze({snapshot});render();
})();
