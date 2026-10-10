#!/usr/bin/env node
'use strict';
const fs = require('node:fs'), path = require('node:path');
const B = require('../character-art-baseline.js');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const [pipelineFile, motionFile, appearanceFile, output] = process.argv.slice(2);
if (!output) {
 console.error('Usage: node tools/create_character_master.cjs PIPELINE.json MOTION.json APPEARANCE.json OUTPUT.json');
 process.exit(2);
}
try {
 const pipeline = read(pipelineFile), motion = read(motionFile), pack = read(appearanceFile);
 if (pack.schemaVersion !== '1.1' || !pack.slots.BodyWithOutfit?.required || !pack.slots.Head?.required) throw Error('Master needs production BodyWithOutfit and independent Head');
 if (pack.headAppearanceModel !== 'HeadIncludesHair' || pack.slots.Hair) throw Error('This RO1 baseline requires complete Head+Hair styles, independently attached to body');
 if (JSON.stringify(pipeline.directions) !== JSON.stringify(motion.directions) || JSON.stringify(pipeline.actions) !== JSON.stringify(Object.keys(motion.actions))) throw Error('Master action/direction contract mismatch');
 if (JSON.stringify(pipeline.registration.canvas) !== JSON.stringify(motion.registration.canvas) || pipeline.registration.root[0] !== motion.registration.root.x || pipeline.registration.root[1] !== motion.registration.root.y) throw Error('Master canvas/root differs from pipeline');
 const baseline = {schemaVersion:'1.0', baselineId:pipeline.baselineId, revision:pipeline.revision,
  status:'REQUIRES_OWNER_VISUAL_REVIEW', referencePack:pack};
 // This command never promotes art or copies historical approval to a new master.
 B.validateBaseline(baseline, motion);
 for (const atlas of Object.values(pack.atlases)) {
  const file=path.resolve(__dirname,'..',atlas.file), bytes=fs.readFileSync(file);
  if(bytes.length<33 || !bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])) || bytes.toString('ascii',12,16)!=='IHDR')throw Error('Master atlas is not PNG: '+atlas.file);
  if(bytes.readUInt32BE(16)!==atlas.width || bytes.readUInt32BE(20)!==atlas.height)throw Error('Master atlas dimensions differ: '+atlas.file);
 }
 fs.mkdirSync(path.dirname(output),{recursive:true});
 fs.writeFileSync(output,JSON.stringify(baseline,null,2)+'\n',{flag:'wx'});
 console.log('Created review candidate master. Owner approval is still required: '+output);
} catch(error) {console.error(error.message);process.exit(1);}
