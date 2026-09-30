/* Data-driven action timing and hit geometry. No DOM, audio or rendering access. */
(() => {
'use strict';
const normalize=(x,y)=>{const n=Math.hypot(x,y)||1;return{x:x/n,y:y/n}};
const base={castTime:.17,activeTime:.06,recovery:.22,cooldown:.46,cost:0,range:2.7,shape:'cone',arc:.75,damage:1,tags:[],animation:'attack',element:'neutral'};
const definitions={
 warrior:{
  attack:{...base,id:'blade-combo',name:'Blade Combo',combo:true},
  skill1:{...base,id:'rising-edge',name:'Rising Edge',castTime:.25,recovery:.3,cooldown:2.6,cost:16,range:3.6,shape:'line',width:1,damage:1.8,tags:['knockback']},
  skill2:{...base,id:'iron-guard',name:'Iron Guard',shape:'self',effect:'guard',castTime:.06,cooldown:4,cost:10,animation:'cast'},
  skill3:{...base,id:'second-wind',name:'Second Wind',shape:'self',effect:'heal',castTime:.35,cooldown:8,cost:18,animation:'cast'},
  skill4:{...base,id:'jade-tempest',name:'Jade Tempest',shape:'circle',range:3.3,castTime:.38,recovery:.4,cooldown:7,cost:30,damage:2.1,animation:'cast',tags:['knockback']}
 },
 mage:{
  attack:{...base,id:'arcane-bolt',name:'Arcane Bolt',castTime:.23,range:7,shape:'projectile',speed:10,damage:.9,animation:'cast',element:'arcane'},
  skill1:{...base,id:'ember-bloom',name:'Ember Bloom',castTime:.52,recovery:.24,cooldown:3,cost:18,range:7,shape:'ground',radius:2,damage:1.8,animation:'cast',element:'fire',tags:['burn']},
  skill2:{...base,id:'frost-ward',name:'Frost Ward',shape:'self',effect:'guard',castTime:.18,cooldown:5,cost:12,animation:'cast',element:'ice'},
  skill3:{...base,id:'aether-mend',name:'Aether Mend',shape:'self',effect:'heal',castTime:.42,cooldown:8,cost:18,animation:'cast'},
  skill4:{...base,id:'tempest',name:'Tempest',shape:'ground',range:7,radius:3,castTime:.7,recovery:.3,cooldown:8,cost:30,damage:.65,animation:'cast',element:'arcane',tags:[],pulses:3,pulseInterval:.65}
 },
 ranger:{
  attack:{...base,id:'arrow',name:'Quick Shot',castTime:.16,recovery:.17,cooldown:.42,range:8,shape:'projectile',speed:15,damage:.85,animation:'attack'},
  skill1:{...base,id:'piercing-arrow',name:'Piercing Arrow',shape:'projectile',speed:18,range:9,castTime:.4,recovery:.25,cooldown:2.8,cost:16,damage:1.6,tags:['pierce']},
  skill2:{...base,id:'thorn-snare',name:'Thorn Snare',shape:'ground',range:6,radius:2,castTime:.2,cooldown:5,cost:12,damage:.55,animation:'cast',tags:['slow']},
  skill3:{...base,id:'field-aid',name:'Field Aid',shape:'self',effect:'heal',castTime:.32,cooldown:8,cost:18,animation:'interact'},
  skill4:{...base,id:'arrow-rain',name:'Arrow Rain',shape:'ground',range:8,radius:3,castTime:.5,recovery:.3,cooldown:7,cost:30,damage:.65,animation:'cast',tags:[],pulses:3,pulseInterval:.55}
 }
};
const colors={neutral:'#f2d399',arcane:'#9ce5eb',fire:'#ffac74',ice:'#9cdefb',qi:'#bce4a2',spirit:'#b1e2d7',plasma:'#80efed',void:'#cbb2fb',lightning:'#eadb96'};
function compile(archetype,id,combo=1,node=null){
 let d={...(definitions[archetype]||definitions.warrior)[id],tags:[...((definitions[archetype]||definitions.warrior)[id]?.tags||[])]};if(!d.id)return null;
 if(d.combo){d.damage=[1,1.12,1.35][combo-1]||1;d.castTime=[.15,.18,.24][combo-1]||.15;d.cooldown=[.44,.48,.6][combo-1]||.44;if(combo===3){d.shape='circle';d.range=2.9;d.tags.push('knockback')}}

 d=window.AstraeonSkillNodes?.apply(d,node)||d;
 d.color=d.color||colors[d.element]||colors.neutral;return d;
}
function contains(def,origin,dir,target,center=origin){const dx=target.x-origin.x,dy=target.y-origin.y,d=Math.hypot(dx,dy);if(def.shape==='circle'||def.shape==='ground')return Math.hypot(target.x-center.x,target.y-center.y)<(def.radius||def.range)+.35;if(d>def.range+.35)return false;if(def.shape==='line')return dx*dir.x+dy*dir.y>=-.2&&Math.abs(dx*dir.y-dy*dir.x)<(def.width||.85);return d<.65||(dx*dir.x+dy*dir.y)/Math.max(.01,d)>Math.cos(def.arc||.75)}
class Timeline {
 constructor(){this.active=null;this.cooldowns={};this.events=[];this.projectiles=[];this.nextProjectile=1;this.fields=[]}
 start(def,origin,aim,now){if(!def||this.active||now<(this.cooldowns[def.id]||0))return false;const direction=normalize(aim.x-origin.x,aim.y-origin.y),range=Math.hypot(aim.x-origin.x,aim.y-origin.y);const center={x:origin.x+direction.x*Math.min(def.range,range),y:origin.y+direction.y*Math.min(def.range,range)};this.active={def,origin:{...origin},direction,center,start:now,impact:now+def.castTime,end:now+def.castTime+def.activeTime+def.recovery,resolved:false};this.cooldowns[def.id]=now+Math.max(def.cooldown,def.castTime+def.activeTime+def.recovery);return true}
 cancel(){this.active=null}
 clear(){this.active=null;this.projectiles=[];this.fields=[]}
 tick(now,dt,entities,blocked=null){const out=[];let a=this.active;if(a&&!a.resolved&&now>=a.impact){a.resolved=true;if(a.def.shape==='projectile'){const p={id:this.nextProjectile++,def:a.def,x:a.origin.x+a.direction.x*.45,y:a.origin.y+a.direction.y*.45,z:a.def.animation==='cast'?53:44,dir:a.direction,travel:0,hits:new Set()};let muzzleBlocked=false;if(blocked)for(let i=1;i<=5;i++){const x=a.origin.x+a.direction.x*.09*i,y=a.origin.y+a.direction.y*.09*i;if(blocked(x,y)){p.x=x;p.y=y;muzzleBlocked=true;break}}if(muzzleBlocked)out.push({type:'blocked',projectile:p});else this.projectiles.push(p);out.push({type:'release',action:a})}else{out.push({type:'impact',action:a});if(a.def.pulses>1)this.fields.push({action:{...a,origin:{...a.origin},center:{...a.center}},remaining:a.def.pulses-1,next:now+a.def.pulseInterval})}}if(a&&now>=a.end)this.active=null;
 for(const p of this.projectiles){let step=Math.min(p.def.speed*dt,p.def.range-p.travel),wallHit=false;const ox=p.x,oy=p.y;if(blocked){const count=Math.ceil(step/.1);for(let i=1;i<=count;i++){if(blocked(ox+p.dir.x*step*i/count,oy+p.dir.y*step*i/count)){step*=Math.max(0,(i-1)/count);wallHit=true;break}}}p.x+=p.dir.x*step;p.y+=p.dir.y*step;p.travel+=step;const candidates=entities.filter(m=>m.hp>0&&!p.hits.has(m)).map(m=>{const along=Math.max(0,Math.min(step,(m.x-ox)*p.dir.x+(m.y-oy)*p.dir.y));return{m,along,distance:Math.hypot(m.x-ox-p.dir.x*along,m.y-oy-p.dir.y*along)}}).filter(v=>v.distance<.65).sort((a,b)=>a.along-b.along);for(const {m} of candidates){p.hits.add(m);out.push({type:'projectileHit',projectile:p,target:m});if(!p.def.tags.includes('pierce')){p.travel=p.def.range;break}}if(wallHit){p.travel=p.def.range;out.push({type:'blocked',projectile:p})}}this.projectiles=this.projectiles.filter(p=>p.travel<p.def.range);for(const field of this.fields){while(field.remaining>0&&now>=field.next){out.push({type:'pulse',action:field.action});field.remaining--;field.next+=field.action.def.pulseInterval}}this.fields=this.fields.filter(f=>f.remaining>0);return out}
 phase(now){const a=this.active;if(!a)return'idle';return now<a.impact?'anticipation':now<a.impact+a.def.activeTime?'active':'recovery'}
}
window.AstraeonCombat={definitions,compile,contains,Timeline,normalize};
})();
