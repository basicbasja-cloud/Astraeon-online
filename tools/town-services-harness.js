/* Isolated engineering actors and canonical public operations, no bypass. */
(() => {
'use strict';
const W=window,$=id=>document.getElementById(id),key='astraeon-town-services-dev-v1',show=(id,x)=>$(id).textContent=JSON.stringify(x,null,2);
let state,player,interactions,ticket=null,lastResult=null,policy=W.AstraeonInventoryCapacity.defaultPolicy;
const context=()=>({zone:0,x:0,y:0,hp:state.hp,actorPresent:true,menuOpen:true});
function attach(raw={name:'Town Services disposable',cls:0,gold:100,itemInventory:W.AstraeonItemInventory.normalize(),equippedItems:{}}){
 state=W.AstraeonSave.normalize(raw);interactions=W.AstraeonQuestEvidence.interactions([{id:'merchant',x:0,y:0},{id:'housing-keeper',x:1,y:0},{id:'guild-registrar',x:0,y:1}]);
 player=W.AstraeonPlayer.attach(state,{getCapacityPolicy:()=>policy,getServiceContext:context,isCurrentServiceInteraction:(e,c)=>interactions.owns(e)&&interactions.current(c)===e,getQuestContext:()=>({interaction:interactions.current(context())}),isQuestTalkEvidence:interactions.owns});
}
const snapshot=()=>({services:player.getTownServices(),inventory:player.getInventory(),equipment:player.getEquipmentSlots(),capacity:player.getInventoryCapacityState(),inventoryRevision:player.getInventoryRevision(),gold:state.gold,serial:player.getInventory().nextItemSerial,quests:player.getQuests(),save:W.AstraeonSave.snapshot(state),ticket,lastResult});
function render(){show('registry',W.AstraeonTownServiceDefinitions.registry());show('inspection',snapshot());show('ticket',ticket);show('result',lastResult)}
function run(fn){try{lastResult=fn()}catch(e){lastResult={ok:false,code:'HARNESS_ERROR',message:e.message}}render();return lastResult}
function interact(serviceId){const r=W.AstraeonTownServiceDefinitions.registry(),s=r.getService(serviceId),e=interactions.interact(s.interactionTargetId,context());if(!e.ok)return e;player.observeQuestTalk(e);return player.openTownService(serviceId,e)}
const item=()=>$('item').value,count=()=>Number($('count').value),instance=()=>$('instance').value;
const request=()=>({operation:$('operation').value,...($('operation').value.endsWith('Instance')?{instanceId:instance()}:{itemId:item(),count:count()})});
for(const id of ['merchant','storage'])$(id).onclick=()=>run(()=>interact(id==='merchant'?'town-merchant':'storage-proof'));
for(const id of ['buy','sell','depositStack','withdrawStack'])$(id).onclick=()=>run(()=>player[id](item(),count()));
for(const id of ['sellItemInstance','depositItemInstance','withdrawItemInstance','unequip'])$(id).onclick=()=>run(()=>player[id](id==='unequip'?'mainHand':instance()));
$('equip').onclick=()=>run(()=>player.equip(instance(),'mainHand'));
$('grant').onclick=()=>run(()=>player.addStack(item(),count()));$('instanceGrant').onclick=()=>run(()=>player.createItemInstance('astral-blade',{source:'town-services-sandbox'}));
$('prepare').onclick=()=>run(()=>ticket=player.prepareTownService(request()));for(const id of ['commit','duplicate'])$(id).onclick=()=>run(()=>player.commitTownService(ticket));
$('policy').onclick=()=>run(()=>{const p={mode:'bounded',slotLimit:Number($('slots').value),weightLimit:1000,overLimitPolicy:'no-worse'},r=W.AstraeonInventoryCapacity.validatePolicy(p);if(r.ok){policy=r.policy;player.invalidatePreparedActions()}return r});
$('accept').onclick=()=>run(()=>player.acceptQuest('quest-proof-collect'));
$('save').onclick=()=>run(()=>{localStorage.setItem(key,JSON.stringify(W.AstraeonSave.snapshot(state)));return {ok:true,key}});
$('reload').onclick=()=>run(()=>{const raw=localStorage.getItem(key);if(!raw)return {ok:false,code:'NO_SANDBOX_SAVE'};attach(JSON.parse(raw));return {ok:true}});
attach();W.AstraeonTownServicesHarness=Object.freeze({snapshot});render();
})();
