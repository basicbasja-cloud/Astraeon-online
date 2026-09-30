/* Authored Shenzhou outdoors and painted ruin presentation. No progression ownership. */
(() => {
'use strict';
const sheets={},patterns=new WeakMap();
const files={outdoor:'outdoor-atlas-v1',ruin:'ruin-atlas-v1',meadow:'meadow-ground-v1',forest:'forest-ground-v1',stone:'ruin-ground-v1',path:'path-ground-v1'};
const pending={};
function load(key){if(sheets[key])return Promise.resolve();return pending[key]??=new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{sheets[key]=im;resolve()};im.onerror=()=>{delete pending[key];reject(new Error(`Cannot load environment: ${files[key]}`))};im.src=`./assets/${files[key]}.webp`})}
const ready=Promise.resolve();
const ensure=(zone,dungeon=false)=>Promise.all((zone===1?['outdoor','ruin','forest','path']:zone===2?['outdoor','ruin','meadow','path']:[]).concat(dungeon?['ruin','stone']:[]).map(load));

const hash=n=>{const x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x)};
const prop=(pack,art,x,y,w,extra={})=>{const entry=window.AstraeonEnvironmentMetadata[pack][art];return {pack,art,x,y,w,h:w*entry.rect[3]/entry.rect[2],...extra}};
const meadow={
 roads:[{points:[[-8,14],[4,14],[9,15],[14,17],[20,15.5],[27,14],[38,14]],width:2.5},{points:[[14.5,-7],[14.5,5],[13.5,10],[14,17],[16,24],[17,35]],width:1.6},{points:[[9,15],[9.5,19],[11,22]],width:1.25}],
 objects:[prop('outdoor','farmhouse',5.5,7,228,{building:true}),prop('outdoor','mill',24,8,256,{building:true}),prop('outdoor','farmhouse',6,24,224,{building:true}),prop('outdoor','camp',24.5,24,202,{building:true}),prop('outdoor','camp',10.5,22,163),prop('outdoor','wall',18,6.3,122),prop('outdoor','wall',21,7,122),prop('outdoor','log',23,18,129),prop('ruin','rubble',26,11,98),prop('ruin','column',26,12.8,73),prop('ruin','chest',10.6,23.1,59)],
 interactions:[{id:'field-camp',kind:'camp',name:'Caravan camp',x:10.5,y:22},{id:'caravan-cache',kind:'chest',name:'Caravan supply chest',x:10.6,y:23.1},{id:'meadow-herbs',kind:'herb',name:'Wild herbs',x:18.5,y:19}],
 title:'Goldenfield Crossroads'
};
const forest={
 roads:[{points:[[14.5,35],[14.5,24],[16.5,19],[14.5,14],[15.4,10],[14.5,7.5]],width:1.9},{points:[[-7,14],[5,14],[11,15.5],[14.5,14],[21,13.5],[27.5,14],[38,14]],width:1.3},{points:[[14.5,11],[18.8,10],[21,8]],width:1}],
 objects:[prop('outdoor','entrance',14.5,7.5,214,{building:true}),prop('outdoor','camp',6,7,179,{building:true}),prop('ruin','altar',24,9,121,{building:true}),prop('ruin','rubble',24,23.5,187,{building:true}),prop('outdoor','log',7,19,148),prop('outdoor','log',22,17.5,136),prop('ruin','column',12,8.4,83),prop('ruin','column',17.2,8.9,83),prop('ruin','brazier',12.5,9.3,40),prop('ruin','brazier',16.7,9.3,40),prop('ruin','seal',14.5,9.3,123),prop('ruin','chest',20.5,9.3,57)],
 interactions:[{id:'moonveil-entry',kind:'dungeon',name:'Moonveil shrine',x:14.5,y:9.5},{id:'forest-cache',kind:'chest',name:'Forgotten pilgrim chest',x:20.5,y:9.3},{id:'moonbamboo-herbs',kind:'herb',name:'Moonleaf herbs',x:18.8,y:18.5}],
 title:'Moonbamboo Trail'
};
// Border groves continue beyond playable terrain to keep every viewport inhabited.
for(const [zone,points] of [[meadow,[[2,2],[10,4],[17,3],[27,2],[2,8],[7,10],[22,11],[27,8],[2,24],[9,23],[18,23],[27,24],[5,16],[25,17],[-3,11],[33,11],[-3,20],[33,20],[8,-3],[21,-3],[8,31],[22,31]]],[forest,[[2,2],[10,4],[18,4],[27,2],[2,8],[6,10],[23,12],[28,8],[4,17],[8,21],[19,17],[27,24],[3,25],[11,24],[22,25],[-3,11],[33,11],[-3,20],[33,20],[7,-3],[22,-3],[7,31],[22,31]]]]){
 points.forEach(([x,y],i)=>zone.objects.push(prop('outdoor',zone===forest?'grove':'willow',x,y,zone===forest?154+(i%3)*17:162+(i%3)*18,{tree:true})));
 for(let i=0;i<10;i++){const x=3+hash(i+91)*24,y=3+hash(i+138)*21;if(zone.roads.some(road=>road.points.some(([rx,ry])=>Math.hypot(rx-x,ry-y)<3)))continue;zone.objects.push(prop('outdoor',i%3?'log':'wall',x,y,58+(i%3)*12));}
}
const zones={1:forest,2:meadow};
let roadCache=null,cachedZone=null;
function pathStroke(g,points,project,width,color){g.strokeStyle=color;g.lineWidth=width;g.beginPath();points.forEach(([x,y],i)=>{const p=project(x,y);i?g.lineTo(p.x,p.y):g.moveTo(p.x,p.y)});g.stroke()}
function terrain(ctx,iso,key){const image=sheets[key];if(!image)return;let cache=patterns.get(ctx);if(!cache){cache={};patterns.set(ctx,cache)}const pattern=cache[key]??=ctx.createPattern(image,'repeat'),origin=iso(0,0),scale=key==='stone'?.7:.72;pattern.setTransform(new DOMMatrix().translate(origin.x,origin.y).scale(scale));ctx.save();if(key==='stone'){ctx.fillStyle='#818577';ctx.fillRect(0,0,ctx.canvas.clientWidth,ctx.canvas.clientHeight);ctx.globalAlpha=.55}ctx.fillStyle=pattern;ctx.fillRect(0,0,ctx.canvas.clientWidth,ctx.canvas.clientHeight);ctx.restore()}
function ground(ctx,iso,zone){const data=zones[zone];if(!data)return false;terrain(ctx,iso,zone===1?'forest':'meadow');
 if(cachedZone!==zone){cachedZone=zone;roadCache=document.createElement('canvas');roadCache.width=2200;roadCache.height=1500;const g=roadCache.getContext('2d'),project=(x,y)=>({x:x*48-y*10+430,y:x*7+y*31+160});g.lineCap='round';g.lineJoin='round';
  for(const road of data.roads){for(const [add,color] of [[26,zone===1?'#273e3024':'#5a693c20'],[10,'#867a5830'],[0,zone===1?'#91866b66':'#bb9f7770']])pathStroke(g,road.points,project,road.width*29+add,color)}
  const mask=document.createElement('canvas');mask.width=roadCache.width;mask.height=roadCache.height;const m=mask.getContext('2d');m.lineCap='round';m.lineJoin='round';for(const road of data.roads)pathStroke(m,road.points,project,road.width*28,'#fff');
  m.globalCompositeOperation='source-in';m.fillStyle=m.createPattern(sheets.path,'repeat');m.fillRect(0,0,mask.width,mask.height);g.globalAlpha=zone===1?.8:.92;g.drawImage(mask,0,0);g.globalAlpha=1;

  for(let i=0;i<2200;i++){const x=hash(i+170)*40-5,y=hash(i+122)*37-5,p=project(x,y);g.fillStyle=i%3?'#eddbb326':'#62554038';g.fillRect(p.x,p.y,1+hash(i)*3,.7+hash(i+12));}
  // Local wear, leaf litter and path-side clearings break up the repeating base material.
  for(const o of data.objects.filter(o=>o.building||o.art==='camp')){const p=project(o.x,o.y),r=o.w*.58,glow=g.createRadialGradient(p.x,p.y,5,p.x,p.y,r);glow.addColorStop(0,zone===1?'#837b6366':'#bd9f7066');glow.addColorStop(1,'#ae956000');g.fillStyle=glow;g.fillRect(p.x-r,p.y-r,r*2,r*2)}
 }
 const p=iso(0,0);ctx.drawImage(roadCache,p.x-430,p.y-160);return true;
}
function drawProp(ctx,o,iso,player,time){const sheet=sheets[o.pack],entry=window.AstraeonEnvironmentMetadata[o.pack]?.[o.art];if(!sheet||!entry)return false;const p=iso(o.x,o.y),left=p.x-o.w*entry.anchor[0],top=p.y-o.h*entry.anchor[1],width=ctx.canvas.clientWidth,height=ctx.canvas.clientHeight;
 if(left>width+20||left+o.w<-20||top>height+20||top+o.h<-20)return true;
 const hero=iso(player.x,player.y),obstructs=(o.tree||o.building)&&hero.x>left+o.w*.15&&hero.x<left+o.w*.86&&hero.y<p.y-8&&hero.y>top+o.h*.16;
 ctx.save();ctx.globalAlpha=obstructs?.38:1;ctx.fillStyle='#152b252e';ctx.beginPath();ctx.ellipse(p.x+6,p.y+2,o.w*.28,o.w*.08,-.12,0,Math.PI*2);ctx.fill();
 const sway=o.tree?Math.sin(time*.6+o.x)*.8:0;ctx.drawImage(sheet,...entry.rect,left+sway,top,o.w,o.h);
 if(o.art==='brazier'||o.art==='camp'){const x=p.x+(o.art==='camp'?-o.w*.22:0),y=p.y-o.h*(o.art==='camp'?.2:.63),r=o.art==='camp'?16:25;const glow=ctx.createRadialGradient(x,y,0,x,y,r);glow.addColorStop(0,`rgba(255,191,89,${.12+.05*Math.sin(time*4+o.x)})`);glow.addColorStop(1,'rgba(255,190,90,0)');ctx.fillStyle=glow;ctx.fillRect(x-r,y-r,r*2,r*2)}
 ctx.restore();return true;
}
function ruinWalls(walls){const out=[];for(const wall of walls){const horizontal=wall.w>wall.h,length=horizontal?wall.w:wall.h,count=Math.max(1,Math.ceil(length/2.7)),step=length/count;for(let i=0;i<count;i++){const x=wall.x+(horizontal?step*(i+.5):wall.w/2),y=wall.y+(horizontal?wall.h/2:step*(i+.5));out.push(prop('ruin',horizontal?'wallX':'wallY',x,y,horizontal?step*48+25:72,{building:true,wall:true}))}}return out}
window.AstraeonEnvironment={ready,ensure,zones,prop,ground,terrain,drawProp,ruinWalls,sheets};
})();
