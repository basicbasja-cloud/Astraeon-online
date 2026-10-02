/* Authored atlas poses with world-space stance-foot locking. No root bob or
 * costume deformation: only textured leg segments follow registered contacts. */
(() => {
'use strict';
const mix=(a,b,k)=>a.map((v,i)=>v+(b[i]-v)*k);
function draw(ctx,iso,t,image,meta,registration,row,column,unit,foot,left,torso){
 const backward=(t.velocity?.x||0)*t.facingDirection.x+(t.velocity?.y||0)*t.facingDirection.y<-.05;
 const native=registration.cellSize===256;
 const phase=(((native?1:backward?-1:1)*t.gait%1+1)%1)*8,fraction=phase-Math.floor(phase),next=(column+1)%8;
 const current=registration.frames[row*8+column],future=registration.frames[row*8+next];
 if(!current?.contacts?.[0]?.hip)return false;
 const bounds=meta.frames[row*8+column],anchor=registration.anchors[row*8+column];
 const origin={x:foot.x+left,y:foot.y-anchor[1]*unit};
 const angle=Math.PI/2-row*Math.PI/4,pitchDelta=native&&Number.isFinite(t.posePitch)?t.posePitch-(t.profile?.bodyPitch||0):0,shift=[Math.cos(angle)*pitchDelta,Math.sin(angle)*pitchDelta*.3];
 const legs=current.contacts.map((contact,i)=>{
  const other=future.contacts[i],hip=mix(contact.hip,other.hip,fraction),knee=mix(contact.knee,other.knee,fraction),authoredFoot=mix(contact.foot,other.foot,fraction),tracked=t.feet?.[i];
  hip[0]+=shift[0];hip[1]+=shift[1];let target=authoredFoot;
  if(tracked){
   const planted=iso(tracked.x,tracked.y,((tracked.groundZ??t.position.z??0)+(tracked.z||0))*35);
   target=[(planted.x-origin.x)/unit,(planted.y-origin.y)/unit];
   // Carry the knee with the ankle while keeping the authored hip seated in the costume.
   knee[0]+=(target[0]-authoredFoot[0])*.55;knee[1]+=(target[1]-authoredFoot[1])*.55;
  }
  return {source:contact,hip,knee,foot:target};
 }).sort((a,b)=>a.foot[1]-b.foot[1]);
 function segment(sourceA,sourceB,targetA,targetB,radius){
  const sourceLength=Math.hypot(sourceB[0]-sourceA[0],sourceB[1]-sourceA[1]),targetLength=Math.hypot(targetB[0]-targetA[0],targetB[1]-targetA[1]);
  if(sourceLength<1||targetLength<1)return;
  const angle=Math.atan2(sourceB[1]-sourceA[1],sourceB[0]-sourceA[0]),nx=-Math.sin(angle)*radius,ny=Math.cos(angle)*radius,ex=Math.cos(angle)*5,ey=Math.sin(angle)*5;
  ctx.save();ctx.translate(origin.x,origin.y);ctx.scale(unit,unit);ctx.translate(...targetA);ctx.rotate(Math.atan2(targetB[1]-targetA[1],targetB[0]-targetA[0]));ctx.scale(targetLength/sourceLength,1);ctx.rotate(-angle);ctx.translate(-sourceA[0],-sourceA[1]);
  const points=[[sourceA[0]+nx-ex,sourceA[1]+ny-ey],[sourceB[0]+nx+ex,sourceB[1]+ny+ey],[sourceB[0]-nx+ex,sourceB[1]-ny+ey],[sourceA[0]-nx-ex,sourceA[1]-ny-ey]];
  ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();ctx.clip();ctx.drawImage(image,...bounds,0,0,bounds[2],bounds[3]);ctx.restore();
 }
 for(const leg of legs){segment(leg.source.hip,leg.source.knee,leg.hip,leg.knee,9);segment(leg.source.knee,leg.source.foot,leg.knee,leg.foot,10)}
 // The painted torso, hair, sword and cape keep their stable registered silhouette.
 if(torso){const cell=registration.cellSize||192;ctx.drawImage(torso,0,row*cell,cell,cell,origin.x+shift[0]*unit,origin.y+shift[1]*unit,cell*unit,cell*unit)}
 else{ctx.save();ctx.beginPath();ctx.rect(origin.x,origin.y,bounds[2]*unit,current.bodyClipY*unit);ctx.clip();ctx.drawImage(image,...bounds,origin.x,origin.y,bounds[2]*unit,bounds[3]*unit);ctx.restore()}
 return true;
}
window.AstraeonWarriorRig={draw};
})();
