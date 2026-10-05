/* One shared depth buffer for authored spatial architecture and painted actors.
 * Canvas is used only to assemble existing illustrated actor frames into textures;
 * actors are alpha-tested world-space quads, never an independent screen layer.
 * Gameplay, saves, A* and combat remain consumers of the native world contract.
 */
import * as THREE from '../../vendor/three/three.module.min.js';
const V=window.AstraeonView;
const palette={stone:'#aaa99b',stoneLight:'#e0cc9e',cream:'#d4c29d',plaster:'#ebd5af',slate:'#345e80',blue:'#305d7c',gold:'#c49a48',wood:'#67432d',timber:'#5c3924',oak:'#9c6b3d',leaf:'#4b713a',leafLight:'#709143',grass:'#84a564',paving:'#cec7b4',terracotta:'#b96d45',teal:'#447970',iron:'#465354',glass:'#496f78',clothBlue:'#4a83ad',clothOchre:'#e2b368',clothRose:'#bd7773',water:'#559ea8',flowers:'#d58b92',soil:'#aa9873'};
Object.assign(palette,{civicIvory:'#e8daba',civicShadow:'#b8b9a8',civicSlate:'#254c72',civicSlateLight:'#36678d',civicGlass:'#345c73',civicGlassLight:'#75b6c5',civicGold:'#d9b35e',civicDoor:'#493021',streetIvory:'#dfcda5',streetSlate:'#345e80',streetOchre:'#c78f50',statueIvory:'#eee3c9',gardenGrass:'#82936a'});
const materialCache=new Map();
Object.assign(palette,{cityPaving:'#c9c2ac',avenuePaving:'#beb6a2'});
Object.assign(palette,{bankStone:'#7d8785',bankStoneLight:'#a3a99b',wallStone:'#b8b1a0',wallCap:'#d8c9aa',roofMoss:'#3c6b60',roofClay:'#aa6240',roofBlue:'#345f80',foliageCutout:'#4e7b3d'});
const atlasTextures=new Map(),atlasImages=new Map(),textureLoads=[];
const occludingOwners={value:new THREE.Vector4(0,0,0,0)};
function texture(name,color){
 const c=document.createElement('canvas');c.width=c.height=256;const g=c.getContext('2d');g.fillStyle=palette[name]||(color?new THREE.Color().setRGB(...color).getStyle():'#b6a57f');g.fillRect(0,0,256,256);
 const random=(i)=>{const v=Math.sin(i*127.1+name.length*69.3)*43758.5453;return v-Math.floor(v)};
 // Original small painted material swatches: directional brush grain, weathered
 // ashlar, overlapped roof courses and timber grain; no perspective building cards.
 for(let i=0;i<220;i++){g.fillStyle=random(i)>.45?'#fff1ce':'#302c21';g.globalAlpha=.015+random(i+1)*.025;g.fillRect(random(i+2)*256,random(i+3)*256,12+random(i+4)*24,4+random(i+5)*9)}
 g.globalAlpha=1;
 if(name==='avenuePaving'){
  // Rounded, broad cobbles distinguish through streets from civic flagstones.
  // Quiet color shifts and shallow seams keep the playable route readable.
  for(let row=0;row<6;row++){
   let x=-48+(row%2)*22;const y=row*256/6;
   for(let col=0;col<8;col++){
    const width=[43,47,39,46][(row+col)%4],gap=1.8;
    g.beginPath();g.roundRect(x+gap,y+gap,width-gap*2,256/6-gap*2,7);
    g.fillStyle=`rgba(${random(row*23+col)>.48?'255,244,218':'75,70,57'},0.06)`;g.fill();g.strokeStyle='#655f503b';g.lineWidth=1.2;g.stroke();
    g.strokeStyle='#fff0d628';g.beginPath();g.moveTo(x+8,y+3);g.lineTo(x+width-8,y+3);g.stroke();x+=width;
   }
  }
 }else if(name==='cityPaving'){
  // Broad dressed flagstones, at a readable person-relative scale. Unequal
  // lengths and softened corners avoid the miniature, perfectly regular grid.
  const lengths=[61,71,56,68];
  for(let row=0;row<4;row++){
   let x=-256+(row%2)*31;const y=row*64;
   for(let col=0;col<13;col++){
    const width=lengths[(row+col)%4],cut=3+random(row*19+col)*3;
    g.beginPath();g.moveTo(x+cut,y+1.5);g.lineTo(x+width-cut,y+1.5);g.lineTo(x+width-1.5,y+cut);g.lineTo(x+width-1.5,y+64-cut);g.lineTo(x+width-cut,y+62.5);g.lineTo(x+cut,y+62.5);g.lineTo(x+1.5,y+64-cut);g.lineTo(x+1.5,y+cut);g.closePath();
    g.fillStyle=`rgba(${random(row*17+col)>.5?'255,245,222':'81,76,61'},0.065)`;g.fill();g.strokeStyle='#6b6a5635';g.lineWidth=1.5;g.stroke();
    g.fillStyle='#fff5dd30';g.fillRect(x+cut,y+2,width-cut*2,1.2);x+=width;
   }
  }
 }else if(['cream','stone','stoneLight','paving','civicIvory','civicShadow','streetIvory','wallStone','wallCap','bankStone','bankStoneLight'].includes(name)){
  for(let row=0;row<8;row++)for(let col=-1;col<5;col++){
   const x=col*64+(row%2)*32,y=row*32;g.fillStyle=`rgba(69,62,44,${.09+random(row*11+col)*.07})`;g.fillRect(x,y,64,1.3);g.fillRect(x,y,1.2,32);
   g.fillStyle='#fff1ce3b';g.fillRect(x+2,y+2,61,1);g.strokeStyle='#74674a20';g.beginPath();g.moveTo(x+7,y+29);g.lineTo(x+28,y+27+random(row+col)*3);g.stroke();
  }
 }else if(['slate','blue','terracotta','teal','civicSlate','civicSlateLight','streetSlate','roofMoss','roofClay','roofBlue'].includes(name)){
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
const waterTime={value:0};
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
 // MSAA coverage softens cutout foliage silhouettes while retaining depth.
 if(spec?.alphaCutoff)m.alphaToCoverage=true;
 if(name==='riverFoam'){m.transparent=true;m.depthWrite=false;m.forceSinglePass=true}
 // Normalize new painted swatches around their linear mean: tile seams and
 // grain retain contrast while the authored palette still owns the building hue.
 // Older atlases retain their existing mix and foliage/cutout behavior.
 {
  const painted=spec&&name!=='bannerSilk';
  const base=palette[name]?new THREE.Color(palette[name]):definition?.color?new THREE.Color().setRGB(...definition.color):new THREE.Color('#b6a57f'),detail=spec?.paletteDetail??(name==='water'?.18:spec?.alphaCutoff ? .42 :/glass/i.test(name)?.48:/wood|oak|timber/i.test(name)?.30:/slate|roof|terracotta/i.test(name)?.32:.24),mean=spec?.meanLinearRGB;
  m.onBeforeCompile=shader=>{
   shader.uniforms.paintBase={value:base};shader.uniforms.paintDetail={value:detail};shader.uniforms.paintMean={value:new THREE.Vector3(...(mean||[1,1,1]))};shader.uniforms.occludingOwners=occludingOwners;
   if(spec?.ripple){shader.uniforms.waterTime=waterTime;shader.uniforms.rippleSettings={value:new THREE.Vector3(spec.ripple.frequency,spec.ripple.speed,spec.ripple.amplitude)}}
   shader.vertexShader='attribute float ownerId;varying float paintOwner;varying vec3 paintPosition;\n'+shader.vertexShader;
   shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\npaintOwner=ownerId;paintPosition=(modelMatrix*vec4(position,1.0)).xyz;');
   shader.fragmentShader='varying float paintOwner;uniform vec4 occludingOwners;varying vec3 paintPosition;uniform vec3 paintBase;uniform vec3 paintMean;uniform float paintDetail;\n'+shader.fragmentShader;
   if(spec?.ripple){
    shader.vertexShader='varying vec2 nativeWaterUV;\n'+shader.vertexShader;
    shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nnativeWaterUV=uv;');
    shader.fragmentShader='varying vec2 nativeWaterUV;uniform float waterTime;uniform vec3 rippleSettings;\n'+shader.fragmentShader;
   }
   if(painted)shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',`#include <map_fragment>
    float wash=1.0+0.035*sin(paintPosition.x*0.49+sin(paintPosition.y*0.27))*sin(paintPosition.y*0.38+paintPosition.z*0.41);
    ${mean?'vec3 variation=clamp(diffuseColor.rgb/paintMean,vec3(0.45),vec3(1.6));diffuseColor.rgb=paintBase*mix(vec3(1.0),variation,paintDetail)*wash;':'diffuseColor.rgb=mix(paintBase,diffuseColor.rgb,paintDetail)*wash;'} `);
   if(spec?.ripple)shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
    float radial=length((nativeWaterUV-vec2(.5))*${spec.worldSize});
    float rings=sin(radial*rippleSettings.x-waterTime*rippleSettings.y);
    float crossing=sin(nativeWaterUV.x*58.0+waterTime*.65)*sin(nativeWaterUV.y*45.0-waterTime*.43);
    diffuseColor.rgb*=1.0+rippleSettings.z*(rings+.35*crossing);
    diffuseColor.rgb+=vec3(.035,.055,.06)*pow(max(0.0,rings),12.0);`);
   shader.fragmentShader=shader.fragmentShader.replace('#include <alphahash_fragment>',`if(paintOwner>0.5 && (abs(paintOwner-occludingOwners.x)<0.1||abs(paintOwner-occludingOwners.y)<0.1||abs(paintOwner-occludingOwners.z)<0.1||abs(paintOwner-occludingOwners.w)<0.1))discard;
    #include <alphahash_fragment>`);
  };m.customProgramCacheKey=()=> 'painterly-material-v68/'+!!painted+'/'+!!mean+'/'+!!spec?.ripple;
 }
 materialCache.set(key,m);return m;
}
function appendMesh(batch,part,lighting){
 const vs=part.vertices,sun=lighting?new THREE.Vector3(-lighting.sun.cast[0],-lighting.sun.cast[1],1).normalize():new THREE.Vector3(-.34,-.45,.82).normalize(),ambient=lighting?.ambient??.8,strength=lighting?.sun.strength??.23,fillTone=lighting?.ambientColor||[.88,.96,1.04],sunTone=lighting?.sun.color||[1.12,1.05,.86];
 for(const [faceIndex,face] of part.faces.entries()){
  const a=new THREE.Vector3(...vs[face[0]]),b=new THREE.Vector3(...vs[face[1]]),c=new THREE.Vector3(...vs[face[2]]),normal=b.clone().sub(a).cross(c.clone().sub(a)).normalize();
  if((part.walkable||/slate|terracotta|roof/i.test(part.material||''))&&normal.z<0)normal.negate();
  const axis=Math.abs(normal.z)>.65?'xy':Math.abs(normal.x)>Math.abs(normal.y)?'yz':'xz';
  const lit=Math.max(0,normal.dot(sun));
  for(let j=1;j<face.length-1;j++)batch.owners?.push(part.objectId||part.id||'terrain');
  for(let j=1;j<face.length-1;j++)for(const i of [face[0],face[j],face[j+1]]){const v=vs[i],corner=face.indexOf(i),uv=part.uvs?.[faceIndex]?.[corner],bake=part.bakedLighting?.[faceIndex]?.[corner],sunlit=lit*(bake?.[1]??1),fill=ambient*(bake?.[0]??1),direct=sunlit*strength;batch.position.push(...v);batch.normal.push(normal.x,normal.y,normal.z);batch.color.push(fill*fillTone[0]+direct*sunTone[0],fill*fillTone[1]+direct*sunTone[1],fill*fillTone[2]+direct*sunTone[2]);batch.ownerId?.push(part.ownerNumber||0);batch.uv.push(...(uv||[axis==='yz'?v[1]/2.4:v[0]/2.4,axis==='xy'?v[1]/2.4:v[2]/2.4]))}
 }
}
function geometry(batch){const g=new THREE.BufferGeometry();for(const [name,size] of [['position',3],['normal',3],['uv',2],['color',3],['ownerId',1],['feather',1]])if(batch[name])g.setAttribute(name,new THREE.Float32BufferAttribute(batch[name],size));g.computeBoundingSphere();return g}
function featherMaterial(base,key){
 const m=base.clone(),compile=base.onBeforeCompile;m.transparent=true;m.depthWrite=false;m.forceSinglePass=true;
 m.onBeforeCompile=shader=>{compile?.(shader);shader.vertexShader='attribute float feather;varying float edgeOpacity;\n'+shader.vertexShader;shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nedgeOpacity=feather;');shader.fragmentShader='varying float edgeOpacity;\n'+shader.fragmentShader;shader.fragmentShader=shader.fragmentShader.replace('#include <alphatest_fragment>','diffuseColor.a*=smoothstep(0.0,1.0,edgeOpacity);\n#include <alphatest_fragment>')};
 m.customProgramCacheKey=()=> 'painterly-feather-v47/'+key;return m;
}
function boundarySegments(polygons,visit){
 for(const polygon of polygons){
  const area=polygon.reduce((s,a,i)=>{const b=polygon[(i+1)%polygon.length];return s+a[0]*b[1]-b[0]*a[1]},0),sign=area>0?1:-1;
  for(let i=0;i<polygon.length;i++){
   const a=polygon[i],b=polygon[(i+1)%polygon.length],dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy),n=[dy/length*sign,-dx/length*sign],steps=Math.ceil(length/.65);
   for(let j=0;j<steps;j++){const p=[a[0]+dx*j/steps,a[1]+dy*j/steps],q=[a[0]+dx*(j+1)/steps,a[1]+dy*(j+1)/steps],probe={x:(p[0]+q[0])/2+n[0]*.035,y:(p[1]+q[1])/2+n[1]*.035};
    if(polygons.some(other=>other!==polygon&&window.AstraeonSpatialV3.pointIn(probe,other)))continue;
    visit(p,q,n);
   }
  }
 }
}
class SpatialRenderer{
 constructor(source){
  this.source=source;this.actors=new Map();this.spriteTextures=new Map();this.stats={backend:'three-webgl',frames:0,frameMs:0};this.active=false;
  this.cameraProfile=V.cameraProfile;this.perspectiveMode=!!this.cameraProfile;this.projectionReady=false;
  this.entityIds=new WeakMap();this.nextEntityId=0;
  this.scene=new THREE.Scene();this.scene.background=new THREE.Color('#bbc9b2');
  this.camera=new THREE.Camera();this.camera.matrixAutoUpdate=false;this.camera.matrixWorld.identity();this.camera.matrixWorldInverse.identity();
  this.buildingNumbers=new Map();this.occluderGroups=[];this.fadedOwners=new Set();this.fadeMeshes=new Map();
  for(const o of source.objects){
   if(o.family==='vegetation'||!o.parts.some(p=>p.visible!==false&&p.role==='solid'&&p.vertices.some(v=>v[2]>2)))continue;
   const id=this.buildingNumbers.size+1;this.buildingNumbers.set(o.id,id);
   const triangles=[],box=new THREE.Box3();for(const p of o.parts.filter(p=>p.visible!==false)){
    const vertices=p.vertices.map(v=>new THREE.Vector3(...v));for(const v of vertices)box.expandByPoint(v);
    for(const f of p.faces)for(let i=1;i<f.length-1;i++)triangles.push([vertices[f[0]],vertices[f[i]],vertices[f[i+1]]]);
   }this.occluderGroups.push({id,owner:o.id,box,triangles});
  }
  const batches=new Map(),add=(part)=>{if(part.visible===false)return;const name=part.material||'paving',spec=source.materials[name]?.texture,key=name+JSON.stringify(spec||'');if(!batches.has(key))batches.set(key,{material:name,position:[],normal:[],uv:[],color:[],ownerId:[],owners:[]});appendMesh(batches.get(key),part,source.lighting)};
  const terrain=source.terrain,bounds=terrain.bounds,groundMesh={...terrain,walkable:true,vertices:terrain.vertices||[[bounds.minX,bounds.minY,terrain.elevation],[bounds.maxX,bounds.minY,terrain.elevation],[bounds.maxX,bounds.maxY,terrain.elevation],[bounds.minX,bounds.maxY,terrain.elevation]],faces:terrain.faces||[[0,1,2,3]]};add(groundMesh);
  for(const s of terrain.surfaces)add({...s,material:s.material||'paving',vertices:s.vertices||s.polygon.map(p=>[...p,.018]),faces:s.faces||[s.polygon.map((_,i)=>i)]});
  for(const o of source.objects)for(const p of o.parts)add({...p,objectId:o.id,ownerNumber:this.buildingNumbers.get(o.id)||0});
  for(const [key,batch] of batches){const name=batch.material,mesh=new THREE.Mesh(geometry(batch),material(name,source.materials?.[name]));mesh.name='static/'+key;mesh.userData.owners=batch.owners;mesh.userData.cacheDynamic=['water','riverCascade'].includes(name)||!!source.materials[name]?.texture?.ripple;this.scene.add(mesh)}
  const spatial=window.AstraeonContent?.nativeWorld?.id===source.id?window.AstraeonContent.nativeWorld.spatial:window.AstraeonSpatialV3.compile(source);this.spatial=spatial;
  // Blend only the exposed union boundary of low paving. Internal strip and
  // junction edges remain opaque, and these visual verges never change paths.
  const edgeMaterial=source.materials.cityPaving?'cityPaving':'paving',paving=terrain.surfaces.filter(s=>s.walkable&&['paving','cityPaving'].includes(s.material)&&s.vertices&&Math.max(...s.vertices.map(v=>v[2]))<.10),edge={position:[],normal:[],uv:[],color:[],ownerId:[],feather:[]},size=source.materials.paving?.texture?.worldSize||4;
  boundarySegments(paving.map(s=>s.polygon),(a,b,n)=>{
   const outer=[a[0]+n[0]*.52,a[1]+n[1]*.52],probe=[(a[0]+b[0])/2+n[0]*.45,(a[1]+b[1])/2+n[1]*.45];
   if(!window.AstraeonSpatialV3.pointIn({x:probe[0],y:probe[1]},terrain.walkablePolygon)||spatial.blocked(...probe,.02))return;
   const v=[[...a,spatial.elevationAt(...a)+.010],[...b,spatial.elevationAt(...b)+.010],[b[0]+n[0]*.52,b[1]+n[1]*.52,terrain.elevation+.011],[...outer,terrain.elevation+.011]];
   appendMesh(edge,{vertices:v,faces:[[0,1,2,3]],material:edgeMaterial,walkable:true,uvs:[v.map(p=>[p[0]/size,p[1]/size])]},source.lighting);
   edge.feather.push(1,1,0,1,0,0);
  });
  if(edge.position.length){const verge=new THREE.Mesh(geometry(edge),featherMaterial(material(edgeMaterial,source.materials[edgeMaterial]),edgeMaterial));verge.name='static/paving-verges';this.scene.add(verge)}
  // A quiet, shallow shoreline ribbon softens the water/rock contact without
  // painting over the cliff silhouette or the usable bridge thresholds.
  const water=terrain.surfaces.find(s=>s.material==='water'),shore={position:[],normal:[],uv:[],color:[],ownerId:[],feather:[]};
  const shorePolygons=[terrain.walkablePolygon,...terrain.surfaces.filter(s=>s.walkable&&s.role==='green'&&s.material==='grass').map(s=>s.polygon)];
  if(water)boundarySegments(shorePolygons,(a,b,n)=>{
   const z=water.vertices[0][2]+.013,points=[[a[0]+n[0]*1.35,a[1]+n[1]*1.35,z],[b[0]+n[0]*1.35,b[1]+n[1]*1.35,z],[b[0]+n[0]*2.4,b[1]+n[1]*2.4,z],[a[0]+n[0]*2.4,a[1]+n[1]*2.4,z]];
   if(!window.AstraeonSpatialV3.pointIn({x:points[0][0],y:points[0][1]},water.polygon))return;
   appendMesh(shore,{vertices:points,faces:[[0,1,2,3]],walkable:true},source.lighting);shore.feather.push(.45,.45,0,.45,0,0);
  });
  if(shore.position.length){const ribbon=new THREE.Mesh(geometry(shore),featherMaterial(new THREE.MeshBasicMaterial({color:'#b8d9ce',vertexColors:true,side:THREE.DoubleSide}),'shore'));ribbon.name='static/shoreline';this.scene.add(ribbon)}
  // Static authored sun shadow atlas: one draw, no dynamic shadow map or PBR.
  this.shadowSize=source.lighting.groundShadow?.resolution||2048;const c=document.createElement('canvas');c.width=c.height=this.shadowSize;const g=c.getContext('2d'),b=terrain.bounds,sx=this.shadowSize/(b.maxX-b.minX),sy=this.shadowSize/(b.maxY-b.minY);
  g.fillStyle='#3a4464';g.globalAlpha=source.lighting.sun.strength;g.filter='blur(2px)';g.beginPath();for(const s of spatial.shadowPolygons){s.polygon.forEach(([x,y],i)=>i?g.lineTo((x-b.minX)*sx,(y-b.minY)*sy):g.moveTo((x-b.minX)*sx,(y-b.minY)*sy));g.closePath()}g.fill();g.filter='none';
  // Soft local depth at building feet supplements the directional cast atlas.
  // One combined stroke avoids repeatedly darkening intersecting foundations.
  g.save();g.filter='blur(3px)';g.strokeStyle='#273449';g.globalAlpha=.22;g.lineWidth=.40*(sx+sy)/2;g.lineJoin='round';g.beginPath();
  for(const solid of spatial.solids){if(solid.visible===false||solid.base>.8||solid.height<1.4)continue;solid.footprint.forEach(([x,y],i)=>i?g.lineTo((x-b.minX)*sx,(y-b.minY)*sy):g.moveTo((x-b.minX)*sx,(y-b.minY)*sy));g.closePath()}g.stroke();g.restore();
  this.shadowPixels=g.getImageData(0,0,this.shadowSize,this.shadowSize).data;this.shadowBounds=b;
  const tex=new THREE.CanvasTexture(c);tex.flipY=false;tex.colorSpace=THREE.SRGBColorSpace;
  // A source-matched native bake uses the real caster triangles and each
  // floor elevation. Its alpha already contains sun strength and local AO.
  // The geometric atlas above remains the fallback for worlds without a bake.
  if(source.lighting.groundShadow){
   const bake=source.lighting.groundShadow;
   textureLoads.push(new Promise((resolve,reject)=>{
    const image=new Image();image.onload=()=>{
     g.save();g.setTransform(1,0,0,1,0,0);g.globalAlpha=1;g.filter='none';g.clearRect(0,0,c.width,c.height);
     g.fillStyle='#3a4464';g.fillRect(0,0,c.width,c.height);g.globalCompositeOperation='destination-in';g.drawImage(image,0,0,c.width,c.height);g.restore();
     this.shadowPixels=g.getImageData(0,0,c.width,c.height).data;tex.needsUpdate=true;resolve();
    };image.onerror=()=>reject(new Error('Could not load native ground shadows: '+bake.file));image.src=new URL('../../'+bake.file,import.meta.url).href;
   }));
  }
  // Project the static atlas onto the authored walkable elevations. A flat
  // decal disappears beneath terraces and cannot ground their architecture.
  const shadowPositions=[],shadowUVs=[],shadowVertex=(x,y,z)=>{shadowPositions.push(x,y,z);shadowUVs.push((x-b.minX)/(b.maxX-b.minX),(y-b.minY)/(b.maxY-b.minY))};
  // One receiver per occupied floor cell, at the highest authored contact.
  // Overlaid ground/road receivers caused depth fighting and doubled opacity
  // at street junctions after the larger-town material pass.
  const land=[terrain.walkablePolygon,...terrain.surfaces.filter(s=>s.walkable).map(s=>s.polygon)].filter(Boolean),cell=.5;
  // Actor casts share the building sun and stop at authored land boundaries.
  // A floor mask prevents a bridge-edge silhouette floating over the river.
  const mask=document.createElement('canvas');mask.width=mask.height=this.shadowSize;const mg=mask.getContext('2d');mg.fillStyle='#fff';
  for(const polygon of land){mg.beginPath();polygon.forEach(([x,y],i)=>i?mg.lineTo((x-b.minX)*sx,(y-b.minY)*sy):mg.moveTo((x-b.minX)*sx,(y-b.minY)*sy));mg.closePath();mg.fill()}
  this.shadowLand=new THREE.CanvasTexture(mask);this.shadowLand.flipY=false;
  this.shadowLand.generateMipmaps=false;this.shadowLand.minFilter=THREE.LinearFilter;
  const contact=document.createElement('canvas');contact.width=contact.height=64;const cg=contact.getContext('2d'),gradient=cg.createRadialGradient(32,32,3,32,32,32);gradient.addColorStop(0,'rgba(255,255,255,1)');gradient.addColorStop(.45,'rgba(255,255,255,.65)');gradient.addColorStop(1,'rgba(255,255,255,0)');cg.fillStyle=gradient;cg.fillRect(0,0,64,64);this.contactTexture=new THREE.CanvasTexture(contact);
  for(let y=b.minY;y<b.maxY;y+=cell)for(let x=b.minX;x<b.maxX;x+=cell){
   if(!land.some(p=>window.AstraeonSpatialV3.pointIn({x:x+cell/2,y:y+cell/2},p)))continue;
   for(const [dx,dy] of [[0,0],[cell,0],[cell,cell],[0,0],[cell,cell],[0,cell]])shadowVertex(x+dx,y+dy,spatial.elevationAt(x+dx,y+dy)+.015);
  }
  const shadowGeo=new THREE.BufferGeometry();shadowGeo.setAttribute('position',new THREE.Float32BufferAttribute(shadowPositions,3));shadowGeo.setAttribute('uv',new THREE.Float32BufferAttribute(shadowUVs,2));shadowGeo.computeBoundingSphere();
  // The inherited screen basis reflects winding. Receiver decals must follow
  // the same double-sided policy as the authored geometry and picking floor.
  const shadow=new THREE.Mesh(shadowGeo,new THREE.MeshBasicMaterial({map:tex,transparent:true,depthWrite:false,side:THREE.DoubleSide,forceSinglePass:true}));shadow.userData.cacheDynamic=true;this.scene.add(shadow);
  this.dynamicNodes=this.scene.children.filter(o=>o.userData.cacheDynamic);
  this.staticNodes=this.scene.children.filter(o=>!o.userData.cacheDynamic);
  // Upright illustrated planes: a pixel of height is real vertical world
  // height, not a camera-facing lean into the wall behind the actor. The XY
  // right vector has zero projected vertical displacement. These bases retain
  // the artwork's screen shape while its head/feet participate in spatial depth.
  const {xx,xy,yx,yy}=this.cameraProfile?.basis||V.basis,det=xx*yy-yx*xy;
  this.right=new THREE.Vector3(yy/det,-xy/det,0);this.up=new THREE.Vector3(0,0,1/35);
  this.raycaster=new THREE.Raycaster();
  const floor={position:[],normal:[],uv:[],color:[]};
  appendMesh(floor,groundMesh);
  for(const s of terrain.surfaces.filter(s=>s.walkable&&s.vertices))appendMesh(floor,s);
  this.navFloor=new THREE.Mesh(geometry(floor),new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));this.navFloor.updateMatrixWorld();
  this.whenReady=Promise.all(textureLoads);
 }
 mount(overlay){
  this.overlay=overlay;
  V.mountCameraControls(overlay);
  // Render the world at least at CSS resolution, including software WebGL.
  // Perspective profiles render directly with antialiasing.
  try{this.renderer=new THREE.WebGLRenderer({antialias:this.perspectiveMode,alpha:false,powerPreference:'high-performance'});}catch(error){throw new Error('Spatial world requires WebGL: '+error.message)}
  const gl=this.renderer.getContext(),debug=gl.getExtension('WEBGL_debug_renderer_info'),device=debug?gl.getParameter(debug.UNMASKED_RENDERER_WEBGL):'';
  this.stats.device=device;this.stats.software=/SwiftShader|llvmpipe|software/i.test(device);
  // Do not silently stretch a half-resolution world behind a sharp UI. Software
  // renderers use native CSS pixels; hardware also follows HiDPI up to 1.5x.
  this.stats.pixelRatio=this.stats.software?1:Math.max(1,Math.min(devicePixelRatio||1,1.5));
  for(const m of materialCache.values()){m.map.anisotropy=this.stats.software?1:Math.min(4,this.renderer.capabilities.getMaxAnisotropy());m.map.minFilter=THREE.LinearMipmapLinearFilter;m.map.needsUpdate=true}
  this.renderer.outputColorSpace=THREE.SRGBColorSpace;this.renderer.setPixelRatio(this.stats.pixelRatio);
  // Decode/upload all complete strips before the first movement. Shared atlases
  // avoid a new canvas texture upload every time an actor changes a frame.
  for(const image of Object.values(window.AstraeonDirectionalArt.sheets))this.spriteTexture(image);
  this.warmFadeMeshes();
  this.renderer.info.autoReset=false;
  this.canvas=this.renderer.domElement;this.canvas.id='spatial-world';this.canvas.setAttribute('aria-hidden','true');this.canvas.style.cssText='position:absolute;inset:0;width:100%;height:100%;z-index:0;pointer-events:none';overlay.before(this.canvas);overlay.style.background='transparent';overlay.parentElement.classList.add('spatial-stage');this.active=true;
 }
 begin(camera,w,h,zoom,anchorY){
  this.frameStarted=performance.now();this.assemblyMs=0;waterTime.value=this.frameStarted/1000;
  if(!this.renderer)return;this.active=true;this.canvas.hidden=false;
  // Slow shared current, rather than a completely static tiled river.
  const water=materialCache.get('water'+JSON.stringify(this.source.materials.water?.texture||''));
  if(water?.map){const time=performance.now()/1000;water.map.offset.set(time*.004,time*.002)}
  const cascade=materialCache.get('riverCascade'+JSON.stringify(this.source.materials.riverCascade?.texture||''));
  if(cascade?.map)cascade.map.offset.y=performance.now()/1000*.35;
  this.width=w;this.height=h;this.zoom=zoom;this.anchorY=anchorY;
  if(this.canvas.clientWidth!==w||this.canvas.clientHeight!==h||this.lastSize!==w+'x'+h){this.renderer.setSize(w,h,false);this.lastSize=w+'x'+h}
  // Reusing rasterized geometry must translate by whole device pixels. Snap
  // only the software camera to its actual (possibly odd-sized) drawing
  // buffer grid; simulation, navigation and the hardware camera remain smooth.
  const size=this.renderer.getDrawingBufferSize(new THREE.Vector2()),gridX=zoom*size.x/w,gridY=zoom*size.y/h;
  this.focus=this.stats.software&&!this.perspectiveMode?{x:Math.round(camera.x*gridX)/gridX,y:Math.round(camera.y*gridY)/gridY}:{...camera};
  const cx=this.focus.x,cy=this.focus.y,s=zoom;
  if(this.perspectiveMode){
   const b=this.cameraProfile.basis,d=this.cameraProfile.depth,focus=V.inverse(cx,cy),cz=this.focus.z||0,w0=1-d.x*focus.x-d.y*focus.y-d.z*cz,n=1-2*anchorY,hx=2*s/w,hy=2*s/h;
   // The long-lens denominator varies with ground depth and height; the local
   // axes stay aligned with input and the existing spatial artwork.
   const ro=this.cameraProfile.kind==='ragnarok',far=1000,near=1,za=ro?(far+near)/(far-near):1.1,zb=ro?2*far*near/(far-near)/(this.cameraProfile.zoom/2):.6;
   this.camera.projectionMatrix.set(
    hx*b.xx,hx*b.yx,0,-hx*cx,
    n*d.x-hy*b.xy,n*d.y-hy*b.yy,n*d.z+hy*35,n*w0+hy*(cy-35*cz),
    za*d.x,za*d.y,za*d.z,za*w0-zb,
    d.x,d.y,d.z,w0
   );
  }else this.camera.projectionMatrix.set(96*s/w,-64*s/w,0,-2*cx*s/w,-28*s/h,-44*s/h,70*s/h,2*cy*s/h+1-2*anchorY,-.0056,-.0084,-.00752,.25,0,0,0,1);
  this.camera.projectionMatrixInverse.copy(this.camera.projectionMatrix).invert();this.camera.updateMatrixWorld();this.projectionReady=true;
  for(const a of this.actors.values())a.mesh.visible=a.shadow.visible=a.cast.visible=false;
 }
 actor(id,t,draw,{alpha=1,shadowAlpha=alpha,radius=.4}={}){
  const assemblyStarted=performance.now();
  const screen=this.perspectiveMode?this.worldToScreen(t.position.x,t.position.y,t.position.z||0):V.project(t.position.x,t.position.y),sx=this.perspectiveMode?screen.x:this.width/2+(screen.x-this.focus.x)*this.zoom,sy=this.perspectiveMode?screen.y:this.height*this.anchorY+(screen.y-this.focus.y-(t.position.z||0)*35)*this.zoom;
  if(sx< -150||sx>this.width+150||sy< -80||sy>this.height+230)return;
  let a=this.actors.get(id);
  if(!a){
   const canvas=document.createElement('canvas');canvas.width=canvas.height=256;const ctx=canvas.getContext('2d',{willReadFrequently:true}),tex=new THREE.CanvasTexture(canvas);tex.colorSpace=THREE.SRGBColorSpace;tex.generateMipmaps=false;tex.minFilter=THREE.LinearFilter;
   const geo=new THREE.BufferGeometry(),positions=[];
   for(const [x,y] of [[-128,-32],[128,-32],[128,224],[-128,224]])positions.push(...this.right.clone().multiplyScalar(x).addScaledVector(this.up,y).toArray());
   geo.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geo.setAttribute('uv',new THREE.Float32BufferAttribute([0,0,1,0,1,1,0,1],2));geo.setIndex([0,1,2,0,2,3]);geo.computeBoundingSphere();
   const mat=new THREE.MeshBasicMaterial({map:tex,alphaTest:.18,transparent:true,depthWrite:true,side:THREE.DoubleSide,forceSinglePass:true});const mesh=new THREE.Mesh(geo,mat);mesh.name='actor/'+id;this.scene.add(mesh);
   const shadow=new THREE.Mesh(new THREE.PlaneGeometry(radius*2.5,radius*2.5),new THREE.MeshBasicMaterial({map:this.contactTexture,color:'#253344',transparent:true,opacity:.17,depthWrite:false,side:THREE.DoubleSide,forceSinglePass:true}));shadow.scale.set(1,1.1,1);shadow.name='contact/'+id;this.scene.add(shadow);
   const grid=6,castGeo=new THREE.BufferGeometry(),indices=[];
   castGeo.setAttribute('position',new THREE.BufferAttribute(new Float32Array((grid+1)**2*3),3));castGeo.setAttribute('uv',new THREE.BufferAttribute(new Float32Array((grid+1)**2*2),2));
   for(let y=0;y<grid;y++)for(let x=0;x<grid;x++){const k=y*(grid+1)+x;indices.push(k,k+1,k+grid+2,k,k+grid+2,k+grid+1)}castGeo.setIndex(indices);
   const castMat=new THREE.MeshBasicMaterial({map:tex,color:'#354363',transparent:true,opacity:.24,depthWrite:false,side:THREE.DoubleSide,forceSinglePass:true});
   const castUniforms={land:{value:this.shadowLand},bounds:{value:new THREE.Vector4(this.shadowBounds.minX,this.shadowBounds.minY,this.shadowBounds.maxX-this.shadowBounds.minX,this.shadowBounds.maxY-this.shadowBounds.minY)},texel:{value:new THREE.Vector2(1/256,1/256)},uvBounds:{value:new THREE.Vector4(0,0,1,1)}};
   castMat.onBeforeCompile=shader=>{
    Object.assign(shader.uniforms,{shadowLand:castUniforms.land,shadowBounds:castUniforms.bounds,shadowTexel:castUniforms.texel,shadowUvBounds:castUniforms.uvBounds});
    shader.vertexShader='varying vec2 shadowGround;\n'+shader.vertexShader;
    shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nshadowGround=(modelMatrix*vec4(position,1.0)).xy;');
    shader.fragmentShader='varying vec2 shadowGround;uniform sampler2D shadowLand;uniform vec4 shadowBounds,shadowUvBounds;uniform vec2 shadowTexel;\n'+shader.fragmentShader;
    shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',`vec2 groundUv=(shadowGround-shadowBounds.xy)/shadowBounds.zw;
     if(any(lessThan(groundUv,vec2(0.0)))||any(greaterThan(groundUv,vec2(1.0)))||texture2D(shadowLand,groundUv).a<0.5)discard;
     vec2 low=shadowUvBounds.xy+shadowTexel*.5,high=shadowUvBounds.zw-shadowTexel*.5;
     float coverage=texture2D(map,clamp(vMapUv,low,high)).a*.4;
     coverage+=texture2D(map,clamp(vMapUv+vec2(shadowTexel.x*1.5,0.0),low,high)).a*.15;
     coverage+=texture2D(map,clamp(vMapUv-vec2(shadowTexel.x*1.5,0.0),low,high)).a*.15;
     coverage+=texture2D(map,clamp(vMapUv+vec2(0.0,shadowTexel.y*1.5),low,high)).a*.15;
     coverage+=texture2D(map,clamp(vMapUv-vec2(0.0,shadowTexel.y*1.5),low,high)).a*.15;
     diffuseColor.a*=coverage;`);
   };castMat.customProgramCacheKey=()=> 'authored-actor-cast-v54';
   const cast=new THREE.Mesh(castGeo,castMat);cast.name='cast/'+id;this.scene.add(cast);
   a={canvas,ctx,tex,mesh,shadow,cast,castUniforms,castGrid:grid};this.actors.set(id,a);
  }
  const p=t.position,prior=V.zoom;V.zoom=1;a.ctx.clearRect(0,0,256,256);a.ctx.save();a.ctx.globalAlpha=alpha;
  const iso=(x,y,z=0)=>{const q=V.project(x-p.x,y-p.y);return{x:128+q.x,y:224+q.y-z+(p.z||0)*35}};
  let sockets;this.paintedFrame=null;this.sampledPose=null;this.assemblingActor=true;try{sockets=draw(a.ctx,iso)}finally{this.assemblingActor=false;a.ctx.restore();V.zoom=prior}
  const frame=this.paintedFrame;
  if(frame){
   const {image,bounds,unit,left,top}=frame,[x,y,w,h]=bounds,uv=a.mesh.geometry.attributes.uv,pos=a.mesh.geometry.attributes.position;
   const coords=[[left,top-h*unit],[left+w*unit,top-h*unit],[left+w*unit,top],[left,top]];
   for(let i=0;i<4;i++){const [dx,dy]=coords[i],v=this.right.clone().multiplyScalar(dx).addScaledVector(this.up,dy);pos.setXYZ(i,v.x,v.y,v.z)}
   uv.setXY(0,x/image.width,1-(y+h)/image.height);uv.setXY(1,(x+w)/image.width,1-(y+h)/image.height);uv.setXY(2,(x+w)/image.width,1-y/image.height);uv.setXY(3,x/image.width,1-y/image.height);
   pos.needsUpdate=uv.needsUpdate=true;a.mesh.geometry.computeBoundingSphere();a.mesh.material.map=this.spriteTexture(image);a.mesh.material.opacity=alpha;a.directFrame=true;
  }else{
   if(a.directFrame){const pos=a.mesh.geometry.attributes.position;[[-128,-32],[128,-32],[128,224],[-128,224]].forEach(([x,y],i)=>{const v=this.right.clone().multiplyScalar(x).addScaledVector(this.up,y);pos.setXYZ(i,v.x,v.y,v.z)});pos.needsUpdate=true;a.mesh.geometry.attributes.uv.array.set([0,0,1,0,1,1,0,1]);a.mesh.geometry.attributes.uv.needsUpdate=true;a.mesh.geometry.computeBoundingSphere()}
   a.directFrame=false;a.mesh.material.map=a.tex;a.mesh.material.opacity=1;a.tex.needsUpdate=true;
  }
  const b=this.shadowBounds,tx=Math.floor((p.x-b.minX)/(b.maxX-b.minX)*this.shadowSize),ty=Math.floor((p.y-b.minY)/(b.maxY-b.minY)*this.shadowSize),shade=tx>=0&&tx<this.shadowSize&&ty>=0&&ty<this.shadowSize?this.shadowPixels[(ty*this.shadowSize+tx)*4+3]/255:0;
  a.mesh.material.color.setRGB(1-shade*.38,1-shade*.32,1-shade*.22);
  if(this.cameraProfile?.kind==='ragnarok'){a.mesh.rotation.z=-this.cameraProfile.yaw*Math.PI/180;const scale=Math.cos(this.cameraProfile.pitch*Math.PI/180)/Math.cos(46*Math.PI/180);a.mesh.scale.set(scale,scale,1)}
  // Registered whole frames travel continuously; freezing a boot would also
  // freeze the pelvis until the next pose and create visible hold/snap motion.
  a.mesh.position.set(p.x,p.y,p.z||0);a.mesh.visible=true;a.shadow.position.set(p.x+.04,p.y+.04,(p.z||0)+.035);a.shadow.material.opacity=.17*shadowAlpha;a.shadow.visible=shadowAlpha>.05;
  this.projectActorShadow(a,p,shadowAlpha,shade);
  a.motionSample={root:[p.x,p.y,p.z||0],renderedRoot:a.mesh.position.toArray(),speed:t.speed,frame:this.sampledPose};
  this.assemblyMs+=performance.now()-assemblyStarted;return sockets;
 }
 projectActorShadow(a,root,alpha,shade){
  a.cast.visible=alpha>.05;if(!a.cast.visible)return;
  a.mesh.updateMatrixWorld();const positions=a.mesh.geometry.attributes.position,sourceUV=a.mesh.geometry.attributes.uv,pos=a.cast.geometry.attributes.position,uv=a.cast.geometry.attributes.uv,grid=a.castGrid,cast=this.source.lighting.sun.cast;
  const corners=[0,1,2,3].map(i=>new THREE.Vector3().fromBufferAttribute(positions,i).applyMatrix4(a.mesh.matrixWorld));
  for(let y=0;y<=grid;y++)for(let x=0;x<=grid;x++){
   const u=x/grid,v=y/grid,i=y*(grid+1)+x,low=corners[0].clone().lerp(corners[1],u),high=corners[3].clone().lerp(corners[2],u),point=low.lerp(high,v);
   let floor=root.z||0,px,py;
   // Project along the sun onto the local authored elevation, including stairs.
   for(let pass=0;pass<3;pass++){const height=Math.max(0,point.z-floor);px=point.x+cast[0]*height;py=point.y+cast[1]*height;floor=this.spatial.elevationAt(px,py)}
   pos.setXYZ(i,px,py,floor+.025);
   uv.setXY(i,THREE.MathUtils.lerp(sourceUV.getX(0),sourceUV.getX(1),u),THREE.MathUtils.lerp(sourceUV.getY(0),sourceUV.getY(3),v));
  }
  pos.needsUpdate=uv.needsUpdate=true;a.cast.geometry.computeBoundingSphere();
  const map=a.mesh.material.map;a.cast.material.map=map;a.cast.material.opacity=.24*alpha*(1-shade*.6);
  a.castUniforms.texel.value.set(1/map.image.width,1/map.image.height);
  a.castUniforms.uvBounds.value.set(sourceUV.getX(0),sourceUV.getY(0),sourceUV.getX(2),sourceUV.getY(2));
 }
 spriteTexture(image){
  if(!this.spriteTextures.has(image)){const tex=new THREE.Texture(image);tex.colorSpace=THREE.SRGBColorSpace;tex.generateMipmaps=false;tex.minFilter=THREE.LinearFilter;tex.magFilter=THREE.LinearFilter;tex.needsUpdate=true;
   const mask=document.createElement('canvas'),scale=Math.min(1,1024/Math.max(image.width,image.height));mask.width=Math.ceil(image.width*scale);mask.height=Math.ceil(image.height*scale);const ctx=mask.getContext('2d',{willReadFrequently:true});ctx.drawImage(image,0,0,mask.width,mask.height);tex.userData.alphaPixels={width:mask.width,height:mask.height,data:ctx.getImageData(0,0,mask.width,mask.height).data};
   this.spriteTextures.set(image,tex);this.renderer?.initTexture(tex)}
  return this.spriteTextures.get(image);
 }
 cachedWorld(){
  const r=this.renderer,pad=192,ratio=r.getPixelRatio(),w=this.width,h=this.height,size=r.getDrawingBufferSize(new THREE.Vector2()),padPixels=Math.round(pad*ratio),cw=w*(size.x+padPixels*2)/size.x,ch=h*(size.y+padPixels*2)/size.y,px=(cw-w)/2,py=(ch-h)/2,key=[w,h,ratio,this.zoom,this.anchorY].join('/');
  let c=this.staticCache;
  if(!c||c.key!==key){
   if(c){c.target.dispose();c.material.dispose();c.quad.geometry.dispose()}
   const gl=r.getContext(),samples=r.capabilities.isWebGL2?gl.getParameter(gl.SAMPLES):0;
   const target=new THREE.WebGLRenderTarget(size.x+padPixels*2,size.y+padPixels*2,{minFilter:THREE.NearestFilter,magFilter:THREE.NearestFilter,depthBuffer:true,samples});target.texture.colorSpace=THREE.SRGBColorSpace;target.depthTexture=new THREE.DepthTexture(target.width,target.height,THREE.UnsignedIntType);
   const material=new THREE.ShaderMaterial({uniforms:{colorMap:{value:target.texture},depthMap:{value:target.depthTexture},viewSize:{value:new THREE.Vector2(w,h)},cacheSize:{value:new THREE.Vector2(cw,ch)},offset:{value:new THREE.Vector2(pad,pad)}},vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=vec4(position.xy,0.0,1.0);}',fragmentShader:'uniform sampler2D colorMap;uniform sampler2D depthMap;uniform vec2 viewSize,cacheSize,offset;varying vec2 vUv;void main(){vec2 p=(vUv*viewSize+offset)/cacheSize;gl_FragColor=texture2D(colorMap,p);gl_FragDepth=texture2D(depthMap,p).r;\n#include <colorspace_fragment>\n}',depthTest:true,depthWrite:true,depthFunc:THREE.AlwaysDepth,toneMapped:false});
   const quad=new THREE.Mesh(new THREE.PlaneGeometry(2,2),material);quad.frustumCulled=false;const scene=new THREE.Scene();scene.add(quad);c=this.staticCache={key,target,material,quad,scene,camera:new THREE.Camera(),focus:null};
  }
  const dx=c.focus?(this.focus.x-c.focus.x)*this.zoom:Infinity,dy=c.focus?(this.focus.y-c.focus.y)*this.zoom:Infinity;
  if(!c.focus||Math.max(Math.abs(dx),Math.abs(dy))>pad-40){
   const matrix=this.camera.projectionMatrix.clone(),actors=[...this.actors.values()].map(a=>[a,a.mesh.visible,a.shadow.visible,a.cast.visible]),surfaces=this.dynamicNodes.map(o=>[o,o.visible]);
   try{
    for(const [a] of actors)a.mesh.visible=a.shadow.visible=a.cast.visible=false;
    for(const [o] of surfaces)o.visible=false;
    this.camera.projectionMatrix.set(96*this.zoom/cw,-64*this.zoom/cw,0,-2*this.focus.x*this.zoom/cw,-28*this.zoom/ch,-44*this.zoom/ch,70*this.zoom/ch,2*this.focus.y*this.zoom/ch+1-2*(h*this.anchorY+py)/ch,-.0056,-.0084,-.00752,.25,0,0,0,1);
    r.setRenderTarget(c.target);r.render(this.scene,this.camera);c.focus={...this.focus};this.stats.cacheUpdates=(this.stats.cacheUpdates||0)+1;
   }finally{this.camera.projectionMatrix.copy(matrix);for(const [a,visible,shadow,cast] of actors){a.mesh.visible=visible;a.shadow.visible=shadow;a.cast.visible=cast}for(const [o,visible] of surfaces)o.visible=visible;r.setRenderTarget(null)}
  }
  c.material.uniforms.offset.value.set(px+(this.focus.x-c.focus.x)*this.zoom,py-(this.focus.y-c.focus.y)*this.zoom);
  // The cached static depth is written into the SAME framebuffer as actor
  // quads. This is a color/depth reuse optimization, not an actor overlay.
  r.render(c.scene,c.camera);const background=this.scene.background;this.scene.background=null;r.autoClear=false;
  const visibility=this.staticNodes.map(o=>o.visible);try{for(const o of this.staticNodes)o.visible=false;r.render(this.scene,this.camera)}finally{this.staticNodes.forEach((o,i)=>o.visible=visibility[i]);this.scene.background=background;r.autoClear=true}
 }
 prepareFadeMeshes(owner){
  if(this.fadeMeshes.has(owner))return;
  const batches=new Map(),object=this.source.objects.find(o=>o.id===owner),meshes=[];
  for(const part of object.parts.filter(p=>p.visible!==false)){
   if(!batches.has(part.material))batches.set(part.material,{position:[],normal:[],uv:[],color:[],ownerId:[]});
   appendMesh(batches.get(part.material),part,this.source.lighting);
  }
  for(const [name,batch] of batches){const original=material(name,this.source.materials[name]),m=original.clone();m.onBeforeCompile=original.onBeforeCompile;m.customProgramCacheKey=original.customProgramCacheKey;m.transparent=true;m.opacity=.16;m.depthWrite=false;m.alphaTest=0;
   const mesh=new THREE.Mesh(geometry(batch),m);mesh.name='fade/'+owner;mesh.userData.cacheDynamic=true;mesh.visible=false;this.scene.add(mesh);meshes.push(mesh);
  }this.fadeMeshes.set(owner,meshes);
 }
 warmFadeMeshes(){
  // Build and upload reveal geometry/programs during loading, rather than at
  // the first movement under a gate or behind a facade.
  for(const group of this.occluderGroups)this.prepareFadeMeshes(group.owner);
  const meshes=[...this.fadeMeshes.values()].flat(),gl=this.renderer.getContext(),target=new THREE.WebGLRenderTarget(256,256,{samples:this.renderer.capabilities.isWebGL2?gl.getParameter(gl.SAMPLES):0}),camera=new THREE.Camera(),b=this.source.terrain.bounds,w=b.maxX-b.minX+8,h=b.maxY-b.minY+35,cx=(b.maxX+b.minX)/2,cy=(b.maxY+b.minY)/2;
  // Match the gameplay framebuffer's output color space/MSAA so warming does
  // not compile a different offscreen-only shader variant.
  target.texture.colorSpace=THREE.SRGBColorSpace;
  // Rasterize actual walls/roofs. An identity camera clips the entire town;
  // some drivers defer a fragment variant until it produces real fragments.
  camera.projectionMatrix.set(2/w,0,0,-2*cx/w,0,-2/h,1/h,2*cy/h,0,-.002,-.004,0,0,0,0,1);
  try{
   for(const mesh of meshes){mesh.visible=true;mesh.frustumCulled=false}
   this.renderer.setRenderTarget(target);this.renderer.render(this.scene,camera);
   // Exercise the masked static path as well as the transparent replacement.
   // Some drivers specialize the all-zero uniform branch on its first draw;
   // warming only replacement meshes leaves the first real reveal expensive.
   occludingOwners.value.set(...Array.from({length:4},(_,i)=>this.occluderGroups[i]?.id||0));
   this.renderer.render(this.scene,camera);
   this.renderer.setRenderTarget(null);this.renderer.render(this.scene,camera);
   gl.finish();
  }finally{
   occludingOwners.value.set(0,0,0,0);
   this.renderer.setRenderTarget(null);target.dispose();
   for(const mesh of meshes){mesh.visible=false;mesh.frustumCulled=true}
  }
  this.dynamicNodes=this.scene.children.filter(o=>o.userData.cacheDynamic);
 }
 updateOcclusion(){
  this.fadedOwners.clear();const ids=[],player=this.actors.get('player'),hit=new THREE.Vector3();
  if(this.perspectiveMode&&player?.mesh.visible){for(const height of [.85,1.65]){
   const p=player.mesh.position.clone();p.z+=height;const screen=this.worldToScreen(p.x,p.y,p.z),ray=this.screenRay(screen.x,screen.y).ray,max=ray.origin.distanceTo(p)-.03;
   for(const group of this.occluderGroups){const entry=ray.intersectBox(group.box,hit);if(!entry||ray.origin.distanceTo(entry)>=max)continue;
    if(group.triangles.some(([a,b,c])=>ray.intersectTriangle(a,b,c,false,hit)&&ray.origin.distanceTo(hit)<max)){
     if(!ids.includes(group.id)&&ids.length<4){ids.push(group.id);this.fadedOwners.add(group.owner)}
    }
   }
  }}
  occludingOwners.value.set(...Array.from({length:4},(_,i)=>ids[i]||0));this.stats.fadedBuildings=[...this.fadedOwners];
  for(const meshes of this.fadeMeshes.values())for(const mesh of meshes)mesh.visible=false;
  for(const owner of [...this.fadedOwners].slice(0,4)){
   this.prepareFadeMeshes(owner);
   for(const mesh of this.fadeMeshes.get(owner))mesh.visible=true;
  }
 }
 end(){const started=performance.now();this.updateOcclusion();this.stats.occlusionMs=performance.now()-started;const renderStarted=performance.now();this.renderer.info.reset();if(this.stats.software&&!this.perspectiveMode)this.cachedWorld();else this.renderer.render(this.scene,this.camera);this.stats.renderMs=performance.now()-renderStarted;this.stats.frames++;this.stats.frameMs=this.stats.frameMs*.95+(performance.now()-started)*.05;this.stats.assemblyMs=this.assemblyMs;this.stats.totalMs=performance.now()-this.frameStarted;this.stats.calls=this.renderer.info.render.calls;this.stats.triangles=this.renderer.info.render.triangles;this.stats.textures=this.renderer.info.memory.textures;this.stats.staticDepthCache=!!this.stats.software&&!this.perspectiveMode;}
 hide(){if(this.canvas)this.canvas.hidden=true;this.active=false;}
 idFor(entity,prefix){if(!this.entityIds.has(entity))this.entityIds.set(entity,prefix+'/'+(++this.nextEntityId));return this.entityIds.get(entity)}
 worldToScreen(x,y,z=0){const p=new THREE.Vector3(x,y,z).project(this.camera);return{x:(p.x+1)*this.width/2,y:(1-p.y)*this.height/2,depth:p.z}}
 screenRay(x,y){const near=new THREE.Vector3(x/this.width*2-1,1-y/this.height*2,-1).unproject(this.camera),far=new THREE.Vector3(x/this.width*2-1,1-y/this.height*2,1).unproject(this.camera);this.raycaster.set(near,far.sub(near).normalize());return this.raycaster}
 screenToWorld(x,y){const hit=this.screenRay(x,y).intersectObject(this.navFloor,false)[0];return hit?{x:hit.point.x,y:hit.point.y}:null}
 pickActor(x,y){
  for(const hit of this.screenRay(x,y).intersectObjects(this.scene.children,false)){
   if(!hit.object.visible||hit.object===this.navFloor)continue;
   const id=hit.object.name;
   if(id.startsWith('actor/')){const a=this.actors.get(id.slice(6));if(!a||!hit.uv)continue;const mask=a.directFrame?a.mesh.material.map.userData.alphaPixels:null,w=mask?.width||256,h=mask?.height||256,px=Math.min(w-1,Math.max(0,Math.floor(hit.uv.x*w))),py=Math.min(h-1,Math.max(0,Math.floor((1-hit.uv.y)*h)));if((mask?mask.data[(py*w+px)*4+3]:a.ctx.getImageData(px,py,1,1).data[3])<26)continue;return id.slice(6)}
   if(id.startsWith('static/')){
    if(!hit.object.userData.owners)continue; // Derived verges/shoreline carry no interactions.
    if(this.fadedOwners.has(hit.object.userData.owners[hit.faceIndex]))continue;
    const m=hit.object.material;if(m.alphaTest&&hit.uv&&m.map.image){
     if(!m.userData.alphaPixels){const image=m.map.image,ctx=image.getContext('2d');m.userData.alphaPixels={data:ctx.getImageData(0,0,image.width,image.height).data,width:image.width,height:image.height}}
     const p=m.userData.alphaPixels,u=((hit.uv.x%1)+1)%1,v=((hit.uv.y%1)+1)%1,x=Math.min(p.width-1,Math.floor(u*p.width)),y=Math.min(p.height-1,Math.floor((1-v)*p.height));
     if(p.data[(y*p.width+x)*4+3]/255<m.alphaTest)continue;
    }return 'object/'+hit.object.userData.owners[hit.faceIndex];
   }
  }return null;
 }
 snapshot(){return {...this.stats,cameraProfile:this.cameraProfile?structuredClone(this.cameraProfile):null,actors:[...this.actors].filter(([,a])=>a.mesh.visible).map(([id,a])=>({id,position:a.mesh.position.toArray(),depthTest:a.mesh.material.depthTest,depthWrite:a.mesh.material.depthWrite,motionSample:a.motionSample}))};}
}
window.AstraeonSpatialRenderer={SpatialRenderer,THREE};
if(window.AstraeonContent?.nativeWorld?.id==='wayfarer-spatial'&&new URLSearchParams(location.search).get('renderer')!=='canvas')window.AstraeonSpatialView=new SpatialRenderer(window.AstraeonContent.nativeWorld.spatial.scene);
