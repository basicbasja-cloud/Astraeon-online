/* Durable separate container. No allocator, carried weight, effects or currency. */
(() => {
'use strict';
const D=window.AstraeonItemDefinitions,I=window.AstraeonItemInventory,T=window.AstraeonTownServiceDefinitions,freeze=D.freeze;
const serial=id=>typeof id==='string'&&/^item-[1-9]\d*$/.test(id)&&Number.isSafeInteger(+id.slice(5))?+id.slice(5):0;
function normalize(raw={},carried=I.normalize(),catalog=D){
 const source=T.plain(raw)?raw:{},historyInput=T.json(source.history)?source.history:{};
 const safeMap=value=>Object.fromEntries(Object.entries(T.plain(value)?value:{}).filter(([key])=>!['__proto__','constructor','prototype'].includes(key)).map(([key,v])=>[key,T.json(v)?v:{quarantined:'NON_JSON_DATA'}]));
 const unsupported=source.schema!==undefined&&source.schema!==1;
 const safe={stacks:unsupported?{}:safeMap(source.stacks),instances:unsupported?{}:safeMap(source.instances),history:{...historyInput,...(unsupported?{unsupportedSchema:{schema:T.json(source.schema)?source.schema:'INVALID_SCHEMA',stacks:safeMap(source.stacks),instances:safeMap(source.instances)}}:{})},nextItemSerial:1};
 const normalized=I.normalize(safe,catalog),instances={...normalized.instances},history=structuredClone(normalized.history);
 // Carried ownership wins ambiguous cross-container references. Retain inert
 // evidence, never create a replacement instance or apply archived modifiers.
 for(const [id,item] of Object.entries(instances))if(Object.hasOwn(carried.instances,id)){history.conflicts??={};history.conflicts[id]=item;delete instances[id]}
 let highest=0;for(const id of Object.keys(T.plain(source.instances)?source.instances:{}))highest=Math.max(highest,serial(id));
 // Observe previously quarantined IDs too; repeated loads must not rewind.
 for(const map of [history.instances,history.conflicts])for(const id of Object.keys(map||{}))highest=Math.max(highest,serial(id));
 return freeze({state:{schema:1,stacks:normalized.stacks,instances,history},reservedSerial:highest>=Number.MAX_SAFE_INTEGER?Number.MAX_SAFE_INTEGER:highest+1});
}
function inventory(storage,serialValue,catalog=D){return I.normalize({stacks:storage.stacks,instances:storage.instances,history:storage.history,nextItemSerial:serialValue},catalog)}
function snapshot(storage,policy=T.storagePolicy){const p=T.validateStoragePolicy(policy);if(!p.ok)return p;const stackSlots=Object.values(storage.stacks).filter(n=>n>0).length,instanceSlots=Object.keys(storage.instances).length,occupiedSlots=stackSlots+instanceSlots;return freeze({ok:true,slotLimit:p.policy.slotLimit,occupiedSlots,stackSlots,instanceSlots,freeSlots:Math.max(0,p.policy.slotLimit-occupiedSlots),isOverLimit:occupiedSlots>p.policy.slotLimit,weightPolicy:'not carried'})}
function evaluate(before,after,policy=T.storagePolicy){const a=snapshot(before,policy),b=snapshot(after,policy);if(!a.ok)return a;if(!b.ok)return b;return b.occupiedSlots>Math.max(a.occupiedSlots,a.slotLimit)?T.fail('STORAGE_SLOT_LIMIT_EXCEEDED'):freeze({ok:true,before:a,after:b})}
window.AstraeonStorageState=freeze({normalize,inventory,snapshot,evaluate});
})();
