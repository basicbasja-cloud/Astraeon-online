(async function(){
'use strict';
const M=window.AstraeonMotionTemplate,A=window.AstraeonCharacterAssembly,$=id=>document.getElementById(id);
const ui={pack:$('pack'),action:$('action'),direction:$('direction'),frame:$('frame'),speed:$('speed'),anchors:$('anchors'),status:$('status')};
let loaded,elapsedMs=0,cosmeticTimeMs=100,forcedFrame=0,last=performance.now(),packRevision=0;
const hidden=new Set(),layerControls=new Map();
function current(){return loaded.sample(ui.action.value,ui.direction.value,elapsedMs,{frameIndex:forcedFrame,cosmeticTimeMs})}
function frameStart(index){return loaded.compiled.motion.template.actions[ui.action.value].directions[ui.direction.value].frames.slice(0,index).reduce((n,f)=>n+f.durationMs,0)}
function paint(canvas,sampled,scale,overlay,visibleLayers){
 const ctx=canvas.getContext('2d');ctx.clearRect(0,0,canvas.width,canvas.height);
 const root=sampled.registration.root,anchors=A.drawAssembly(ctx,sampled,loaded.images,{x:root.x*scale,y:root.y*scale,scale,visibleLayers});
 if(overlay){
  ctx.save();ctx.font='10px monospace';
  for(const [name,a] of Object.entries(anchors)){
   ctx.strokeStyle=name==='root'?'#ff7697':'#eafff6';ctx.beginPath();ctx.moveTo(a.x-3,a.y);ctx.lineTo(a.x+3,a.y);ctx.moveTo(a.x,a.y-3);ctx.lineTo(a.x,a.y+3);ctx.stroke();
   if(scale>=4){ctx.fillStyle='#fff';ctx.fillText(name,a.x+5,a.y-3)}
  }
  ctx.restore();
 }
}
function makeLayerControls(sample){
 for(const layer of sample.drawOrder){
  if(layerControls.has(layer))continue;
  const label=document.createElement('label'),row=document.createElement('span'),check=document.createElement('input'),canvas=document.createElement('canvas');
  row.className='layer-header';check.type='checkbox';check.checked=true;check.dataset.layer=layer;canvas.width=canvas.height=128;
  row.append(check,document.createTextNode(layer));label.append(row,canvas);$('layers').append(label);layerControls.set(layer,{canvas,check});
  check.addEventListener('change',()=>{if(check.checked)hidden.delete(layer);else hidden.add(layer);render()});
 }
}
function render(){
 if(!loaded)return;
 const s=current();makeLayerControls(s);
 const visible=s.drawOrder.filter(l=>!hidden.has(l));
 for(const [id,scale] of [['gameplay',1],['review',2],['diagnostic',4]])paint($(id),s,scale,ui.anchors.value==='1',visible);
 for(const [layer,{canvas}] of layerControls)paint(canvas,s,1,false,[layer]);
 ui.frame.max=loaded.compiled.motion.template.actions[s.action].directions[s.direction].frames.length-1;ui.frame.value=s.frameIndex;$('frame-label').textContent=s.frameIndex;
 ui.status.textContent=`${loaded.compiled.pack.packId} / ${s.action} / ${s.direction} / frame ${s.frameIndex} / ${s.frame.role} / ENGINE FIXTURE`;
 $('metadata').textContent=JSON.stringify({motionTemplateId:s.motionTemplateId,provenance:loaded.compiled.motion.template.provenance,action:s.action,direction:s.direction,frame:s.frameIndex,elapsedMs,cosmeticTimeMs,durationMs:s.frame.durationMs,totalDurationMs:s.totalDurationMs,role:s.frame.role,referencePhase:s.frame.referencePhase,between:s.frame.between,root:s.frame.root,anchors:s.frame.anchors,drawOrder:s.layers.map(l=>l.layer),sampling:s.layers.map(l=>({layer:l.layer,part:l.partId,mode:l.mode,sample:l.sampleIndex})),events:s.frame.events},null,2);
}
function failure(error){ui.status.textContent=error.message;ui.status.className='error';console.error(error)}
async function choosePack(){
 const request=++packRevision;
 const next=await A.loadAssembly({motionUrl:'authoring/characters/motion-templates/assembly-debug/motion-template.json',appearanceUrl:`authoring/characters/appearance/${ui.pack.value}/appearance-pack.json`,allowDev:true});
 if(request!==packRevision)return;
 loaded=next;
 for(const [id,slot] of [['hair','Hair'],['weapon','MainHand'],['offhand','OffHand'],['headgear','Headgear'],['garment','Garment']])$(id).value=loaded.appearance[slot]||'';
 // Replacing a compatible pack also preserves the current presentation clock.
 render();
}
for(const [id,slot] of [['hair','Hair'],['weapon','MainHand'],['offhand','OffHand'],['headgear','Headgear'],['garment','Garment']]){
 $(id).addEventListener('change',async()=>{try{await loaded.setAppearance({[slot]:$(id).value||null});render()}catch(e){failure(e)}});
}
ui.pack.addEventListener('change',()=>choosePack().catch(failure));
ui.action.addEventListener('change',()=>{elapsedMs=0;forcedFrame=0;render()});
ui.direction.addEventListener('change',render);
$('rotate').addEventListener('click',()=>{ui.direction.value=M.DIRECTIONS[(M.DIRECTIONS.indexOf(ui.direction.value)+1)%8];render()});
ui.frame.addEventListener('input',()=>{forcedFrame=Number(ui.frame.value);elapsedMs=frameStart(forcedFrame);ui.speed.value='0';render()});
ui.speed.addEventListener('change',()=>{forcedFrame=undefined;render()});
ui.anchors.addEventListener('change',render);
function tick(now){
 const delta=Math.min(now-last,100);last=now;
 if(loaded&&Number(ui.speed.value)>0){elapsedMs+=delta*Number(ui.speed.value);cosmeticTimeMs+=delta*Number(ui.speed.value);forcedFrame=undefined;render()}
 requestAnimationFrame(tick);
}
try{
 await choosePack();
 window.AstraeonCharacterReview=Object.freeze({
  snapshot:()=>{const s=current();return {...s,root:s.frame.root,anchors:s.frame.anchors,role:s.frame.role}},
  renderPose:({action=ui.action.value,direction=ui.direction.value,frameIndex=0,appearance=loaded.appearance,cosmeticTimeMs:cosmetic=100,visibleLayers,scale=1}={})=>{
   const s=loaded.compiled.sample(action,direction,0,{frameIndex,appearance,cosmeticTimeMs:cosmetic}),canvas=document.createElement('canvas');canvas.width=canvas.height=128*scale;paint(canvas,s,scale,false,visibleLayers);return canvas.toDataURL('image/png');
  },
  async prepareVariants(){const previous=loaded.appearance;await loaded.setAppearance({Hair:'hair-b',MainHand:'weapon-b',Headgear:'headgear-b'});await loaded.setAppearance(previous);render()},
  get loaded(){return loaded}
 });
 requestAnimationFrame(tick);
}catch(error){failure(error)}
})();
