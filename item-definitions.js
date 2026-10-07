/* Existing prototype content only. All values remain provisional. */
(() => {
'use strict';
const freeze=value=>{if(value&&typeof value==='object'){Object.values(value).forEach(freeze);Object.freeze(value)}return value};
const definitions={};
function define(id,name,kind,options={}){definitions[id]=freeze({id,name,key:`item.${id}`,kind,stackable:kind!=='equipment',maxStack:kind==='equipment'?1:Number.MAX_SAFE_INTEGER,equipmentSlots:[],weight:0,modifiers:[],requirements:{},tags:[kind],metadata:{balance:'provisional',weight:'unconfigured',source:'existing-prototype'},...options})}
for(const [id,name] of [['herb','Herb'],['ore','Ore'],['shard','Relic Shards']])define(id,name,'material');
define('potion','Healing Flask','consumable',{effects:{restoreHP:45},actionItem:{actionKind:'resourceRestore',target:'self',cooldownGroup:'hp-potion',usableStates:['town','field','dungeon']}});
define('ration','Field Rations','consumable',{effects:{restoreSP:20},actionItem:{actionKind:'resourceRestore',target:'self',cooldownGroup:'sp-potion',usableStates:['town','field','dungeon']}});
define('traveler-blade','Traveler Blade','equipment',{equipmentSlots:['weapon']});
define('astral-blade','Astral Blade','equipment',{equipmentSlots:['weapon'],modifiers:[{add:{physicalATK:6,magicATK:6}}]});
define('adventurer-garb','Adventurer Garb','equipment',{equipmentSlots:['armor']});
define('warden-plate','Warden Plate','equipment',{equipmentSlots:['armor'],modifiers:[{add:{DEF:2}}],effects:{incomingFlatReduction:2}});
for(const [id,name] of [['spirit-charm','Spirit Charm'],['moonveil-sigil','Moonveil Sigil'],['sunstone-crest','Sunstone Crest'],['dawn-circuit','Dawn Circuit'],['veilheart','Veilheart']])define(id,name,'equipment',{equipmentSlots:['relic'],modifiers:[{add:{physicalATK:3,magicATK:3}}]});
const legacyCounters={herb:'herb',ore:'ore',shard:'shard',potion:'potion',ration:'ration',blade:'astral-blade',charm:'spirit-charm',plate:'warden-plate'};
const legacyNames=Object.fromEntries(Object.values(definitions).map(d=>[d.name,d.id]));
const recipes=[{id:'potion',name:'Healing Flask',inputs:{herb:2,shard:1},output:'potion'},{id:'blade',name:'Astral Blade',inputs:{ore:4,shard:2},output:'astral-blade'},{id:'plate',name:'Warden Plate',inputs:{ore:6,shard:3},output:'warden-plate'},{id:'ration',name:'Field Rations',inputs:{herb:1,ore:1},output:'ration'},{id:'charm',name:'Spirit Charm',inputs:{herb:2,shard:2},output:'spirit-charm'}];
const merchant={potion:{buy:15},ration:{buy:8},herb:{buy:5,sell:2},ore:{buy:7,sell:3}};
const getDefinition=id=>typeof id==='string'&&Object.hasOwn(definitions,id)?definitions[id]:null;
window.AstraeonItemDefinitions=freeze({definitions,getDefinition,legacyCounters,legacyNames,recipes,merchant,freeze});
})();
