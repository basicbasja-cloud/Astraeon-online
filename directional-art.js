/* Illustrated directional characters: continuous world orientation selects authored views.
 * Art stays at the project's original detail level. No horizontal mirroring.
 */
(() => {
'use strict';
const sheets={},pending={},silhouettes={};
function load(key){if(sheets[key])return Promise.resolve();return pending[key]??=new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>{sheets[key]=image;resolve()};image.onerror=()=>{delete pending[key];reject(new Error(`Cannot load ${key} directional art`))};image.src=`./assets/${key==='warrior-reactions'?'warrior-reactions-v2':key+(key.endsWith('-walk')?'-v1':'-directional-v1')}.webp`})}
const ready=Promise.all(['warrior','mage','ranger','warrior-walk','mage-walk','ranger-walk','warrior-reactions'].map(load));
const ensure=(zone,dungeon=false)=>Promise.all((dungeon?['forest','boss']:zone===1?['forest']:zone===2?['meadow']:zone>2?['meadow','forest']:[]).map(load));

const directionRow=angle=>((Math.round((Math.PI/2-angle)/(Math.PI/4))%8)+8)%8;
function pose(state,t,progress,impactAt=.45){
 if(['walk','run','sprint','start'].includes(state)&&t.speed>.02)return Math.floor(t.gait*2)%2+1;
 if(state==='dodge')return 5;
 if(state==='attack'||state==='cast')return progress<impactAt?3:4;
 if(state==='hit'||state==='death')return 5;
 if(state==='pickup')return 5;
 if(state==='interact')return 3;
 return 0;
}
function frame(ctx,iso,t,key,row,column,width,state,progress,time=0){
 const image=sheets[key],meta=window.AstraeonDirectionalMetadata?.[key];if(!image||!meta)return false;
 const cols=meta.cols,cellW=image.naturalWidth/cols,cellH=image.naturalHeight/(meta.rows||8),bounds=meta.frames[row*cols+column]||[column*cellW,row*cellH,cellW,cellH],foot=iso(t.position.x,t.position.y,t.position.z*35),registration=window.AstraeonHeroRegistration?.[key];
 const unit=(registration?70*(width/76)/registration.heights[row]:width/cellW)*(window.AstraeonView?.zoom||1),anchor=registration?.anchors[row*cols+column];
 const left=anchor?-anchor[0]*unit:(bounds[0]-column*cellW-cellW/2)*unit;
 ctx.save();ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
 if(state==='hit')ctx.globalAlpha*=.72+.28*Math.sin(progress*Math.PI);
 if(state==='death')ctx.globalAlpha*=Math.max(0,Math.min(1,(1-progress)/.35));
 const outline=meta.outlines?.[row*cols+column];
 if(outline){const id=`${key}/${row}/${column}`;let path=silhouettes[id];if(!path){path=silhouettes[id]=new Path2D();outline.forEach(([x,y],i)=>{i?path.lineTo(x,y):path.moveTo(x,y)});path.closePath()}ctx.translate(foot.x+left,foot.y-bounds[3]*unit);ctx.scale(unit,unit);ctx.clip(path);ctx.drawImage(image,...bounds,0,0,bounds[2],bounds[3])}
 else ctx.drawImage(image,...bounds,foot.x+left,foot.y-bounds[3]*unit*(state==='idle'?1+Math.sin(t.distance+time*2.3)*.003:1),bounds[2]*unit,bounds[3]*unit*(state==='idle'?1+Math.sin(t.distance+time*2.3)*.003:1));ctx.restore();
 return true;
}
function humanoid(ctx,iso,t,{archetype='warrior',state=t.state,time=0,progress=0,scale=1,impactAt=.45}={}){
 const row=directionRow(t.rotation),walking=['walk','run','sprint','start'].includes(state)&&t.speed>.02;
 // Four reviewed reaction views share the same eight-direction world facing.
 // Diagonals select the nearest authored cardinal; weapon hands are never mirrored.
 const reaction=archetype==='warrior'&&(state==='hit'||state==='death');
 // Keep the accepted rear poses where the extended sheet drifted toward a side/front view.
 const extended=walking&&row!==4&&row!==5;
 const backward=(t.velocity?.x||0)*t.facingDirection.x+(t.velocity?.y||0)*t.facingDirection.y<-.05;
 let stride=Math.floor((backward?8-t.gait*8%8:t.gait*8))%8;
 if(archetype==='warrior'&&stride===6)stride=5; // The sixth generated stride contains a neighboring sword fragment.
 frame(ctx,iso,t,reaction?'warrior-reactions':extended?`${archetype}-walk`:archetype,reaction?Math.round(row/2)%4:row,reaction?(state==='death'?1:0):extended?stride:pose(state,t,progress,impactAt),(window.AstraeonView?.scale.humanoid||103)*scale,state,progress,time);
 const facing=t.facingDirection;return {RightHand:[t.position.x+facing.y*.22,t.position.y-facing.x*.22,t.position.z+1.2],LeftHand:[t.position.x-facing.y*.22,t.position.y+facing.x*.22,t.position.z+1.2],Back:[t.position.x-facing.x*.2,t.position.y-facing.y*.2,t.position.z+1.2],Hip:[t.position.x,t.position.y,t.position.z+.8]};
}
function monster(ctx,iso,t,entity,time){
 const state=entity.hp<=0?'death':entity.animUntil>time?entity.animState:t.state,progress=Math.min(1,(time-(entity.hp<=0?entity.deadAt:entity.animStarted||0))/.9),column=(8-directionRow(t.rotation))%8;
 if(entity.boss){let row=0;if(['walk','run','start'].includes(state)&&t.speed>.02)row=1+Math.floor(t.gait*2)%2;else if(state==='attack')row=progress<.45?3:4;else if(state==='cast')row=5;else if(state==='hit')row=6;else if(state==='death')row=7;return frame(ctx,iso,t,'boss',row,column,window.AstraeonView?.scale.boss||150,state,progress,time)}
 const species=entity.species||0,row=(species%4)*2+(state==='attack'||state==='cast'?1:0),width=(window.AstraeonView?.scale.monster[species]||(species===6?115:species===3?100:85))*(entity.elite?1.15:1);
 return frame(ctx,iso,t,species<4?'meadow':'forest',row,column,width,state,progress,time);
}
window.AstraeonDirectionalArt={ready,ensure,humanoid,monster,directionRow,pose,sheets,views:8};
})();
