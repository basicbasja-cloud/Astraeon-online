(async()=>{
'use strict';
const $=id=>document.getElementById(id),main=$('master').getContext('2d'),runtime=$('runtime').getContext('2d');
let data,masters,guides,frame=0,time=0,last=0,ready=false;
function path(p){return new URL(p,document.baseURI).href}
async function load(p,size){const im=new Image();im.src=path(p);await im.decode();if(im.width!==size||im.height!==size)throw Error('Unexpected image canvas: '+p);return im}
function draw(){if(!ready)return;main.clearRect(0,0,768,768);if($('onion').checked){main.globalAlpha=.2;main.drawImage(masters[(frame+15)%16],0,0);main.globalAlpha=1}main.drawImage(masters[frame],0,0);if($('guide').checked){main.globalAlpha=.35;main.drawImage(guides[frame],0,0,768,768);main.globalAlpha=1}
runtime.clearRect(0,0,240,240);runtime.drawImage(masters[frame],0,0,240,240);
if($('root').checked)for(const [c,x,y]of [[main,384,550.4],[runtime,120,172]]){c.strokeStyle='#eb3483';c.lineWidth=1;c.beginPath();c.moveTo(x-8,y);c.lineTo(x+8,y);c.moveTo(x,y-8);c.lineTo(x,y+8);c.stroke()}
$('frame').value=frame;$('frame-label').textContent=`${frame} / 15`;$('status').textContent=`Walk · SW · source ${data.source_frames[frame]}f · painted frame ${frame}\nAll 16 masters predecoded · ${data.durations_ms[frame].toFixed(4)} ms · one fixed 768 canvas → 240 raster\n${data.status} · overlay tools do not change the underlying masters`;
document.body.dataset.frame=frame;
}
function seek(n){$('speed').value='0';frame=Math.max(0,Math.min(15,n));time=data.durations_ms.slice(0,frame).reduce((a,b)=>a+b,0);last=0;draw()}
function tick(now){if(ready&&last&&Number($('speed').value)>0){time=(time+(now-last)*Number($('speed').value))%data.durations_ms.reduce((a,b)=>a+b,0);let t=time,i=0;while(i<15&&t>=data.durations_ms[i])t-=data.durations_ms[i++];if(i!==frame){frame=i;draw()}}last=now;requestAnimationFrame(tick)}
$('previous').onclick=()=>seek(frame-1);$('next').onclick=()=>seek(frame+1);$('frame').oninput=()=>seek(Number($('frame').value));$('replay').onclick=()=>{frame=0;time=0;last=0;$('speed').value='1';draw()};$('speed').onchange=()=>{time=data.durations_ms.slice(0,frame).reduce((a,b)=>a+b,0);last=0};for(const id of ['guide','onion','root'])$(id).onchange=draw;$('background').onchange=()=>{for(const id of ['master','runtime'])$(id).style.background=$('background').value};$('zoom').onclick=()=>$('runtime').classList.toggle('zoom');
try{const response=await fetch('swordsman-master-review.json');if(!response.ok)throw Error('Missing master review manifest');data=await response.json();if(data.frames.length!==16||data.durations_ms.length!==16)throw Error('Incomplete Walk sequence');[masters,guides]=await Promise.all([Promise.all(data.frames.map(p=>load(p,768))),Promise.all(data.guides.map(p=>load(p,1536)))]);for(const id of ['normal','slow','receipt'])$(id).href=path(data.downloads[id]);$('reference').src=path(data.reference);ready=true;document.body.dataset.ready='true';for(const id of ['speed','previous','next','replay','frame'])$(id).disabled=false;draw();requestAnimationFrame(tick)}catch(e){$('status').textContent=e.message;document.body.dataset.ready='error';console.error(e)}
})();
