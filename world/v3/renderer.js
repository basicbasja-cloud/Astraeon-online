/* One shared depth buffer for authored spatial architecture and painted actors.
 * Canvas is used only to assemble existing illustrated actor frames into textures;
 * actors are alpha-tested world-space quads, never an independent screen layer.
 * Gameplay, saves, A* and combat remain consumers of the native world contract.
 */
import * as THREE from '../../vendor/three/three.module.min.js';
const V=window.AstraeonView;
const palette={stone:'#afa084',stoneLight:'#e0cc9e',cream:'#d4c29d',plaster:'#ebd5af',slate:'#345e80',blue:'#305d7c',gold:'#c49a48',wood:'#67432d',timber:'#5c3924',oak:'#9c6b3d',leaf:'#4b713a',leafLight:'#709143',grass:'#84926c',paving:'#c7b999',terracotta:'#b96d45',teal:'#447970',iron:'#465354',glass:'#496f78',clothBlue:'#4a83ad',clothOchre:'#e2b368',clothRose:'#bd7773',water:'#559ea8',flowers:'#d58b92',soil:'#aa9873'};
const materialCache=new Map();
const atlasTextures=new Map(),atlasImages=new Map(),textureLoads=[];
function texture(name,color){
 const c=document.createElement('canvas');c.width=c.height=256;const g=c.getContext('2d');g.fillStyle=palette[name]||(color?new THREE.Color().setRGB(...color).getStyle():'#b6a57f');g.fillRect(0,0,256,256);
 const random=(i)=>{const v=Math.sin(i*127.1+name.length*69.3)*43758.5453;return v-Math.floor(v)};
 // Original small painted material swatches: directional brush grain, weathered
 // ashlar, overlapped roof courses and timber grain; no perspective building cards.
 for(let i=0;i<3100;i++){g.fillStyle=random(i)>.45?'#fff1ce':'#302c21';g.globalAlpha=.025+random(i+1)*.07;g.fillRect(random(i+2)*256,random(i+3)*256,1+random(i+4)*7,.5+random(i+5)*2)}
 g.globalAlpha=1;
 if(['cream','stone','stoneLight','paving'].includes(name)){
  for(let row=0;row<8;row++)for(let col=-1;col<5;col++){
   const x=col*64+(row%2)*32,y=row*32;g.fillStyle=`rgba(69,62,44,${.09+random(row*11+col)*.07})`;g.fillRect(x,y,64,1.3);g.fillRect(x,y,1.2,32);
   g.fillStyle='#fff1ce3b';g.fillRect(x+2,y+2,61,1);g.strokeStyle='#74674a20';g.beginPath();g.moveTo(x+7,y+29);g.lineTo(x+28,y+27+random(row+col)*3);g.stroke();
  }
 }else if(['slate','blue','terracotta','teal'].includes(name)){
  for(let row=0;row<13;row++)for(let col=-1;col<12;col++){
   const x=col*24+(row%2)*12,y=row*20;g.fillStyle='#111e2c48';g.fillRect(x,y,24,2);g.fillRect(x,y,1,20);g.fillStyle='#ffebbc35';g.fillRect(x+2,y+3,21,1.5);g.fillStyle='#ffebbc12';g.fillRect(x+4,y+4,17,10);
  }
 }else if(['oak','timber','wood'].includes(name)){
  for(let i=0;i<32;i++){g.strokeStyle=i%4?'#170f0730':'#f3cf8444';g.beginPath();g.moveTo(i*8,0);g.bezierCurveTo(i*8+3,85,i*8-3,170,i*8,256);g.stroke()}
 }else if(name.startsWith('cloth')){
  g.globalAlpha=.23;g.fillStyle='#fff1d2';for(let x=0;x<256;x+=64)g.fillRect(x,0,24,256);g.globalAlpha=1;
 }else if(name==='water'){
  g.strokeStyle='#bce5d93b';for(let i=0;i<36;i++){g.beginPath();g.moveTo(random(i)*256,random(i+50)*256);g.lineTo(random(i)*256+15,random(i+50)*256+1);g.stroke()}
 }else if(name==='leaf'||name==='leafLight'){
  g.fillStyle=name==='leaf'?'#365532':'#577839';g.fillRect(0,0,256,256);
  for(let i=0;i<520;i++){
   const x=random(i+31)*256,y=random(i+92)*256,r=3+random(i+141)*7;g.fillStyle=['#879853','#728e45','#56763a','#375d32','#a6ad6a'][i%5];g.beginPath();g.ellipse(x,y,r,r*.48,random(i+4)*6.28,0,Math.PI*2);g.fill();g.strokeStyle='#c7c98844';g.beginPath();g.moveTo(x-r*.4,y);g.lineTo(x+r*.4,y-1);g.stroke();
  }
 }
 const t=new THREE.CanvasTexture(c);t.colorSpace=THREE.SRGBColorSpace;t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=4;return t;
}
function material(name,definition){
 const spec=definition?.texture,key=name+JSON.stringify(spec||'');if(materialCache.has(key))return materialCache.get(key);
 let map=texture(name,definition?.color);
 if(spec){
  const tileKey=spec.file+'/'+spec.tile;
  if(!atlasTextures.has(tileKey)){
   // Separate tile mip chains prevent adjacent atlas materials bleeding into
   // repeated lawns/roofs at gameplay distance. Artwork and authored UVs stay intact.
   const t=new THREE.Texture();t.colorSpace=THREE.SRGBColorSpace;t.wrapS=t.wrapT=THREE.RepeatWrapping;t.anisotropy=1;
   if(!atlasImages.has(spec.file))atlasImages.set(spec.file,new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>resolve(image);image.onerror=()=>reject(new Error('Could not load world material: '+spec.file));image.src=new URL('../../'+spec.file,import.meta.url).href}));
   textureLoads.push(atlasImages.get(spec.file).then(image=>{const [cols,rows]=spec.grid,w=image.naturalWidth/cols,h=image.naturalHeight/rows,c=document.createElement('canvas');c.width=Math.round(w);c.height=Math.round(h);c.getContext('2d').drawImage(image,(spec.tile%cols)*w,Math.floor(spec.tile/cols)*h,w,h,0,0,c.width,c.height);t.image=c;t.needsUpdate=true}));
   atlasTextures.set(tileKey,t);
  }map=atlasTextures.get(tileKey);
 }
 const m=new THREE.MeshBasicMaterial({map,vertexColors:true,side:THREE.DoubleSide,alphaTest:spec?.alphaCutoff||0});
 materialCache.set(key,m);return m;
}
function appendMesh(batch,part,lighting){
 const vs=part.vertices,sun=lighting?new THREE.Vector3(-lighting.sun.cast[0],-lighting.sun.cast[1],1).normalize():new THREE.Vector3(-.34,-.45,.82).normalize(),ambient=lighting?.ambient??.8,strength=lighting?.sun.strength??.23;
 for(const [faceIndex,face] of part.faces.entries()){
  const a=new THREE.Vector3(...vs[face[0]]),b=new THREE.Vector3(...vs[face[1]]),c=new THREE.Vector3(...vs[face[2]]),normal=b.clone().sub(a).cross(c.clone().sub(a)).normalize();
  const axis=Math.abs(normal.z)>.65?'xy':Math.abs(normal.x)>Math.abs(normal.y)?'yz':'xz';
  const shade=ambient+Math.max(0,normal.dot(sun))*strength;
  for(let j=1;j<face.length-1;j++)batch.owners?.push(part.objectId||part.id||'terrain');
  for(let j=1;j<face.length-1;j++)for(const i of [face[0],face[j],face[j+1]]){const v=vs[i],uv=part.uvs?.[faceIndex]?.[face.indexOf(i)];batch.position.push(...v);batch.normal.push(normal.x,normal.y,normal.z);batch.color.push(shade,shade*.99,shade*.96);batch.uv.push(...(uv||[axis==='yz'?v[1]/2.4:v[0]/2.4,axis==='xy'?v[1]/2.4:v[2]/2.4]))}
 }
}
function geometry(batch){const g=new THREE.BufferGeometry();for(const [name,size] of [['position',3],['normal',3],['uv',2],['color',3]])g.setAttribute(name,new THREE.Float32BufferAttribute(batch[name],size));g.computeBoundingSphere();return g}
class SpatialRenderer{
 constructor(source){
  this.source=source;this.actors=new Map();this.stats={backend:'three-webgl',frames:0,frameMs:0};this.active=false;
  this.entityIds=new WeakMap();this.nextEntityId=0;
  this.scene=new THREE.Scene();this.scene.background=new THREE.Color('#bbc9b2');
  this.camera=new THREE.Camera();this.camera.matrixAutoUpdate=false;this.camera.matrixWorld.identity();this.camera.matrixWorldInverse.identity();
  const batches=new Map(),add=(part)=>{if(part.visible===false)return;const name=part.material||'paving',key=name;if(!batches.has(key))batches.set(key,{material:name,position:[],normal:[],uv:[],color:[],owners:[]});appendMesh(batches.get(key),part,source.lighting)};
  const terrain=source.terrain,bounds=terrain.bounds,groundMesh={...terrain,vertices:terrain.vertices||[[bounds.minX,bounds.minY,terrain.elevation],[bounds.maxX,bounds.minY,terrain.elevation],[bounds.maxX,bounds.maxY,terrain.elevation],[bounds.minX,bounds.maxY,terrain.elevation]],faces:terrain.faces||[[0,1,2,3]]};add(groundMesh);
  for(const s of terrain.surfaces)add({...s,material:s.material||'paving',vertices:s.vertices||s.polygon.map(p=>[...p,.018]),faces:s.faces||[s.polygon.map((_,i)=>i)]});
  for(const o of source.objects)for(const p of o.parts)add({...p,objectId:o.id});
  for(const [key,batch] of batches){const name=batch.material,mesh=new THREE.Mesh(geometry(batch),material(name,source.materials?.[name]));mesh.name='static/'+key;mesh.userData.owners=batch.owners;this.scene.add(mesh)}
  this.whenReady=Promise.all(textureLoads);
  const spatial=window.AstraeonContent?.nativeWorld?.id===source.id?window.AstraeonContent.nativeWorld.spatial:window.AstraeonSpatialV3.compile(source);this.spatial=spatial;
  // Static authored sun shadow atlas: one draw, no dynamic shadow map or PBR.
  const c=document.createElement('canvas');c.width=c.height=1024;const g=c.getContext('2d'),b=terrain.bounds,sx=1024/(b.maxX-b.minX),sy=1024/(b.maxY-b.minY);
  g.fillStyle='#23352f';g.globalAlpha=source.lighting.sun.strength;g.beginPath();for(const s of spatial.shadowPolygons){s.polygon.forEach(([x,y],i)=>i?g.lineTo((x-b.minX)*sx,(y-b.minY)*sy):g.moveTo((x-b.minX)*sx,(y-b.minY)*sy));g.closePath()}g.fill();
  this.shadowPixels=g.getImageData(0,0,1024,1024).data;this.shadowBounds=b;
  const tex=new THREE.CanvasTexture(c);tex.flipY=false;tex.colorSpace=THREE.SRGBColorSpace;
  // Project the static atlas onto the authored walkable elevations. A flat
  // decal disappears beneath terraces and cannot ground their architecture.
  const shadowPositions=[],shadowUVs=[],shadowVertex=(x,y,z)=>{shadowPositions.push(x,y,z);shadowUVs.push((x-b.minX)/(b.maxX-b.minX),(y-b.minY)/(b.maxY-b.minY))};
  // Receivers follow the land outline; a bounds rectangle would project a
  // floating shadow sheet over the water outside the defended bank.
  const receive=part=>{for(const face of part.faces)for(let j=1;j<face.length-1;j++)for(const i of [face[0],face[j],face[j+1]]){const v=part.vertices[i];shadowVertex(v[0],v[1],v[2]+.028)}};
  receive(groundMesh);
  if(terrain.walkablePolygon)for(const surface of terrain.surfaces.filter(s=>s.walkable&&s.vertices?.some(v=>!window.AstraeonSpatialV3.pointIn({x:v[0],y:v[1]},terrain.walkablePolygon))))receive(surface);
  const raised=terrain.surfaces.filter(s=>s.walkable&&s.vertices?.some(v=>v[2]>terrain.elevation+.1)).flatMap(s=>s.vertices);
  if(raised.length){const minX=Math.min(...raised.map(v=>v[0])),maxX=Math.max(...raised.map(v=>v[0])),minY=Math.min(...raised.map(v=>v[1])),maxY=Math.max(...raised.map(v=>v[1]));
   for(let y=minY;y<maxY;y+=.25)for(let x=minX;x<maxX;x+=.25){if(spatial.elevationAt(x+.125,y+.125)<terrain.elevation+.03)continue;
    for(const [dx,dy] of [[0,0],[.25,0],[.25,.25],[0,0],[.25,.25],[0,.25]])shadowVertex(x+dx,y+dy,spatial.elevationAt(x+dx,y+dy)+.028);
   }
  }
  const shadowGeo=new THREE.BufferGeometry();shadowGeo.setAttribute('position',new THREE.Float32BufferAttribute(shadowPositions,3));shadowGeo.setAttribute('uv',new THREE.Float32BufferAttribute(shadowUVs,2));shadowGeo.computeBoundingSphere();
  // The inherited screen basis reflects winding. Receiver decals must follow
  // the same double-sided policy as the authored geometry and picking floor.
  const shadow=new THREE.Mesh(shadowGeo,new THREE.MeshBasicMaterial({map:tex,transparent:true,depthWrite:false,side:THREE.DoubleSide,forceSinglePass:true,polygonOffset:true,polygonOffsetFactor:-1,polygonOffsetUnits:-1}));this.scene.add(shadow);
  this.staticNodes=[...this.scene.children];
  // Upright illustrated planes: a pixel of height is real vertical world
  // height, not a camera-facing lean into the wall behind the actor. The XY
  // right vector has zero projected vertical displacement. These bases retain
  // the artwork's screen shape while its head/feet participate in spatial depth.
  const {xx,xy,yx,yy}=V.basis,det=xx*yy-yx*xy;
  this.right=new THREE.Vector3(yy/det,-xy/det,0);this.up=new THREE.Vector3(0,0,1/35);
  this.raycaster=new THREE.Raycaster();
  const floor={position:[],normal:[],uv:[],color:[]};
  appendMesh(floor,groundMesh);
  for(const s of terrain.surfaces.filter(s=>s.walkable&&s.vertices))appendMesh(floor,s);
  this.navFloor=new THREE.Mesh(geometry(floor),new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));this.navFloor.updateMatrixWorld();
 }
 mount(overlay){
  this.overlay=overlay;
  try{this.renderer=new THREE.WebGLRenderer({antialias:false,alpha:false,powerPreference:'low-power'});}catch(error){throw new Error('Spatial world requires WebGL: '+error.message)}
  const gl=this.renderer.getContext(),debug=gl.getExtension('WEBGL_debug_renderer_info'),device=debug?gl.getParameter(debug.UNMASKED_RENDERER_WEBGL):'';
  this.stats.device=device;this.stats.software=/SwiftShader|llvmpipe|software/i.test(device);this.stats.pixelRatio=this.stats.software?.75:Math.min(devicePixelRatio||1,1.5);
  // Software WebGL is fill-rate limited in headless/VM browsers. Keep the real
  // device budget independent; neither path relies on expensive anisotropic filtering.
  if(this.stats.software)this.stats.pixelRatio=.5;
  for(const m of materialCache.values()){m.map.anisotropy=1;m.map.minFilter=THREE.LinearMipmapNearestFilter;m.map.needsUpdate=true}
  this.renderer.outputColorSpace=THREE.SRGBColorSpace;this.renderer.setPixelRatio(this.stats.pixelRatio);
  this.renderer.info.autoReset=false;
  this.canvas=this.renderer.domElement;this.canvas.id='spatial-world';this.canvas.setAttribute('aria-hidden','true');this.canvas.style.cssText='position:absolute;inset:0;width:100%;height:100%;z-index:0;pointer-events:none';overlay.before(this.canvas);overlay.style.background='transparent';overlay.parentElement.classList.add('spatial-stage');this.active=true;
 }
 begin(camera,w,h,zoom,anchorY){
  this.frameStarted=performance.now();this.assemblyMs=0;
  if(!this.renderer)return;this.active=true;this.canvas.hidden=false;
  this.width=w;this.height=h;this.zoom=zoom;this.anchorY=anchorY;
  if(this.canvas.clientWidth!==w||this.canvas.clientHeight!==h||this.lastSize!==w+'x'+h){this.renderer.setSize(w,h,false);this.lastSize=w+'x'+h}
  // Reusing rasterized geometry must translate by whole device pixels. Snap
  // only the software camera to its actual (possibly odd-sized) drawing
  // buffer grid; simulation, navigation and the hardware camera remain smooth.
  const size=this.renderer.getDrawingBufferSize(new THREE.Vector2()),gridX=zoom*size.x/w,gridY=zoom*size.y/h;
  this.focus=this.stats.software?{x:Math.round(camera.x*gridX)/gridX,y:Math.round(camera.y*gridY)/gridY}:{...camera};
  const cx=this.focus.x,cy=this.focus.y,s=zoom;
  this.camera.projectionMatrix.set(96*s/w,-64*s/w,0,-2*cx*s/w,-28*s/h,-44*s/h,70*s/h,2*cy*s/h+1-2*anchorY,-.0056,-.0084,-.00752,.25,0,0,0,1);
  this.camera.projectionMatrixInverse.copy(this.camera.projectionMatrix).invert();this.camera.updateMatrixWorld();
  for(const a of this.actors.values())a.mesh.visible=a.shadow.visible=false;
 }
 actor(id,t,draw,{alpha=1,shadowAlpha=alpha,radius=.4}={}){
  const assemblyStarted=performance.now();
  const screen=V.project(t.position.x,t.position.y),sx=this.width/2+(screen.x-this.focus.x)*this.zoom,sy=this.height*this.anchorY+(screen.y-this.focus.y-(t.position.z||0)*35)*this.zoom;
  if(sx< -150||sx>this.width+150||sy< -80||sy>this.height+230)return;
  let a=this.actors.get(id);
  if(!a){
   const canvas=document.createElement('canvas');canvas.width=canvas.height=256;const ctx=canvas.getContext('2d',{willReadFrequently:true}),tex=new THREE.CanvasTexture(canvas);tex.colorSpace=THREE.SRGBColorSpace;tex.generateMipmaps=false;tex.minFilter=THREE.LinearFilter;
   const geo=new THREE.BufferGeometry(),positions=[];
   for(const [x,y] of [[-128,-32],[128,-32],[128,224],[-128,224]])positions.push(...this.right.clone().multiplyScalar(x).addScaledVector(this.up,y).toArray());
   geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geo.setAttribute('uv',new THREE.Float32BufferAttribute([0,0,1,0,1,1,0,1],2));geo.setIndex([0,1,2,0,2,3]);geo.computeBoundingSphere();
   const mat=new THREE.MeshBasicMaterial({map:tex,alphaTest:.10,transparent:true,depthWrite:true,side:THREE.DoubleSide,forceSinglePass:true});const mesh=new THREE.Mesh(geo,mat);mesh.name='actor/'+id;this.scene.add(mesh);
   const shadow=new THREE.Mesh(new THREE.CircleGeometry(radius,20),new THREE.MeshBasicMaterial({color:'#23352f',transparent:true,opacity:.22,depthWrite:false,side:THREE.DoubleSide,forceSinglePass:true}));shadow.scale.set(1,1.1,1);this.scene.add(shadow);
   a={canvas,ctx,tex,mesh,shadow};this.actors.set(id,a);
  }
  const p=t.position,prior=V.zoom;V.zoom=1;a.ctx.clearRect(0,0,256,256);a.ctx.save();a.ctx.globalAlpha=alpha;
  const iso=(x,y,z=0)=>{const q=V.project(x-p.x,y-p.y);return{x:128+q.x,y:224+q.y-z+(p.z||0)*35}};
  let sockets;this.assemblingActor=true;try{sockets=draw(a.ctx,iso)}finally{this.assemblingActor=false;a.ctx.restore();V.zoom=prior}
  const b=this.shadowBounds,tx=Math.floor((p.x-b.minX)/(b.maxX-b.minX)*1024),ty=Math.floor((p.y-b.minY)/(b.maxY-b.minY)*1024),shade=tx>=0&&tx<1024&&ty>=0&&ty<1024?this.shadowPixels[(ty*1024+tx)*4+3]/255:0;
  a.mesh.material.color.setRGB(1-shade*.4,1-shade*.35,1-shade*.3);
  a.tex.needsUpdate=true;a.mesh.position.set(p.x,p.y,p.z||0);a.mesh.visible=true;a.shadow.position.set(p.x+.08,p.y+.08,(p.z||0)+.035);a.shadow.material.opacity=.22*shadowAlpha;a.shadow.visible=shadowAlpha>.05;
  this.assemblyMs+=performance.now()-assemblyStarted;return sockets;
 }
 cachedWorld(){
  const r=this.renderer,pad=192,ratio=r.getPixelRatio(),w=this.width,h=this.height,size=r.getDrawingBufferSize(new THREE.Vector2()),padPixels=Math.round(pad*ratio),cw=w*(size.x+padPixels*2)/size.x,ch=h*(size.y+padPixels*2)/size.y,px=(cw-w)/2,py=(ch-h)/2,key=[w,h,ratio,this.zoom,this.anchorY].join('/');
  let c=this.staticCache;
  if(!c||c.key!==key){
   if(c){c.target.dispose();c.material.dispose();c.quad.geometry.dispose()}
   const target=new THREE.WebGLRenderTarget(size.x+padPixels*2,size.y+padPixels*2,{minFilter:THREE.LinearFilter,magFilter:THREE.LinearFilter,depthBuffer:true});target.texture.colorSpace=THREE.SRGBColorSpace;target.depthTexture=new THREE.DepthTexture(target.width,target.height,THREE.UnsignedIntType);
   const material=new THREE.ShaderMaterial({uniforms:{colorMap:{value:target.texture},depthMap:{value:target.depthTexture},viewSize:{value:new THREE.Vector2(w,h)},cacheSize:{value:new THREE.Vector2(cw,ch)},offset:{value:new THREE.Vector2(pad,pad)}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position.xy,0.0,1.0);}',fragmentShader:'uniform sampler2D colorMap;uniform sampler2D depthMap;uniform vec2 viewSize,cacheSize,offset;varying vec2 vUv;void main(){vec2 p=(vUv*viewSize+offset)/cacheSize;gl_FragColor=texture2D(colorMap,p);gl_FragDepth=texture2D(depthMap,p).r;\n#include <colorspace_fragment>\n}',depthTest:true,depthWrite:true,depthFunc:THREE.AlwaysDepth,toneMapped:false});
   const quad=new THREE.Mesh(new THREE.PlaneGeometry(2,2),material);quad.frustumCulled=false;const scene=new THREE.Scene();scene.add(quad);c=this.staticCache={key,target,material,quad,scene,camera:new THREE.Camera(),focus:null};
  }
  const dx=c.focus?(this.focus.x-c.focus.x)*this.zoom:Infinity,dy=c.focus?(this.focus.y-c.focus.y)*this.zoom:Infinity;
  if(!c.focus||Math.max(Math.abs(dx),Math.abs(dy))>pad-40){
   const matrix=this.camera.projectionMatrix.clone(),actors=[...this.actors.values()].map(a=>[a,a.mesh.visible,a.shadow.visible]);
   try{
    for(const [a] of actors)a.mesh.visible=a.shadow.visible=false;
    this.camera.projectionMatrix.set(96*this.zoom/cw,-64*this.zoom/cw,0,-2*this.focus.x*this.zoom/cw,-28*this.zoom/ch,-44*this.zoom/ch,70*this.zoom/ch,2*this.focus.y*this.zoom/ch+1-2*(h*this.anchorY+py)/ch,-.0056,-.0084,-.00752,.25,0,0,0,1);
    r.setRenderTarget(c.target);r.render(this.scene,this.camera);c.focus={...this.focus};this.stats.cacheUpdates=(this.stats.cacheUpdates||0)+1;
   }finally{this.camera.projectionMatrix.copy(matrix);for(const [a,visible,shadow] of actors){a.mesh.visible=visible;a.shadow.visible=shadow}r.setRenderTarget(null)}
  }
  c.material.uniforms.offset.value.set(px+(this.focus.x-c.focus.x)*this.zoom,py-(this.focus.y-c.focus.y)*this.zoom);
  // The cached static depth is written into the SAME framebuffer as actor
  // quads. This is a color/depth reuse optimization, not an actor overlay.
  r.render(c.scene,c.camera);const background=this.scene.background;this.scene.background=null;r.autoClear=false;
  const visibility=this.staticNodes.map(o=>o.visible);try{for(const o of this.staticNodes)o.visible=false;r.render(this.scene,this.camera)}finally{this.staticNodes.forEach((o,i)=>o.visible=visibility[i]);this.scene.background=background;r.autoClear=true}
 }
 end(){const started=performance.now();this.renderer.info.reset();if(this.stats.software)this.cachedWorld();else this.renderer.render(this.scene,this.camera);this.stats.frames++;this.stats.frameMs=this.stats.frameMs*.95+(performance.now()-started)*.05;this.stats.assemblyMs=this.assemblyMs;this.stats.totalMs=performance.now()-this.frameStarted;this.stats.calls=this.renderer.info.render.calls;this.stats.triangles=this.renderer.info.render.triangles;this.stats.textures=this.renderer.info.memory.textures;this.stats.staticDepthCache=!!this.stats.software;}
 hide(){if(this.canvas)this.canvas.hidden=true;this.active=false;}
 idFor(entity,prefix){if(!this.entityIds.has(entity))this.entityIds.set(entity,prefix+'/'+(++this.nextEntityId));return this.entityIds.get(entity)}
 screenRay(x,y){const near=new THREE.Vector3(x/this.width*2-1,1-y/this.height*2,-1).unproject(this.camera),far=new THREE.Vector3(x/this.width*2-1,1-y/this.height*2,1).unproject(this.camera);this.raycaster.set(near,far.sub(near).normalize());return this.raycaster}
 screenToWorld(x,y){const hit=this.screenRay(x,y).intersectObject(this.navFloor,false)[0];return hit?{x:hit.point.x,y:hit.point.y}:null}
 pickActor(x,y){
  for(const hit of this.screenRay(x,y).intersectObjects(this.scene.children,false)){
   if(!hit.object.visible||hit.object===this.navFloor)continue;
   const id=hit.object.name;
   if(id.startsWith('actor/')){const a=this.actors.get(id.slice(6));if(!a||!hit.uv)continue;const px=Math.min(255,Math.max(0,Math.floor(hit.uv.x*256))),py=Math.min(255,Math.max(0,Math.floor((1-hit.uv.y)*256)));if(a.ctx.getImageData(px,py,1,1).data[3]<26)continue;return id.slice(6)}
   if(id.startsWith('static/')){
    const m=hit.object.material;if(m.alphaTest&&hit.uv&&m.map.image){
     if(!m.userData.alphaPixels){const image=m.map.image,ctx=image.getContext('2d');m.userData.alphaPixels={data:ctx.getImageData(0,0,image.width,image.height).data,width:image.width,height:image.height}}
     const p=m.userData.alphaPixels,u=((hit.uv.x%1)+1)%1,v=((hit.uv.y%1)+1)%1,x=Math.min(p.width-1,Math.floor(u*p.width)),y=Math.min(p.height-1,Math.floor((1-v)*p.height));
     if(p.data[(y*p.width+x)*4+3]/255<m.alphaTest)continue;
    }return 'object/'+hit.object.userData.owners[hit.faceIndex];
   }
  }return null;
 }
 snapshot(){return {...this.stats,actors:[...this.actors].filter(([,a])=>a.mesh.visible).map(([id,a])=>({id,position:a.mesh.position.toArray(),depthTest:a.mesh.material.depthTest,depthWrite:a.mesh.material.depthWrite}))};}
}
window.AstraeonSpatialRenderer={SpatialRenderer,THREE};
if(window.AstraeonContent?.nativeWorld?.id==='wayfarer-spatial'&&new URLSearchParams(location.search).get('renderer')!=='canvas')window.AstraeonSpatialView=new SpatialRenderer(window.AstraeonContent.nativeWorld.spatial.scene);
