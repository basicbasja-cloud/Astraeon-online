/* Semantic interaction and narrow observers of existing Lifecycle output. */
(() => {
'use strict';
const freeze=window.AstraeonItemDefinitions.freeze,fail=code=>freeze({ok:false,code});
function interactions(targets){
 const registry=new Map(targets.filter(n=>window.AstraeonQuestDefinitions.targetIds.includes(n.id)&&Number.isFinite(n.x)&&Number.isFinite(n.y)).map(n=>[n.id,freeze({id:n.id,x:n.x,y:n.y,zone:0})]));
 const issued=new WeakSet();let latest=null,serial=0;
 function permitted(n,c){return n&&c?.zone===n.zone&&Number.isFinite(c.hp)&&c.hp>0&&!c.transitionPending&&!c.loading&&Number.isFinite(c.x)&&Number.isFinite(c.y)&&Math.hypot(n.x-c.x,n.y-c.y)<=2.5}
 function interact(id,context){const target=typeof id==='string'?registry.get(id):null;if(!permitted(target,context))return fail('INVALID_INTERACTION');if(serial>=Number.MAX_SAFE_INTEGER)return fail('IDENTITY_EXHAUSTED');const evidence=freeze({ok:true,type:'NPC_INTERACTED',targetId:id,interactionId:'interaction-'+(++serial)});issued.add(evidence);latest=evidence;return evidence}
 return freeze({interact,owns:e=>!!e&&typeof e==='object'&&issued.has(e),current:context=>latest&&permitted(registry.get(latest.targetId),context)?latest:null,targets:[...registry.values()]});
}
function deaths(lifecycle,observe){
 const issued=new WeakSet(),seen=new WeakSet();
 function deliver(actor,output){
  const event=output?.deathEvent;if(!event||seen.has(event))return fail('NO_NEW_DEATH');
  const state=lifecycle.inspect(actor);
  // Preserve object authority from this Lifecycle owner, never infer death from
  // HP, disappearance or a Loot result. Snapshot retains immutable event identity.
  if(!state.ok||!state.active||state.deathId!==event.deathId||state.instanceId!==event.instanceId||state.lifeGeneration!==event.lifeGeneration||!lifecycle.snapshot().events.includes(event))return fail('INVALID_DEATH_EVIDENCE');
  const evidence=freeze({ok:true,type:'MONSTER_DIED',monsterDefinitionId:state.definitionId,monsterInstanceId:event.instanceId,lifeGeneration:event.lifeGeneration,deathId:event.deathId});
  seen.add(event);issued.add(evidence);return observe(evidence);
 }
 return freeze({deliver,owns:e=>!!e&&typeof e==='object'&&issued.has(e)});
}
window.AstraeonQuestEvidence=freeze({interactions,deaths});
})();
