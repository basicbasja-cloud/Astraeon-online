import assert from 'node:assert/strict';
import test from 'node:test';
import {TIMES,DURATION,FX_START,FX_END,keyAt,geometry} from './hand-tail.mjs';
import fs from 'node:fs';
const data=JSON.parse(fs.readFileSync(new URL('./evidence/selected-bank.json',import.meta.url)));
test('exact exposure boundaries and terminal key',()=>{TIMES.forEach((t,i)=>assert.equal(keyAt(t),i));assert.equal(keyAt(DURATION),7)});
test('no smear during ready/windup/coil',()=>{for(let t=0;t<FX_START;t++)assert.equal(geometry(t,data).active,false)});
test('smear expires before recovery/ready',()=>{for(let t=FX_END;t<=DURATION;t++)assert.equal(geometry(t,data).active,false)});
test('cancellation clears current tail immediately',()=>assert.equal(geometry(280,data,{cancelled:true}).active,false));
test('disabled effect never changes body key',()=>{assert.equal(geometry(280,data,{enabled:false}).active,false);assert.equal(keyAt(280),4)});
test('live tail follows pose-bound virtual tip',()=>{for(let t=FX_START;t<FX_END;t++)assert(geometry(t,data).endpoint_error_px<1e-8)});
test('tail collapses and fades instead of frozen terminal smear',()=>{const a=geometry(360,data),b=geometry(399,data);assert(b.alpha<a.alpha);assert(Math.hypot(...b.outer[0].map((v,k)=>v-b.outer.at(-1)[k]))<Math.hypot(...a.outer[0].map((v,k)=>v-a.outer.at(-1)[k])))});
test('all pose-bound guide samples are finite and in this control viewport',()=>{for(let t=FX_START;t<FX_END;t++)for(const p of [...geometry(t,data).outer,...geometry(t,data).inner])assert(p.every(x=>Number.isFinite(x)&&x>=0&&x<=512))});

test("leading smear face reaches current painted hand rather than floating",()=>{for(let t=FX_START;t<FX_END;t++){const g=geometry(t,data);assert(Math.hypot(...g.inner.at(-1).map((v,k)=>v-g.head_palm_xy[k]))<1e-8)}});

test("follow-through drops the early windup arc instead of holding one full sweep",()=>{const a=geometry(230,data),b=geometry(280,data);assert.notDeepEqual(a.outer[0],b.outer[0]);assert(b.outer[0][0]>a.outer[0][0]+100)});
