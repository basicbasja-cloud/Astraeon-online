/* Sprite presentation and animation clips; gameplay state is supplied by the caller. */
(() => {
'use strict';
const images={},keys=['warrior','mage','ranger','meadow-monsters','forest-monsters','moonveil-boss'];
for(const key of keys){const im=new Image();im.src=`./assets/${key}-atlas-v1.webp`;images[key]=im}
const clips=Object.freeze({
 idle:{frames:[0,1,2,3,4,5],duration:1.8,loop:true},
 run:{frames:[6,7,8,9,10,11],stride:1.35,loop:true},
 attack:{frames:[12,13,14,15,16,17],duration:.55},
 cast:{frames:[18,19,20,21,22,23],duration:.75},
 dodge:{frames:[24,25,26,27],duration:.42},
 hit:{frames:[28,29],duration:.3},
 knockdown:{frames:[30,31,32],duration:.95},
 death:{frames:[30,31,33],duration:.8},
 interact:{frames:[34],duration:.45},
 sit:{frames:[35],duration:1,loop:true}
});
const archetype=cls=>cls===3?'ranger':cls>=12&&cls<=16?'mage':'warrior';
function drawCell(ctx,key,index,x,y,size,flip=false,alpha=1){
 const image=images[key],meta=window.AstraeonAtlasMetadata?.[key];if(!image?.complete||!image.naturalWidth||!meta)return false;
 const cols=meta.cols,fw=image.naturalWidth/cols,fh=image.naturalHeight/meta.rows,col=index%cols,row=Math.floor(index/cols),anchor=meta.anchors[index]??.93;
 const rect=meta.rects?.[index]||[col*fw,row*fh,fw,fh],height=size*rect[3]/fw;
 ctx.save();ctx.globalAlpha*=alpha;ctx.translate(x,y);if(flip)ctx.scale(-1,1);ctx.drawImage(image,...rect,-size/2,-height*anchor,size,height);ctx.restore();return true;
}
function player(ctx,cls,anim,x,y,time,size=86){
 const clip=clips[anim.state]||clips.idle,elapsed=Math.max(0,time-anim.started),progress=clip.stride?(anim.distance||0)/clip.stride:elapsed/(anim.duration||clip.duration),phase=clip.loop?progress%1:Math.min(.999,progress),index=clip.frames[Math.min(clip.frames.length-1,Math.floor(phase*clip.frames.length))];
 return drawCell(ctx,archetype(cls),index,x,y,size,anim.facing<0);
}
function npc(ctx,kind,x,y,time,moving=false,distance=0,flip=false,size=69){const key=kind==='craft'||kind==='guild'?'warrior':kind==='housing'||kind==='market'?'mage':'ranger',frame=moving?6+Math.floor(distance/1.35*6)%6:Math.floor(time*2)%6;return drawCell(ctx,key,frame,x,y,size,flip)}
function monster(ctx,m,x,y,time,alpha=1){
 let key,index,size=m.boss?167:m.elite?104:83;
 const state=m.hp<=0?'dead':m.animUntil>time?m.animState:m.moving?'run':'idle';
 if(m.boss){key='moonveil-boss';index=state==='dead'?15:state==='attack'?8+Math.min(3,Math.floor(Math.max(0,time-(m.animStarted||time))*7)):state==='hit'?12:state==='run'?4+Math.floor(time*6)%4:Math.floor(time*2)%4}
 else{key=m.species>=4?'forest-monsters':'meadow-monsters';let row=(m.species||0)%4;index=row*4+(state==='attack'?2:state==='hit'||state==='dead'?3:state==='run'?1:0);if(m.species===1||m.species===6)size+=8}
 const bob=state==='idle'?Math.sin(time*2+m.x)*.6:state==='run'?Math.sin(time*8+m.x)*1.2:0;
 return drawCell(ctx,key,index,x,y+bob,size,m.facing<0,alpha);
}
window.AstraeonAnimation={clips,archetype,player,npc,monster,drawCell,ready:key=>images[key]?.complete&&images[key].naturalWidth};
})();
