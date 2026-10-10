/* Artwork-only character families. No class/gender branches or gameplay state. */
(function (scope) {
'use strict';
const A = scope.AstraeonCharacterAssembly || (typeof require === 'function' ? require('./character-assembly.js') : null);
const M = scope.AstraeonMotionTemplate || (typeof require === 'function' ? require('./character-motion-template.js') : null);
const clone = value => JSON.parse(JSON.stringify(value));
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);
const id = value => typeof value === 'string' && /^[a-z][a-z0-9-]*$/.test(value);
const own = (value, key) => Object.prototype.hasOwnProperty.call(value, key);
function fields(value, allowed, label) {
 if (!object(value)) throw Error(label + ' must be an object');
 for (const key of Object.keys(value)) if (!allowed.includes(key)) throw Error(label + ' cannot override ' + key);
}
function atlasIds(part) {
 const result = new Set();
 for (const directions of Object.values(part.timelines)) for (const sequence of Object.values(directions)) {
  for (const frame of sequence.frames || sequence.phases || sequence.views || []) {
   for (const layer of Object.values(frame.layers)) result.add(layer.atlasId);
  }
 }
 return [...result].sort();
}
function validateBaseline(baseline, template) {
 fields(baseline, ['schemaVersion', 'baselineId', 'revision', 'status', 'referencePack', 'review'], 'Baseline');
 if (baseline.schemaVersion !== '1.0' || !id(baseline.baselineId) || !Number.isSafeInteger(baseline.revision) || baseline.revision < 1) throw Error('Invalid baseline identity');
 if (!['DRAFT', 'REQUIRES_OWNER_VISUAL_REVIEW', 'APPROVED'].includes(baseline.status)) throw Error('Invalid baseline status');
 if (baseline.referencePack?.source?.ownerRejected === true) throw Error('Owner-rejected appearance cannot become a reusable master');
 if (baseline.status === 'APPROVED' && (!baseline.review?.approvedBy || !baseline.review?.reference || baseline.referencePack?.status !== 'APPROVED')) throw Error('Approved baseline requires approved reference art and owner provenance');
 const errors = A.validateAppearancePack(baseline.referencePack, template);
 if (errors.length) throw Error('Invalid baseline reference pack: ' + errors.join('; '));
 return baseline;
}
function makeArtManifest(baseline, variantId, selections) {
 if (!id(variantId)) throw Error('Invalid variant identity');
 if (!object(selections) || !Object.keys(selections).length) throw Error('Select at least one reference part');
 const parts = {};
 for (const [slot, sourcePart] of Object.entries(selections)) {
  const part = baseline.referencePack.parts[sourcePart];
  if (!part || part.slot !== slot) throw Error('Incompatible reference part ' + sourcePart);
  parts[slot] = {sourcePart, textures: Object.fromEntries(atlasIds(part).map(key => {
   const atlas = baseline.referencePack.atlases[key];
   return [key, {file: `assets/characters/${variantId}/${key}.png`, width: atlas.width, height: atlas.height}];
  }))};
 }
 return {schemaVersion: '1.0', baselineId: baseline.baselineId, baselineRevision: baseline.revision,
  variantId, label: variantId, status: 'REQUIRES_OWNER_VISUAL_REVIEW', parts};
}
function buildAppearanceFamily(baseline, template, manifests, {allowDraft = false} = {}) {
 validateBaseline(baseline, template);
 if (baseline.status !== 'APPROVED' && !allowDraft) throw Error('Baseline has not passed owner visual review; allowDraft is for explicit development previews only');
 if (!Array.isArray(manifests)) throw Error('Variant manifests must be an array');
 const pack = clone(baseline.referencePack), variants = {}, seen = new Set();
 pack.packId = baseline.baselineId + '-family';
 // A family containing new artwork is never implicitly owner-approved.
 pack.status = 'REQUIRES_OWNER_VISUAL_REVIEW';
 pack.source = {...pack.source, method: 'Shared baseline with artwork-only replacements', baselineId: baseline.baselineId, baselineRevision: baseline.revision};
 delete pack.source.approvedBy;
 for (const manifest of manifests) {
  fields(manifest, ['schemaVersion', 'baselineId', 'baselineRevision', 'variantId', 'label', 'status', 'parts'], 'Artwork manifest');
  if (manifest.schemaVersion !== '1.0' || manifest.baselineId !== baseline.baselineId || manifest.baselineRevision !== baseline.revision) throw Error('Artwork baseline version mismatch');
  if (!id(manifest.variantId) || seen.has(manifest.variantId)) throw Error('Invalid or duplicate variant identity');
  seen.add(manifest.variantId);
  if (manifest.status !== 'REQUIRES_OWNER_VISUAL_REVIEW') throw Error('Replacement artwork requires visual review');
  if (!object(manifest.parts) || !Object.keys(manifest.parts).length) throw Error('Empty artwork replacement');
  const selection = {};
  for (const [slot, replacement] of Object.entries(manifest.parts)) {
   fields(replacement, ['sourcePart', 'textures'], 'Artwork part ' + slot);
   const source = baseline.referencePack.parts[replacement.sourcePart];
   if (!own(pack.slots, slot) || !source || source.slot !== slot) throw Error('Unknown or incompatible source part ' + slot);
   const required = atlasIds(source);
   if (!object(replacement.textures) || JSON.stringify(Object.keys(replacement.textures).sort()) !== JSON.stringify(required)) throw Error('Replacement must supply every required texture for ' + slot);
   const remap = {};
   for (const key of required) {
    const texture = replacement.textures[key], original = baseline.referencePack.atlases[key];
    fields(texture, ['file', 'width', 'height'], 'Artwork texture');
    if (texture.width !== original.width || texture.height !== original.height) throw Error('Artwork atlas dimensions differ from baseline ' + key);
    const newId = `${manifest.variantId}--${slot.toLowerCase()}--${key}`;
    if (own(pack.atlases, newId)) throw Error('Atlas identity collision');
    pack.atlases[newId] = clone(texture);
    remap[key] = newId;
   }
   const part = clone(source), newId = `${manifest.variantId}--${slot.toLowerCase()}`;
   if (own(pack.parts, newId)) throw Error('Part identity collision');
   for (const directions of Object.values(part.timelines)) for (const sequence of Object.values(directions)) {
    for (const frame of sequence.frames || sequence.phases || sequence.views || []) {
     for (const layer of Object.values(frame.layers)) layer.atlasId = remap[layer.atlasId];
    }
   }
   pack.parts[newId] = part;
   selection[slot] = newId;
  }
  variants[manifest.variantId] = {label: manifest.label || manifest.variantId, selection};
 }
 const errors = A.validateAppearancePack(pack, template);
 if (errors.length) throw Error('Invalid assembled character family: ' + errors.join('; '));
 return M.freeze({pack, variants});
}
const api = Object.freeze({atlasIds, validateBaseline, makeArtManifest, buildAppearanceFamily});
scope.AstraeonArtBaseline = api;
if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
