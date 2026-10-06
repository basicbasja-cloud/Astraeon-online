/* Repair native patrol waypoints displaced by the revised occupied ground. */
const fs=require('fs');global.window={};require('../navigation.js');require('../world/v3/spatial.js');
const w=JSON.parse(fs.readFileSync('world/v3/wayfarer-spatial.json')),s=window.AstraeonSpatialV3.compile(w),blocked=(x,y)=>s.blocked(x,y,.28),spawn={x:w.spawn[0],y:w.spawn[1]},nav=window.AstraeonNavigation;
const path=(a,b)=>nav.route({x:a[0],y:a[1]},{x:b[0],y:b[1]},blocked,{bounds:s.bounds,reach:.05,step:.5}),reachable=new Map();
function connected(p){const k=p.join(',');if(!reachable.has(k))reachable.set(k,!blocked(...p)&&!!path([spawn.x,spawn.y],p));return reachable.get(k)}
function snap(p){if(connected(p))return p;const candidates=[];for(let ix=-24;ix<=24;ix++)for(let iy=-24;iy<=24;iy++){const q=[Math.round(p[0]*2)/2+ix*.5,Math.round(p[1]*2)/2+iy*.5];if(!blocked(...q))candidates.push(q)}candidates.sort((a,b)=>Math.hypot(a[0]-p[0],a[1]-p[1])-Math.hypot(b[0]-p[0],b[1]-p[1]));for(const q of candidates)if(connected(q))return q;throw Error('No reachable native patrol margin '+p)}
const repairs={},checks=[];
for(const o of w.objects)for(const a of o.walkers||[]){
 const old=a.route;if(old.every((p,i)=>nav.clear({x:p[0],y:p[1]},{x:old[(i+1)%old.length][0],y:old[(i+1)%old.length][1]},blocked))){checks.push({id:a.id,changed:false});continue}
 const points=old.map(snap),fixed=[points[0]];
 for(let i=0;i<points.length;i++){const route=path(points[i],points[(i+1)%points.length]);if(!route)throw Error('Native patrol connection failed '+a.id);for(const q of route)if(Math.hypot(q.x-fixed.at(-1)[0],q.y-fixed.at(-1)[1])>.01)fixed.push([q.x,q.y]);}
 if(Math.hypot(fixed.at(-1)[0]-fixed[0][0],fixed.at(-1)[1]-fixed[0][1])<.01)fixed.pop();
 for(let i=0;i<fixed.length;i++){const p=fixed[i],q=fixed[(i+1)%fixed.length];if(!nav.clear({x:p[0],y:p[1]},{x:q[0],y:q[1]},blocked))throw Error('Patrol leg still clips native geometry '+a.id)}
 repairs[a.id]=fixed;checks.push({id:a.id,changed:true,originalWaypoints:old.length,finalWaypoints:fixed.length});
}
fs.writeFileSync(process.argv[2],JSON.stringify({version:72,checks,repairs},null,2)+'\n');console.log(JSON.stringify(checks));
