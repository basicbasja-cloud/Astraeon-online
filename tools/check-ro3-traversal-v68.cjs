/* Review the native occupied ground after house/fountain changes. */
const fs=require('fs'),crypto=require('crypto');global.window={};require('../navigation.js');require('../world/v3/spatial.js');
const w=JSON.parse(fs.readFileSync('world/v3/wayfarer-spatial.json')),s=window.AstraeonSpatialV3.compile(w),start={x:w.spawn[0],y:w.spawn[1]};
const routeChecks=[],patrolChecks=[],repairs={};
for(const stop of [...w.route,...w.objects.flatMap(o=>(o.services||[]).map(a=>({name:a.name||a.id,position:a.position})))]){
 const [x,y]=stop.position,path=s.route(start,{x,y});routeChecks.push({name:stop.name,position:[x,y],blocked:s.blocked(x,y),reachable:!!path,waypoints:path?.length||0});
}
function nearest(p){if(!s.blocked(...p,.28))return p;for(let r=.25;r<=5;r+=.25)for(let k=0;k<32;k++){const q=[p[0]+r*Math.cos(k*Math.PI/16),p[1]+r*Math.sin(k*Math.PI/16)];if(!s.blocked(...q,.28))return q;}throw Error('No free waypoint '+p)}
for(const o of w.objects)for(const a of o.walkers||[]){
 let blocked=0;const route=a.route;
 for(let i=0;i<route.length;i++){const p=route[i],q=route[(i+1)%route.length],steps=Math.max(1,Math.ceil(Math.hypot(q[0]-p[0],q[1]-p[1])/.18));for(let j=0;j<=steps;j++)if(s.blocked(p[0]+(q[0]-p[0])*j/steps,p[1]+(q[1]-p[1])*j/steps,.18))blocked++;}
 const report={id:a.id,blockedSamples:blocked};patrolChecks.push(report);
 if(!blocked)continue;
 const points=route.map(nearest),fixed=[points[0]];
 for(let i=0;i<points.length;i++){const p=points[i],q=points[(i+1)%points.length],path=window.AstraeonNavigation.route({x:p[0],y:p[1]},{x:q[0],y:q[1]},(x,y)=>s.blocked(x,y,.28),{bounds:s.bounds,reach:.05,step:.5});if(!path)throw Error('Unreachable patrol leg '+a.id);fixed.push(...path.map(p=>[p.x,p.y]));}
 while(fixed.length>1&&Math.hypot(fixed.at(-1)[0]-fixed[0][0],fixed.at(-1)[1]-fixed[0][1])<.1)fixed.pop();
 repairs[a.id]=fixed;report.repairedWaypoints=fixed.length;
}
const report={version:68,routeChecks,patrolChecks,repairs,pass:routeChecks.every(r=>!r.blocked&&r.reachable)&&!Object.keys(repairs).length};
report.sourceSHA256=crypto.createHash('sha256').update(fs.readFileSync('world/v3/wayfarer-spatial.json')).digest('hex');
const path=process.argv[2]||'/tmp/astraeon-ro3-68/traversal.json';fs.writeFileSync(path,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({routes:routeChecks.length,unreachable:routeChecks.filter(r=>!r.reachable||r.blocked),patrols:patrolChecks.length,repairs:Object.keys(repairs).length}));

if(!report.pass)process.exitCode=1;
