/* Disposable inspection only; evidence and rewards use shared authorities. */
(() => {
'use strict';
const $=id=>document.getElementById(id),show=(id,v)=>$(id).textContent=JSON.stringify(v,null,2),key='astraeon-quest-dev-v1';
let state,player,interactions,bridge,lifecycle,actor=null,ticket=null,lastResult=null,time=0,policy=window.AstraeonInventoryCapacity.defaultPolicy;
function attach(raw={name:'Quest disposable',cls:0,itemInventory:window.AstraeonItemInventory.normalize(),equippedItems:{}}){
 state=window.AstraeonSave.normalize(raw);interactions=window.AstraeonQuestEvidence.interactions([{id:'guild-registrar',x:0,y:0}]);
 const actorContext=()=>({zone:0,hp:player.snapshot().currentHP,x:0,y:0});
 player=window.AstraeonPlayer.attach(state,{getCapacityPolicy:()=>policy,getQuestContext:()=>({interaction:interactions.current(actorContext())}),isQuestTalkEvidence:interactions.owns,isQuestKillEvidence:e=>bridge?.owns(e)===true});
 const loot=window.AstraeonMonsterLootRuntime.create({commit:(r,id)=>player.commitMonsterRewards(r,id,[])},{initialKillOrdinal:state.kills});
 lifecycle=window.AstraeonMonsterLifecycle.create({loot,getRewardContext:()=>player.getMonsterRewardContext(2),rng:window.AstraeonCombatRuntime.sequenceRng([])});bridge=window.AstraeonQuestEvidence.deaths(lifecycle,player.observeQuestKill);actor=null;
}
const snapshot=()=>({state:player.getQuestState(),objectives:player.getQuests(),inventory:player.getInventory(),capacity:player.getInventoryCapacityState(),lifecycle:lifecycle.snapshot(),actor:actor?lifecycle.inspect(actor):null,save:window.AstraeonSave.snapshot(state),ticket,lastResult});
function render(){show('definitions',window.AstraeonQuestDefinitions.createRegistry(window.AstraeonQuestDefinitions.definitions));show('ticket',ticket);show('result',lastResult);show('inspection',snapshot())}
function action(fn){try{lastResult=fn()}catch(e){lastResult={ok:false,code:'HARNESS_ERROR',message:e.message}}render()}
for(const d of window.AstraeonQuestDefinitions.definitions)$('quest').add(new Option(d.id,d.id));
$('accept').onclick=()=>action(()=>player.acceptQuest($('quest').value));
$('talk').onclick=()=>action(()=>player.observeQuestTalk(interactions.interact('guild-registrar',{zone:0,hp:player.snapshot().currentHP,x:0,y:0})));
$('give').onclick=()=>action(()=>player.addStack($('item').value,Number($('count').value)));
$('consume').onclick=()=>action(()=>player.consumeStack($('item').value,Number($('count').value)));
$('policy').onclick=()=>action(()=>{const candidate={mode:'bounded',slotLimit:Number($('slots').value),weightLimit:100000,overLimitPolicy:'no-worse'},r=window.AstraeonInventoryCapacity.validatePolicy(candidate);if(r.ok)policy=candidate;return r});
$('spawn').onclick=()=>action(()=>{if(actor)return {ok:false,code:'ALREADY_SPAWNED'};actor={x:5,y:5,hp:10,maxHp:10};return lifecycle.register(actor,'leafmane-fox',{id:'sandbox-fox',home:{x:5,y:5}},time)});
$('attack').onclick=()=>action(()=>{if(!actor)return {ok:false,code:'NO_ACTOR'};const a=window.AstraeonCombat.compile('warrior','attack'),input=window.AstraeonCombatRuntime.buildInput({attackerLevel:player.snapshot().baseLevel,attackerStats:player.getDerivedStats(),action:a,damageType:'physical'}),r=window.AstraeonCombatResolution.resolveAttack(input,{rng:window.AstraeonCombatRuntime.sequenceRng([.5,.5,.5])});if(!r.ok||!lifecycle.inspect(actor).alive)return r;const hp=window.AstraeonCombatResolution.applyHP(actor.hp,actor.maxHp,r);if(!hp.ok)return hp;actor.hp=hp.hpAfter;if(actor.hp>0)return {...r,hp};const death=lifecycle.notifyDeath(actor,++time);return {...r,death,quest:bridge.deliver(actor,death)}});
$('respawn').onclick=()=>action(()=>{if(!actor)return {ok:false,code:'NO_ACTOR'};time+=13;lifecycle.update(actor,{now:time,active:true});return lifecycle.respawn(actor,time)});
$('prepare').onclick=()=>action(()=>ticket=player.prepareQuestTurnIn($('quest').value));
for(const id of ['commit','duplicate'])$(id).onclick=()=>action(()=>player.commitQuestTurnIn(ticket));
$('save').onclick=()=>action(()=>{localStorage.setItem(key,JSON.stringify(window.AstraeonSave.snapshot(state)));return {ok:true,key}});
$('reload').onclick=()=>action(()=>{const raw=localStorage.getItem(key);if(!raw)return {ok:false,code:'NO_SANDBOX_SAVE'};attach(JSON.parse(raw));return {ok:true,oldTicketInvalid:true}});
attach();window.AstraeonQuestHarness=Object.freeze({snapshot});render();
})();
