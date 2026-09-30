/* Readable enemy attacks in world coordinates. Telegraph and damage share one shape. */
(() => {
'use strict';
const normal=[
 {name:'Pounce',shape:'cone',range:1.5,arc:.85,duration:.55},
 {name:'Tusk rush',shape:'line',range:4.8,width:.8,duration:1.05,charge:true},
 {name:'Shell slam',shape:'circle',radius:1.35,duration:.8},
 {name:'Aimed arrow',shape:'line',range:7,width:.36,duration:.9,projectile:true},
 {name:'Spore patch',shape:'ground',radius:1.45,duration:1.1,field:true},
 {name:'Spirit bolt',shape:'line',range:6,width:.48,duration:.95,projectile:true},
 {name:'Stone sweep',shape:'cone',range:2.4,arc:1.05,duration:1.15},
 {name:'Veil bite',shape:'cone',range:1.65,arc:.8,duration:.65}
];
const boss=[
 {name:'Crescent sweep',shape:'cone',range:3.4,arc:1.1,duration:.9},
 {name:'Antler charge',shape:'line',range:6.3,width:1.0,duration:1.15,charge:true},
 {name:'Moonseal',shape:'ground',radius:2.65,duration:1.35,field:true}
];
function plan(entity,target,time){
 const definition=entity.boss?boss[entity.pattern%3]:normal[entity.species||0],dx=target.x-entity.x,dy=target.y-entity.y,n=Math.hypot(dx,dy)||1,dir={x:dx/n,y:dy/n},duration=definition.duration*(entity.boss&&entity.phase?.82:1);
 return {...definition,origin:{x:entity.x,y:entity.y},dir,x:definition.shape==='ground'?target.x:entity.x,y:definition.shape==='ground'?target.y:entity.y,end:time+duration,duration,range:definition.charge?Math.min(definition.range,n+1.2):definition.range,damage:entity.boss?12+(entity.phase?3:0):entity.elite?9:5,color:entity.boss?'#ee8bb3':definition.field?'#b5cc82':'#eba574'};
}
function distanceToSegment(point,a,b){const dx=b.x-a.x,dy=b.y-a.y,n=dx*dx+dy*dy,t=n?Math.max(0,Math.min(1,((point.x-a.x)*dx+(point.y-a.y)*dy)/n)):0;return Math.hypot(point.x-a.x-dx*t,point.y-a.y-dy*t)}
function contains(a,point){if(a.shape==='ground'||a.shape==='circle')return Math.hypot(point.x-a.x,point.y-a.y)<a.radius+.25;const dx=point.x-a.origin.x,dy=point.y-a.origin.y,along=dx*a.dir.x+dy*a.dir.y;if(a.shape==='line')return along>=-.2&&along<=a.range+.25&&Math.abs(dx*a.dir.y-dy*a.dir.x)<a.width+.25;const length=Math.hypot(dx,dy);return length<a.range+.25&&(length<.45||along/length>Math.cos(a.arc))}
function outline(a){const p=a.origin||{x:a.x,y:a.y};if(a.shape==='line'){const side={x:-a.dir.y*a.width,y:a.dir.x*a.width},end={x:p.x+a.dir.x*a.range,y:p.y+a.dir.y*a.range};return [{x:p.x+side.x,y:p.y+side.y},{x:end.x+side.x,y:end.y+side.y},{x:end.x-side.x,y:end.y-side.y},{x:p.x-side.x,y:p.y-side.y}]}
 if(a.shape==='cone'){const heading=Math.atan2(a.dir.y,a.dir.x),points=[p];for(let i=0;i<=24;i++){const angle=heading-a.arc+i/24*a.arc*2;points.push({x:p.x+Math.cos(angle)*a.range,y:p.y+Math.sin(angle)*a.range})}return points}
 return Array.from({length:48},(_,i)=>{const angle=i*Math.PI/24;return {x:a.x+Math.cos(angle)*a.radius,y:a.y+Math.sin(angle)*a.radius}});
}
window.AstraeonEnemyCombat={normal,boss,plan,contains,outline,distanceToSegment};
})();
