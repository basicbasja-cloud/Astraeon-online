/* Disposable developer presentation. Opening authority remains the shared runtime. */
(() => {
'use strict';
const $=id=>document.getElementById(id),show=(id,value)=>$(id).textContent=JSON.stringify(value,null,2),BOX='monster-box-proof',key='astraeon-monster-box-dev-v1';
let state,player,ticket=null,lastResult=null;
const rng=()=>window.AstraeonCombatRuntime.sequenceRng($('rolls').value.split(',').filter(x=>x.trim()).map(Number));
function attach(raw={name:'Box disposable sandbox',cls:0}){state=window.AstraeonSave.normalize(raw);player=window.AstraeonPlayer.attach(state,{getBoxRng:rng})}
const snapshot=()=>({save:window.AstraeonSave.snapshot(state),inventory:player.getInventory(),revision:player.getInventoryRevision(),boxQuantity:player.getQuantity(BOX),runtime:player.getMonsterBoxRuntime(),ticket,lastResult});
function render(){show('definition',window.AstraeonMonsterBox.compile(BOX));show('ticket',ticket);show('result',lastResult);show('inspection',snapshot())}
function action(fn){try{lastResult=fn()}catch(error){lastResult={ok:false,code:'HARNESS_ERROR',message:error.message}}render()}
const count=()=>Number($('count').value);
$('add-one').onclick=()=>action(()=>player.addStack(BOX,1));$('add-many').onclick=()=>action(()=>player.addStack(BOX,5));
$('prepare').onclick=()=>action(()=>ticket=player.prepareMonsterBoxOpen(BOX,count()));
for(const id of ['commit','duplicate'])$(id).onclick=()=>action(()=>player.commitMonsterBoxOpen(ticket));
$('single').onclick=()=>action(()=>player.openMonsterBoxes(BOX,1));$('bulk').onclick=()=>action(()=>player.openMonsterBoxes(BOX,count()));
$('mutate').onclick=()=>action(()=>player.addStack('ore',1));
$('save').onclick=()=>action(()=>{localStorage.setItem(key,JSON.stringify(window.AstraeonSave.snapshot(state)));return {ok:true,key}});
$('reload').onclick=()=>action(()=>{const raw=localStorage.getItem(key);if(!raw)return {ok:false,code:'NO_SANDBOX_SAVE'};attach(JSON.parse(raw));return {ok:true,oldTicketInvalid:true}});
attach();window.AstraeonMonsterBoxHarness=Object.freeze({snapshot});render();
})();
