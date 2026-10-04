/* Presentation adapter. Gameplay actors select painted views from their world orientation. */
(() => {
'use strict';
const archetype=cls=>cls===3?'ranger':cls>=12&&cls<=16?'mage':'warrior';
function player(ctx,cls,anim,transform,iso,time,equipment){return window.AstraeonCharacters.humanoid(ctx,iso,transform,{archetype:archetype(cls),state:anim.state,time,progress:Math.max(0,Math.min(1,(time-anim.started)/(anim.duration||1))),equipment,impactAt:anim.impactAt})}
function npc(ctx,kind,transform,iso,time,appearance){const fallback=['housing','market','guild','shrine'].includes(kind)?'mage':['travel','inn'].includes(kind)?'ranger':'warrior';return window.AstraeonCharacters.humanoid(ctx,iso,transform,{archetype:['warrior','mage','ranger'].includes(appearance)?appearance:fallback,state:transform.state,time,scale:window.AstraeonView?.scale.npc||.92})}
function monster(ctx,entity,transform,iso,time){return window.AstraeonCharacters.monster(ctx,iso,transform,entity,time)}
window.AstraeonAnimation={archetype,player,npc,monster};
})();
