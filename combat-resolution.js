/* Pure staged calculation. No world, presentation, time, storage or global RNG. */
(() => {
'use strict';
const immutable=value=>{if(value&&typeof value==='object'){Object.values(value).forEach(immutable);Object.freeze(value)}return value};
const clamp=(n,min,max)=>Math.max(min,Math.min(max,n));
class Invalid extends Error{constructor(code,path){super(path);this.code=code;this.path=path}}
const fail=(code,path)=>{throw new Invalid(code,path)};
const number=(n,path,min=0,max=Number.MAX_VALUE)=>{if(!Number.isFinite(n)||n<min||n>max)fail('INVALID_NUMBER',path);return n};
const rate=(n,path)=>number(n,path,0,1);
const object=(v,path)=>{if(!v||typeof v!=='object'||Array.isArray(v))fail('MISSING_OBJECT',path);return v};
// Only plain data crosses this boundary; nested numeric metadata is checked too.
function data(value,path){
 if(typeof value==='number'){if(!Number.isFinite(value))fail('INVALID_NUMBER',path)}
 else if(value!==null&&typeof value==='object'){
  if(!Array.isArray(value)&&Object.getPrototypeOf(value)!==Object.prototype&&Object.getPrototypeOf(value)!==null)fail('INVALID_DATA',path);
  for(const [key,v] of Object.entries(value))data(v,`${path}.${key}`);
 }else if(!['string','boolean','undefined'].includes(typeof value)&&value!==null)fail('INVALID_DATA',path);
}
function validateConfig(c){
 object(c,'config');data(c,'config');
 for(const key of ['accuracy','perfectDodge','critical','defense','resistance','mitigation','damage','timing','damageTypes'])object(c[key],`config.${key}`);
 const a=c.accuracy;number(a.base,'accuracy.base',-Number.MAX_VALUE);number(a.hitFleeScale,'accuracy.hitFleeScale');number(a.levelScale,'accuracy.levelScale',-Number.MAX_VALUE);rate(a.min,'accuracy.min');rate(a.max,'accuracy.max');if(a.min>a.max)fail('INVALID_CONFIG','accuracy.bounds');
 number(c.perfectDodge.scale,'perfectDodge.scale');rate(c.perfectDodge.max,'perfectDodge.max');number(c.critical.scale,'critical.scale');rate(c.critical.max,'critical.max');number(c.critical.multiplier,'critical.multiplier');rate(c.critical.defenseIgnore,'critical.defenseIgnore');if(typeof c.critical.bypassAccuracy!=='boolean')fail('INVALID_CONFIG','critical.bypassAccuracy');
 number(c.resistance.min,'resistance.min',-Number.MAX_VALUE,1);number(c.resistance.max,'resistance.max',c.resistance.min,1);
 for(const key of ['guardReduction','blockReduction','parryReduction'])rate(c.mitigation[key],`mitigation.${key}`);
 number(c.damage.minimum,'damage.minimum');if(!['floor','ceil','round','none'].includes(c.damage.rounding))fail('INVALID_CONFIG','damage.rounding');
 if(!Number.isInteger(c.damage.precision)||c.damage.precision<0||c.damage.precision>15)fail('INVALID_CONFIG','damage.precision');
 number(c.timing.referenceASPD,'timing.referenceASPD',Number.MIN_VALUE);number(c.timing.minInterval,'timing.minInterval');number(c.timing.minCast,'timing.minCast');
 for(const [key,type] of Object.entries(c.damageTypes)){
  if(!type||typeof type.attackStat!=='string'||typeof type.defenseStat!=='string')fail('INVALID_CONFIG',`damageTypes.${key}`);
  const d=object(c.defense[key],`defense.${key}`);if(!['flat','ratio'].includes(d.mode))fail('INVALID_CONFIG',`defense.${key}.mode`);number(d.scale,`defense.${key}.scale`,d.mode==='ratio'?Number.MIN_VALUE:0);
 }
 return c;
}
function normalizeInput(raw,c){
 object(raw,'input');data(raw,'input');
 const input=structuredClone(raw);
 for(const role of ['attacker','defender']){
  const actor=object(input[role],role);number(actor.level,`${role}.level`,1);const s=object(actor.stats,`${role}.stats`);
  for(const key of ['physicalATK','magicATK','HIT','FLEE','CRIT','perfectDodge','DEF','MDEF'])number(s[key],`${role}.stats.${key}`);
  number(s.CRIT,`${role}.stats.CRIT`,0,100);number(s.perfectDodge,`${role}.stats.perfectDodge`,0,100);
 }
 const a=object(input.action,'action'),type=c.damageTypes[a.damageType];if(!Object.hasOwn(c.damageTypes,a.damageType))fail('UNKNOWN_DAMAGE_TYPE','action.damageType');
 number(input.attacker.stats[type.attackStat],`attacker.stats.${type.attackStat}`);number(input.defender.stats[type.defenseStat],`defender.stats.${type.defenseStat}`);
 a.coefficient??=1;number(a.coefficient,'action.coefficient');if(a.baseDamage!==undefined)number(a.baseDamage,'action.baseDamage');
 a.canCrit??=true;a.accuracy??='normal';a.canPerfectDodge??=true;
 for(const key of ['canCrit','canPerfectDodge','canGuard','canBlock','canParry','canShield']){a[key]??=true;if(typeof a[key]!=='boolean')fail('INVALID_POLICY',`action.${key}`)}
 if(!['normal','guaranteed','ignoreFlee'].includes(a.accuracy))fail('INVALID_POLICY','action.accuracy');
 a.penetration??={};object(a.penetration,'action.penetration');a.penetration.flat??=0;a.penetration.percent??=0;number(a.penetration.flat,'penetration.flat');rate(a.penetration.percent,'penetration.percent');
 a.resistanceCategory??=a.damageType;if(typeof a.resistanceCategory!=='string'||!a.resistanceCategory)fail('INVALID_POLICY','resistanceCategory');
 for(const key of ['statusCandidates','onHitCandidates']){a[key]??=[];if(!Array.isArray(a[key]))fail('INVALID_DATA',`action.${key}`)}
 a.tags??=[];if(!Array.isArray(a.tags)||!a.tags.every(tag=>typeof tag==='string'))fail('INVALID_DATA','action.tags');
 const d=input.defender;d.resistances??={};object(d.resistances,'defender.resistances');for(const [key,value] of Object.entries(d.resistances))number(value,`resistances.${key}`,-1,1);
 d.mitigation??={};object(d.mitigation,'defender.mitigation');const m=d.mitigation;
 for(const key of ['guarded','blocked','parried']){m[key]??=false;if(typeof m[key]!=='boolean')fail('INVALID_POLICY',`mitigation.${key}`)}
 m.shield??=0;number(m.shield,'mitigation.shield');for(const key of ['guardReduction','blockReduction','parryReduction'])if(m[key]!==undefined)rate(m[key],`mitigation.${key}`);
 input.context??={};object(input.context,'context');input.context.mode??='pve';if(!['pve','pvp'].includes(input.context.mode))fail('INVALID_POLICY','context.mode');
 return immutable(input);
}
function validate(raw,{config=window.AstraeonCombatResolutionConfig.defaults,rng}={}){
 try{validateConfig(config);if(typeof rng?.next!=='function')fail('INVALID_RNG','rng.next');return immutable({ok:true,input:normalizeInput(raw,config)})}
 catch(e){return immutable({ok:false,code:e.code||'INVALID_INPUT',path:e.path||'input',finalDamage:0})}
}
function resolveAttack(raw,options={}){
 const config=options.config||window.AstraeonCombatResolutionConfig.defaults;
 const checked=validate(raw,{config,rng:options.rng});if(!checked.ok)return checked;
 const input=checked.input,{attacker,defender,action:a}=input,trace=[],rolls=[];
 const stage=(name,values)=>trace.push({stage:name,...values});
 const result={ok:true,outcome:'hit',input,rolls,accuracyResult:null,perfectDodge:false,baseDamage:0,critical:false,criticalMultiplier:1,defenseBeforePenetration:0,effectiveDefense:0,damageAfterDefense:0,resistanceApplied:0,damageAfterResistance:0,guarded:false,blocked:false,parried:false,absorbed:0,mitigated:0,finalDamage:0,statusCandidates:[],onHitCandidates:[],procMetadata:a.procMetadata??{},trace};
 const roll=label=>{let value;try{value=options.rng.next()}catch{fail('INVALID_RNG',label)}if(!Number.isFinite(value)||value<0||value>=1)fail('INVALID_RNG',label);rolls.push({stage:label,value});return value};
 const chance=(value,scale,max)=>clamp(value*scale,0,max);
 try{
  stage('validate',{ok:true});
  // Policy-only crit preselection permits bypass without applying crit damage early.
  let criticalRoll,criticalSelected=false;
  const critChance=chance(attacker.stats.CRIT,config.critical.scale,config.critical.max);
  if(a.canCrit&&config.critical.bypassAccuracy){criticalRoll=roll('criticalPolicy');criticalSelected=criticalRoll<critChance}
  const bypass=a.accuracy==='guaranteed'||criticalSelected;
  const accuracyChance=number(bypass?1:clamp(config.accuracy.base+(attacker.stats.HIT-(a.accuracy==='ignoreFlee'?0:defender.stats.FLEE))*config.accuracy.hitFleeScale+(attacker.level-defender.level)*config.accuracy.levelScale,config.accuracy.min,config.accuracy.max),'accuracyChance',0,1);
  const accuracyRoll=bypass?null:roll('accuracy');const hit=bypass||accuracyRoll<accuracyChance;
  result.accuracyResult={hit,chance:accuracyChance,roll:accuracyRoll,bypassed:bypass,bypassedByCritical:criticalSelected};stage('accuracy',result.accuracyResult);
  if(!hit){result.outcome='miss';return immutable(result)}
  const dodgeChance=a.canPerfectDodge?chance(defender.stats.perfectDodge,config.perfectDodge.scale,config.perfectDodge.max):0;
  const dodgeRoll=a.canPerfectDodge?roll('perfectDodge'):null;result.perfectDodge=a.canPerfectDodge&&dodgeRoll<dodgeChance;stage('perfectDodge',{dodged:result.perfectDodge,chance:dodgeChance,roll:dodgeRoll});
  if(result.perfectDodge){result.outcome='perfectDodge';return immutable(result)}
  result.baseDamage=number((a.baseDamage??attacker.stats[config.damageTypes[a.damageType].attackStat])*a.coefficient,'baseDamage');stage('baseDamage',{damage:result.baseDamage});
  if(a.canCrit&&criticalRoll===undefined){criticalRoll=roll('critical');criticalSelected=criticalRoll<critChance}
  result.critical=criticalSelected;result.criticalMultiplier=criticalSelected?config.critical.multiplier:1;
  const afterCrit=number(result.baseDamage*result.criticalMultiplier,'criticalDamage');stage('critical',{critical:criticalSelected,chance:critChance,roll:criticalRoll??null,multiplier:result.criticalMultiplier,damage:afterCrit});
  result.defenseBeforePenetration=defender.stats[config.damageTypes[a.damageType].defenseStat];
  const afterPen=Math.max(0,result.defenseBeforePenetration*(1-a.penetration.percent)-a.penetration.flat);
  result.effectiveDefense=afterPen*(1-(result.critical?config.critical.defenseIgnore:0));
  const rule=config.defense[a.damageType];
  result.damageAfterDefense=rule.mode==='flat'?Math.max(0,afterCrit-result.effectiveDefense*rule.scale):afterCrit/(1+result.effectiveDefense/rule.scale);
  number(result.damageAfterDefense,'damageAfterDefense');stage('defense',{before:result.defenseBeforePenetration,afterPenetration:afterPen,effective:result.effectiveDefense,damage:result.damageAfterDefense});
  const rawResistance=defender.resistances[a.resistanceCategory]??0;result.resistanceApplied=clamp(rawResistance,config.resistance.min,config.resistance.max);
  result.damageAfterResistance=number(result.damageAfterDefense*(1-result.resistanceApplied),'damageAfterResistance');stage('resistance',{category:a.resistanceCategory,raw:rawResistance,applied:result.resistanceApplied,damage:result.damageAfterResistance});
  const m=defender.mitigation;let damage=result.damageAfterResistance;
  // An absolute defense floor is applied before consumable mitigation. Parry/shield may still reach zero.
  if(afterCrit>0)damage=Math.max(config.damage.minimum,damage);
  result.parried=m.parried&&a.canParry;result.guarded=m.guarded&&a.canGuard;result.blocked=m.blocked&&a.canBlock;
  if(result.parried)damage*=1-(m.parryReduction??config.mitigation.parryReduction);
  if(result.guarded)damage*=1-(m.guardReduction??config.mitigation.guardReduction);
  if(result.blocked)damage*=1-(m.blockReduction??config.mitigation.blockReduction);
  result.absorbed=a.canShield?Math.min(damage,m.shield):0;damage-=result.absorbed;
  result.mitigated=Math.max(0,result.damageAfterResistance-damage);
  const stableDamage=Number(number(damage,'mitigatedDamage').toFixed(config.damage.precision));
  result.finalDamage=number(config.damage.rounding==='none'?stableDamage:Math[config.damage.rounding](stableDamage),'finalDamage');
  if(result.parried&&result.finalDamage===0)result.outcome='parried';else if(result.absorbed>0&&result.finalDamage===0)result.outcome='absorbed';
  stage('mitigation',{guarded:result.guarded,blocked:result.blocked,parried:result.parried,absorbed:result.absorbed,mitigated:result.mitigated,finalDamage:result.finalDamage});
  stage('hpApplication',{pending:true,damage:result.finalDamage});
  // Candidates carry no side effects. Runtime decides whether/when to consume them.
  if(result.finalDamage>0){result.statusCandidates=structuredClone(a.statusCandidates);result.onHitCandidates=structuredClone(a.onHitCandidates)}
  stage('statusOutput',{statusCandidates:result.statusCandidates,onHitCandidates:result.onHitCandidates});return immutable(result);
 }catch(e){return immutable({ok:false,code:e.code||'RESOLUTION_FAILED',path:e.path||'resolution',finalDamage:0,trace,rolls})}
}
function applyCombatResult(hp,result,maxHP=Number.MAX_VALUE){
 try{number(hp,'hp');number(maxHP,'maxHP');if(hp>maxHP)fail('INVALID_HP','hp');if(!result?.ok)return immutable({ok:false,hpBefore:hp,hpAfter:hp,appliedDamage:0,code:result?.code||'REJECTED_RESULT'});number(result.finalDamage,'finalDamage');const hpAfter=clamp(hp-result.finalDamage,0,maxHP);return immutable({ok:true,hpBefore:hp,hpAfter,appliedDamage:hp-hpAfter,killed:hp>0&&hpAfter===0,overkill:Math.max(0,result.finalDamage-hp)})}
 catch(e){return immutable({ok:false,code:e.code||'INVALID_HP',hpBefore:hp,hpAfter:hp,appliedDamage:0})}
}
function resolveAttackInterval(baseInterval,derived,config=window.AstraeonCombatResolutionConfig.defaults){validateConfig(config);number(baseInterval,'baseInterval');number(derived.ASPD,'ASPD',Number.MIN_VALUE);return number(Math.max(config.timing.minInterval,baseInterval*(config.timing.referenceASPD/derived.ASPD)),'attackInterval')}
function resolveCastDuration(baseDuration,derived,config=window.AstraeonCombatResolutionConfig.defaults){validateConfig(config);number(baseDuration,'baseDuration');number(derived.castTimeModifier,'castTimeModifier');return number(Math.max(config.timing.minCast,baseDuration*derived.castTimeModifier),'castDuration')}
window.AstraeonCombatResolution=Object.freeze({validate,normalizeInput,resolveAttack,applyCombatResult,resolveAttackInterval,resolveCastDuration});
})();
