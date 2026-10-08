const {test}=require('node:test');
const assert=require('node:assert/strict');
global.window={};
for(const file of ['skill-nodes','combat','progression-config','progression','stats','skill-definitions','skill-tree','action-loadout','skill-runtime','action-runtime','character-state','item-definitions','item-inventory','inventory-capacity','item-equipment','item-state','action-item-config','item-effects','action-item','action-item-runtime','player-state','save-state','combat-resolution-config','combat-resolution','combat-runtime'])require('../'+file+'.js');
const C=window.AstraeonCombatResolution,R=window.AstraeonCombatRuntime,F=window.AstraeonCombatResolutionConfig;
const sheet=()=>({physicalATK:100,magicATK:80,HIT:100,FLEE:0,CRIT:0,perfectDodge:0,DEF:0,MDEF:0});
const fixture=()=>({attacker:{level:1,stats:sheet()},defender:{level:1,stats:sheet()},action:{damageType:'physical',coefficient:1},context:{mode:'pve'}});
const resolve=(input=fixture(),rolls=[.5,.5,.5],overrides={})=>C.resolveAttack(input,{rng:R.sequenceRng(rolls),config:F.configure(overrides)});
const modified=fn=>{const input=fixture();fn(input);return input};
for(const [name,change] of [
 ['missing attacker',i=>delete i.attacker],['missing defender stats',i=>delete i.defender.stats],['missing required HIT',i=>delete i.attacker.stats.HIT],
 ['NaN snapshot',i=>i.attacker.stats.HIT=NaN],['infinite snapshot',i=>i.defender.stats.MDEF=Infinity],['negative damage',i=>i.action.baseDamage=-1],
 ['negative coefficient',i=>i.action.coefficient=-1],['unknown damage type',i=>i.action.damageType='invalid'],['negative flat penetration',i=>i.action.penetration={flat:-1}],
 ['invalid percent penetration',i=>i.action.penetration={percent:1.1}],['negative level',i=>i.attacker.level=0],['invalid CRIT rate',i=>i.attacker.stats.CRIT=101],
 ['invalid perfect dodge rate',i=>i.defender.stats.perfectDodge=101],['invalid resistance',i=>i.defender.resistances={physical:2}],['invalid shield',i=>i.defender.mitigation={shield:-1}],
 ['invalid mitigation rate',i=>i.defender.mitigation={guardReduction:2}],['invalid action flag',i=>i.action.canCrit=1],['invalid accuracy policy',i=>i.action.accuracy='always'],
 ['invalid candidate data',i=>i.action.statusCandidates={}],['nested infinity metadata',i=>i.context={nested:{bad:Infinity}}],['invalid context mode',i=>i.context.mode='raid'],
 ['negative defense',i=>i.defender.stats.DEF=-1]
 ])test('atomic rejection: '+name,()=>{const i=modified(change),before=structuredClone(i),r=resolve(i);assert.equal(r.ok,false);assert.equal(r.finalDamage,0);assert.deepEqual(i,before);assert.equal(C.applyCombatResult(40,r).hpAfter,40)});
