/* Reusable painted-hero feedback. Node colors reuse the same world-space geometry. */
(() => {
'use strict';
function draw(ctx,iso,f){
 const a=Math.max(0,Math.min(1,f.life/(f.maxLife||.5))),zoom=window.AstraeonView.zoom;
 if(f.kind==='slash'){
  const heading=Math.atan2(f.direction.y,f.direction.x),radius=.6+(1-a)*1.1;
  const point=(angle,r)=>iso(f.x+Math.cos(angle)*r,f.y+Math.sin(angle)*r,30+Math.sin((angle-heading+.85)/1.7*Math.PI)*9);
  ctx.fillStyle=f.color;ctx.globalAlpha*=.34;ctx.beginPath();
  for(let i=0;i<=24;i++){const angle=heading-.85+i/24*1.7,p=point(angle,radius);i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y)}
  for(let i=24;i>=0;i--){const angle=heading-.85+i/24*1.7,p=point(angle,radius-.3*a*Math.sin(i/24*Math.PI));ctx.lineTo(p.x,p.y)}ctx.closePath();ctx.fill();
  ctx.globalAlpha/=.34;ctx.strokeStyle=f.color;ctx.shadowColor=f.color;ctx.shadowBlur=7*zoom;ctx.lineWidth=(1+2*a)*zoom;ctx.beginPath();
  for(let i=0;i<=24;i++){const p=point(heading-.85+i/24*1.7,radius);i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y)}ctx.stroke();
  ctx.shadowBlur=0;ctx.globalAlpha*=.75;ctx.strokeStyle='#fff0cb';ctx.lineWidth=.8*zoom;ctx.stroke();return true;
 }
 if(f.kind==='dodge-dust'){
  const d=f.direction,right={x:d.y,y:-d.x},progress=1-a;
  for(let i=0;i<7;i++){
   const side=(i%2?1:-1)*(.12+progress*(.25+i*.025)),behind=progress*(.3+i*.06),x=f.x-d.x*behind+right.x*side,y=f.y-d.y*behind+right.y*side,p=iso(x,y,2+Math.sin(progress*Math.PI)*(3+i));
   ctx.fillStyle=i%3?'#c8b99a':'#8d846b';ctx.globalAlpha=a*.35;ctx.beginPath();ctx.ellipse(p.x,p.y,(2+progress*5)*zoom,(1+progress*2)*zoom,0,0,Math.PI*2);ctx.fill();
  }
  ctx.globalAlpha=a*.2;ctx.strokeStyle='#e4d7b7';ctx.lineWidth=1.1*zoom;
  for(const side of [-1,1]){const p=iso(f.x+right.x*.25*side,f.y+right.y*.25*side,18),q=iso(f.x-d.x*.75+right.x*.25*side,f.y-d.y*.75+right.y*.25*side,18);ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke()}return true;
 }
 return false;
}
window.AstraeonVFX={draw};
})();
