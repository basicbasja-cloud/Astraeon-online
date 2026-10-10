'use strict';
const test = require('node:test'), assert = require('node:assert/strict'), fs = require('node:fs');
const B = require('../character-art-baseline.js'), A = require('../character-assembly.js');
const read = file => JSON.parse(fs.readFileSync(file));
// Synthetic engine fixtures test reuse; no rejected production art is promoted.
const motion = read('authoring/characters/motion-templates/assembly-debug/motion-template.json');
const pack = read('authoring/characters/appearance/debug-blue/appearance-pack.json');
const baseline = {schemaVersion:'1.0', baselineId:'synthetic-reuse-test', revision:1, status:'DRAFT', referencePack:pack};
const manifest = id => B.makeArtManifest(baseline, id, {Body:pack.defaultParts.Body, Head:pack.defaultParts.Head});

test('new class and gender artwork use identical engine samples with unchanged shared equipment', () => {
 const family = B.buildAppearanceFamily(baseline, motion, [manifest('swordsman-female'), manifest('mage-male')], {allowDraft:true});
 const assembly = A.compileAssembly(motion, family.pack);
 const original = structuredClone(baseline);
 for (const action of Object.keys(motion.actions)) for (const direction of motion.directions) {
  const sequence = motion.actions[action].directions[direction];
  let elapsed = 0;
  for (let frame = 0; frame < sequence.frames.length; frame++) {
   const controller = A.createController(assembly, {action, direction, elapsedMs:elapsed + 1, cosmeticTimeMs:987});
   const before = controller.sample();
   const weaponBefore = before.layers.find(l => l.layer === 'MainHand');
   for (const variant of Object.values(family.variants)) {
    controller.setAppearance(variant.selection);
    const after = controller.sample();
    assert.deepEqual(after.frame, before.frame);
    assert.deepEqual(after.registeredAnchors, before.registeredAnchors);
    assert.deepEqual(after.drawOrder, before.drawOrder);
    assert.deepEqual(after.layers.find(l => l.layer === 'MainHand'), weaponBefore);
    assert.equal(after.frameIndex, frame);
    assert.equal(controller.elapsedMs, elapsed + 1);
    assert.equal(controller.cosmeticTimeMs, 987);
    assert.equal(after.appearance.Hair, before.appearance.Hair);
    assert.equal(after.appearance.Garment, before.appearance.Garment);
   }
   elapsed += sequence.frames[frame].durationMs;
  }
 }
 assert.deepEqual(baseline, original);
 assert.equal(family.pack.status, 'REQUIRES_OWNER_VISUAL_REVIEW');
});

test('a costume-only replacement leaves the selected head and all other slots untouched', () => {
 const body = B.makeArtManifest(baseline, 'costume-two', {Body:pack.defaultParts.Body});
 const family = B.buildAppearanceFamily(baseline, motion, [body], {allowDraft:true});
 const controller = A.createController(A.compileAssembly(motion, family.pack), {elapsedMs:95});
 const before = controller.appearance;
 controller.setAppearance(family.variants['costume-two'].selection);
 const after = controller.sample().appearance;
 for (const slot of Object.keys(pack.slots).filter(s => s !== 'Body')) assert.equal(after[slot], before[slot]);
});

test('artwork cannot alter timing, pivots, registration, draw order, dimensions, or contract version', () => {
 const changes = [
  m => m.timing = {duration:1},
  m => m.parts.Body.pivot = [0,0],
  m => m.parts.Head.anchors = {},
  m => m.parts.Head.drawProfile = 'front',
  m => Object.values(m.parts.Body.textures)[0].width++,
  m => m.baselineRevision++,
  m => delete m.parts.Body.textures[Object.keys(m.parts.Body.textures)[0]],
  m => m.parts.Body.textures.extra = {file:'assets/characters/x.png',width:1,height:1},
  m => Object.values(m.parts.Head.textures)[0].file = '../outside.png',
  m => m.parts.Body.sourcePart = pack.defaultParts.MainHand,
  m => m.status = 'APPROVED'
 ];
 for (const change of changes) {
  const m = manifest('replacement'); change(m);
  assert.throws(() => B.buildAppearanceFamily(baseline, motion, [m], {allowDraft:true}));
 }
});

test('unapproved baseline cannot enter the normal build path and duplicates are rejected', () => {
 assert.throws(() => B.buildAppearanceFamily(baseline, motion, [manifest('example')]), /visual review/);
 assert.throws(() => B.buildAppearanceFamily(baseline, motion, [manifest('example'),manifest('example')], {allowDraft:true}), /duplicate/);
 const forged = {...baseline, status:'APPROVED'};
 assert.throws(() => B.buildAppearanceFamily(forged, motion, []), /owner provenance/);
 const rejected=structuredClone(baseline);rejected.referencePack.source.ownerRejected=true;
 assert.throws(() => B.buildAppearanceFamily(rejected,motion,[],{allowDraft:true}),/Owner-rejected/);
});
