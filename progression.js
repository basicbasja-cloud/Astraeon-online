/* Pure progression transitions: no DOM, storage, clock or mutable definitions. */
(() => {
'use strict';
const defaults=window.AstraeonProgressionConfig.progression;
const tracks={base:{level:'baseLevel',exp:'baseExp',points:'statPoints'},job:{level:'baseJobLevel',exp:'baseJobExp',points:'skillPoints'}};
function integer(value,label,min=0,max=Number.MAX_SAFE_INTEGER){if(!Number.isSafeInteger(value)||value<min||value>max)throw new RangeError(`${label} must be an integer from ${min} to ${max}`);return value}
function requirement(level,track,config=defaults){integer(level,'level',1);const d=config[track];if(!d)throw new TypeError('Unknown progression track');if(level>=d.cap)return 0;const curve=d.exp;return integer(curve.overrides[level]??(curve.constant+curve.linear*level+curve.quadratic*level*level),'EXP requirement',1)}
function grant(state,track,amount,config=defaults){
 integer(amount,'EXP');const keys=tracks[track];if(!keys)throw new TypeError('Unknown progression track');
 const next={...state},before=next[keys.level],cap=config[track].cap;
 if(before>=cap){const discarded=integer(next[keys.exp]+amount,'discarded EXP');next[keys.exp]=0;return {state:Object.freeze(next),levelsGained:0,discarded}}
 next[keys.exp]=integer(next[keys.exp]+amount,'total EXP');
 while(next[keys.level]<cap){const needed=requirement(next[keys.level],track,config);if(next[keys.exp]<needed)break;next[keys.exp]-=needed;next[keys.level]++;next[keys.points]=integer(next[keys.points]+config[track].pointsPerLevel,'point balance')}
 const discarded=next[keys.level]>=cap?next[keys.exp]:0;if(discarded)next[keys.exp]=0;
 return {state:Object.freeze(next),levelsGained:next[keys.level]-before,discarded};
}
function setLevel(state,track,level,config=defaults){
 const keys=tracks[track];if(!keys)throw new TypeError('Unknown progression track');integer(level,'level',1,config[track].cap);
 if(level===state[keys.level])return Object.freeze({...state});
 const balance=state[keys.points]+(level-state[keys.level])*config[track].pointsPerLevel;
 integer(balance,'point balance'); // Lowering a level cannot reclaim already spent points.
 return Object.freeze({...state,[keys.level]:level,[keys.exp]:0,[keys.points]:balance});
}
function addPoints(state,track,amount){integer(amount,'points');const keys=tracks[track];if(!keys)throw new TypeError('Unknown progression track');return Object.freeze({...state,[keys.points]:integer(state[keys.points]+amount,'point balance')})}
window.AstraeonProgression=Object.freeze({integer,requirement,grant,setLevel,addPoints,
 getBaseExpRequirement:(level,config=defaults)=>requirement(level,'base',config),getJobExpRequirement:(level,config=defaults)=>requirement(level,'job',config)});
})();
