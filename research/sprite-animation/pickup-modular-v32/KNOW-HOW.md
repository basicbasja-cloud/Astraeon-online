# From failed redraw to reusable modular motion

## What changed, and why it worked

The v31 whole-character image generator repeatedly changed the feet and recovery pose even with a calibrated source sheet. Those failures are durable evidence: more detailed prompts did not create controllable skeletons. In v32 the generator supplies original **appearance parts**. A deterministic runtime supplies joint ownership, timing, constraints and transforms. Rendered pixels still undergo separate image checks.

This is an authored 2D rig, not a recovered skeleton inside a generated image. Its usefulness is that every thigh, shin and boot has a persistent identity and explicit parent connection. An overlapping knee may be hidden under a tabard without changing which hip owns the leg. The proof is the complete isolated asset plus its stored binding and render matrix, not blue/orange recoloring or the location of the teal cloth.

This execution applies the previously read [Spine weights](https://esotericsoftware.com/spine-weights), [Spine IK](https://esotericsoftware.com/spine-ik-constraints) and [Godot Skeleton2D](https://docs.godotengine.org/en/stable/classes/class_skeleton2d.html) principles. Their acquired sections/receipts remain in [v31](../pickup-pilot-v31/targeted-source-receipts.json). No Spine/Godot project or new paper implementation was run: this pilot uses native Canvas transforms and analytic two-bone IK. Learned ideas and our executed implementation have different provenance.

## 1. Choose a source family before painting

Use a source with verifiable rig names, timestamps and license. Here the creator's CC0 [license](../joint-tracking-ro-v30/preset-source/KayKit-License.txt) accompanies the [actual GLB](../joint-tracking-ro-v30/preset-source/Rig_Medium_General.glb); [source.json](../pickup-pilot-v31/source/source.json) binds the clip, camera, 23 bones, eight sample times and eight mesh-render hashes. The action lasts 1.3 seconds. The source's `head` bone is a head-mount driver, not a nonexistent neck bone. Preserve chest/head distinctions when mapping.

This motion has a planted two-foot support policy. Fixed boot pieces are appropriate for this family. They would be wrong during a walk step, jump takeoff or dash release; those require a stance/swing/contact schedule and actual moving footwear poses. Do not reuse this contact policy blindly just because a GIF looks stable.

Keep the prior rejected slash sheets/rigs out of new conditioning. The only own motion image used in atlas generation was v31 frame0 for neutral appearance, not its failed motion. Exact accepted W frame0 supplied costume/style only. Generation inputs and SHA values are in the ledger.

## 2. Generate complete parts and inspect receiving joints

The first real atlas contains 16 authored slots: head+hair, torso/scarf, cape, teal panel, paired upper/forearms, paired thighs/shins/feet and two ivory tabards. It has explicit anatomical right/far and left/near drawings in this fixed view. No mirror operation synthesizes the opposite side.

Inspect actual atlas packing; requested cell geometry is not evidence that the output obeys it. The first 1254-square atlas uses explicit empty-gutter panel crops. Later landscape limbs use explicit 1536×1024 panel bounds. Crop origins stay part of the binding record. Never silently fit every full sprite to a new box.

Two important art failures required genuine image edits:

1. The first torso already had pauldrons. Adding articulated upper arms doubled shoulder armor. A new torso image removes embedded pauldrons while preserving complete navy overlap receivers.
2. Open black socket ellipses at elbows/ankles read as detached costume pieces. A new eight-piece limb atlas paints **closed, filled** receivers, with navy cloth/brown shaft extending under the adjoining piece. Joining empty holes is not solved by passing a bone endpoint test.

Asset normalization selects each panel's largest connected alpha component, removing detached background specks/neighbor fragments. It keeps retained pixels unchanged and records discarded counts. Raw imagegen outputs remain intact. This is one shared part-extraction operation, not per-frame anatomy editing. It assumes one isolated connected piece per panel; a future split accessory must have its own component contract rather than disappearing silently.

## 3. Bind once, pose from source, then check real matrices

The authored rest pelvis is [192,309]. Source pelvis X displacement is retained; its Y displacement is scaled2.8 to suit this body's compact proportions. The source head-to-pelvis vector drives the authored upper-body/head mount with a fixed rest basis. Source wrist deltas have one shared1.35scale. These adaptations are deliberate art direction, not exact source joint recovery.

Foot anchors are fixed at right[165,429] / left[241,450]. Thigh/shin lengths are right68/45 and left78/59 pixels. Analytic IK keeps both links fixed and preserves one knee-bend branch. Unreachable chains throw an error instead of silently stretching. Moving pelvis/knees/torso/arms still produce the crouch; locking the complete lower half would erase the action.

Limb affine matrices map each asset's authored pivot and endpoint to its own chain. Their determinants must remain positive. Width scale is constant per part; no per-frame fit is applied. Shoes draw below shins so filled shafts cover receivers; far arm draws behind torso, near arm in front. A shoe pivot belongs at the gold ankle-cuff center, not the top of its added receiving shaft. Using the wrong receiver pivot initially placed the boot outside the canvas; correcting the shared bind repairs every pose without translating any final frame.

Verify the **actual exported matrices**, asset SHA values, endpoint positions, bone lengths, owner assignments and branch signs. A colored rig overlay is useful for inspection but cannot be the only proof. A wrong-leg parent matrix must fail even if the visual-review JSON was previously positive.

## 4. Observe rendered pixels independently

The new rigid-surface observer takes frame0 texture patches, a fixed search region and, for the cuff, frame0 isolated alpha. It searches rotations−80..80° at2° steps. Later joint coordinates, predicted positions and predicted rotations are absent from its inputs. It checks visibility, texture similarity and positional ambiguity. Missing texture, repeated indistinguishable patches or stale hashes produce unknown/error, not invented joints.

Toe centers are screen-far[118,465] and screen-near[198,489]. These names do not determine anatomical side. Their whole RGBA patches are byte-identical across eight frames, and independent matches return zero X/Y displacement. The cuff seed[118,291] is the visible painted glove/bracer junction, not a measured exposed wrist bone. All seven held-out matching errors against the renderer's authored point are under0.782px. This establishes matching accuracy only for this exact rigid texture, angle range and view; v30/v31 general redraw trackers are not suddenly accurate.

Use unchanged6px support and0.25source-phase budgets. Source phase calibration uses frames0/3; exclude them from the held-out phase metric. The new maximum phase discrepancy is0.005313. The old v31 case still gives55/62px shoe drift and a frame6 early-recovery warning. A narrower new claim does not rewrite the historical failures.

Do not promote static toe pixels to force, sole pressure or 3D balance evidence. Do not infer hidden knee/hip image coordinates from the clothing. This pilot instead has authored part ownership, mechanical binding proof, visible texture evidence and visual review as separate inputs.

## 5. Keep clocks and visual acceptance explicit

Eight native source keys remain at0..1.3seconds. Source GIF durations are190/180/190/180/190/180/190/600ms, summing1900ms; centisecond quantization is explicit. Game review uses100ms for seven intervals plus600ms terminal hold:700ms active,1300ms total. Same poses, different playback. Both GIFs are formatted at192×256 from untouched384×512RGBA masters. Native Canvas review stays at full resolution. The first and last full RGBA frames are identical, avoiding a fabricated return jump.

Inspect the ordered contact board, lowering/recovery, part seams and live Canvas playback. Save the exact eight image hashes in a separate visual receipt. **Packaging must not issue visual acceptance for changed images.** Numeric pass and artistic review combine only in the bounded motion receipt; the general surface checker still leaves hidden anatomy/contact/production unapproved.

## 6. Reproduce and extend safely

Run from the repository root. Dependencies used: Python/Pillow12.3, NumPy2.3.5, OpenCV4.11; Node with Playwright and Chromium. In this executor the optional vision wheels are under `/tmp/astraeon-vision-deps`, so set `PYTHONPATH=/tmp/astraeon-vision-deps` for Python commands using OpenCV/NumPy. Normal installed environments do not require that path. Raw generated images are preserved; reproduction does not call a paid provider or generate new art.

```bash
python research/sprite-animation/pickup-modular-v32/extract-parts.py
python research/sprite-animation/pickup-modular-v32/repair-parts.py
python research/sprite-animation/pickup-modular-v32/build-runtime.py
node research/sprite-animation/pickup-modular-v32/export-runtime.cjs
node research/sprite-animation/pickup-modular-v32/export-observer-input.cjs
python research/sprite-animation/pickup-modular-v32/package-review.py
python research/sprite-animation/pickup-modular-v32/check-pixels.py
node research/sprite-animation/pickup-modular-v32/check-runtime.cjs
python research/sprite-animation/pickup-modular-v32/build-review-case.py
python skills/modular-eight-direction-sprites/scripts/modular-motion-review.py --case research/sprite-animation/pickup-modular-v32/review-case.json --root . --out research/sprite-animation/pickup-modular-v32/motion-review.json
python -m unittest discover -s skills/modular-eight-direction-sprites/scripts/tests -p test_modular_motion_review.py -v
python research/sprite-animation/pickup-modular-v32/audit-evidence.py
```

If pixels change, `build-review-case.py` stops until the new artwork is genuinely inspected and a new bound visual receipt is written. Keep old acceptance/rejection evidence. Retest after any source/bind/part/timing change. Start other characters by authoring their own complete receivers, camera basis, proportions and calibrated visible texture patches; source identity names do not infer their geometry.

Next factory work: real head/hair separation and swap proof; one additional view with original perspective-specific limb art; then locomotion stance/swing transfer. Weapons still require appropriate per-pose projected blade/guard/hilt drawings when their plane changes, not one flat sword spun in screen space. This body's rigid posing success is not a license to ignore weapon perspective or to resurrect rejected slash acting.
