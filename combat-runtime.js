/* Authorized actions/stat sheets -> resolver. World mutation stays with caller. */
(() => {
'use strict';
const config=window.AstraeonCombatResolutionConfig;
const productionRng=()=>({next:()=>Math.random()});
function sequenceRng(values){const copy=[...values];let index=0;return {next:()=>copy[index++]}}
function buildInput({attackerLevel,attackerStats,defenderLevel=1,defenderStats=config.defaults.legacyDefender,action,damageType,defenderMitigation={},resistances={}}){
 return {attacker:{level:attackerLevel,stats:attackerStats},defender:{level:defenderLevel,stats:defenderStats,mitigation:defenderMitigation,resistances},action:{damageType,coefficient:action.damage,canCrit:true,accuracy:'normal',tags:action.tags||[],resistanceCategory:action.element||damageType,statusCandidates:[{kind:'legacyContact',tags:action.tags||[],node:action.node??null}],onHitCandidates:[{kind:'legacyContactReward'}]},context:{mode:'pve',sourceSkillId:action.learnedSkillId||action.id,sourceRank:action.learnedRank??null,nodeId:action.node??null}};
}
window.AstraeonCombatRuntime=Object.freeze({productionRng,sequenceRng,buildInput});
})();
