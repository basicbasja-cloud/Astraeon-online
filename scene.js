/* Presentation-only city renderer. Receives projection/state; never mutates combat. */
(() => {
'use strict';
const content=window.AstraeonContent, atlas=new Image();atlas.src='./assets/town-atlas-v1.webp';
const secondary=new Image();secondary.src='./assets/secondary-atlas-v1.webp';
const hash=n=>{let x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x)};
const stoneColors=['#bfb297','#cec1a4','#a79e88','#d0c3a7'];
// Static authored paving is cached once, then translated with the camera.
let terrainCache=null;
function ground(ctx,iso,t){
 if(!terrainCache){terrainCache=document.createElement('canvas');terrainCache.width=2600;terrainCache.height=1700;const g=terrainCache.getContext('2d'),p=(x,y)=>({x:x*48-y*10+500,y:x*7+y*31+100});g.lineCap='round';g.lineJoin='round';
 for(const road of content.townRoads){const ps=road.points.map(([x,y])=>p(x,y));for(const [extra,color] of [[12,'#3c55394d'],[5,'#877962aa'],[0,'#b7a480f0']]){g.strokeStyle=color;g.lineWidth=road.width*35+extra;g.beginPath();ps.forEach((q,i)=>i?g.lineTo(q.x,q.y):g.moveTo(q.x,q.y));g.stroke()}}
 // Limestone courses across the square, with irregular edges and warm wear.
 for(let row=-12;row<13;row++)for(let col=-12;col<13;col++){const x=14.5+col*.34+(row%2)*.17,y=15.3+row*.33;if(Math.hypot((x-14.5)/1.12,y-15.3)>4.05)continue;const q=p(x,y),seed=(row+13)*29+col+13,w=14+hash(seed)*2,h=8+hash(seed+17)*2;g.fillStyle=stoneColors[seed%4];g.strokeStyle='#8e826755';g.lineWidth=.7;g.beginPath();g.moveTo(q.x-w/2+1,q.y-h/2);g.lineTo(q.x+w/2,q.y-h/2+1);g.lineTo(q.x+w/2-1,q.y+h/2);g.lineTo(q.x-w/2,q.y+h/2-1);g.closePath();g.fill();g.stroke();g.fillStyle='#eee5cb30';g.fillRect(q.x-w/2+2,q.y-h/2+1,w-4,1)}
 for(let i=0;i<2600;i++){const x=11.9+hash(i+1190)*5.2,y=hash(i+1370)*38-5,q=p(x,y);g.fillStyle=i%3?'#76654718':'#eee0b32a';g.fillRect(q.x,q.y,.6+hash(i+1400)*3,.7)}
 }
 const origin=iso(0,0);ctx.drawImage(terrainCache,origin.x-500,origin.y-100);
}
function prop(ctx,o,iso,player,time){
 const sheet=o.pack==='secondary'?secondary:atlas;if(!sheet.complete||!sheet.naturalWidth)return false;
 const a=(o.pack==='secondary'?content.secondaryAtlas:content.atlas)[o.art],p=iso(o.x,o.y),left=p.x-o.w*a.anchor[0],top=p.y-o.h*a.anchor[1];
 if(left>ctx.canvas.clientWidth||left+o.w<0||top>ctx.canvas.clientHeight||top+o.h<0)return true;
 let alpha=1,hero=iso(player.x,player.y);
 if((o.tree||o.building)&&hero.x>left+o.w*.18&&hero.x<left+o.w*.83&&hero.y<p.y-10&&hero.y>top+o.h*.15)alpha=.36;
 ctx.save();ctx.globalAlpha=alpha;ctx.fillStyle='#17291f38';ctx.beginPath();ctx.ellipse(p.x+8,p.y+2,o.w*.32,o.w*.10,-.12,0,Math.PI*2);ctx.fill();
 const sway=o.tree?Math.sin(time*.7+o.x)*.8:0;
 ctx.drawImage(sheet,...a.rect,left+sway,top,o.w,o.h);
 if(o.art==='fountain'){ctx.globalAlpha=.3;ctx.strokeStyle='#b9f9ed';ctx.lineWidth=1;for(let k=0;k<2;k++){ctx.beginPath();ctx.ellipse(p.x,p.y-25,18+((time*9+k*15)%28),5+((time*2+k*4)%8),0,0,Math.PI*2);ctx.stroke()}}
 if(o.art==='stall'){ctx.globalAlpha=.55;ctx.fillStyle='#ffe1a0';let q=.65+.35*Math.sin(time*2+o.x);ctx.shadowColor='#ffd37b';ctx.shadowBlur=6*q;ctx.beginPath();ctx.arc(p.x+o.w*.33,p.y-o.h*.43,2.5,0,Math.PI*2);ctx.fill()}
 ctx.restore();return true;
}
function flowerBeds(ctx,iso){for(const [x,y] of [[11,12],[17.8,12],[11,19.5],[18,22]]){let p=iso(x,y);ctx.save();ctx.fillStyle='#395f3e';ctx.beginPath();ctx.ellipse(p.x,p.y,30,13,0,0,Math.PI*2);ctx.fill();for(let i=0;i<9;i++){let xx=p.x+(hash(i+x)*2-1)*25,yy=p.y+(hash(i+y)*2-1)*8;ctx.fillStyle=i%2?'#e9b0a1':'#f3dea0';ctx.beginPath();ctx.arc(xx,yy-3,2,0,Math.PI*2);ctx.fill()}ctx.restore()}}
window.AstraeonScene={ground,prop,flowerBeds,objects:content.townObjects,ready:()=>atlas.complete&&atlas.naturalWidth};
})();
