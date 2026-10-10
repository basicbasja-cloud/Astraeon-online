#!/usr/bin/env node
'use strict';
// Scaffold or verify artwork manifests; never generate poses or retarget anatomy.
const fs = require('node:fs'), path = require('node:path');
const B = require('../character-art-baseline.js');
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
const [command, baselineFile, motionFile, arg, output] = process.argv.slice(2);
if (!['scaffold', 'verify'].includes(command) || !baselineFile || !motionFile || !arg) {
 console.error('Usage: node tools/character_art_variant.cjs scaffold BASELINE MOTION VARIANT_ID OUTPUT\n       node tools/character_art_variant.cjs verify BASELINE MOTION MANIFEST');
 process.exit(2);
}
try {
 const baseline = read(baselineFile), motion = read(motionFile);
 B.validateBaseline(baseline, motion);
 if (command === 'scaffold') {
  if (!output) throw Error('An output path is required');
  const selections = Object.fromEntries(['BodyWithOutfit', 'Head'].map(slot => {
   const id = baseline.referencePack.defaultParts[slot];
   if (!id) throw Error('Baseline must contain production BodyWithOutfit and complete Head+Hair defaults');
   return [slot, id];
  }));
  const manifest = B.makeArtManifest(baseline, arg, selections);
  fs.mkdirSync(path.dirname(output), {recursive: true});
  fs.writeFileSync(output, JSON.stringify(manifest, null, 2) + '\n', {flag: 'wx'});
  console.log('Created artwork manifest; texture files still need original artwork: ' + output);
 } else {
  const manifest = read(arg);
  B.buildAppearanceFamily(baseline, motion, [manifest], {allowDraft: true});
  for (const part of Object.values(manifest.parts)) for (const texture of Object.values(part.textures)) {
   const resolved = path.resolve(__dirname, '..', texture.file);
   const bytes = fs.readFileSync(resolved);
   if (bytes.length < 33 || !bytes.subarray(0, 8).equals(Buffer.from([137,80,78,71,13,10,26,10])) || bytes.toString('ascii', 12, 16) !== 'IHDR') throw Error('Expected PNG: ' + texture.file);
   if (bytes.readUInt32BE(16) !== texture.width || bytes.readUInt32BE(20) !== texture.height) throw Error('Actual PNG dimensions differ: ' + texture.file);
  }
  console.log('Artwork contract and PNG dimensions verified. Visual anatomy, grip, and occlusion still require review.');
 }
} catch (error) { console.error(error.message); process.exit(1); }
