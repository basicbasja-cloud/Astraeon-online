/* Reusable physical town kit. Ground coordinates and gameplay remain unchanged.
 * Artwork is partitioned into opaque layers; never fade an entire building. */
(() => {
'use strict';
const C=window.AstraeonContent,V=window.AstraeonView;
const district=id=>id==='guild-hall'?'civic':id==='artisan-workshop'?'forge':id==='east-inn'?'inn':id==='moon-shrine'?'shrine':id==='market-shop'?'market':'residential';
const roofMasks={
 forge:[[.05,.43],[.23,.15],[.66,.11],[.86,.28],[.91,.46],[.46,.63],[.05,.48]],
 inn:[[.08,.27],[.25,.06],[.59,.04],[.92,.16],[.96,.40],[.64,.45],[.30,.37],[.08,.31]],
 shrine:[[.29,.20],[.40,.09],[.80,.25],[.96,.51],[.64,.67],[.58,.40]],
 cottage:[[.04,.32],[.22,.06],[.65,.02],[.93,.18],[.98,.43],[.62,.53],[.24,.44]],
 civic:[[.04,.30],[.18,.06],[.52,0],[.77,.08],[.98,.37],[.75,.49],[.39,.46],[.08,.40]]
};
const groundPolygons={
 forge:[[.03,.83],[.54,.65],[.97,.78],[.58,.99]],
 inn:[[.12,.80],[.62,.65],[.96,.78],[.58,.99]],
 shrine:[[.09,.88],[.60,.70],[.93,.84],[.44,.98]],
 cottage:[[.12,.83],[.65,.70],[.93,.83],[.55,.97]],
 civic:[[.06,.82],[.58,.69],[.96,.83],[.45,.98]]
};
const metadata=Object.fromEntries(C.townObjects.filter(o=>o.building||o.tree).map(o=>{
 if(C.structures?.[o.id])return [o.id,C.structures[o.id]];
 const b=C.townBlocks.find(b=>b.id===o.id),roof=roofMasks[o.id==='guild-hall'?'civic':o.art];
 return [o.id,{district:district(o.id),groundPolygon:groundPolygons[o.id==='guild-hall'?'civic':o.art],renderAnchor:o.id==='guild-hall'?[.4,.91]:o.pack==='district'?[o.art==='shrine'?.42:o.art==='inn'?.43:.5,.94]:[.48,.94],footprint:b?{x:b.x,y:b.y,w:b.w,h:b.h}:null,entrance:[o.x,o.y],light:[-.7,-.6],collision:b||null,
 layers:o.tree?[{name:'trunk',region:[0,.62,1,1],depth:[o.x,o.y]},{name:'canopy',region:[0,0,1,.62],depth:[o.x+.35,o.y+.45]}]:[
 {name:'rear-wall',region:[.62,roof?0:.42,1,1],exclude:roof,depth:b?[b.x+b.w,b.y+b.h*.55]:[o.x,o.y]},
 {name:'frontage',region:[0,roof?0:.42,.62,1],exclude:roof,depth:b?[b.x+b.w*.45,b.y+b.h]:[o.x,o.y]},
 {name:'roof',region:[0,0,1,roof?1:.42],polygon:roof,depth:b?[b.x+b.w*.5,b.y+b.h]:[o.x,o.y]}]}];
}));
const layerCache=new WeakMap();
function layers(objects){if(layerCache.has(objects))return layerCache.get(objects);const result=objects.flatMap(o=>{
 const m=metadata[o.id];return m?m.layers.map(layer=>({x:layer.depth[0],y:layer.depth[1],prop:{...o,structuralLayer:layer,structure:m}})):[{x:o.x,y:o.y,prop:o}];
});
 for(const part of C.nativeWorld?.spatial.parts||[])if(part.objectId.startsWith('town-wall-')){
  const [x,y]=part.footprint.reduce((sum,v)=>[sum[0]+v[0]/part.footprint.length,sum[1]+v[1]/part.footprint.length],[0,0]);result.push({x,y,prop:{pack:'native-masonry',part}});
 }
 layerCache.set(objects,result);return result}
function face(ctx,iso,points,height,fill,stroke='#6e6354'){
 ctx.beginPath();points.forEach(([x,y,z=height],i)=>{const p=iso(x,y,z);i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y)});ctx.closePath();ctx.fillStyle=fill;ctx.fill();if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=.65*V.zoom;ctx.stroke()}
}
function platform(ctx,iso,b,height=7){
 const x=b.x-.12,y=b.y-.12,w=b.w+.24,h=b.h+.24;
 face(ctx,iso,[[x,y+h,height],[x+w,y+h,height],[x+w,y+h,0],[x,y+h,0]],height,'#8e8066');
 face(ctx,iso,[[x+w,y,height],[x+w,y+h,height],[x+w,y+h,0],[x+w,y,0]],height,'#756c5b');
 face(ctx,iso,[[x,y],[x+w,y],[x+w,y+h],[x,y+h]],height,'#c6b99b','#e2d6bb');
 // Courses and joints communicate a load-bearing foundation.
 for(let i=0;i<w;i+=.6){const a=iso(x+i,y+h,height),z=iso(x+i,y+h,0);ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(z.x,z.y);ctx.strokeStyle='#645d4f';ctx.stroke()}
}
function ground(ctx,iso){
 if(C.nativeWorld){
  ctx.beginPath();for(const shadow of C.nativeWorld.spatial.shadowPolygons){shadow.polygon.forEach(([x,y],i)=>{const p=iso(x,y);i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y)});ctx.closePath()}
  ctx.fillStyle='#25382e23';ctx.fill();return;
 }
 for(const o of C.townObjects.filter(o=>o.building)){
  const m=metadata[o.id],points=m?.groundPolygon;if(!points)continue;
  const p=iso(o.x,o.y),[ax,ay]=m.renderAnchor;
  // Casting geometry belongs to the artwork's ground plane, not its collision rectangle.
  ctx.beginPath();points.forEach(([x,y],i)=>{const sx=p.x+(x-ax)*o.w+14,sy=p.y+(y-ay)*o.h+9;i?ctx.lineTo(sx,sy):ctx.moveTo(sx,sy)});ctx.closePath();ctx.fillStyle='#26392e2b';ctx.fill();
 }

 // Raised planting edge around the civic square: open circulation is retained.
 for(const [x,y] of [[10.9,12.6],[18,12.6]])platform(ctx,iso,{x:x-.45,y:y-.32,w:.9,h:.64},5);
}
const entrances=C.townObjects.filter(o=>o.building&&metadata[o.id]?.footprint);
function elevationAt(x,y){
 if(C.nativeWorld)return C.nativeWorld.spatial.elevationAt(x,y);
 let elevation=0;
 for(const o of entrances){
  if(Math.abs(x-o.x)>.65||y<o.y-.28||y>o.y+.55)continue;
  const rise=o.id==='guild-hall'?.18:.10;
  elevation=Math.max(elevation,rise*Math.max(0,Math.min(1,(o.y+.55-y)/.75)));
 }
 return elevation;
}
window.AstraeonTownStructure={metadata,layers,ground,platform,elevationAt};
})();