test('physical hit and complete conceptual trace',()=>{const r=resolve();assert.equal(r.finalDamage,100);assert.deepEqual(r.trace.map(s=>s.stage),['validate','accuracy','perfectDodge','baseDamage','critical','defense','resistance','mitigation','hpApplication','statusOutput'])});
test('magical hit consumes magicATK',()=>assert.equal(resolve(modified(i=>i.action.damageType='magical')).finalDamage,80));
test('ordinary miss terminates before perfect dodge and consumes one roll',()=>{const r=resolve(modified(i=>i.defender.stats.FLEE=300),[.9]);assert.equal(r.outcome,'miss');assert.equal(r.rolls.length,1);assert.equal(r.trace.at(-1).stage,'accuracy')});
test('guaranteed hit bypasses accuracy',()=>{const r=resolve(modified(i=>{i.defender.stats.FLEE=999;i.action.accuracy='guaranteed'}));assert.equal(r.outcome,'hit');assert.equal(r.accuracyResult.bypassed,true)});
test('ignore FLEE remains configurable accuracy policy',()=>assert.equal(resolve(modified(i=>{i.defender.stats.FLEE=999;i.action.accuracy='ignoreFlee'})).outcome,'hit'));
test('perfect dodge is separate after accuracy',()=>{const r=resolve(modified(i=>i.defender.stats.perfectDodge=100));assert.equal(r.outcome,'perfectDodge');assert.equal(r.finalDamage,0);assert.equal(C.applyCombatResult(30,r).hpAfter,30);assert.equal(r.trace.at(-1).stage,'perfectDodge')});
test('guaranteed hit remains subject to perfect dodge',()=>assert.equal(resolve(modified(i=>{i.action.accuracy='guaranteed';i.defender.stats.perfectDodge=100})).outcome,'perfectDodge'));
test('perfect dodge exclusion is action data',()=>assert.equal(resolve(modified(i=>{i.action.canPerfectDodge=false;i.defender.stats.perfectDodge=100})).outcome,'hit'));
test('critical success',()=>{const r=resolve(modified(i=>i.attacker.stats.CRIT=100));assert.equal(r.critical,true);assert.equal(r.finalDamage,150)});
test('non critical success',()=>assert.equal(resolve().critical,false));
test('canCrit false disables critical',()=>assert.equal(resolve(modified(i=>{i.attacker.stats.CRIT=100;i.action.canCrit=false})).finalDamage,100));
test('critical coefficient is configurable',()=>assert.equal(resolve(modified(i=>i.attacker.stats.CRIT=100),undefined,{critical:{multiplier:2}}).finalDamage,200));
test('critical scale is configurable',()=>assert.equal(resolve(modified(i=>i.attacker.stats.CRIT=100),undefined,{critical:{scale:0}}).critical,false));
test('critical bypass configured before accuracy, still dodgeable',()=>{const i=modified(i=>{i.attacker.stats.CRIT=100;i.defender.stats.FLEE=999});const r=resolve(i,undefined,{critical:{bypassAccuracy:true}});assert.equal(r.accuracyResult.bypassedByCritical,true);assert.equal(r.critical,true);i.defender.stats.perfectDodge=100;assert.equal(resolve(i,undefined,{critical:{bypassAccuracy:true}}).outcome,'perfectDodge')});
test('physical defense flat reduction',()=>assert.equal(resolve(modified(i=>i.defender.stats.DEF=20)).finalDamage,80));
test('magical defense uses MDEF',()=>assert.equal(resolve(modified(i=>{i.action.damageType='magical';i.defender.stats.MDEF=20;i.defender.stats.DEF=99})).finalDamage,60));
test('flat penetration',()=>assert.equal(resolve(modified(i=>{i.defender.stats.DEF=30;i.action.penetration={flat:10}})).finalDamage,80));
test('percent then flat penetration order',()=>{const r=resolve(modified(i=>{i.defender.stats.DEF=40;i.action.penetration={percent:.5,flat:5}}));assert.equal(r.effectiveDefense,15);assert.equal(r.finalDamage,85)});
test('critical ignore applies after penetration',()=>{const r=resolve(modified(i=>{i.attacker.stats.CRIT=100;i.defender.stats.DEF=40;i.action.penetration={percent:.5,flat:5}}));assert.equal(r.effectiveDefense,10.5);assert.equal(r.finalDamage,139)});
test('critical ignore configurable',()=>assert.equal(resolve(modified(i=>{i.attacker.stats.CRIT=100;i.defender.stats.DEF=40}),undefined,{critical:{defenseIgnore:1}}).finalDamage,150));
test('over penetration cannot create negative defense',()=>assert.equal(resolve(modified(i=>i.action.penetration={flat:999})).effectiveDefense,0));
test('extreme defense yields safe minimum',()=>{const r=resolve(modified(i=>i.defender.stats.DEF=Number.MAX_VALUE));assert.equal(r.finalDamage,1);assert.equal(r.damageAfterDefense,0)});
test('ratio defense is configurable without changing algorithm',()=>assert.equal(resolve(modified(i=>i.defender.stats.DEF=100),undefined,{defense:{physical:{mode:'ratio',scale:100}}}).finalDamage,50));
test('resistance reduction',()=>assert.equal(resolve(modified(i=>i.defender.resistances={physical:.5})).finalDamage,50));
test('resistance upper cap with stable decimal rounding',()=>assert.equal(resolve(modified(i=>i.defender.resistances={physical:1})).finalDamage,20));
test('resistance vulnerability cap',()=>assert.equal(resolve(modified(i=>i.defender.resistances={physical:-1})).finalDamage,160));
test('future resistance category does not require algorithm change',()=>assert.equal(resolve(modified(i=>{i.action.resistanceCategory='future';i.defender.resistances={future:.5}})).finalDamage,50));
test('unknown resistance categories default neutral',()=>assert.equal(resolve(modified(i=>i.action.resistanceCategory='future')).finalDamage,100));
test('guard mitigation separately reported',()=>{const r=resolve(modified(i=>i.defender.mitigation={guarded:true}));assert.equal(r.guarded,true);assert.equal(r.finalDamage,30);assert.equal(r.mitigated,70)});
test('block mitigation separately reported',()=>{const r=resolve(modified(i=>i.defender.mitigation={blocked:true}));assert.equal(r.blocked,true);assert.equal(r.finalDamage,30)});
test('parry removes HP damage and candidates',()=>{const r=resolve(modified(i=>{i.defender.mitigation={parried:true};i.action.statusCandidates=[{id:'burn'}]}));assert.equal(r.parried,true);assert.equal(r.outcome,'parried');assert.equal(r.finalDamage,0);assert.deepEqual(r.statusCandidates,[])});
test('shield absorption reports consumed amount',()=>{const r=resolve(modified(i=>i.defender.mitigation={shield:40}));assert.equal(r.absorbed,40);assert.equal(r.finalDamage,60)});
test('shield fully absorbs even minimum damage',()=>{const r=resolve(modified(i=>{i.defender.stats.DEF=999;i.defender.mitigation={shield:10}}));assert.equal(r.outcome,'absorbed');assert.equal(r.finalDamage,0);assert.equal(r.absorbed,1)});
test('mitigation eligibility flags are independent',()=>{const r=resolve(modified(i=>{i.defender.mitigation={guarded:true,blocked:true,parried:true,shield:100};Object.assign(i.action,{canGuard:false,canBlock:false,canParry:false,canShield:false})}));assert.equal(r.finalDamage,100)});
test('combined mitigation has documented parry guard block shield order',()=>{const r=resolve(modified(i=>i.defender.mitigation={parried:true,parryReduction:.5,guarded:true,guardReduction:.2,blocked:true,blockReduction:.5,shield:5}));assert.equal(r.finalDamage,15);assert.equal(r.absorbed,5)});
test('minimum can be configured',()=>assert.equal(resolve(modified(i=>i.defender.stats.DEF=999),undefined,{damage:{minimum:3}}).finalDamage,3));
test('zero input damage never gains a minimum',()=>assert.equal(resolve(modified(i=>i.action.baseDamage=0)).finalDamage,0));
test('rounding can be configured',()=>assert.equal(resolve(modified(i=>i.action.baseDamage=1.2),undefined,{damage:{rounding:'ceil'}}).finalDamage,2));
test('identical inputs and RNG are deeply reproducible',()=>assert.deepEqual(resolve(),resolve()));
test('seeded provider is reproducible',()=>{const seeded=()=>{let n=17;return {next:()=>((n=(n*1664525+1013904223)>>>0)/4294967296)}};assert.deepEqual(C.resolveAttack(fixture(),{rng:seeded()}),C.resolveAttack(fixture(),{rng:seeded()}))});
test('result is deeply immutable without freezing input',()=>{const i=fixture(),before=structuredClone(i),r=resolve(i);assert.deepEqual(i,before);assert.equal(Object.isFrozen(i),false);assert.equal(Object.isFrozen(r.input.attacker.stats),true);assert.equal(Object.isFrozen(r.trace),true)});
for(const value of [NaN,Infinity,-.1,1,undefined,'0.5'])test('invalid RNG draw '+String(value),()=>{const r=resolve(fixture(),[value]);assert.equal(r.ok,false);assert.equal(r.code,'INVALID_RNG')});
test('RNG exhaustion rejects after prior successful stages atomically',()=>{const r=resolve(fixture(),[.5,.5]);assert.equal(r.ok,false);assert.equal(C.applyCombatResult(20,r).hpAfter,20)});
test('missing RNG is rejected',()=>assert.equal(C.resolveAttack(fixture()).code,'INVALID_RNG'));
test('throwing RNG is structured rejection',()=>assert.equal(C.resolveAttack(fixture(),{rng:{next(){throw Error('bad')}}}).code,'INVALID_RNG'));
test('invalid config is rejected before RNG',()=>{let draws=0;const r=C.resolveAttack(fixture(),{config:F.configure({critical:{multiplier:-1}}),rng:{next(){draws++;return .5}}});assert.equal(r.ok,false);assert.equal(draws,0)});
test('overflow base damage is rejected',()=>assert.equal(resolve(modified(i=>i.action.coefficient=Number.MAX_VALUE)).ok,false));
test('HP application clamps death and overkill',()=>{const r=C.applyCombatResult(40,resolve(),50);assert.equal(r.hpAfter,0);assert.equal(r.appliedDamage,40);assert.equal(r.killed,true);assert.equal(r.overkill,60)});
test('HP application never heals through negative damage',()=>assert.equal(C.applyCombatResult(40,{ok:true,finalDamage:-1}).hpAfter,40));
test('rejected resolution preserves HP',()=>assert.equal(C.applyCombatResult(40,{ok:false}).hpAfter,40));
test('HP result rejects NaN',()=>assert.equal(C.applyCombatResult(40,{ok:true,finalDamage:NaN}).ok,false));
test('HP application leaves result unchanged',()=>{const r=resolve(),before=structuredClone(r);C.applyCombatResult(40,r);assert.deepEqual(r,before)});
test('status candidates output without mutation or application',()=>{const i=modified(i=>{i.action.statusCandidates=[{id:'burn',duration:3}];i.action.onHitCandidates=[{id:'reward'}];i.action.procMetadata={source:'node'}}),r=resolve(i);assert.deepEqual(r.statusCandidates,i.action.statusCandidates);assert.notEqual(r.statusCandidates,i.action.statusCandidates);assert.equal(r.procMetadata.source,'node')});
test('miss cannot output status or on hit',()=>{const r=resolve(modified(i=>{i.defender.stats.FLEE=999;i.action.onHitCandidates=[{id:'reward'}]}),[.9]);assert.deepEqual(r.onHitCandidates,[])});
test('future damage category uses configured derived keys',()=>{const i=fixture();i.action.damageType='future';i.attacker.stats.futureATK=30;i.defender.stats.futureDEF=10;assert.equal(resolve(i,undefined,{damageTypes:{future:{attackStat:'futureATK',defenseStat:'futureDEF'}},defense:{future:{mode:'flat',scale:1}}}).finalDamage,20)});
test('future timing helpers remain separate from Timeline',()=>{assert.equal(C.resolveAttackInterval(1,{ASPD:200}),.5);assert.equal(C.resolveCastDuration(2,{castTimeModifier:.5}),1)});
test('invalid timing data is rejected',()=>assert.throws(()=>C.resolveAttackInterval(1,{ASPD:0})));
test('learned rank, compatible Node and passive derived snapshot feed runtime adapter',()=>{const state=window.AstraeonSave.normalize({name:'fixture',cls:0,baseJobLevel:12,skillPoints:30,actionLoadout:Array(8).fill(null)}),p=window.AstraeonPlayer.attach(state);assert.equal(p.learnSkill('rising-edge').ok,true);p.rankUpSkill('rising-edge');p.rankUpSkill('rising-edge');const before=p.getDerivedStats().physicalATK;p.learnSkill('sword-mastery');assert.equal(p.getDerivedStats().physicalATK,before+2);p.assignSkill(0,'rising-edge');p.setSkillNode('rising-edge','qi');const action=p.compileAction(0),input=R.buildInput({attackerLevel:state.baseLevel,attackerStats:p.getDerivedStats(),action,damageType:'physical'}),r=resolve(input);assert.equal(input.action.coefficient,action.damage);assert.equal(input.context.sourceRank,3);assert.equal(input.context.nodeId,'qi');assert.equal(r.baseDamage,p.getDerivedStats().physicalATK*action.damage);assert.equal(r.statusCandidates[0].node,'qi')});
test('legacy actions retain authorized coefficient',()=>{const action=window.AstraeonCombat.compile('mage','attack'),i=R.buildInput({attackerLevel:1,attackerStats:sheet(),action,damageType:'magical'});assert.equal(resolve(i).baseDamage,80*action.damage)});
