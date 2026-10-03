/* Shared world projection, responsive framing and human-relative scale. */
(() => {
'use strict';
const scale=Object.freeze({humanoid:92,npc:.94,boss:176,monster:[66,83,52,77,58,84,95,71]});
// Ground axes match the painted front and side foundation planes.
const legacyBasis=Object.freeze({xx:48,xy:14,yx:-32,yy:22});
// Controlled long-lens study: local ground/height ratios correspond to
// approximately 55/60/65 degrees of downward pitch at similar actor height.
const townCameras=Object.freeze({
 ragnarok:{kind:'ragnarok',fov:15,pitch:46,yaw:0,zoom:125,basis:{xx:35/Math.cos(46*Math.PI/180),xy:0,yx:0,yy:35*Math.tan(46*Math.PI/180)},depth:{x:0,y:-Math.cos(46*Math.PI/180)/62.5,z:-Math.sin(46*Math.PI/180)/62.5}},
 concept38:{basis:{xx:47,xy:12,yx:-25,yy:25},depth:{x:-.002,y:-.008,z:-.007}},
 concept45:{basis:{xx:49,xy:13,yx:-26,yy:33},depth:{x:-.002,y:-.008,z:-.009}},
 civic:{basis:{xx:49,xy:0,yx:0,yy:31},depth:{x:0,y:-.009,z:-.008}},
 baseline:{basis:{xx:46,xy:0,yx:0,yy:24},depth:{x:0,y:-.012,z:-.007}},
 tilt55:{basis:{xx:61,xy:0,yx:0,yy:50},depth:{x:0,y:-.0096,z:-.0136}},
 tilt60:{basis:{xx:70,xy:0,yx:0,yy:61},depth:{x:0,y:-.0094,z:-.0163}},
 tilt65:{basis:{xx:83,xy:0,yx:0,yy:75},depth:{x:0,y:-.0094,z:-.0201}}
});
const cameraChoice=new URLSearchParams(globalThis.location?.search||'').get('camera');
const cameraProfile=cameraChoice==='legacy'?null:structuredClone(townCameras[cameraChoice]||townCameras.ragnarok);
const cameraTarget={pitch:46,yaw:0,zoom:125};
const currentBasis=()=>cameraProfile&&window.AstraeonView?.zone===0?cameraProfile.basis:legacyBasis;
const project=(x,y)=>{const b=currentBasis();return{x:x*b.xx+y*b.yx,y:x*b.xy+y*b.yy}};
const inverse=(x,y)=>{const b=currentBasis(),det=b.xx*b.yy-b.yx*b.xy;return{x:(b.yy*x-b.yx*y)/det,y:(b.xx*y-b.xy*x)/det}};
const materialTransform=(unit,origin,zoom=1)=>{const b=currentBasis();return[b.xx*unit*zoom,b.xy*unit*zoom,b.yx*unit*zoom,b.yy*unit*zoom,origin.x,origin.y]};
const framing=(width,height)=>window.AstraeonView?.zone===0?(cameraProfile?.kind==='ragnarok'?{zoom:height/(2*Math.tan(cameraProfile.fov*Math.PI/360))*Math.cos(cameraProfile.pitch*Math.PI/180)/(cameraProfile.zoom/2*35),anchorY:.5}:({zoom:width/height<.8?.65:width>1000?.56:.63,anchorY:width/height<.8?.68:.77})):({zoom:width/height<.8?1:width>1000?.92:.96,anchorY:width/height<.8?.56:.55});
function advanceCamera(dt,camera){
 if(cameraProfile?.kind!=='ragnarok'||window.AstraeonView?.zone!==0)return;
 const focus=inverse(camera.x,camera.y),rate=1-Math.exp(-12*dt);
 for(const k of ['pitch','yaw','zoom'])cameraProfile[k]+=(cameraTarget[k]-cameraProfile[k])*rate;
 const p=cameraProfile.pitch*Math.PI/180,a=cameraProfile.yaw*Math.PI/180,c=Math.cos(p),s=Math.sin(p),ca=Math.cos(a),sa=Math.sin(a),distance=cameraProfile.zoom/2;
 cameraProfile.basis={xx:35*ca/c,xy:35*Math.tan(p)*sa,yx:-35*sa/c,yy:35*Math.tan(p)*ca};
 cameraProfile.depth={x:-c*sa/distance,y:-c*ca/distance,z:-s/distance};
 Object.assign(camera,project(focus.x,focus.y));
}
function mountCameraControls(canvas){
 if(cameraProfile?.kind!=='ragnarok')return;
 let drag=null,lastDown=-Infinity;
 const active=()=>window.AstraeonView?.zone===0&&window.AstraeonSpatialView?.active;
 canvas.addEventListener('contextmenu',e=>{if(active())e.preventDefault()});
 canvas.addEventListener('wheel',e=>{if(!active())return;e.preventDefault();cameraTarget.zoom=Math.max(65,Math.min(325,cameraTarget.zoom+Math.sign(e.deltaY)*15))},{passive:false});
 canvas.addEventListener('pointerdown',e=>{if(e.button!==2||!active())return;e.preventDefault();
  const now=performance.now();if(now-lastDown<350){if(e.shiftKey)cameraTarget.pitch=46;else if(e.ctrlKey)cameraTarget.zoom=125;else cameraTarget.yaw=0}lastDown=now;
  drag={id:e.pointerId,x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);
 });
 canvas.addEventListener('pointermove',e=>{if(!drag||e.pointerId!==drag.id)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;drag.x=e.clientX;drag.y=e.clientY;
  if(e.shiftKey)cameraTarget.pitch=Math.max(10,Math.min(89,cameraTarget.pitch+dy/canvas.clientHeight*300));
  else if(e.ctrlKey)cameraTarget.zoom=Math.max(65,Math.min(325,cameraTarget.zoom-dy*1.5));
  else cameraTarget.yaw-=dx/canvas.clientWidth*720;
 });
 const release=e=>{if(drag?.id===e.pointerId)drag=null};for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,release);
}
const limits=zone=>zone===0?{w:window.AstraeonContent?.nativeWorld?.spatial?.bounds?.maxX??44,h:window.AstraeonContent?.nativeWorld?.spatial?.bounds?.maxY??40}:{w:30,h:27};
function screen(x,y,z,camera,width,height){const spatial=window.AstraeonSpatialView;if(cameraProfile&&window.AstraeonView?.zone===0&&spatial?.projectionReady)return spatial.worldToScreen(x,y,z/35);const p=project(x,y),v=framing(width,height);return{x:width/2+(p.x-camera.x)*v.zoom,y:height*v.anchorY+(p.y-camera.y-z)*v.zoom}}
function world(x,y,camera,width,height){const v=framing(width,height);return inverse((x-width/2)/v.zoom+camera.x,(y-height*v.anchorY)/v.zoom+camera.y)}
function drawCache(ctx,cache,origin,offsetX,offsetY){const zoom=window.AstraeonView.zoom,left=origin.x-offsetX*zoom,top=origin.y-offsetY*zoom,sx=Math.max(0,-left/zoom),sy=Math.max(0,-top/zoom),ex=Math.min(cache.width,(ctx.canvas.clientWidth-left)/zoom),ey=Math.min(cache.height,(ctx.canvas.clientHeight-top)/zoom);if(ex>sx&&ey>sy)ctx.drawImage(cache,sx,sy,ex-sx,ey-sy,left+sx*zoom,top+sy*zoom,(ex-sx)*zoom,(ey-sy)*zoom)}
window.AstraeonView={scale,get basis(){return currentBasis()},cameraProfile,project,inverse,materialTransform,framing,limits,screen,world,drawCache,advanceCamera,mountCameraControls,zoom:1};
})();
