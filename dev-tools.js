/* Developer adapters only. Each owner supplies existing canonical authorities. */
(() => {
'use strict';
const W=window,freeze=W.AstraeonItemDefinitions.freeze;
const fail=code=>freeze({ok:false,code,blockedReason:code});
const integer=(n,min=0)=>Number.isSafeInteger(n)&&n>=min;
const enabled=search=>new URLSearchParams(search).get('dev')==='1';
function create(owner,search){
 if(!enabled(search))return null;
 let busy=false;
 const snapshot=()=>owner.getPlayer()?freeze(structuredClone(owner.saveSnapshot())):null;
 const stats=()=>{const p=owner.getPlayer();return p?freeze({primary:p.getPrimaryStats(),derived:p.getDerivedStats(),modifiers:p.getModifierGroups()}):null};
 function begin(operation){
  if(busy)return fail('DEV_COMMAND_IN_PROGRESS');
  if(!owner.getPlayer())return fail('NO_CHARACTER');
  if(owner.isLoading())return fail('CONTEXT_BLOCKED');
  let before;try{before=snapshot()}catch{return fail('INVALID_SAVE_STATE')}
  busy=true;return {ok:true,operation,before};
 }
 function finish(start,result){
  if(result?.ok===false)return freeze({...result,operation:start.operation,before:start.before,after:snapshot()});
  const persistence=owner.afterMutation?.()??{ok:true};
  return freeze({ok:true,operation:start.operation,before:start.before,after:snapshot(),result:result??null,persistence});
 }
 function run(operation,action){
  const start=begin(operation);if(!start.ok)return start;
  try{return finish(start,action(owner.getPlayer()))}
  catch(error){return finish(start,fail(error instanceof RangeError?'INVALID_VALUE':'INVALID_COMMAND'))}
  finally{busy=false}
 }
 const configured=action=>p=>owner.canConfigure()?action(p):fail('UNSAFE_CONFIGURATION');
 function level(track,n){return run('set-'+track+'-level',p=>integer(n,1)&&n<=W.AstraeonProgressionConfig.progression[track].cap?(track==='base'?p.setBaseLevel(n):p.setBaseJobLevel(n)):fail('INVALID_LEVEL'))}
 function exp(track,n){return run('add-'+track+'-exp',p=>integer(n)?(track==='base'?p.grantBaseExp(n):p.grantJobExp(n)):fail('INVALID_EXP'))}
 const api={
  progression:{setBaseLevel:n=>level('base',n),setJobLevel:n=>level('job',n),addBaseExp:n=>exp('base',n),addJobExp:n=>exp('job',n)},
  items:{give:(id,count=1)=>run('give-item',p=>{
   if(typeof id!=='string'||!W.AstraeonItemDefinitions.getDefinition(id))return fail('UNKNOWN_ITEM');
   if(!integer(count,1))return fail('INVALID_QUANTITY');
   return p.grantItemPackage([{itemId:id,quantity:count}]);
  })},
  money:{give:n=>run('give-gold',p=>p.grantGold(n)),set:n=>run('set-gold',p=>p.setGold(n))},
  skills:{learn:id=>run('learn-skill',configured(p=>typeof id==='string'?p.learnSkill(id):fail('UNKNOWN_SKILL'))),rankUp:id=>run('rank-skill',configured(p=>typeof id==='string'?p.rankUpSkill(id):fail('UNKNOWN_SKILL'))),reset:()=>run('reset-skills',configured(p=>p.resetSkills()))},
  stats:{allocate:(id,count=1)=>run('allocate-stat',configured(p=>{
   if(!W.AstraeonProgressionConfig.primary.keys.includes(id))return fail('UNKNOWN_STAT');
   if(!integer(count,1))return fail('INVALID_QUANTITY');return p.allocateStat(id,count);
  })),reset:()=>run('reset-stats',configured(p=>p.resetStats()))},
  monsters:{spawn:(id,point)=>run('spawn-monster',()=>typeof id==='string'?owner.spawnMonster(id,point):fail('UNKNOWN_MONSTER_DEFINITION')),kill:id=>run('kill-target',()=>id===undefined||typeof id==='string'?owner.killTarget(id):fail('UNKNOWN_MONSTER_INSTANCE'))},
  world:{async teleport(point){
   const start=begin('teleport');if(!start.ok)return start;
   try{return finish(start,await owner.teleport(point))}catch{return finish(start,fail('TELEPORT_FAILED'))}finally{busy=false}
  }},
  inspect:{stats,effects:()=>owner.getPlayer()?freeze({modifiers:owner.getPlayer().getModifierGroups(),equipmentEffects:owner.getPlayer().getEquipmentEffects(),runtime:structuredClone(owner.effects())}):null,save:snapshot,monsters:()=>freeze(structuredClone(owner.monsters())),maps:()=>freeze(structuredClone(owner.maps()))},
  save:{snapshot,wipeTestCharacter:confirmation=>run('wipe-test-character',()=>owner.wipe(confirmation))}
 };
 return freeze(api);
}
W.AstraeonDevTools=freeze({create,enabled});
})();
