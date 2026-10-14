const {chromium}=require('/opt/codex/runtimes/cua/lib/node_modules/playwright'),fs=require('fs');
(async()=>{
 const b=await chromium.launch({executablePath:'/usr/bin/chromium',args:['--no-sandbox','--disable-dev-shm-usage']});
 const p=await b.newPage({viewport:{width:1100,height:950}});let errors=[],bindings={};
 p.on('pageerror',e=>errors.push(e.message));await p.route('**/*',r=>r.abort());await p.setContent(fs.readFileSync(__dirname+'/hair-preview.html','utf8'));await p.waitForFunction(()=>hair?.ready);
 for(const s of ['original','silver','auburn','bald']){
  fs.mkdirSync(__dirname+'/frames/'+s,{recursive:true});fs.mkdirSync(__dirname+'/head-masks/'+s,{recursive:true});bindings[s]=[];
  for(let i=0;i<8;i++){
   const data=await p.evaluate(([i,s])=>({url:hair.frame(i,s),head:hair.headFrame(i,s),rows:hair.rows(i,s).map(r=>({name:r.name,matrix:r.matrix,texture_sha256:r.part.sha256,head_mount_inherited:r.head_mount_inherited??false}))}),[i,s]);
   fs.writeFileSync(__dirname+'/frames/'+s+'/'+String(i).padStart(2,'0')+'.png',Buffer.from(data.url.split(',')[1],'base64'));
   fs.writeFileSync(__dirname+'/head-masks/'+s+'/'+String(i).padStart(2,'0')+'.png',Buffer.from(data.head.split(',')[1],'base64'));bindings[s].push(data.rows);
  }
  const url=await p.evaluate(s=>hair.headPreview(s),s);fs.writeFileSync(__dirname+'/head-'+s+'.png',Buffer.from(url.split(',')[1],'base64'));
 }
 fs.writeFileSync(__dirname+'/bindings.json',JSON.stringify(bindings,null,2)+'\n');fs.writeFileSync(__dirname+'/poses.json',JSON.stringify(await p.evaluate(()=>hair.poses),null,2)+'\n');
 await p.evaluate(()=>hair.select('silver',0));await p.screenshot({path:__dirname+'/runtime-browser.png',fullPage:true});await b.close();
 if(errors.length)throw Error(errors.join('\n'));console.log(JSON.stringify({frames:32,head_passes:32,errors}));
})().catch(e=>{console.error(e.stack);process.exit(1)});
