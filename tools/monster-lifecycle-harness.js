/* Isolated in-memory developer presentation. No playable save key or formulas. */
(() => {
'use strict';
const W=window,D=W.AstraeonMonsterLifecycleDefinitions;
let now=0,actor=null,runtime=null,loot=null,player=null,state=null,latest=null,target={id:'player',x:20,y:0,hp:100};
const out=document.querySelector('#inspection'),result=document.querySelector('#result');
function inspect(){return {now,definition:actor?D.getDefinition(runtime.inspect(actor).definitionId):null,monster:actor?runtime.inspect(actor):null,target:{...target},loot:loot?.snapshot(),inventory:player?.getInventory(),gold:state?.gold,latest}}
function render(){out.textContent=JSON.stringify(inspect(),null,2);result.textContent=JSON.stringify(latest,null,2)}
function spawn(id=D.fixtureIds[0]){
 now=0;state=W.AstraeonSave.normalize({name:'Lifecycle sandbox',cls:0});player=W.AstraeonPlayer.attach(state);
 loot=W.AstraeonMonsterLootRuntime.create({commit:(r,p)=>player.commitMonsterRewards(r,p)});
 runtime=W.AstraeonMonsterLifecycle.create({loot,getRewardContext:()=>player.getMonsterRewardContext(2),rng:W.AstraeonCombatRuntime.sequenceRng([])});
 const hp=D.maxHP(D.getDefinition(id)).maxHP;actor={x:0,y:0,hp,maxHp:hp};target={id:'player',x:20,y:0,hp:100};latest=runtime.register(actor,id,{id:'sandbox-spawn',home:{x:0,y:0}},now);render();return latest;
}
function tick(delta=0){if(!Number.isFinite(delta)||delta<0)return {ok:false,code:'INVALID_TIME'};now+=delta;latest=runtime.update(actor,{now,active:true,target,canRespawn:true});if(latest.impactIntent)latest={...latest,combatAcceptance:runtime.consumeImpact(latest.impactIntent,{now,active:true,target})};render();return latest}
function position(x,y=0){target.x=x;target.y=y;return tick()}
function damage(amount){const applied=W.AstraeonCombatResolution.applyCombatResult(actor.hp,{ok:true,finalDamage:amount},actor.maxHp);if(!applied.ok)return applied;actor.hp=applied.hpAfter;latest=actor.hp===0?runtime.notifyDeath(actor,now):applied;render();return latest}
document.querySelector('#definition').innerHTML=D.fixtureIds.map(id=>`<option>${id}</option>`).join('');
document.querySelector('#spawn').onclick=()=>spawn(document.querySelector('#definition').value);
document.querySelector('#outside').onclick=()=>position(20);document.querySelector('#detect').onclick=()=>position(5);document.querySelector('#attack').onclick=()=>position(1);document.querySelector('#leash').onclick=()=>position(13);
document.querySelector('#home').onclick=()=>{actor.x=0;actor.y=0;tick()};document.querySelector('#advance').onclick=()=>tick(Number(document.querySelector('#delta').value));document.querySelector('#damage').onclick=()=>damage(1);document.querySelector('#kill').onclick=()=>damage(actor.hp);
document.querySelector('#respawn').onclick=()=>{if(actor.hp!==0)return;tick();tick(Math.max(0,runtime.inspect(actor).respawnReadyAt-now))};
W.AstraeonMonsterLifecycleHarness=Object.freeze({snapshot:inspect,spawn,tick,position,damage});spawn();
})();
