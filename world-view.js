/* Shared world projection, responsive framing and human-relative scale. */
(() => {
'use strict';
const scale=Object.freeze({humanoid:76,npc:.94,boss:176,monster:[66,83,52,77,58,84,95,71]});
// Ground axes match the painted front and side foundation planes.
const legacyBasis=Object.freeze({xx:48,xy:14,yx:-32,yy:22});
// Controlled long-lens study: local ground/height ratios correspond to
// approximately 55/60/65 degrees of downward pitch at similar actor height.
const townCameras=Object.freeze({
 baseline:{basis:{xx:46,xy:0,yx:0,yy:24},depth:{x:0,y:-.012,z:-.007}},
 tilt55:{basis:{xx:61,xy:0,yx:0,yy:50},depth:{x:0,y:-.0096,z:-.0136}},
 tilt60:{basis:{xx:70,xy:0,yx:0,yy:61},depth:{x:0,y:-.0094,z:-.0163}},
 tilt65:{basis:{xx:83,xy:0,yx:0,yy:75},depth:{x:0,y:-.0094,z:-.0201}}
});
const cameraChoice=new URLSearchParams(location.search).get('camera');
const cameraProfile=cameraChoice==='legacy'?null:townCameras[cameraChoice]||townCameras.tilt55;
const currentBasis=()=>cameraProfile&&window.AstraeonView?.zone===0?cameraProfile.basis:legacyBasis;
const project=(x,y)=>{const b=currentBasis();return{x:x*b.xx+y*b.yx,y:x*b.xy+y*b.yy}};
const inverse=(x,y)=>{const b=currentBasis(),det=b.xx*b.yy-b.yx*b.xy;return{x:(b.yy*x-b.yx*y)/det,y:(b.xx*y-b.xy*x)/det}};
const materialTransform=(unit,origin,zoom=1)=>{const b=currentBasis();return[b.xx*unit*zoom,b.xy*unit*zoom,b.yx*unit*zoom,b.yy*unit*zoom,origin.x,origin.y]};
const framing=(width,height)=>window.AstraeonView?.zone===0?({zoom:width/height<.8?.98:width>1000?.82:.9,anchorY:width/height<.8?.62:.72}):({zoom:width/height<.8?1:width>1000?.92:.96,anchorY:width/height<.8?.56:.55});
const limits=zone=>zone===0?{w:window.AstraeonContent?.nativeWorld?.spatial?.bounds?.maxX??44,h:window.AstraeonContent?.nativeWorld?.spatial?.bounds?.maxY??40}:{w:30,h:27};
function screen(x,y,z,camera,width,height){const spatial=window.AstraeonSpatialView;if(cameraProfile&&window.AstraeonView?.zone===0&&spatial?.projectionReady)return spatial.worldToScreen(x,y,z/35);const p=project(x,y),v=framing(width,height);return{x:width/2+(p.x-camera.x)*v.zoom,y:height*v.anchorY+(p.y-camera.y-z)*v.zoom}}
function world(x,y,camera,width,height){const v=framing(width,height);return inverse((x-width/2)/v.zoom+camera.x,(y-height*v.anchorY)/v.zoom+camera.y)}
function drawCache(ctx,cache,origin,offsetX,offsetY){const zoom=window.AstraeonView.zoom,left=origin.x-offsetX*zoom,top=origin.y-offsetY*zoom,sx=Math.max(0,-left/zoom),sy=Math.max(0,-top/zoom),ex=Math.min(cache.width,(ctx.canvas.clientWidth-left)/zoom),ey=Math.min(cache.height,(ctx.canvas.clientHeight-top)/zoom);if(ex>sx&&ey>sy)ctx.drawImage(cache,sx,sy,ex-sx,ey-sy,left+sx*zoom,top+sy*zoom,(ex-sx)*zoom,(ey-sy)*zoom)}
window.AstraeonView={scale,get basis(){return currentBasis()},cameraProfile,project,inverse,materialTransform,framing,limits,screen,world,drawCache,zoom:1};
})();
