/* Static UV ownership for articulated armor. Visible armor has one owner; an explicitly declared dark sleeve underlap may overlap.
   Requires SpriteSegmentedChain. The masks are fixed in rest-art space. */
'use strict';
class SpriteOwnedSegmentChain extends SpriteSegmentedChain {
 constructor(canvas,image,d){
  const cuts=d?.owned_cuts;
  if(!Array.isArray(cuts)||cuts.length!==4||cuts.some((v,i)=>!Number.isFinite(v)||v<=0||v>=d.canvas[1]||(i&&v<=cuts[i-1])))throw Error('Invalid owned joint cuts');
  const f=d.dark_sleeve_underlap;if(f){if(!Array.isArray(f.rows)||f.rows.length!==2||f.rows.some((v,i)=>!Number.isFinite(v)||v<0||v>d.canvas[1]||(i&&v<=f.rows[i-1]))||!Array.isArray(f.maximum_rgb)||f.maximum_rgb.length!==3||f.maximum_rgb.some(v=>!Number.isFinite(v)||v<0||v>255)||!Number.isFinite(f.minimum_blue_to_red)||f.minimum_blue_to_red<0||f.minimum_blue_to_red>1||!Number.isFinite(d.joint_underlap_radius)||d.joint_underlap_radius<=0||d.joint_underlap_radius>Math.max(...d.canvas))throw Error('Invalid static sleeve underlap');}
  super(canvas,image,d);
  const names=['upper','knee','lower','cuff','distal'],bounds=[0,...cuts,d.canvas[1]];
  this.pieceTextures={};this.segmentRest={};const gl=this.gl;
  for(let i=0;i<names.length;i++){
   const c=document.createElement('canvas');[c.width,c.height]=d.canvas;const x=c.getContext('2d');x.drawImage(image,0,0);const p=x.getImageData(0,0,c.width,c.height);
   for(let y=0;y<c.height;y++)if(y<bounds[i]||y>=bounds[i+1])for(let j=0;j<c.width;j++){const k=(y*c.width+j)*4,f=d.dark_sleeve_underlap,keep=names[i]==='upper'&&f&&y>=f.rows[0]&&y<f.rows[1]&&p.data[k]<=f.maximum_rgb[0]&&p.data[k+1]<=f.maximum_rgb[1]&&p.data[k+2]<=f.maximum_rgb[2]&&p.data[k+2]>=p.data[k]*f.minimum_blue_to_red;if(!keep)p.data[k+3]=0;}
   if((names[i]==='knee'||names[i]==='upper')&&d.dark_sleeve_underlap){const f=d.dark_sleeve_underlap,E=d.rest[d.nodes[1]],radius=d.joint_underlap_radius;for(let y=0;y<c.height;y++)for(let j=0;j<c.width;j++){const k=(y*c.width+j)*4;if(((names[i]==='knee'&&y<E[1])||(names[i]==='upper'&&y>=cuts[0]))&&Math.hypot(j-E[0],y-E[1])>radius&&p.data[k]<=f.maximum_rgb[0]&&p.data[k+1]<=f.maximum_rgb[1]&&p.data[k+2]<=f.maximum_rgb[2]&&p.data[k+2]>=p.data[k]*f.minimum_blue_to_red)p.data[k+3]=0;}}
   x.putImageData(p,0,0);const tex=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,tex);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,c);this.pieceTextures[names[i]]=tex;
   const r=[];for(let k=0;k<this.allRest.length;k+=3){const tri=this.allRest.slice(k,k+3);if(Math.max(...tri.map(v=>v[1]))>=bounds[i]-1&&Math.min(...tri.map(v=>v[1]))<=(names[i]==='upper'&&d.dark_sleeve_underlap?d.dark_sleeve_underlap.rows[1]:bounds[i+1])+1)r.push(...tri)}this.segmentRest[names[i]]=r;
  }
  this.originalTexture=this.texture;
 }
 skinPoint(x,y,p){const [a,b,c,e]=this.definition.nodes;if(this.segment==='knee')return this.mapBone([x,y],b,c,p);if(this.segment==='cuff'){if(this.definition.distal==='fixed_orientation')return[x+p[c][0],y+p[c][1]];return this.mapBone([x,y],c,e,p,true)}return super.skinPoint(x,y,p)}
 drawPieces(p){const w=this.canvas.width,h=this.canvas.height;if(this.output.width!==w)this.output.width=w;if(this.output.height!==h)this.output.height=h;const x=this.output.getContext('2d');x.clearRect(0,0,w,h);const geometry={};for(const n of ['upper','lower','knee','cuff','distal']){this.segment=n;this.rest=this.segmentRest[n];if(!this.rest.length)continue;this.texture=this.pieceTextures[n];geometry[n]={rest:this.rest,vertices:SpriteArticulatedLayer.prototype.draw.call(this,p)};x.drawImage(this.canvas,0,0)}this.texture=this.originalTexture;this.rest=this.allRest;return{canvas:this.output,geometry}}
 dispose(){for(const t of Object.values(this.pieceTextures))this.gl.deleteTexture(t);this.texture=this.originalTexture;super.dispose()}
}
window.SpriteOwnedSegmentChain=SpriteOwnedSegmentChain;
