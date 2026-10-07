/* Core Spine definitions. Balance values are provisional, not a final balance pass. */
(() => {
'use strict';
function freeze(value){if(value&&typeof value==='object'){Object.values(value).forEach(freeze);Object.freeze(value)}return value}
window.AstraeonProgressionConfig=freeze({
 progression:{
  // Base Class cap is 60. A later authorized tier can supply a different cap/curve.
  base:{cap:60,initialLevel:1,initialPoints:0,pointsPerLevel:3,exp:{linear:45,constant:0,quadratic:0,overrides:{}}},
  job:{cap:50,initialLevel:1,initialPoints:0,pointsPerLevel:1,exp:{linear:30,constant:0,quadratic:0,overrides:{}}},
  storedLevelLimit:999,activityJobExpRatio:1
 },
 primary:{keys:['STR','AGI','VIT','INT','DEX','LUK'],initial:1,cap:99,pointCost:1},
 derived:{
  base:{physicalATK:14,magicATK:14,maxHP:100,maxSP:60,DEF:0,MDEF:0,HIT:100,FLEE:0,CRIT:0,perfectDodge:0,ASPD:100,castTimeModifier:1,carryWeight:1000,physicalResilience:0},
  perBaseLevel:{physicalATK:3,magicATK:3,maxHP:12,maxSP:5,HIT:1,FLEE:1},
  primary:{STR:{physicalATK:2,carryWeight:30},AGI:{ASPD:1,FLEE:1},VIT:{maxHP:10,DEF:.25,carryWeight:5,physicalResilience:.001},INT:{magicATK:2,maxSP:5,MDEF:.25},DEX:{HIT:1,castTimeModifier:-.005},LUK:{CRIT:.3,perfectDodge:.1}},
  limits:{physicalATK:[0,Number.MAX_SAFE_INTEGER],magicATK:[0,Number.MAX_SAFE_INTEGER],maxHP:[1,Number.MAX_SAFE_INTEGER],maxSP:[1,Number.MAX_SAFE_INTEGER],DEF:[0,Number.MAX_SAFE_INTEGER],MDEF:[0,Number.MAX_SAFE_INTEGER],HIT:[0,Number.MAX_SAFE_INTEGER],FLEE:[0,Number.MAX_SAFE_INTEGER],CRIT:[0,100],perfectDodge:[0,100],ASPD:[1,190],castTimeModifier:[.2,3],carryWeight:[0,Number.MAX_SAFE_INTEGER],physicalResilience:[0,.5]},
  integer:['physicalATK','magicATK','maxHP','maxSP','HIT','FLEE','carryWeight'],precision:6
 },
 // Adapter for current string-based gear; no item/schema redesign in this task.
 legacyEquipment:{weapon:{'Astral Blade':{add:{physicalATK:6,magicATK:6}}},armor:{'Warden Plate':{add:{DEF:2}}},relic:{add:{physicalATK:3,magicATK:3}}},
 legacyParty:{add:{maxHP:10}}
});
})();
