/* Browser-save compatibility boundary. Unknown progression fields are retained. */
(() => {
'use strict';
const number=(value,fallback,min=0,max=Number.MAX_SAFE_INTEGER)=>Number.isFinite(value)?Math.max(min,Math.min(max,value)):fallback;
const text=(value,fallback)=>typeof value==='string'?value:fallback;
const version=4;
 class UnsupportedSaveError extends Error{
  constructor(saveVersion){super(`Save version ${saveVersion} requires a newer game (supported: ${version}).`);this.name='UnsupportedSaveError';this.code='UNSUPPORTED_SAVE_VERSION';this.saveVersion=saveVersion;this.supportedVersion=version}
 }
function backbone(raw,state){
 const canonical=window.AstraeonCharacter.normalize({...raw,baseLevel:number(raw.baseLevel,state.lv,1),baseExp:number(raw.baseExp,state.xp)});
 const modifiers=window.AstraeonPlayer.legacyModifiers(state);
 modifiers.passiveModifiers.push(...window.AstraeonSkillTree.passiveModifiers(canonical.learnedSkills,window.AstraeonSkillDefinitions.classIdFor(state)));
 // No load-time EXP grants or retrospective point awards. Absent legacy pools start at zero.
 if(raw.saveVersion!==version&&!raw.legacyBackbone){
  state.legacyBackbone={};for(const key of ['saveVersion','lv','xp','hp','maxHp','energy','maxEnergy'])if(Object.hasOwn(raw,key))state.legacyBackbone[key]=raw[key];
 }
 if(!raw.resourceBase||!Number.isFinite(raw.resourceBase.maxHP)||!Number.isFinite(raw.resourceBase.maxSP)){
  const baseline=window.AstraeonStats.calculate({baseLevel:canonical.baseLevel,primaryStats:canonical,...modifiers});
  canonical.resourceBase={maxHP:number(raw.maxHP,state.maxHp,1)-baseline.maxHP,maxSP:number(raw.maxSP,state.maxEnergy,1)-baseline.maxSP};
 }
 const derived=window.AstraeonStats.calculate({baseLevel:canonical.baseLevel,primaryStats:canonical,characterBase:canonical.resourceBase,...modifiers});
 Object.assign(state,canonical,{maxHP:derived.maxHP,maxSP:derived.maxSP,currentHP:number(raw.currentHP,state.hp,0,derived.maxHP),currentSP:number(raw.currentSP,state.energy,0,derived.maxSP)});
 state.lv=state.baseLevel;state.xp=state.baseExp;state.hp=state.currentHP;state.maxHp=state.maxHP;state.energy=state.currentSP;state.maxEnergy=state.maxSP;
 return state;
}
function normalize(raw){
 if(raw&&typeof raw==='object'&&raw.saveVersion>version)throw new UnsupportedSaveError(raw.saveVersion);
 if(!raw||typeof raw!=='object'||Array.isArray(raw)||typeof raw.name!=='string'||!raw.name.trim())return null;
 const state={...raw,saveVersion:version};
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
 state.actionLoadout=window.AstraeonSkillRuntime.normalizeLoadout(raw.actionLoadout);
 // Old four-button saves keep their authored actions without granting learned ranks.
 // New characters explicitly provide an empty eight-slot loadout and opt out.
 state.legacySkillControls=typeof raw.legacySkillControls==='boolean'?raw.legacySkillControls:!Object.hasOwn(raw,'actionLoadout');
 state.worldClaims=raw.worldClaims&&typeof raw.worldClaims==='object'&&!Array.isArray(raw.worldClaims)?{...raw.worldClaims}:{};
 return backbone(raw,state);
}
// Serialize getters as ordinary canonical data; runtime effect groups belong to the controller.
function snapshot(state){return normalize(JSON.parse(JSON.stringify(state)))}
window.AstraeonSave=Object.freeze({version,normalize,snapshot,UnsupportedSaveError});
})();
