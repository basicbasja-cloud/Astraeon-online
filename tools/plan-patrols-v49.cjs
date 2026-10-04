/* Re-plan source patrol legs against the current exported native geometry.
 * Writes an authoring input, never a runtime collision/navigation override. */
const fs=require('node:fs'),path=require('node:path');
global.window={};require('../navigation.js');require('../world/v3/spatial.js');
const scene=require('../world/v3/wayfarer-spatial.json'),world=window.AstraeonSpatialV3.compile(scene),result={};
function free(point){
 const [x,y]=point;if(!world.blocked(x,y))return {x,y};
 const near=world.navCells.filter(p=>p.walkable).sort((a,b)=>Math.hypot(a.x-x,a.y-y)-Math.hypot(b.x-x,b.y-y))[0];
 if(Math.hypot(near.x-x,near.y-y)>4)throw Error('Patrol stop needs a deliberate replacement: '+point);
 return {x:near.x,y:near.y};
}
for(const walker of scene.objects.flatMap(o=>o.walkers||[])){
 const stops=walker.route.map(free),points=[stops[0]];
 for(let i=0;i<stops.length;i++){
  const start=points.at(-1),goal=stops[(i+1)%stops.length],route=world.route(start,goal);
  if(!route)throw Error('Unreachable patrol leg '+walker.id+'/'+i);
  for(const p of route){if(Math.hypot(p.x-points.at(-1).x,p.y-points.at(-1).y)>.01)points.push(p)}
 }
 if(Math.hypot(points.at(-1).x-points[0].x,points.at(-1).y-points[0].y)<.01)points.pop();
 for(let i=0;i<points.length;i++)if(!window.AstraeonNavigation.clear(points[i],points[(i+1)%points.length],world.blocked))throw Error('Unclear planned patrol '+walker.id+'/'+i);
 result[walker.id]=points.map(p=>[p.x,p.y]);
}
const target=path.join(__dirname,'../authoring/patrol-routes-v49.json');fs.writeFileSync(target,JSON.stringify(result,null,2)+'\n');console.log('Planned',Object.keys(result).length,'closed source patrols');
