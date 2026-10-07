(() => {
'use strict';
const $=id=>document.getElementById(id),stats={physicalATK:100,magicATK:80,HIT:100,FLEE:0,CRIT:0,perfectDodge:0,DEF:0,MDEF:0};
$('input').value=JSON.stringify({attacker:{level:1,stats},defender:{level:1,stats:{...stats,DEF:20},mitigation:{shield:5},resistances:{}},action:{damageType:'physical',coefficient:1,canCrit:true},context:{mode:'pve'}},null,2);
$('resolve').onclick=()=>{try{const result=window.AstraeonCombatResolution.resolveAttack(JSON.parse($('input').value),{rng:window.AstraeonCombatRuntime.sequenceRng(JSON.parse($('rolls').value)),config:window.AstraeonCombatResolutionConfig.configure(JSON.parse($('config').value))});$('result').textContent=JSON.stringify({result,hpApplication:window.AstraeonCombatResolution.applyCombatResult(Number($('hp').value),result)},null,2)}catch(error){$('result').textContent=JSON.stringify({ok:false,message:error.message})}};
$('resolve').click();
})();
