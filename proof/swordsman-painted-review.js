(async function(){
'use strict';
const M=window.AstraeonMotionTemplate,A=window.AstraeonCharacterAssembly,$=id=>document.getElementById(id);
const params=new URLSearchParams(location.search),legacy=params.has('legacy'),registration=params.has('registration');
let anatomy; const visibility=new Map();
let loaded,time=0,cosmetic=0,playing=true,forcedFrame,last=performance.now();
const layers=new Map(),debug=new Map();
const groups={BodyWithOutfit:['Body'],Head:['HeadBase'],Hair:['HairBack','HairFront'],MainHand:['MainHand'],OffHand:['OffHand'],Headgear:['HeadgearLower','HeadgearMiddle','HeadgearTop'],Garment:['GarmentBack','GarmentFront']};
for(const [name,layers]of [['BodyWithOutfit',['Body']],['Head',['HeadBase']],['Hair',['HairBack','HairFront']],['MainHand',['MainHand']],['Cape',['GarmentBack','GarmentFront']]]){
 const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.checked=true;input.dataset.visible=name;label.append(input,name);$('visibility').append(label);visibility.set(name,{input,layers});input.onchange=render;
}
for(const name of ['arm joints','root','body anchors','head pivot','hair pivot','mainHand anchor','weapon grip pivot','back anchor','cape pivot','bounding boxes','action phase','sampling mode','draw order']){
 const label=document.createElement('label'),input=document.createElement('input');input.type='checkbox';input.checked=false;input.dataset.debug=name;label.append(input,name);$('debug-toggles').append(label);debug.set(name,input);input.onchange=render;
}
function current(){const seq=loaded.compiled.motion.template.actions[$('action').value].directions[$('direction').value];return loaded.sample($('action').value,$('direction').value,time%seq.totalDurationMs,{frameIndex:forcedFrame,cosmeticTimeMs:cosmetic})}
function diagnostics(ctx,s,{x,y,scale},options){
 const root=s.registration.root,point=p=>({x:x+(p.x-root.x)*scale,y:y+(p.y-root.y)*scale});
 function mark(p,label,col){const q=point(p);ctx.strokeStyle=col;ctx.fillStyle=col;ctx.beginPath();ctx.arc(q.x,q.y,4,0,Math.PI*2);ctx.stroke();ctx.fillText(label,q.x+6,q.y-5)}
 ctx.save();ctx.font='12px monospace';ctx.lineWidth=1.5;
 const enabled=n=>options===true||options?.includes(n);
 for(const [n,p]of Object.entries(s.registeredAnchors||s.frame.anchors))if(enabled('body anchors')||n==='root'&&enabled('root')||n==='mainHand'&&enabled('mainHand anchor')||n==='back'&&enabled('back anchor'))mark(p,n,'#ffc56e');
 const names={HeadBase:['head pivot','#9fffea'],HairFront:['hair pivot','#ef9dff'],MainHand:['weapon grip pivot','#ff7e9d'],GarmentBack:['cape pivot','#95caff']};
 for(const ref of s.layers){
  if(names[ref.layer]&&enabled(names[ref.layer][0])){mark(ref.transform,names[ref.layer][0],names[ref.layer][1]);if(ref.anchorTransform){const p=point(ref.anchorTransform),q=point(ref.transform);ctx.strokeStyle=names[ref.layer][1];ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke()}}
  if(ref.layer==='MainHand'&&ref.bladeTip&&ref.guardCentre&&enabled('weapon grip pivot')){
   const local=p=>A.composeTransform(ref.transform,{x:p[0]-ref.pivot[0],y:p[1]-ref.pivot[1],rotation:0,scale:1});
   const grip=point(ref.transform),tip=point(local(ref.bladeTip));ctx.strokeStyle='#ff7e9d';ctx.beginPath();ctx.moveTo(grip.x,grip.y);ctx.lineTo(tip.x,tip.y);ctx.stroke();mark(local(ref.guardCentre),'guard','#95caff');
  }
  if(enabled('bounding boxes')){
   let corners;
   if(ref.space==='canvas')corners=[[0,0],[320,0],[320,320],[0,320]].map(([x,y])=>point({x,y}));
   else corners=[[0,0],[ref.rect[2],0],[ref.rect[2],ref.rect[3]],[0,ref.rect[3]]].map(([x,y])=>point(A.composeTransform(ref.transform,{x:x-ref.pivot[0],y:y-ref.pivot[1],rotation:0,scale:1})));
   ctx.strokeStyle=names[ref.layer]?.[1]||'#839daa';ctx.beginPath();corners.forEach((p,i)=>i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y));ctx.closePath();ctx.stroke();
  }
 }
 if(enabled('arm joints')&&s.action==='BasicAttack'&&anatomy){
  const entry=anatomy.frames[s.direction]?.[s.frameIndex],joints=entry?.joints;
  if(joints){const colors=['#ffca70','#86e8e2','#83bcff','#ff8da1'];ctx.lineWidth=2;ctx.strokeStyle='#eef5fa';ctx.beginPath();joints.forEach((p,i)=>{const q=point({x:p[0],y:p[1]});i?ctx.lineTo(q.x,q.y):ctx.moveTo(q.x,q.y)});ctx.stroke();joints.forEach((p,i)=>mark({x:p[0],y:p[1]},['shoulder','elbow','wrist','grip'][i],colors[i]));}
 }
 let line=16;function text(s){ctx.fillStyle='#10202bdd';ctx.fillRect(3,line-12,ctx.measureText(s).width+8,16);ctx.fillStyle='#eef5fa';ctx.fillText(s,7,line);line+=18}
 if(enabled('action phase'))text(`${s.action}/${s.direction} frame ${s.frameIndex} phase ${s.phase.toFixed(3)} ${s.frame.referencePhase||s.frame.role}`);
 if(enabled('sampling mode'))for(const l of s.layers)text(`${l.slot}: ${l.mode} sample ${l.sampleIndex}`);
 if(enabled('draw order'))text(s.layers.map(l=>l.slot).join(' > ')+ (s.layers.some(l=>l.foregroundPasses?.length)?' / body fingers cover held grip':''));
 ctx.restore();
}
function paint(canvas,sample,zoom,visibleLayers,overlay=false,canonical=false){
 const ctx=canvas.getContext('2d');ctx.clearRect(0,0,canvas.width,canvas.height);
 const scale=canonical?zoom:70/sample.registration.referenceHeight*zoom;
 const transform=canonical?{x:sample.registration.root.x*scale,y:sample.registration.root.y*scale,scale}:{x:canvas.width/2,y:canvas.height*.825,scale};
 A.drawAssembly(ctx,sample,loaded.images,{...transform,visibleLayers});if(overlay)diagnostics(ctx,sample,transform,overlay);
}
function render(){
 if(!loaded)return;const s=current(),zoom=Number($('scale').value),solo=groups[$('solo').value],hidden=[...visibility.values()].flatMap(v=>v.input.checked?[]:v.layers),visible=solo?solo.filter(l=>!hidden.includes(l)):s.drawOrder.filter(l=>!hidden.includes(l)),overlays=$('anchors').value==='1'?true:[...debug].filter(([n,c])=>c.checked).map(([n])=>n);
 $('hero').width=$('hero').height=128*zoom;
 for(const [id,z]of [['hero',zoom],['gameplay',1],['review',2]])paint($(id),s,z,visible,overlays.length||overlays===true?overlays:false);
 $('status').textContent=`${s.action==='BasicAttack'?'Basic Attack':s.action} · ${s.direction} · ${playing?'Playing':'Paused'} · frame ${s.frameIndex}/${loaded.compiled.motion.template.actions[s.action].directions[s.direction].frames.length-1} · Owner approval pending`;
 $('frame').max=loaded.compiled.motion.template.actions[s.action].directions[s.direction].frames.length-1;$('frame').value=s.frameIndex;$('frame-label').textContent=s.frameIndex;
 for(const b of $('directions').children)b.setAttribute('aria-pressed',b.textContent===s.direction);
 if(document.querySelector('details').open){
  for(const layer of s.layers)if(!layers.has(layer.layer)){const label=document.createElement('label'),canvas=document.createElement('canvas');label.append(layer.slot,canvas);canvas.width=canvas.height=128;$('layers').append(label);layers.set(layer.layer,canvas)}
  for(const [layer,canvas]of layers)paint(canvas,s,1,[layer]);
  $('metadata').textContent=JSON.stringify({role:s.frame.role,evidenceClass:s.frame.evidenceClass,referencePhase:s.frame.referencePhase,durationMs:s.frame.durationMs,totalDurationMs:s.totalDurationMs,root:s.frame.root,anchors:s.frame.anchors,events:s.frame.events,appearance:s.appearance,drawOrder:s.layers.map(l=>l.layer),foregroundPasses:s.layers.flatMap(l=>(l.foregroundPasses||[]).map(p=>({source:l.layer,...p}))),sampling:s.layers.map(l=>({part:l.partId,mode:l.mode,sample:l.sampleIndex,pivot:l.pivot,transform:l.transform,parent:l.parentLayer}))},null,2);
 }
}
function fail(e){$('status').className='error';$('status').textContent=e.message;console.error(e)}
try{
 loaded=await A.loadAssembly({motionUrl:'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json',appearanceUrl:`authoring/characters/appearance/${legacy?'swordsman-male-painted':registration?'swordsman-bodywithoutfit':'swordsman-basicattack-anatomy'}/appearance-pack.json`,allowDev:true});
 if(!legacy&&!registration)anatomy=await (await fetch('authoring/characters/builds/swordsman-basicattack-anatomy-v1/joint-review.json')).json();
 for(const d of M.DIRECTIONS){const b=document.createElement('button');b.textContent=d;b.onclick=()=>{$('direction').value=d;render()};$('directions').append(b)}
 for(const [id,slot]of [['costume','BodyWithOutfit'],['hair','Hair'],['weapon','MainHand'],['offhand','OffHand'],['headgear','Headgear'],['garment','Garment']]){
  if(legacy&&id==='costume'){$(id).disabled=true;continue}
  $(id).onchange=async()=>{try{await loaded.setAppearance({[slot]:$(id).value||null});render()}catch(e){fail(e)}};
 }
 $('action').onchange=()=>{time=0;forcedFrame=undefined;render()};$('direction').onchange=render;$('scale').onchange=render;$('anchors').onchange=render;$('solo').onchange=render;
 $('play').onclick=()=>{playing=!playing;forcedFrame=undefined;$('play').textContent=playing?'Pause':'Play';render()};
 function inspectFrame(index){forcedFrame=index;playing=false;$('play').textContent='Play';time=loaded.compiled.motion.template.actions[$('action').value].directions[$('direction').value].frames.slice(0,index).reduce((n,f)=>n+f.durationMs,0);render()}
 for(const [id,delta]of [['previous',-1],['next',1]])$(id).onclick=()=>{const s=current(),count=loaded.compiled.motion.template.actions[s.action].directions[s.direction].frames.length;inspectFrame((s.frameIndex+delta+count)%count)};
 $('frame').oninput=()=>{forcedFrame=Number($('frame').value);playing=false;$('play').textContent='Play';time=loaded.compiled.motion.template.actions[$('action').value].directions[$('direction').value].frames.slice(0,forcedFrame).reduce((n,f)=>n+f.durationMs,0);render()};
 const api={snapshot:()=>({...current(),playing,time,cosmetic}),get loaded(){return loaded},
  async prepareVariants(){const previous=loaded.appearance;await loaded.setAppearance({...(legacy?{}:{BodyWithOutfit:'swordsman-body-royal-proof'}),Hair:'hair-b',MainHand:'weapon-b',OffHand:'offhand',Headgear:'headgear'});await loaded.setAppearance(previous)},
  async setAppearance(patch){await loaded.setAppearance(patch);render()},
  renderPose:({action='Walk',direction='S',frameIndex=0,appearance=loaded.appearance,visibleLayers,scale=1,overlay=false,canonical=false,timeMs}={})=>{
   const seq=loaded.compiled.motion.template.actions[action].directions[direction];const t=timeMs??seq.frames.slice(0,frameIndex).reduce((n,f)=>n+f.durationMs,0);const s=loaded.compiled.sample(action,direction,t,{frameIndex:timeMs===undefined?frameIndex:undefined,appearance,cosmeticTimeMs:t});const c=document.createElement('canvas');c.width=c.height=(canonical?320:128)*scale;paint(c,s,scale,visibleLayers,overlay,canonical);return c.toDataURL('image/png')},
  setReviewPose:({action='Walk',direction='S',frameIndex,play=true,timeMs=0}={})=>{$('action').value=action;$('direction').value=direction;time=timeMs;forcedFrame=frameIndex;playing=play;$('play').textContent=play?'Pause':'Play';render()},render};
 window.AstraeonCharacterReview=Object.freeze(api);
 function tick(now){const dt=Math.min(now-last,100);last=now;if(playing){time+=dt*Number($('speed').value);cosmetic+=dt*Number($('speed').value);forcedFrame=undefined;render()}requestAnimationFrame(tick)}
 render();requestAnimationFrame(tick);
}catch(e){fail(e)}
})();
