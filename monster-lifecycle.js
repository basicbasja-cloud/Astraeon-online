/* One local lifecycle owner. HP/transform remain the existing actor authority.
 * Explicit simulation seconds; structured intents, never damage/nav/render code. */
(() => {
'use strict';
const freeze=window.AstraeonItemDefinitions.freeze,D=window.AstraeonMonsterLifecycleDefinitions;
const states=freeze(['SPAWN','IDLE','DETECT','AGGRO','CHASE','ATTACK','LEASH','RETURN','DEAD','RESPAWN_WAIT']);
const edges=freeze({SPAWN:['IDLE','LEASH','DEAD'],IDLE:['DETECT','LEASH','DEAD'],DETECT:['AGGRO','LEASH','DEAD'],AGGRO:['CHASE','LEASH','DEAD'],CHASE:['ATTACK','LEASH','DEAD'],ATTACK:['CHASE','LEASH','DEAD'],LEASH:['RETURN','DEAD'],RETURN:['IDLE','DEAD'],DEAD:['RESPAWN_WAIT'],RESPAWN_WAIT:['SPAWN']});
const fail=code=>freeze({ok:false,code,blockedReason:code});
const point=p=>!!p&&Number.isFinite(p.x)&&Number.isFinite(p.y);
const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
const time=n=>Number.isFinite(n)&&n>=0;
const targetValid=t=>!!t&&typeof t.id==='string'&&!!t.id&&point(t)&&Number.isFinite(t.hp)&&t.hp>0;
function canTransition(from,to){return typeof from==='string'&&typeof to==='string'&&Object.hasOwn(edges,from)&&edges[from].includes(to)}
function create({loot,getRewardContext=()=>({zone:0}),rng,definitions=D}={}){
 const actors=new WeakMap(),tokens=new WeakMap(),spawns=new Set(),registered=new Set(),history=[];let epoch=0,busy=false;
 const record=e=>{history.push(e);if(history.length>128)history.shift()};
 function valid(actor,r){return r&&r.epoch===epoch&&point(actor)&&Number.isFinite(actor.maxHp)&&actor.maxHp>0&&Number.isFinite(actor.hp)&&actor.hp>=0&&actor.hp<=actor.maxHp}
 function clock(r,now){return time(now)&&now>=r.lastTime}
 function transition(r,to,reason,now,events){
  if(!canTransition(r.state,to))throw Error('Invalid internal transition');
  const e=freeze({type:'stateChanged',instanceId:r.instanceId,spawnId:r.spawnId,lifeGeneration:r.life,fromState:r.state,toState:to,reason,time:now});r.state=to;r.entered=now;r.latest=e;events.push(e);record(e);
 }
 function release(r,reason,now,events){
  if(r.targetId){const e=freeze({type:'targetReleased',instanceId:r.instanceId,targetId:r.targetId,reason,time:now});events.push(e);record(e)}
  r.targetId=null;r.pending=null;r.aggroGeneration++;
 }
 function snapshot(actor){
  const r=actors.get(actor);if(!r)return fail('UNKNOWN_MONSTER_INSTANCE');
  return freeze({ok:true,active:r.epoch===epoch,instanceId:r.instanceId,definitionId:r.definition.id,rewardDefinitionId:r.definition.rewardDefinitionId,spawnId:r.spawnId,lifeGeneration:r.life,state:r.state,stateEnteredAt:r.entered,lastTime:r.lastTime,alive:actor.hp>0&&!['DEAD','RESPAWN_WAIT'].includes(r.state),hp:actor.hp,maxHP:actor.maxHp,position:{x:actor.x,y:actor.y},home:{...r.home},targetId:r.targetId,targetDistance:r.targetDistance,detectRange:r.definition.perception.detectRange,attackRange:r.definition.combat.attackRange,leashRange:r.definition.lifecycle.leashRange,attackReadyAt:r.readyAt,attackReady:r.lastTime>=r.readyAt,attackIntent:r.pending,deathId:r.death?.deathId||null,respawnReadyAt:r.respawnAt,latestTransition:r.latest,rewardResult:r.reward||null});
 }
 function register(actor,definitionId,spawn,now=0){
  if(busy)return fail('TRANSACTION_IN_PROGRESS');if(actors.has(actor))return fail('ALREADY_REGISTERED');
  const checked=definitions.validate(definitions.getDefinition(definitionId));if(!checked.ok)return checked;
  if(!time(now)||!point(actor)||!Number.isFinite(actor.maxHp)||actor.maxHp<=0||!Number.isFinite(actor.hp)||actor.hp<=0||actor.hp>actor.maxHp)return fail('INVALID_MONSTER');
  if(!time(now+checked.definition.combat.initialDelay))return fail('INVALID_TIME');
  if(!spawn||typeof spawn.id!=='string'||!spawn.id.trim()||!point(spawn.home))return fail('INVALID_SPAWN');
  if(spawns.has(spawn.id))return fail('DUPLICATE_SPAWN');
  const identity=loot.register(actor,checked.definition.rewardDefinitionId);if(!identity.ok)return identity;
  const r={definition:checked.definition,spawnId:spawn.id,home:{x:spawn.home.x,y:spawn.home.y},instanceId:identity.monsterInstanceId,life:identity.lifeGeneration,epoch,state:'SPAWN',entered:now,lastTime:now,targetId:null,targetDistance:null,aggroGeneration:0,pending:null,sequence:0,readyAt:now+checked.definition.combat.initialDelay,death:null,reward:null,respawnAt:null,latest:null};
  actors.set(actor,r);registered.add(actor);spawns.add(spawn.id);return snapshot(actor);
 }
 function notifyDeath(actor,now){
  const r=actors.get(actor);if(busy)return fail('TRANSACTION_IN_PROGRESS');
  if(!valid(actor,r))return fail('INVALID_MONSTER');if(!clock(r,now))return fail('INVALID_TIME');if(actor.hp!==0)return fail('MONSTER_NOT_DEAD');
  if(r.death)return freeze({ok:true,duplicate:true,deathEvent:null,reward:r.reward,events:[]});
  const respawnAt=now+r.definition.lifecycle.respawnDelay;if(!time(respawnAt))return fail('INVALID_TIME');
  const events=[];release(r,'AUTHORITATIVE_DEATH',now,events);transition(r,'DEAD','HP_ZERO',now,events);r.lastTime=now;r.respawnAt=respawnAt;
  // Exactly one handoff attempt, even when the reward owner rejects. Loot owns
  // the immutable claim and any retry; normal lifecycle updates never reroll.
  busy=true;let claim,reward;
  try{claim=loot.prepareDeath(actor,getRewardContext(actor),rng);reward=claim.ok?loot.commit(claim):claim}catch{reward=fail('LOOT_HANDOFF_REJECTED')}finally{busy=false}
  r.claim=claim;r.reward=reward;
  r.death=freeze({type:'death',instanceId:r.instanceId,spawnId:r.spawnId,lifeGeneration:r.life,deathId:loot.inspect(actor).deathId||`${r.instanceId}:life-${r.life}:death-1`,time:now,reason:'HP_ZERO'});events.push(r.death);record(r.death);
  return freeze({ok:true,deathEvent:r.death,reward,events});
 }
 function respawn(actor,now){
  const r=actors.get(actor);if(busy)return fail('TRANSACTION_IN_PROGRESS');if(!valid(actor,r))return fail('INVALID_MONSTER');if(!clock(r,now))return fail('INVALID_TIME');
  if(r.state!=='RESPAWN_WAIT'||now<r.respawnAt)return fail('RESPAWN_NOT_READY');
  const checked=definitions.validate(r.definition);if(!checked.ok)return checked;
  if(!time(now+r.definition.combat.initialDelay))return fail('INVALID_TIME');
  if(r.life>=Number.MAX_SAFE_INTEGER)return fail('IDENTITY_EXHAUSTED');
  const before=actor.hp;actor.hp=actor.maxHp;const identity=loot.newLife(actor);if(!identity.ok){actor.hp=before;return identity}
  actor.x=r.home.x;actor.y=r.home.y;r.life=identity.lifeGeneration;r.targetId=null;r.targetDistance=null;r.pending=null;r.aggroGeneration++;r.sequence=0;r.death=null;r.claim=null;r.reward=null;r.respawnAt=null;r.readyAt=now+r.definition.combat.initialDelay;r.lastTime=now;
  const events=[];transition(r,'SPAWN','RESPAWN_READY',now,events);const event=freeze({type:'respawn',instanceId:r.instanceId,spawnId:r.spawnId,lifeGeneration:r.life,time:now});events.push(event);record(event);transition(r,'IDLE','SPAWN_COMPLETE',now,events);return freeze({ok:true,respawnEvent:event,events});
 }
 function update(actor,context){
  const r=actors.get(actor);if(busy)return fail('TRANSACTION_IN_PROGRESS');if(!valid(actor,r))return fail('INVALID_MONSTER');
  if(!context||!clock(r,context.now)||typeof context.active!=='boolean'||context.paused!==undefined&&typeof context.paused!=='boolean'||context.canRespawn!==undefined&&typeof context.canRespawn!=='boolean'||context.attackAllowed!==undefined&&typeof context.attackAllowed!=='boolean')return fail('INVALID_CONTEXT');
  const now=context.now,events=[];let movementIntent=null,attackIntent=null,impactIntent=null;
  if(!time(now+r.definition.combat.windup+r.definition.combat.cadence)||!time(now+r.definition.lifecycle.respawnDelay))return fail('INVALID_TIME');
  if(r.death&&actor.hp!==0)return fail('INVALID_MONSTER');
  if(context.paused)return freeze({ok:true,paused:true,events,movementIntent,attackIntent,impactIntent});
  if(actor.hp===0&&!r.death)return notifyDeath(actor,now);
  r.lastTime=now;
  if(r.state==='DEAD'){transition(r,'RESPAWN_WAIT','DEATH_RECORDED',now,events);return freeze({ok:true,events,movementIntent,attackIntent,impactIntent})}
  if(r.state==='RESPAWN_WAIT'){
   if(context.active&&context.canRespawn&&now>=r.respawnAt)return respawn(actor,now);
   return freeze({ok:true,events,movementIntent,attackIntent,impactIntent});
  }
  if(r.state==='SPAWN')transition(r,'IDLE','SPAWN_COMPLETE',now,events);
  const target=context.target,eligible=context.active&&targetValid(target),homeDistance=distance(actor,r.home),d=eligible?distance(actor,target):null;r.targetDistance=d;
  if(!['RETURN','LEASH'].includes(r.state)&&((r.targetId&&(!eligible||r.targetId!==target.id))||homeDistance>r.definition.lifecycle.leashRange||eligible&&r.targetId&&distance(target,r.home)>r.definition.lifecycle.leashRange)){
   const reason=!eligible?'INVALID_TARGET':r.targetId!==target.id?'TARGET_CHANGED':'HOME_LEASH';release(r,reason,now,events);transition(r,'LEASH',reason,now,events);
  }
  if(r.state==='LEASH')transition(r,'RETURN','RETURN_HOME',now,events);
  if(r.state==='RETURN'){
   if(homeDistance<=r.definition.movement.homeTolerance){transition(r,'IDLE','HOME_REACHED',now,events);return freeze({ok:true,events,movementIntent,attackIntent,impactIntent})}
   movementIntent={type:'movement',mode:'return',targetId:null,position:{...r.home},speed:r.definition.movement.returnSpeed,stopDistance:r.definition.movement.homeTolerance};
  }else if(!context.active){return freeze({ok:true,events,movementIntent,attackIntent,impactIntent})}
  else{
   if(r.state==='IDLE'&&eligible&&d<=r.definition.perception.detectRange&&distance(target,r.home)<=r.definition.lifecycle.leashRange){
    transition(r,'DETECT','DETECTED_TARGET',now,events);r.targetId=target.id;r.aggroGeneration++;
    const acquired=freeze({type:'targetAcquired',instanceId:r.instanceId,targetId:target.id,reason:'DETECTED_TARGET',time:now});events.push(acquired);record(acquired);
    transition(r,'AGGRO','TARGET_ACQUIRED',now,events);transition(r,'CHASE','CHASE_TARGET',now,events);
   }
   if(r.targetId&&eligible){
    const inRange=d<=r.definition.combat.attackRange&&context.attackAllowed!==false;
    if(r.state==='ATTACK'&&!inRange){r.pending=null;transition(r,'CHASE','OUT_OF_ATTACK_RANGE',now,events)}
    if(r.state==='CHASE'&&inRange)transition(r,'ATTACK','ATTACK_RANGE',now,events);
    if(r.state==='CHASE')movementIntent={type:'movement',mode:'chase',targetId:r.targetId,position:{x:target.x,y:target.y},speed:r.definition.movement.speed,stopDistance:r.definition.combat.attackRange};
    if(r.state==='ATTACK'){
     if(r.pending&&now>=r.pending.impactAt)impactIntent=r.pending;
     else if(!r.pending&&now>=r.readyAt){
      const impactAt=now+r.definition.combat.windup,readyAt=impactAt+r.definition.combat.cadence;if(!time(readyAt))return fail('INVALID_TIME');
      const token=freeze({type:'attack',instanceId:r.instanceId,spawnId:r.spawnId,lifeGeneration:r.life,targetId:r.targetId,attackId:`${r.instanceId}:life-${r.life}:attack-${++r.sequence}`,time:now,impactAt});
      tokens.set(token,{actor,epoch,life:r.life,aggro:r.aggroGeneration,impacted:false});r.pending=token;r.readyAt=readyAt;attackIntent=token;record(token);
     }
    }
   }
  }
  return freeze({ok:true,events,movementIntent,attackIntent,impactIntent});
 }
 function canDeliver(token,context){
  const ticket=tokens.get(token),r=ticket&&actors.get(ticket.actor);
  if(!ticket||!valid(ticket.actor,r)||ticket.actor.hp<=0||r.death||ticket.epoch!==epoch||ticket.life!==r.life||ticket.aggro!==r.aggroGeneration||!ticket.impacted&&r.pending!==token||!r.targetId||['DEAD','RESPAWN_WAIT','LEASH','RETURN'].includes(r.state))return fail('STALE_ATTACK');
  if(!context||!clock(r,context.now)||context.active!==true||context.paused||!targetValid(context.target)||context.target.id!==token.targetId||context.now<token.impactAt||distance(context.target,r.home)>r.definition.lifecycle.leashRange||distance(ticket.actor,r.home)>r.definition.lifecycle.leashRange)return fail('INVALID_ATTACK_CONTEXT');
  return freeze({ok:true});
 }
 function consumeImpact(token,context){
  const allowed=canDeliver(token,context);if(!allowed.ok)return allowed;
  const ticket=tokens.get(token),r=actors.get(ticket.actor);if(ticket.impacted||r.pending!==token)return fail('ALREADY_EXECUTED');
  if(r.state!=='ATTACK'||distance(ticket.actor,context.target)>r.definition.combat.attackRange||context.attackAllowed===false)return fail('OUT_OF_ATTACK_RANGE');
  ticket.impacted=true;r.pending=null;r.lastTime=context.now;return freeze({ok:true,attackId:token.attackId});
 }
 function invalidateTargets(now,reason='INVALID_TARGET'){
  if(busy)return fail('TRANSACTION_IN_PROGRESS');if(!time(now)||[...registered].some(a=>!clock(actors.get(a),now)))return fail('INVALID_TIME');
  const events=[];for(const actor of registered){const r=actors.get(actor);release(r,reason,now,events);if(!['DEAD','RESPAWN_WAIT','LEASH','RETURN'].includes(r.state))transition(r,'LEASH',reason,now,events);if(r.state==='LEASH')transition(r,'RETURN','RETURN_HOME',now,events);r.lastTime=now}return freeze({ok:true,events});
 }
 function retireAll(now=0,reason='CONTEXT_INVALIDATED'){
  if(busy)return fail('TRANSACTION_IN_PROGRESS');if(!time(now)||[...registered].some(a=>!clock(actors.get(a),now)))return fail('INVALID_TIME');
  const retired=loot.retireAll();if(!retired.ok)return retired;
  const events=[];for(const actor of registered)release(actors.get(actor),reason,now,events);epoch++;spawns.clear();registered.clear();return freeze({ok:true,reason,time:now,events});
 }
 return freeze({register,inspect:snapshot,update,notifyDeath,respawn,canDeliver,consumeImpact,invalidateTargets,retireAll,snapshot:()=>freeze({epoch,events:[...history]})});
}
window.AstraeonMonsterLifecycle=freeze({states,canTransition,create});
})();
