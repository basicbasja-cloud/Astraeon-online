/* Executable foundation defaults ONLY. None of these values is final balance. */
(() => {
'use strict';
const freeze=value=>{if(value&&typeof value==='object'){Object.values(value).forEach(freeze);Object.freeze(value)}return value};
const defaults=freeze({
 provisional:true,
 damageTypes:{physical:{attackStat:'physicalATK',defenseStat:'DEF'},magical:{attackStat:'magicATK',defenseStat:'MDEF'}},
 accuracy:{base:1,hitFleeScale:.005,levelScale:0,min:.05,max:1},
 perfectDodge:{scale:.01,max:1},
 critical:{scale:.01,max:1,multiplier:1.5,defenseIgnore:.3,bypassAccuracy:false},
 defense:{physical:{mode:'flat',scale:1},magical:{mode:'flat',scale:1}},
 resistance:{min:-.6,max:.8},
 mitigation:{guardReduction:.7,blockReduction:.7,parryReduction:1},
 damage:{minimum:1,rounding:'floor',precision:6},
 timing:{referenceASPD:100,minInterval:.01,minCast:0},
 // Existing enemies have no authored combat stat sheet. Neutral compatibility fixture.
 legacyDefender:{physicalATK:0,magicATK:0,HIT:100,FLEE:0,CRIT:0,perfectDodge:0,DEF:0,MDEF:0}
});
function configure(overrides={}){
 const merge=(a,b)=>{const out=structuredClone(a);for(const [key,value] of Object.entries(b)){out[key]=value&&typeof value==='object'&&!Array.isArray(value)&&a[key]&&typeof a[key]==='object'?merge(a[key],value):structuredClone(value)}return out};
 return freeze(merge(defaults,overrides));
}
window.AstraeonCombatResolutionConfig=Object.freeze({defaults,configure});
})();
