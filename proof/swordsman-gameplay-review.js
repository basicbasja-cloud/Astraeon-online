(async function(){
'use strict';
const A=window.AstraeonCharacterAssembly,$=id=>document.getElementById(id);
let loaded,lastTransform,lastSample,drawCount=0,started=performance.now();
try{
 loaded=await A.loadAssembly({motionUrl:'authoring/characters/motion-templates/ro1-swordsman-male/motion-template.json',appearanceUrl:'authoring/characters/appearance/swordsman-male-painted/appearance-pack.json',allowDev:true});
 // The game entry and gameplay files are loaded unchanged. The sandbox's
 // Storage object is private memory, so review never edits the owner's save.
 const response=await fetch('index.html?spriteDev=1');if(!response.ok)throw Error('Cannot load game entry');let html=await response.text();
 const seed={name:'Swordsman visual proof',race:0,cls:12,zone:0,x:128,y:164,worldLayout:'wayfarer-regional-capital-v75',lv:1,inventory:{},equipment:{},journal:[]};
 const bootstrap='<base href="'+new URL('.',location.href).href+'"><script>const reviewMemory=new Map([["astraeon-iso-v1",'+JSON.stringify(JSON.stringify(seed))+']]);Object.defineProperty(window,"localStorage",{value:{getItem:k=>reviewMemory.get(k)??null,setItem:(k,v)=>reviewMemory.set(k,String(v)),removeItem:k=>reviewMemory.delete(k),clear:()=>reviewMemory.clear(),key:i=>[...reviewMemory.keys()][i]??null,get length(){return reviewMemory.size}}});window.AstraeonVisualReviewMemoryOnly=true;<\/script>';
 html=html.replace('<head>','<head>'+bootstrap);$('game').srcdoc=html;
 for(const [id,slot] of [['hair','Hair'],['weapon','MainHand'],['offhand','OffHand'],['headgear','Headgear'],['garment','Garment']])$(id).onchange=()=>loaded.setAppearance({[slot]:$(id).value||null}).catch(fail);
 $('action').onchange=()=>{started=performance.now()};
 const install=setInterval(()=>{
  const w=$('game').contentWindow;if(!w?.AstraeonAnimation?.player)return;
  clearInterval(install);const prior=w.AstraeonAnimation.player;
  w.AstraeonAnimation.player=function(ctx,cls,anim,t,iso,gameTime,equipment,modular){
   const action=$('action').value,direction=$('direction').value;
   const duration=loaded.compiled.motion.duration(action,direction);
   const time=(performance.now()-started)%duration,s=loaded.sample(action,direction,time,{cosmeticTimeMs:performance.now()-started});
   const view=w.AstraeonView,p=t.position,foot=iso(p.x,p.y,((p.z||0)+(t.flight||0))*35);
   const unit=70*((view.scale.humanoid||103)/76)/s.registration.referenceHeight*(view.zoom||1);
   const spriteSockets=A.drawAssembly(ctx,s,loaded.images,{x:foot.x,y:foot.y,scale:unit,visibleLayers:s.drawOrder.filter(l=>l!=='Shadow')});
   if(w.AstraeonSpatialView?.assemblingActor)w.AstraeonSpatialView.sampledPose={clip:'assembly/'+s.motionTemplateId,row:AstraeonMotionTemplate.DIRECTIONS.indexOf(direction),column:s.frameIndex,bounds:[0,0,320,320]};
   lastTransform=t.snapshot();lastSample={action,direction,frameIndex:s.frameIndex,role:s.frame.role,drawOrder:s.layers.map(l=>l.layer),unit,rasterFoot:{x:foot.x,y:foot.y},worldFoot:w.AstraeonSpatialView?.worldToScreen(p.x,p.y,p.z||0)||foot,worldTime:gameTime};drawCount++;
   const f=t.facingDirection;
   // Legacy world-space aliases stay presentation-only, matching old adapter.
   return {RightHand:[p.x+f.y*.22,p.y-f.x*.22,p.z+1.2],LeftHand:[p.x-f.y*.22,p.y+f.x*.22,p.z+1.2],Back:[p.x-f.x*.2,p.y-f.y*.2,p.z+1.2],Hip:[p.x,p.y,p.z+.8],spriteSockets};
  };
  window.AstraeonGameplayReview=Object.freeze({get loaded(){return loaded},snapshot:()=>({drawCount,lastTransform,lastSample,memoryOnly:w.AstraeonVisualReviewMemoryOnly===true,gameplayClass:12,presentationClass:'Swordsman',combatAuthority:'existing game; visual markers never executed'}),setPose:(action,direction)=>{$('action').value=action;$('direction').value=direction;started=performance.now()},restore:()=>{w.AstraeonAnimation.player=prior}});
  $('status').textContent='Painted Swordsman animating in the actual world. WASD still uses existing movement. This isolated Mage mechanics fixture changes presentation only; all saves stay in memory.';
 },50);
}catch(e){fail(e)}
function fail(e){$('status').textContent=e.message;console.error(e)}
})();
