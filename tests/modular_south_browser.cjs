/* Inspect a rejected authoring candidate; this is never visual approval. */
const {chromium}=require('playwright'),fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const out=path.resolve('docs/review/character-true-modular-v2');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-gpu','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1360,height:1000}}),errors=[],badHttp=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)badHttp.push(r.status()+' '+r.url())});
 await page.goto('http://127.0.0.1:8021/character-modular-source-review.html',{waitUntil:'networkidle'});
 await page.waitForFunction(()=>!!window.AstraeonModularSourceReview);
 const before=await page.evaluate(()=>AstraeonModularSourceReview.snapshot());
 assert.equal(before.visualGate,'VISUAL_FAIL');assert.deepEqual(before.missing,['HairBack','HairFront']);
 await page.screenshot({path:path.join(out,'browser-authoring-failure.png')});
 await page.selectOption('#scale','0.54');await page.screenshot({path:path.join(out,'browser-game-size-failure.png')});
 const layerData=await page.evaluate(()=>{
  const r=AstraeonModularSourceReview,s=r.draft.sample(),before={};
  for(const l of s.layers)before[l.layer]=r.renderPose({visibleLayers:[l.layer]});
  const hidden=r.renderPose({appearance:{Weapon:null}}),after={};
  for(const l of r.draft.sample().layers)after[l.layer]=r.renderPose({visibleLayers:[l.layer]});
  return {before,after,full:r.renderPose(),hidden};
 });
 for(const layer of Object.keys(layerData.before))assert.equal(layerData.before[layer],layerData.after[layer]);
 assert.notEqual(layerData.full,layerData.hidden);
 const decode=data=>Buffer.from(data.split(',')[1],'base64');
 fs.writeFileSync(path.join(out,'browser-weapon-hidden-diagnostic.png'),decode(layerData.hidden));
 const hashes=Object.fromEntries(Object.entries(layerData.before).map(([l,png])=>[l,crypto.createHash('sha256').update(decode(png)).digest('hex')]));
 const report={standaloneBrowser:'PASS_DIAGNOSTIC_ONLY',visualGate:'VISUAL_FAIL',ownerApproval:'PENDING',verifiedRasterSources:5,
  unchangedLayerRastersOnWeaponHide:hashes,sourceCoverageComplete:false,missing:['HairBack','HairFront'],newCosmeticABProof:false,
  desktopAuthoringCapture:true,approximateGameplayScale:.54,sourceHashes:before.sourceHashes,errors,badHttp};
 fs.writeFileSync(path.join(out,'browser-review.json'),JSON.stringify(report,null,2)+'\n');
 console.log('PASS standalone diagnostic:5 hash-verified layers,5 unaffected raster comparisons, weapon hide differs; South remains VISUAL_FAIL.');
 // The world stays isolated in a srcdoc memory save, preserving normal boot.
 const ownerStorage=await page.evaluate(()=>JSON.stringify({...localStorage}));
 await page.evaluate(()=>AstraeonModularSourceReview.loadWorld());
 for(let tries=0;tries<8;tries++){
  try{await page.waitForFunction(()=>AstraeonModularSourceReview.snapshot().worldDraws>3,{timeout:30000});break}
  catch(e){console.log('World initialization still pending ('+(tries+1)+'/8).');if(tries===7)throw e}
 }
 const world=await page.evaluate(()=>AstraeonModularSourceReview.snapshot());
 assert.equal(world.worldSample.memoryOnly,true);assert.equal(world.worldSample.visualGate,'VISUAL_FAIL');assert.equal(world.worldSample.poseId,'Idle/S/key0');
 assert.equal(ownerStorage,await page.evaluate(()=>JSON.stringify({...localStorage})));
 await page.locator('#worldReview').scrollIntoViewIfNeeded();
 await page.screenshot({path:path.join(out,'world-failed-candidate.png')});
 report.worldReview={actualWorldCapture:true,saveInMemory:true,ownerStorageUnchanged:true,snapshot:world.worldSample};
 assert.deepEqual(errors,[]);assert.deepEqual(badHttp,[]);
 fs.writeFileSync(path.join(out,'browser-review.json'),JSON.stringify(report,null,2)+'\n');
 console.log('PASS actual-world failed candidate capture; memory-only save, static South pose, unchanged owner storage.');
 await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1});
