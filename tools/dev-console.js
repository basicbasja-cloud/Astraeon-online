/* Presentation only: commands act on the real same-origin game frame. */
(() => {
'use strict';
const $=id=>document.getElementById(id),n=id=>Number($(id).value),point=()=>({zone:n('zone'),x:n('x'),y:n('y')});
const actions={
 'base-level':d=>d.progression.setBaseLevel(n('value')),'job-level':d=>d.progression.setJobLevel(n('value')),
 'base-exp':d=>d.progression.addBaseExp(n('value')),'job-exp':d=>d.progression.addJobExp(n('value')),
 'give-item':d=>d.items.give($('item').value,n('count')),gold:d=>d.money.give(n('value')),
 learn:d=>d.skills.learn($('skill').value),rank:d=>d.skills.rankUp($('skill').value),'reset-skills':d=>d.skills.reset(),
 allocate:d=>d.stats.allocate($('stat').value,n('count')),'reset-stats':d=>d.stats.reset(),
 spawn:d=>d.monsters.spawn($('monster').value,point()),kill:d=>d.monsters.kill($('target').value||undefined),teleport:d=>d.world.teleport(point()),
 stats:d=>d.inspect.stats(),effects:d=>d.inspect.effects(),snapshot:d=>d.save.snapshot(),monsters:d=>d.inspect.monsters(),maps:d=>d.inspect.maps(),wipe:d=>d.save.wipeTestCharacter($('confirmation').value)
};
for(const b of document.querySelectorAll('[data-command]'))b.onclick=async()=>{
 const d=$('game').contentWindow.AstraeonDev;if(!d){$('result').textContent=JSON.stringify({ok:false,code:'DEV_GAME_NOT_READY'});return}
 b.disabled=true;try{const r=await actions[b.dataset.command](d);$('result').textContent=JSON.stringify(r,null,2);if(b.dataset.command==='spawn'&&r.ok)$('target').value=r.result.monster.instanceId}catch{$('result').textContent=JSON.stringify({ok:false,code:'DEV_COMMAND_FAILED'})}finally{b.disabled=false}
};
})();
