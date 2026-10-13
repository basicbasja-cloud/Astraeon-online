// Pose-bound hand sweep. No rigid weapon image, rotation or independent sword clock.
export const TIMES=[0,100,200,260,320,400,500,600];
export const DURATION=720;
export const FX_START=260, FX_END=440;
export function keyAt(t){return TIMES.reduce((i,v,j)=>t>=v?j:i,0)}
function mix(a,b,u){return a.map((v,k)=>v+(b[k]-v)*u)}
function normAngle(a,b){return (b-a+540)%360-180}
function spanAt(t,data){
  const i=keyAt(t),j=Math.min(i+1,7),u=j===i?0:Math.min(1,Math.max(0,(t-TIMES[i])/(TIMES[j]-TIMES[i])));
  const a=data.frames[i],b=data.frames[j],palm=mix(a.palm_xy,b.palm_xy,u);
  const av=a.guide_vector_xy,bv=b.guide_vector_xy;
  const angle=Math.atan2(av[1],av[0])*180/Math.PI;
  const target=Math.atan2(bv[1],bv[0])*180/Math.PI;
  const theta=(angle+normAngle(angle,target)*u)*Math.PI/180;
  const radius=(Math.hypot(...av)+(Math.hypot(...bv)-Math.hypot(...av))*u)*data.virtual_blade_scale;
  return {palm,vector:[Math.cos(theta)*radius,Math.sin(theta)*radius]};
}
export function geometry(t,data,{cancelled=false,enabled=true}={}){
  if(cancelled||!enabled||t<FX_START||t>=FX_END)return {active:false,outer:[],inner:[],endpoint_error_px:null};
  const key=keyAt(t),end=TIMES[key],fade=t>=400?(FX_END-t)/(FX_END-400):1;
  const length= Math.max(0,(end-220)*fade);
  const start=end-length,outer=[],inner=[];
  for(let j=0;j<=32;j++){
    const s=spanAt(start+(end-start)*j/32,data);
    outer.push(mix(s.palm,s.palm.map((v,k)=>v+s.vector[k]),1));
    inner.push(s.palm.map((v,k)=>v+s.vector[k]*(.72-.4*Math.pow(j/32,6))));
  }
  const current=spanAt(end,data),tip=current.palm.map((v,k)=>v+current.vector[k]);
  return {active:true,key,outer,inner,alpha:.78*fade,head_palm_xy:current.palm,tip_xy:tip,
    endpoint_error_px:Math.hypot(...outer.at(-1).map((v,k)=>v-tip[k])),
    mode:'hand_sweep_tail',scope:'Authored interpolation of bound painted palms plus projected source blade vectors. No rendered blade or recovered painted 3D motion.'};
}
export function drawTail(ctx,t,data,state={}){
  const g=geometry(t,data,state);if(!g.active)return g;
  ctx.save();ctx.globalAlpha=g.alpha;ctx.beginPath();g.outer.forEach((p,j)=>j?ctx.lineTo(...p):ctx.moveTo(...p));
  [...g.inner].reverse().forEach(p=>ctx.lineTo(...p));ctx.closePath();
  const gradient=ctx.createLinearGradient(...g.outer[0],...g.outer.at(-1));
  gradient.addColorStop(0,'rgba(144,145,190,0)');gradient.addColorStop(.22,'rgba(181,184,225,.35)');
  gradient.addColorStop(.72,'rgba(230,232,255,.95)');gradient.addColorStop(1,'rgba(255,250,225,1)');
  ctx.fillStyle=gradient;ctx.fill();ctx.beginPath();g.outer.forEach((p,j)=>j?ctx.lineTo(...p):ctx.moveTo(...p));
  ctx.strokeStyle='rgba(255,252,231,.9)';ctx.lineWidth=2;ctx.stroke();ctx.restore();return g;
}
