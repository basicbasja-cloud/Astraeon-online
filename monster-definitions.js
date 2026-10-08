/* Reward references for EXISTING prototype actors; not the final monster catalogue. */
(() => {
'use strict';
const freeze=window.AstraeonItemDefinitions.freeze;
const speciesIds=['leafmane-fox','mossback-boar','amber-beetle','caravan-outlaw','sporeling','lanternwood-spirit','moonstone-sentinel','veil-serpent'];
const definitions=Object.fromEntries(speciesIds.map(id=>[id,{id,dropTableId:'prototype-cycle',rewardProfileId:'prototype-kill'}]));
definitions['moonveil-guardian']={id:'moonveil-guardian',dropTableId:'prototype-cycle',rewardProfileId:'prototype-boss'};
definitions['astral-echo']={id:'astral-echo',dropTableId:'prototype-echo',rewardProfileId:'prototype-kill'};
definitions['arena-sparring']={id:'arena-sparring',dropTableId:'prototype-arena',rewardProfileId:'prototype-arena'};
for(const suffix of ['material','consumable','equipment','none','multi','monster-box'])definitions['proof-'+suffix]={id:'proof-'+suffix,dropTableId:'proof-'+suffix,rewardProfileId:'proof',metadata:{fixture:true}};
freeze(definitions);
window.AstraeonMonsterDefinitions=freeze({definitions,speciesIds,getDefinition:id=>Object.hasOwn(definitions,id)?definitions[id]:null});
})();
