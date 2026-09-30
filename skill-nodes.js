/* Authored Base Skill + one compatible Node. No trees or arbitrary composition. */
(() => {
'use strict';
const catalog=Object.freeze({
 fire:{name:'Fire',family:'Elemental',color:'#ffac74',text:'Burn enemies; striking a burning target ignites it.',tags:['burn','ignite'],element:'fire'},
 ice:{name:'Ice',family:'Elemental',color:'#9cdefb',text:'Slow enemies and build frost; repeated contacts freeze ordinary foes.',tags:['frost','slow'],element:'ice'},
 lightning:{name:'Lightning',family:'Elemental',color:'#eadb96',text:'Chain to a nearby foe and briefly disrupt ordinary enemies.',tags:['chain','shock'],element:'lightning'},
 gravity:{name:'Gravity',family:'Cosmic',color:'#c5b0f1',text:'Pull enemies toward the skill center and suppress movement.',tags:['pull','slow'],element:'gravity'},
 qi:{name:'Qi',family:'Mystic',color:'#bce4a2',text:'Return Resolve on confirmed contact; the warrior keeps its melee rhythm.',tags:['restore'],element:'qi'},
 spirit:{name:'Spirit',family:'Mystic',color:'#b1e2d7',text:'The skill also restores health when you stand inside its area.',tags:['spirit'],element:'spirit'},
 void:{name:'Void',family:'Cosmic',color:'#cbb2fb',text:'Disrupt ordinary enemy windups and delay their next attack.',tags:['disrupt'],element:'void'},
 wind:{name:'Wind',family:'Elemental',color:'#d5edce',text:'Release the arrow, then retreat along its opposite direction.',tags:[],element:'wind',movement:'backstep'},
 plasma:{name:'Plasma',family:'Technology',color:'#80efed',text:'A projectile marks its enemy for a delayed heat burst.',tags:['heat'],element:'plasma'}
});
const compatibility=Object.freeze({
 'rising-edge':['qi','ice','gravity'], 'jade-tempest':['qi','fire','gravity'],
 'ember-bloom':['fire','gravity','spirit'], 'tempest':['fire','ice','lightning','gravity','spirit','void'],
 'piercing-arrow':['lightning','wind','plasma'], 'arrow-rain':['ice','lightning','spirit']
});
function apply(def,node){const allowed=compatibility[def.id]||[];if(typeof node!=='string'||!allowed.includes(node))return def;const n=catalog[node];return {...def,node,name:`${def.name} · ${n.name}`,element:n.element,color:n.color,tags:[...new Set([...def.tags,...n.tags])],movement:n.movement||def.movement}}
function normalize(raw){const result={};if(!raw||typeof raw!=='object'||Array.isArray(raw))return result;for(const [id,node] of Object.entries(raw))if(Object.hasOwn(compatibility,id)&&typeof node==='string'&&compatibility[id].includes(node))result[id]=node;return result}
function contact(def,enemy,time){const tags=def.tags||[],ordinary=!enemy.boss;
 return {ignite:tags.includes('ignite')&&enemy.burnUntil>time,burn:tags.includes('burn')?time+4:0,slow:tags.includes('slow')?time+3:0,frost:tags.includes('frost')?(enemy.frostUntil>time?enemy.frost||0:0)+.6:0,freeze:ordinary&&tags.includes('frost')&&(enemy.frostUntil>time?enemy.frost||0:0)+.6>=1.1,shock:ordinary&&tags.includes('shock'),disrupt:ordinary&&tags.includes('disrupt'),restore:tags.includes('restore')?4:0,pull:tags.includes('pull'),heat:tags.includes('heat')};
}
window.AstraeonSkillNodes={catalog,compatibility,apply,normalize,contact};
})();
