// Original diagnostic geometry shared by preview and offline exporter.
import {add,sub,mul,unit,rotate} from './motion.mjs';
const faceColors=['#afc2d1','#839ead','#6a8799','#93aebe','#7794a5','#a0b9c9'];
function cross(a,b){return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];}
function box(center,size,angle,color,faces,part='body'){
  const vertices=[];
  for(const z of [-1,1])for(const y of [-1,1])for(const x of [-1,1]) vertices.push(add(center,rotate([x*size[0]/2,y*size[1]/2,z*size[2]/2],angle)));
  [[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]].forEach((ids,i)=>faces.push({part,points:ids.map(j=>vertices[j]),color:Array.isArray(color)?color[i]:color}));
}
function bone(limb,radius,color,faces,part='body'){
  const axis=unit(sub(limb.end,limb.start)),hint=Math.abs(axis[0])<.8?[1,0,0]:[0,1,0];
  const u=unit(cross(axis,hint)),v=unit(cross(axis,u));const vertices=[];
  for(const end of [limb.start,limb.end]) for(const a of [-1,1])for(const b of [-1,1])vertices.push(add(end,add(mul(u,a*radius),mul(v,b*radius))));
  [[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]].forEach(ids=>faces.push({part,points:ids.map(j=>vertices[j]),color}));
}
export function bodyFaces(p,appearance){
  const f=[],coat=appearance.coat==='red'?'#ad615e':'#54899f';
  for(const side of ['left','right']) {
    const l=p.legs[side];bone({start:l.start,end:l.joint},.085,'#688194',f);bone({start:l.joint,end:l.end},.065,'#7892a4',f);
    box(add(p.feet[side].point,[0,.05,.045]),[.17,.28,.09],0,side==='left'?'#66bde0':'#edaa65',f);
    const a=p.arms[side];bone({start:a.start,end:a.joint},.075,coat,f);bone({start:a.joint,end:a.end},.055,'#d3bca4',f);
    box(a.end,[.10,.10,.10],p.twist,'#e1c3a6',f);
  }
  box(add(p.hip,[0,0,.06]),[.43,.28,.20],p.twist,coat,f);
  box(add(p.hip,[0,p.lean,.32]),[.49,.29,.35],p.twist,coat,f);
  box(add(p.hip,[0,p.lean,.56]),[.13,.13,.12],p.twist,'#dbc5ac',f);
  box(p.head,[.53,.45,.54],p.twist,faceColors,f);
  for(const sign of [-1,1])box(add(p.head,rotate([sign*.13,.232,.015],p.twist)),[.046,.025,.058],p.twist,'#192c3e',f);
  box(add(p.head,rotate([0,.255,-.055],p.twist)),[.07,.06,.06],p.twist,'#c3d2da',f);
  if(appearance.hat!=='none') {
    box(add(p.head,[0,0,.29]),[.59,.51,.12],p.twist,'#cfa76d',f,'hat');
    if(appearance.hat==='crest')box(add(p.head,[0,0,.42]),[.10,.44,.25],p.twist,'#d69273',f,'hat');
  }
  if(appearance.weapon!=='none') {
    const hand=p.arms.right.end,tip=add(hand,mul(p.swordDirection,appearance.weapon==='wand'?.45:.65));
    bone({start:hand,end:tip},appearance.weapon==='wand'?.025:.035,appearance.weapon==='wand'?'#cda774':'#d9e5eb',f,'weapon');
    box(add(hand,mul(p.swordDirection,.09)),[.20,.08,.06],p.twist,'#cca96f',f,'weapon');
  }
  if(appearance.shield!=='none') {
    const hand=p.arms.left.end,large=appearance.shield==='large';
    box(add(hand,rotate([-.06,.06,.05],p.twist)),[large?.40:.29,.09,large?.52:.34],p.twist,'#a9805c',f,'shield');
  }
  return f;
}
