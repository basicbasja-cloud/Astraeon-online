/* Appearance changes only: immutable v32 pose and non-head recipe retained. */
const multiply2D=(a,b)=>[a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5]];
function hairRows(baseRows,bank,style){
 const head=baseRows.find(r=>r.name==='head_hair');if(!head)throw Error('Missing original head mount');
 const inserts=style==='original'?[head]:[...(style==='bald'?[]:[bank.parts.find(p=>p.name===style+'.rear')]),bank.parts.find(p=>p.name==='head.base'),...(style==='bald'?[]:[bank.parts.find(p=>p.name===style+'.front')])].map(part=>({name:part.name,part,matrix:multiply2D(head.matrix,bank.registration[part.name]),head_mount_inherited:true}));
 if(inserts.some(r=>!r.part||!r.matrix))throw Error('Unknown/incomplete hair style');
 return baseRows.flatMap(r=>r.name==='head_hair'?inserts:[r]);
}
window.HairSwap={rows:hairRows,multiply:multiply2D};
