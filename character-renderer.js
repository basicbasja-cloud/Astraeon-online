/* Painted directional actor adapters and grounded world-space contact shadows. */
(() => {
'use strict';
function shadow(ctx,iso,t,radius=.4,alpha=.24){const p=t.position;ctx.save();ctx.fillStyle=`rgba(8,18,24,${alpha})`;ctx.beginPath();for(let i=0;i<=20;i++){const a=i*Math.PI/10,q=iso(p.x+Math.cos(a)*radius,p.y+Math.sin(a)*radius,p.z*35);i?ctx.lineTo(q.x,q.y):ctx.moveTo(q.x,q.y)}ctx.closePath();ctx.fill();ctx.restore()}
function humanoid(ctx,iso,t,options={}){shadow(ctx,iso,t,.4*(options.scale||1));return window.AstraeonDirectionalArt.humanoid(ctx,iso,t,options)}
function monster(ctx,iso,t,entity,time){shadow(ctx,iso,t,entity.boss?.7:.4);return window.AstraeonDirectionalArt.monster(ctx,iso,t,entity,time)}
window.AstraeonCharacters={humanoid,monster,shadow};
})();
