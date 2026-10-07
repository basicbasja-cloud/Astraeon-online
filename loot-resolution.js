/* Pure drop validation/rolling. No ownership, clocks, random source or lifecycle. */
(() => {
'use strict';
const D=window.AstraeonItemDefinitions,freeze=D.freeze;
const object=v=>!!v&&typeof v==='object'&&!Array.isArray(v);
const integer=(v,min=0)=>Number.isSafeInteger(v)&&v>=min;
const fail=(code,path)=>freeze({ok:false,code,path,itemRewards:[],currencyRewards:[]});
function data(v,seen=new Set(),depth=0){
 if(depth>64)return false;
 if(v===null||typeof v==='string'||typeof v==='boolean')return true;
 if(typeof v==='number')return Number.isFinite(v);
 if(typeof v!=='object'||seen.has(v))return false;seen.add(v);
 const ok=(Array.isArray(v)||Object.getPrototypeOf(v)===Object.prototype||Object.getPrototypeOf(v)===null)&&Object.values(v).every(x=>data(x,seen,depth+1));seen.delete(v);return ok;
}
function validate(table,{catalog=D}={}){
 if(!object(table)||typeof table.id!=='string'||!table.id||!Array.isArray(table.entries)||table.entries.length>256)return fail('INVALID_TABLE','table');
 const ids=new Set();
 for(let i=0;i<table.entries.length;i++){
  const e=table.entries[i],path=`entries.${i}`;
  if(!object(e)||typeof e.id!=='string'||!e.id)return fail('INVALID_ENTRY',path);
  if(ids.has(e.id))return fail('DUPLICATE_ENTRY_ID',path+'.id');ids.add(e.id);
  if(typeof e.itemId!=='string'||!catalog.getDefinition(e.itemId))return fail('UNKNOWN_ITEM',path+'.itemId');
  if(!Number.isFinite(e.chance)||e.chance<0||e.chance>1)return fail('INVALID_CHANCE',path+'.chance');
  if(!integer(e.minQuantity,1)||!integer(e.maxQuantity,1)||e.minQuantity>e.maxQuantity)return fail('INVALID_QUANTITY',path+'.quantity');
  if(!['independent','guaranteed'].includes(e.rollMode)||e.rollMode==='guaranteed'&&e.chance!==1)return fail('INVALID_ROLL_MODE',path+'.rollMode');
  if(e.condition!==undefined&&(!object(e.condition)||Object.keys(e.condition).length!==1||!integer(e.condition.killModulo,1)))return fail('INVALID_CONDITION',path+'.condition');
 }
 if(table.currency!==undefined&&(!object(table.currency)||!integer(table.currency.base)||!integer(table.currency.perZone)||Object.keys(table.currency).some(k=>!['base','perZone'].includes(k))))return fail('INVALID_CURRENCY','currency');
 if(!data(table))return fail('INVALID_TABLE','table');
 return freeze({ok:true,tableId:table.id});
}
function validateReference(id,{tables=window.AstraeonDropTables,catalog=D}={}){const table=tables.getDefinition(id);return table?validate(table,{catalog}):fail('UNKNOWN_DROP_TABLE','dropTableId')}
function resolve(table,context,rng,{catalog=D}={}){
 const checked=validate(table,{catalog});if(!checked.ok)return checked;
 if(!object(context)||!data(context)||!integer(context.zone)||!integer(context.killOrdinal,1)||!['deathId','monsterInstanceId','monsterDefinitionId'].every(k=>typeof context[k]==='string'&&context[k]))return fail('INVALID_CONTEXT','context');
 if(typeof rng?.next!=='function')return fail('INVALID_RNG','rng.next');
 const rolls=[],itemRewards=[];
 function roll(entryId,purpose){const value=rng.next();if(!Number.isFinite(value)||value<0||value>=1)throw Error('INVALID_RNG');rolls.push({entryId,purpose,value});return value}
 try{
  for(const e of table.entries){
   if(e.condition&&context.killOrdinal%e.condition.killModulo!==0)continue;
   // Zero/guaranteed chance consumes no RNG. Exact boundary: value < chance.
   const hit=e.chance===1||e.chance>0&&roll(e.id,'chance')<e.chance;
   if(!hit)continue;
   const quantity=e.minQuantity===e.maxQuantity?e.minQuantity:e.minQuantity+Math.floor(roll(e.id,'quantity')*(e.maxQuantity-e.minQuantity+1));
   itemRewards.push({entryId:e.id,itemId:e.itemId,quantity});
  }
 }catch{return fail('INVALID_RNG','rng.next')}
 const gold=table.currency?table.currency.base+table.currency.perZone*context.zone:0;
 if(!integer(gold))return fail('CURRENCY_OVERFLOW','currency');
 return freeze({...structuredClone(context),ok:true,dropTableId:table.id,rolls,itemRewards,currencyRewards:gold?[{currencyId:'gold',amount:gold}]:[],metadata:structuredClone(table.metadata||{})});
}
window.AstraeonLootResolution=freeze({validate,validateReference,resolve});
})();
