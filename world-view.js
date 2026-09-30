/* Shared world projection, responsive framing and human-relative scale. */
(() => {
'use strict';
const scale=Object.freeze({humanoid:76,npc:.94,boss:176,monster:[66,83,52,77,58,84,95,71]});
const project=(x,y)=>({x:x*48-y*10,y:x*7+y*31});
const inverse=(x,y)=>({x:(31*x+10*y)/1558,y:(48*y-7*x)/1558});
const framing=(width,height)=>({zoom:width/height<.8?1:width>1000?.92:.96,anchorY:width/height<.8?.56:.55});
const limits=zone=>zone===0?{w:44,h:40}:{w:30,h:27};
function screen(x,y,z,camera,width,height){const p=project(x,y),v=framing(width,height);return{x:width/2+(p.x-camera.x)*v.zoom,y:height*v.anchorY+(p.y-camera.y-z)*v.zoom}}
function world(x,y,camera,width,height){const v=framing(width,height);return inverse((x-width/2)/v.zoom+camera.x,(y-height*v.anchorY)/v.zoom+camera.y)}
function drawCache(ctx,cache,origin,offsetX,offsetY){const zoom=window.AstraeonView.zoom,left=origin.x-offsetX*zoom,top=origin.y-offsetY*zoom,sx=Math.max(0,-left/zoom),sy=Math.max(0,-top/zoom),ex=Math.min(cache.width,(ctx.canvas.clientWidth-left)/zoom),ey=Math.min(cache.height,(ctx.canvas.clientHeight-top)/zoom);if(ex>sx&&ey>sy)ctx.drawImage(cache,sx,sy,ex-sx,ey-sy,left+sx*zoom,top+sy*zoom,(ex-sx)*zoom,(ey-sy)*zoom)}
window.AstraeonView={scale,project,inverse,framing,limits,screen,world,drawCache,zoom:1};
})();
