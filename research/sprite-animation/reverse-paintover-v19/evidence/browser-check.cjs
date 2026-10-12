const {chromium}=require('playwright');
const fs=require('fs');
const path=require('path');
const assert=require('assert');
(async()=>{
 const out=path.resolve('research/sprite-animation/reverse-paintover-v19/evidence');
 const report={scope:'Standalone inline research viewer controls and decoded embedded images; not game integration or artistic approval',file_navigation:'Unavailable: ERR_BLOCKED_BY_ADMINISTRATOR. Use supported inline page content with embedded local artifacts, no file URL access or policy changes.',checks:[],errors:[]};
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking']});
 try{
  const page=await browser.newPage({viewport:{width:1400,height:1050}});
  await page.route('http://**/*',r=>r.abort());await page.route('https://**/*',r=>r.abort());
  page.on('pageerror',e=>report.errors.push(String(e)));
  await page.setContent(fs.readFileSync(path.resolve('research/sprite-animation/reverse-paintover-v19/frame-review.html'),'utf8'));
  await page.waitForFunction(()=>window.REVIEW&&document.querySelectorAll('.bank').length===6);
  async function check(name,fn){await fn();report.checks.push(name)}
  await check('6 complete banks /8,8,16,6,6,13 exposures',async()=>assert.deepEqual(await page.evaluate(()=>REVIEW.DATA.map(b=>b.urls.length)),[8,8,16,6,6,13]));
  await check('57 embedded images decode',async()=>assert(await page.evaluate(async()=>{for(const b of REVIEW.DATA)for(const src of b.urls){const im=new Image();im.src=src;await im.decode();if(!im.naturalWidth)return false}return true})));
  await check('comparison canvases share the same top despite heading wrap',async()=>{const y=await page.locator('.bank img').evaluateAll(els=>els.slice(0,3).map(e=>e.getBoundingClientRect().y));assert(y.every(v=>Math.abs(v-y[0])<1))});
  const current=()=>page.locator('.bank').evaluateAll(els=>els.map(e=>Number(e.dataset.frame)));
  await check('native75ms /correct separate clocks',async()=>{await page.evaluate(()=>REVIEW.setTime(75));assert.deepEqual(await current(),[1,1,2,0,0,2])});
  await check('native600ms /RO seam without resetting Valyria or KingLucas',async()=>{await page.evaluate(()=>REVIEW.setTime(600));assert.deepEqual(await current(),[0,0,0,4,4,7])});
  await check('equal800ms phase control is explicit retiming',async()=>{await page.selectOption('#mode','equal');await page.evaluate(()=>REVIEW.setTime(200));assert.deepEqual(await current(),[2,2,4,1,1,3])});
  await check('step and scrub pause playback',async()=>{await page.selectOption('#mode','native');await page.locator('#phase').evaluate(e=>{e.value=4;e.dispatchEvent(new Event('input'))});assert.deepEqual((await current()).slice(0,3),[2,2,4]);assert.equal(await page.evaluate(()=>REVIEW.playing),false);await page.click('#next');assert.equal((await current())[2],5)});
  await check('previous wraps first sample to last phase',async()=>{await page.evaluate(()=>REVIEW.setTime(0));await page.click('#back');assert.deepEqual((await current()).slice(0,3),[7,7,15])});
  await check('play progresses and pause freezes',async()=>{await page.evaluate(()=>REVIEW.setTime(0));await page.click('#play');await page.waitForTimeout(160);assert.equal(await page.evaluate(()=>REVIEW.playing),true);await page.click('#play');const before=await current();await page.waitForTimeout(80);assert.deepEqual(await current(),before)});
  await page.evaluate(()=>REVIEW.setTime(0));await page.screenshot({path:path.join(out,'viewer-desktop.png'),fullPage:true});
  await check('mobile layout has no horizontal overflow',async()=>{await page.setViewportSize({width:390,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth))});
  await page.screenshot({path:path.join(out,'viewer-mobile.png'),fullPage:true});
  await check('no browser script errors',async()=>assert.deepEqual(report.errors,[]));
  report.passed=report.checks.length;fs.writeFileSync(path.join(out,'browser-report.json'),JSON.stringify(report,null,2)+'\n');
  console.log('BROWSER_CHECKS',report.passed);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
