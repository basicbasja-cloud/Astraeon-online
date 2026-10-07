/* Resource effect dispatcher boundary. No inventory, Stats formulas or side effects. */
(() => {
'use strict';
const freeze=window.AstraeonItemDefinitions.freeze,fail=code=>freeze({ok:false,code});
const plain=value=>!!value&&typeof value==='object'&&!Array.isArray(value)&&(Object.getPrototypeOf(value)===Object.prototype||Object.getPrototypeOf(value)===null);
const handlers=freeze({restoreHP:{current:'currentHP',maximum:'maxHP'},restoreSP:{current:'currentSP',maximum:'maxSP'}});
function compile(raw){
 if(!plain(raw)||!Object.keys(raw).length)return fail('INVALID_ITEM_EFFECT');
 const effects=[];
 for(const [type,amount] of Object.entries(raw)){
  if(!Object.hasOwn(handlers,type)||!Number.isFinite(amount)||amount<=0)return fail('INVALID_ITEM_EFFECT');
  effects.push({type,amount,target:'self'});
 }
 return freeze({ok:true,effects});
}
function validResources(value){return plain(value)&&['currentHP','currentSP','maxHP','maxSP'].every(key=>Number.isFinite(value[key])&&value[key]>=0)&&value.maxHP>0&&value.maxSP>0&&value.currentHP<=value.maxHP&&value.currentSP<=value.maxSP}
function plan(effects,resources){
 if(!validResources(resources))return fail('INVALID_RESOURCE');
 if(!Array.isArray(effects)||!effects.length)return fail('INVALID_ITEM_EFFECT');
 const resourceBefore={...resources},resourceAfter={...resources},effectResults=[];
 for(const effect of effects){
  if(!plain(effect)||effect.target!=='self'||!Object.hasOwn(handlers,effect.type)||!Number.isFinite(effect.amount)||effect.amount<=0)return fail('INVALID_ITEM_EFFECT');
  const handler=handlers[effect.type],before=resourceAfter[handler.current],sum=before+effect.amount;
  if(!Number.isFinite(sum))return fail('INVALID_ITEM_EFFECT');
  const after=Math.min(resourceAfter[handler.maximum],sum);resourceAfter[handler.current]=after;
  effectResults.push({...effect,before,after,applied:after-before});
 }
 return freeze({ok:true,resourceBefore,resourceAfter,effectResults,changed:effectResults.some(effect=>effect.applied>0)});
}
window.AstraeonItemEffects=freeze({compile,plan,validResources});
})();
