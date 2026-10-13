const fs=require('fs'),path=require('path');
let playwright;try{playwright=require(process.env.PLAYWRIGHT_MODULE_PATH||'playwright')}catch(e){playwright=require('/opt/codex/runtimes/cua/lib/node_modules/playwright')}
const {chromium}=playwright;
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_EXECUTABLE||'/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking']});
 const page=await browser.newPage();const checks=[];const errors=[];page.on('pageerror',e=>errors.push(e.message));
 function check(name,ok){checks.push({name,pass:!!ok});if(!ok)throw Error(name)}
 try{
  await page.goto('http://127.0.0.1:8744/reference-reader.html');await page.locator('#frame').evaluate(im=>im.decode());
  check('real_frame_decodes',await page.locator('#frame').evaluate(im=>im.naturalWidth===600&&im.naturalHeight===338));
  check('no_svg',await page.locator('svg').count()===0);
  check('745_source_exposures_available',await page.evaluate(()=>referenceReader.data.reduce((n,c)=>n+c.frames.length,0)===745));
  await page.click('#next');check('step_forward_keeps_native_pts',await page.evaluate(()=>referenceReader.state.index===1&&referenceReader.data[0].frames[1].source_pts_ms===40));
  await page.click('#prev');check('step_backward',await page.evaluate(()=>referenceReader.state.index===0));
  await page.evaluate(()=>referenceReader.advance(79));check('exposure_boundary_before',await page.evaluate(()=>referenceReader.state.index===1));
  await page.evaluate(()=>referenceReader.advance(80));check('exposure_boundary_at',await page.evaluate(()=>referenceReader.state.index===2));
  await page.selectOption('#capture','2');check('capture_switch_resets_index',await page.evaluate(()=>referenceReader.state.source===2&&referenceReader.state.index===0));
  await page.evaluate(()=>referenceReader.advance(10001));check('finite_clip_terminal_hold_no_loop',await page.evaluate(()=>referenceReader.state.index===244&&!referenceReader.state.running));
  await page.click('#prev');check('last_frame_backward',await page.evaluate(()=>referenceReader.state.index===243));
  check('unknown_review_not_promoted',await page.locator('#meta').textContent().then(t=>t.includes('pending')));
  check('no_javascript_errors',errors.length===0);
 }finally{
  await browser.close();fs.writeFileSync(path.join(__dirname,'browser-review.json'),JSON.stringify({checks,errors,scope:'Native capture viewer decoding/order/exposure boundaries/finite terminal state only; no anatomy or motion-art approval.'},null,2)+'\n');
 }
 console.log(JSON.stringify({checks:checks.length,all_pass:checks.every(c=>c.pass)}));
})().catch(e=>{console.error(e.message);process.exit(1)});
