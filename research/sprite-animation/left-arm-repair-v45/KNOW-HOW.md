# v45 — Left free-arm bend repair

User: “แขนซ้ายงอผิดรูปในบางมุมนะ”. Review all eight views; do not assume the user selected one exact direction or frame. The v44 constraints and tool passes do not override this feedback. Work remains local/free, zero provider calls, on the same research branch. All v30–v44 evidence stays frozen.

## What actually went wrong

The old source fixed the free LEFT grip in world coordinates and aimed its elbow pole strongly outward: `shoulder + (.45,0,-.30)`. When the torso bent, the hand did not follow the torso's local frame. The upper arm swung laterally and the elbow bend plane turned away from the body-relative plane expected for this relaxed pickup. In some camera views it reads as an arm folded sideways, even though every bone retained its length and every measured skin ring retained its cross-sectional area.

The old free-arm skin is not proven globally inside-out, and these positions are not declared universally impossible human poses. The failure is the intended action's anatomy/readability, confirmed by user feedback and before/after inspection. Do not call a width/area/length gate an anatomy or acting detector.

## Current source correction

Keep the canonical right collecting arm, target/contact event, torso, head, legs, camera matrices and source timing. Re-author the free LEFT hand and pole in the torso frame:

```
hand = pelvis + lateral*.32
       - torso_up*(.10-.10*depth)
       + torso_forward*(-.015+.125*depth)
pole = shoulder - torso_up*.35 - torso_forward*.12 + lateral*.04
```

Re-solve elbow IK with upper arm .29 and elbow-to-grip .39 (.27forearm + .07hand + .05grip). Recompute wrist/palm on the same distal axis. Rebind this changed arm's actual rest geometry; do not rotate one prepainted arm, relabel left/right, move only colored diagnostic pixels or fit each view independently.

This source has no axial torso twist and actor forward is(0,-1,0), so the authored forward construction is the matching no-yaw torso frame. For a turning/rolling actor, build a full orthonormal torso basis from the actual rig; do not transplant this world-axis shortcut to every motion or body. Eight views here are eight physical cameras around the same world action, not eight differently authored arm poses.

## Actual saved-rig findings

`inspect-arm.py` opens both exact .blend files independently; it never imports the authoring pose function. It evaluates313times across1.3sec, including times between the157bake samples, and compares eight exact anchors against an independently expressed target recipe. Source hips/head/right arm/legs retain the prior v43 world targets.

| Metric | Rejected v44 source | v45 source |
|---|---:|---:|
| Maximum upper-arm lateral-component angle |42.8468°|6.2635°|
| Maximum bend-plane normal deviation from body lateral axis |89.0182°|11.3244°|
| Maximum normal change per313sample interval |1.4394°|0.2072°|
| Flexion range |29.6793–66.5211°|29.6793–66.9952°|
| Minimum adjacent skin-ring center spacing/rest spacing |0.97307|0.97265|

The first angle is a component measurement, not an isolated clinical glenohumeral-abduction diagnosis. The second uses the actual shoulder-line lateral axis and the actual upper/forearm cross product. Normal-sign continuity is checked independently; absolute-axis alignment alone must not hide a180°flip. Degenerate/undefined planes are UNKNOWN/fail, not silently zero.

Current body-relative guards in `arm-contract.json`: lateral-component angle≤20°, plane deviation≤25°, flexion15–100°. These are provisional authored **relaxed free-arm pickup** limits. They are not valid blanket restrictions on raised arms, shields, casting, attacks, shoulder rotation or all human movement. The real old rig must fail this contract; new labels or recolored masks cannot fix its measurements. This is not a benchmarked general anatomical classifier.

## Skin shape and between-key continuity

The actual left arm is a continuous weighted surface. Evaluate current deformed vertices, not only bone positions: closed bind geometry, enabled Armature modifiers, normalized nonnegative weights, bind invariance, ring area and longitudinal ring-center spacing. Ring area by itself missed the original action failure; neither area nor spacing establishes full collision-free volume or elbow anatomy.

At313times, measured source foot drift and right-grip residual peak at about5.86e-5 and5.04e-5world units **in both old and new rigs**. This is approximately0.012 and0.010native render pixels, caused by evaluating between baked keys. Do not call them exact zero or mix them with the earlier157exact-bake measurements. The independent between-bake budget is1e-4world (~0.02px); exact eight anchor errors still use1e-5world, and bone-length precision still uses1e-5. These are distinct precision contracts, not a relaxed visible-foot-jump budget. Current body/right source behavior is unchanged; no per-frame foot patch or normalization is used.

