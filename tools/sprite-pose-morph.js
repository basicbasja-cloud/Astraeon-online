/* Painted-key 2D mesh interpolation. Rest cages are authored, never image fits. */
'use strict';
class SpritePoseMorph {
 constructor(canvas,images,contract){
  this.canvas=canvas;this.contract=contract;canvas.width=contract.width;canvas.height=contract.height;
  const gl=this.gl=canvas.getContext('webgl',{alpha:true,premultipliedAlpha:false,antialias:false,preserveDrawingBuffer:true});if(!gl)throw Error('WebGL unavailable');
  const shader=(type,src)=>{let s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s};
  let p=this.program=gl.createProgram();gl.attachShader(p,shader(gl.VERTEX_SHADER,'attribute vec2 p;attribute vec2 a;attribute vec2 b;uniform vec2 size;varying vec2 u;varying vec2 v;void main(){gl_Position=vec4(p.x/size.x*2.-1.,1.-p.y/size.y*2.,0.,1.);u=a;v=b;}'));gl.attachShader(p,shader(gl.FRAGMENT_SHADER,'precision highp float;uniform sampler2D artA;uniform sampler2D artB;uniform float blend;varying vec2 u;varying vec2 v;void main(){vec4 x=texture2D(artA,u),y=texture2D(artB,v);float alpha=mix(x.a,y.a,blend);vec3 prem=mix(x.rgb*x.a,y.rgb*y.a,blend);gl_FragColor=vec4(alpha>0.?prem/alpha:vec3(0.),alpha);}'));gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));gl.useProgram(p);gl.uniform2f(gl.getUniformLocation(p,'size'),canvas.width,canvas.height);gl.uniform1i(gl.getUniformLocation(p,'artA'),0);gl.uniform1i(gl.getUniformLocation(p,'artB'),1);this.blend=gl.getUniformLocation(p,'blend');
  this.buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,this.buffer);for(const[name,offset]of[['p',0],['a',8],['b',16]]){let n=gl.getAttribLocation(p,name);gl.enableVertexAttribArray(n);gl.vertexAttribPointer(n,2,gl.FLOAT,false,24,offset)}
  this.textures=images.map(im=>{if(im.width!==canvas.width||im.height!==canvas.height)throw Error('Wrong texture dimensions');let t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL,false);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,im);return t});
  for(let row of contract.cage_y)if(row.length!==contract.cage_y[0].length||row[0]!==0||row.at(-1)!==canvas.height||row.some((v,i)=>!Number.isFinite(v)||(i&&v<=row[i-1])))throw Error('Invalid source cage');
 }
 draw(sample){
  const c=this.contract,gl=this.gl,a=c.cage_y[sample.a],b=c.cage_y[sample.b],f=sample.f;if(!a||!b||!Number.isFinite(f)||f<0||f>1)throw Error('Invalid morph sample');
  const target=a.map((y,i)=>y*(1-f)+b[i]*f),data=[];let minRatio=Infinity,maxRatio=0;
  for(let j=0;j<target.length-1;j++){
   minRatio=Math.min(minRatio,(target[j+1]-target[j])/(a[j+1]-a[j]),(target[j+1]-target[j])/(b[j+1]-b[j]));maxRatio=Math.max(maxRatio,(target[j+1]-target[j])/(a[j+1]-a[j]),(target[j+1]-target[j])/(b[j+1]-b[j]));
   for(let x=0;x<c.width;x+=c.grid_px){let xr=Math.min(c.width,x+c.grid_px);for(let[xx,row]of[[x,j],[xr,j],[x,j+1],[xr,j],[xr,j+1],[x,j+1]])data.push(xx,target[row],xx/c.width,a[row]/c.height,xx/c.width,b[row]/c.height)}
  }
  gl.useProgram(this.program);gl.viewport(0,0,c.width,c.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.disable(gl.BLEND);for(let i=0;i<2;i++){gl.activeTexture(gl.TEXTURE0+i);gl.bindTexture(gl.TEXTURE_2D,this.textures[i?sample.b:sample.a])}gl.uniform1f(this.blend,f);gl.bindBuffer(gl.ARRAY_BUFFER,this.buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(data),gl.DYNAMIC_DRAW);gl.drawArrays(gl.TRIANGLES,0,data.length/6);return{min_triangle_area_ratio:minRatio,max_triangle_area_ratio:maxRatio,target_cage:target};
 }
}
if(typeof window!=='undefined')window.SpritePoseMorph=SpritePoseMorph;
