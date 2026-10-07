/* Pure death orchestration adapter: progression and quest credit are not drops. */
(() => {
'use strict';
const freeze=window.AstraeonItemDefinitions.freeze,int=v=>Number.isSafeInteger(v)&&v>=0;
const gold=v=>Number.isFinite(v)&&v>=0&&v<=Number.MAX_SAFE_INTEGER;
const profiles=freeze({'prototype-kill':{baseExp:7,perZone:3,killCredit:true},'prototype-boss':{baseExp:25,perZone:3,killCredit:true},'prototype-arena':{baseExp:7,perZone:3,killCredit:true,arenaWin:true},proof:{baseExp:0,perZone:0,killCredit:false}});
function plan(state,resolution,profileId,contracts=[],ratio=window.AstraeonProgressionConfig.progression.activityJobExpRatio){
 const fail=code=>freeze({ok:false,code});const profile=Object.hasOwn(profiles,profileId)?profiles[profileId]:null;
 if(!profile||!resolution?.ok||!Array.isArray(resolution.currencyRewards)||!Array.isArray(resolution.itemRewards))return fail('INVALID_REWARD_PACKAGE');
 if(!gold(state.gold)||!int(state.kills)||!int(state.clears)||!int(state.reputation)||!int(state.pvpWins)||!Array.isArray(state.journal))return fail('INVALID_REWARD_STATE');
 if(!int(resolution.zone)||!Number.isFinite(ratio)||ratio<0)return fail('INVALID_REWARD_CONTEXT');
 let currencyGranted=0;for(const c of resolution.currencyRewards){if(!c||c.currencyId!=='gold'||!int(c.amount))return fail('INVALID_CURRENCY');currencyGranted+=c.amount}
 let baseExp=profile.baseExp+profile.perZone*resolution.zone;
 const fields={kills:state.kills+(profile.killCredit?1:0),clears:state.clears,reputation:state.reputation,pvpWins:state.pvpWins+(profile.arenaWin?1:0)},itemRewards=[...resolution.itemRewards];
 let quest=state.quest?{...state.quest}:null,questCredit=0,completedQuest=null,journal=[...state.journal],questExp=0;
 // Credit only the quest active at death. Later quest changes do not erase loot.
 // Concurrent pending deaths may advance the same quest's current progress.
 if(profile.killCredit&&quest&&resolution.quest?.id===quest.id){
  const q=contracts[quest.id];if(!q||!int(quest.progress)||!int(q.target)||!int(q.reward)||!int(q.xp))return fail('INVALID_QUEST_REWARD');
  if(q.zone===resolution.zone){quest.progress++;questCredit=1;if(quest.progress>=q.target){completedQuest={...q};currencyGranted+=q.reward;questExp=q.xp;itemRewards.push({entryId:'quest-completion',itemId:'shard',quantity:2});fields.clears++;fields.reputation+=5;journal.unshift(`สำเร็จ: ${q.title}`);quest=null}}
 }
 const jobExp=Math.floor(baseExp*ratio)+Math.floor(questExp*ratio);baseExp+=questExp;
 if(!Object.values(fields).every(int)||!int(baseExp)||!int(jobExp)||!int(currencyGranted))return fail('REWARD_OVERFLOW');
 fields.gold=state.gold+currencyGranted;if(!gold(fields.gold))return fail('REWARD_OVERFLOW');
 fields.quest=quest;fields.journal=journal;fields.rank=fields.clears>=5?'Silver':fields.clears>=2?'Iron':state.rank;
 return freeze({ok:true,fields,itemRewards,currencyGranted,baseExp,jobExp,questCredit,completedQuest,killCredit:profile.killCredit?1:0});
}
window.AstraeonMonsterRewards=freeze({profiles,plan});
})();
