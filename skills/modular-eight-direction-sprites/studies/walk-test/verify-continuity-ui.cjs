const fs=require('fs'),path=require('path'),assert=require('assert');
const {chromium}=require('playwright');
(async()=>{
 const root=path.resolve(__dirname,'../../../..'),out=path.join(root,'research/sprite-animation/continuity-v14/browser-check');fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1480,height:1000}});let errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.setContent(fs.readFileSync(path.join(root,'research/sprite-animation/continuity-v14/frame-review.html'),'utf8'),{waitUntil:'load'});
 const checks=[];function check(name,ok){assert(ok,name);checks.push({name,passed:true})}
 check('five real image comparisons',await page.locator('#panels img').count()===5);
 check('eight character slots',await page.locator('#phase').getAttribute('max')==='7');
 const hashes=[];
 for(let i=0;i<8;i++){
  await page.locator('#phase').evaluate((el,n)=>{el.value=n;el.dispatchEvent(new Event('input'))},i);
  await page.waitForFunction(()=>Array.from(document.querySelectorAll('#panels img')).every(i=>i.complete&&i.naturalWidth>0));
  check(`slot ${i+1} source time label`,(await page.locator('#position').textContent()).includes('source '+i*5));
  const actual=await page.locator('[data-kind="after"] img').getAttribute('src');
  const expected=fs.readFileSync(path.join(root,`research/sprite-animation/continuity-v14/attempts/geometry-first/frames/${String(i).padStart(2,'0')}.png`)).toString('base64');
  check(`slot ${i+1} actual new RGBA bound`,actual==='data:image/png;base64,'+expected);hashes.push(actual);
 }
 check('eight distinct candidate files',new Set(hashes).size===8);
 await page.screenshot({path:path.join(out,'frame8-desktop.png'),fullPage:true});
 await page.locator('#next').click();check('last-to-first transition',await page.locator('#phase').inputValue()==='0');
 await page.locator('#reference').selectOption('king');check('all sixteen native King frames accessible',await page.locator('#nativePhase').getAttribute('max')==='15');
 for(let i=0;i<16;i++){
  await page.locator('#nativePhase').evaluate((el,n)=>{el.value=n;el.dispatchEvent(new Event('input'))},i);
  await page.waitForFunction(()=>document.querySelector('#native').complete&&document.querySelector('#native').naturalWidth>0);
  const actual=await page.locator('#native').getAttribute('src');const expected=fs.readFileSync(path.join(root,`research/sprite-animation/motion-reference-v6/other-games/king-lucas-walk-2/${String(i).padStart(4,'0')}.png`)).toString('base64');
  check(`native King ${i} exact original capture`,actual==='data:image/png;base64,'+expected);
 }
 await page.locator('#reference').selectOption('ro');check('all eight native RO frames accessible',await page.locator('#nativePhase').getAttribute('max')==='7');
 check('separate source and review clocks',await page.locator('#clock option').count()===3);
 await page.locator('#play').click();await page.waitForTimeout(190);check('actual playback advances',await page.locator('#phase').inputValue()!=='0');await page.locator('#play').click();
 check('approval scopes visible',(await page.locator('body').textContent()).includes('ไม่โอนคำอนุมัติเดิม'));
 await page.locator('#phase').evaluate(el=>{el.value=3;el.dispatchEvent(new Event('input'))});
 check('actual unresolved source-spacing warning remains visible',(await page.locator('#notes').textContent()).includes('เครื่องมือเตือน'));
 await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(out,'mobile.png'),fullPage:true});
 check('mobile no horizontal overflow',await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth));
 check('no JavaScript errors',errors.length===0);
 fs.writeFileSync(path.join(out,'browser-report.json'),JSON.stringify({checks,count:checks.length,errors,scope:'Offline actual UI/pixel-binding test, not game integration or art acceptance'},null,2)+'\n');
 console.log('CONTINUITY_UI',checks.length,'checks passed');await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
