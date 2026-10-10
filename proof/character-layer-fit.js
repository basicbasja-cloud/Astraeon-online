(async function(){
'use strict';
const $=id=>document.getElementById(id),config=new URLSearchParams(location.search).get('config');
if(!config)throw Error('Supply ?config=PATH to an authored layer-fit study');
const response=await fetch(config);if(!response.ok)throw Error('Cannot load layer-fit configuration');const c=await response.json();
if(c.status!=='PARTIAL_STUDY'||c.visualApproval!==false)throw Error('Layer-fit studies cannot claim production approval');
const images={};await Promise.all(Object.entries(c.sources).map(([id,source])=>new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{images[id]=im;resolve()};im.onerror=()=>reject(Error('Cannot load '+id));im.src=source.file})));
const motion=await(await fetch(c.motionTemplate)).json(),timing=motion.actions[c.action].directions[c.direction].frames.map(f=>f.durationMs),duration=timing.reduce((a,b)=>a+b,0);
if(c.timelineToPose.length!==timing.length)throw Error('Study mapping differs from motion clock');
for(const [i,p]of c.poses.entries()){const option=document.createElement('option');option.value=i;option.textContent=p.name;$('phase').append(option)}
let elapsed=0,last=performance.now(),playing=true,forced=null;const ctx=$('stage').getContext('2d');
function sample(){let t=elapsed%duration,index=0;while(index<timing.length-1&&t>=timing[index])t-=timing[index++];return c.poses[forced===null?c.timelineToPose[index]:forced]}
function raster(id,rect,pivot,anchor,scale){ctx.drawImage(images[id],...rect,anchor[0]-pivot[0]*scale,anchor[1]-pivot[1]*scale,rect[2]*scale,rect[3]*scale)}
function draw(){const p=sample();ctx.clearRect(0,0,960,640);ctx.save();ctx.translate(160,0);ctx.scale(2,2);
 const bodyPoint=point=>[c.root[0]+(point[0]-c.bodyRoot[0])*c.bodyScale,c.root[1]+(point[1]-c.bodyRoot[1])*c.bodyScale];
 const head=bodyPoint(p.neck),grip=bodyPoint(p.hand),bodyRect=[p.cell[0]*512,p.cell[1]*512,512,512];
 for(const layer of p.drawOrder||['body','head','weapon']){
  if(!$(layer).checked)continue;
  if(layer==='body')raster('body',bodyRect,c.bodyRoot,c.root,c.bodyScale);
  if(layer==='head')raster('head',c.headRect,c.headPivot,head,c.headScale);
  if(layer==='weapon')raster('weapon',bodyRect,p.weaponGrip,grip,c.weaponScale);
 }
 // Fingers are a body-owned foreground pass; no hand pixels are in weapon art.
 if($('body').checked&&$('weapon').checked){ctx.save();ctx.beginPath();p.fingers.forEach((point,i)=>{const q=bodyPoint(point);i?ctx.lineTo(...q):ctx.moveTo(...q)});ctx.closePath();ctx.clip();raster('body',bodyRect,c.bodyRoot,c.root,c.bodyScale);ctx.restore()}
 if($('debug').checked){for(const [label,point]of [['neck',head],['hand / grip',grip],['root',c.root]]){ctx.fillStyle='#b9ff89';ctx.beginPath();ctx.arc(...point,2,0,Math.PI*2);ctx.fill();ctx.font='7px system-ui';ctx.fillText(label,point[0]+4,point[1])}}
 ctx.restore();$('status').textContent=c.direction+' · '+c.action+' · '+p.name+' · partial study';$('diagnostics').textContent=JSON.stringify({elapsedMs:elapsed,neck:head,hand:grip,weaponGrip:p.weaponGrip,visualApproval:false,limitations:c.limitations},null,2);
}
$('play').onclick=()=>{playing=!playing;forced=null;$('play').textContent=playing?'Pause':'Play'};
$('phase').onchange=()=>{forced=Number($('phase').value);playing=false;$('play').textContent='Play';draw()};
for(const id of ['body','head','weapon','debug'])$(id).onchange=draw;
window.characterLayerFit={snapshot:()=>({elapsedMs:elapsed,playing,pose:sample().name,visualApproval:false}),pause:()=>{playing=false},
 describe:()=>({direction:c.direction,action:c.action,timing,timelineToPose:c.timelineToPose,poseNames:c.poses.map(p=>p.name)}),
 render:(pose,visible=['body','head','weapon'])=>{if(!Number.isInteger(pose)||pose<0||pose>=c.poses.length)throw Error('Unknown pose');playing=false;forced=pose;for(const id of ['body','head','weapon'])$(id).checked=visible.includes(id);draw();return $('stage').toDataURL('image/png')}};
function tick(now){if(playing)elapsed+=Math.min(now-last,100);last=now;draw();requestAnimationFrame(tick)}requestAnimationFrame(tick);
})().catch(e=>{document.getElementById('status').textContent=e.message;console.error(e)});
