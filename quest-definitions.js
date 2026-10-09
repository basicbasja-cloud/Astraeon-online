/* Immutable engineering fixtures. No final story, rewards or quest balance. */
(() => {
'use strict';
const freeze=window.AstraeonItemDefinitions.freeze;
const targetIds=freeze(['artisan','gatekeeper','inn-host','quest-board','guild-registrar','merchant','luna-attendant','housing-keeper']);
const plain=v=>!!v&&typeof v==='object'&&!Array.isArray(v)&&(Object.getPrototypeOf(v)===Object.prototype||Object.getPrototypeOf(v)===null);
function json(v,seen=new Set(),depth=0){if(depth>64)return false;if(v===null||['string','boolean'].includes(typeof v))return true;if(typeof v==='number')return Number.isFinite(v);if((!Array.isArray(v)&&!plain(v))||seen.has(v))return false;seen.add(v);try{return Object.values(v).every(x=>json(x,seen,depth+1))}catch{return false}finally{seen.delete(v)}}
const id=v=>typeof v==='string'&&!!v.trim()&&v.length<=128&&!['__proto__','constructor','prototype'].includes(v);
const count=v=>Number.isSafeInteger(v)&&v>0&&v<=100000;
const fail=(code,path)=>freeze({ok:false,code,blockedReason:code,path});
function validate(definition,{catalog=window.AstraeonItemDefinitions,monsters=window.AstraeonMonsterLifecycleDefinitions||window.AstraeonMonsterDefinitions,targets=targetIds}={}){
 try{
  const d=definition;if(!plain(d)||!json(d)||!id(d.id)||d.repeatable!==false||!Array.isArray(d.objectives)||!d.objectives.length||d.objectives.length>32||!Array.isArray(d.prerequisites)||d.prerequisites.length>64||!targets.includes(d.turnInTargetId))return fail('INVALID_QUEST_DEFINITION','definition');
  const seen=new Set();for(const o of d.objectives){
   if(!plain(o)||!id(o.id)||seen.has(o.id)||!count(o.required))return fail('INVALID_OBJECTIVE','objectives');seen.add(o.id);
   if(o.type==='TALK'){if(!targets.includes(o.targetId))return fail('UNKNOWN_INTERACTION_TARGET',o.id)}
   else if(o.type==='KILL'){if(!id(o.monsterDefinitionId)||!monsters?.getDefinition(o.monsterDefinitionId))return fail('UNKNOWN_MONSTER',o.id)}
   else if(o.type==='COLLECT'){if(!id(o.itemId)||!catalog.getDefinition(o.itemId)||typeof o.consumeOnTurnIn!=='boolean')return fail('INVALID_COLLECT',o.id)}
   else return fail('UNKNOWN_OBJECTIVE_TYPE',o.id);
  }
  if(d.prerequisites.some(p=>!id(p)||p===d.id)||new Set(d.prerequisites).size!==d.prerequisites.length)return fail('INVALID_PREREQUISITE',d.id);
  const r=d.rewards;if(!plain(r)||Object.keys(r).some(k=>!['baseExp','jobExp','gold','items'].includes(k))||['baseExp','jobExp','gold'].some(k=>!Number.isSafeInteger(r[k])||r[k]<0)||!Array.isArray(r.items)||r.items.length>64)return fail('INVALID_QUEST_REWARD',d.id);
  const totals={};let units=0;for(const item of r.items){const def=catalog.getDefinition(item?.itemId);if(!def||!count(item.quantity))return fail('INVALID_QUEST_REWARD',d.id);totals[def.id]=(totals[def.id]||0)+item.quantity;if(!Number.isSafeInteger(totals[def.id])||def.stackable&&totals[def.id]>def.maxStack)return fail('INVALID_QUEST_REWARD',d.id);if(!def.stackable)units+=item.quantity}if(units>10000)return fail('REWARD_SIZE_LIMIT',d.id);
  return freeze({ok:true,definition:structuredClone(d)});
 }catch{return fail('INVALID_QUEST_DEFINITION','definition')}
}
function createRegistry(authored,options={}){
 if(!Array.isArray(authored)||!authored.length||authored.length>64)return fail('INVALID_QUEST_REGISTRY','registry');
 const entries=new Map();for(const d of authored){const checked=validate(d,options);if(!checked.ok)return checked;if(entries.has(d.id))return fail('DUPLICATE_QUEST',d.id);entries.set(d.id,checked.definition)}
 for(const d of entries.values())if(d.prerequisites.some(p=>!entries.has(p)))return fail('UNKNOWN_PREREQUISITE',d.id);
 const visiting=new Set(),done=new Set();function visit(key){if(visiting.has(key))return false;if(done.has(key))return true;visiting.add(key);if(!entries.get(key).prerequisites.every(visit))return false;visiting.delete(key);done.add(key);return true}
 if(![...entries.keys()].every(visit))return fail('PREREQUISITE_CYCLE','registry');
 const definitions=freeze(Object.fromEntries(entries));return freeze({ok:true,definitions,ids:[...entries.keys()],getDefinition:key=>typeof key==='string'&&Object.hasOwn(definitions,key)?definitions[key]:null});
}
const rewards=(baseExp=0,jobExp=0,gold=0,items=[])=>({baseExp,jobExp,gold,items});
const make=(key,objectives,r,prerequisites=[])=>({id:'quest-proof-'+key,objectives,prerequisites,turnInTargetId:'guild-registrar',rewards:r,repeatable:false,metadata:{fixture:true,balance:'NON-FINAL engineering proof; no story approval'}});
const talk={id:'talk-registrar',type:'TALK',targetId:'guild-registrar',required:1};
const kill={id:'kill-fox',type:'KILL',monsterDefinitionId:'leafmane-fox',required:2};
const collect={id:'collect-herb',type:'COLLECT',itemId:'herb',required:3,consumeOnTurnIn:true};
const definitions=freeze([
 make('talk',[talk],rewards(3,2,4,[{itemId:'potion',quantity:1}])),
 make('kill',[kill],rewards(5,3,6,[{itemId:'herb',quantity:1}])),
 make('collect',[collect],rewards(0,0,3,[{itemId:'potion',quantity:1}])),
 make('mixed',[talk,{...kill,required:1},{id:'collect-ore',type:'COLLECT',itemId:'ore',required:2,consumeOnTurnIn:true}],rewards(4,2,5,[{itemId:'offhand-proof',quantity:1}])),
 make('chain',[talk],rewards(0,0,1,[{itemId:'ration',quantity:1}]),['quest-proof-talk'])
]);
window.AstraeonQuestDefinitions=freeze({definitions,targetIds,plain,json,id,count,validate,createRegistry});
})();
