/* Original small-motion 2D texture renderer. Static rest weights; no frame fitting. */
'use strict';
class SpriteMesh {
 constructor(canvas,image,adapter){
  if(!adapter||!Number.isInteger(adapter.width)||adapter.width<=0||!Number.isInteger(adapter.height)||adapter.height<=0||!Number.isInteger(adapter.grid_px)||adapter.grid_px<=0||!Array.isArray(adapter.bands)||adapter.bands.length<2)throw Error('Invalid mesh dimensions or rest bands');
  if(adapter.bands[0].y!==0||adapter.bands.at(-1).y!==adapter.height||adapter.bands.some((v,i)=>!Number.isFinite(v.y)||typeof v.channel!=='string'||(i&&v.y<=adapter.bands[i-1].y)))throw Error('Rest bands must cover the canvas in order');
  if((image.naturalWidth||image.width)!==adapter.width||(image.naturalHeight||image.height)!==adapter.height)throw Error('Texture size differs from declared rest space');
  for(const i of adapter.influences||[])if(!Array.isArray(i.center)||i.center.length!==2||i.center.some(v=>!Number.isFinite(v))||!Array.isArray(i.radius)||i.radius.length!==2||i.radius.some(v=>!Number.isFinite(v)||v<=0)||!Array.isArray(i.support_y)||i.support_y.length!==4||i.support_y.some((v,j)=>!Number.isFinite(v)||(j&&v<=i.support_y[j-1])))throw Error('Invalid authored influence');
  this.canvas=canvas;this.image=image;this.adapter=adapter;canvas.width=adapter.width;canvas.height=adapter.height;
  const gl=this.gl=canvas.getContext('webgl',{alpha:true,premultipliedAlpha:false,antialias:false,preserveDrawingBuffer:true});if(!gl)throw Error('WebGL unavailable');
  const shader=(type,source)=>{const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s};
  const p=this.program=gl.createProgram();gl.attachShader(p,shader(gl.VERTEX_SHADER,'attribute vec2 p;attribute vec2 uv;uniform vec2 size;varying vec2 t;void main(){gl_Position=vec4(p.x/size.x*2.-1.,1.-p.y/size.y*2.,0.,1.);t=uv;}'));gl.attachShader(p,shader(gl.FRAGMENT_SHADER,'precision mediump float;uniform sampler2D art;varying vec2 t;void main(){gl_FragColor=texture2D(art,t);}'));gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));gl.useProgram(p);gl.uniform2f(gl.getUniformLocation(p,'size'),canvas.width,canvas.height);
  this.buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,this.buffer);for(const [name,offset]of[['p',0],['uv',8]]){const loc=gl.getAttribLocation(p,name);gl.enableVertexAttribArray(loc);gl.vertexAttribPointer(loc,2,gl.FLOAT,false,16,offset)}
  this.texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,this.texture);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,false);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,image);gl.disable(gl.BLEND);this.rest=[];
  const xs=[...new Set([0,canvas.width,...Array.from({length:Math.ceil(canvas.width/adapter.grid_px)},(_,i)=>Math.min(canvas.width,i*adapter.grid_px))])].sort((a,b)=>a-b),ys=[...new Set([0,canvas.height,...adapter.bands.map(x=>x.y),...Array.from({length:Math.ceil(canvas.height/adapter.grid_px)},(_,i)=>Math.min(canvas.height,i*adapter.grid_px))])].sort((a,b)=>a-b);
  for(let j=0;j<ys.length-1;j++)for(let i=0;i<xs.length-1;i++){let a=[xs[i],ys[j]],b=[xs[i+1],ys[j]],c=[xs[i],ys[j+1]],d=[xs[i+1],ys[j+1]];this.rest.push(a,b,c,b,d,c)}
 }
 point(x,y,pose){
  const a=this.adapter;let bands=a.bands,left=bands[0],right=bands.at(-1);
  for(let i=0;i<bands.length-1;i++)if(y>=bands[i].y&&y<=bands[i+1].y){left=bands[i];right=bands[i+1];break}
  const t=right.y===left.y?0:Math.max(0,Math.min(1,(y-left.y)/(right.y-left.y))),get=n=>pose[n]||[0,0],u=get(left.channel),v=get(right.channel);let dx=u[0]*(1-t)+v[0]*t,dy=u[1]*(1-t)+v[1]*t;
  // Every limb influence is an authored smooth rest-space support, never image matching.
  for(const influence of a.influences||[]){const q=pose[influence.channel]||[0,0],s=influence.support_y,fade=Math.max(0,Math.min(1,(y-s[0])/(s[1]-s[0]),(s[3]-y)/(s[3]-s[2]))),w=fade*Math.exp(-(((x-influence.center[0])/influence.radius[0])**2+((y-influence.center[1])/influence.radius[1])**2));dx+=q[0]*w;dy+=q[1]*w}
  return [x+dx,y+dy];
 }
 draw(pose={}){for(const v of Object.values(pose))if(!Array.isArray(v)||v.length!==2||v.some(x=>!Number.isFinite(x)))throw Error('Invalid pose vector');const gl=this.gl,data=[];this.vertices=[];for(const [x,y]of this.rest){const q=this.point(x,y,pose);this.vertices.push(q);data.push(q[0],q[1],x/this.canvas.width,y/this.canvas.height)}gl.viewport(0,0,this.canvas.width,this.canvas.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.bindBuffer(gl.ARRAY_BUFFER,this.buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(data),gl.DYNAMIC_DRAW);gl.drawArrays(gl.TRIANGLES,0,this.rest.length);return this.vertices;}
 dispose(){const gl=this.gl;gl.deleteTexture(this.texture);gl.deleteBuffer(this.buffer);gl.deleteProgram(this.program);}
}
if(typeof window!=='undefined')window.SpriteMesh=SpriteMesh;
