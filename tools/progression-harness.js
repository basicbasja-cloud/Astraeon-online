/* Presentation only. All authoritative operations use the shared player API. */
(() => {
'use strict';
const key='astraeon-progression-dev-v1',$=id=>document.getElementById(id);
let state,player;
function render(){
 const s=player.snapshot(),summary={baseLevel:s.baseLevel,baseExp:`${s.baseExp} / ${player.getBaseExpRequirement()||'CAP'}`,baseJobLevel:s.baseJobLevel,baseJobExp:`${s.baseJobExp} / ${player.getJobExpRequirement()||'CAP'}`,statPoints:s.statPoints,skillPoints:s.skillPoints,currentHP:`${s.currentHP} / ${s.maxHP}`,currentSP:`${s.currentSP} / ${s.maxSP}`};
 $('summary').replaceChildren(...Object.entries(summary).map(([name,value])=>{const row=document.createElement('tr'),label=document.createElement('th'),cell=document.createElement('td');label.textContent=name;cell.textContent=value;row.append(label,cell);return row}));
 for(const stat of window.AstraeonProgressionConfig.primary.keys)$('value-'+stat).textContent=s[stat];
 $('derived').textContent=JSON.stringify(player.getDerivedStats(),null,2);$('persistent').textContent=JSON.stringify(window.AstraeonSave.snapshot(state),null,2);
 const selected=$('skill-id').value,available=player.getAvailableSkills();
 $('skill-class').value=String(state.cls);
 $('skill-id').replaceChildren(...available.map(({definition:d})=>{const option=document.createElement('option');option.value=d.id;option.textContent=d.name;return option}));
 if(available.some(({definition:d})=>d.id===selected))$('skill-id').value=selected;
 renderNodes();
 $('skill-tree').textContent=JSON.stringify({tree:player.getSkillTree(),skills:available},null,2);
 $('skill-passives').textContent=JSON.stringify(player.getPassiveSkillModifiers(),null,2);
 $('skill-loadout').textContent=JSON.stringify({slots:player.getActionLoadout(),runtime:player.compileAction(number('skill-slot')-1)},null,2);
}
function renderNodes(){
 const id=$('skill-id').value,choices=window.AstraeonSkillNodes.compatibility[id]||[];
 $('skill-node').replaceChildren(...['',...choices].map(node=>{const option=document.createElement('option');option.value=node;option.textContent=node||'Base (no Node)';return option}));
 $('skill-node').value=state.skillNodes[id]||'';
}
function load(){
 const stored=localStorage.getItem(key);state=window.AstraeonSave.normalize(stored?JSON.parse(stored):{name:'Developer test',saveVersion:4});
 if(!state)throw Error('Invalid developer save');player=window.AstraeonPlayer.attach(state);render();
}
function run(operation){try{const result=operation();render();$('status').textContent=result?.ok===false?JSON.stringify(result):'OK'}catch(error){$('status').textContent=error.message}}
const number=id=>Number($(id).value);
for(const stat of window.AstraeonProgressionConfig.primary.keys){
 const line=document.createElement('p'),value=document.createElement('output'),button=document.createElement('button');value.id='value-'+stat;button.textContent='Allocate '+stat;button.dataset.stat=stat;button.onclick=()=>run(()=>player.allocateStat(stat,number('allocation')));line.append(stat+' ',value,' ',button);$('stats').append(line);
}
const actions={
 'grant-base':()=>player.grantBaseExp(number('base-exp')),'grant-job':()=>player.grantJobExp(number('job-exp')),
 'set-base':()=>player.setBaseLevel(number('base-level')),'set-job':()=>player.setBaseJobLevel(number('job-level')),
 'stat-points':()=>player.addStatPoints(number('points')),'skill-points':()=>player.addSkillPoints(number('points')),
 'reset-stats':()=>player.resetStats(),'set-hp':()=>player.setCurrentHP(number('hp')),'set-sp':()=>player.setCurrentSP(number('sp')),
 'learn-skill':()=>player.learnSkill($('skill-id').value),'rank-skill':()=>player.rankUpSkill($('skill-id').value),
 'reset-skills':()=>player.resetSkills(),'assign-skill':()=>player.assignSkill(number('skill-slot')-1,$('skill-id').value),
 'clear-slot':()=>player.assignSkill(number('skill-slot')-1,null),'set-node':()=>player.setSkillNode($('skill-id').value,$('skill-node').value||null),
 save:()=>localStorage.setItem(key,JSON.stringify(window.AstraeonSave.snapshot(state))),reload:load
};
for(const [id,action] of Object.entries(actions))$(id).onclick=()=>run(action);
$('skill-class').onchange=()=>run(()=>{state.cls=number('skill-class');player.recalculate()});
$('skill-id').onchange=renderNodes;
window.AstraeonProgressionHarness=Object.freeze({snapshot:()=>window.AstraeonSave.snapshot(state),getDerivedStats:()=>player.getDerivedStats()});
run(load);
})();
