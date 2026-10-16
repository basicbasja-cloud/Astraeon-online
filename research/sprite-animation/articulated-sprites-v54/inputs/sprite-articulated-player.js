/* Original static rest-art skinning. One authored binding; no frame image fitting. Requires SpriteMesh. */
'use strict';
class SpriteArticulatedLayer extends SpriteMesh {
 constructor(canvas,image,definition){
  if(!definition||!['chain','head','body'].includes(definition.kind))throw Error('Unknown articulated layer');
  const size=definition.canvas;if(!Array.isArray(size)||size.length!==2)throw Error('Missing logical canvas');
  const ys=[0,...(definition.kind==='chain'?(definition.bands||[]):[]),size[1]].sort((a,b)=>a-b);super(canvas,image,{width:size[0],height:size[1],grid_px:8,bands:ys.map(y=>({y,channel:'fixed'}))});this.definition=definition;
  if(definition.kind==='chain'){
   if(!['left','right'].includes(definition.owner)||!['arm','leg'].includes(definition.role)||!Array.isArray(definition.nodes)||definition.nodes.some(n=>typeof n!=='string'||!n.startsWith(definition.owner+'.')))throw Error('Unsafe anatomical owner binding');
   const expected=definition.role==='leg'?['hip','knee','ankle','toe']:['shoulder','elbow','wrist','palm'];if(definition.nodes.some((n,i)=>n!==definition.owner+'.'+expected[i]))throw Error('Role and joint sequence differ');
   if(!Array.isArray(definition.nodes)||definition.nodes.length!==4||!Array.isArray(definition.bands)||definition.bands.length!==4||definition.bands.some((v,i)=>!Number.isFinite(v)||(i&&v<=definition.bands[i-1])))throw Error('Invalid static chain binding');
   for(const n of definition.nodes){const p=definition.rest[n];if(!Array.isArray(p)||p.length!==2||p.some(v=>!Number.isFinite(v)))throw Error('Missing finite rest joint');}
   for(let i=0;i<3;i++){let a=definition.rest[definition.nodes[i]],b=definition.rest[definition.nodes[i+1]];if(Math.hypot(b[0]-a[0],b[1]-a[1])<1)throw Error('Zero length rest bone');}
  }
  if(definition.kind==='body'){if(!Array.isArray(definition.influences))throw Error('Missing body influence adapter');for(const f of definition.influences)if(typeof f.channel!=='string'||!Array.isArray(f.center)||f.center.length!==2||f.center.some(v=>!Number.isFinite(v))||!Array.isArray(f.radius)||f.radius.length!==2||f.radius.some(v=>!Number.isFinite(v)||v<=0)||!Number.isFinite(f.gain))throw Error('Invalid body influence');if(definition.cape_support)for(const axis of ['x','y']){let a=definition.cape_support[axis];if(!Array.isArray(a)||a.length!==2||a.some(v=>!Number.isFinite(v))||a[0]>=a[1])throw Error('Invalid cape support')}}
  // Retain only cells intersecting actual source alpha, including faint edges.
  const t=document.createElement('canvas');t.width=size[0];t.height=size[1];const tx=t.getContext('2d');tx.drawImage(image,0,0);const pixels=tx.getImageData(0,0,...size).data,w=size[0],h=size[1],integral=new Uint32Array((w+1)*(h+1));
  for(let y=0;y<h;y++){let row=0;for(let x=0;x<w;x++){row+=pixels[(y*w+x)*4+3]>0?1:0;integral[(y+1)*(w+1)+x+1]=integral[y*(w+1)+x+1]+row;}}
  const kept=[];for(let i=0;i<this.rest.length;i+=3){const a=this.rest.slice(i,i+3),x0=Math.max(0,Math.floor(Math.min(...a.map(p=>p[0])))-1),y0=Math.max(0,Math.floor(Math.min(...a.map(p=>p[1])))-1),x1=Math.min(w,Math.ceil(Math.max(...a.map(p=>p[0])))+1),y1=Math.min(h,Math.ceil(Math.max(...a.map(p=>p[1])))+1),sum=integral[y1*(w+1)+x1]-integral[y0*(w+1)+x1]-integral[y1*(w+1)+x0]+integral[y0*(w+1)+x0];if(sum)kept.push(...a)}this.rest=kept;if(!kept.length)throw Error('Empty rest art');
 }
 smooth(a,b,y){let t=Math.max(0,Math.min(1,(y-a)/(b-a)));return t*t*(3-2*t)}
 mapBone(p,a,b,pose,rigid=false){const d=this.definition,A=d.rest[a],B=d.rest[b],pa=pose[a],pb=pose[b],u=[B[0]-A[0],B[1]-A[1]],len=Math.hypot(...u),v=[B[0]+pb[0]-A[0]-pa[0],B[1]+pb[1]-A[1]-pa[1]],next=Math.hypot(...v);if(next<.1)throw Error('Collapsed animated bone');let ex=u[0]/len,ey=u[1]/len,nx=-ey,ny=ex,fx=v[0]/next,fy=v[1]/next,gx=-fy,gy=fx,q=[p[0]-A[0],p[1]-A[1]],along=q[0]*ex+q[1]*ey,across=q[0]*nx+q[1]*ny;return[A[0]+pa[0]+fx*along*(rigid?1:next/len)+gx*across,A[1]+pa[1]+fy*along*(rigid?1:next/len)+gy*across];}
 skinPoint(x,y,pose){
  const d=this.definition;if(d.kind==='head'){const p=pose.head;return[x+p[0],y+p[1]]}
  if(d.kind==='body'){const p=pose.hips;let dx=p[0],dy=p[1];for(const f of d.influences){const q=pose[f.channel],w=Math.exp(-(((x-f.center[0])/f.radius[0])**2+((y-f.center[1])/f.radius[1])**2))*f.gain;dx+=(q[0]-p[0])*w;dy+=(q[1]-p[1])*w}const cape=d.cape_support?this.smooth(...d.cape_support.x,x)*this.smooth(...d.cape_support.y,y):0;return[x+dx+pose.cape_wave[0]*cape,y+dy+pose.cape_wave[1]*cape]}
  const [a,b,c,e]=d.nodes,s=d.bands,u=1-this.smooth(s[0],s[1],y),v=this.smooth(s[2],s[3],y),weights=[u,(1-u)*(1-v),(1-u)*v],p=[x,y],upper=this.mapBone(p,a,b,pose),lower=this.mapBone(p,b,c,pose);let distal;
  if(d.distal==='fixed_orientation'){const z=pose[c];distal=[x+z[0],y+z[1]]}else distal=this.mapBone(p,c,e,pose,true);
  return[upper[0]*weights[0]+lower[0]*weights[1]+distal[0]*weights[2],upper[1]*weights[0]+lower[1]*weights[1]+distal[1]*weights[2]];
 }
 point(x,y,pose){const q=this.skinPoint(x,y,pose),o=pose.output_offset||[0,0];return[q[0]+o[0],q[1]+o[1]];}
 setViewport(width,height){if(!Number.isInteger(width)||!Number.isInteger(height)||width<this.definition.canvas[0]||height<this.definition.canvas[1])throw Error('Output viewport smaller than logical art');if(this.canvas.width!==width)this.canvas.width=width;if(this.canvas.height!==height)this.canvas.height=height;}
 draw(pose){const d=this.definition,required=d.kind==='chain'?d.nodes:d.kind==='head'?['head']:['hips','cape_wave',...d.influences.map(f=>f.channel)];for(const n of required)if(!Array.isArray(pose[n])||pose[n].length!==2||pose[n].some(v=>!Number.isFinite(v)))throw Error('Missing finite pose channel '+n);for(const v of Object.values(pose))if(!Array.isArray(v)||v.length!==2||v.some(x=>!Number.isFinite(x)))throw Error('Invalid pose vector');
  const gl=this.gl,data=[];this.vertices=[];for(const [x,y]of this.rest){const q=this.point(x,y,pose);this.vertices.push(q);data.push(q[0],q[1],x/d.canvas[0],y/d.canvas[1]);}
  gl.useProgram(this.program);gl.bindBuffer(gl.ARRAY_BUFFER,this.buffer);for(const [name,offset]of[['p',0],['uv',8]]){const loc=gl.getAttribLocation(this.program,name);gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,2,gl.FLOAT,false,16,offset)}gl.bindTexture(gl.TEXTURE_2D,this.texture);gl.uniform2f(gl.getUniformLocation(this.program,'size'),this.canvas.width,this.canvas.height);gl.viewport(0,0,this.canvas.width,this.canvas.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(data),gl.DYNAMIC_DRAW);gl.drawArrays(gl.TRIANGLES,0,this.rest.length);return this.vertices;
 }
}
if(typeof window!=='undefined')window.SpriteArticulatedLayer=SpriteArticulatedLayer;
