/* Explicit development-only presentation selection; no gameplay/save inputs. */
(() => {
'use strict';
window.AstraeonSwordsmanDevelopmentInit=async bodyVariant=>{
 const api=window.AstraeonModularSprites;
 if(!/^[a-z][a-z0-9-]*$/.test(bodyVariant))throw Error('Invalid development body variant');
 const factoryReview=bodyVariant==='fantasy';
 let url=`./assets/characters/swordsman-${bodyVariant}-candidate/sprite.json`;
 if(factoryReview){
  const root='./authoring/characters/swordsman-production/fantasy-base-01/';
  const proof=await(await fetch(root+'factory/runtime-compatibility.json?spriteDev=1&t='+Date.now(),{cache:'no-store'})).json();
  url=root+'runtime/assets/characters/fantasy-golden-01/sprite-'+proof.nativeSHA256.slice(0,12)+'-'+proof.bankSHA256.slice(0,12)+'.json';
 }
 const visual=await api.load(url,{
  allowDev:true,bodyVariant:factoryReview?'male':bodyVariant,isolateDevelopmentCache:true,animationIds:['Idle']
 });
 if(visual.compiled.definition.classId!=='Swordsman')throw Error('Development appearance must use Swordsman class');
 const badge=document.createElement('aside');badge.id='swordsman-development-status';
 badge.style.cssText='position:fixed;right:8px;top:8px;z-index:1000;padding:6px 9px;border:1px solid #edc86d;background:#17242ded;color:#ffe5a1;font:12px system-ui;pointer-events:none;max-width:260px';
 document.body.append(badge);
 let current='Idle',wanted='Idle',recent='Idle',request=0,error=null;
 const retain=()=>{if(current!=='Idle')recent=current;visual.keepAnimations([...new Set(['Idle',recent,current])])};
 const status=message=>badge.textContent=`DEVELOPMENT · Swordsman ${bodyVariant} · NOT APPROVED · ${message}`;
 status('Idle');
 const playable=clip=>!!clip&&(factoryReview||clip.tags?.includes('INTERNAL_VISUAL_PASS'));
 function visualFor(state){
  const clip=api.STATE_CLIPS[state]||'Idle',definition=visual.compiled.definition.clips[clip];
  if(!playable(definition)){
   status(`${clip} pending visual production`);return undefined;
  }
  if(clip!==wanted){
   wanted=clip;error=null;const ticket=++request;status(`Loading ${clip}`);
   // Prepared actions and the retained Idle can switch on this very frame.
   const ready=visual.compiled.sample(clip,'S',0,{appearance:visual.appearance}).layers.every(layer=>visual.images[layer.atlasId]);
   if(ready){current=clip;status(clip)}
   visual.ensure(clip).then(()=>{
    if(ticket===request){current=clip;status(clip)}
    retain();
   }).catch(failure=>{
    if(ticket===request){error=failure.message;status(error)}
    retain();
   });
  }
  return {...visual,appearance:visual.appearance,animationId:current};
 }
 const snapshot=()=>({classId:'Swordsman',bodyVariant,currentClip:current,requestedClip:wanted,
  appearance:visual.appearance,atlases:Object.keys(visual.images),error,
  decodedAtlasBytes:Object.keys(visual.images).reduce((sum,id)=>{const a=visual.compiled.definition.atlases[id];return sum+a.width*a.height*4},0)});
 window.AstraeonSwordsmanDevelopment=Object.freeze({visualFor,snapshot,
  async prepare(clip){if(!playable(visual.compiled.definition.clips[clip]))throw Error('Clip has not passed visual production');await visual.ensure(clip);return snapshot()},
  async setCosmetics(cosmeticLoadout){await visual.setAppearance({}, {cosmeticLoadout});retain();return snapshot()}
 });
 if(factoryReview){
  // The explicit factory page previews its source even on a saved Mage/Ranger
  // profile. Supply only the render argument; never alter gameplay or saves.
  const renderPlayer=window.AstraeonAnimation.player;
  window.AstraeonAnimation.player=(...args)=>{args[7]=visualFor(args[2]?.state||'idle');return renderPlayer(...args)};
  const sets=await(await fetch('./authoring/characters/swordsman-production/fantasy-base-01/runtime/appearance-sets.json',{cache:'no-store'})).json();
  const panel=document.createElement('aside');panel.style.cssText='position:fixed;right:8px;top:58px;z-index:1001;padding:9px;background:#17242ded;color:#ffe5a1;font:12px system-ui;max-width:270px';
  panel.innerHTML='<label>Factory outfit <select id="factory-outfit"><option value="default">Original</option><option value="alternate">Crimson</option></select></label><br><label>Factory sword <select id="factory-weapon"><option value="default">Original</option><option value="alternate">Short blade</option><option value="none">None</option></select></label><br><label><input id="factory-headgear" type="checkbox">Circlet</label> <label><input id="factory-offhand" type="checkbox">Buckler</label> <label><input id="factory-cape" type="checkbox" checked>Cape</label><p>Technical playback · Art NOT APPROVED</p>';
  document.body.append(panel);
  panel.onchange=async()=>{try{const selected={...sets.outfit[panel.querySelector('#factory-outfit').value],...sets.weapon[panel.querySelector('#factory-weapon').value],...sets.headgear[panel.querySelector('#factory-headgear').checked?'default':'none'],...sets.offhand[panel.querySelector('#factory-offhand').checked?'default':'none'],...sets.cape[panel.querySelector('#factory-cape').checked?'default':'none']};await visual.setAppearance(selected);retain();status(current)}catch(failure){status(failure.message)}};
 }
};
})();
