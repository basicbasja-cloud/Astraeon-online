/* Owned inventory opening authorization. Prepare never rolls or reveals contents. */
(() => {
'use strict';
const D=window.AstraeonItemDefinitions,freeze=D.freeze,B=window.AstraeonMonsterBox;
const fail=(code,path)=>freeze({ok:false,code,blockedReason:code,openedCount:0,consumed:false,...(path?{path}:{})});
function create(owner,{catalog=D,tables=window.AstraeonBoxContentTables,getRng,restrictions=()=>true}={}){
 const authorityValid=!!owner&&['getInventory','getRevision','getQuantity','getCurrentHP','commit'].every(key=>typeof owner[key]==='function');
 const tickets=new WeakMap();let epoch=0,serial=0,busy=false,checking=false,retired=false,pending=null;
 function getState(boxItemId,count=1,context={}){
  if(!authorityValid)return fail('NO_AUTHORITY');
  if(retired)return fail('RETIRED_RUNTIME');if(busy||checking)return fail('TRANSACTION_IN_PROGRESS');
  if(!context||typeof context!=='object'||Array.isArray(context))return fail('INVALID_CONTEXT');
  for(const key of ['actorPresent','transitionPending','restricted','menuOpen'])if(context[key]!==undefined&&typeof context[key]!=='boolean')return fail('INVALID_CONTEXT');
  if(context.state!==undefined&&!['town','field','dungeon'].includes(context.state)||context.intent!==undefined&&context.intent!=='inventory')return fail('INVALID_CONTEXT');
  if(!Number.isSafeInteger(count)||count<=0)return fail('INVALID_OPEN_COUNT');if(count>B.limits.openCount)return fail('BATCH_SIZE_LIMIT');
  const compiled=B.compile(boxItemId,{catalog,tables});if(!compiled.ok)return fail(compiled.code,compiled.path);
  const inventory=owner.getInventory(),quantity=owner.getQuantity(boxItemId),hp=owner.getCurrentHP();
  if(context.actorPresent===false||!inventory)return fail('NO_ACTOR');
  if(!Number.isFinite(hp)||hp<0)return fail('INVALID_ACTOR');if(hp===0)return fail('DEAD');
  if(context.transitionPending||context.restricted)return fail('FORBIDDEN_STATE');
  if(!Number.isSafeInteger(quantity)||quantity<0)return fail('INVALID_INVENTORY');if(count>quantity)return fail('INSUFFICIENT_ITEMS');
  const signature=JSON.stringify([compiled.definition,compiled.table]);
  if(pending&&(pending.boxItemId!==boxItemId||pending.count!==count))return fail('OPENING_PENDING');
  if(pending&&pending.signature!==signature)return fail('STALE_CONTENT');
  checking=true;let restriction;try{restriction=restrictions(compiled.definition,freeze(structuredClone(context)))}catch{restriction=false}finally{checking=false}
  if(restriction!==true)return fail(typeof restriction?.code==='string'?restriction.code:'BOX_RESTRICTION');
  return freeze({ok:true,source:'inventory/openableItem',boxItemId,boxContentTableId:compiled.table.id,requestedCount:count,quantity,definition:compiled.definition,table:compiled.table});
 }
 function prepare(boxItemId,count=1,context={}){
  const state=getState(boxItemId,count,context);if(!state.ok)return state;
  if(serial>=Number.MAX_SAFE_INTEGER)return fail('IDENTITY_EXHAUSTED');
  const ticket=freeze({ok:true,source:'inventory/openableItem',openingId:`box-open-${++serial}`,boxItemId,boxContentTableId:state.boxContentTableId,requestedCount:count,quantityBefore:state.quantity,authorizationOnly:true});
  tickets.set(ticket,{epoch,inventory:owner.getInventory(),revision:owner.getRevision(),signature:JSON.stringify([state.definition,state.table]),used:false});return ticket;
 }
 function commit(ticket,context={}){
  const record=ticket&&typeof ticket==='object'?tickets.get(ticket):null;
  if(!record)return fail('INVALID_PACKAGE');if(record.used)return fail('ALREADY_COMMITTED');
  if(retired||record.epoch!==epoch||record.inventory!==owner.getInventory()||record.revision!==owner.getRevision())return fail('STALE_PACKAGE');
  const state=getState(ticket.boxItemId,ticket.requestedCount,context);if(!state.ok)return state;
  const signature=JSON.stringify([state.definition,state.table]);if(signature!==record.signature)return fail('STALE_PACKAGE');
  if(!pending)pending={boxItemId:ticket.boxItemId,count:ticket.requestedCount,signature,attempted:false,resolution:null};
  // A failed post-roll preflight retains ONE private outcome, including a failed
  // RNG attempt. Re-authorizing after unrelated mutations cannot shop another roll.
  busy=true;let applied;
  try{
   applied=owner.commit({itemId:ticket.boxItemId,count:ticket.requestedCount,expectedInventory:record.inventory,expectedRevision:record.revision},()=>{
    if(!pending.attempted){pending.attempted=true;try{pending.resolution=B.resolve(state.table,ticket.requestedCount,getRng?.(),{catalog})}catch{pending.resolution=fail('INVALID_RNG')}}
    return pending.resolution;
   });
  }catch{applied=fail('BOX_COMMIT_REJECTED')}finally{busy=false}
  if(applied?.ok!==true)return fail(applied?.code||'BOX_COMMIT_REJECTED',applied?.path);
  record.used=true;const resolution=pending.resolution;pending=null;epoch++;
  return freeze({ok:true,source:'inventory/openableItem',consumed:true,openingId:ticket.openingId,boxItemId:ticket.boxItemId,boxContentTableId:ticket.boxContentTableId,requestedCount:ticket.requestedCount,openedCount:ticket.requestedCount,quantityBefore:applied.quantityBefore,quantityAfter:applied.quantityAfter,boxes:resolution.boxes,aggregatedStackRewards:applied.stackRewards,instanceRewards:applied.instanceRewards,serialBefore:applied.serialBefore,serialAfter:applied.serialAfter,metadata:resolution.metadata});
 }
 const request=(id,count=1,context={})=>{const ticket=prepare(id,count,context);return ticket.ok?commit(ticket,context):ticket};
 function invalidatePrepared(){if(busy||checking)return fail('TRANSACTION_IN_PROGRESS');epoch++;return freeze({ok:true})}
 function retire(){const result=invalidatePrepared();if(result.ok)retired=true;return result}
 return freeze({getState,prepare,commit,request,invalidatePrepared,retire,snapshot:()=>freeze({source:'inventory/openableItem',retired,epoch,pending:pending?{boxItemId:pending.boxItemId,requestedCount:pending.count,attempted:pending.attempted}:null})});
}
window.AstraeonMonsterBoxRuntime=freeze({create});
})();
