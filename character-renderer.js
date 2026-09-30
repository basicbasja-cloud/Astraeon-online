/* Painted directional actor adapters and grounded world-space contact shadows. */
(() => {
'use strict';
function shadow(ctx,iso,t,radius=.4,alpha=.24){
 const p=t.position,foot=iso(p.x,p.y),x=iso(p.x+1,p.y),y=iso(p.x,p.y+1);
 ctx.save();ctx.transform(x.x-foot.x,x.y-foot.y,y.x-foot.x,y.y-foot.y,foot.x,foot.y);
 // Shared upper-left sun; diffuse cast shadow and tight contact stay on the ground.
 for(const [dx,dy,r,opacity] of [[.14,.16,radius*1.55,alpha*.6],[0,0,radius*.75,alpha]]){
  const g=ctx.createRadialGradient(dx,dy,0,dx,dy,r);g.addColorStop(0,`rgba(25,36,30,${opacity})`);g.addColorStop(1,'rgba(25,36,30,0)');ctx.fillStyle=g;ctx.fillRect(dx-r,dy-r,r*2,r*2);
 }
 ctx.restore();
}
function humanoid(ctx,iso,t,options={}){shadow(ctx,iso,t,.4*(options.scale||1));return window.AstraeonDirectionalArt.humanoid(ctx,iso,t,options)}
function monster(ctx,iso,t,entity,time){shadow(ctx,iso,t,entity.boss?.7:.4);return window.AstraeonDirectionalArt.monster(ctx,iso,t,entity,time)}
window.AstraeonCharacters={humanoid,monster,shadow};
})();
