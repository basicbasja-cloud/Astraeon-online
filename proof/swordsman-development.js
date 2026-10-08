/* Explicit development-only presentation selection; no gameplay/save inputs. */
(() => {
'use strict';
window.AstraeonSwordsmanDevelopmentInit=async bodyVariant=>{
 const api=window.AstraeonModularSprites;
 if(!/^[a-z][a-z0-9-]*$/.test(bodyVariant))throw Error('Invalid development body variant');
 const visual=await api.load(`./assets/characters/swordsman-${bodyVariant}-candidate/sprite.json`,{
  allowDev:true,bodyVariant,isolateDevelopmentCache:true,animationIds:['Idle']
 });
 if(visual.compiled.definition.classId!=='Swordsman')throw Error('Development appearance must use Swordsman class');
 const badge=document.createElement('aside');badge.id='swordsman-development-status';
 badge.style.cssText='position:fixed;right:8px;top:8px;z-index:1000;padding:6px 9px;border:1px solid #edc86d;background:#17242ded;color:#ffe5a1;font:12px system-ui;pointer-events:none;max-width:260px';
 document.body.append(badge);
 let current='Idle',wanted='Idle',recent='Idle',request=0,error=null;
 const retain=()=>{if(current!=='Idle')recent=current;visual.keepAnimations([...new Set(['Idle',recent,current])])};
 const status=message=>badge.textContent=`DEVELOPMENT · Swordsman ${bodyVariant} · NOT APPROVED · ${message}`;
 status('Idle');
 function visualFor(state){
  const clip=api.STATE_CLIPS[state]||'Idle',definition=visual.compiled.definition.clips[clip];
  if(!definition?.tags?.includes('INTERNAL_VISUAL_PASS')){
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
  async prepare(clip){if(!visual.compiled.definition.clips[clip]?.tags?.includes('INTERNAL_VISUAL_PASS'))throw Error('Clip has not passed visual production');await visual.ensure(clip);return snapshot()},
  async setCosmetics(cosmeticLoadout){await visual.setAppearance({}, {cosmeticLoadout});retain();return snapshot()}
 });
};
})();
