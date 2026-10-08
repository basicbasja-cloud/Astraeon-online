/* Enemy intent/contact -> existing staged Combat, then existing Player HP owner.
 * Guard is resolver mitigation. Plate DEF already enters derived stats once. */
(() => {
'use strict';
const freeze=window.AstraeonItemDefinitions.freeze;
function resolve({damage,player,guarded=false,level=1,rng}){
 const neutral=window.AstraeonCombatResolutionConfig.defaults.legacyDefender;
 const input={attacker:{level,stats:neutral},defender:{level:player.snapshot().baseLevel,stats:player.getDerivedStats(),mitigation:{guarded,guardReduction:.7}},action:{damageType:'physical',baseDamage:damage,coefficient:1,accuracy:'guaranteed',canCrit:false,canPerfectDodge:false},context:{mode:'pve',sourceSkillId:'prototype-enemy-contact'}};
 const result=window.AstraeonCombatResolution.resolveAttack(input,{rng});
 if(!result.ok)return result;
 const hp=window.AstraeonCombatResolution.applyCombatResult(player.snapshot().currentHP,result,player.snapshot().maxHP);
 return freeze({ok:hp.ok,result,hp});
}
window.AstraeonMonsterCombatRuntime=freeze({resolve});
})();
