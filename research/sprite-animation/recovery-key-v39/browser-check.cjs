const fs=require('fs'),crypto=require('crypto'),assert=require('assert');
const {chromium}=require('/opt/codex/runtimes/cua/lib/node_modules/playwright');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
(async()=>{
 const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
 const p=await b.newPage({viewport:{width:1100,height:850}}),errors=[],checks=[];
 p.on('pageerror',e=>errors.push(e.message));await p.route('**/*',r=>r.abort());
 await p.setContent(fs.readFileSync(__dirname+'/motion-preview.html','utf8'));
 await p.waitForFunction(()=>window.motion?.ready);
 const check=(name,value)=>{assert(value,name);checks.push({name,pass:true})};
 check('two logical slots, three ordered rendering passes',await p.evaluate(()=>motion.data.logical_slots.length===2&&motion.data.draw_order.length===3));
 const count=await p.evaluate(()=>{let n=0;const original=CanvasRenderingContext2D.prototype.drawImage;CanvasRenderingContext2D.prototype.drawImage=function(...a){n++;return original.apply(this,a)};motion.frame(3);CanvasRenderingContext2D.prototype.drawImage=original;return n});
 check('actual full frame makes three drawImage calls',count===3);
 for(const v of ['review','raw8']){
  let same=true;for(let i=0;i<8;i++){
   const url=await p.evaluate(([i,v])=>motion.frame(i,v),[i,v]);
   same&&=sha(Buffer.from(url.split(',')[1],'base64'))===sha(fs.readFileSync(`${__dirname}/renders/${v}/full/${String(i).padStart(2,'0')}.png`));
  }check(v+' exported pixels reproducible across all eight keys',same);
 }
 check('review has seven unique body drawings and matching terminal rest',await p.evaluate(()=>new Set(motion.data.variants.review.map(x=>x.body.sha256)).size===7&&JSON.stringify(motion.data.selected_pose_map)==='[[2,7],[2,1],[2,2],[2,3],[2,4],[2,5],[39,0],[2,7]]'));
 check('terminal rest matches start; near-rest is a distinct drawing',await p.evaluate(()=>motion.frame(0)===motion.frame(7)&&motion.frame(6)!==motion.frame(7)));
 await p.locator('#frame').fill('4');check('slider changes frame and stops play',await p.evaluate(()=>motion.index===4&&!motion.running));
 await p.locator('#variant').selectOption('raw8');check('variant switch keeps current logical frame',await p.evaluate(()=>motion.index===4&&document.querySelector('#status').textContent.startsWith('raw8')));
 await p.locator('#clock').selectOption('game');check('clock selection resets one shared action state',await p.evaluate(()=>motion.index===0&&!motion.running));
 await p.clock.install();await p.locator('#play').click();await p.clock.runFor(450);
 check('game clock reaches key four at 450ms',await p.evaluate(()=>motion.index===4&&motion.running));
 await p.clock.runFor(900);check('game playback ends in terminal hold',await p.evaluate(()=>motion.index===7&&!motion.running));
 await p.locator('#clock').selectOption('source');await p.locator('#play').click();await p.clock.runFor(600);
 check('source clock reaches key three at 600ms',await p.evaluate(()=>motion.index===3&&motion.running));
 await p.clock.runFor(1350);check('source playback ends at 1.3s plus 600ms hold',await p.evaluate(()=>motion.index===7&&!motion.running));
 await p.evaluate(()=>motion.select('review',3));
 const before=await p.locator('#view').screenshot();await p.locator('#guides').check();const after=await p.locator('#view').screenshot();
 check('actual observed edge overlay changes canvas pixels',sha(before)!==sha(after));await p.locator('#guides').uncheck();
 check('one common positive body transform across all keys',await p.evaluate(()=>motion.data.variants.review.every(r=>JSON.stringify(r.body_matrix)===JSON.stringify(motion.data.body_uniform_rest_matrix))&&motion.data.body_uniform_rest_matrix[0]>0));
 check('head scale unchanged from v36',await p.evaluate(()=>motion.data.head_scale===.11));
 check('runtime binds current normalization receipt',await p.evaluate(()=>motion.data.isolated_key_provenance.normalization.sha256)===sha(fs.readFileSync(__dirname+'/normalization.json')));
 check('isolated-key review scope remains visible',await p.locator('.status').innerText().then(t=>t.includes('same seven other poses')));
 check('no browser runtime errors',errors.length===0);
 await p.evaluate(()=>motion.select('review',6));await p.screenshot({path:__dirname+'/motion-browser.png',fullPage:true});
 fs.writeFileSync(__dirname+'/browser-qa.json',JSON.stringify({checks,errors,production_pass:false},null,2)+'\n');
 await b.close();console.log(`${checks.length} actual browser checks passed`);
})().catch(e=>{console.error(e.stack);process.exit(1)});
