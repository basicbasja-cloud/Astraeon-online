/* Persistent world discoveries. Claims are explicit and independent of presentation. */
(() => {
'use strict';
const available=(entry,state)=>!state.worldClaims?.[entry.id];
function claim(entry,state,{addItems}={}){
 if(!available(entry,state))return {ok:false,message:'สำรวจจุดนี้แล้ว'};
 if(!['chest','herb'].includes(entry.kind))return {ok:false,message:'จุดนี้ไม่มีทรัพยากร'};
 const rewards=entry.kind==='chest'?{potion:1,shard:1}:{herb:2};
 // Live gameplay supplies the canonical transaction. Unattached historical
 // fixtures retain the original plain-counter interface used by old checks.
 if(addItems){const result=addItems(rewards);if(!result.ok)return {ok:false,message:'รับไอเทมไม่สำเร็จ',code:result.code}}
 else{if(state.itemInventory)return {ok:false,code:'CANONICAL_ADAPTER_REQUIRED'};for(const [id,count] of Object.entries(rewards))state.inventory[id]+=count}
 state.worldClaims??={};state.worldClaims[entry.id]=true;
 if(entry.kind==='chest'){state.gold+=12;state.journal.unshift(`ค้นพบ: ${entry.name}`);return {ok:true,message:`${entry.name} · +12 gold, +1 Flask, +1 Shard`,color:'#f3d08b'}}
 state.profXP++;return {ok:true,message:'เก็บ Moonleaf · +2 Herb, +1 Profession XP',color:'#a8db91'};
}
window.AstraeonExploration={available,claim};
})();
