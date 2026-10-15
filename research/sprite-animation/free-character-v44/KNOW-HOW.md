# v44 — Free local rig route

User steering (2026-10-15): “ไม่ใช้เครดิต ใช้ฟรีเอานะเรา ทำต่อเลย”. The previous paid Tripo proposal is closed/declined. No asset-generation provider was called, no image/model upload, credential/account lookup, paid CLI execution, or spend. Native ImageGen was also not called this iteration. This does not require payment to proceed.

## What changed

v43's preferred common-hinge arm skin was a real deforming arm, but the rest of its mannequin was rebuilt per exposure. v44 authors original local geometry in Blender and binds every character mesh to one real armature. There are two authoring/export ownership groups: `body_outfit` and `complete_head`. Internal sleeves/limbs/trim/hair/face meshes are not additional player equipment slots. Continuous arm and leg surfaces blend adjacent bones; rigid armor, boots, face, hair and clothing details have explicit bone ownership. This is an original colored 3D blockout, not a replacement for the approved painted character.

No rejected own arm artwork, old own attack pose, third-party game sprite, or rejected rear modeling reference was used as a successful character texture. The approved v39 neutral drawing is displayed as an unchanged visual target and supplies the standing display height; its pixels are not projected onto the new model. The original concept attachment's missing local bytes remain missing, so no fabricated concept hash or exact concept proportion score is reported.

## 1. Authoring transforms must survive actual Blender evaluation

Use a nonzero head–tail direction before assigning an EditBone matrix; set length explicitly, then compare the saved `matrix_local` against the intended rest frame. Blender's API states that `EditBone.matrix` covers head position/direction/roll and **does not include/support bone length/size**. `length` moves the tail. Our initial zero-length construction produced a real basis mismatch; retained file `attempt1-bind-axis-REJECTED/original-character.blend` reproduces it. Never infer correct binding from a plausible list of world joint coordinates.

For a rest-space vertex v, verify the actually evaluated neutral point equals the original point: `p_neutral - p_rest`, in common world space, under the dependency graph. Also verify real pose bone heads/tails against the intended world targets. Core/foot bones must have their Y axes along the intended bone, not a convenient body authoring axis. In this implementation torso-local mesh construction uses its own rest coordinates, independently from the bone frame; they must not be confused.

Keep the common elbow-plane basis developed in v43. The hand inherits the forearm frame for this pickup. A zero-pronation test does not establish full wrist pronation, finger anatomy, arbitrary attacks or universal retargeting. Exactly straight hinges still need a transported/rest fallback before expanding this adapter to arbitrary clips.

## 2. A vertex-group label is not a live skin connection

`bpy.ops.object.convert(target='MESH')` works on selected objects. Our curve conversion unintentionally included previously selected weighted meshes, baking/removing their Armature modifiers. Those objects still had normalized vertex groups. A weight-only gate passed while boots, neck skin, face details and cape trim stayed behind during motion.

The retained `attempt4-unbound-details-REJECTED` file proves this. `diagnose-negative-cases.py` reopens both real rejected blends. The unbound-details case has a nearly correct bind pose and **10 actual missing deformation modifiers**. The fix deselects all other objects before converting each new curve. The production check now requires exactly one enabled intended-armature modifier per character object, with normalized nonnegative weights and actual evaluated bind/dense pose checks. A modifier-presence check alone still would not prove geometry/anatomy correctness.

## 3. Rendering has its own authoritative clock

A manually assigned pose can be reset by animation evaluation when rendering the scene at the wrong current frame. Our first full-bank attempt rendered a standing pose for the deep key. `attempt3-frame-evaluation-REJECTED/S-00.png` and `S-03.png` are actual identical wrong-clock captures, not synthetic negatives.

Set `scene.frame_set(frame, subframe=...)` before each pose/capture. Bake authored poses at their actual times and explicitly check real hand bones **after** each render. The saved rig is independently reopened and evaluated by `inspect-saved-rig.py`; it does not import or execute the model authoring script. Source records, saved animation, renderer time and current PNG bytes are separate evidence.

## 4. Add motion samples through targets and IK, not independent anatomy

