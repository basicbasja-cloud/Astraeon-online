const test=require('node:test'),assert=require('node:assert/strict');
const manifest=require('../world/v3/warrior-painted-locomotion.json');
global.window={AstraeonDirectionalMetadata:{},AstraeonHeroRegistration:{},AstraeonView:{project:(x,y)=>({x,y}),zoom:1,scale:{humanoid:76}},AstraeonSpriteMotion:{sample:()=>({x:0,lift:0,lean:0,stretch:1})}};
global.Image=class{constructor(){this.naturalWidth=this.naturalHeight=2560}set src(value){this.url=value;queueMicrotask(()=>this.onload())}};
require('../directional-art.js');
test('all authored modes play eight distinct complete frames, including rear views',async()=>{
 await window.AstraeonDirectionalArt.configurePaintedLocomotion(manifest);
 for(const mode of ['walk','run','sprint'])for(let row=0;row<8;row++){
  const crops=[],ctx={save(){},restore(){},translate(){},rotate(){},scale(){},drawImage(image,...args){assert(image.url.includes(manifest.clips[mode].clip));crops.push(args.slice(0,4).join(','))}};
  for(let phase=0;phase<8;phase++)window.AstraeonDirectionalArt.humanoid(ctx,()=>({x:0,y:0}),{rotation:Math.PI/2-row*Math.PI/4,state:mode,activeStrategy:mode,speed:2,gait:phase/8,position:{x:0,y:0,z:0},velocity:{x:0,y:2},facingDirection:{x:0,y:1}},{state:mode});
  assert.equal(new Set(crops).size,8,mode+'/'+manifest.directions[row]);
 }
});
test('malformed registration is rejected before it can crop another body or divide by zero',()=>{
 const broken=structuredClone(manifest);broken.clips.walk.heights[0]=0;assert.throws(()=>window.AstraeonDirectionalArt.configurePaintedLocomotion(broken));
 const wrong=structuredClone(manifest);wrong.clips.walk.frames[0].anchor[0]=10000;assert.throws(()=>window.AstraeonDirectionalArt.configurePaintedLocomotion(wrong));
 const direction=structuredClone(manifest);direction.clips.walk.frames[32].direction='S';assert.throws(()=>window.AstraeonDirectionalArt.configurePaintedLocomotion(direction));
 for(const mutate of [c=>c.frames[0].sole[1]=Infinity,c=>c.frames[0].support='left',c=>c.frames[0].stance=1,c=>c.duty=0]){
  const bad=structuredClone(manifest);mutate(bad.clips.run);assert.throws(()=>window.AstraeonDirectionalArt.configurePaintedLocomotion(bad));
 }
});
