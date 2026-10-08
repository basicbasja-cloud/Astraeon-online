/* Isolated authored fixtures; no playable state or production bypass. */
(() => {
'use strict';
const D=AstraeonItemDefinitions,C=AstraeonInventoryCapacity,I=AstraeonItemInventory,S=AstraeonSave,key='astraeon-capacity-dev-v1',BOX='monster-box-proof';
let player,state,policy,catalog,loot,actor,claim,ticket,draws=0,rolls=[],index=0,result=null,config;
const show=(id,value)=>document.getElementById(id).textContent=JSON.stringify(value,null,2);
const snapshot=()=>({inventory:player.getInventory(),equipment:player.getEquipment(),capacity:player.getInventoryCapacityState(),stats:player.getDerivedStats(),save:S.snapshot(state),draws,result,boxRuntime:player.getMonsterBoxRuntime()});
function render(){show('inspection',snapshot());show('result',result);show('envelope',{bounds:AstraeonMonsterBox.envelope(AstraeonBoxContentTables.getDefinition('box-proof-basic'),Number(document.getElementById('count').value),{catalog}),acceptance:player.getMonsterBoxState(BOX,Number(document.getElementById('count').value))})}
function attach(raw){state=S.normalize(raw);player=AstraeonPlayer.attach(state,{itemCatalog:catalog,getCapacityPolicy:()=>policy,getBoxRng:()=>({next:()=>{draws++;return rolls[index++]}}),boxTables:config.table?{getDefinition:()=>config.table}:undefined});loot=AstraeonMonsterLootRuntime.create({commit:(r,p)=>player.commitMonsterRewards(r,p)});actor=claim=null}
function reset(options={}){
 config=structuredClone(options);policy={mode:'bounded',slotLimit:options.slotLimit??10,weightLimit:options.weightLimit??10,overLimitPolicy:'no-worse',metadata:{fixture:true}};
 const checked=C.validatePolicy(policy);if(!checked.ok)return checked;policy=checked.policy;
 const weights={herb:.1,ore:.2,shard:.1,potion:.3,ration:.2,'astral-blade':.4,...options.weights};
 const definitions=D.freeze(Object.fromEntries(Object.values(D.definitions).map(d=>[d.id,{...d,weight:weights[d.id]??d.weight}])));catalog=Object.freeze({getDefinition:id=>Object.hasOwn(definitions,id)?definitions[id]:null});
 // Fixture import simulates returning ownership; grants below respect policy.
 let inventory=I.normalize({stacks:options.stacks||{}},catalog);for(const id of options.instances||[]){const added=I.createInstance(inventory,id,{},catalog);if(!added.ok)return added;inventory=added.inventory}
 draws=index=0;rolls=[.4];ticket=null;result=null;attach({name:'Capacity sandbox',cls:options.cls??0,saveVersion:5,itemInventory:inventory,equippedItems:{},equipment:{weapon:'None',armor:'None',relic:'None'}});render();return snapshot();
}
const run=fn=>{try{result=fn();render();return result}catch(error){result={ok:false,code:'HARNESS_ERROR',message:error.message};render();return result}};
const api={snapshot,reset:options=>reset(options),
 setPolicy:(slots,weight)=>run(()=>{const checked=C.validatePolicy({...policy,slotLimit:slots,weightLimit:weight});if(!checked.ok)return checked;const safe=player.invalidatePreparedActions();if(!safe.ok)return safe;policy=checked.policy;return player.getInventoryCapacityState()}),
 preflight:packageData=>run(()=>player.canAcceptItemPackage(packageData)),
 add:(id,count=1)=>run(()=>player.addStack(id,count)),remove:(id,count=1)=>run(()=>player.removeStack(id,count)),create:id=>run(()=>player.createItemInstance(id)),
 equip:(id,slot='weapon')=>run(()=>player.equip(id,slot)),unequip:(slot='weapon')=>run(()=>player.unequip(slot)),
 buy:(id,count=1)=>run(()=>player.buy(id,count)),sell:(id,count=1)=>run(()=>player.sell(id,count)),craft:id=>run(()=>player.craft(id)),
 consume:(id='potion')=>run(()=>{player.setCurrentHP(1);player.setCurrentSP(1);player.resetActionItemCooldowns();return player.useConsumable(id,{now:0,intent:'inventory'})}),
 setRolls:values=>{rolls=[...values];index=0;return {ok:true}},
 prepare:(count=1)=>run(()=>ticket=player.prepareMonsterBoxOpen(BOX,count)),commit:()=>run(()=>player.commitMonsterBoxOpen(ticket)),open:(count=1)=>run(()=>player.openMonsterBoxes(BOX,count)),
 prepareLoot:(id='proof-multi',values=[0,0,0,0])=>run(()=>{actor={hp:1};const registered=loot.register(actor,id);if(!registered.ok)return registered;actor.hp=0;return claim=loot.prepareDeath(actor,player.getMonsterRewardContext(2),AstraeonCombatRuntime.sequenceRng(values))}),commitLoot:()=>run(()=>loot.commit(claim)),
 save:()=>{localStorage.setItem(key,JSON.stringify({config,policy,save:S.snapshot(state)}));return {ok:true}},
 reload:()=>run(()=>{const saved=JSON.parse(localStorage.getItem(key));if(!saved)return {ok:false,code:'NO_SANDBOX_SAVE'};const oldTicket=ticket;reset(saved.config);ticket=oldTicket;policy=saved.policy;attach(saved.save);return snapshot()})};
window.AstraeonCapacityHarness=Object.freeze(api);
document.getElementById('set-policy').onclick=()=>api.setPolicy(Number(document.getElementById('slots').value),Number(document.getElementById('weight').value));
document.getElementById('preflight').onclick=()=>api.preflight(JSON.parse(document.getElementById('candidate').value));
for(const [id,fn] of Object.entries({'add-herb':()=>api.add('herb'),'add-ore':()=>api.add('ore'),'add-instance':()=>api.create('astral-blade'),'give-box':()=>api.add(BOX),'open':()=>api.open(Number(document.getElementById('count').value)),prepare:()=>api.prepare(Number(document.getElementById('count').value)),commit:api.commit,'duplicate':api.commit,save:api.save,reload:api.reload,reset:()=>reset()}))document.getElementById(id).onclick=fn;
reset();
})();
