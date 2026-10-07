/* Immutable prototype compatibility tables and isolated, NON-FINAL proof data. */
(() => {
'use strict';
const freeze=window.AstraeonItemDefinitions.freeze;
const entry=(id,itemId,modulo)=>({id,itemId,rollMode:'guaranteed',chance:1,minQuantity:1,maxQuantity:1,condition:{killModulo:modulo}});
const cycle=[entry('ore-cycle','ore',3),entry('herb-cycle','herb',2),entry('shard-cycle','shard',4)];
const proof=(id,itemId,chance=1,minQuantity=1,maxQuantity=minQuantity)=>({id,itemId,chance,minQuantity,maxQuantity,rollMode:'independent'});
const definitions=freeze({
 'prototype-cycle':{id:'prototype-cycle',entries:cycle,currency:{base:4,perZone:2},metadata:{balance:'existing prototype kill cycle; non-final'}},
 'prototype-echo':{id:'prototype-echo',entries:[...cycle,{...proof('echo-shards','shard',1,3),rollMode:'guaranteed'}],currency:{base:54,perZone:2},metadata:{balance:'existing prototype echo reward; non-final'}},
 'prototype-arena':{id:'prototype-arena',entries:cycle,currency:{base:14,perZone:2},metadata:{balance:'existing prototype sparring reward; non-final'}},
 'proof-material':{id:'proof-material',entries:[proof('material','herb',1,2)],currency:{base:7,perZone:0},metadata:{fixture:true,balance:'non-final'}},
 'proof-consumable':{id:'proof-consumable',entries:[proof('consumable','potion',1,2)],metadata:{fixture:true,balance:'non-final'}},
 'proof-equipment':{id:'proof-equipment',entries:[proof('equipment','astral-blade')],metadata:{fixture:true,balance:'non-final'}},
 'proof-none':{id:'proof-none',entries:[],metadata:{fixture:true,balance:'non-final'}},
 'proof-multi':{id:'proof-multi',entries:[proof('material','herb',.5,1,3),proof('consumable','potion',.5),proof('equipment','astral-blade',.25)],currency:{base:7,perZone:0},metadata:{fixture:true,balance:'non-final'}}
});
window.AstraeonDropTables=freeze({definitions,getDefinition:id=>Object.hasOwn(definitions,id)?definitions[id]:null});
})();
