/* Pure Box Content grammar/resolution: no death, ownership, clock or RNG source. */
(() => {
'use strict';
const D=window.AstraeonItemDefinitions,freeze=D.freeze;
const limits=freeze({entries:256,openCount:10000}); // Processing guards, not capacity/UI limits.
const integer=(n,min=1)=>Number.isSafeInteger(n)&&n>=min;
const plain=v=>!!v&&typeof v==='object'&&!Array.isArray(v)&&(Object.getPrototypeOf(v)===Object.prototype||Object.getPrototypeOf(v)===null);
function data(v,ancestors=new Set(),depth=0){
 if(depth>64)return false;
 if(v===null||['string','boolean'].includes(typeof v))return true;
 if(typeof v==='number')return Number.isFinite(v);
 if(!Array.isArray(v)&&!plain(v)||ancestors.has(v))return false;
 ancestors.add(v);const ok=Object.values(v).every(x=>data(x,ancestors,depth+1));ancestors.delete(v);return ok;
}
const fail=(code,path)=>freeze({ok:false,code,blockedReason:code,path});
function validate(table,{catalog=D}={}){
 if(!plain(table)||typeof table.id!=='string'||!table.id.trim()||!Array.isArray(table.entries)||!table.entries.length||table.entries.length>limits.entries)return fail('INVALID_BOX_TABLE','table');
 const ids=new Set();let weight=0,weighted=0;
 for(let index=0;index<table.entries.length;index++){
  const e=table.entries[index],path=`entries.${index}`;
  if(!plain(e)||typeof e.id!=='string'||!e.id.trim())return fail('INVALID_BOX_ENTRY',path);
  if(ids.has(e.id))return fail('DUPLICATE_ENTRY_ID',path+'.id');ids.add(e.id);
  if(typeof e.itemId!=='string'||!catalog.getDefinition(e.itemId))return fail('UNKNOWN_ITEM',path+'.itemId');
  if(!integer(e.minQuantity)||!integer(e.maxQuantity)||e.minQuantity>e.maxQuantity)return fail('INVALID_QUANTITY',path+'.quantity');
  if(!['guaranteed','weighted'].includes(e.rollMode))return fail('INVALID_ROLL_MODE',path+'.rollMode');
  if(e.rollMode==='weighted'){
   if(!Number.isFinite(e.weight)||e.weight<0)return fail('INVALID_WEIGHT',path+'.weight');weight+=e.weight;weighted++;
  }else if(e.weight!==undefined)return fail('INVALID_WEIGHT',path+'.weight');
  if(Object.keys(e).some(k=>!['id','itemId','rollMode','weight','minQuantity','maxQuantity','metadata'].includes(k)))return fail('UNSUPPORTED_BOX_ENTRY',path);
 }
 if(weighted&&(!Number.isFinite(weight)||weight<=0))return fail('INVALID_TOTAL_WEIGHT','entries');
 if(Object.keys(table).some(k=>!['id','entries','metadata'].includes(k))||!data(table))return fail('INVALID_BOX_TABLE','table');
 return freeze({ok:true,boxContentTableId:table.id,totalWeight:weight});
}
function compile(itemId,{catalog=D,tables=window.AstraeonBoxContentTables}={}){
 const d=catalog.getDefinition(itemId);if(!d)return fail('UNKNOWN_ITEM','itemId');
 if(d.kind!=='monsterBox'||d.stackable!==true||!plain(d.openable))return fail('NOT_MONSTER_BOX','itemId');
 if(!integer(d.maxStack)||d.actionItem!==undefined||d.effects!==undefined||!data(d)||Object.keys(d.openable).some(k=>k!=='boxContentTableId'))return fail('INVALID_MONSTER_BOX','definition');
 const id=d.openable.boxContentTableId,table=typeof id==='string'?tables?.getDefinition(id):null;
 if(!table)return fail('UNKNOWN_BOX_TABLE','boxContentTableId');
 const checked=validate(table,{catalog});if(!checked.ok)return checked;
 return freeze({ok:true,source:'inventory/openableItem',definition:freeze(structuredClone(d)),table:freeze(structuredClone(table))});
}
function resolve(table,count,rng,{catalog=D}={}){
 const checked=validate(table,{catalog});if(!checked.ok)return checked;
 if(!integer(count))return fail('INVALID_OPEN_COUNT','count');if(count>limits.openCount)return fail('BATCH_SIZE_LIMIT','count');
 if(typeof rng?.next!=='function')return fail('INVALID_RNG','rng.next');
 table=freeze(structuredClone(table));const boxes=[],totals=new Map();
 const weighted=table.entries.filter(e=>e.rollMode==='weighted'&&e.weight>0);
 try{
  for(let boxIndex=0;boxIndex<count;boxIndex++){
   const rolls=[],rewards=[];
   const draw=(purpose,entryId=null)=>{const value=rng.next();if(!Number.isFinite(value)||value<0||value>=1)throw Error('INVALID_RNG');rolls.push({purpose,entryId,value});return value};
   let selected=null;
   if(weighted.length){const needle=draw('choice')*checked.totalWeight;let cumulative=0;selected=weighted.at(-1);for(const e of weighted){cumulative+=e.weight;if(needle<cumulative){selected=e;break}}}
   for(const e of table.entries){
    if(e.rollMode==='weighted'&&e!==selected)continue;
    const quantity=e.minQuantity===e.maxQuantity?e.minQuantity:e.minQuantity+Math.floor(draw('quantity',e.id)*(e.maxQuantity-e.minQuantity+1));
    const total=(totals.get(e.itemId)||0)+quantity;if(!integer(total))return fail('REWARD_OVERFLOW','itemRewards');
    totals.set(e.itemId,total);rewards.push({entryId:e.id,itemId:e.itemId,quantity});
   }
   boxes.push({boxIndex,rolls,itemRewards:rewards});
  }
 }catch{return fail('INVALID_RNG','rng.next')}
 return freeze({ok:true,boxContentTableId:table.id,requestedCount:count,boxes,itemRewards:[...totals].map(([itemId,quantity])=>({itemId,quantity})),metadata:structuredClone(table.metadata||{})});
}
window.AstraeonMonsterBox=freeze({limits,validate,compile,resolve});
})();
