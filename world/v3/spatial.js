/* Authoring-independent spatial contract. Meshes are the only source of solids,
 * visibility regions and shadow volumes; consumers never author replacement boxes. */
(() => {
'use strict';
const pointIn=(p,poly)=>{let inside=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const a=poly[i],b=poly[j];if((a[1]>p.y)!==(b[1]>p.y)&&p.x<(b[0]-a[0])*(p.y-a[1])/(b[1]-a[1])+a[0])inside=!inside}return inside};
function hull(points){const p=[...new Map(points.map(a=>[a.join(','),a])).values()].sort((a,b)=>a[0]-b[0]||a[1]-b[1]);const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);const chain=[];for(const a of p){while(chain.length>1&&cross(chain.at(-2),chain.at(-1),a)<=0)chain.pop();chain.push(a)}const lower=chain.slice();chain.length=0;for(const a of p.reverse()){while(chain.length>1&&cross(chain.at(-2),chain.at(-1),a)<=0)chain.pop();chain.push(a)}return lower.slice(0,-1).concat(chain.slice(0,-1))}
function distanceToEdge(p,a,b){const dx=b[0]-a[0],dy=b[1]-a[1],k=Math.max(0,Math.min(1,((p.x-a[0])*dx+(p.y-a[1])*dy)/(dx*dx+dy*dy||1)));return Math.hypot(p.x-a[0]-k*dx,p.y-a[1]-k*dy)}
function touches(p,poly,radius){return pointIn(p,poly)||poly.some((a,i)=>distanceToEdge(p,a,poly[(i+1)%poly.length])<radius)}
function validate(scene){
 if(scene.version!==3||!scene.terrain||!scene.navigation||!scene.lighting||!Array.isArray(scene.objects))throw Error('Invalid world v3 contract');
 const bounds=scene.terrain.bounds;if(!bounds||![bounds.minX,bounds.minY,bounds.maxX,bounds.maxY,scene.terrain.elevation,scene.navigation.actorRadius,scene.navigation.cellSize,...scene.lighting.sun.cast].every(Number.isFinite)||bounds.maxX<=bounds.minX||bounds.maxY<=bounds.minY||scene.navigation.actorRadius<=0||scene.navigation.cellSize<=0)throw Error('Invalid terrain/navigation/lighting');
 const ids=new Set(),parts=new Set();for(const o of scene.objects){if(ids.has(o.id)||!o.family||!o.parts?.length)throw Error('Invalid or duplicate object '+o.id);ids.add(o.id);for(const p of o.parts){if(parts.has(p.id)||!p.vertices?.length||!p.faces?.length||!['solid','overhead','decorative'].includes(p.role))throw Error('Invalid mesh '+p.id);parts.add(p.id);if(p.vertices.some(v=>v.length!==3||v.some(n=>!Number.isFinite(n))))throw Error('Non-finite mesh');if(p.faces.some(f=>f.length<3||f.some(i=>!Number.isInteger(i)||i<0||i>=p.vertices.length)))throw Error('Invalid face indices')}
  for(const portal of o.portals||[])if(!portal.anchor?.every(Number.isFinite)||!portal.approach?.every(Number.isFinite)||portal.anchor.length!==3||portal.approach.length!==3)throw Error('Invalid portal '+o.id);
 }
 return scene;
}
function compile(scene){
 validate(scene);const parts=scene.objects.flatMap(o=>o.parts.map(p=>({...p,objectId:o.id,family:o.family,footprint:hull(p.vertices.map(v=>v.slice(0,2))),height:Math.max(...p.vertices.map(v=>v[2])),base:Math.min(...p.vertices.map(v=>v[2]))}))),solids=parts.filter(p=>p.role==='solid'),overheads=parts.filter(p=>p.role==='overhead');
 const bounds=scene.terrain.bounds,radius=scene.navigation.actorRadius;
 const blocked=(x,y,r=radius)=>x<bounds.minX+r||x>bounds.maxX-r||y<bounds.minY+r||y>bounds.maxY-r||solids.some(p=>touches({x,y},p.footprint,r));
 const portalMap=scene.objects.flatMap(o=>(o.portals||[]).map(p=>({...p,objectId:o.id,range:p.range||1})));
 const navCells=[];for(let y=bounds.minY+.5;y<bounds.maxY;y+=scene.navigation.cellSize)for(let x=bounds.minX+.5;x<bounds.maxX;x+=scene.navigation.cellSize)navCells.push({x,y,walkable:!blocked(x,y)});
 const shadowPolygons=parts.filter(p=>p.shadow).map(p=>({id:p.id,polygon:hull(p.vertices.map(v=>[v[0]+scene.lighting.sun.cast[0]*v[2],v[1]+scene.lighting.sun.cast[1]*v[2]]))}));
 return {scene,parts,solids,overheads,portals:portalMap,navCells,shadowPolygons,blocked,
  elevationAt:()=>scene.terrain.elevation,
  interactionAt:(x,y)=>portalMap.find(p=>Math.hypot(x-p.approach[0],y-p.approach[1])<=p.range),
  route:(start,goal)=>window.AstraeonNavigation.route(start,goal,blocked,{bounds,reach:.26}),
  bounds};
}
window.AstraeonSpatialV3={compile,validate,hull,pointIn,touches};
})();
