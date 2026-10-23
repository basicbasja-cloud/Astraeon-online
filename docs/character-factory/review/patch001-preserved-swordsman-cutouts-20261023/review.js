(async()=>{
const data=await(await fetch('samples.json')).json(),api=window.AstraeonModularSprites,images={},checks=[];
const root='../../../../',canvases=Object.fromEntries(['source','actual','detail'].map(id=>[id,document.getElementById(id)]));
const native=document.createElement('canvas');native.width=native.height=768;const nctx=native.getContext('2d');
const reference=document.createElement('canvas');reference.width=reference.height=240;const rctx=reference.getContext('2d');
function ctx(c){const x=c.getContext('2d');x.imageSmoothingEnabled=true;x.imageSmoothingQuality='high';return x}
async function load(url){const im=new Image();im.src=url;await im.decode();return im}
await Promise.all(Object.entries(data.atlases).map(async([id,a])=>{images[id]=await load(a.file);if(images[id].naturalWidth!==a.width||images[id].naturalHeight!==a.height)throw Error('Atlas size mismatch')}));
function sample(f,selected){return{canvas:data.canvas,sockets:{root:[120,172]},layers:f.parts.filter(p=>selected(p.role)).map(({atlasId,rect,offset})=>({atlasId,rect,offset}))}}
function draw(f,selected,c=canvases.actual){const cctx=ctx(c);cctx.clearRect(0,0,c.width,c.height);const scale=c.width/240;api.draw(cctx,sample(f,selected),images,{x:120*scale,y:172*scale,scale})}
function compare(a,b){const aa=a.getContext('2d').getImageData(0,0,240,240).data,bb=b.getContext('2d').getImageData(0,0,240,240).data;let pixels=0,max=0;for(let k=0;k<aa.length;k+=4){let different=false;for(let j=0;j<4;j++){const d=Math.abs(aa[k+j]-bb[k+j]);different||=d!==0;max=Math.max(max,d)}if(different)pixels++}return{changed_pixels:pixels,max_channel_difference:max}}
function expected(){rctx.clearRect(0,0,240,240);rctx.imageSmoothingEnabled=true;rctx.imageSmoothingQuality='high';rctx.drawImage(native,0,0,240,240)}
for(const f of data.frames){
 const master=await load(root+f.master_file);nctx.clearRect(0,0,768,768);nctx.drawImage(master,0,0);expected();draw(f,r=>!r.startsWith('WeaponLight'));const base=compare(reference,canvases.actual);
 const sources=await Promise.all(f.parts.map(p=>load(root+p.source_file)));nctx.clearRect(0,0,768,768);sources.forEach(im=>nctx.drawImage(im,0,0));expected();draw(f,()=>true);const fx=compare(reference,canvases.actual);
 checks.push({action:f.action,direction:f.direction,index:f.index,base,with_trail:fx,passed:base.changed_pixels===0&&fx.changed_pixels===0});
 sources.forEach(im=>im.src='');master.src='';
}
const report={status:checks.every(c=>c.passed)?'ACTUAL_PRESERVED_ART_COMPOSITOR_PASS_NOT_FULL_CHARACTER_ACCEPTANCE':'FAIL',poses_checked:checks.length,comparisons:checks.length*2,checks,reference_path:'Native master/source images decoded 1:1 to a 768px canvas, followed by the same final resize.',unique_pixel_objects:data.unique_pixel_objects,part_bindings:data.part_bindings,playable_characters_verified:0,semantic_mask_approval:false,runtime_admitted:false};
window.preservedSwordsmanReport=report;document.getElementById('report').textContent=JSON.stringify(report,null,2);
const config=await(await fetch(root+'authoring/characters/factory-v3/configs/layered_action_catalog.json')).json(),timings={};
await Promise.all(Object.entries(config.actions).map(async([name,a])=>timings[name]=(await(await fetch(root+a.directory+'/assembly-audit.json')).json()).durations_ms));
let paused=true,time=0,last=performance.now(),ticket=0;
function current(){return data.frames.find(f=>f.action===document.getElementById('action').value&&f.direction===document.getElementById('direction').value&&f.index===Number(document.getElementById('pose').value))}
function selected(r){return(r!=='HeadHair'||document.getElementById('head').checked)&&(r!=='Weapon'||document.getElementById('weapon').checked)&&(!r.startsWith('WeaponLight')||document.getElementById('fx').checked)}
async function render(){const f=current();if(!f)return;const stamp=++ticket;draw(f,selected);draw(f,selected,canvases.detail);document.getElementById('position').textContent=f.action+' / '+f.direction+' / '+f.index;const im=await load(root+f.master_file);if(stamp!==ticket)return;nctx.clearRect(0,0,768,768);nctx.drawImage(im,0,0);const c=ctx(canvases.source);c.clearRect(0,0,240,240);c.drawImage(native,0,0,240,240)}
window.setPreservedSwordsmanFrame=async(action,direction,index)=>{paused=true;document.getElementById('action').value=action;document.getElementById('direction').value=direction;document.getElementById('pose').value=index;await render()};
for(const id of ['action','direction','head','weapon','fx','pose'])document.getElementById(id).oninput=()=>{paused=true;render()};
document.getElementById('replay').onclick=()=>{time=0;paused=false;last=performance.now()};
function tick(now){if(!paused){const durations=timings[document.getElementById('action').value],total=durations.reduce((a,b)=>a+b,0);time+=(now-last)*Number(document.getElementById('speed').value);if(time>=total){if(document.getElementById('loop').checked)time%=total;else{time=total-1;paused=true}}let i=0,acc=0;while(i<15&&acc+durations[i]<=time)acc+=durations[i++];if(Number(document.getElementById('pose').value)!==i){document.getElementById('pose').value=i;render()}}last=now;requestAnimationFrame(tick)}
await render();requestAnimationFrame(tick);
})().catch(error=>{window.preservedSwordsmanReport={status:'FAIL',error:String(error)};document.getElementById('report').textContent=String(error)});
