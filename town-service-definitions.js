/* Immutable local engineering contracts; no final services/economy approval. */
(() => {
'use strict';
const D=window.AstraeonItemDefinitions,freeze=D.freeze;
const plain=v=>!!v&&typeof v==='object'&&!Array.isArray(v)&&(Object.getPrototypeOf(v)===Object.prototype||Object.getPrototypeOf(v)===null);
const id=v=>typeof v==='string'&&!!v.trim()&&v.length<=128&&!['__proto__','constructor','prototype'].includes(v);
const integer=(n,min=0)=>Number.isSafeInteger(n)&&n>=min;
const fail=code=>freeze({ok:false,code,blockedReason:code});
function json(v,seen=new Set(),depth=0){
 if(depth>64)return false;if(v===null||['string','boolean'].includes(typeof v))return true;if(typeof v==='number')return Number.isFinite(v);
 if((!Array.isArray(v)&&!plain(v))||seen.has(v))return false;seen.add(v);
 try{return Object.entries(v).every(([k,x])=>!['__proto__','constructor','prototype'].includes(k)&&json(x,seen,depth+1))}catch{return false}finally{seen.delete(v)}
}
const services=freeze([
 {id:'town-merchant',type:'MERCHANT',interactionTargetId:'merchant',enabled:true,metadata:{source:'existing-prototype'}},
 {id:'storage-proof',type:'STORAGE',interactionTargetId:'housing-keeper',enabled:true,metadata:{fixture:true,design:'NON-FINAL engineering binding; not authored Storage lore'}}
]);
const shops=freeze([{id:'merchant-proof',serviceId:'town-merchant',offers:[
 ...Object.entries(D.merchant).map(([itemId,price])=>({itemId,buyPrice:price.buy??null,sellPrice:price.sell??null})),
 {itemId:'astral-blade',buyPrice:20,sellPrice:4}
],metadata:{balance:'NON-FINAL; original stack prices retained; one existing gear proof offer'}}]);
const storagePolicy=freeze({slotLimit:100,metadata:{balance:'NON-FINAL engineering slots; Storage has no carried weight limit'}});
function validateStoragePolicy(p){return plain(p)&&json(p)&&integer(p.slotLimit)&&Object.keys(p).every(k=>['slotLimit','metadata'].includes(k))?freeze({ok:true,policy:structuredClone(p)}):fail('INVALID_STORAGE_POLICY')}
function registry(authored=services,shopData=shops,{targets=window.AstraeonQuestDefinitions?.targetIds||[],catalog=D}={}){
 try{
  if(!Array.isArray(authored)||!authored.length||authored.length>64||!Array.isArray(shopData)||shopData.length>64)return fail('INVALID_SERVICE_REGISTRY');
  const definitions={},byTarget=new Set(),shopDefinitions={};
  for(const s of authored){if(!plain(s)||!json(s)||!id(s.id)||!['MERCHANT','STORAGE'].includes(s.type)||!targets.includes(s.interactionTargetId)||typeof s.enabled!=='boolean')return fail('INVALID_SERVICE_DEFINITION');if(Object.hasOwn(definitions,s.id)||byTarget.has(s.interactionTargetId))return fail('DUPLICATE_SERVICE_BINDING');definitions[s.id]=structuredClone(s);byTarget.add(s.interactionTargetId)}
  const bound=new Set();for(const shop of shopData){if(!plain(shop)||!json(shop)||!id(shop.id)||definitions[shop.serviceId]?.type!=='MERCHANT'||!Array.isArray(shop.offers)||!shop.offers.length||shop.offers.length>64)return fail('INVALID_SHOP_DEFINITION');if(Object.hasOwn(shopDefinitions,shop.id)||bound.has(shop.serviceId))return fail('DUPLICATE_SHOP');bound.add(shop.serviceId);const items=new Set();
   for(const o of shop.offers){if(!plain(o)||!catalog.getDefinition(o.itemId)||items.has(o.itemId)||!['buyPrice','sellPrice'].every(k=>o[k]===null||integer(o[k]))||o.buyPrice===null&&o.sellPrice===null)return fail('INVALID_SHOP_OFFER');items.add(o.itemId)}shopDefinitions[shop.id]=structuredClone(shop)
  }
  if(Object.values(definitions).some(s=>s.type==='MERCHANT'&&!bound.has(s.id)))return fail('MISSING_SHOP');
  return freeze({ok:true,definitions,shops:shopDefinitions,getService:key=>typeof key==='string'&&Object.hasOwn(definitions,key)?definitions[key]:null,getShop:key=>typeof key==='string'&&Object.hasOwn(shopDefinitions,key)?shopDefinitions[key]:null,forTarget:key=>Object.values(definitions).find(s=>s.interactionTargetId===key)||null});
 }catch{return fail('INVALID_SERVICE_REGISTRY')}
}
window.AstraeonTownServiceDefinitions=freeze({services,shops,storagePolicy,registry,validateStoragePolicy,json,plain,id,integer,fail});
})();
