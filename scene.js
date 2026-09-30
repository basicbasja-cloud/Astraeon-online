/* Presentation-only city renderer. Receives projection/state; never mutates combat. */
(() => {
'use strict';
const content=window.AstraeonContent, atlas=new Image();atlas.src='./assets/town-atlas-v1.webp';
const hash=n=>{let x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x)};
const stoneColors=['#bfb297','#cec1a4','#a79e88','#d0c3a7'];
const paving=[];for(let i=0;i<540;i++){let a=hash(i)*Math.PI*2,r=Math.sqrt(hash(i+590))*4.15;paving.push({x:14.5+Math.cos(a)*r,y:15.3+Math.sin(a)*r,w:.14+hash(i+780)*.2,h:.11+hash(i+930)*.18,color:stoneColors[i%4]})}
function ground(ctx,iso,t){
 ctx.save();ctx.lineCap='round';ctx.lineJoin='round';
 for(const road of content.townRoads){const ps=road.points.map(([x,y])=>iso(x,y));for(const [extra,color] of [[14,'#4e5d3c55'],[7,'#93826477'],[0,'#c4b38bcc']]){ctx.strokeStyle=color;ctx.lineWidth=road.width*35+extra;ctx.beginPath();ps.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.stroke()}}
 const center=iso(14.5,15.3);ctx.fillStyle='#ada58dcc';ctx.beginPath();ctx.ellipse(center.x,center.y,192,124,.13,0,Math.PI*2);ctx.fill();
 for(const s of paving){const p=iso(s.x,s.y);ctx.fillStyle=s.color;ctx.globalAlpha=.72;ctx.beginPath();ctx.roundRect(p.x,p.y,s.w*48,s.h*31,2);ctx.fill()}ctx.globalAlpha=1;
 // Wear, scattered pebbles and grass at road shoulders stay fixed in world space.
 for(let i=0;i<95;i++){let x=11.8+hash(i+1190)*5.4,y=hash(i+1370)*29,p=iso(x,y);ctx.fillStyle=i%3?'#7e775355':'#e4d7b977';ctx.beginPath();ctx.ellipse(p.x,p.y,1.5+hash(i+1400)*2,1,0,0,Math.PI*2);ctx.fill()}
 ctx.restore();
}
function prop(ctx,o,iso,player,time){
 if(!atlas.complete||!atlas.naturalWidth)return false;
 const a=content.atlas[o.art],p=iso(o.x,o.y),left=p.x-o.w*a.anchor[0],top=p.y-o.h*a.anchor[1];
 if(left>ctx.canvas.width||left+o.w<0||top>ctx.canvas.height||top+o.h<0)return true;
 let alpha=1,hero=iso(player.x,player.y);
 if((o.tree||o.building)&&hero.x>left+o.w*.18&&hero.x<left+o.w*.83&&hero.y<p.y-10&&hero.y>top+o.h*.15)alpha=.36;
 ctx.save();ctx.globalAlpha=alpha;ctx.fillStyle='#17291f38';ctx.beginPath();ctx.ellipse(p.x+8,p.y+2,o.w*.32,o.w*.10,-.12,0,Math.PI*2);ctx.fill();
 const sway=o.tree?Math.sin(time*.7+o.x)*.8:0;
 ctx.drawImage(atlas,...a.rect,left+sway,top,o.w,o.h);
 if(o.art==='fountain'){ctx.globalAlpha=.3;ctx.strokeStyle='#b9f9ed';ctx.lineWidth=1;for(let k=0;k<2;k++){ctx.beginPath();ctx.ellipse(p.x,p.y-25,18+((time*9+k*15)%28),5+((time*2+k*4)%8),0,0,Math.PI*2);ctx.stroke()}}
 if(o.art==='stall'){ctx.globalAlpha=.55;ctx.fillStyle='#ffe1a0';let q=.65+.35*Math.sin(time*2+o.x);ctx.shadowColor='#ffd37b';ctx.shadowBlur=6*q;ctx.beginPath();ctx.arc(p.x+o.w*.33,p.y-o.h*.43,2.5,0,Math.PI*2);ctx.fill()}
 ctx.restore();return true;
}
function flowerBeds(ctx,iso){for(const [x,y] of [[11,12],[17.8,12],[11,19.5],[18,22]]){let p=iso(x,y);ctx.save();ctx.fillStyle='#395f3e';ctx.beginPath();ctx.ellipse(p.x,p.y,30,13,0,0,Math.PI*2);ctx.fill();for(let i=0;i<9;i++){let xx=p.x+(hash(i+x)*2-1)*25,yy=p.y+(hash(i+y)*2-1)*8;ctx.fillStyle=i%2?'#e9b0a1':'#f3dea0';ctx.beginPath();ctx.arc(xx,yy-3,2,0,Math.PI*2);ctx.fill()}ctx.restore()}}
window.AstraeonScene={ground,prop,flowerBeds,objects:content.townObjects,ready:()=>atlas.complete&&atlas.naturalWidth};
})();
