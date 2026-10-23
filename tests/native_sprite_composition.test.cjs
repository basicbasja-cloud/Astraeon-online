'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
global.window={};const api=require('../modular-sprites.js');
const fixture=()=>{const d=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures/modular-contract/swordsman.json'),'utf8'));d.canvas.compositionWidth=d.canvas.compositionHeight=640;for(const [id,part]of Object.entries(d.parts))for(const ref of Object.values(part.frames)){ref.rect=[id==='weapon-alt'?64:0,0,64,64];ref.offset=[100,200]}return d};
function context(){return{calls:[],save(){this.calls.push(['save'])},restore(){this.calls.push(['restore'])},clearRect(...args){this.calls.push(['clearRect',...args])},drawImage(...args){this.calls.push(['drawImage',...args])}}}
test('native trimmed layers compose once before reduction, retain root, and cache by selected pixels',()=>{
 const surfaces=[];window.OffscreenCanvas=class{constructor(width,height){this.width=width;this.height=height;this.context=context();surfaces.push(this)}getContext(){return this.context}};
 const d=fixture(),compiled=api.compile(d),sample=compiled.sample('Walk','SW',130),images=Object.fromEntries(Object.keys(d.atlases).map(id=>[id,{id}])),ctx=context();
 const sockets=api.draw(ctx,sample,images,{x:400,y:500,scale:.5});assert.equal(surfaces.length,2);
 const source=surfaces[0].context.calls.filter(c=>c[0]==='drawImage');assert.equal(source.length,sample.layers.length);for(const call of source)assert.deepEqual(call.slice(-4),[100,200,64,64]);
 assert.deepEqual(surfaces[1].context.calls.find(c=>c[0]==='drawImage').slice(-8),[98,198,68,68,0,0,68,68]);
 assert.equal(ctx.calls.filter(c=>c[0]==='drawImage').length,1);assert.deepEqual(ctx.calls.find(c=>c[0]==='drawImage').slice(-4),[320,368,160,160]);assert.deepEqual(sockets.root,{x:400,y:500});
 api.draw(context(),sample,images,{x:50,y:60,scale:2});assert.equal(surfaces.length,2,'world placement does not invalidate the reusable pose');
 api.draw(context(),compiled.sample('Walk','SW',130,{appearance:{Weapon:'weapon-alt'}}),images);assert.equal(surfaces.length,3,'a changed weapon recomposes from the retained body');
 api.draw(context(),{...sample,layers:sample.layers.filter(l=>l.slot!=='Weapon')},images);assert.equal(surfaces.length,4,'a diagnostic hidden-weapon view must not reuse the equipped image');
});
test('native source canvas and integer atlas placements are validated',()=>{
 for(const mutate of [d=>d.canvas.compositionWidth=600,d=>d.canvas.compositionWidth=d.canvas.compositionHeight=256,d=>d.canvas.compositionWidth=d.canvas.compositionHeight=4096,d=>Object.values(d.parts.hair.frames)[0].offset=[-1,2],d=>Object.values(d.parts.hair.frames)[0].offset=[600,2],d=>Object.values(d.parts.hair.frames)[0].offset=[1.5,2]]){const d=fixture();mutate(d);assert.ok(api.validateDefinition(d).length);assert.throws(()=>api.compile(d))}
 assert.deepEqual(api.validateDefinition(fixture()),[]);
});
test('missing images leave the destination untouched in native composition mode',()=>{
 const d=fixture(),sample=api.compile(d).sample('Idle','S'),ctx=context();assert.throws(()=>api.draw(ctx,sample,{}),/Atlas not loaded/);assert.equal(ctx.calls.length,0);
});
