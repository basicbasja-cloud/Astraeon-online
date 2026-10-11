import {bodyFaces} from './geometry.mjs';
import {DIRECTIONS,PERIOD,pose,createState,swapAppearance,project,rotate,add,sub,mul,unit,mod,viewIndex,sampleTime} from './motion.mjs';
const state=createState();const $=id=>document.getElementById(id);
const views=$('views'),strip=$('strip');let last=performance.now(),yaw=0,pitch=46;
function draw(ctx,p,direction,x,y,scale,appearance,grid=true){
  const proj=q=>{const a=project(q,direction,pitch,yaw);return [x+a[0]*scale,y+a[1]*scale,a[2]];};
  ctx.save();ctx.beginPath();ctx.rect(x-132,y-245,264,268);ctx.clip();
  if(grid){
    ctx.strokeStyle='#365068';ctx.lineWidth=1;
    for(let i=-5;i<=5;i++) {
      const row=i*.23-mod(p.root[1],.23);
      for(const [a,b] of [[[-1,row,0],[1,row,0]],[[i*.23,-1,0],[i*.23,1,0]]]){
        const aa=proj(a),bb=proj(b);ctx.beginPath();ctx.moveTo(...aa.slice(0,2));ctx.lineTo(...bb.slice(0,2));ctx.stroke();
      }
    }
  }
  for(const side of ['left','right']) {
    const foot=p.feet[side],a=proj(foot.point);ctx.beginPath();ctx.ellipse(a[0],a[1],12,5,0,0,Math.PI*2);ctx.strokeStyle=foot.contact?'#79d7a8':'#546b7d';ctx.lineWidth=2;ctx.stroke();
  }
  const faces=bodyFaces(p,appearance).map(f=>({...f,points:f.points.map(proj)}));
  faces.sort((a,b)=>a.points.reduce((s,p)=>s+p[2],0)/a.points.length-b.points.reduce((s,p)=>s+p[2],0)/b.points.length);
  for(const f of faces){ctx.beginPath();ctx.moveTo(...f.points[0].slice(0,2));f.points.slice(1).forEach(q=>ctx.lineTo(...q.slice(0,2)));ctx.closePath();ctx.fillStyle=f.color;ctx.fill();ctx.strokeStyle='#23394b';ctx.lineWidth=.7;ctx.stroke();}
  ctx.restore();
}
function sampleElapsed(t){return sampleTime(state.action,t,$('sampling').value);}
function render(){
  const p=pose(state.action,sampleElapsed(state.elapsed)),ctx=views.getContext('2d');
  p.root=pose(state.action,state.elapsed).root; // Ground motion stays continuous even with held sprite poses.
  ctx.clearRect(0,0,views.width,views.height);
  for(let d=0;d<8;d++) {
    const x=(d%4)*280+140,y=Math.floor(d/4)*280+242;
    draw(ctx,p,d,x,y,132,state.appearance);
    ctx.fillStyle='#d5e6f1';ctx.font='14px system-ui';ctx.fillText(`World ${DIRECTIONS[d]} · view ${DIRECTIONS[viewIndex(d,yaw)]}`,x-125,y-216);
    ctx.fillStyle='#93aec2';ctx.fillText(`${p.feet.left.contact?'L planted':'L swing'} / ${p.feet.right.contact?'R planted':'R swing'}`,x-125,y+25);
  }
  const sctx=strip.getContext('2d');sctx.clearRect(0,0,strip.width,strip.height);
  for(let i=0;i<8;i++){
    const t=i/8*(state.action==='attack'?.72:PERIOD);draw(sctx,pose(state.action,t),0,i*140+70,180,96,state.appearance,false);
    sctx.fillStyle='#a6bfd2';sctx.font='12px system-ui';sctx.fillText(`${i} · phase ${(i/8).toFixed(3)}`,i*140+15,205);
  }
  $('phase').value=Math.floor(p.phase*999);$('readout').textContent=`${state.action} · phase ${p.phase.toFixed(3)} · ${state.speed}× · pitch ${pitch}° · ${$('sampling').selectedOptions[0].textContent} · all parts share ${state.elapsed.toFixed(3)} seconds`;
}
for(const slot of ['hat','coat','weapon','shield'])$(slot).addEventListener('change',()=>{swapAppearance(state,slot,$(slot).value);render();});
$('action').addEventListener('change',()=>{state.action=$('action').value;state.elapsed=0;render();});
$('speed').addEventListener('change',()=>{state.speed=Number($('speed').value);});
$('yaw').addEventListener('change',()=>{yaw=Number($('yaw').value);render();});
$('pitch').addEventListener('input',()=>{pitch=Number($('pitch').value);render();});
$('sampling').addEventListener('change',render);
$('pause').addEventListener('click',()=>{state.running=!state.running;$('pause').textContent=state.running?'Pause':'Play';});
$('phase').addEventListener('input',()=>{state.running=false;$('pause').textContent='Play';state.elapsed=Number($('phase').value)/999*(state.action==='attack'?.72:PERIOD);render();});
function tick(now){if(state.running)state.elapsed+=(now-last)/1000*state.speed;last=now;render();requestAnimationFrame(tick);}
// Read-only diagnostics for measurements; controls above drive behavior.
window.motionStudy={snapshot:()=>structuredClone(state)};
render();requestAnimationFrame(tick);
