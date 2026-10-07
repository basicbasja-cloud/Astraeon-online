/** Derive render transport from authored source without changing any draw attribute.
 * Run offline: node --max-old-space-size=6000 tools/build-world-streaming.mjs
 * The existing renderer's appendMesh/boundarySegments are the conversion authority.
 */
import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
const root=new URL('../',import.meta.url),read=p=>fs.readFileSync(new URL(p,root)),hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const sourceBytes=read('world/v3/wayfarer-spatial.json'),sourceHash=hash(sourceBytes),source=JSON.parse(sourceBytes),renderer=read('world/v3/renderer.js').toString();
const THREE=await import('data:text/javascript;base64,'+read('vendor/three/three.core.min.js').toString('base64'));
const window={};window.window=window;vm.runInNewContext(read('world/v3/spatial.js').toString(),{window});
const spatial=window.AstraeonSpatialV3.compile(source);
const appendCode=renderer.slice(renderer.indexOf('function appendMesh('),renderer.indexOf('function geometry('));
const boundaryCode=renderer.slice(renderer.indexOf('function boundarySegments('),renderer.indexOf('class SpatialRenderer'));
const {appendMesh,boundarySegments}=vm.runInNewContext(appendCode+boundaryCode+';({appendMesh,boundarySegments})',{THREE,window});
const folder='world/v3/streamed/wayfarer-'+sourceHash.slice(0,12)+'/',dir=new URL(folder,root);fs.mkdirSync(dir,{recursive:true});
const writeJSON=(path,value)=>{const b=Buffer.from(JSON.stringify(value));fs.writeFileSync(new URL(path,root),b);return {url:path,bytes:b.length,sha256:hash(b)}};
const buildingNumbers=new Map(),owners=[];
for(const o of source.objects){if(o.family!=='vegetation'&&o.parts.some(p=>p.role==='solid'&&p.vertices.some(v=>v[2]>2))&&o.parts.some(p=>p.visible!==false))buildingNumbers.set(o.id,buildingNumbers.size+1);owners.push({id:o.id,number:buildingNumbers.get(o.id)||0})}
const attrs=[['position',3],['normal',3],['uv',2],['color',3],['ownerId',1],['feather',1]],chunks=new Map(),cellSize=32;
function chunkFor(id){if(!chunks.has(id))chunks.set(id,{id,batches:new Map(),bounds:[Infinity,Infinity,Infinity,-Infinity,-Infinity,-Infinity]});return chunks.get(id)}
let triangleCount=0;
function distribute(batch,key,definition){
 const rows=batch.position.length/9;
 for(let t=0;t<rows;t++){
  const at=t*9,x=(batch.position[at]+batch.position[at+3]+batch.position[at+6])/3,y=(batch.position[at+1]+batch.position[at+4]+batch.position[at+7])/3;
  // The underlying ocean/terrain spans the map but costs only a few triangles.
  const id=definition.global?'global':'c'+Math.floor(x/cellSize)+'_'+Math.floor(y/cellSize),chunk=chunkFor(id);
  if(!chunk.batches.has(key))chunk.batches.set(key,{...definition,key,owners:[],...Object.fromEntries(attrs.filter(([n])=>batch[n]).map(([n])=>[n,[]]))});const target=chunk.batches.get(key);
  for(const [name,size] of attrs)if(batch[name])for(let j=t*3*size;j<(t+1)*3*size;j++)target[name].push(batch[name][j]);
  target.owners.push(batch.owners?.[t]||'terrain');
  for(let j=at;j<at+9;j+=3)for(let k=0;k<3;k++){chunk.bounds[k]=Math.min(chunk.bounds[k],batch.position[j+k]);chunk.bounds[k+3]=Math.max(chunk.bounds[k+3],batch.position[j+k])}
  triangleCount++;
 }
}
function add(part){
 if(part.visible===false)return;const name=part.material||'paving',spec=source.materials[name]?.texture;let cell='';
 if(!spec?.alphaBlend&&!['water','riverFoam','riverCascade'].includes(name)){let minX=Infinity,minY=Infinity,maxX=-Infinity,maxY=-Infinity;for(const [x,y] of part.vertices){minX=Math.min(minX,x);minY=Math.min(minY,y);maxX=Math.max(maxX,x);maxY=Math.max(maxY,y)}cell=maxX-minX>32||maxY-minY>32?'/wide/'+(part.id||'terrain'):'/cell/'+Math.floor((minX+maxX)/32)+','+Math.floor((minY+maxY)/32)}
 const opacity=!!part.vertexOpacity,key=name+JSON.stringify(spec||'')+cell+(opacity?'/native-opacity':'');
 const batch={position:[],normal:[],uv:[],color:[],ownerId:[],owners:[],...(opacity?{feather:[]}:{})};appendMesh(batch,part,source.lighting);
 distribute(batch,key,{material:name,kind:'static',opacity,global:part.id===source.terrain.id||part===source.terrain||part.globalTransport===true});
}
const terrain=source.terrain,b=terrain.bounds;
add({...terrain,id:'transport-base-ground',globalTransport:true,walkable:true});
for(const s of terrain.surfaces)add({...s,globalTransport:s.material==='water',material:s.material||'paving',vertices:s.vertices||s.polygon.map(p=>[...p,.018]),faces:s.faces||[s.polygon.map((_,i)=>i)]});
for(const o of source.objects)for(const p of o.parts)add({...p,objectId:o.id,ownerNumber:buildingNumbers.get(o.id)||0});
// Preserve the existing derived paving verge and shoreline, including exclusion probes.
const edgeMaterial=source.materials.cityPaving?'cityPaving':'paving',paving=terrain.surfaces.filter(s=>s.walkable&&['paving','cityPaving'].includes(s.material)&&s.vertices&&Math.max(...s.vertices.map(v=>v[2]))<.10),edge={position:[],normal:[],uv:[],color:[],ownerId:[],feather:[]},size=source.materials[edgeMaterial]?.texture?.worldSize||4;
boundarySegments(paving.map(s=>s.polygon),(a,b,n)=>{const outer=[a[0]+n[0]*.10,a[1]+n[1]*.10],probe=[(a[0]+b[0])/2+n[0]*.085,(a[1]+b[1])/2+n[1]*.085];if(!window.AstraeonSpatialV3.pointIn({x:probe[0],y:probe[1]},terrain.walkablePolygon)||spatial.blocked(...probe,.02))return;const v=[[...a,spatial.elevationAt(...a)+.010],[...b,spatial.elevationAt(...b)+.010],[b[0]+n[0]*.10,b[1]+n[1]*.10,terrain.elevation+.011],[...outer,terrain.elevation+.011]];appendMesh(edge,{vertices:v,faces:[[0,1,2,3]],material:edgeMaterial,walkable:true,uvs:[v.map(p=>[p[0]/size,p[1]/size])]},source.lighting);edge.feather.push(1,1,0,1,0,0)});
distribute(edge,'paving-verges',{kind:'verge',material:edgeMaterial,opacity:true});
const water=terrain.surfaces.find(s=>s.material==='water'),shore={position:[],normal:[],uv:[],color:[],ownerId:[],feather:[]};
if(water)boundarySegments([terrain.walkablePolygon,...terrain.surfaces.filter(s=>s.walkable&&s.role==='green'&&s.material==='grass').map(s=>s.polygon)],(a,b,n)=>{const z=water.vertices[0][2]+.013,points=[[a[0]+n[0]*1.35,a[1]+n[1]*1.35,z],[b[0]+n[0]*1.35,b[1]+n[1]*1.35,z],[b[0]+n[0]*2.4,b[1]+n[1]*2.4,z],[a[0]+n[0]*2.4,a[1]+n[1]*2.4,z]];if(!window.AstraeonSpatialV3.pointIn({x:points[0][0],y:points[0][1]},water.polygon))return;appendMesh(shore,{vertices:points,faces:[[0,1,2,3]],walkable:true},source.lighting);shore.feather.push(.45,.45,0,.45,0,0)});
distribute(shore,'shoreline',{kind:'shore',opacity:true});
// Exactly the previous half-meter highest-floor receivers, generated once offline.
for(let y=b.minY;y<b.maxY;y+=.5)for(let x=b.minX;x<b.maxX;x+=.5){if(!spatial.containsGround(x+.25,y+.25))continue;const batch={position:[],uv:[]};for(const [dx,dy] of [[0,0],[.5,0],[.5,.5],[0,0],[.5,.5],[0,.5]]){batch.position.push(x+dx,y+dy,spatial.elevationAt(x+dx,y+dy)+.015);batch.uv.push((x+dx-b.minX)/(b.maxX-b.minX),(y+dy-b.minY)/(b.maxY-b.minY))}distribute(batch,'floor-shadow/'+Math.floor(x/16)+','+Math.floor(y/16),{kind:'shadow'})}
const chunkRecords=[];let rawBytes=0,compressedBytes=0;
for(const [id,chunk] of [...chunks].sort(([a],[b])=>a.localeCompare(b))){
 const pieces=[],batches=[];let offset=0;
 for(const batch of chunk.batches.values()){
  const fields=attrs.filter(([n])=>batch[n]),stride=fields.reduce((s,[,n])=>s+n,0),lookup=new Map(),values=[],indices=[];
  // Float32 conversion is identical to the original THREE.Float32BufferAttribute.
  const arrays=Object.fromEntries(fields.map(([n])=>[n,new Float32Array(batch[n])])),vertices=batch.position.length/3;
  for(let i=0;i<vertices;i++){const row=fields.flatMap(([n,k])=>Array.from(arrays[n].subarray(i*k,(i+1)*k))),key=row.join(',');let index=lookup.get(key);if(index===undefined){index=lookup.size;lookup.set(key,index);values.push(...row)}indices.push(index)}
  const attributes={},unique=lookup.size;
  let fieldOffset=0;for(const [name,itemSize] of fields){const out=new Float32Array(unique*itemSize);for(let i=0;i<unique;i++)for(let j=0;j<itemSize;j++)out[i*itemSize+j]=values[i*stride+fieldOffset+j];const buffer=Buffer.from(out.buffer);attributes[name]={offset,count:unique,itemSize};pieces.push(buffer);offset+=buffer.length;fieldOffset+=itemSize}
  const index=new Uint32Array(indices),indexOffset=offset,bytes=Buffer.from(index.buffer);pieces.push(bytes);offset+=bytes.length;
  const owners=[];for(const owner of batch.owners){const last=owners.at(-1);if(last?.[1]===owner)last[0]++;else owners.push([1,owner])}
  batches.push({key:batch.key,material:batch.material,kind:batch.kind,opacity:batch.opacity||false,attributes,index:{offset:indexOffset,count:indices.length},owners});
 }
 const binary=Buffer.concat(pieces),gzip=zlib.gzipSync(binary,{level:9}),binaryURL=folder+id+'-'+hash(gzip).slice(0,12)+'.bin.gz';fs.writeFileSync(new URL(binaryURL,root),gzip);
 const payload={format:'astraeon-render-buffer-v1',id,sourceSHA256:sourceHash,binary:{url:binaryURL,bytes:gzip.length,decodedBytes:binary.length,sha256:hash(gzip)},bounds:chunk.bounds,batches};
 const manifest=writeJSON(folder+id+'.json',payload);chunkRecords.push({id,bounds:chunk.bounds,...manifest,compressedBytes:gzip.length,decodedBytes:binary.length});rawBytes+=binary.length;compressedBytes+=gzip.length;console.log(id,gzip.length,binary.length);
}
// The real source collision/elevation geometry is retained, without render-only arrays.
const collisionPart=p=>Object.fromEntries(Object.entries(p).filter(([k])=>!['uvs','bakedLighting','vertexOpacity'].includes(k)));
const semantic={...source,streaming:{format:'astraeon-zone-semantics-v1',sourceSHA256:sourceHash},objects:source.objects.map(o=>({...o,parts:o.parts.filter(p=>p.role==='solid').map(collisionPart)})),terrain:{...terrain,surfaces:terrain.surfaces.map(collisionPart)}};
const semantics=writeJSON(folder+'semantics.json',semantic);
const assetFiles=new Set(Object.values(source.materials).flatMap(m=>m.texture?[m.texture.file]:[]));assetFiles.add(source.lighting.groundShadow.file);
const assets=writeJSON(folder+'assets.json',{version:1,assets:[...assetFiles].sort().map(url=>({url,bytes:read(url).length,sha256:hash(read(url))}))});
const zone=writeJSON(folder+'zone.json',{version:1,id:source.id,sourceSHA256:sourceHash,cellSize,semantics,assets,owners,chunks:chunkRecords});
writeJSON('world/v3/world-manifest.json',{version:1,defaultZone:source.id,zones:{[source.id]:zone}});
const report={sourceSHA256:sourceHash,conversionSHA256:hash(Buffer.from(appendCode+boundaryCode)),chunks:chunkRecords.length,triangles:triangleCount,rawBytes,compressedBytes,semanticsBytes:semantics.bytes,zoneManifestBytes:zone.bytes,assetCount:assetFiles.size,sourceUnchanged:hash(read('world/v3/wayfarer-spatial.json'))===sourceHash};
const review=process.env.ASTRAEON_CAPITAL_REVIEW_DIR||'docs/review/wayfarer-capital-v76';
fs.mkdirSync(new URL(review+'/mobile-streaming/',root),{recursive:true});
writeJSON(review+'/mobile-streaming/chunk-build.json',report);console.log(JSON.stringify(report,null,2));
