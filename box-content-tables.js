/* Separate from Monster Drop Tables. One isolated, NON-FINAL opening fixture. */
(() => {
'use strict';
const freeze=window.AstraeonItemDefinitions.freeze;
const definitions=freeze({
 'box-proof-basic':{
  id:'box-proof-basic',
  entries:[
   {id:'material',itemId:'herb',rollMode:'weighted',weight:1,minQuantity:2,maxQuantity:3},
   {id:'consumable',itemId:'potion',rollMode:'weighted',weight:1,minQuantity:1,maxQuantity:1},
   {id:'equipment',itemId:'astral-blade',rollMode:'weighted',weight:1,minQuantity:1,maxQuantity:1}
  ],
  metadata:{fixture:true,balance:'non-final; equal weights are mechanical proof only'}
 }
});
window.AstraeonBoxContentTables=freeze({definitions,getDefinition:id=>typeof id==='string'&&Object.hasOwn(definitions,id)?definitions[id]:null});
})();
