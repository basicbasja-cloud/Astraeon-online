/* Presentation-only city renderer. Receives projection/state; never mutates combat. */
(() => {
'use strict';
const content=window.AstraeonContent, atlas=new Image();atlas.src='./assets/town-atlas-v1.webp';
const paving=new Image();paving.src='./assets/town-limestone-v1.webp';
const secondary=new Image();secondary.src='./assets/secondary-atlas-v1.webp';
const whenReady=Promise.all([atlas,secondary,paving].map(image=>image.complete&&image.naturalWidth?Promise.resolve():new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=()=>reject(new Error('Cannot load town artwork'))})));
const hash=n=>{let x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x)};
// World-aligned material courses share the same projection as architecture and actors.
let terrainCache=null;
function polygon(g,points,p){g.beginPath();points.forEach(([x,y],i)=>{const q=p(x,y);i?g.lineTo(q.x,q.y):g.moveTo(q.x,q.y)});g.closePath()}
function corridor(g,road,p){
 for(let i=1;i<road.points.length;i++){
  const a=road.points[i-1],b=road.points[i],dx=b[0]-a[0],dy=b[1]-a[1],n=Math.hypot(dx,dy),nx=-dy/n*road.width/2,ny=dx/n*road.width/2;
  polygon(g,[[a[0]+nx,a[1]+ny],[b[0]+nx,b[1]+ny],[b[0]-nx,b[1]-ny],[a[0]-nx,a[1]-ny]],p);g.fill();
 }
 for(const [x,y] of road.points){polygon(g,Array.from({length:24},(_,i)=>[x+Math.cos(i/24*Math.PI*2)*road.width/2,y+Math.sin(i/24*Math.PI*2)*road.width/2]),p);g.fill()}
}
function ground(ctx,iso,t){
 if(!terrainCache){
  terrainCache=document.createElement('canvas');terrainCache.width=2900;terrainCache.height=2100;const g=terrainCache.getContext('2d'),p=(x,y)=>({x:x*48-y*10+500,y:x*7+y*31+100});
  const mask=document.createElement('canvas');mask.width=2900;mask.height=2100;const m=mask.getContext('2d');m.fillStyle='#fff';
  for(const road of content.townRoads.filter(r=>!['service','field'].includes(r.role)))corridor(m,road,p);
  polygon(m,content.goldenScene.plaza,p);m.fill();
  // One limestone family, small value changes, staggered joints, no screen-axis checkerboard.
  const stones=document.createElement('canvas');stones.width=2900;stones.height=2100;const s=stones.getContext('2d');s.fillStyle='#a49c85';s.fillRect(0,0,2900,2100);
  const paint=s.createPattern(paving,'repeat'),unit=4/paving.naturalWidth;
  paint.setTransform(new DOMMatrix([48*unit,7*unit,-10*unit,31*unit,500,100]));s.fillStyle=paint;s.fillRect(0,0,2900,2100);
  s.globalCompositeOperation='destination-in';s.drawImage(mask,0,0);
  // Soft dust apron beneath the hard material edge, followed by restrained drainage/wear.
  g.save();g.filter='blur(4px)';g.globalAlpha=.28;g.drawImage(stones,0,0);g.restore();g.drawImage(stones,0,0);
  g.strokeStyle='#776f542f';g.lineWidth=2;polygon(g,content.goldenScene.plaza,p);g.stroke();g.strokeStyle='#ded4b537';g.lineWidth=.8;g.stroke();
  for(const road of content.townRoads){
   if(['service','field'].includes(road.role)){
    const dirt=document.createElement('canvas');dirt.width=2900;dirt.height=2100;const d=dirt.getContext('2d');d.fillStyle='#aa967477';corridor(d,road,p);g.save();g.filter='blur(3px)';g.drawImage(dirt,0,0);g.restore();
   }
   for(let j=1;j<road.points.length;j++){
    const a=road.points[j-1],b=road.points[j],dx=b[0]-a[0],dy=b[1]-a[1],n=Math.hypot(dx,dy),nx=-dy/n,ny=dx/n;
    for(let i=0;i<n*9;i++)for(const side of [-1,1]){
     const f=i/(n*9),seed=i+j*991+road.points[0][0]*13,edge=road.width/2+(hash(seed)-.5)*.12,x=a[0]+dx*f+nx*edge*side,y=a[1]+dy*f+ny*edge*side,q=p(x,y);
     g.fillStyle=hash(seed+1)>.45?'#79805f5a':'#81745a44';g.beginPath();g.ellipse(q.x,q.y,1+hash(seed+2)*2.5,.6+hash(seed+3),-.1,0,Math.PI*2);g.fill();
     if(hash(seed+4)>.86){g.strokeStyle='#64754c69';g.lineWidth=.7;g.beginPath();g.moveTo(q.x,q.y);g.lineTo(q.x-1.8,q.y-2.7);g.moveTo(q.x,q.y);g.lineTo(q.x+1.1,q.y-3.8);g.stroke()}
    }
   }
  }
  // Designed foot traffic from the Consortium threshold to the fountain and market.
  for(const [x,y,rx,ry] of [[10.8,15.8,54,27],[14.5,18.6,85,24],[20.3,17.7,65,24]]){const q=p(x,y);g.save();g.translate(q.x,q.y);g.scale(1,ry/rx);const wear=g.createRadialGradient(0,0,0,0,0,rx);wear.addColorStop(0,'#87795816');wear.addColorStop(1,'#87795800');g.fillStyle=wear;g.fillRect(-rx,-rx,rx*2,rx*2);g.restore()}
 }
 window.AstraeonView.drawCache(ctx,terrainCache,iso(0,0),500,100);
}
function prop(ctx,o,iso,player,time){
 if(o.pack!=='outdoor'&&o.pack!=='ruin'){const zoom=window.AstraeonView?.zoom||1;o={...o,w:o.w*zoom,h:o.h*zoom}}
 if(o.pack==='outdoor'||o.pack==='ruin')return window.AstraeonEnvironment.drawProp(ctx,o,iso,player,time);
 const sheet=o.pack==='secondary'?secondary:atlas;if(!sheet.complete||!sheet.naturalWidth)return false;
 const a=(o.pack==='secondary'?content.secondaryAtlas:content.atlas)[o.art],p=iso(o.x,o.y),left=p.x-o.w*a.anchor[0],top=p.y-o.h*a.anchor[1];
 if(left>ctx.canvas.clientWidth||left+o.w<0||top>ctx.canvas.clientHeight||top+o.h<0)return true;
 let alpha=1,hero=iso(player.x,player.y);
 if((o.tree||o.building||o.art==='stall'||o.art==='cart')&&hero.x>left+o.w*.18&&hero.x<left+o.w*.83&&hero.y<p.y-10&&hero.y>top+o.h*.15)alpha=.36;
 ctx.save();ctx.globalAlpha=alpha;ctx.save();ctx.translate(p.x+9,p.y+6);ctx.scale(1,.3);const contact=ctx.createRadialGradient(0,0,o.w*.04,0,0,o.w*.32);contact.addColorStop(0,'#28372c38');contact.addColorStop(1,'#28372c00');ctx.fillStyle=contact;ctx.fillRect(-o.w*.34,-o.w*.34,o.w*.68,o.w*.68);ctx.restore();
 const sway=o.tree?Math.sin(time*.7+o.x)*.8:0;
 ctx.drawImage(sheet,...a.rect,left+sway,top,o.w,o.h);
 if(o.art==='fountain'){ctx.globalAlpha=.3;ctx.strokeStyle='#b9f9ed';ctx.lineWidth=1;for(let k=0;k<2;k++){ctx.beginPath();ctx.ellipse(p.x,p.y-25,18+((time*9+k*15)%28),5+((time*2+k*4)%8),0,0,Math.PI*2);ctx.stroke()}}
 if(o.art==='stall'){ctx.globalAlpha=.55;ctx.fillStyle='#ffe1a0';let q=.65+.35*Math.sin(time*2+o.x);ctx.shadowColor='#ffd37b';ctx.shadowBlur=6*q;ctx.beginPath();ctx.arc(p.x+o.w*.33,p.y-o.h*.43,2.5,0,Math.PI*2);ctx.fill()}
 ctx.restore();return true;
}
function flowerBeds(ctx,iso){for(const [x,y] of [[11,12],[17.8,12],[11,19.5],[18,22]]){let p=iso(x,y);ctx.save();ctx.fillStyle='#395f3e';ctx.beginPath();ctx.ellipse(p.x,p.y,30,13,0,0,Math.PI*2);ctx.fill();for(let i=0;i<9;i++){let xx=p.x+(hash(i+x)*2-1)*25,yy=p.y+(hash(i+y)*2-1)*8;ctx.fillStyle=i%2?'#e9b0a1':'#f3dea0';ctx.beginPath();ctx.arc(xx,yy-3,2,0,Math.PI*2);ctx.fill()}ctx.restore()}}
window.AstraeonScene={whenReady,ground,prop,flowerBeds,objects:content.townObjects,ready:()=>atlas.complete&&atlas.naturalWidth};
})();
