/* Authored 2D modular rig driven by fresh external source. No frame fitting,
   image mirroring, synthesized repaint or attachment ownership inferred from color. */
const add=(a,b)=>a.map((v,i)=>v+b[i]),sub=(a,b)=>a.map((v,i)=>v-b[i]),mul=(v,k)=>v.map(x=>x*k),length=v=>Math.hypot(...v);
const rot=(v,a)=>[v[0]*Math.cos(a)-v[1]*Math.sin(a),v[0]*Math.sin(a)+v[1]*Math.cos(a)];
const angle=v=>Math.atan2(v[1],v[0]);
function ik(a,b,l1,l2,sign){const delta=sub(b,a),d=length(delta);if(d>l1+l2+1e-5||d<Math.abs(l1-l2)-1e-5)throw Error('Unreachable authored chain');const u=mul(delta,1/d),along=(l1*l1-l2*l2+d*d)/(2*d),h=Math.sqrt(Math.max(0,l1*l1-along*along)),perp=[-u[1],u[0]];return add(add(a,mul(u,along)),mul(perp,h*sign))}
function sourceDelta(source,i,n){return sub(source.frames[i].points[n].xy,source.frames[0].points[n].xy)}
function pose(source,i){
 const points=source.frames[i].points,base=source.frames[0].points;
 const pelvis=add([192,309],mul(sourceDelta(source,i,'pelvis'),1));pelvis[1]=309+sourceDelta(source,i,'pelvis')[1]*2.8;
 const spineBase=sub(base.head.xy,base.pelvis.xy),spine=sub(points.head.xy,points.pelvis.xy);
 const restSpine=[-12,-104],basis=angle(restSpine)-angle(spineBase),s=length(restSpine)/length(spineBase);
 const neck=add(pelvis,mul(rot(spine,basis),s)),turn=angle(sub(neck,pelvis))-angle(restSpine);
 const joints={pelvis,neck};
 joints['right.hip']=add(pelvis,[-17,8]);joints['left.hip']=add(pelvis,[20,13]);
 joints['right.ankle']=[165,429];joints['left.ankle']=[241,450];
 joints['right.knee']=ik(joints['right.hip'],joints['right.ankle'],68,45,1);
 joints['left.knee']=ik(joints['left.hip'],joints['left.ankle'],78,59,1);
 joints['right.shoulder']=add(neck,rot([-28,9],turn));joints['left.shoulder']=add(neck,rot([45,12],turn));
 joints['right.wrist']=add([118,291],mul(sourceDelta(source,i,'right.wrist'),1.35));
 joints['left.wrist']=add([245,315],mul(sourceDelta(source,i,'left.wrist'),1.35));
 joints['right.elbow']=ik(joints['right.shoulder'],joints['right.wrist'],52,50,-1);
 joints['left.elbow']=ik(joints['left.shoulder'],joints['left.wrist'],60,50,-1);
 return {joints,turn,index:i,source_time_seconds:source.frames[i].source_time_seconds,foot_anchors_authored:true,source_motion_adapted:true}
}
function boneMatrix(part,a,b){
 const v=sub(part.end,part.pivot),len=length(v),e=mul(v,1/len),n=[e[1],-e[0]],delta=sub(b,a),w=mul(delta,1/length(delta)),z=[w[1],-w[0]],sx=part.width_scale,sy=length(delta)/len;
 const A=z[0]*n[0]*sx+w[0]*e[0]*sy,B=z[1]*n[0]*sx+w[1]*e[0]*sy,C=z[0]*n[1]*sx+w[0]*e[1]*sy,D=z[1]*n[1]*sx+w[1]*e[1]*sy;
 return [A,B,C,D,a[0]-A*part.pivot[0]-C*part.pivot[1],a[1]-B*part.pivot[0]-D*part.pivot[1]]
}
function rigidMatrix(part,position,turn=0,scale=part.width_scale){const c=Math.cos(turn)*scale,s=Math.sin(turn)*scale;return[c,s,-s,c,position[0]-c*part.pivot[0]+s*part.pivot[1],position[1]-s*part.pivot[0]-c*part.pivot[1]]}
function apply(m,p){return[m[0]*p[0]+m[2]*p[1]+m[4],m[1]*p[0]+m[3]*p[1]+m[5]]}
function recipe(parts,q){
 const j=q.joints,get=n=>parts.find(p=>p.name===n),rows=[];
 const rigid=(n,pos,r=0,s=null)=>{let p=get(n);rows.push({name:n,part:p,matrix:rigidMatrix(p,pos,r,s??p.width_scale)})};
 const bone=(n,a,b)=>{let p=get(n);rows.push({name:n,part:p,matrix:boneMatrix(p,j[a],j[b])})};
 rigid('cape',j.neck,q.turn);
 rigid('right.foot',j['right.ankle'],0,.30);rigid('left.foot',j['left.ankle'],0,.29);
 bone('right.thigh','right.hip','right.knee');bone('right.shin','right.knee','right.ankle');
 bone('left.thigh','left.hip','left.knee');bone('left.shin','left.knee','left.ankle');
 bone('right.upperarm','right.shoulder','right.elbow');bone('right.forearm','right.elbow','right.wrist');
 bone('torso','neck','pelvis');
 rigid('side_tabard',add(j.pelvis,[-18,8]),q.turn*.12);
 rigid('front_tabard',add(j.pelvis,[-7,8]),q.turn*.1);
 rigid('teal_panel',add(j.pelvis,[22,8]),q.turn*.12);
 rigid('head_hair',j.neck,q.turn);
 bone('left.upperarm','left.shoulder','left.elbow');bone('left.forearm','left.elbow','left.wrist');

 return rows
}
function render(ctx,rows,images,owners=false){
 ctx.clearRect(0,0,384,512);for(const r of rows){ctx.save();ctx.setTransform(...r.matrix);ctx.drawImage(images[r.name],0,0);ctx.restore()}
 if(owners){ // Debug topology is a separate draw, not recoloring actor pixels.
  ctx.strokeStyle='#edf0ff';ctx.lineWidth=1;for(const r of rows)if(r.part.end){const a=apply(r.matrix,r.part.pivot),b=apply(r.matrix,r.part.end);ctx.strokeStyle=r.name.startsWith('right.')?'#3b9eff':r.name.startsWith('left.')?'#ff9937':'#ffffff';ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.stroke();for(const p of[a,b]){ctx.beginPath();ctx.arc(...p,3,0,Math.PI*2);ctx.stroke()}}
 }
}
window.ModularPickup={pose,recipe,render,apply,ik};
