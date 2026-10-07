/* Presentation-only city renderer. Receives projection/state; never mutates combat. */
(() => {
'use strict';
const content=window.AstraeonContent, atlas=new Image(),paving=new Image(),secondary=new Image(),hall=new Image();
const district=Object.fromEntries(['forge','inn','shrine','cottage'].map(key=>[key,new Image()]));
const artwork=[[atlas,'./assets/town-atlas-v1.webp'],[paving,'./assets/town-limestone-v1.webp'],[secondary,'./assets/secondary-atlas-v1.webp'],[hall,'./assets/consortium-hall-v2.webp'],...Object.entries(district).map(([key,image])=>[image,`./assets/wayfarer-${key}-v1.webp`])];
let artworkReady;
function ensure(zone=0){if(zone===0&&content.nativeWorld?.spatial.scene.streaming)return Promise.resolve();if(!artworkReady)artworkReady=Promise.all(artwork.map(([image,url])=>new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=()=>{artworkReady=null;reject(new Error('Cannot load town artwork'))};image.src=url})));return artworkReady}
const whenReady=content.nativeWorld?.spatial.scene.streaming?Promise.resolve():ensure();
let blueHall=null;
function civicArtwork(){
 if(blueHall)return blueHall;
 blueHall=document.createElement('canvas');blueHall.width=hall.naturalWidth;blueHall.height=hall.naturalHeight;
 const g=blueHall.getContext('2d');g.drawImage(hall,0,0);const image=g.getImageData(0,0,blueHall.width,blueHall.height),d=image.data;
 // A material palette conversion preserves the painted roof-plane lighting.
 for(let i=0;i<d.length;i+=4){const r=d[i],green=d[i+1],b=d[i+2];if(d[i+3]&&green>r*1.12&&b>r*.92&&green>b*.98&&green-r>14){d[i]=green*.64;d[i+1]=green*.83;d[i+2]=Math.min(255,green*1.08)}}
 g.putImageData(image,0,0);return blueHall;
}
const hash=n=>{let x=Math.sin(n*127.1+311.7)*43758.5453;return x-Math.floor(x)};
// World-aligned material courses share the same projection as architecture and actors.
let terrainCache=null,vergePattern=null;
const visibility=new Map();
const visibilitySnapshot=()=>[...visibility].map(([id,s])=>({id,alpha:s.alpha,overlap:s.overlap}));
function verge(ctx,iso,image){
 if(!vergePattern){
  const material=document.createElement('canvas');material.width=384;material.height=384;const g=material.getContext('2d');
  g.fillStyle='#859074';g.fillRect(0,0,384,384);g.globalAlpha=.44;g.filter='blur(.7px)';g.drawImage(image,0,0,384,384);
  vergePattern=ctx.createPattern(material,'repeat');
 }
 const origin=iso(0,0),zoom=window.AstraeonView.zoom,unit=8/384;
 vergePattern.setTransform(new DOMMatrix(window.AstraeonView.materialTransform(unit,origin,zoom)));
 ctx.fillStyle=vergePattern;ctx.fillRect(0,0,ctx.canvas.clientWidth,ctx.canvas.clientHeight);
}
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
  terrainCache=document.createElement('canvas');terrainCache.width=4000;terrainCache.height=2100;const g=terrainCache.getContext('2d'),p=(x,y,z=0)=>{const q=window.AstraeonView.project(x,y);return{x:q.x+1450,y:q.y+100-z}};
  for(const space of content.spaces||[]){
   polygon(g,space.polygon,p);g.fillStyle=space.role==='yard'?'#a08c67bb':space.role==='garden'?'#6c7e5966':'#66815155';g.fill();
   g.lineWidth=space.role==='garden'?5:3;g.strokeStyle=space.role==='yard'?'#b6a18499':'#b8b39a99';g.stroke();
   g.lineWidth=1;g.strokeStyle='#58614977';g.stroke();
  }
  const mask=document.createElement('canvas');mask.width=4000;mask.height=2100;const m=mask.getContext('2d');m.fillStyle='#fff';
  for(const road of content.townRoads.filter(r=>!['service','field'].includes(r.role)))corridor(m,road,p);
  polygon(m,content.goldenScene.plaza,p);m.fill();
  // Door landings and service approaches belong to the same public ground as roads.
  for(const court of content.forecourts){polygon(m,court.points,p);m.fill()}
  // One limestone family, small value changes, staggered joints, no screen-axis checkerboard.
  const stones=document.createElement('canvas');stones.width=4000;stones.height=2100;const s=stones.getContext('2d');s.fillStyle='#a49c85';s.fillRect(0,0,4000,2100);
  const paint=s.createPattern(paving,'repeat'),unit=4/paving.naturalWidth;
  paint.setTransform(new DOMMatrix(window.AstraeonView.materialTransform(unit,{x:1450,y:100})));s.fillStyle=paint;s.fillRect(0,0,4000,2100);
  // A quiet limestone court has its own scale and value grouping, within one family.
  s.save();polygon(s,content.goldenScene.plaza,p);s.clip();s.fillStyle='#d1c6aa';s.globalAlpha=.3;s.fillRect(0,0,4000,2100);s.globalAlpha=1;
  // Projected ashlar border and a restrained meeting-ring give the square a public identity.
  s.lineJoin='round';s.lineWidth=9;s.strokeStyle='#8a80693d';polygon(s,content.goldenScene.plaza,p);s.stroke();
  s.lineWidth=3;s.strokeStyle='#e5d9bd80';s.stroke();
  const basin=content.townObjects.find(o=>o.id==='astral-fountain');
  for(const radius of [1.65,1.82]){polygon(s,Array.from({length:64},(_,i)=>[basin.x+Math.cos(i/64*Math.PI*2)*radius,basin.y+Math.sin(i/64*Math.PI*2)*radius]),p);s.lineWidth=radius===1.65?4:1.5;s.strokeStyle=radius===1.65?'#81785e55':'#eee0bf80';s.stroke()}
  s.restore();
  // Broad, clipped wear varies this connected material without pasted texture patches.
  s.save();s.globalCompositeOperation='multiply';
  for(const court of content.forecourts){const [x,y]=court.points.reduce((a,p)=>[a[0]+p[0]/court.points.length,a[1]+p[1]/court.points.length],[0,0]),r=90,tint='#dbcfb9';
   const q=p(x,y);s.save();s.translate(q.x,q.y);s.scale(1,.55);const wash=s.createRadialGradient(0,0,0,0,0,r);wash.addColorStop(0,tint);wash.addColorStop(1,'#ffffff');s.fillStyle=wash;s.fillRect(-r,-r,r*2,r*2);s.restore();
  }s.restore();
  s.globalCompositeOperation='destination-in';s.drawImage(mask,0,0);
  // Soil accumulation surrounds the stone. A softened alpha edge seats paving in the verge.
  const apron=document.createElement('canvas');apron.width=4000;apron.height=2100;const ag=apron.getContext('2d');
  ag.drawImage(mask,0,0);ag.globalCompositeOperation='source-in';ag.fillStyle='#b09e7b';ag.fillRect(0,0,4000,2100);
  g.save();g.filter='blur(8px)';g.globalAlpha=.55;g.drawImage(apron,0,0);g.restore();
  g.save();g.filter='blur(.45px)';g.drawImage(stones,0,0);g.restore();
  g.strokeStyle='#776f542f';g.lineWidth=2;polygon(g,content.goldenScene.plaza,p);g.stroke();g.strokeStyle='#ded4b537';g.lineWidth=.8;g.stroke();
  for(const road of content.townRoads){
   if(['service','field'].includes(road.role)){
    const dirt=document.createElement('canvas');dirt.width=4000;dirt.height=2100;const d=dirt.getContext('2d');d.fillStyle='#aa967477';corridor(d,road,p);g.save();g.filter='blur(3px)';g.drawImage(dirt,0,0);g.restore();
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
  // Traffic wear follows authored services, never the superseded court coordinates.
  for(const entry of content.services||[]){const q=p(entry.x,entry.y),rx=48;g.save();g.translate(q.x,q.y);g.scale(1,.45);const wear=g.createRadialGradient(0,0,0,0,0,rx);wear.addColorStop(0,'#87795825');wear.addColorStop(1,'#87795800');g.fillStyle=wear;g.fillRect(-rx,-rx,rx*2,rx*2);g.restore()}
  // Earth under the existing tree clusters, rather than a tree pasted onto stone/grass.
  for(const o of content.townObjects.filter(o=>o.tree)){
   const q=p(o.x,o.y),r=o.w*.23;g.save();g.translate(q.x,q.y);g.scale(1,.55);const soil=g.createRadialGradient(0,0,3,0,0,r);soil.addColorStop(0,'#75694f66');soil.addColorStop(.55,'#89795735');soil.addColorStop(1,'#89795700');g.fillStyle=soil;g.fillRect(-r,-r,r*2,r*2);g.restore();
  }
  window.AstraeonTownStructure.ground(g,p);
 }
 window.AstraeonView.drawCache(ctx,terrainCache,iso(0,0),1450,100);
}
function prop(ctx,o,iso,player,time){
 if(o.pack==='native-masonry'){
  const vs=o.part.vertices,faces=o.part.faces.map(indices=>({indices,points:indices.map(i=>iso(vs[i][0],vs[i][1],vs[i][2]*35))}));
  faces.sort((a,b)=>a.indices.reduce((s,i)=>s+14*vs[i][0]+22*vs[i][1]+30*vs[i][2],0)/a.indices.length-b.indices.reduce((s,i)=>s+14*vs[i][0]+22*vs[i][1]+30*vs[i][2],0)/b.indices.length);
  for(const face of faces){const ps=face.points,area=ps.reduce((s,p,i)=>s+p.x*ps[(i+1)%ps.length].y-ps[(i+1)%ps.length].x*p.y,0);if(area>=0)continue;
   const top=face.indices.every(i=>vs[i][2]>.01);ctx.beginPath();ps.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.closePath();ctx.fillStyle=top?'#d6c6a6':'#9c947f';ctx.fill();ctx.lineWidth=.7*window.AstraeonView.zoom;ctx.strokeStyle='#746f60';ctx.stroke();
   if(!top){const low=face.indices.filter(i=>vs[i][2]<.01);if(low.length===2){const a=vs[low[0]],b=vs[low[1]],n=Math.hypot(b[0]-a[0],b[1]-a[1]);for(let row=1;row<3;row++){const p=iso(a[0],a[1],row*.95/3*35),q=iso(b[0],b[1],row*.95/3*35);ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke()}
    for(let d=.55;d<n;d+=.55){const f=d/n,p=iso(a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f),q=iso(a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f,.95*35);ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke()}}
   }
  }return true;
 }
 if(o.pack!=='outdoor'&&o.pack!=='ruin'){const zoom=window.AstraeonView?.zoom||1;o={...o,w:o.w*zoom,h:o.h*zoom}}
 if(o.pack==='outdoor'||o.pack==='ruin')return window.AstraeonEnvironment.drawProp(ctx,o,iso,player,time);
 const sheet=o.pack==='district'?district[o.art]:o.id==='guild-hall'?hall:o.pack==='secondary'?secondary:atlas;if(!sheet.complete||!sheet.naturalWidth)return false;
 const a=o.pack==='district'?{rect:[0,0,sheet.naturalWidth,sheet.naturalHeight],anchor:[o.art==='shrine'?.42:o.art==='inn'?.43:.5,.94]}:o.id==='guild-hall'?{rect:[0,0,hall.naturalWidth,hall.naturalHeight],anchor:[.4,.91]}:(o.pack==='secondary'?content.secondaryAtlas:content.atlas)[o.art],p=iso(o.x,o.y),left=p.x-o.w*a.anchor[0],top=p.y-o.h*a.anchor[1];
 if(left>ctx.canvas.clientWidth||left+o.w<0||top>ctx.canvas.clientHeight||top+o.h<0)return true;
 ctx.save();ctx.save();
 const block=content.townBlocks.find(b=>b.id===o.id);
 if(block&&!o.structuralLayer||block&&o.structuralLayer.name==='rear-wall'){
  // Tight contact follows the art anchor, separate from broad cached cast geometry.
  ctx.translate(p.x+4,p.y+3);ctx.scale(1,.32);
  const shade=ctx.createRadialGradient(0,0,0,0,0,o.w*.28);shade.addColorStop(0,'#293c323c');shade.addColorStop(1,'#293c3200');ctx.fillStyle=shade;ctx.fillRect(-o.w*.28,-o.w*.28,o.w*.56,o.w*.56);
 }else if(!o.structuralLayer||o.structuralLayer.name==='trunk'){ctx.translate(p.x+9,p.y+6);ctx.scale(1,.3);const contact=ctx.createRadialGradient(0,0,o.w*.04,0,0,o.w*.32);contact.addColorStop(0,'#28372c38');contact.addColorStop(1,'#28372c00');ctx.fillStyle=contact;ctx.fillRect(-o.w*.34,-o.w*.34,o.w*.68,o.w*.68)}ctx.restore();
 const sway=o.tree?Math.sin(time*.7+o.x)*.8:0;
 if(o.structuralLayer){
  const [x0,y0,x1,y1]=o.structuralLayer.region;
  ctx.save();ctx.beginPath();
  const shape=o.structuralLayer.polygon,hole=o.structuralLayer.exclude;
  const outline=points=>{points.forEach(([x,y],i)=>{i?ctx.lineTo(left+x*o.w,top+y*o.h):ctx.moveTo(left+x*o.w,top+y*o.h)});ctx.closePath()};
  if(shape)outline(shape);else ctx.rect(left+x0*o.w,top+y0*o.h,(x1-x0)*o.w,(y1-y0)*o.h);
  if(hole){ctx.clip();ctx.beginPath();ctx.rect(left,top,o.w,o.h);outline(hole)}ctx.clip('evenodd');
  if(o.structuralLayer.visibility==='selective-overhead'){
   const playerFoot=iso(player.x,player.y),layer=o.structuralLayer,depth=(x,y)=>14*x+22*y;
   const inside=(x,y)=>{if(x<x0||x>x1||y<y0||y>y1)return false;return !shape||window.AstraeonSpatialV3.pointIn({x,y},shape)};
   const overlap=depth(...layer.depth)>depth(player.x,player.y)&&[[0,62],[-8,45],[8,45]].some(([dx,dy])=>inside((playerFoot.x+dx*window.AstraeonView.zoom-left)/o.w,(playerFoot.y-dy*window.AstraeonView.zoom-top)/o.h));
   const key=o.id+'/'+layer.name,prior=visibility.get(key)||{alpha:1,time:time-.05},dt=Math.min(.1,Math.max(0,time-prior.time));
   const alpha=prior.alpha+((overlap?.23:1)-prior.alpha)*(1-Math.exp(-14*dt));visibility.set(key,{alpha,time,overlap});ctx.globalAlpha*=alpha;
  }
  ctx.drawImage(o.id==='guild-hall'?civicArtwork():sheet,...a.rect,left+sway,top,o.w,o.h);ctx.restore();
 }else ctx.drawImage(o.id==='guild-hall'?civicArtwork():sheet,...a.rect,left+sway,top,o.w,o.h);
 if(o.art==='fountain'){ctx.globalAlpha=.3;ctx.strokeStyle='#b9f9ed';ctx.lineWidth=1;for(let k=0;k<2;k++){ctx.beginPath();ctx.ellipse(p.x,p.y-25,18+((time*9+k*15)%28),5+((time*2+k*4)%8),0,0,Math.PI*2);ctx.stroke()}}
 if(o.art==='stall'){ctx.globalAlpha=.55;ctx.fillStyle='#ffe1a0';let q=.65+.35*Math.sin(time*2+o.x);ctx.shadowColor='#ffd37b';ctx.shadowBlur=6*q;ctx.beginPath();ctx.arc(p.x+o.w*.33,p.y-o.h*.43,2.5,0,Math.PI*2);ctx.fill()}
 if(!o.structuralLayer||['frontage','span'].includes(o.structuralLayer.name))for(const emitter of (content.lights||[]).filter(l=>l.objectId===o.id)){
  const lamp=iso(...emitter.position.slice(0,2),emitter.position[2]*35),r=12*window.AstraeonView.zoom;
  ctx.globalAlpha=.34+.025*Math.sin(time*3.1);const halo=ctx.createRadialGradient(lamp.x,lamp.y,0,lamp.x,lamp.y,r);halo.addColorStop(0,emitter.color+'bb');halo.addColorStop(1,emitter.color+'00');ctx.fillStyle=halo;ctx.fillRect(lamp.x-r,lamp.y-r,r*2,r*2);
 }
 ctx.restore();return true;
}
function flowerBeds(ctx,iso){for(const [x,y] of [[11,12],[17.8,12],[11,19.5],[18,22]]){let p=iso(x,y);ctx.save();ctx.fillStyle='#395f3e';ctx.beginPath();ctx.ellipse(p.x,p.y,30,13,0,0,Math.PI*2);ctx.fill();for(let i=0;i<9;i++){let xx=p.x+(hash(i+x)*2-1)*25,yy=p.y+(hash(i+y)*2-1)*8;ctx.fillStyle=i%2?'#e9b0a1':'#f3dea0';ctx.beginPath();ctx.arc(xx,yy-3,2,0,Math.PI*2);ctx.fill()}ctx.restore()}}
window.AstraeonScene={whenReady,ensure,verge,ground,prop,flowerBeds,visibilitySnapshot,objects:content.townObjects,ready:()=>atlas.complete&&atlas.naturalWidth};
})();
