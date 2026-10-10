#!/usr/bin/env node
'use strict';
// Generic static layer-fit proof. Cannot be mistaken for the full action master.
const fs=require('node:fs'),path=require('node:path'),M=require('../character-motion-template.js'),A=require('../character-assembly.js');
const [configFile,outDir]=process.argv.slice(2);
if(!configFile||!outDir){console.error('Usage: node tools/compile_character_pose_study.cjs STUDY.json OUTPUT_DIRECTORY');process.exit(2)}
const c=JSON.parse(fs.readFileSync(configFile,'utf8')),T=(x,y)=>({x,y,rotation:0,scale:1}),root=T(...c.root),layers=[...M.LAYERS];
const motion={schemaVersion:'1.0',motionTemplateId:c.id+'-neutral-fit',status:'DEV_ONLY',provenance:{kind:'SYNTHETIC_ENGINE_FIXTURE',description:'Static original-art layer fitting only. Not animation choreography or an approved master.'},directions:[...M.DIRECTIONS],registration:{canvas:c.canvas,root,referenceHeight:c.referenceHeight,mirroring:'none'},transformConvention:'canvas pixels; clockwise radians; uniform positive scale',drawProfiles:{neutral:layers},defaultDrawProfile:'neutral',actions:{Idle:{loop:true,directions:{}}}};
const pack={schemaVersion:'1.1',packId:c.id+'-neutral-fit',status:'DEV_ONLY',headAppearanceModel:'HeadIncludesHair',source:{reference:configFile,method:'Fresh original static layer fit; no rejected pose art reused'},compatibleMotionTemplates:[motion.motionTemplateId],registration:motion.registration,mirroring:'none',slots:{BodyWithOutfit:{required:true,layers:['Body']},Head:{required:true,layers:['HeadBase']}},defaultParts:{BodyWithOutfit:'body-study',Head:'head-study'},parts:{'body-study':{slot:'BodyWithOutfit',mode:'BODY_SYNC',space:'canvas',contractId:c.id+'-neutral-body',timelines:{Idle:{}}},'head-study':{slot:'Head',mode:'BODY_SYNC',space:'attachment',anchor:'head',timelines:{Idle:{}}}},atlases:c.atlases,bodyContract:{contractId:c.id+'-neutral-body',model:'BodyWithOutfit+Head',registration:motion.registration,directions:[...M.DIRECTIONS],actions:['Idle'],timeline:{Idle:{}},sockets:['head','mainHand','offHand','back'],anchorRegistration:{Idle:{}}}};
for(const [row,d]of M.DIRECTIONS.entries()){
 const head=T(...c.headAttachments[d]),anchors={root:{...root},head,mainHand:T(root.x-25,root.y-70),offHand:T(root.x+25,root.y-70),back:T(root.x,root.y-90),waist:T(root.x,root.y-65),footL:T(root.x-12,root.y),footR:T(root.x+12,root.y)};
 const f={id:`Idle/${d}/neutral`,durationMs:1000,role:'referenceKey',referencePhase:'neutralFit',root:{...root},anchors,events:[],poseIntent:{bodyOrientation:d,limbPhase:'Static fitted original art; equipment anchors not authored',footContact:'Shared normalization origin',attackPhase:'No attack in this study',silhouette:'Original neutral source; visual approval pending'},source:{kind:'SYNTHETIC_ENGINE_FIXTURE'}};
 motion.actions.Idle.directions[d]={totalDurationMs:1000,referenceKeys:[f],frames:[f]};
 pack.bodyContract.timeline.Idle[d]=[1000];pack.bodyContract.anchorRegistration.Idle[d]=Object.fromEntries(['head','mainHand','offHand','back'].map(k=>[k,T(0,0)]));pack.bodyContract.anchorRegistration.Idle[d]=[pack.bodyContract.anchorRegistration.Idle[d]];
 const rect=[0,row*c.canvas[1],...c.canvas];
 pack.parts['body-study'].timelines.Idle[d]={frames:[{layers:{Body:{atlasId:'body',rect,sourceDirection:d}}}]};
 pack.parts['head-study'].timelines.Idle[d]={frames:[{layers:{HeadBase:{atlasId:'head',rect,pivot:c.headPivot,trim:{sourceSize:c.canvas,offset:[0,0]},sockets:{hair:T(0,0),headgear:T(0,-35)},sourceDirection:d}}}]};
}
M.compileMotionTemplate(motion);A.compileAssembly(motion,pack);
fs.mkdirSync(outDir,{recursive:true});fs.writeFileSync(path.join(outDir,'motion-template.json'),JSON.stringify(motion,null,2)+'\n');fs.writeFileSync(path.join(outDir,'appearance-pack.json'),JSON.stringify(pack,null,2)+'\n');console.log('Static original-art fit compiled; equipment/Walk/Attack unavailable, not a master.');
