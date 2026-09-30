/* Persistent world discoveries. Claims are explicit and independent of presentation. */
(() => {
'use strict';
const available=(entry,state)=>!state.worldClaims?.[entry.id];
function claim(entry,state){
 if(!available(entry,state))return {ok:false,message:'สำรวจจุดนี้แล้ว'};
 if(!['chest','herb'].includes(entry.kind))return {ok:false,message:'จุดนี้ไม่มีทรัพยากร'};
 state.worldClaims??={};state.worldClaims[entry.id]=true;
 if(entry.kind==='chest'){state.gold+=12;state.inventory.potion++;state.inventory.shard++;state.journal.unshift(`ค้นพบ: ${entry.name}`);return {ok:true,message:`${entry.name} · +12 gold, +1 Flask, +1 Shard`,color:'#f3d08b'}}
 state.inventory.herb+=2;state.profXP++;return {ok:true,message:'เก็บ Moonleaf · +2 Herb, +1 Profession XP',color:'#a8db91'};
}
window.AstraeonExploration={available,claim};
})();
