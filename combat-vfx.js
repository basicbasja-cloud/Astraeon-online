/* Reusable painted-hero feedback. Node colors reuse the same world-space geometry. */
(() => {
'use strict';
function draw(ctx,iso,f){
 const a=Math.max(0,Math.min(1,f.life/(f.maxLife||.5))),zoom=window.AstraeonView.zoom;
 if(f.kind==='slash'){
  const heading=Math.atan2(f.direction.y,f.direction.x),age=1-a,sweep=.88,radius=.88+age*.58;
  const point=(angle,r,lift=0)=>iso(f.x+Math.cos(angle)*r,f.y+Math.sin(angle)*r,30+Math.sin((angle-heading+sweep)/(sweep*2)*Math.PI)*10+lift);
  const arc=(start,end,r)=>{ctx.beginPath();for(let i=0;i<=24;i++){const p=point(start+(end-start)*i/24,r);i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y)}};
  // Layer a broad painted crescent under a bright, tapered blade edge.
  ctx.fillStyle=f.color;ctx.globalAlpha*=.48;ctx.beginPath();
  for(let i=0;i<=24;i++){const angle=heading-sweep+i/24*sweep*2,p=point(angle,radius);i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y)}
  for(let i=24;i>=0;i--){const u=i/24,angle=heading-sweep+u*sweep*2,p=point(angle,radius-(.22+.08*a)*Math.sin(u*Math.PI));ctx.lineTo(p.x,p.y)}
  ctx.closePath();ctx.fill();ctx.globalAlpha/=.48;
  ctx.lineCap='round';ctx.strokeStyle=f.color;ctx.shadowColor=f.color;ctx.shadowBlur=10*zoom;ctx.lineWidth=(2+2.5*a)*zoom;arc(heading-sweep,heading+sweep,radius);ctx.stroke();
  ctx.shadowBlur=0;ctx.globalAlpha*=.86;ctx.strokeStyle='#fff2cf';ctx.lineWidth=1.25*zoom;arc(heading-sweep*.84,heading+sweep*.84,radius-.025);ctx.stroke();
  // Two fine trailing strokes keep the hit legible without hiding the target.
  ctx.globalAlpha*=.62;ctx.strokeStyle='#fff8e5';ctx.lineWidth=.72*zoom;arc(heading-sweep*.69,heading+sweep*.59,radius-.17);ctx.stroke();
  ctx.globalAlpha/= (.86*.62);
  // A short six-point contact glint makes skill impacts readable at isometric scale.
  const flash=Math.max(0,1-age/.58),side={x:-f.direction.y,y:f.direction.x},cx=f.x+f.direction.x*.45,cy=f.y+f.direction.y*.45;
  if(flash>0){ctx.globalAlpha*=flash;ctx.lineCap='round';ctx.shadowColor=f.color;ctx.shadowBlur=8*zoom;
   for(let i=0;i<6;i++){const angle=i*Math.PI/3,dx=f.direction.x*Math.cos(angle)+side.x*Math.sin(angle),dy=f.direction.y*Math.cos(angle)+side.y*Math.sin(angle),from=iso(cx+dx*.10,cy+dy*.10,38),to=iso(cx+dx*(.22+age*.1),cy+dy*(.22+age*.1),38);ctx.strokeStyle=i%2?'#fff3d4':f.color;ctx.lineWidth=(i%2?1.25:1.9)*zoom;ctx.beginPath();ctx.moveTo(from.x,from.y);ctx.lineTo(to.x,to.y);ctx.stroke()}
   ctx.shadowBlur=0;
  }
  return true;
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
