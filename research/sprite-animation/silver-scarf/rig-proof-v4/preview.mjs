// Research compositor: complete source strips, packed per-pixel depth, shared clock.
import {createAttackSampler} from './attack-sampling.mjs';
const $=id=>document.getElementById(id), canvas=$('sprite'),ctx=canvas.getContext('2d');
const manifest=await fetch('rig-manifest.json').then(r=>{if(!r.ok)throw Error('Missing manifest');return r.json()});
const durations=manifest.clips.attack.frame_delays_ms,total=durations.reduce((a,b)=>a+b,0);
const starts=durations.map((_,i)=>durations.slice(0,i).reduce((a,b)=>a+b,0));
const sampleAttack=createAttackSampler(manifest.clips.attack,manifest.trail);
export const pairedAttackViews={S:'SW',SW:'SW',W:'NW',NW:'NW',N:'NE',NE:'NE',E:'SE',SE:'SE'};
const state={elapsed:0,playing:true,once:false,interrupted:false,direction:'SE',parts:[],loading:true,error:null,frame:0,revision:0,loadedFacing:null,renderCount:0};
const fixed=manifest.default.filter(p=>!p.startsWith('hair.')&&!p.startsWith('torso.')&&!p.startsWith('cape.')&&!p.startsWith('weapon.'));
const strips=new Map();let generation=0,pendingFacing=null;
for(const d of manifest.directions){const opt=new Option(d,d);$('direction').add(opt)}$('direction').value='SE';
async function pixels(url){
 const response=await fetch(url);if(!response.ok)throw Error(`Missing required part: ${url}`);
 const bitmap=await createImageBitmap(await response.blob());
 const tmp=document.createElement('canvas');tmp.width=bitmap.width;tmp.height=bitmap.height;
 if(tmp.width!==2048||tmp.height!==256){bitmap.close();throw Error(`Incompatible canvas: ${url}`)}
 const c=tmp.getContext('2d',{willReadFrequently:true});c.drawImage(bitmap,0,0);bitmap.close();
 const data=c.getImageData(0,0,tmp.width,tmp.height).data;tmp.width=1;tmp.height=1;return data;
}
function equipment(){
 const parts=[...fixed];for(const id of ['hair','torso','cape','weapon','headgear']){const p=$(id).value;if(p)parts.push(p)}
 return parts.filter(p=>!($('headgear').value==='headgear.helm'&&p.startsWith('hair.')));
}
async function loadFacing(dir,token){
 for(;;){
   if(token!==generation)return;
   if(state.loadedFacing===dir)return;
   if(pendingFacing){await pendingFacing;continue}
   strips.clear();state.loadedFacing=null;
   pendingFacing=Promise.all(Object.keys(manifest.parts).map(async part=>{
     const [color,depth]=await Promise.all([pixels(`strips/${part}/${dir}.png`),pixels(`strips/${part}/${dir}.depth.png`)]);
     return [part,{color,depth}];
   })).then(entries=>{for(const [part,data]of entries)strips.set(part,data);state.loadedFacing=dir});
   try{await pendingFacing}finally{pendingFacing=null}
 }
}
async function stage(){
 const token=++generation,requested=$('direction').value,dir=$('viewPolicy').value==='paired'?pairedAttackViews[requested]:requested,parts=equipment();state.loading=true;state.error=null;status();
 try{
   // Load every compatible item for this facing once: bounded at 17 strips.
   // Subsequent swaps are atomic and need no asynchronous texture load.
   await loadFacing(dir,token);
   if(token!==generation)return;
   state.parts=parts;state.direction=dir;state.loading=false;state.revision++;render();status();
 }catch(e){if(token!==generation)return;state.error=e.message;state.loading=false;status()}
}
function poseIndex(ms){return sampleAttack(ms).frame}
function depthAt(data,j){const n=data[j]*65536+data[j+1]*256+data[j+2];return n===16777215?Infinity:n}
const source=new Float32Array(256*256*4),nearest=new Float32Array(256*256),native=ctx.createImageData(128,128);
function render(){
 if(state.loading||state.error||!state.parts.length)return;
 const {frame,fxGain}=sampleAttack(state.elapsed,state.interrupted);state.frame=frame;$('pose').value=frame;
 source.fill(0);nearest.fill(Infinity);
 for(const part of state.parts){
   const {color,depth}=strips.get(part);
   for(let y=0;y<256;y++)for(let x=0;x<256;x++){
     const n=y*256+x,j=(y*2048+frame*256+x)*4,z=depthAt(depth,j);
     if(color[j+3]&&z<nearest[n]){nearest[n]=z;const k=n*4;source[k]=color[j];source[k+1]=color[j+1];source[k+2]=color[j+2];source[k+3]=color[j+3]/255}
   }
 }
 if($('fx').checked&&fxGain>0){
   const weapon=state.parts.find(p=>p.startsWith('weapon.'));
   const {color,depth}=strips.get(weapon.replace('weapon.','trail.'));
   for(let y=0;y<256;y++)for(let x=0;x<256;x++){
     const n=y*256+x,j=(y*2048+frame*256+x)*4,z=depthAt(depth,j),k=n*4,a=color[j+3]/255*fxGain;
     if(a&&z<nearest[n]){const old=source[k+3],combined=a+old*(1-a);for(let c=0;c<3;c++)source[k+c]=(color[j+c]*a+source[k+c]*old*(1-a))/combined;source[k+3]=combined}
   }
 }
 // Premultiplied 2x2 area resolve, preserving RGB around transparent edges.
 for(let y=0;y<128;y++)for(let x=0;x<128;x++){
   const indices=[((y*2)*256+x*2)*4,((y*2)*256+x*2+1)*4,((y*2+1)*256+x*2)*4,((y*2+1)*256+x*2+1)*4];
   const k=(y*128+x)*4,a=indices.reduce((s,j)=>s+source[j+3],0);
   for(let c=0;c<3;c++)native.data[k+c]=a?Math.round(indices.reduce((s,j)=>s+source[j+c]*source[j+3],0)/a):0;
   native.data[k+3]=Math.round(a*255/4);
 }
 ctx.putImageData(native,0,0);
 if($('diagnostic').checked){const p=manifest.poses.find(p=>p.direction===state.direction&&p.index===frame);for(const [name,color]of [['right_grip','#60dcff'],['left_hand','#ffb679']]){const [x,y]=p[name];ctx.strokeStyle=color;ctx.lineWidth=1;ctx.beginPath();ctx.arc(x/2,y/2,3,0,Math.PI*2);ctx.stroke()} }
 state.renderCount++;status();
}
function status(){
 $('status').className=state.error?'error':'';
 const phase=manifest.poses.find(p=>p.direction===state.direction&&p.index===state.frame)?.phase;
 $('status').textContent=state.error?state.error:`${state.loading?'Loading complete facing…':$('direction').value+' → '+state.direction+' · '+phase}\nPose ${state.frame+1}/8 · phase ${Math.round(state.elapsed)} / ${total} ms\nSword: anatomical RIGHT hand · ${state.interrupted?'interrupted / trail cleared':state.playing?'playing':'paused'}\n${state.parts.length} equipped parts · ${strips.size} cached item strips`;
}
for(const id of ['direction','viewPolicy','hair','torso','cape','weapon','headgear'])$(id).addEventListener('change',stage);
for(const id of ['fx','diagnostic'])$(id).addEventListener('change',render);
$('play').onclick=()=>{state.playing=!state.playing;state.once=false;if(state.playing)state.interrupted=false;$('play').textContent=state.playing?'Pause':'Play';status()};
$('once').onclick=()=>{state.elapsed=0;state.playing=true;state.once=true;state.interrupted=false;render();$('play').textContent='Pause'};
$('stop').onclick=()=>{state.elapsed=0;state.playing=false;state.once=false;state.interrupted=true;render();$('play').textContent='Play'};
$('pose').oninput=()=>{state.elapsed=starts[Number($('pose').value)];state.playing=false;state.once=false;state.interrupted=false;render();$('play').textContent='Play'};
$('defaults').onclick=()=>{for(const id of ['hair','torso','cape','weapon','headgear'])$(id).selectedIndex=0;stage()};
let last=performance.now(),previousSignature='';
function tick(now){const delta=Math.min(now-last,100);last=now;if(state.playing){state.elapsed+=delta*Number($('speed').value);if(state.elapsed>=total){if(state.once){state.elapsed=0;state.playing=false;state.once=false;state.interrupted=true;$('play').textContent='Play'}else state.elapsed%=total}}
 const sample=sampleAttack(state.elapsed,state.interrupted);
 const signature=[sample.frame,sample.fxGain.toFixed(2),state.direction,state.revision,state.interrupted].join(':');if(signature!==previousSignature){previousSignature=signature;render()}
 requestAnimationFrame(tick);
}
// Read-only diagnostics plus deliberate timeline stepping for browser validation.
window.rigProof={state,manifest,setTime(ms){state.playing=false;state.interrupted=false;state.elapsed=ms;render()},getPixels(){return Array.from(ctx.getImageData(0,0,128,128).data)},cacheBytes(){return [...strips.values()].reduce((n,s)=>n+s.color.byteLength+s.depth.byteLength,0)},ready:()=>!state.loading&&!state.error};
await stage();requestAnimationFrame(tick);
