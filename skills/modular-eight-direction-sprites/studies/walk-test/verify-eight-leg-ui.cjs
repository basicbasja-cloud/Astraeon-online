/* Actual standalone eight-facing image review UI, no rejected game assets. */
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),assert=require('assert');
async function main(){
 const root=path.resolve('research/sprite-animation/eight-direction-v11'),out=path.join(root,'browser-check');fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage({viewport:{width:1200,height:1100}}),errors=[],checks=[];
 page.on('pageerror',e=>errors.push(e.message));
 async function check(name,fn){await fn();checks.push({name,passed:true})}
 async function load(v){await page.goto('about:blank');await page.setContent(fs.readFileSync(path.join(root,'master',v,'leg-review.html'),'utf8'));await page.waitForFunction(()=>window.legReview&&images.every(x=>x.complete&&x.naturalWidth===512)&&ownerImages.every(x=>x&&x.complete&&x.naturalWidth===512))}
 async function upload(c){await page.locator('#import').setInputFiles({name:'control.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(c))});await page.waitForTimeout(80)}
 try{
  for(const v of ['S','SE','E','NE','N','NW','W','SW'])await check(v+' loads four actual art and source-owner images with matching facing',async()=>{await load(v);assert.equal(await page.evaluate(()=>legReview.data.facing),v);assert.match(await page.locator('#facing').textContent(),new RegExp(v));assert.equal(await page.evaluate(()=>legReview.data.frames.length),4);assert.equal(await page.locator('#status').textContent(),v==='NE'?'REJECTED':'REVIEW_REQUIRED')});
  await load('SE');const original=JSON.parse(fs.readFileSync(path.join(root,'master/SE/leg-annotations.json')));
  await check('two separate 512-square art and owner canvases',async()=>{for(const id of ['canvas','ownerCanvas'])assert.deepEqual(await page.locator('#'+id).evaluate(c=>[c.width,c.height]),[512,512])});
  await check('next/previous controls select actual source poses',async()=>{await page.click('#next');assert.equal(await page.evaluate(()=>legReview.key),1);assert.match(await page.locator('#position').textContent(),/source 10/);await page.click('#prev');assert.equal(await page.evaluate(()=>legReview.key),0)});
  await check('quarter-speed and loop seam follow source clock',async()=>{await page.locator('#frame').fill('3');await page.selectOption('#speed','0.25');await page.click('#play');await page.waitForTimeout(500);assert.equal(await page.evaluate(()=>legReview.key),3);await page.waitForTimeout(950);assert.equal(await page.evaluate(()=>legReview.key),0);await page.click('#play')});
  await page.locator('#frame').fill('1');
  await check('new pose 2 has independently marked pixel trace evidence',async()=>{assert.match(await page.locator('#report').textContent(),/reviewed_match/);assert(await page.isChecked('#traceConfirmed'));assert.equal(await page.evaluate(()=>legReview.data.frames[1].occlusion_reviews[0].observed_foreground),'r')});
  await check('clicking a new trace point invalidates trace confirmation and report',async()=>{await page.click('#clearTrace');await page.selectOption('#mode','trace');const b=await page.locator('#canvas').boundingBox();for(const [x,y] of [[248,319],[275,343],[217,351]])await page.locator('#canvas').click({position:{x:b.width*x/512,y:b.height*y/512}});assert.equal(await page.evaluate(()=>legReview.data.frames[1].occlusion_reviews[0].art_trace.length),3);assert.equal(await page.evaluate(()=>legReview.data.frames[1].occlusion_reviews[0].trace_review),'unconfirmed');assert(await page.evaluate(()=>legReview.dirty));assert.match(await page.locator('#report').textContent(),/พักไว้/)});
  await check('actual image crossing pointer uses master coordinates',async()=>{await page.selectOption('#mode','crossing');const b=await page.locator('#canvas').boundingBox();await page.locator('#canvas').click({position:{x:b.width*275/512,y:b.height*346/512}});const xy=await page.evaluate(()=>legReview.data.frames[1].occlusion_reviews[0].art_xy);assert(Math.abs(xy[0]-275)<=1&&Math.abs(xy[1]-346)<=1)});
  await check('foreground and trace confirmation are separate',async()=>{await page.selectOption('#foreground','unknown');await page.check('#traceConfirmed');assert.equal(await page.evaluate(()=>legReview.data.frames[1].occlusion_reviews[0].observed_foreground),'unknown');assert.equal(await page.evaluate(()=>legReview.data.frames[1].occlusion_reviews[0].trace_review),'confirmed')});
  await check('flagging visible error binds it to displayed frame bytes',async()=>{await page.click('#flagError');const issue=await page.evaluate(()=>legReview.data.frames[1].review_issues.at(-1));assert(issue.confirmed);assert.equal(issue.image_sha256,original.frames[1].image_sha256)});
  await check('import cannot erase a confirmed visible error',async()=>{await upload(original);assert.equal(await page.evaluate(()=>legReview.data.frames[1].review_issues.length),1)});
  await check('import/export retains visible image error and trace',async()=>{const wait=page.waitForEvent('download');await page.click('#export');const d=await wait;await d.saveAs('/tmp/astraeon-v11-browser-export.json');const c=JSON.parse(fs.readFileSync('/tmp/astraeon-v11-browser-export.json'));assert.equal(c.frames[1].review_issues.length,1);assert(c.frames[1].occlusion_reviews[0].art_trace.length>=3);await upload(c);assert.equal(await page.evaluate(()=>legReview.data.frames[1].review_issues.length),1)});
  for(const [name,change] of [
   ['deleted required source crossing',c=>c.frames[1].occlusion_reviews=[]],
   ['relabelled source foreground',c=>c.frames[1].occlusion_reviews[0].expected_foreground='l'],
   ['modified source skeleton',c=>c.frames[1].reference.knee_r[0]+=1],
   ['modified source time',c=>c.frames[1].time_seconds+=.01],
   ['different facing',c=>c.facing='SW'],
   ['different image bytes',c=>c.frames[1].image_sha256='0'.repeat(64)],
   ['invalid out-of-frame trace',c=>c.frames[1].occlusion_reviews[0].art_trace.push([999,999])],
   ['error bound to other image',c=>c.frames[1].review_issues=[{code:'control',confirmed:true,image_sha256:'0'.repeat(64)}]]
  ])await check('import rejects '+name,async()=>{const c=structuredClone(original);change(c);await upload(c);assert.match(await page.locator('#status').textContent(),/โหลดไม่ได้/)});
  await load('SE');await page.locator('#frame').fill('1');await page.screenshot({path:path.join(out,'SE-pose-2-desktop.png'),fullPage:true});
  await check('mobile has no horizontal overflow',async()=>{await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2))});
  await check('mobile frame controls work',async()=>{await page.click('#next');assert.equal(await page.evaluate(()=>legReview.key),2)});
  await page.screenshot({path:path.join(out,'SE-mobile.png'),fullPage:true});
  await load('NE');await page.locator('#frame').fill('1');await page.screenshot({path:path.join(out,'NE-rejected-mobile.png'),fullPage:true});
  await check('new wrong attachment frame remains rejected in its actual image report',async()=>assert.match(await page.locator('#report').textContent(),/teal_cloth_changes_anatomical_attachment_side/));
  await check('no JavaScript runtime errors',async()=>assert.deepEqual(errors,[]));
  fs.writeFileSync(path.join(out,'browser-report.json'),JSON.stringify({browser:await browser.version(),checks,total:checks.length,errors,load_method:'Self-contained actual local HTML via setContent; managed browser blocks file navigation',scope:'Review controls and hash-bound image annotations; not semantic-model accuracy or art acceptance'},null,2)+'\n');console.log('EIGHT_LEG_UI',checks.length,'passed');
 }finally{await browser.close()}
}
main().catch(e=>{console.error(e);process.exit(1)});
