/* Bounded adapter: existing painted Canvas systems consume authored placement,
 * footprint and circulation records. No renderer, save or gameplay dependency. */
(() => {
'use strict';
function content(scene,baseline){
 window.AstraeonSpatialV3.validate(scene);
 const townObjects=scene.objects.filter(o=>o.presentation).map(o=>({id:o.id,...o.presentation.sprite,x:o.presentation.position[0],y:o.presentation.position[1]}));
 const townBlocks=scene.objects.flatMap(o=>o.parts.filter(p=>p.role==='solid').map(p=>{const xs=p.vertices.map(v=>v[0]),ys=p.vertices.map(v=>v[1]),minX=Math.min(...xs),minY=Math.min(...ys),maxX=Math.max(...xs),maxY=Math.max(...ys);
  // These bounds serve minimap/presentation only. Gameplay queries the compiled
  // authored polygons below, including gate openings and registered foundations.
  return{id:o.id,x:minX,y:minY,w:maxX-minX,h:maxY-minY,...(o.presentation?.sprite.art==='fountain'?{kind:'fountain'}:{})}}));
 const forecourts=scene.terrain.surfaces.filter(s=>['forecourt','market'].includes(s.role)).map(s=>({id:s.objectId||s.id,points:s.polygon}));
 const townRoads=scene.terrain.surfaces.filter(s=>s.centerline).map(s=>({role:s.legacyRole,points:s.centerline,width:s.width}));
 const plaza=scene.terrain.surfaces.find(s=>s.role==='plaza');
 const services=scene.objects.flatMap(o=>(o.services||[]).map(s=>({id:s.id,name:s.name,kind:s.kind,symbol:s.symbol,x:s.position[0],y:s.position[1],objectId:o.id})));
 const walkers=scene.objects.flatMap(o=>o.walkers||[]);
 const structures=Object.fromEntries(scene.objects.filter(o=>o.presentation?.structure).map(o=>{const p=o.presentation,s=structuredClone(p.structure);s.entrance=s.entrance.map((v,i)=>v+p.position[i]);s.layers=s.layers.map(l=>({...l,depth:l.depth.map((v,i)=>v+p.position[i])}));return [o.id,s]}));
 const transitions=scene.objects.flatMap(o=>o.portals.filter(p=>p.transition).map(p=>({zone:0,x:p.anchor[0],y:p.anchor[1],...p.transition,returnArrival:p.approach.slice(0,2)})));
 return Object.freeze({...baseline,townObjects,townBlocks,forecourts,townRoads,services,walkers:walkers.length?walkers:baseline.walkers,structures,transitions,districts:scene.districts||baseline.districts,
  goldenScene:{...baseline.goldenScene,center:scene.route.find(s=>s.name==='Plaza')?.position||baseline.goldenScene.center,plaza:plaza?.polygon||baseline.goldenScene.plaza},
  nativeWorld:{id:scene.id,source:scene.source,version:scene.version,layoutId:scene.layoutId,spawn:scene.spawn,safeSpawn:scene.safeSpawn||scene.spawn,spatial:window.AstraeonSpatialV3.compile(scene)},
  spaces:scene.terrain.surfaces.filter(s=>['yard','garden','green'].includes(s.role)),lights:scene.objects.flatMap(o=>o.lights.map(l=>({...l,objectId:o.id})))});
}
window.AstraeonTownImportV3={content};
})();
