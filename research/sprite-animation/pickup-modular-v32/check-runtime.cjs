/* Actual browser renders and negative attachment/IK controls. No source pixels are
   substituted for generated parts. All assertions concern this one authored rig. */
const {chromium}=require('/opt/codex/runtimes/cua/lib/node_modules/playwright'),fs=require('fs'),assert=require('assert');
(async()=>{
 const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});const page=await b.newPage({viewport:{width:1100,height:900}});let errors=[],checks=[];
 page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',r=>r.abort());await page.setContent(fs.readFileSync(__dirname+'/rig-preview.html','utf8'));await page.waitForFunction(()=>window.pickup?.ready);
 const add=(name,pass)=>{assert(pass,name);checks.push({name,pass})};
 const receipt=await page.evaluate(()=>{
  const r=ModularPickup,part=pickup.data.parts,chain={
   'right.thigh':['right.hip','right.knee',68], 'right.shin':['right.knee','right.ankle',45],
   'left.thigh':['left.hip','left.knee',78], 'left.shin':['left.knee','left.ankle',59],
   'right.upperarm':['right.shoulder','right.elbow',52], 'right.forearm':['right.elbow','right.wrist',50],
   'left.upperarm':['left.shoulder','left.elbow',60], 'left.forearm':['left.elbow','left.wrist',50],
   torso:['neck','pelvis',null]};
  const dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
  function audit(q,rows){let issues=[];for(const row of rows){const c=chain[row.name],det=row.matrix[0]*row.matrix[3]-row.matrix[1]*row.matrix[2];if(det<=0)issues.push('MIRRORED_PART:'+row.name);
   if(c){if(dist(r.apply(row.matrix,row.part.pivot),q.joints[c[0]])>1e-6||dist(r.apply(row.matrix,row.part.end),q.joints[c[1]])>1e-6)issues.push('WRONG_PARENT:'+row.name);if(c[2]&&Math.abs(dist(q.joints[c[0]],q.joints[c[1]])-c[2])>1e-6)issues.push('BONE_LENGTH_DRIFT:'+row.name)}
   if(row.name.endsWith('.foot')){const owner=row.name.split('.')[0];if(dist(r.apply(row.matrix,row.part.pivot),q.joints[owner+'.ankle'])>1e-6)issues.push('FOOT_BIND:'+row.name)}
   if(row.part.semantic_owner!== (row.name.includes('.')?row.name.split('.')[0]:'body'))issues.push('WRONG_OWNER:'+row.name)
  }return issues;}
  const frames=pickup.poses.map(q=>({index:q.index,source_time_seconds:q.source_time_seconds,rows:r.recipe(part,q).map(row=>({name:row.name,semantic_owner:row.part.semantic_owner,texture_sha256:row.part.sha256,matrix:row.matrix,pivot_world:r.apply(row.matrix,row.part.pivot),end_world:row.part.end?r.apply(row.matrix,row.part.end):null})),issues:audit(q,r.recipe(part,q))}));
  const q=pickup.poses[3],rows=r.recipe(part,q),swapped=rows.map(row=>({...row,matrix:[...row.matrix]}));const a=swapped.find(row=>row.name==='right.thigh'),bb=swapped.find(row=>row.name==='left.thigh');[a.matrix,bb.matrix]=[bb.matrix,a.matrix];
  const mirror=rows.map(row=>({...row,matrix:[...row.matrix]}));mirror.find(row=>row.name==='right.forearm').matrix[0]*=-1;mirror.find(row=>row.name==='right.forearm').matrix[1]*=-1;
  let unreachable=false;try{r.ik([0,0],[300,0],68,45,1)}catch(e){unreachable=true}
  const variants={};for(const side of ['right','left']){const values=pickup.poses.map(q=>{const j=q.joints,h=j[side+'.hip'],k=j[side+'.knee'],a=j[side+'.ankle'];return (a[0]-h[0])*(k[1]-h[1])-(a[1]-h[1])*(k[0]-h[0])});variants[side]=values}
  return {frames,chain,swap_issues:audit(q,swapped),mirror_issues:audit(q,mirror),unreachable,knee_bend_signed_cross:variants};
 });
 add('all8 actual rig bindings/positive transforms/fixed limb lengths',receipt.frames.length===8&&receipt.frames.every(f=>f.issues.length===0));
 add('both knee bend branches retain sign',Object.values(receipt.knee_bend_signed_cross).every(v=>v.every(x=>x>0)));
 add('swapped thigh parents rejected',receipt.swap_issues.some(x=>x==='WRONG_PARENT:right.thigh')&&receipt.swap_issues.some(x=>x==='WRONG_PARENT:left.thigh'));
 add('mirrored forearm rejected',receipt.mirror_issues.some(x=>x==='MIRRORED_PART:right.forearm'));
 add('unreachable IK refused instead of stretching',receipt.unreachable);
 add('initial actual source image loads',await page.locator('#source-view').evaluate(im=>im.complete&&im.naturalWidth===384));
 await page.locator('#frame').evaluate(el=>{el.value=3;el.dispatchEvent(new Event('input'))});add('slider selects fourth actual source/actor pair',await page.evaluate(()=>pickup.index===3&&document.getElementById('status').textContent.includes('frame4')));
 const plain=await page.locator('#view').evaluate(c=>c.toDataURL());await page.locator('#bones').check();add('guide toggle changes debug draw without replacing pose',await page.locator('#view').evaluate(c=>c.toDataURL())!==plain&&await page.evaluate(()=>pickup.index===3));await page.locator('#bones').uncheck();
 for(const clock of ['source','game']){await page.locator('#clock').selectOption(clock);await page.locator('#play').click();await page.waitForFunction(()=>!pickup.running&&pickup.index===7,{},{timeout:4000});add(clock+' clock plays once and stops on exact eighth frame',await page.evaluate(()=>pickup.index===7&&!pickup.running));}
 add('native Canvas runtime without SVG',await page.locator('svg').count()===0&&await page.locator('canvas').count()===1);add('no browser errors',errors.length===0);
 let same=true;for(let i=0;i<8;i++){const url=await page.evaluate(i=>pickup.frame(i,false),i);same=same&&Buffer.from(url.split(',')[1],'base64').equals(fs.readFileSync(__dirname+'/frames/'+String(i).padStart(2,'0')+'.png'))}add('all8 saved RGBA frames exactly reproduce from live part renderer',same);
 await page.screenshot({path:__dirname+'/runtime-browser.png',fullPage:true});await b.close();fs.writeFileSync(__dirname+'/rig-bind-review.json',JSON.stringify(receipt,null,2)+'\n');fs.writeFileSync(__dirname+'/browser-qa.json',JSON.stringify({checks,errors,scope:'One-view modular motion browser/binding behavior, not art approval or universal rig detection.'},null,2)+'\n');console.log(JSON.stringify({checks:checks.length,errors}));
})().catch(e=>{console.error(e.stack);process.exit(1)});
