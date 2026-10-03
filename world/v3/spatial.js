/* Authoring-independent spatial contract. Meshes are the only source of solids,
 * visibility regions and shadow volumes; consumers never author replacement boxes. */
(() => {
'use strict';
const pointIn=(p,poly)=>{let inside=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const a=poly[i],b=poly[j];if((a[1]>p.y)!==(b[1]>p.y)&&p.x<(b[0]-a[0])*(p.y-a[1])/(b[1]-a[1])+a[0])inside=!inside}return inside};
function hull(points){const p=[...new Map(points.map(a=>[a.join(','),a])).values()].sort((a,b)=>a[0]-b[0]||a[1]-b[1]);const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);const chain=[];for(const a of p){while(chain.length>1&&cross(chain.at(-2),chain.at(-1),a)<=0)chain.pop();chain.push(a)}const lower=chain.slice();chain.length=0;for(const a of p.reverse()){while(chain.length>1&&cross(chain.at(-2),chain.at(-1),a)<=0)chain.pop();chain.push(a)}return lower.slice(0,-1).concat(chain.slice(0,-1))}
function distanceToEdge(p,a,b){const dx=b[0]-a[0],dy=b[1]-a[1],k=Math.max(0,Math.min(1,((p.x-a[0])*dx+(p.y-a[1])*dy)/(dx*dx+dy*dy||1)));return Math.hypot(p.x-a[0]-k*dx,p.y-a[1]-k*dy)}
function touches(p,poly,radius){return pointIn(p,poly)||poly.some((a,i)=>distanceToEdge(p,a,poly[(i+1)%poly.length])<radius)}
function triangleHeight(x,y,a,b,c){const den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1]);if(Math.abs(den)<1e-9)return null;const u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den,v=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den;return u>=-1e-6&&v>=-1e-6&&u+v<=1+1e-6?u*a[2]+v*b[2]+(1-u-v)*c[2]:null}
function validateGeometry(p){
 if(!p.vertices?.length||!p.faces?.length||p.vertices.some(v=>v.length!==3||v.some(n=>!Number.isFinite(n)))||p.faces.some(f=>f.length<3||f.some(i=>!Number.isInteger(i)||i<0||i>=p.vertices.length)))throw Error('Invalid mesh geometry '+(p.id||'terrain'));
 if(p.uvs&&(p.uvs.length!==p.faces.length||p.uvs.some((uvs,i)=>uvs.length!==p.faces[i].length||uvs.some(uv=>uv.length!==2||!uv.every(Number.isFinite)))))throw Error('Invalid authored UVs '+(p.id||'terrain'));
}
function validate(scene){
 if(scene.version!==3||!scene.terrain||!scene.navigation||!scene.lighting||!Array.isArray(scene.objects))throw Error('Invalid world v3 contract');
 const bounds=scene.terrain.bounds;if(!bounds||![bounds.minX,bounds.minY,bounds.maxX,bounds.maxY,scene.terrain.elevation,scene.navigation.actorRadius,scene.navigation.cellSize,...scene.lighting.sun.cast].every(Number.isFinite)||bounds.maxX<=bounds.minX||bounds.maxY<=bounds.minY||scene.navigation.actorRadius<=0||scene.navigation.cellSize<=0)throw Error('Invalid terrain/navigation/lighting');
 if(scene.terrain.vertices)validateGeometry(scene.terrain);for(const surface of scene.terrain.surfaces||[])if(surface.vertices)validateGeometry(surface);
 const ids=new Set(),parts=new Set();for(const o of scene.objects){if(ids.has(o.id)||!o.family||!o.parts?.length)throw Error('Invalid or duplicate object '+o.id);ids.add(o.id);for(const p of o.parts){if(parts.has(p.id)||!['solid','overhead','decorative'].includes(p.role))throw Error('Invalid mesh '+p.id);parts.add(p.id);validateGeometry(p)}
  for(const portal of o.portals||[])if(!portal.anchor?.every(Number.isFinite)||!portal.approach?.every(Number.isFinite)||portal.anchor.length!==3||portal.approach.length!==3)throw Error('Invalid portal '+o.id);
  for(const service of o.services||[])if(service.position?.length!==3||!service.position.every(Number.isFinite)||!['guild','craft','market','travel','housing','journal','inn','shrine'].includes(service.kind))throw Error('Invalid service '+o.id);
  for(const walker of o.walkers||[])if(!walker.route?.length||walker.route.some(p=>p.length!==2||!p.every(Number.isFinite))||!(walker.pace>0))throw Error('Invalid walker '+o.id);
  for(const layer of o.presentation?.structure?.layers||[])if(layer.depth?.length!==2||!layer.depth.every(Number.isFinite)||layer.region?.length!==4||!layer.region.every(Number.isFinite))throw Error('Invalid painted part '+o.id);
 }
 return scene;
}
function compile(scene){
 validate(scene);const parts=scene.objects.flatMap(o=>o.parts.map(p=>({...p,objectId:o.id,family:o.family,footprint:hull(p.vertices.map(v=>v.slice(0,2))),height:Math.max(...p.vertices.map(v=>v[2])),base:Math.min(...p.vertices.map(v=>v[2]))}))),solids=parts.filter(p=>p.role==='solid'),overheads=parts.filter(p=>p.role==='overhead');
 const bounds=scene.terrain.bounds,radius=scene.navigation.actorRadius;
 for(const p of solids)p.bounds={minX:Math.min(...p.footprint.map(v=>v[0])),maxX:Math.max(...p.footprint.map(v=>v[0])),minY:Math.min(...p.footprint.map(v=>v[1])),maxY:Math.max(...p.footprint.map(v=>v[1]))};
 // Broad phase for the expanded town. Query only nearby geometry, including
 // boundary cells and radius overlap; exact polygon/contact tests stay unchanged.
 const bucketSize=8,index=items=>{const buckets=new Map();for(const item of items){const b=item.bounds;for(let y=Math.floor(b.minY/bucketSize);y<=Math.floor(b.maxY/bucketSize);y++)for(let x=Math.floor(b.minX/bucketSize);x<=Math.floor(b.maxX/bucketSize);x++){const key=x+','+y;if(!buckets.has(key))buckets.set(key,[]);buckets.get(key).push(item)}}return buckets};
 const nearby=(buckets,x,y,r=0)=>{const result=new Set();for(let by=Math.floor((y-r)/bucketSize);by<=Math.floor((y+r)/bucketSize);by++)for(let bx=Math.floor((x-r)/bucketSize);bx<=Math.floor((x+r)/bucketSize);bx++)for(const p of buckets.get(bx+','+by)||[])result.add(p);return result};
 const solidIndex=index(solids);
 const floorPolygons=scene.terrain.walkablePolygon?[scene.terrain.walkablePolygon,...scene.terrain.surfaces.filter(s=>s.walkable).map(s=>s.polygon)]:null;
 const onLand=(x,y)=>!floorPolygons||floorPolygons.some(poly=>pointIn({x,y},poly));
 const blocked=(x,y,r=radius)=>x<bounds.minX+r||x>bounds.maxX-r||y<bounds.minY+r||y>bounds.maxY-r||!onLand(x,y)||[...nearby(solidIndex,x,y,r)].some(p=>x>=p.bounds.minX-r&&x<=p.bounds.maxX+r&&y>=p.bounds.minY-r&&y<=p.bounds.maxY+r&&touches({x,y},p.footprint,r));
 const portalMap=scene.objects.flatMap(o=>(o.portals||[]).map(p=>({...p,objectId:o.id,range:p.range||1})));
 const navCells=[];for(let y=bounds.minY+.5;y<bounds.maxY;y+=scene.navigation.cellSize)for(let x=bounds.minX+.5;x<bounds.maxX;x+=scene.navigation.cellSize)navCells.push({x,y,walkable:!blocked(x,y)});
 const shadowPolygons=parts.filter(p=>p.shadow).map(p=>({id:p.id,polygon:hull(p.vertices.map(v=>[v[0]+scene.lighting.sun.cast[0]*v[2],v[1]+scene.lighting.sun.cast[1]*v[2]]))}));
 const floorTriangles=scene.terrain.surfaces.filter(s=>s.walkable&&s.vertices&&s.faces).flatMap(s=>s.faces.flatMap(f=>f.slice(1,-1).map((_,i)=>[s.vertices[f[0]],s.vertices[f[i+1]],s.vertices[f[i+2]]])));
 const floorIndex=index(floorTriangles.map(t=>({t,bounds:{minX:Math.min(...t.map(v=>v[0])),maxX:Math.max(...t.map(v=>v[0])),minY:Math.min(...t.map(v=>v[1])),maxY:Math.max(...t.map(v=>v[1]))}})));
 const elevationAt=(x,y)=>{let height=scene.terrain.elevation;for(const {t} of nearby(floorIndex,x,y)){const h=triangleHeight(x,y,...t);if(h!==null)height=Math.max(height,h)}return height};
 return {scene,parts,solids,overheads,portals:portalMap,navCells,shadowPolygons,blocked,
  elevationAt,
  interactionAt:(x,y)=>portalMap.find(p=>Math.hypot(x-p.approach[0],y-p.approach[1])<=p.range),
  route:(start,goal)=>window.AstraeonNavigation.route(start,goal,blocked,{bounds,reach:.26,step:bounds.maxX-bounds.minX>80?1:.5}),
  bounds};
}
window.AstraeonSpatialV3={compile,validate,hull,pointIn,touches};
})();
