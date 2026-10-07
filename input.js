/* Device bindings produce actions and axes; gameplay uses this action vocabulary. */
(() => {
'use strict';
class ActionInput {
 constructor(){this.keys=new Set();this.bindings={f:'attack',' ':'dodge','1':'skill1','2':'skill2','3':'skill3','4':'skill4',q:'potion',e:'interact',tab:'target',j:'menu:journal',c:'menu:character',k:'menu:skills',i:'menu:inventory',m:'menu:map'}}
 key(value,pressed){const k=value.toLowerCase();pressed?this.keys.add(k):this.keys.delete(k);return pressed?this.bindings[k]:null}
 move(touch={x:0,y:0}){const has=(a,b)=>this.keys.has(a)||this.keys.has(b);return{x:touch.x+Number(has('d','arrowright'))-Number(has('a','arrowleft')),y:touch.y+Number(has('s','arrowdown'))-Number(has('w','arrowup'))}}
 get sprint(){return this.keys.has('shift')}
 get walk(){return this.keys.has('alt')}
 clear(){this.keys.clear()}
}
const actionSlotIntent=slot=>Number.isSafeInteger(slot)&&slot>=0&&slot<8?`actionSlot${slot+1}`:null;
const slotFromIntent=intent=>{const match=typeof intent==='string'?/^(?:actionSlot([1-8])|skill([1-4]))$/.exec(intent):null;return match?Number(match[1]||match[2])-1:null};
// The four shipped key aliases remain. Slots 5–8 have system intents, no new UX keys.
window.AstraeonInput=Object.freeze({ActionInput,actionSlotIntent,slotFromIntent,separateActions:Object.freeze({basicAttack:'attack',potion:'potion',dodge:'dodge',interact:'interact'})});
})();
