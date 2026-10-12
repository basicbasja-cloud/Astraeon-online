/* Browser QA on the standalone review tool, no game/branch character assets. */
const {chromium}=require('playwright');
const fs=require('fs'),path=require('path'),assert=require('assert');
async function main(){
 const root=path.resolve('research/sprite-animation/quality-review-v10'),out=path.join(root,'browser-check');fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage({viewport:{width:1200,height:1000}}),errors=[],checks=[];
 page.on('pageerror',e=>errors.push(e.message));
 async function check(name,fn){await fn();checks.push({name,passed:true})}
 try{
  // Managed browser blocks file navigation; render this self-contained local document directly.
  const html=fs.readFileSync(path.join(root,'leg-review.html'),'utf8');
  await page.setContent(html);await page.waitForFunction(()=>window.legReview&&images.every(x=>x.complete&&x.naturalWidth>0));
  await check('four actual source-key frames loaded',async()=>assert.equal(await page.evaluate(()=>legReview.data.frames.length),4));
  await check('master canvas stays 512-square',async()=>assert.deepEqual(await page.locator('canvas').evaluate(c=>[c.width,c.height]),[512,512]));
  await check('review status is not approval',async()=>assert.match(await page.locator('#status').textContent(),/REVIEW_REQUIRED/));
  await check('next and previous frame controls',async()=>{await page.click('#next');assert.equal(await page.evaluate(()=>legReview.key),1);await page.click('#prev');assert.equal(await page.evaluate(()=>legReview.key),0)});
  await check('keyboard navigation',async()=>{await page.locator('h1').click();await page.keyboard.press('ArrowRight');assert.equal(await page.evaluate(()=>legReview.key),1)});
  await check('slider can inspect loop seam',async()=>{await page.locator('#frame').fill('3');assert.equal(await page.evaluate(()=>legReview.key),3);assert.match(await page.locator('#report').textContent(),/"includes_loop_seam": true/)});
  await check('quarter-speed uses source intervals',async()=>{await page.selectOption('#speed','.25').catch(()=>page.selectOption('#speed','0.25'));await page.click('#play');await page.waitForTimeout(450);assert.equal(await page.evaluate(()=>legReview.key),3);await page.waitForTimeout(1050);assert.equal(await page.evaluate(()=>legReview.key),0);await page.click('#play')});
  await check('onion skin and source overlay toggle',async()=>{await page.check('#onion');await page.uncheck('#source');assert(await page.isChecked('#onion'));await page.check('#source')});
  await check('pointer maps screen to master pixels',async()=>{
   await page.click('#knee_r');await page.selectOption('#visibility','estimated');const b=await page.locator('canvas').boundingBox();
   await page.locator('canvas').click({position:{x:b.width*210/512,y:b.height*350/512}});
   const p=await page.evaluate(()=>legReview.data.frames[0].points.knee_r);assert(Math.abs(p.xy[0]-210)<=1&&Math.abs(p.xy[1]-350)<=1);assert.equal(p.visibility,'estimated')
  });
  await check('uncertainty edit persists',async()=>{await page.locator('#uncertainty').fill('12');await page.locator('#notes').focus();assert.equal(await page.evaluate(()=>legReview.data.frames[0].points.knee_r.uncertainty_px),12)});
  await check('point edits invalidate the old report',async()=>{assert(await page.evaluate(()=>legReview.dirty));assert.match(await page.locator('#report').textContent(),/พักไว้/)});
  await check('text-field arrows do not navigate frames',async()=>{await page.locator('#notes').fill('manual review');await page.keyboard.press('ArrowRight');assert.equal(await page.evaluate(()=>legReview.key),0)});
  await check('export includes actual edited coordinates',async()=>{const downloadPromise=page.waitForEvent('download');await page.click('#export');const download=await downloadPromise;await download.saveAs(path.join(out,'export-control.json'));const c=JSON.parse(fs.readFileSync(path.join(out,'export-control.json')));assert.equal(c.frames[0].points.knee_r.uncertainty_px,12)});
  await check('clear marks unknown instead of guessing',async()=>{await page.click('#clear');const p=await page.evaluate(()=>legReview.data.frames[0].points.knee_r);assert.equal(p.xy,null);assert.equal(p.visibility,'unknown')});
  const original=fs.readFileSync(path.join(root,'leg-annotations.json'));
  await check('annotation import round trip',async()=>{await page.locator('#import').setInputFiles({name:'original.json',mimeType:'application/json',buffer:original});await page.waitForFunction(()=>legReview.data.frames[0].points.knee_r.xy!==null);assert.equal(await page.evaluate(()=>legReview.data.frames[0].points.knee_r.uncertainty_px),8)});
  await check('import rejects altered source bones',async()=>{const c=JSON.parse(original);c.frames[0].reference.knee_r[0]+=1;await page.locator('#import').setInputFiles({name:'bad-bones.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(c))});await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('โหลดไม่ได้'));assert.match(await page.locator('#status').textContent(),/ต้นแบบ/)});
  await check('import rejects altered pose time',async()=>{const c=JSON.parse(original);c.frames[0].time_seconds+=.01;await page.locator('#import').setInputFiles({name:'bad-time.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(c))});await page.waitForFunction(()=>document.querySelector('#status').textContent.includes('โหลดไม่ได้'));assert.match(await page.locator('#status').textContent(),/เวลา/)});
  // Reset all edits for screenshots of the actual reviewed case.
  await page.goto('about:blank');await page.setContent(html);await page.waitForFunction(()=>window.legReview&&images.every(x=>x.complete&&x.naturalWidth>0));await page.locator('#frame').fill('2');
  await page.screenshot({path:path.join(out,'desktop.png'),fullPage:true});
  await check('mobile has no horizontal overflow',async()=>{await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2))});
  await check('mobile frame control works',async()=>{await page.click('#next');assert.equal(await page.evaluate(()=>legReview.key),3)});
  await page.screenshot({path:path.join(out,'mobile.png'),fullPage:true});
  await check('no runtime JS errors including reload and mobile',async()=>assert.deepEqual(errors,[]));
  fs.writeFileSync(path.join(out,'browser-report.json'),JSON.stringify({browser:await browser.version(),checked_page:'leg-review.html',load_method:'Self-contained local markup via setContent; managed browser blocks file navigation',checks,total:checks.length,errors,scope:'Standalone anatomical review UI only; not game integration or artwork acceptance'},null,2)+'\n');
  console.log('LEG_UI_CHECK',checks.length,'passed');
 }finally{await browser.close()}
}
main().catch(e=>{console.error(e);process.exit(1)});
