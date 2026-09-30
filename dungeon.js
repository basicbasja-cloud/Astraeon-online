/* One authored Moonveil ruin: three chambers and a guardian court, not new regions. */
(() => {
'use strict';
const rooms=[
 {name:'Lantern Vestibule',x:3,y:16,w:10,h:9,start:[8,22],spawns:[[6,19,4],[10,19,5]],door:{x:8,y:14.8,label:'Moonlit Gallery'}},
 {name:'Moonlit Gallery',x:3,y:4,w:10,h:10,start:[8,12],spawns:[[6,8,7],[10,8,4],[8,6,5]],door:{x:14.5,y:9,label:'Sentinel Cloister'}},
 {name:'Sentinel Cloister',x:16,y:4,w:11,h:10,start:[18,9],spawns:[[21,6,6],[24,8,7],[20,11,5],[24,12,4]],door:{x:21,y:14.8,label:'Guardian Court'}},
 {name:'Guardian Court',x:16,y:16,w:11,h:9,start:[21,18],spawns:[[21,21,1]],door:null}
];
const corridors=[{x:6.7,y:13,w:2.6,h:4},{x:12,y:7.7,w:5,h:2.6},{x:19.7,y:13,w:2.6,h:4}];
const inside=(x,y,r,margin=0)=>x>=r.x+margin&&x<=r.x+r.w-margin&&y>=r.y+margin&&y<=r.y+r.h-margin;
const walls=[];
function segment(x,y,w,h){if(w>.01&&h>.01)walls.push({x,y,w,h})}
// Gaps match authored passages. Walls are actual navigation obstacles.
for(let i=0;i<rooms.length;i++){
 const r=rooms[i];for(const side of ['north','south','east','west']){
  const gap=side==='north'&&(i===0||i===3)?21:side==='south'&&(i===1||i===2)?8:side==='east'&&i===1?9:side==='west'&&i===2?9:null;
  const horizontal=side==='north'||side==='south',at=horizontal?(side==='north'?r.y:r.y+r.h):(side==='west'?r.x:r.x+r.w),begin=horizontal?r.x:r.y,end=horizontal?r.x+r.w:r.y+r.h;
  const center=horizontal?(i===0||i===1?8:21):9;
  if(gap!==null){if(horizontal){segment(begin,at-.14,center-1.3-begin,.28);segment(center+1.3,at-.14,end-center-1.3,.28)}else{segment(at-.14,begin,.28,center-1.3-begin);segment(at-.14,center+1.3,.28,end-center-1.3)}}
  else if(horizontal)segment(begin,at-.14,end-begin,.28);else segment(at-.14,begin,.28,end-begin);
 }
}
const props=[
 {art:'arch',x:8,y:16.2,w:150,h:168},
 {art:'arch',x:8,y:13.9,w:150,h:168},
 {art:'pillar',x:13,y:7.5,w:58,h:102},
 {art:'pillar',x:16,y:10.5,w:58,h:102},
 {art:'arch',x:21,y:16.2,w:160,h:179},
 {art:'terrace',x:21,y:23.5,w:205,h:145},
 {art:'bamboo',x:3.5,y:24.5,w:97,h:134},
 {art:'bamboo',x:12.7,y:5.5,w:87,h:124},
 {art:'bamboo',x:26.8,y:12.8,w:90,h:128},
 {art:'pillar',x:18,y:23.3,w:58,h:102},
 {art:'pillar',x:24,y:23.3,w:58,h:102}
].map((p,i)=>({...p,pack:'secondary',id:'moonveil-'+i}));
const wallObjects=window.AstraeonEnvironment?.ruinWalls(walls)||[];
const extraProps=window.AstraeonEnvironment?[...rooms.flatMap((r,i)=>[
 window.AstraeonEnvironment.prop('ruin','brazier',r.x+1.5,r.y+1.3,47),
 window.AstraeonEnvironment.prop('ruin','brazier',r.x+r.w-1.5,r.y+1.3,47),
 window.AstraeonEnvironment.prop('ruin',i===3?'altar':'rubble',r.x+1,r.y+r.h-1,88),
]),window.AstraeonEnvironment.prop('ruin','seal',21,21.4,220),window.AstraeonEnvironment.prop('ruin','column',18,17.7,78),window.AstraeonEnvironment.prop('ruin','column',24,17.7,78)]:[];
for(let i=0;i<22&&window.AstraeonEnvironment;i++){const x=(i*7.3)%39-4,y=(i*11.7)%35-4;if(rooms.some(r=>inside(x,y,r,-1))||corridors.some(r=>inside(x,y,r,-1)))continue;extraProps.push(window.AstraeonEnvironment.prop('ruin',i%3?'rubble':'column',x,y,100+i%4*18,{building:true}))}
props.push(...extraProps);
function ground(ctx,iso){window.AstraeonEnvironment.terrain(ctx,iso,'stone');}
function blocked(x,y,wave){const accessible=[...rooms.slice(0,wave+1),...corridors.slice(0,wave)];return !accessible.some(r=>inside(x,y,r,.12))||walls.some(r=>inside(x,y,{x:r.x-.18,y:r.y-.18,w:r.w+.36,h:r.h+.36}))}
window.AstraeonDungeon={rooms,corridors,walls,wallObjects,props,ground,blocked};
})();
