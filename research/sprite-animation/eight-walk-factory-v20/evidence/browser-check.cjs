const {chromium}=require('playwright');const fs=require('fs');const path=require('path');const assert=require('assert');
(async()=>{
 const out=path.resolve('research/sprite-animation/eight-walk-factory-v20/evidence');
 const report={scope:'Inline standalone motion QA viewer, raster canvases and controls; not game-engine integration, anatomical acceptance or measured runtime cadence',checks:[],errors:[]};
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking']});
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1100}});page.on('pageerror',e=>report.errors.push(String(e)));
  await page.route('http://**/*',r=>r.abort());await page.route('https://**/*',r=>r.abort());
  await page.setContent(fs.readFileSync(path.resolve('research/sprite-animation/eight-walk-factory-v20/motion-review.html'),'utf8'));
  await page.waitForFunction(()=>window.QA&&QA.DATA.length===8);
  const check=async(n,f)=>{await f();report.checks.push(n)};
  await check('eight authored directions in fixed order',async()=>assert.deepEqual(await page.evaluate(()=>QA.DATA.map(b=>b.facing)),['S','SE','E','NE','N','NW','W','SW']));
  await check('64 art and192 reference images decode',async()=>assert(await page.evaluate(async()=>{for(const b of QA.DATA)for(const bank of ['art','owner','cutaway','RO']){if(b[bank].length!==8)return false;for(const src of b[bank]){const im=new Image();im.src=src;await im.decode();if(!im.naturalWidth)return false}}return true})));
  const state=()=>page.locator('#grid .card').evaluateAll(els=>els.map(e=>Number(e.dataset.frame)));
  await check('600ms frame boundary75ms shared across directions',async()=>{await page.evaluate(()=>QA.setTime(75));assert.deepEqual(await state(),Array(8).fill(1))});
  await check('last sample is retained and600ms wraps',async()=>{await page.evaluate(()=>QA.setTime(599));assert.deepEqual(await state(),Array(8).fill(7));await page.evaluate(()=>QA.setTime(600));assert.deepEqual(await state(),Array(8).fill(0))});
  await check('direction change preserves current phase',async()=>{await page.evaluate(()=>QA.setTime(300));await page.selectOption('#facing','N');assert.equal(await page.evaluate(()=>QA.frame),4);assert.deepEqual(await state(),Array(8).fill(4))});
  await check('800ms control preserves selected frame',async()=>{await page.selectOption('#clock','800');assert.equal(await page.evaluate(()=>QA.frame),4);await page.evaluate(()=>QA.setTime(799));assert.equal(await page.evaluate(()=>QA.frame),7)});
  await check('previous wraps frame1 to8',async()=>{await page.evaluate(()=>QA.setTime(0));await page.click('#prev');assert.equal(await page.evaluate(()=>QA.frame),7)});
  await check('next wraps8to1',async()=>{await page.click('#next');assert.equal(await page.evaluate(()=>QA.frame),0)});
  await check('scrub pauses and chooses exact frame',async()=>{await page.locator('#phase').evaluate(e=>{e.value=3;e.dispatchEvent(new Event('input'))});assert.equal(await page.evaluate(()=>QA.frame),3);assert.equal(await page.evaluate(()=>QA.playing),false)});
  await check('stable-head front view still displaysREJECTED',async()=>{await page.selectOption('#facing','S');assert((await page.locator('#blockers').innerText()).includes('confirmed_actual_image_issue'))});
  await check('W shows residual vertical warning',async()=>{await page.selectOption('#facing','W');assert((await page.locator('#blockers').innerText()).includes('visible_surface_bounce'));assert((await page.locator('#metrics').innerText()).includes('16.21'))});
  await check('bone overlay and surface toggles retain phase',async()=>{await page.check('#bones');await page.uncheck('#surface');assert.equal(await page.evaluate(()=>QA.frame),3);await page.check('#surface')});
  await check('all four selected-detail canvases drawn',async()=>assert(await page.locator('#detail canvas').evaluateAll(cs=>cs.every(c=>{const a=c.getContext('2d').getImageData(0,0,512,512).data;let n=0;for(let i=3;i<a.length;i+=4)if(a[i]>128)n++;return n>1000}))))
  await check('play and pause behave',async()=>{await page.click('#play');await page.waitForTimeout(180);assert.equal(await page.evaluate(()=>QA.playing),true);await page.click('#play');const before=await state();await page.waitForTimeout(80);assert.deepEqual(await state(),before)});
  await page.selectOption('#clock','600');await page.evaluate(()=>QA.setTime(0));await page.screenshot({path:path.join(out,'viewer-desktop.png'),fullPage:true});
  await check('mobile has no horizontal overflow',async()=>{await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth))});
  await page.screenshot({path:path.join(out,'viewer-mobile.png'),fullPage:true});
  await check('no script errors orSVGdependencies',async()=>{assert.deepEqual(report.errors,[]);assert.equal(await page.locator('svg').count(),0)});
  report.passed=report.checks.length;fs.writeFileSync(path.join(out,'browser-report.json'),JSON.stringify(report,null,2)+'\n');console.log('MOTION_BROWSER_CHECKS',report.passed);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