## Image inspection and occlusion

`render-arm-visibility.py` opens the actual saved new rig and creates128real depth-tested captures at eight keys/eight cameras:

1. The LEFT arm meshes are orange, all other meshes opaque black. Occluded arm surfaces stay occluded.
2. A separate explicitly ISOLATED reference hides the other meshes to measure total projected arm area. This is never pasted over the character or presented as visible anatomy.

Visible/isolated pixel fractions are geometric visibility diagnostics. A view with less than20%of the projected arm visible is marked `IMAGE_ANATOMY_UNKNOWN_OCCLUDED`. Even greater visibility is only a partial known-source surface observation, not automatic joint tracking or approval of arbitrary painted anatomy. Waist/legs are not colored orange in this arm-only pass. Color coding diagnoses source ownership; it is not a successful redraw or an anatomical fix.

The actual normal renders use16local path samples instead of v44's32, without a provider or denoiser. Thus do not require shaded RGB equality outside the arm: sampling noise and changed left-arm shadows can change pixels. World targets, actual geometry and the fixed display mapping are the appropriate unchanged-source controls. No current hand-painted sprite or new generated image is involved.

## Fair before/after review

Inherit the exact frozen v44 display matrix, not a new neutral fit. All phases/views use the same matrix and the same clocks. Both8key and27sample previews remain1900ms overall; uniform source anchors and the190/180ms exposure holds differ by up to4.29ms as previously documented. No new timing acceptance is inferred.

`before-after-eight.gif` shows the actual old and new captures at the same27source phases. `left-arm-before-after.png` uses one union-of-source-projections crop per camera, shared by old/new/rest/bend, plus a fixed32pxmargin. Uniform review scaling only, no individual feature fit or sprite repair. The crop is a source-guided inspection window, not a detected anatomical outline.

## Reproduction and scope

Copy this frozen case into a new versioned case before authoring again:

```sh
blender --background --threads 8 --python research/sprite-animation/left-arm-repair-v45/build-character.py -- --all
blender --background --threads 2 --python research/sprite-animation/left-arm-repair-v45/inspect-arm.py
blender --background --threads 2 --python research/sprite-animation/left-arm-repair-v45/render-arm-visibility.py
python research/sprite-animation/left-arm-repair-v45/build-review.py
python research/sprite-animation/left-arm-repair-v45/build-comparison.py
python research/sprite-animation/left-arm-repair-v45/test-arm-gate.py
python research/sprite-animation/left-arm-repair-v45/audit.py --source-only
node research/sprite-animation/left-arm-repair-v45/browser-check.cjs
```

Final-art acceptance remains false: face/hair/costume/proportions/rigid cape and actual runtime sprite replacement layers are not approved. Source improvement does not erase that boundary. The earlier v44 experimental/corrective GLB files are for their exact older motion; do not reuse their export-fidelity receipts for the changed left-arm action. This iteration does not claim a new validated GLB, game import, universal detector, user acceptance or completed factory.

Knowledge basis: direct retained before/after render and saved-rig experiments; v44's retained official Blender EditBone/Armature references and v43's CMU/Spine study remain relevant within their existing scopes. No new clinical paper, game motion dataset or patent implementation is claimed here.

## Isolated-pass counterexample: animated visibility

Visual inspection of the first isolated diagnostic caught a black collectible still present. The renderer reevaluated its animated `hide_render` property, undoing the temporary object hide. Two exact bad images and their scripts are retained under `failed-isolation-prop-REJECTED/`; they are not accepted isolated reference images.

The corrected diagnostic separates actual arm meshes and other meshes into distinct in-memory collections, then excludes the entire occluder collection for the isolated capture. Animation can no longer bring the non-arm prop back into that pass. Full-scene captures restore occluders and retain physical depth. No saved source blend is modified. All isolated opaque pixels must belong to the orange arm surface; a black/non-arm opaque pixel now blocks this diagnostic gate. This is another reason a correct pose record does not establish correct render outputs.

`render-before-arm.py` additionally captures the exact old saved arm alone in all64key/view combinations as a negative shape comparison; it never replaces the frozen old rig or old images. `build-isolated-comparison.py` uses the same fixed camera ROI as the normal comparison. This exposes the actual changed arm geometry even where the outfit/cape hides it in the full actor.

Precision note: the0.012/0.010pxfigures are projection-equivalent upper bounds from measured world displacements and the204.8px/world camera scale, not image-tracked toe/grip pixel measurements. Do not report them as a raster tracking benchmark.
