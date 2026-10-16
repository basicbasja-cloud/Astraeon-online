const fs=require('fs'),path=require('path');
const {chromium}=require('/opt/codex/runtimes/cua/lib/node_modules/playwright');
(async()=>{
 const root=__dirname,work=path.resolve(root,'../../../work/v60-browser');fs.mkdirSync(work,{recursive:true});
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
 const results=[];
 for(const name of ['original','reverse-recovery','accepted-control','old-head','corrected-head']){
  const page=await browser.newPage({viewport:{width:1000,height:800}}),errors=[],requests=[];
  page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',r=>{requests.push(r.request().url());r.abort()});
  await page.setContent(fs.readFileSync(path.join(root,name+'-review/review.html'),'utf8'));
  await page.waitForFunction(()=>window.READY||window.LOAD_ERROR);if(await page.evaluate(()=>window.LOAD_ERROR))throw Error('load failed');
  const boundaries=await page.evaluate(()=>{let t=0,r=[];for(let i=0;i<review.durations.length;i++){r.push(review.at(t)===i,review.at(t+review.durations[i]-0.01)===i);t+=review.durations[i];}r.push(review.at(t)===0,review.at(-1)===review.durations.length-1);return r;});
  if(!boundaries.every(Boolean))throw Error('clock boundary');
  const dir=path.join(work,name);fs.mkdirSync(dir,{recursive:true});
  for(let i=0;i<16;i++){
   const url=await page.evaluate(i=>{review.select(i);return review.ctx.canvas.toDataURL('image/png')},i);
   fs.writeFileSync(path.join(dir,String(i).padStart(2,'0')+'.png'),Buffer.from(url.split(',')[1],'base64'));
  }
  await page.evaluate(()=>review.select(0));await page.click('#play');await page.waitForTimeout(260);
  if(!await page.evaluate(()=>review.playing&&review.index>0))throw Error('no actual playback');
  await page.click('#play');const paused=await page.evaluate(()=>review.index);await page.waitForTimeout(180);
  if(await page.evaluate(()=>review.index)!==paused)throw Error('pause drift');
  await page.selectOption('#rate','0.25');await page.evaluate(()=>review.select(0));await page.click('#play');await page.waitForTimeout(500);
  if(!await page.evaluate(()=>review.playing&&review.index>=1&&review.index<=2))throw Error('quarter rate');
  await page.evaluate(()=>review.select(7));if(await page.evaluate(()=>review.playing))throw Error('seek did not stop');
  await page.check('#onion');await page.check('#floor');await page.uncheck('#onion');await page.uncheck('#floor');
  await page.screenshot({path:path.join(root,name+'-review/browser.png'),fullPage:true});
  if(errors.length||requests.length)throw Error(JSON.stringify({errors,requests}));
  results.push({name,boundary_checks:boundaries.length,actual_png_exports:16,actual_play_pause_quarter_seek:true,overlay_controls:true,page_errors:errors,network_requests:requests});
  await page.close();
 }
 await browser.close();fs.writeFileSync(path.join(root,'browser-review.json'),JSON.stringify({pass:true,clips:results,production_pass:false},null,2)+'\n');
 console.log('Actual five-player/80-frame/clock/playback/overlay browser checks PASS');
})().catch(e=>{console.error(e.stack);process.exit(1)});