This is the v43 target-conditioned pickup, not a newly researched attack or unchanged preset. Eight anchor poses are retained. Monotone cubic target curves interpolate depth, torso bend and right-hand grip; endpoint velocities are zero and internal slope reversals have zero tangent. Re-solve fixed-length leg and arm IK at each time. Do not interpolate rendered frame positions, independently resize parts, relabel limbs after occlusion, or add intermediate generated images without source checks.

Bone animation contains a dense local bake plus all exact eight anchor times. The independent inspector samples 157 times, checks bone lengths, feet, held-object socket and hinge axes, and measures actual deformed ring cross-sectional areas. Closed surfaces/ring areas are not a proof of total body volume, collision-free cloth, trained acting, or accurate generated anatomy. The source remains one specific pickup with zero wrist pronation.

The 8-exposure reference-clock preview totals 1900ms. The dense comparison uses 27 drawings: 26 intervals ×50ms plus a 600ms final hold, also1900ms. Its unique drawing rate is20Hz, not27fps and not a new RO frame-count claim. Extra drawings are an experiment, not user approval of a new timing policy. GIF repeats for inspection; the HTML player plays the pickup once.

## 5. Physical cameras and one calibration

The same world geometry/targets feed the eight retained v43 physical cameras, with equal orthographic scale. No raster mirroring. Body proportions do not change per direction or pose. The actor-only S neutral is calibrated once to399px/floor480 and horizontal center224.5; the separate collectible is excluded using a full-scene, depth-tested emission ID render. The exact same matrix is used for every camera and phase. No per-frame, head, limb, depth, or view fitting.

Camera-dependent silhouette dimensions legitimately vary, and matching one standing height is not matching the approved family. The displayed v39 drawing is a different view/protocol, so arm/head/boot width comparisons are visual observations, not exact anatomical error percentages. More accurate materials and original-style modeling/painting are still required.

## 6. Current image checks have limited authority

Eight key poses have actual depth-tested ownership captures: blue canonical RIGHT, orange LEFT, green complete head, gray torso/clothing, red item. They render the same evaluated meshes and depth occlusion; no skeleton is painted over an inconsistent image. This supports debugging the current known geometry, not automatic anatomy classification of arbitrary painted sprites.

The audit binds all raw PNGs by SHA256, verifies independent world-to-camera projections, observes actual green-head surface centroid movement to reject a static render, and preserves current source/image separation. A green surface centroid is not a detected head joint. The overlay is source-joint projection only, not a claim of image tracking accuracy. Missing/hidden anatomical cues in arbitrary redraws remain UNKNOWN; earlier v43 painted-owner failure remains rejected.

## 7. Visual limits and next art work

The original colored mesh is deliberately labeled BLOCKOUT. Its face/hair, armor, cloth and flat cape do not match the approved hand-painted quality; the cape is a weighted shell, not simulated cloth. Dense samples may make the joint path smoother but cannot approve acting or fix artistic stiffness. No user art acceptance, production sprite bank, proven 2D replacement-layer compositor, engine import or factory completion is claimed.

The `.blend` supports two named authoring collections. The experimental GLB preserves skinned character geometry, group extras and an animation bake; the separate collectible/visibility/store event are intentionally not exported as finished gameplay. Local animated rendering does not imply GLB engine playback validation. The next free iteration should refine the same model's proportions, head/hair/face design and garment topology against approved matching-view artwork; test cape/body intersections and dense pose extremes before treating renders as redraw guides. Do not add paid generation or substitute the rejected art to claim completion.

## Reproduce locally

From repository root, in a **new copied case** after this evidence is frozen:

```sh
blender --background --threads 8 --python research/sprite-animation/free-character-v44/build-character.py -- --all
blender --background --threads 2 --python research/sprite-animation/free-character-v44/inspect-saved-rig.py
blender --background --threads 2 --python research/sprite-animation/free-character-v44/diagnose-negative-cases.py
blender --background --threads 2 --python research/sprite-animation/free-character-v44/export-character.py
python research/sprite-animation/free-character-v44/build-review.py
python research/sprite-animation/free-character-v44/test-audit.py
python research/sprite-animation/free-character-v44/audit.py --source-only
node research/sprite-animation/free-character-v44/browser-check.cjs
```

