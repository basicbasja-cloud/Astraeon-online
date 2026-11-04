(async()=>{
'use strict';
const $=id=>document.getElementById(id),ctx=$('stage').getContext('2d'),images=new Map();
let catalog,clip,frame=0,elapsed=0,last=0,ticket=0,ready=false;
function choices(id,values,preferred){const field=$(id);field.replaceChildren(...values.map(v=>new Option(v,v)));field.value=values.includes(preferred)?preferred:values[0];field.disabled=values.length<2}
function url(path){return new URL(path,document.baseURI).href}
function image(path){const key=url(path);if(!images.has(key))images.set(key,new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{if(im.width!==512||im.height!==512)reject(Error('Wrong canvas '+path));else resolve(im)};im.onerror=()=>{images.delete(key);reject(Error('Missing image '+path))};im.src=key}));return images.get(key)}
function partSkin(role){return role==='HeadHair'?$('head').value:role==='Weapon'?$('weapon').value:$('body').value}
async function draw(){if(!clip)return;const serial=++ticket;ready=false;
 try{const view=clip.views[$('direction').value],selected=clip.order.filter(role=>$('layers').querySelector(`[data-role="${role}"]`).checked);
 const parts=await Promise.all(selected.map(role=>image(view[partSkin(role)][role][frame])));if(serial!==ticket)return;
 ctx.clearRect(0,0,512,512);for(const im of parts)ctx.drawImage(im,0,0);ready=true;
 $('frame').value=frame;$('frame-label').textContent=`${frame} / ${clip.durations.length-1}`;
 $('status').textContent=`${clip.label} · ${$('direction').value} · frame ${frame} · ${clip.durations[frame]} ms\n${clip.loop?'Loop':'One shot, holds final frame'} · fixed 512 × 512 source canvas\n${clip.limits.join('\n')}`;
 }catch(error){if(serial!==ticket)return;ctx.clearRect(0,0,512,512);$('speed').value='0';$('status').textContent=error.message;console.error(error)}
}
function chooseDirection(){ctx.clearRect(0,0,512,512);$('status').textContent='Loading matching pose assets…';const skins=Object.keys(clip.views[$('direction').value]);for(const id of ['head','body','weapon'])choices(id,skins,$(id).value);images.clear();frame=0;elapsed=0;last=0;draw()}
function chooseAction(){clip=catalog.actions[$('action').value];$('speed').value='0';choices('direction',Object.keys(clip.views),$('direction').value);$('frame').max=clip.durations.length-1;$('layers').replaceChildren(...clip.order.map(role=>{const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.checked=true;input.dataset.role=role;label.append(input,role);return label}));chooseDirection()}
function seek(value){$('speed').value='0';frame=Math.max(0,Math.min(clip.durations.length-1,value));elapsed=clip.durations.slice(0,frame).reduce((a,b)=>a+b,0);draw()}
$('action').onchange=chooseAction;$('direction').onchange=chooseDirection;for(const id of ['head','body','weapon'])$(id).onchange=()=>{last=0;draw()};$('layers').onchange=draw;$('frame').oninput=()=>seek(Number($('frame').value));$('previous').onclick=()=>seek(frame-1);$('next').onclick=()=>seek(frame+1);
$('replay').onclick=()=>{frame=0;elapsed=0;last=0;$('speed').value='1';draw()};$('speed').onchange=()=>{elapsed=clip.durations.slice(0,frame).reduce((a,b)=>a+b,0);last=0};
function tick(now){if(clip&&ready&&last&&Number($('speed').value)>0){const total=clip.durations.reduce((a,b)=>a+b,0);elapsed+=(now-last)*Number($('speed').value);if(clip.loop)elapsed%=total;else elapsed=Math.min(elapsed,total);let time=elapsed,next=0;while(next<clip.durations.length-1&&time>=clip.durations[next])time-=clip.durations[next++];if(next!==frame){frame=next;draw()}if(!clip.loop&&elapsed===total)$('speed').value='0'}last=now;requestAnimationFrame(tick)}
try{const response=await fetch('character-factory-catalog.json');if(!response.ok)throw Error('Cannot load review catalog');catalog=await response.json();choices('action',Object.keys(catalog.actions),'BasicAttack');chooseAction();requestAnimationFrame(tick)}catch(error){$('status').textContent=error.message;console.error(error)}
})();
