/* Canvas2D adapter for the ASTRAEON-native spatial contract. Static terrain,
 * mesh parts and shadows are cached independently; actors share their depth list. */
(() => {
'use strict';
const palette={stone:0xa99876,stoneLight:0xdac79b,blue:0x244e6d,gold:0xd5a24d,wood:0x60452d,leaf:0x42613e,grass:0x68734c,paving:0xa99b7f};
const project=v=>{const p=AstraeonView.project(v[0],v[1]);return [p.x,p.y-v[2]*35]};
const groundDepth=p=>AstraeonView.project(p[0],p[1]).y;
const shade=(color,k)=>((Math.min(255,(color>>16)*k)|0)<<16)|((Math.min(255,((color>>8)&255)*k)|0)<<8)|(Math.min(255,(color&255)*k)|0);
const color=c=>typeof c==='number'?'#'+c.toString(16).padStart(6,'0'):c;
function polygon(g,points,fill,alpha=1,stroke=null){g.save();g.globalAlpha=alpha;g.beginPath();points.forEach(([x,y],i)=>i?g.lineTo(x,y):g.moveTo(x,y));g.closePath();g.fillStyle=color(fill);g.fill();if(stroke){g.strokeStyle=color(stroke);g.lineWidth=.8;g.stroke()}g.restore()}
function cache(bounds,paint){const [x,y,w,h]=bounds,canvas=document.createElement('canvas');canvas.width=Math.ceil(w);canvas.height=Math.ceil(h);const ctx=canvas.getContext('2d');ctx.translate(-x,-y);paint(ctx);return {canvas,x,y}}
function meshCache(part){const points=part.vertices.map(project),xs=points.map(p=>p[0]),ys=points.map(p=>p[1]),left=Math.floor(Math.min(...xs))-2,top=Math.floor(Math.min(...ys))-2;return cache([left,top,Math.max(...xs)-left+2,Math.max(...ys)-top+2],ctx=>{
 const faces=part.faces.map(indices=>indices.map(i=>part.vertices[i])).sort((a,b)=>{const depth=vs=>vs.reduce((sum,v)=>sum+1120*v[0]+1680*v[1]+1504*v[2],0)/vs.length;return depth(a)-depth(b)});
 for(const vs of faces){const screen=vs.map(project),area=screen.reduce((sum,p,i)=>{const next=screen[(i+1)%screen.length];return sum+p[0]*next[1]-p[1]*next[0]},0);if(area<=0)continue;const a=vs[0],b=vs[1],c=vs[2],u=b.map((v,i)=>v-a[i]),v=c.map((n,i)=>n-a[i]),normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]],len=Math.hypot(...normal)||1,k=.72+.30*Math.abs(normal[2])/len+.10*normal[0]/len;polygon(ctx,screen,shade(palette[part.material]||0xaa9988,k),1,0x27352e)}
 })}
