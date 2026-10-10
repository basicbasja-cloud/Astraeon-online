/* Deterministic geometry diagnostics, deliberately not a visual approval oracle. */
(function(scope) {
'use strict';
const A = scope.AstraeonCharacterAssembly || (typeof require === 'function' ? require('./character-assembly.js') : null);
const point = p => Array.isArray(p) && p.length === 2 && p.every(Number.isFinite);
function worldPoint(layer, p) {
 if (!point(p) || !point(layer.pivot)) throw Error('Invalid local landmark');
 const world = A.composeTransform(layer.transform, {x:p[0]-layer.pivot[0], y:p[1]-layer.pivot[1], rotation:0, scale:1});
 return [world.x, world.y];
}
function inspectGrip(sample, tolerance = 2) {
 if (!Number.isFinite(tolerance) || tolerance < 0) throw Error('Invalid grip tolerance');
 const weapon = sample.layers.find(l => l.layer === 'MainHand');
 if (!weapon) return {status:'NOT_EQUIPPED', errors:[], visualApproval:false};
 const pose = weapon.weaponPoseFrame;
 if (!pose) return {status:'UNMEASURED', errors:['WeaponPoseSet landmarks missing'], visualApproval:false};
 const errors = [];
 for (const key of ['equipmentAnchor','gripContactPoint','weaponTip','handContactPoint']) {
  if (!point(pose[key])) errors.push('Invalid ' + key);
 }
 if (errors.length) return {status:'INVALID', errors, visualApproval:false};
 const grip = worldPoint(weapon, pose.gripContactPoint);
 const tip = worldPoint(weapon, pose.weaponTip);
 const equipment = worldPoint(weapon, pose.equipmentAnchor);
 const distance = Math.hypot(grip[0]-pose.handContactPoint[0], grip[1]-pose.handContactPoint[1]);
 if (distance > tolerance) errors.push('Visible grip misses independently authored hand contact');
 // The two landmarks have different meanings but may legitimately coincide.
 // Numerical inequality cannot establish independent visual measurement.
 return {status:errors.length?'INVALID':'GEOMETRY_WITHIN_TOLERANCE', errors, distancePixels:distance,
  equipment, grip, hand:pose.handContactPoint.slice(), tip, perspective:pose.perspectiveVariant,
  visualApproval:false, limitation:'Equal points do not prove painted anatomy, handle contact, perspective or occlusion.'};
}
function auditSequence(assembly, action, direction, appearance = {}, {gripTolerance = 2, tipStepWarning = 90} = {}) {
 if (!Number.isFinite(tipStepWarning) || tipStepWarning <= 0) throw Error('Invalid trajectory threshold');
 const frames = assembly.motion.template.actions[action]?.directions[direction]?.frames;
 if (!frames) throw Error('Unknown action or direction');
 const records = frames.map((f,i) => ({frame:i, durationMs:f.durationMs,
  ...inspectGrip(assembly.sample(action,direction,0,{frameIndex:i,appearance}),gripTolerance)}));
 const warnings = [];
 for (let i=1;i<records.length;i++) if (records[i].tip && records[i-1].tip) {
  const delta = Math.hypot(records[i].tip[0]-records[i-1].tip[0], records[i].tip[1]-records[i-1].tip[1]);
  if (delta>tipStepWarning) warnings.push({from:i-1,to:i,tipDeltaPixels:delta,reason:'Inspect sword arc; diagnostic does not change poses'});
 }
 return {action,direction,records,warnings,visualApproval:false};
}
const api = Object.freeze({worldPoint,inspectGrip,auditSequence});
scope.AstraeonProductionValidation=api;
if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
