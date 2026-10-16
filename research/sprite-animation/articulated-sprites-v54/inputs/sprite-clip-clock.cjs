/* Independent original controller. One clock for frames/events; no engine dependency. */
'use strict';
class ClipClock {
  constructor(clip,onEvent=()=>{}) {
    if(!clip||!Array.isArray(clip.durations)||!clip.durations.length||clip.durations.some(x=>!Number.isFinite(x)||x<=0))throw Error('Invalid exposure durations');
    this.clip={...clip,durations:[...clip.durations]};this.total=clip.durations.reduce((a,b)=>a+b,0);this.events=(clip.events||[]).map(e=>({...e})).sort((a,b)=>a.at-b.at);
    if(!Number.isFinite(this.total)||typeof onEvent!=='function')throw Error('Invalid total or callback');
    if(this.events.some(e=>typeof e.id!=='string'||!e.id.length||!Number.isFinite(e.at)||e.at<0||e.at>this.total)||new Set(this.events.map(e=>e.id)).size!==this.events.length)throw Error('Invalid or duplicate event');
    this.onEvent=onEvent;this.time=0;this.running=false;this.finished=false;this.iteration=0;this.emitted=new Set();
  }
  start(){this.time=0;this.running=true;this.finished=false;this.iteration=0;this.emitted.clear();this._emit(-1,0);return this.sample();}
  cancel(){this.running=false;return this.sample();}
  seek(t){if(!Number.isFinite(t)||t<0||t>this.total)throw Error('Invalid seek');this.running=false;this.time=t;this.finished=t===this.total;return this.sample();}
  _emit(before,after){for(const e of this.events){const key=this.iteration+':'+e.id;if(e.at>before&&e.at<=after&&!this.emitted.has(key)){this.emitted.add(key);this.onEvent({...e,iteration:this.iteration});if(!this.running)break;}}}
  advance(delta){
    if(!Number.isFinite(delta)||delta<0)throw Error('Invalid delta');if(!this.running)return this.sample();
    let remaining=delta;
    while(this.running){const next=this.events.find(e=>e.at>this.time&&!this.emitted.has(this.iteration+':'+e.id));const old=this.time,step=Math.min(remaining,this.total-this.time,next?next.at-this.time:Infinity);this.time+=step;remaining-=step;this._emit(old,this.time);if(!this.running)break;
      if(this.time===this.total){if(this.clip.loop){this.iteration++;this.time=0;this.emitted.clear();this._emit(-1,0);}else{this.running=false;this.finished=true;}}
      if(remaining<=0||!this.running)break;
    }
    return this.sample();
  }
  sample(){let offset=this.time,frame=0;while(frame<this.clip.durations.length-1&&offset>=this.clip.durations[frame])offset-=this.clip.durations[frame++];return{frame,progress:Math.max(0,Math.min(1,offset/this.clip.durations[frame])),time:this.time,running:this.running,finished:this.finished,iteration:this.iteration};}
}
if(typeof module!=='undefined')module.exports={ClipClock};
if(typeof window!=='undefined')window.SpriteClipClock=ClipClock;
