/* Local per-life entitlement authority. AI/respawn timing and pickup are callers. */
(() => {
'use strict';
const freeze=window.AstraeonItemDefinitions.freeze,R=window.AstraeonLootResolution;
const fail=code=>freeze({ok:false,code,blockedReason:code,committed:false});
function create(owner,{monsters=window.AstraeonMonsterDefinitions,tables=window.AstraeonDropTables,catalog=window.AstraeonItemDefinitions,initialKillOrdinal=0}={}){
 if(!Number.isSafeInteger(initialKillOrdinal)||initialKillOrdinal<0)throw new TypeError('Invalid initial kill ordinal');
 const actors=new WeakMap(),claims=new WeakMap();let serial=0,ordinal=initialKillOrdinal,epoch=0,busy=false;const events=[];
 const record=value=>{events.push(value);if(events.length>64)events.shift()};
 function register(actor,definitionId){
  if(busy)return fail('TRANSACTION_IN_PROGRESS');
  if(!actor||typeof actor!=='object'||!Number.isFinite(actor.hp)||actor.hp<=0)return fail('INVALID_MONSTER');
  if(actors.has(actor))return fail('ALREADY_REGISTERED');
  const definition=monsters.getDefinition(definitionId);if(!definition)return fail('UNKNOWN_MONSTER');
  const checked=R.validateReference(definition.dropTableId,{tables,catalog});if(!checked.ok)return checked;
  if(serial>=Number.MAX_SAFE_INTEGER)return fail('IDENTITY_EXHAUSTED');
  actors.set(actor,{instanceId:`monster-${++serial}`,definition,life:1,epoch,claim:null,attempt:null});return inspect(actor);
 }
 function inspect(actor){const a=actors.get(actor);return a?freeze({ok:true,monsterInstanceId:a.instanceId,monsterDefinitionId:a.definition.id,lifeGeneration:a.life,deathId:a.attempt?.deathId||null,claimState:a.claim?(claims.get(a.claim).used?'committed':'pending'):a.attempt?'failed':'alive',active:a.epoch===epoch}):fail('UNKNOWN_MONSTER_INSTANCE')}
 function prepareDeath(actor,context,rng){
  if(busy)return fail('TRANSACTION_IN_PROGRESS');const a=actors.get(actor);
  if(!a||a.epoch!==epoch)return fail('STALE_MONSTER');
  if(a.claim)return a.claim;if(a.attempt)return a.attempt.result;
  if(actor.hp!==0)return fail('MONSTER_NOT_DEAD');
  if(ordinal>=Number.MAX_SAFE_INTEGER)return fail('IDENTITY_EXHAUSTED');
  const deathId=`${a.instanceId}:life-${a.life}:death-1`;
  // Cache even a failed authored/RNG attempt: another call cannot reroll this death.
  a.attempt={deathId,result:fail('RESOLUTION_IN_PROGRESS')};busy=true;
  try{
   const killOrdinal=a.definition.metadata?.fixture?ordinal+1:++ordinal;
   const resolution=R.resolve(tables.getDefinition(a.definition.dropTableId),{...context,monsterInstanceId:a.instanceId,monsterDefinitionId:a.definition.id,deathId,lifeGeneration:a.life,killOrdinal},rng,{catalog});
   if(!resolution.ok){a.attempt.result=resolution;return resolution}
   const claim=freeze({ok:true,claimId:deathId,deathId,resolution,rewardProfileId:a.definition.rewardProfileId});
   claims.set(claim,{actor,life:a.life,epoch,used:false});a.claim=claim;a.attempt.result=claim;return claim;
  }catch{a.attempt.result=fail('RESOLUTION_REJECTED');return a.attempt.result}finally{busy=false}
 }
 function commit(claim){
  const ticket=claim&&typeof claim==='object'?claims.get(claim):null;
  if(!ticket)return fail('INVALID_CLAIM');if(ticket.used)return fail('ALREADY_COMMITTED');if(busy)return fail('TRANSACTION_IN_PROGRESS');
  const a=actors.get(ticket.actor);if(ticket.epoch!==epoch||a.life!==ticket.life||a.claim!==claim||ticket.actor.hp!==0)return fail('STALE_CLAIM');
  busy=true;let result;try{result=owner.commit(claim.resolution,claim.rewardProfileId)}catch{result=fail('REWARD_COMMIT_REJECTED')}finally{busy=false}
  if(result?.ok!==true)return fail(result?.code||'REWARD_COMMIT_REJECTED');
  ticket.used=true;const value=freeze({...result,ok:true,committed:true,deathId:claim.deathId,claimId:claim.claimId});record(value);return value;
 }
 function newLife(actor){
  if(busy)return fail('TRANSACTION_IN_PROGRESS');const a=actors.get(actor);
  if(!a||a.epoch!==epoch)return fail('STALE_MONSTER');
  if(!a.attempt||!Number.isFinite(actor.hp)||actor.hp<=0)return fail('INVALID_NEW_LIFE');
  if(a.life>=Number.MAX_SAFE_INTEGER)return fail('IDENTITY_EXHAUSTED');a.life++;a.claim=null;a.attempt=null;return inspect(actor);
 }
 function retireAll(){if(busy)return fail('TRANSACTION_IN_PROGRESS');epoch++;return freeze({ok:true})}
 return freeze({register,inspect,prepareDeath,commit,newLife,retireAll,snapshot:()=>freeze({epoch,lastKillOrdinal:ordinal,registeredCount:serial,events:[...events]})});
}
window.AstraeonMonsterLootRuntime=freeze({create});
})();
