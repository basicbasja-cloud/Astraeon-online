/* Patch 0.0.1 appearance is presentation data, independent of gear and stats. */
(function(scope){
'use strict';
const freeze=o=>{if(o&&typeof o==='object'){Object.values(o).forEach(freeze);Object.freeze(o)}return o};
const ANATOMY=freeze({frameWidth:160,frameHeight:160,rootAnchorX:80,rootAnchorY:132,referenceHeight:88,headWidth:24,headHeight:25});
const CLIPS=freeze(['Idle','Walk','Run','Sprint','BasicAttack','SkillAction','CastChannel','CastRelease','Guard','Dash','Blink','Hit','Death','Interact','Pickup','ItemUse','Sit','Respawn']);
const CATALOG=freeze({
 hair:[{id:'hair-native',name:'Class hairstyle',kind:'included'},{id:'silver-bob',name:'Silver tied bob',kind:'cosmetic',sku:'hair.silver-bob.001'}],
 outfit:[{id:'traveler',name:'Traveler attire',kind:'included'},{id:'astral-court',name:'Astral Court',kind:'cosmetic',sku:'costume.astral-court.001'}],
 bodies:['male','female']
});
function normalize(raw){
 if(!raw||typeof raw!=='object'||Array.isArray(raw))return null;
 return {version:1,bodyVariant:CATALOG.bodies.includes(raw.bodyVariant)?raw.bodyVariant:'male',hair:CATALOG.hair.some(v=>v.id===raw.hair)?raw.hair:'hair-native',outfit:CATALOG.outfit.some(v=>v.id===raw.outfit)?raw.outfit:'traveler'};
}
const defaults=()=>normalize({});
const classId=cls=>cls===0?'swordsman':cls===12?'mage':null;
function cosmetics(config,cls){const kind=classId(cls);if(!kind)throw Error('No 0.0.1 sprite class for '+cls);return {Hair:config.hair,Outfit:config.outfit==='traveler'?kind+'-traveler':config.outfit}}
async function load(config,cls,animationIds=['Idle']){
 config=normalize(config)||defaults();const kind=classId(cls);if(!kind)throw Error('Unsupported cosmetic class');
 const visual=await scope.AstraeonModularSprites.load(`./assets/characters/${kind}-${config.bodyVariant}-001/sprite.json`,{allowDev:true,bodyVariant:config.bodyVariant,cosmeticLoadout:cosmetics(config,cls),animationIds});
 for(const [key,value] of Object.entries(ANATOMY))if(key in visual.compiled.definition.canvas&&visual.compiled.definition.canvas[key]!==value)throw Error('Class anatomy differs: '+key);
 for(const id of CLIPS)if(!visual.compiled.definition.clips[id]||visual.compiled.definition.clips[id].tags?.includes('PENDING_PRODUCTION'))throw Error('Incomplete animation '+id);
 return visual;
}
let active=null,activeClass=null,activeConfig=null,selection=0,loadError=null,current='Idle',requested='Idle',clipTicket=0;
const pending=new Map();
function readyFor(visual,clip){return visual.compiled.sample(clip,'S',0,{appearance:visual.appearance}).layers.every(part=>visual.images[part.atlasId])}
async function select(raw,cls){
 const config=normalize(raw);const ticket=++selection;
 if(!config||!classId(cls)){active=null;activeClass=null;activeConfig=config;return null}
 loadError=null;
 const visual=await load(config,cls,['Idle','Walk','Run','Sprint']);
 if(ticket!==selection)return null;
 active=visual;activeClass=cls;activeConfig=config;current=requested='Idle';clipTicket++;pending.clear();return visual;
}
async function prepare(clip){
 const visual=active;if(!visual)return null;if(!CLIPS.includes(clip))throw Error('Unknown motion '+clip);
 if(!pending.has(clip))pending.set(clip,visual.ensure(clip).catch(error=>{if(active===visual){loadError=error.message;pending.delete(clip)}throw error}));
 await pending.get(clip);return active===visual?visual:null;
}
function actionClip(id,cls,def){
 if(id==='dodge')return cls===12?'Blink':'Dash';
 if(id==='potion')return 'ItemUse';if(id==='interact')return 'Interact';
 if(def?.effect==='guard')return 'Guard';
 if(id==='attack')return cls===12?'CastRelease':'BasicAttack';
 return def?.animation==='cast'?'CastRelease':def?.animation==='interact'?'ItemUse':'SkillAction';
}
function visualFor(cls,anim,transform,time){
 if(!active||activeClass!==cls)return undefined;
 const states={idle:'Idle',start:'Walk',walk:'Walk',run:'Run',sprint:'Sprint',turn:'Idle',stop:'Idle',attack:'BasicAttack',cast:'CastRelease',hit:'Hit',death:'Death',dodge:cls===12?'Blink':'Dash',interact:'Interact',pickup:'Pickup',item:'ItemUse',sit:'Sit',respawn:'Respawn',guard:'Guard',channel:'CastChannel'};
 const progress=Math.max(0,Math.min(1,(time-anim.started)/(anim.duration||1)));
 let desired=(anim.clipId&&time<anim.until?anim.clipId:null)||states[anim.state]||'Idle';
 if(desired==='CastRelease'&&Number.isFinite(anim.impactAt)&&progress<anim.impactAt)desired='CastChannel';
 const visual=active;
 if(desired!==requested){requested=desired;const ticket=++clipTicket;
  prepare(desired).then(()=>{if(active===visual&&ticket===clipTicket){current=desired;const retained=['Idle','Walk','Run','Sprint','Hit','Death','Respawn',current];if(['CastChannel','CastRelease'].includes(current))retained.push('CastChannel','CastRelease');visual.keepAnimations([...new Set(retained)].filter(id=>readyFor(visual,id)));for(const id of pending.keys())if(!readyFor(visual,id))pending.delete(id)}}).catch(()=>{});
 }
 if(readyFor(visual,desired))current=desired;
 const result={...visual,appearance:visual.appearance,animationId:current};
 const clip=visual.compiled.definition.clips[current],total=visual.compiled.duration(current);
 if(!['Walk','Run','Sprint','Idle'].includes(current)){
  let p=progress;
  if(current==='CastChannel'){result.elapsedMs=Math.max(0,(time-anim.started)*1000);return result}
  if(['BasicAttack','SkillAction','CastRelease'].includes(current)&&Number.isFinite(anim.impactAt)){
   const index={BasicAttack:7,SkillAction:6,CastRelease:3}[current],release=clip.durations.slice(0,index).reduce((a,b)=>a+b,0)/total,impact=Math.max(.01,Math.min(.99,anim.impactAt));
   p=p<impact?p/impact*release:release+(p-impact)/(1-impact)*(1-release);
  }
  result.elapsedMs=p*total;
 }
 return result;
}
const snapshot=()=>({appearance:activeConfig,classId:activeClass,current,requested,error:loadError,atlases:active?Object.keys(active.images):[],anatomy:ANATOMY});
const api={ANATOMY,CLIPS,CATALOG,normalize,defaults,classId,cosmetics,load,select,prepare,actionClip,visualFor,snapshot};
scope.AstraeonWardrobe=Object.freeze(api);if(typeof module!=='undefined')module.exports=api;
})(typeof window==='undefined'?globalThis:window);
