/* Owned transient access and complete deterministic transaction plans. */
(() => {
'use strict';
const T=window.AstraeonTownServiceDefinitions,S=window.AstraeonStorageState,I=window.AstraeonItemInventory,D=window.AstraeonItemDefinitions,freeze=D.freeze,fail=T.fail;
function create(owner,{catalog=D,registry=T.registry(),rawStorage,storagePolicy=()=>T.storagePolicy}={}){
 let storage=S.normalize(rawStorage,owner.getInventory(),catalog).state,storageRevision=0,epoch=0,session=null,busy=false;
 const tickets=new WeakMap(),openedEvidence=new WeakSet();
 function guarded(fn){if(busy)return fail('TRANSACTION_IN_PROGRESS');busy=true;try{return fn()}catch{return fail('INVALID_SERVICE_STATE')}finally{busy=false}}
 function context(){try{return owner.getContext()}catch{return null}}
 function permitted(service,evidence){
  const c=context();return registry.ok&&service?.enabled&&c?.zone===0&&c.actorPresent!==false&&owner.getCurrentHP()>0&&!c.loading&&!c.transitionPending&&evidence?.targetId===service.interactionTargetId&&owner.isCurrentInteraction(evidence,c)===true;
 }
 function access(type){const service=registry.ok&&registry.getService(session?.serviceId);return service?.type===type&&session.epoch===epoch&&permitted(service,session.evidence)?{ok:true,service}:fail('SERVICE_ACCESS_REQUIRED')}
 function gold(){const n=owner.getGold();return T.integer(n)?{ok:true,value:n}:fail('INVALID_CURRENCY')}
 function plan(request){
  const operation=request?.operation,trade=['buy','sellStack','sellInstance'].includes(operation),transfer=['depositStack','withdrawStack','depositInstance','withdrawInstance'].includes(operation);
  if(!trade&&!transfer)return fail('INVALID_SERVICE_OPERATION');const allowed=access(trade?'MERCHANT':'STORAGE');if(!allowed.ok)return allowed;
  const before=owner.getInventory(),money=gold();if(!money.ok)return money;
  if(trade){
   const shop=Object.values(registry.shops).find(s=>s.serviceId===allowed.service.id),item=operation==='sellInstance'&&Object.hasOwn(before.instances,request.instanceId)?before.instances[request.instanceId]:null;
   if(operation==='sellInstance'&&!item)return fail('UNKNOWN_INSTANCE');
   const itemId=item?.definitionId??request.itemId,d=catalog.getDefinition(itemId),offer=shop?.offers.find(o=>o.itemId===itemId),count=operation==='sellInstance'?1:request.count;
   if(!T.integer(count,1)||count>100000)return fail('INVALID_QUANTITY');
   if(!d||!offer)return fail('INVALID_TRADE');if(operation==='sellStack'&&!d.stackable||operation==='sellInstance'&&d.stackable)return fail('INVALID_TRADE');
   const price=operation==='buy'?offer.buyPrice:offer.sellPrice;if(price===null)return fail(operation==='buy'?'NOT_FOR_SALE':'UNSELLABLE_ITEM');
   const total=price*count;if(!T.integer(total))return fail('CURRENCY_OVERFLOW');if(operation==='buy'&&money.value<total)return fail('INSUFFICIENT_GOLD');
   const currencyAfter=operation==='buy'?money.value-total:money.value+total;if(!T.integer(currencyAfter))return fail('CURRENCY_OVERFLOW');
   const transaction=operation==='buy'?{itemRewards:[{itemId,quantity:count}]}:operation==='sellStack'?{stackDebits:[{itemId,quantity:count}]}:{instanceDebits:[item.instanceId]};
   const capacity=owner.preflight(transaction);if(!capacity.ok)return capacity;
   return freeze({ok:true,operation,itemId,instanceId:item?.instanceId??null,count,total,currencyBefore:money.value,currencyAfter,transaction,capacity});
  }
  const depositing=operation.startsWith('deposit'),unique=operation.endsWith('Instance'),source=depositing?before:S.inventory(storage,before.nextItemSerial,catalog),destination=depositing?S.inventory(storage,before.nextItemSerial,catalog):before;
  let sourceAfter,destinationAfter,moved;
  if(unique){const id=request.instanceId;if(typeof id!=='string'||!Object.hasOwn(source.instances,id))return fail('UNKNOWN_INSTANCE');if(Object.hasOwn(destination.instances,id))return fail('INSTANCE_OWNERSHIP_CONFLICT');
   const removed=I.deleteInstance(source,id,depositing?owner.getEquipment():{},catalog);if(!removed.ok)return removed;
   moved=source.instances[id];sourceAfter=removed.inventory;destinationAfter=freeze({...destination,instances:{...destination.instances,[id]:moved}});
   if(!I.valid(destinationAfter,catalog))return fail('INVALID_TRANSFER');
  }else{const d=catalog.getDefinition(request.itemId),count=request.count;if(!d?.stackable||!T.integer(count,1)||count>100000)return fail('INVALID_QUANTITY');
   const removed=I.removeStack(source,d.id,count,catalog);if(!removed.ok)return removed;const added=I.addStack(destination,d.id,count,catalog);if(!added.ok)return added;sourceAfter=removed.inventory;destinationAfter=added.inventory;moved={itemId:d.id,quantity:count};
  }
  const nextInventory=depositing?sourceAfter:destinationAfter,stored=depositing?destinationAfter:sourceAfter,nextStorage=freeze({schema:1,stacks:stored.stacks,instances:stored.instances,history:stored.history});
  const capacity=owner.preflightOwnership(nextInventory);if(!capacity.ok)return capacity;const storageCapacity=S.evaluate(storage,nextStorage,storagePolicy());if(!storageCapacity.ok)return storageCapacity;
  if(Object.keys(nextStorage.instances).some(id=>Object.hasOwn(nextInventory.instances,id)))return fail('INSTANCE_OWNERSHIP_CONFLICT');
  return freeze({ok:true,operation,moved,nextInventory,nextStorage,capacity,storageCapacity,currencyBefore:money.value,currencyAfter:money.value});
 }
 function prepare(request){return guarded(()=>{if(T.plain(request)&&Object.hasOwn(request,'count')&&(!T.integer(request.count,1)||request.count>100000))return fail('INVALID_QUANTITY');if(!T.plain(request)||!T.json(request)||Object.keys(request).some(k=>!['operation','itemId','instanceId','count'].includes(k)))return fail('INVALID_SERVICE_OPERATION');const fixed=freeze(structuredClone(request)),result=plan(fixed);if(!result.ok)return result;const ticket=freeze({ok:true,operation:result.operation,serviceId:session.serviceId,plan:result});tickets.set(ticket,{request:fixed,session,epoch,inventory:owner.getInventory(),inventoryRevision:owner.getInventoryRevision(),storage,storageRevision,gold:owner.getGold(),used:false});return ticket})}
 function commit(ticket){return guarded(()=>{
  const owned=ticket&&typeof ticket==='object'?tickets.get(ticket):null;if(!owned)return fail('FOREIGN_SERVICE_TICKET');if(owned.used)return fail('SERVICE_TICKET_USED');
  if(owned.epoch!==epoch||owned.session!==session||owned.inventory!==owner.getInventory()||owned.inventoryRevision!==owner.getInventoryRevision()||owned.storage!==storage||owned.storageRevision!==storageRevision||owned.gold!==owner.getGold()){owned.used=true;return fail('STALE_SERVICE_TICKET')}
  const result=plan(owned.request);owned.used=true;if(!result.ok)return result;
  if(owned.inventory!==owner.getInventory()||owned.inventoryRevision!==owner.getInventoryRevision()||owned.gold!==owner.getGold())return fail('STALE_SERVICE_TICKET');
  const publish=()=>{if(result.nextStorage){storage=result.nextStorage;storageRevision++}else owner.setGold(result.currencyAfter);return true};
  const applied=result.nextInventory?owner.commitTransfer(result.nextInventory,owned.inventory,owned.inventoryRevision,publish):owner.commitTrade(result.transaction,owned.inventory,owned.inventoryRevision,publish);
  return applied.ok?freeze({...applied,operation:result.operation,serviceId:session.serviceId,moved:result.moved??null,currencyBefore:result.currencyBefore,currencyAfter:result.currencyAfter,storageRevision,storage,storageCapacity:result.storageCapacity??null}):applied;
 })}
 function request(value){const ticket=prepare(value);return ticket.ok?commit(ticket):ticket}
 function invalidate(){if(busy)return fail('TRANSACTION_IN_PROGRESS');epoch++;session=null;return freeze({ok:true,epoch})}
 return freeze({
  open(serviceId,evidence){return guarded(()=>{const service=registry.ok&&registry.getService(serviceId);if(!permitted(service,evidence))return fail('SERVICE_ACCESS_REQUIRED');if(openedEvidence.has(evidence))return fail('INTERACTION_ALREADY_USED');openedEvidence.add(evidence);epoch++;session=freeze({serviceId,epoch,evidence});return freeze({ok:true,serviceId,type:service.type})})},
  prepare,commit,request,invalidate,getStorage:()=>storage,getStorageRevision:()=>storageRevision,
  snapshot:()=>freeze({registry:registry.ok?registry.definitions:null,shops:registry.ok?registry.shops:null,storage,storageRevision,storageCapacity:S.snapshot(storage,storagePolicy()),epoch,session:session?{serviceId:session.serviceId,valid:access(registry.getService(session.serviceId)?.type).ok}:null}),
  buy:(itemId,count=1)=>request({operation:'buy',itemId,count}),sell:(itemId,count=1)=>request({operation:'sellStack',itemId,count}),sellInstance:instanceId=>request({operation:'sellInstance',instanceId}),
  depositStack:(itemId,count=1)=>request({operation:'depositStack',itemId,count}),withdrawStack:(itemId,count=1)=>request({operation:'withdrawStack',itemId,count}),depositInstance:instanceId=>request({operation:'depositInstance',instanceId}),withdrawInstance:instanceId=>request({operation:'withdrawInstance',instanceId})
 });
}
window.AstraeonTownServiceRuntime=freeze({create});
})();
