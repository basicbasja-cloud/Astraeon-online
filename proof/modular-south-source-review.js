(async function(){
'use strict';
const $=id=>document.getElementById(id),root='authoring/characters/true-modular/swordsman-male-v2/';
const read=async path=>{const r=await fetch(path+'?spriteDev=1');if(!r.ok)throw Error('Cannot read source '+path);return new Uint8Array(await r.arrayBuffer())};
const sha=async bytes=>Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),v=>v.toString(16).padStart(2,'0')).join('');
let draft,images={},sourceHashes={},worldDraws=0,worldSample;
try{
 const [mb,cb]=await Promise.all([read(root+'source-manifest.json'),read(root+'pose-contract.json')]);
 const m=JSON.parse(new TextDecoder().decode(mb)),c=JSON.parse(new TextDecoder().decode(cb));
 if(await sha(cb)!==m.contractSHA256)throw Error('Pose guide identity mismatch');
 const t=JSON.parse(new TextDecoder().decode(await read(c.pose.motionTemplate)));
 draft=AstraeonSourceAuthoring.compileSources(m,c,t,{diagnosticIncomplete:true});
 await Promise.all(Object.values(m.parts).flatMap(p=>Object.values(p.layers)).map(async r=>{
  const [raw,raster,prompt]=await Promise.all([read(r.rawSource),read(r.file),read(r.prompt)]);
  if(await sha(raw)!==r.rawSHA256||await sha(raster)!==r.rasterSHA256||await sha(prompt)!==r.promptSHA256)throw Error('Source digest mismatch '+r.rawSource);
  images[r.file]=await createImageBitmap(new Blob([raster],{type:'image/png'}));
  if(images[r.file].width!==320||images[r.file].height!==320)throw Error('Shared canvas mismatch');
  sourceHashes[r.file]=r.rasterSHA256;
 }));
 for(const layer of m.drawOrder){
  const available=draft.sample().layers.some(l=>l.layer===layer),label=document.createElement('label'),input=document.createElement('input');
  input.type='checkbox';input.checked=available;input.disabled=!available;input.value=layer;input.onchange=render;
  label.append(input,document.createTextNode(' '+layer+(available?'':' · missing')));$('layers').append(label);
 }
 $('scale').onchange=render;$('world').onclick=loadWorld;
 $('status').textContent='Five source/raster/prompt identities verified. Source coverage INCOMPLETE; South VISUAL FAIL. Inspection never grants visual approval.';
 render();
 window.AstraeonModularSourceReview=Object.freeze({draft,images,sourceHashes,
  renderPose:({visibleLayers,appearance={}}={})=>{const s=draft.sample(undefined,{appearance}),canvas=document.createElement('canvas');canvas.width=canvas.height=320;draft.draw(canvas.getContext('2d'),s,images,{x:160,y:264,visibleLayers});return canvas.toDataURL('image/png')},
  snapshot:()=>({sourceHashes,poseId:draft.pose.poseId,visualGate:draft.manifest.gates.south,missing:draft.manifest.missingComponents,sourceCoverageErrors:draft.sourceCoverageErrors,worldDraws,worldSample}),loadWorld});
}catch(e){$('status').textContent=e.message;console.error(e)}
function render(){
 const scale=Number($('scale').value),canvas=$('composite');canvas.width=canvas.height=Math.round(320*scale);
 const ctx=canvas.getContext('2d');ctx.clearRect(0,0,canvas.width,canvas.height);
 const layers=[...$('layers').querySelectorAll('input:checked')].map(i=>i.value);
 draft.draw(ctx,draft.sample(),images,{x:160*scale,y:264*scale,scale,visibleLayers:layers});
}
async function loadWorld(){
 $('worldReview').hidden=false;$('world').disabled=true;
 try{
  let html=new TextDecoder().decode(await read('index.html'));
  const seed={name:'Rejected modular South candidate',race:0,cls:12,zone:0,x:128,y:164,worldLayout:'wayfarer-regional-capital-v75',lv:1,inventory:{},equipment:{},journal:[]};
  const bootstrap='<base href="'+new URL('.',location.href).href+'"><script>const reviewMemory=new Map([["astraeon-iso-v1",'+JSON.stringify(JSON.stringify(seed))+']]);Object.defineProperty(window,"localStorage",{value:{getItem:k=>reviewMemory.get(k)??null,setItem:(k,v)=>reviewMemory.set(k,String(v)),removeItem:k=>reviewMemory.delete(k),clear:()=>reviewMemory.clear(),key:i=>[...reviewMemory.keys()][i]??null,get length(){return reviewMemory.size}}});window.AstraeonVisualReviewMemoryOnly=true;<\/script>';
  html=html.replace('<head>','<head>'+bootstrap);$('game').srcdoc=html;
  const started=performance.now(),install=setInterval(()=>{
   const w=$('game').contentWindow;
   if(performance.now()-started>240000){clearInterval(install);$('worldStatus').textContent='World review did not become ready; standalone source evidence remains available.';return}
   if(!w?.AstraeonAnimation?.player)return;
   clearInterval(install);
   w.AstraeonAnimation.player=function(ctx,cls,anim,t,iso){
    const s=draft.sample(),v=w.AstraeonView,p=t.position,foot=iso(p.x,p.y,((p.z||0)+(t.flight||0))*35);
    const scale=70*((v.scale.humanoid||103)/76)/s.registration.referenceHeight*(v.zoom||1);
    const spriteSockets=draft.draw(ctx,s,images,{x:foot.x,y:foot.y,scale});
    if(w.AstraeonSpatialView?.assemblingActor)w.AstraeonSpatialView.sampledPose={clip:'modular-source-diagnostic/'+s.motionTemplateId,row:0,column:0,bounds:[0,0,320,320]};
    worldDraws++;worldSample={poseId:s.frame.id,scale,sourceCoverageComplete:false,visualGate:'VISUAL_FAIL',memoryOnly:w.AstraeonVisualReviewMemoryOnly===true,gameplayClass:12,presentationOnly:true};
    const f=t.facingDirection;
    return {RightHand:[p.x+f.y*.22,p.y-f.x*.22,p.z+1.2],LeftHand:[p.x-f.y*.22,p.y+f.x*.22,p.z+1.2],Back:[p.x-f.x*.2,p.y-f.y*.2,p.z+1.2],Hip:[p.x,p.y,p.z+.8],spriteSockets};
   };
   $('worldStatus').textContent='Failed South art, static pose only. Existing Mage mechanics and actual world are unchanged; this save stays in memory.';
  },100);
 }catch(e){$('worldStatus').textContent=e.message;console.error(e)}
}
})();