class WorldView{
 constructor(canvas,world){this.canvas=canvas;this.ctx=canvas.getContext('2d');this.world=world;this.nodes=new Map();this.debug={collision:false,navigation:false,occlusion:false,lighting:false};this.camera={x:0,y:0};this.zoom=1;this.root={x:0,y:0};this.occlusion=[];
  const b=world.bounds,pts=[[b.minX,b.minY,0],[b.maxX,b.minY,0],[b.maxX,b.maxY,0],[b.minX,b.maxY,0]].map(project),xs=pts.map(p=>p[0]),ys=pts.map(p=>p[1]);this.cacheBounds=[Math.min(...xs)-140,Math.min(...ys)-180,Math.max(...xs)-Math.min(...xs)+280,Math.max(...ys)-Math.min(...ys)+360];
  this.ground=cache(this.cacheBounds,g=>{polygon(g,pts,palette[world.scene.terrain.material]||palette.grass);for(let x=b.minX;x<b.maxX;x+=.5)for(let y=b.minY;y<b.maxY;y+=.5){const c=((x*19+y*37)%7)<2?0x7c8256:0x5f7149;polygon(g,[[x,y,0],[x+.45,y,0],[x+.45,y+.45,0],[x,y+.45,0]].map(project),c,.16)}
   for(const s of world.scene.terrain.surfaces){polygon(g,s.polygon.map(p=>project([...p,.01])),palette.paving);const xs=s.polygon.map(p=>p[0]),ys=s.polygon.map(p=>p[1]);for(let x=Math.min(...xs);x<Math.max(...xs);x+=.5)for(let y=Math.min(...ys);y<Math.max(...ys);y+=.5)if(AstraeonSpatialV3.pointIn({x:x+.25,y:y+.25},s.polygon))polygon(g,[[x,y,0],[x+.48,y,0],[x+.48,y+.48,0],[x,y+.48,0]].map(project),palette.paving,1,0x80745f)}
  });
  this.shadows=cache(this.cacheBounds,g=>{for(const p of world.shadowPolygons)polygon(g,p.polygon.map(v=>project([...v,0])),0x172b28,world.scene.lighting.sun.strength);for(const p of world.solids)polygon(g,p.footprint.map(v=>project([...v,0])),0x101d1b,.22)});
  this.lightPools=cache(this.cacheBounds,g=>{for(const o of world.scene.objects)for(const l of o.lights){const p=project([l.position[0],l.position[1],0]);g.save();g.translate(...p);g.scale(1,.46);const gradient=g.createRadialGradient(0,0,0,0,0,l.radius*28);gradient.addColorStop(0,l.color+'30');gradient.addColorStop(1,l.color+'00');g.fillStyle=gradient;g.fillRect(-l.radius*28,-l.radius*28,l.radius*56,l.radius*56);g.restore()}});
  for(const part of world.parts){const center=part.footprint.reduce((sum,v)=>[sum[0]+v[0]/part.footprint.length,sum[1]+v[1]/part.footprint.length],[0,0]);this.nodes.set(part.id,{...meshCache(part),zIndex:groundDepth(center)+part.height*.001,alpha:1})}
 }
 setDebug(name,on){this.debug[name]=on;this.debugCache=cache(this.cacheBounds,g=>this.paintDebug(g))}
 paintDebug(g){if(this.debug.navigation)for(const c of this.world.navCells){const p=project([c.x,c.y,0]);g.fillStyle=c.walkable?'#73eed2':'#f88380';g.beginPath();g.arc(...p,2,0,Math.PI*2);g.fill()}
  if(this.debug.collision)for(const s of this.world.solids)polygon(g,s.footprint.map(v=>project([...v,.02])),0xfc6262,.24,0xff9999);
  if(this.debug.occlusion)for(const p of this.world.overheads)polygon(g,AstraeonSpatialV3.hull(p.vertices.map(project)),0x8e97ff,.12,0xc6c9ff);
  if(this.debug.lighting)for(const p of this.world.shadowPolygons)polygon(g,p.polygon.map(v=>project([...v,.02])),0xf5c467,.10,0xffcf67);
 }
 update(t,bitmap,dt){const p=project([t.position.x,t.position.y,t.position.z]),samples=[{x:p[0],y:p[1]-65},{x:p[0]-12,y:p[1]-45},{x:p[0]+12,y:p[1]-45}];this.actorDepth=groundDepth([t.position.x,t.position.y]);this.occlusion=[];
  for(const part of this.world.overheads){const poly=AstraeonSpatialV3.hull(part.vertices.map(project)),hide=samples.some(s=>AstraeonSpatialV3.pointIn(s,poly)),node=this.nodes.get(part.id),goal=hide?.18:1;node.alpha+=(goal-node.alpha)*(1-Math.exp(-12*dt));if(hide)this.occlusion.push(part.id)}
  const w=innerWidth,h=innerHeight,dpr=Math.min(2,devicePixelRatio);if(this.canvas.width!==Math.round(w*dpr)||this.canvas.height!==Math.round(h*dpr)){this.canvas.width=Math.round(w*dpr);this.canvas.height=Math.round(h*dpr);this.canvas.style.width=w+'px';this.canvas.style.height=h+'px'}
  const b=this.world.bounds,groundWidth=(b.maxX-b.minX)*48+(b.maxY-b.minY)*32,groundHeight=(b.maxX-b.minX)*14+(b.maxY-b.minY)*22;this.zoom=w<700?1:Math.min(1.05,(w-60)/groundWidth,(h-175)/(groundHeight+26));const center=w<700?p:project([(b.minX+b.maxX)/2,(b.minY+b.maxY)/2,0]),k=1-Math.exp(-6*dt);this.camera.x+=(center[0]-this.camera.x)*k;this.camera.y+=(center[1]-this.camera.y)*k;this.root={x:w/2-this.camera.x*this.zoom,y:h*.57-this.camera.y*this.zoom};
  const g=this.ctx;g.setTransform(dpr,0,0,dpr,0,0);g.clearRect(0,0,w,h);g.save();g.translate(this.root.x,this.root.y);g.scale(this.zoom,this.zoom);const blit=node=>{g.save();g.globalAlpha=node.alpha??1;g.drawImage(node.canvas,node.x,node.y);g.restore()};blit(this.ground);blit(this.shadows);blit(this.lightPools);
  for(const f of t.feet){if(!f)continue;const v=project([f.x,f.y,t.position.z]);g.fillStyle='rgba(18,37,29,'+.33*(1-Math.min(.7,f.z))+')';g.beginPath();g.ellipse(...v,7,3.4,0,0,Math.PI*2);g.fill()}
  const actor={zIndex:this.actorDepth,draw:()=>g.drawImage(bitmap,p[0]-64,p[1]-102)};for(const node of [...this.nodes.values(),actor].sort((a,b)=>a.zIndex-b.zIndex))node.draw?node.draw():blit(node);if(this.debugCache)blit(this.debugCache);g.restore();
 }
 screenToWorld(x,y){return AstraeonView.inverse((x-this.root.x)/this.zoom,(y-this.root.y)/this.zoom)}
 worldToScreen(x,y){const p=project([x,y,0]);return{x:this.root.x+p[0]*this.zoom,y:this.root.y+p[1]*this.zoom}}
 snapshot(){return{occlusion:[...this.occlusion],alphas:Object.fromEntries([...this.nodes].map(([id,n])=>[id,n.alpha])),shadowPolygons:this.world.shadowPolygons,actorDepth:this.actorDepth,partDepths:Object.fromEntries([...this.nodes].map(([id,n])=>[id,n.zIndex])),zoom:this.zoom,debug:{...this.debug}}}
}
class WarriorView{
 constructor(manifest){this.manifest=manifest;this.images={};this.canvas=document.createElement('canvas');this.canvas.width=this.canvas.height=128;this.ctx=this.canvas.getContext('2d')}
 async load(){await Promise.all(Object.values(this.manifest.clips).flatMap(c=>[[c.clip,c.atlas],[c.torso,'assets/'+c.torso+'.webp']]).concat([['warrior','assets/warrior-directional-v1.webp']]).map(([id,path])=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{this.images[id]=im;resolve()};im.onerror=()=>reject(Error('Cannot load '+path));im.src=path})))}
 draw(t,{scrub=false}={}){const ctx=this.ctx;ctx.clearRect(0,0,128,128);const heading=AstraeonView.project(Math.cos(t.rotation),Math.sin(t.rotation)),row=((Math.round((Math.PI/2-Math.atan2(heading.y,heading.x))/(Math.PI/4))%8)+8)%8;
  const p=AstraeonView.project(t.position.x,t.position.y),iso=(x,y,z=0)=>{const q=AstraeonView.project(x,y);return {x:64+q.x-p.x,y:102+q.y-p.y-z+t.position.z*35}},profile=t.profile;
  if(t.speed>.02||['stop','start'].includes(t.state)||scrub){const key=profile.clip,cycle=((t.gait%1)+1)%1,col=Math.floor(cycle*8),registration=AstraeonHeroRegistration[key],anchor=registration.anchors[row*8+col];AstraeonWarriorRig.draw(ctx,iso,t,this.images[key],AstraeonDirectionalMetadata[key],registration,row,col,.5,{x:64,y:102-(t.flight||0)*35},-anchor[0]*.5,this.images[profile.torso]);this.frame={row,column:col,clip:key,phase:cycle,contacts:registration.frames[row*8+col].contacts}}
  else{const meta=AstraeonDirectionalMetadata.warrior,reg=AstraeonHeroRegistration.warrior,b=meta.frames[row*6],a=reg.anchors[row*6],unit=70/reg.heights[row];ctx.drawImage(this.images.warrior,...b,64-a[0]*unit,102-a[1]*unit,b[2]*unit,b[3]*unit);this.frame={row,column:0,clip:'warrior',phase:0,contacts:[]}}
  if(scrub){const frame=this.manifest.clips[t.strategy].frames[row*8+this.frame.column],origin=[64-frame.footAnchorX*.5,102-frame.footAnchorY*.5];ctx.strokeStyle='#9cfff0';ctx.lineWidth=.7;const x=origin[0]+frame.bodyAnchor[0]*.5,y=origin[1]+frame.bodyAnchor[1]*.5;ctx.beginPath();ctx.moveTo(x-4,y);ctx.lineTo(x+4,y);ctx.moveTo(x,y-4);ctx.lineTo(x,y+4);ctx.stroke();this.frame.bodyAnchor=[...frame.bodyAnchor];this.frame.footAnchor=[frame.footAnchorX,frame.footAnchorY];this.frame.events=[...frame.events];this.frame.attachments=structuredClone(frame.attachments)}
  return this.canvas;
 }
}
window.AstraeonCanvasV3={WorldView,WarriorView,project};
})();
