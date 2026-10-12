// Procedural runtime FX from bound observed painted blade spans. No body warp.
// Between-pose sweep is authored interpolation, not recovered animation pixels.
export const ATTACK_STARTS=[0,100,220,300,360,440,560,700];
export const ATTACK_DURATION=800;
export function attackKey(ms){
 if(!Number.isFinite(ms)||ms<0)throw new Error('Invalid authoritative time');
 let i=0;for(let k=0;k<ATTACK_STARTS.length;k++)if(ms>=ATTACK_STARTS[k])i=k;return i;
}
export function trailState(ms,cancelled=false){
 const key=attackKey(ms);return {key,active:!cancelled&&ms>=300&&ms<430,fade:Math.max(0,Math.min(1,(430-ms)/70)),expiry_ms:430};
}
function mix(a,b,u){return a.map((v,k)=>v+(b[k]-v)*u);}
function sweep(a,b,u){
 const av=a.blade_tip_xy.map((v,k)=>v-a.blade_base_xy[k]),bv=b.blade_tip_xy.map((v,k)=>v-b.blade_base_xy[k]);
 const aa=Math.atan2(av[1],av[0]),ba=Math.atan2(bv[1],bv[0]);let d=ba-aa;while(d>Math.PI)d-=2*Math.PI;while(d<-Math.PI)d+=2*Math.PI;
 const base=mix(a.blade_base_xy,b.blade_base_xy,u),len=Math.hypot(...av)+(Math.hypot(...bv)-Math.hypot(...av))*u,angle=aa+d*u,vec=[Math.cos(angle)*len,Math.sin(angle)*len];
 return {outer:base.map((v,k)=>v+vec[k]),inner:base.map((v,k)=>v+vec[k]*.60)};
}
export function trailGeometry(ms,frames,cancelled=false){
 const state=trailState(ms,cancelled);if(!state.active)return {...state,outer:[],inner:[],blade_endpoint_error_px:null};
 const last=state.key;const samples=[];
 for(let k=Math.max(2,last-2);k<last;k++)for(let j=0;j<12;j++)samples.push(sweep(frames[k],frames[k+1],j/12));
 samples.push(sweep(frames[last],frames[last],1));
 const outer=samples.map(x=>x.outer),inner=samples.map(x=>x.inner);const endpoint=outer.at(-1),tip=frames[last].blade_tip_xy;
 return {...state,outer,inner,blade_endpoint_error_px:Math.hypot(endpoint[0]-tip[0],endpoint[1]-tip[1]),scope:'Authored polar interpolation of manually observed painted blade spans; source-only socket proof and visual grip review remain separate.'};
}
export function drawTrail(ctx,geometry){
 if(!geometry.active)return;ctx.save();ctx.globalAlpha=.62*geometry.fade;
 ctx.beginPath();geometry.outer.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));[...geometry.inner].reverse().forEach(p=>ctx.lineTo(...p));ctx.closePath();
 const last=geometry.outer.at(-1),gradient=ctx.createLinearGradient(geometry.outer[0][0],geometry.outer[0][1],last[0],last[1]);gradient.addColorStop(0,'rgba(247,177,70,0)');gradient.addColorStop(.45,'rgba(255,220,136,.45)');gradient.addColorStop(1,'rgba(255,250,228,.85)');ctx.fillStyle=gradient;ctx.fill();
 ctx.globalAlpha=.7*geometry.fade;ctx.beginPath();geometry.outer.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.strokeStyle='#fff4cf';ctx.lineWidth=2.2;ctx.lineJoin='round';ctx.stroke();ctx.restore();
}
