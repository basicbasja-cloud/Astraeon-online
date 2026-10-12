const fs=require('fs'),path=require('path'),{chromium}=require('playwright');
const root=path.resolve(__dirname,'../../../..'),out=path.join(root,'research/sprite-animation/leg-ownership-v16');
const uri=p=>'data:image/png;base64,'+fs.readFileSync(p).toString('base64');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1440,height:1100}}),errors=[],checks=[];
 page.on('pageerror',e=>errors.push(String(e)));
 const check=(name,passed)=>{checks.push({name,passed:!!passed});if(!passed)throw Error(name)};
 await page.setContent(fs.readFileSync(path.join(out,'frame-review.html'),'utf8'));
 check('uniform800ms default clock',await page.locator('#clock').inputValue()==='800');
 const source=JSON.parse(fs.readFileSync(path.join(root,'research/sprite-animation/ground-walk-sixteen-v15/source/source-ground.json')));
 for(let i=0;i<16;i++){
  await page.locator('#phase').evaluate((el,i)=>{el.value=i;el.dispatchEvent(new Event('input'))},i);
  check('fractional phase '+i,(await page.locator('#label').textContent()).includes('source sample '+i*2.5));
  check('exact new pixels '+i,await page.locator('#new').getAttribute('src')===uri(path.join(out,'attempt3/frames',String(i).padStart(2,'0')+'.png')));
  check('actual source owner render '+i,await page.locator('#source').getAttribute('src')===uri(path.join(root,source.frames[i].cutaway_path)));
  check('scoped rejection status '+i,(await page.locator('#status').textContent()).includes('REJECTED_SEQUENCE_MEMBER')===(i>=8&&i<=10));
 }
 await page.locator('#next').click();check('16to1 seam',(await page.locator('#phase').inputValue())==='0');
 await page.locator('#attempt').selectOption('attempt2');check('failed attempt available',await page.locator('#new').getAttribute('src')===uri(path.join(out,'candidate/frames/00.png')));
 await page.locator('#attempt').selectOption('attempt3');check('unknown contacts block acceptance',(await page.locator('#blockers').textContent()).includes('unknown_visible_contact_samples'));
 await page.locator('#phase').evaluate(el=>{el.value=12;el.dispatchEvent(new Event('input'))});check('12to13 surface warning visible',(await page.locator('#status').textContent()).includes('surface-step warning'));
 await page.locator('#cutaway').uncheck();check('dressed source switch',await page.locator('#source').getAttribute('src')===uri(path.join(root,source.frames[12].dressed_path)));
 for(const clock of ['600','1333','2400','800']){await page.locator('#clock').selectOption(clock);check('clock '+clock,await page.locator('#clock').inputValue()===clock)}
 await page.locator('#phase').evaluate(el=>{el.value=0;el.dispatchEvent(new Event('input'))});await page.locator('#play').click();await page.waitForTimeout(160);check('actual playback advances',await page.locator('#phase').inputValue()!=='0');await page.locator('#play').click();
 fs.mkdirSync(path.join(out,'browser-check'),{recursive:true});await page.screenshot({path:path.join(out,'browser-check/desktop.png'),fullPage:true});
 await page.setViewportSize({width:390,height:844});check('mobile no horizontal overflow',await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(out,'browser-check/mobile.png'),fullPage:true});check('no JS errors',errors.length===0);
 fs.writeFileSync(path.join(out,'browser-check/browser-report.json'),JSON.stringify({count:checks.length,checks,errors,scope:'Actual UI/pixels/source/time/rejection/warnings only; no anatomical acceptance or game integration'},null,2)+'\n');await browser.close();console.log('STANDARD_BROWSER_CHECKS',checks.length);
})().catch(e=>{console.error(e);process.exit(1)});
