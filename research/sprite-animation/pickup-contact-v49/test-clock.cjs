'use strict';const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');const {ClipClock}=require('./inputs/sprite-clip-clock.cjs');
const durations=[90,100,90,90,90,100,90,90,90,100,90,90,60,60,70,600];
const clip={durations,loop:false,events:[{id:'start',at:0},{id:'contact',at:560},{id:'attach',at:830},{id:'store',at:1300},{id:'end',at:1900}]};let checks={};let ev=[],c=new ClipClock(clip,e=>ev.push(e.id));c.start();c.advance(1900);assert.deepEqual(ev,['start','contact','attach','store','end']);assert.equal(c.sample().frame,15);assert.equal(c.sample().finished,true);checks.large_delta_emits_every_event_once=true;c.advance(1000);assert.equal(ev.length,5);checks.end_is_stable=true;
ev=[];c=new ClipClock(clip,e=>ev.push(e.id));c.start();for(let i=0;i<190;i++)c.advance(10);assert.deepEqual(ev,['start','contact','attach','store','end']);checks.small_steps_match_large_delta=true;
ev=[];c=new ClipClock(clip,e=>ev.push(e.id));c.start();c.advance(600);c.cancel();c.advance(2000);assert.deepEqual(ev,['start','contact']);checks.cancel_does_not_attach_or_store=true;
ev=[];c=new ClipClock(clip,e=>ev.push(e.id));c.seek(1300);assert.equal(ev.length,0);assert.equal(c.sample().frame,15);checks.review_seek_has_no_side_effect=true;
ev=[];c=new ClipClock({...clip,loop:true},e=>ev.push(e.id));c.start();c.advance(3801);assert.equal(c.sample().iteration,2);assert.equal(ev.filter(x=>x==='attach').length,2);assert.equal(ev.filter(x=>x==='start').length,3);checks.loop_events_once_per_iteration=true;

assert.throws(()=>new ClipClock({durations:[100,-1]}));assert.throws(()=>new ClipClock({durations:[100],events:[{id:'x',at:101}]}));assert.throws(()=>new ClipClock({durations:[100],events:[{id:'x',at:10},{id:'x',at:20}]}));assert.throws(()=>c.advance(-2));checks.invalid_durations_events_delta_rejected=true;
for(let i=0,t=0;i<durations.length;i++){c.seek(t);assert.equal(c.sample().frame,i);t+=durations[i];}checks.all16_key_boundaries=true;
ev=[];c=new ClipClock(clip,e=>{ev.push(e.id);if(e.id==='contact')c.cancel()});c.start();c.advance(1900);assert.deepEqual(ev,['start','contact']);assert.equal(c.time,560);checks.callback_cancel_stops_at_event_time=true;
c=new ClipClock({durations:[0.000000001]});c.seek(c.total);assert.equal(c.sample().progress,1);checks.subnanosecond_valid_duration_end=true;
const report={pass:true,checks,scope:'Controller clocks/events only, no art acceptance or actual inventory mutation'};fs.writeFileSync(path.join(__dirname,'clock-qa.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
