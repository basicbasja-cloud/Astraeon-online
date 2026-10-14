const fs=require('fs'),assert=require('assert'),crypto=require('crypto');
const {chromium}=require('/opt/codex/runtimes/cua/lib/node_modules/playwright');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage({viewport:{width:1150,height:1000}}),errors=[],checks=[];
 const check=(name,ok)=>{assert(ok,name);checks.push({name,pass:true})};
 page.on('pageerror',e=>errors.push(e.message));await page.route('**/*',r=>r.abort());
 await page.setContent(fs.readFileSync(__dirname+'/approved-gif-review.html','utf8'));await page.waitForFunction(()=>review.ready);
 check('three real384x512 canvases',await page.locator('canvas').count()===3);
 check('approved source/game clocks come from decoded GIFs',await page.evaluate(()=>JSON.stringify(review.data.reference.map(r=>r.frames.map(f=>f.duration_ms)))==='[[190,180,190,180,190,180,190,600],[100,100,100,100,100,100,100,600]]'));
 check('all eight current normalized image file bindings',await page.evaluate(()=>review.data.candidate_frames).then(rows=>rows.every(r=>sha(fs.readFileSync(__dirname+'/../../../'+r.path))===r.sha256)));
 const reproduction=await page.evaluate(()=>{
   const same=(canvas,im)=>{const c=document.createElement('canvas');c.width=384;c.height=512;const x=c.getContext('2d');x.drawImage(im,0,0,384,512);const a=canvas.getContext('2d').getImageData(0,0,384,512).data,b=x.getImageData(0,0,384,512).data;return a.every((v,i)=>v===b[i])};
   let candidate=true,approved=true,source=true;
   for(let i=0;i<8;i++){review.select(i);candidate&&=same(document.querySelector('#candidate'),images[review.data.candidate_frames[i].path]);approved&&=same(document.querySelector('#approved'),images[review.data.reference[0].frames[i].decoded_path]);source&&=same(document.querySelector('#source'),images[sourcePath(i)])}
   return {candidate,approved,source};
 });
 for(const [k,v] of Object.entries(reproduction))check(k+' actual eight exposed images reproduced without extra transforms',v);
 await page.locator('#frame').fill('3');check('one slider controls all three images',await page.evaluate(()=>review.index===3&&!review.running));
 const pixelHash=selector=>page.locator(selector).screenshot().then(sha);
 const before=await pixelHash('#candidate');await page.locator('#grid').check();check('visible grid changes actual canvas',before!==await pixelHash('#candidate'));await page.locator('#grid').uncheck();
 const paintedBefore=await pixelHash('#candidate'),sourceBefore=await pixelHash('#source');await page.locator('#bones').check();
 check('source bone overlay changes real source panel',sourceBefore!==await pixelHash('#source'));
 check('source joints never masquerade as painted observations',paintedBefore===await pixelHash('#candidate'));await page.locator('#bones').uncheck();
 await page.locator('#surfaces').check();check('measured boot surfaces overlay changes actual painting',paintedBefore!==await pixelHash('#candidate'));await page.locator('#surfaces').uncheck();
 await page.locator('#candidate').click({position:{x:100,y:200}});
 check('clicked landmark is SHA-bound to current actual frame',await page.evaluate(()=>{const q=review.exportData();return q.observations[3].visible_neck_receiver.image_sha256===review.data.candidate_frames[3].sha256&&q.observations[3].visible_neck_receiver.xy[0]>115&&q.observations[3].visible_neck_receiver.xy[0]<125}));
 await page.locator('#landmark').selectOption('right_picking_glove');await page.locator('#unknown').click();
 check('occluded glove explicitly exports null rather than guessing',await page.evaluate(()=>review.exportData().observations[3].right_picking_glove.xy===null));
 await page.locator('#clock').selectOption('game');check('clock change resets shared frame and stops play',await page.evaluate(()=>review.index===0&&!review.running&&review.clock==='game'));
 await page.clock.install();await page.locator('#play').click();await page.clock.runFor(450);check('game exposure4 reached at450ms',await page.evaluate(()=>review.index===4&&review.running));
 await page.clock.runFor(900);check('game ends after true1300ms total',await page.evaluate(()=>review.index===7&&!review.running));
 await page.locator('#clock').selectOption('source');await page.locator('#play').click();await page.clock.runFor(600);check('source exposure3 reached at600ms',await page.evaluate(()=>review.index===3&&review.running));
 await page.clock.runFor(1350);check('source ends after true1900ms total',await page.evaluate(()=>review.index===7&&!review.running));
 check('actual current raster failure cannot become art approval',await page.evaluate(()=>!review.data.floor_qa.surface_checks_pass&&review.data.floor_qa.raster.tracks.near.range_display_px[0]===10&&review.data.floor_qa.raster.tracks.far.range_display_px[0]===25));
 check('first neutral399px match is only a calibration',await page.evaluate(()=>review.allData.size_qa.neutral_comparison[0].observed_height_px===399&&review.allData.size_qa.neutral_comparison[0].role==='calibration'));
 check('held-out terminal neutral is420px and clipped, not approved',await page.evaluate(()=>review.allData.size_qa.neutral_comparison[1].observed_height_px===420&&!review.allData.size_qa.neutral_comparison[1].raw_complete_silhouette&&!review.allData.size_qa.character_size_pass));
 check('whole-height matching does not silently approve head/body family',await page.evaluate(()=>!review.allData.size_qa.checks.head_body_family_review_bound));
 check('18part requirements keep new art blocked',await page.evaluate(()=>review.allData.parts.required_metrics.length===18&&!review.allData.parts.part_proportion_pass&&!review.allData.size_qa.checks.part_dimensions_and_ratios));
 check('same-view boot growth remains FAIL',await page.evaluate(()=>review.allData.parts.comparisons.some(r=>r.frames.join(',')==='candidate0,candidate7'&&r.metric==='boot_length'&&r.status==='FAIL')));
 await page.evaluate(()=>review.select(0));const noPartCandidate=await pixelHash('#candidate'),noPartApproved=await pixelHash('#approved');await page.locator('#partOverlay').check();
 check('actual visible endpoints draw on both approved and new art',noPartCandidate!==await pixelHash('#candidate')&&noPartApproved!==await pixelHash('#approved'));
 check('part table exposes occlusion and fixed399denominator',await page.locator('#partTable').innerText().then(t=>t.includes('shoulder_breadth: UNKNOWN')&&t.includes('leg_thickness: 49.0px / 12.3%')));
 await page.locator('#partOverlay').uncheck();check('turning off part overlay restores exact art',noPartCandidate===await pixelHash('#candidate')&&noPartApproved===await pixelHash('#approved'));
 await page.evaluate(()=>review.select(3));const matched=await pixelHash('#candidate');await page.locator('#profile').selectOption('before');
 check('before-size comparison switches actual pixels at same frame',matched!==await pixelHash('#candidate')&&await page.evaluate(()=>review.index===3&&review.profile==='before'));
 check('annotations do not transfer between size profiles',await page.evaluate(()=>Object.keys(review.exportData().observations[3]).length===0));await page.locator('#profile').selectOption('matched');
 check('visible nonapproval status',await page.locator('.fail').innerText().then(x=>x.includes('ยังไม่ผ่าน')));
 check('no runtime errors',errors.length===0);
 // Synthetic UI click coordinates are NOT anatomical observations. Clear them
 // before the review capture so the screenshot cannot promote a test point.
 await page.evaluate(()=>{review.clearAnnotations();review.select(3)});await page.locator('#grid').check();await page.locator('#surfaces').check();await page.screenshot({path:__dirname+'/approved-gif-browser.png',fullPage:true});
 await page.evaluate(()=>review.select(0));await page.screenshot({path:__dirname+'/size-standing-browser.png',fullPage:true});
 await page.evaluate(()=>review.select(7));await page.screenshot({path:__dirname+'/size-return-browser.png',fullPage:true});
 await page.evaluate(()=>review.select(0));await page.locator('#partOverlay').check();await page.screenshot({path:__dirname+'/part-size-browser.png',fullPage:true});
 fs.writeFileSync(__dirname+'/browser-qa.json',JSON.stringify({checks,errors,production_pass:false},null,2)+'\n');
 await browser.close();console.log(checks.length+' actual browser checks passed');
})().catch(e=>{console.error(e.stack);process.exit(1)});