Use installed Blender/Python/Pillow/NumPy/Chromium. No downloaded executables or model weights. `game-dev` capability discovery found no installed executable; no canonical Game Development Studio package or its verification is claimed. The optional local Blender denoiser was unavailable; rendering uses local sample accumulation instead. The broad user instruction authorizes these local writes; no further paid-provider approval is inferred.

## Primary sources actually fetched

- [Blender4.3 EditBone API](https://docs.blender.org/api/4.3/bpy.types.EditBone.html): matrix excludes length; explicit length and roll semantics. Full retrieved HTML retained locally.
- [Blender4.3 Armature modifier](https://docs.blender.org/manual/en/4.3/modeling/modifiers/deform/armature.html): target armature/vertex groups, Preserve Volume uses quaternions and has an angular discontinuity near180°. It is not a blanket volume/anatomy guarantee. Full HTML retained.
- Existing v43 primary Spine weights/IK and CMU26_09 data/reader remain frozen and their earlier scopes apply. No new motion-capture data, paper model or research-patent implementation was acquired this iteration.

The browser search tool returned402 for these docs; direct public HTTP retrieval succeeded under the network-capable tool environment. Only public documentation was downloaded, with no account/paywall action. Primary-source text plus locally reproduced failures supports these rules; it does not prove a universal error-free sprite factory.

## 8. Actual GLB roundtrip counterexample

`inspect-glb.py` confirms the first GLB has115 skinned character mesh nodes, one skin, two ownership extras, normalized weight accessors and a1.3sec clip. Those nine static checks pass. `check-glb-roundtrip.py` then actually reimports it and compares evaluated surfaces at source frames1/18/40 with an explicitly derived imported-action start offset. The imported armature uses LBS (`preserve_volume=false`), while the Blender source uses DQ. Peak leg vertex displacement is0.03203 world units; the unsampled shell is also missing the cape's0.008 thickness. Thus static validity does not mean surface fidelity. The initial GLB remains EXPERIMENTAL/ROUNDTRIP_FAIL; it is not the authority for the GIFs. Symmetric nearest-vertex distance here is a bounded sampled comparison, not continuous triangle Hausdorff distance or engine rendering proof.

## 9. Local sampled corrective export

The second local exporter measures actual DQ vertex positions on the40integer-frame bake before changing any skinning. For each mixed vertex, let M be its weighted LBS matrix at that sample and q the measured DQ point in mesh space. Store a corrective pre-skin shape point `M^-1 q` and key that target at the corresponding sample. It explicitly rejects near-singular M. This applies only to the five mixed-weight surfaces; rigid accessories need no correction. Bake the cape's shell at rest in memory while preserving its bone weights; the original `.blend` is never overwritten.

The local evaluation of all40corrected samples is within8.9e-7world units of the DQ source. Actual glTF reimport is then checked separately by `check-glb-roundtrip.py -- --corrected`; read `corrective-glb-roundtrip.json` for the measured imported surface error, exact sample times and all per-object values. This is still sampled vertex fidelity in Blender, not arbitrary-between-sample equivalence, triangle-surface proof or game-runtime validation. Skeletal blending with another action can invalidate the correction and needs a new bake/test. Static and roundtrip receipts are separate.

The first corrective export still had six independent animation clips because Blender's SCENE mode defaults to splitting objects. It did not play the five morph curves with the armature as one action; actual roundtrip remained wrong. That exact GLB and failed receipts are preserved in `corrective-split-actions-REJECTED/`. Set `export_anim_scene_split_object=False`, verify **one synchronized animation** in the actual GLB, and then reimport. Do not rename the six-clip export to call it fixed.

Extra local commands, after the first GLB counterexample:

```sh
blender --background --threads 2 --python research/sprite-animation/free-character-v44/export-corrective-character.py
python research/sprite-animation/free-character-v44/inspect-glb.py --corrected
blender --background --threads 2 --python research/sprite-animation/free-character-v44/check-glb-roundtrip.py -- --corrected
```

This corrected portable export is an experimental source asset. It does not upgrade the blockout's art quality, approve head/body swaps, implement inventory events, or make the factory complete.

Timing precision: the dense source bake uses uniform anchor timesi/7×1300ms, while the8hold preview uses cumulative190/180ms exposures; both total1900ms but anchor timing is not identical (maximumdifferenceabout4.29ms). No exact exposure-to-source-clock identity or new timing approval is inferred.
