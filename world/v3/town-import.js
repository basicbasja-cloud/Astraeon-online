/* Bounded adapter: existing painted Canvas systems consume authored placement,
 * footprint and circulation records. No renderer, save or gameplay dependency. */
(() => {
'use strict';
function content(scene,baseline){
 window.AstraeonSpatialV3.validate(scene);
 const townObjects=scene.objects.filter(o=>o.presentation).map(o=>({id:o.id,...o.presentation.sprite,x:o.presentation.position[0],y:o.presentation.position[1]}));
 const townBlocks=scene.objects.flatMap(o=>o.parts.filter(p=>p.role==='solid').map(p=>{const xs=p.vertices.map(v=>v[0]),ys=p.vertices.map(v=>v[1]),minX=Math.min(...xs),minY=Math.min(...ys),maxX=Math.max(...xs),maxY=Math.max(...ys);
  // The current client's collision adapter supports axis-aligned footprints.
  // Reject new rotated/polygon solids until its polygon query is migrated.
  if(p.vertices.some(v=>![minX,maxX].some(x=>Math.abs(x-v[0])<.00001)||![minY,maxY].some(y=>Math.abs(y-v[1])<.00001)))throw Error('Polygon collision adapter required for '+p.id);
  return{id:o.id,x:minX,y:minY,w:maxX-minX,h:maxY-minY,...(o.presentation?.sprite.art==='fountain'?{kind:'fountain'}:{})}}));
 const forecourts=scene.terrain.surfaces.filter(s=>s.role==='forecourt').map(s=>({id:s.objectId,points:s.polygon}));
 const townRoads=scene.terrain.surfaces.filter(s=>s.centerline).map(s=>({role:s.legacyRole,points:s.centerline,width:s.width}));
 const plaza=scene.terrain.surfaces.find(s=>s.role==='plaza');
 return Object.freeze({...baseline,townObjects,townBlocks,forecourts,townRoads,goldenScene:{...baseline.goldenScene,plaza:plaza?.polygon||baseline.goldenScene.plaza},nativeWorld:{id:scene.id,source:scene.source,version:scene.version}});
}
window.AstraeonTownImportV3={content};
})();
