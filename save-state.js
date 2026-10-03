/* Browser-save compatibility boundary. Unknown progression fields are retained. */
(() => {
'use strict';
const number=(value,fallback,min=0,max=Number.MAX_SAFE_INTEGER)=>Number.isFinite(value)?Math.max(min,Math.min(max,value)):fallback;
const text=(value,fallback)=>typeof value==='string'?value:fallback;
function normalize(raw){
 if(!raw||typeof raw!=='object'||Array.isArray(raw)||typeof raw.name!=='string'||!raw.name.trim())return null;
 const state={...raw,saveVersion:3};
 for(const [key,fallback,min,max] of [['race',0,0,13],['cls',0,0,21],['path',-1,-1,1],['lv',1,1,999],['zone',0,0,4]])state[key]=Math.floor(number(raw[key],fallback,min,max));
 state.name=raw.name.slice(0,24);state.maxHp=number(raw.maxHp,100,1);state.hp=number(raw.hp,state.maxHp,0,state.maxHp);state.maxEnergy=number(raw.maxEnergy,60,1);state.energy=number(raw.energy,state.maxEnergy,0,state.maxEnergy);
 const townBounds=window.AstraeonContent?.nativeWorld?.spatial?.bounds;
 state.x=number(raw.x,14.5,1,state.zone===0?(townBounds?.maxX??44)-2:28);state.y=number(raw.y,18,1,state.zone===0?(townBounds?.maxY??40)-2:25);state.origin=text(raw.origin,'Guildborn');state.rank=text(raw.rank,'Copper');state.profession=text(raw.profession,'Untrained');
 for(const key of ['xp','gold','kills','clears','profXP','reputation','house','pvpWins','camp','skillMastery','weaponMastery','bossKills'])state[key]=number(raw[key],key==='gold'?50:0);
 const inventory=raw.inventory&&typeof raw.inventory==='object'?raw.inventory:{};state.inventory={...inventory};for(const key of ['herb','ore','shard','potion','ration','blade','charm','plate'])state.inventory[key]=Math.floor(number(inventory[key],0));
 const gear=raw.equipment&&typeof raw.equipment==='object'?raw.equipment:{};state.equipment={...gear,weapon:text(gear.weapon,'Traveler Blade'),armor:text(gear.armor,'Adventurer Garb'),relic:text(gear.relic,'None')};
 for(const key of ['mail','journal','party'])state[key]=Array.isArray(raw[key])?raw[key].filter(v=>typeof v==='string'):[];
 state.discovered=Array.isArray(raw.discovered)?raw.discovered.filter(v=>Number.isInteger(v)&&v>=0&&v<=4):[0];state.chapters=Array.isArray(raw.chapters)?raw.chapters.filter(v=>Number.isInteger(v)&&v>=0&&v<=3):[];
 state.techniques=Array.isArray(raw.techniques)?raw.techniques.filter(v=>v&&typeof v==='object'&&typeof v.name==='string').slice(-6):[];state.active=Math.floor(number(raw.active,0,0,Math.max(0,state.techniques.length-1)));
 state.quest=raw.quest&&Number.isInteger(raw.quest.id)&&raw.quest.id>=0&&raw.quest.id<5?{...raw.quest,progress:number(raw.quest.progress,0)}:null;state.guild=typeof raw.guild==='string'?raw.guild:null;
 state.skillNodes=window.AstraeonSkillNodes?.normalize(raw.skillNodes)||{};
 state.worldClaims=raw.worldClaims&&typeof raw.worldClaims==='object'&&!Array.isArray(raw.worldClaims)?{...raw.worldClaims}:{};
 return state;
}
window.AstraeonSave={normalize};
})();
