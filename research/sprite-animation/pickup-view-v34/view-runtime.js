/* New authored view. Anatomical owners come from the source, never screen order. */
function viewPose(source,i){
 const b=source.frames[0].points,p=source.frames[i].points;
 const pelvis=add([192,309],sourceDelta(source,i,'pelvis'));pelvis[1]=309+sourceDelta(source,i,'pelvis')[1]*2.8;
 const restSpine=[12,-104],spineBase=sub(b.head.xy,b.pelvis.xy),spine=sub(p.head.xy,p.pelvis.xy),basis=angle(restSpine)-angle(spineBase);
 const neck=add(pelvis,mul(rot(spine,basis),length(restSpine)/length(spineBase))),turn=angle(sub(neck,pelvis))-angle(restSpine),j={pelvis,neck};
 j['right.hip']=add(pelvis,[-20,13]);j['left.hip']=add(pelvis,[17,8]);
 j['right.ankle']=[165,450];j['left.ankle']=[232,425];
 j['right.knee']=ik(j['right.hip'],j['right.ankle'],78,59,-1);j['left.knee']=ik(j['left.hip'],j['left.ankle'],68,45,-1);
 j['right.shoulder']=add(neck,rot([-45,12],turn));j['left.shoulder']=add(neck,rot([28,9],turn));
 j['right.wrist']=add([154,291],mul(sourceDelta(source,i,'right.wrist'),1.1));j['left.wrist']=add([252,307],mul(sourceDelta(source,i,'left.wrist'),1.35));
 j['right.elbow']=ik(j['right.shoulder'],j['right.wrist'],60,50,1);j['left.elbow']=ik(j['left.shoulder'],j['left.wrist'],52,50,1);
 return{joints:j,turn,index:i,source_time_seconds:source.frames[i].source_time_seconds,view:'B',near_anatomical_side:'right',source_motion_adapted:true};
}
function viewRows(parts,q,style){
 if(!['original','silver','bald'].includes(style)||q.view!=='B')throw Error('Unsupported appearance/view');
 const j=q.joints,rows=[],get=n=>{const p=parts.find(p=>p.name===n&&p.view==='B');if(!p)throw Error('Missing view B asset: '+n);return p};
 const rigid=(n,pos,r=0,s=null)=>{const p=get(n);rows.push({name:n,part:p,matrix:rigidMatrix(p,pos,r,s??p.width_scale),view:'B'})};
 const bone=(n,a,b)=>{const p=get(n);rows.push({name:n,part:p,matrix:boneMatrix(p,j[a],j[b]),view:'B',joint_chain:[a,b]})};
 rigid('cape',j.neck,q.turn);
 rigid('left.foot',j['left.ankle']);bone('left.shin','left.knee','left.ankle');bone('left.thigh','left.hip','left.knee');
 rigid('right.foot',j['right.ankle']);bone('right.shin','right.knee','right.ankle');bone('right.thigh','right.hip','right.knee');
 bone('left.upperarm','left.shoulder','left.elbow');bone('left.forearm','left.elbow','left.wrist');
 // Far anatomical left cloth behind torso/near right limbs, not swapped to near hip.
 rigid('teal_panel',add(j.pelvis,[22,8]),q.turn*.12);
 bone('torso','neck','pelvis');rigid('side_tabard',add(j.pelvis,[-18,8]),q.turn*.12);rigid('front_tabard',add(j.pelvis,[7,8]),q.turn*.1);
 if(style==='original')rigid('head_hair',j.neck,q.turn);
 else{if(style==='silver')rigid('hair.rear',j.neck,q.turn);rigid('head.base',j.neck,q.turn);if(style==='silver')rigid('hair.front',j.neck,q.turn)}
 bone('right.upperarm','right.shoulder','right.elbow');bone('right.forearm','right.elbow','right.wrist');
 return rows;
}
window.ViewPickup={pose:viewPose,rows:viewRows};
