/* Original source-driven cutout articulation. Requires SpriteArticulatedLayer.
   Static UV partitions overlap at joints; no image/frame fitting or final shoe patch. */
'use strict';
class SpriteSegmentedChain extends SpriteArticulatedLayer {
 constructor(canvas,image,d){super(canvas,image,d);this.allRest=this.rest;this.segment='upper';this.output=document.createElement('canvas');this.output.width=this.output.height=512;const [a,b,c,e]=d.bands;
  this.segmentRest={upper:[],lower:[],distal:[]};for(let i=0;i<this.allRest.length;i+=3){const tri=this.allRest.slice(i,i+3),lo=Math.min(...tri.map(p=>p[1])),hi=Math.max(...tri.map(p=>p[1]));if(hi<=b+1e-8)this.segmentRest.upper.push(...tri);if(lo>=a-1e-8&&hi<=e+1e-8)this.segmentRest.lower.push(...tri);if(lo>=c-1e-8)this.segmentRest.distal.push(...tri)}
 }
 skinPoint(x,y,p){const d=this.definition,[a,b,c,e]=d.nodes;if(this.segment==='upper')return this.mapBone([x,y],a,b,p);if(this.segment==='lower')return this.mapBone([x,y],b,c,p);if(d.distal==='fixed_orientation')return[x+p[c][0],y+p[c][1]];return this.mapBone([x,y],c,e,p,true)}
 drawPieces(pose){const w=this.canvas.width,h=this.canvas.height;if(this.output.width!==w)this.output.width=w;if(this.output.height!==h)this.output.height=h;const q=this.output.getContext('2d');q.clearRect(0,0,w,h);const geometry={};for(const name of ['upper','lower','distal']){this.segment=name;this.rest=this.segmentRest[name];geometry[name]={rest:this.rest,vertices:super.draw(pose)};q.drawImage(this.canvas,0,0)}this.rest=this.allRest;return{canvas:this.output,geometry}}
}
class SpritePickupTorso extends SpriteArticulatedLayer {
 constructor(canvas,image,d){
  for(const n of ['hips','neck'])if(!Array.isArray(d.rest?.[n])||d.rest[n].length!==2||d.rest[n].some(x=>!Number.isFinite(x)))throw Error('Invalid torso rest');
  const f=d.hanging_cloth;if(f){for(const [key,len]of [['x',4],['y',2]])if(!Array.isArray(f[key])||f[key].length!==len||f[key].some((x,i)=>!Number.isFinite(x)||(i&&x<=f[key][i-1])))throw Error('Invalid hanging garment field');}
  super(canvas,image,d);
 }
 skinPoint(x,y,p){const q=this.mapBone([x,y],'hips','neck',p),f=this.definition.hanging_cloth;if(!f)return q;
  const w=this.smooth(f.y[0],f.y[1],y)*this.smooth(f.x[0],f.x[1],x)*(1-this.smooth(f.x[2],f.x[3],x));
  return[q[0]*(1-w)+(x+p.hips[0])*w,q[1]*(1-w)+(y+p.hips[1])*w];}
 draw(p){if(!Array.isArray(p.neck))throw Error('Missing neck pose');return super.draw(p)}
}
class SpritePickupHead extends SpriteArticulatedLayer {
 skinPoint(x,y,p){const a=this.definition.pivot_neck,t=p.head_angle[0],dx=x-a[0],dy=y-a[1];return[a[0]+p.neck[0]+Math.cos(t)*dx-Math.sin(t)*dy,a[1]+p.neck[1]+Math.sin(t)*dx+Math.cos(t)*dy]}
 draw(p){if(!Array.isArray(p.neck)||!Array.isArray(p.head_angle))throw Error('Missing head attachment/angle');return super.draw(p)}
}
class SpritePickupFrontPlane extends SpritePickupTorso {
 skinPoint(x,y,p){const d=this.definition,A=d.rest.hips,B=d.rest.neck;
  let ratio=(B[1]+p.neck[1]-A[1]-p.hips[1])/(B[1]-A[1]);
  if(d.front_plane==='waist'){const sides=['left','right'];ratio=sides.reduce((sum,s)=>{const a=d.rest[s+'.hip'],b=d.rest[s+'.knee'];return sum+(b[1]+p[s+'.knee'][1]-a[1]-p[s+'.hip'][1])/(b[1]-a[1])},0)/2;}
  return[x+p.hips[0],A[1]+p.hips[1]+(y-A[1])*ratio];}
 draw(p){const d=this.definition,A=d.rest.hips,B=d.rest.neck,ratio=(B[1]+p.neck[1]-A[1]-p.hips[1])/(B[1]-A[1]);
  if(d.front_plane==='torso'&&ratio<=0){const gl=this.gl;gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);this.vertices=[];return[];}
  return super.draw(p);}
}
Object.assign(window,{SpriteSegmentedChain,SpritePickupTorso,SpritePickupHead,SpritePickupFrontPlane});
