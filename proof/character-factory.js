(async()=>{
'use strict';
const $=id=>document.getElementById(id),ctx=$('stage').getContext('2d'),images=new Map();
let catalog,clip,frame=0,elapsed=0,last=0,ticket=0,ready=false,checking=false;
function choices(id,values,preferred){const field=$(id);field.replaceChildren(...values.map(v=>new Option(v,v)));field.value=values.includes(preferred)?preferred:values[0];field.disabled=values.length<2}
function url(path){return new URL(path,document.baseURI).href}
function image(path){const key=url(path);if(!images.has(key))images.set(key,new Promise((resolve,reject)=>{const im=new Image();im.onload=()=>{if(im.width!==512||im.height!==512)reject(Error('Wrong canvas '+path));else resolve(im)};im.onerror=()=>{images.delete(key);reject(Error('Missing image '+path))};im.src=key}));return images.get(key)}
function partSkin(role){return role==='HeadHair'?$('head').value:role==='Weapon'?$('weapon').value:$('body').value}
async function draw(){if(!clip||checking)return;const serial=++ticket;ready=false;
 try{const view=clip.views[$('direction').value],selected=clip.order.filter(role=>$('layers').querySelector(`[data-role="${role}"]`).checked);
 const parts=await Promise.all(selected.map(role=>image(view[partSkin(role)][role][frame])));const previous=$('onion').checked&&frame>0?await Promise.all(selected.map(role=>image(view[partSkin(role)][role][frame-1]))):[];if(serial!==ticket)return;
 ctx.clearRect(0,0,512,512);ctx.globalAlpha=.25;for(const im of previous)ctx.drawImage(im,0,0);ctx.globalAlpha=1;for(const im of parts)ctx.drawImage(im,0,0);ready=true;
 $('frame').value=frame;$('frame-label').textContent=`${frame} / ${clip.durations.length-1}`;
 $('status').textContent=`${clip.label} · ${$('direction').value} · frame ${frame} · ${clip.durations[frame]} ms\n${clip.loop?'Loop':'One shot, holds final frame'} · fixed 512 × 512 source canvas\n${clip.limits.join('\n')}${$('onion').checked?'\nPrevious frame overlay enabled':''}`;
 }catch(error){if(serial!==ticket)return;ctx.clearRect(0,0,512,512);$('speed').value='0';$('status').textContent=error.message;console.error(error)}
}
function chooseDirection(){ctx.clearRect(0,0,512,512);$('status').textContent='Loading matching pose assets…';const skins=Object.keys(clip.views[$('direction').value]);for(const id of ['head','body','weapon'])choices(id,skins,$(id).value);images.clear();frame=0;elapsed=0;last=0;draw()}
function chooseAction(){clip=catalog.actions[$('action').value];$('speed').value='0';choices('direction',Object.keys(clip.views),$('direction').value);$('frame').max=clip.durations.length-1;$('layers').replaceChildren(...clip.order.map(role=>{const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.checked=true;input.dataset.role=role;label.append(input,role);return label}));chooseDirection()}
function seek(value){$('speed').value='0';frame=Math.max(0,Math.min(clip.durations.length-1,value));elapsed=clip.durations.slice(0,frame).reduce((a,b)=>a+b,0);draw()}
$('action').onchange=chooseAction;$('direction').onchange=chooseDirection;for(const id of ['head','body','weapon'])$(id).onchange=()=>{last=0;draw()};$('layers').onchange=draw;$('onion').onchange=draw;$('frame').oninput=()=>seek(Number($('frame').value));$('previous').onclick=()=>seek(frame-1);$('next').onclick=()=>seek(frame+1);
$('replay').onclick=()=>{frame=0;elapsed=0;last=0;$('speed').value='1';draw()};$('speed').onchange=()=>{elapsed=clip.durations.slice(0,frame).reduce((a,b)=>a+b,0);last=0};
function tick(now){if(clip&&ready&&!checking&&last&&Number($('speed').value)>0){const total=clip.durations.reduce((a,b)=>a+b,0);elapsed+=(now-last)*Number($('speed').value);if(clip.loop)elapsed%=total;else elapsed=Math.min(elapsed,total);let time=elapsed,next=0;while(next<clip.durations.length-1&&time>=clip.durations[next])time-=clip.durations[next++];if(next!==frame){frame=next;draw()}if(!clip.loop&&elapsed===total)$('speed').value='0'}last=now;requestAnimationFrame(tick)}
$('check-integrity').onclick=async()=>{
 if(checking||!catalog)return;checking=true;ticket++;$('speed').value='0';$('check-integrity').disabled=true;
 const controls=[...document.querySelectorAll('.controls select,.controls button,#frame,#layers input,#onion')];const disabled=controls.map(el=>el.disabled);controls.forEach(el=>el.disabled=true);
 const records=[],canvas=document.createElement('canvas');canvas.width=canvas.height=512;const c=canvas.getContext('2d',{willReadFrequently:true});
 const pixels=()=>c.getImageData(0,0,512,512).data;
 function mismatches(a,b){let n=0;for(let j=0;j<a.length;j+=4)if(a[j+3]!==b[j+3]||((a[j+3]||b[j+3])&&(a[j]!==b[j]||a[j+1]!==b[j+1]||a[j+2]!==b[j+2])))n++;return n}
 try{
  for(const [action,entry] of Object.entries(catalog.actions)){
   if(!entry.masters)continue;
   for(const direction of Object.keys(entry.views)){
    images.clear();
    for(let i=0;i<entry.durations.length;i++){
     const view=entry.views[direction].gold,master=await image(entry.masters[direction][i]);c.clearRect(0,0,512,512);c.drawImage(master,0,0);const expected=pixels();c.clearRect(0,0,512,512);
     for(const role of ['BodyCostume','HeadHair','Weapon'])c.drawImage(await image(view[role][i]),0,0);
     const core=mismatches(expected,pixels());c.clearRect(0,0,512,512);
     for(const role of entry.order.filter(r=>!r.startsWith('WeaponLight')))c.drawImage(await image(view[role][i]),0,0);
     records.push({action,direction,frame:i,coreMismatchPixels:core,withHandOccluderMismatchPixels:mismatches(expected,pixels())});
     $('integrity-status').textContent=`Checked ${records.length} original frame views…`;
    }
   }
  }
  const result={status:'PIXEL_RECONSTRUCTION_ONLY',frames:records.length,coreFailedFrames:records.filter(r=>r.coreMismatchPixels>0).length,withHandOccluderFailedFrames:records.filter(r=>r.withHandOccluderMismatchPixels>0).length,records};
  $('integrity-results').textContent=JSON.stringify(result,null,2);$('integrity-status').textContent=`${result.frames} checked · core mismatches in ${result.coreFailedFrames} frames · with hand occluder mismatches in ${result.withHandOccluderFailedFrames} frames. Motion/semantic approval remains separate.`;
 }catch(error){$('integrity-status').textContent=error.message;console.error(error)}
 finally{checking=false;images.clear();controls.forEach((el,i)=>el.disabled=disabled[i]);$('check-integrity').disabled=false;last=0;draw()}
};
try{const response=await fetch('character-factory-catalog.json');if(!response.ok)throw Error('Cannot load review catalog');catalog=await response.json();$('check-integrity').disabled=false;choices('action',Object.keys(catalog.actions),'BasicAttack');chooseAction();requestAnimationFrame(tick);if(new URLSearchParams(location.search).get('integrity')==='1'){$('integrity').open=true;$('check-integrity').click()}}catch(error){$('status').textContent=error.message;console.error(error)}
})();
