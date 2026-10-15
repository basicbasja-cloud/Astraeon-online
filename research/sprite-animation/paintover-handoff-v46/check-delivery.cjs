// Offline viewer/clock/artifact verification. No provider or network calls.
const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/opt/codex/runtimes/cua/lib/node_modules/playwright');
const P=__dirname;
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1100,height:850}}), errors=[];let requests=0;
 await page.route('**/*',r=>{requests++;return r.abort()});page.on('pageerror',e=>errors.push(e.message));
 await page.setContent(fs.readFileSync(path.join(P,'review.html'),'utf8'),{waitUntil:'load'});
 await page.waitForFunction(()=>document.querySelector('#label').textContent.includes('Frame'));
 const checks={};checks.eight_views=await page.locator('#view option').count()===8;
 await page.locator('#play').click();checks.pause=await page.locator('#play').textContent()==='Play';
 for(const v of ['S','SE','E','NE','N','NW','W','SW']){
  await page.selectOption('#view',v);
  for(const k of [0,3,7]){
   await page.locator('#key').evaluate((el,k)=>{el.value=k;el.dispatchEvent(new Event('input'))},k);
   await page.waitForFunction(k=>document.querySelector('#label').textContent.startsWith(`Frame ${k+1}/8`),k);
  }
  checks[v+'_step']=true;
 }
 await page.locator('#grid').uncheck();checks.grid_toggle=!(await page.locator('#grid').isChecked());
 await page.locator('#grid').check();await page.selectOption('#view','W');
 await page.locator('#key').evaluate(el=>{el.value=3;el.dispatchEvent(new Event('input'))});
 await page.waitForFunction(()=>document.querySelector('#label').textContent.startsWith('Frame 4/8'));
 await page.screenshot({path:path.join(P,'handoff','review-browser.png')});
 checks.no_page_errors=errors.length===0;checks.no_external_requests=requests===0;
 const report={checks,pass:Object.values(checks).every(Boolean),errors,requests,production_pass:false,scope:'Offline UI controls/image decode only; not anatomy or visual quality'};
 fs.writeFileSync(path.join(P,'handoff','browser-qa.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report));await browser.close();if(!report.pass)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
