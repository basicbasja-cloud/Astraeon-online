# Anatomical identity and source-bone continuity review

The user explicitly requests checking generated left/right legs carefully, comparing them with the template bones, measuring continuity and keeping a reusable tool. Use [leg-continuity.py](../scripts/leg-continuity.py) and the [v10 actual review](../../../research/sprite-animation/quality-review-v10/README.md) before promoting any generated motion.

## Primary research studied, 2026-10-12

| Source | Relevant finding | Application and boundary |
| --- | --- | --- |
| [OpenPose / Cao et al., CVPR 2017](https://arxiv.org/html/1611.08050) | Joint localization and connecting limbs are separate problems; contextual limb associations help resolve left/right confusion. | Check connected hip–knee–ankle–toe chains. This tool does not execute the paper's learned PAF model; photo-benchmark results are not evidence for our chibi art. |
| [PoseTrack / Andriluka et al., CVPR 2018](https://arxiv.org/html/1710.10000) | Evaluating individual-frame pose locations is insufficient to evaluate articulated tracking across a video. | Keep anatomical names stable over time and test source-timed transitions and the loop seam. Our internal leg comparison is an adaptation, not the benchmark's person-tracking MOTA or a trained PoseTrack system. |
| [Footskate Cleanup / Kovar et al., SCA 2002](https://graphics.cs.wisc.edu/Papers/2002/KSG02/cleanup.pdf) | Footplant constraints belong to heel/ball intervals; choosing incorrect plant intervals can introduce new artifacts. | Do not infer a plant from the lowest 2D boot pixel. Keep contact review separate from identity checks. The paper's solver allows length variation; our current mesh clearance repair instead retains fixed leg lengths and does not reproduce that full solver. |

The combined checker below is original bounded engineering practice, not a published classifier. No paper establishes error-free image generation or a calibrated accuracy percentage for this art style.

## What the checker actually compares

Source means measured 3D joints from the actual baked original Blender rig, with the fixed export camera. Source author transforms are separately SHA-bound. Keep original source animation, target rig, sampled time, projection and generated pixels as separate evidence.

Explicit source map: hip=`thigh_*`, knee=`calf_*`, ankle=`foot_*`, distal toe=`ball_leaf_*`. The ball joint is **not** the distal toe. Manual boot contour landmarks remain approximate proxies for internal joints; record uncertainty. Do not copy the source points into artwork annotations and call those independently detected joints.

On `init`, all generated-art points start unknown. A reviewer traces visible chains and labels anatomical sides. Use costume ownership, attachment paths and the source view; screen-left is not anatomical-left. Mark covered hips/knees as estimated and genuinely hidden ankles/toes as unknown. Keep identity unconfirmed until reviewed. The original v10 checker supported SE only; v11 now projects all eight physical facings. Read [occlusion-image-review](occlusion-image-review.md) for the mandatory actual-image crossing and trace gates, mixed-chain comparisons, and the confirmed failures that coordinate fits cannot override.

The CLI checks artwork hashes/canvases, source motion hash, capture and GLB identities, baked `.blend` hash and saved-pose replay hash. It recomputes each reference projection and verifies actual source times; changing the stored skeleton cannot manufacture a passing score.

One positive scale is fitted from complete projected chain lengths across the clip, without rotation/reflection or per-key scale. This is diagnostic calibration; it does not alter artwork. Compare pelvis-relative annotated joints with the corresponding source joints, and compare that cost with exchanging the full leg identities. A better exchanged fit is a **possible label/pose swap**, not proof of semantic identity when clothes hide the hip attachments.

For continuity, compare same-named displacement vectors against the source displacement at the same elapsed time. Include last→first using the true cycle duration. Large source-relative residuals or better exchanged-next-frame fits raise review flags. Naturally crossing legs are allowed because labels follow the skeleton, rather than sorting points by screen position or following the nearest foot.

Default provisional budgets at 512 square: 16 px pose residual, 8 px exchanged-fit margin and 60 px/s trajectory residual; scale budgets proportionally for other master sizes. These are review settings, not RO standards or scientifically calibrated accuracy bounds. Save raw errors alongside errors after subtracting declared landmark/hip uncertainty. Large uncertainty must not hide a discrepancy: raw differences receive their own review flags.

Report observed coverage, estimated/observed measurement coverage and measured-point budget fractions separately. **None is anatomical correctness probability.** Unknown points cannot pass; unconfirmed identity and uncertainty keep the review blocked. World foot-lock, hidden anatomy, actual weight transfer and production release are outside this check and remain explicitly unverified. Pelvis-relative comparison alone does not test whole-body root jitter.

## Commands

Run from repository root. The source motion folder must include the corresponding original `.blend` and `saved-rig-check.json`.

```bash
python skills/modular-eight-direction-sprites/scripts/leg-continuity.py init \
  --motion research/sprite-animation/walk-test-v9/motion.json \
  --frames research/sprite-animation/quality-review-v10/master/frames \
  --keys 0,10,20,30 --out /tmp/new-leg-annotations.json

python skills/modular-eight-direction-sprites/scripts/leg-continuity.py check \
  --case research/sprite-animation/quality-review-v10/leg-annotations.json \
  --out /tmp/new-leg-check --html /tmp/new-leg-review.html

python -m unittest discover -s skills/modular-eight-direction-sprites/scripts/tests -q
node skills/modular-eight-direction-sprites/studies/walk-test/verify-leg-ui.cjs
```

The standalone HTML embeds the actual images, reference and provisional annotations. It provides joint selection, pointer editing, visibility/uncertainty, playback, quarter speed, onion skin and JSON import/export. Changes invalidate the old report; export annotations and rerun the CLI. An overlay can align the template to the marked pelvis for chain inspection; this never changes exported art or proves correct ground registration.

`init` writes a new annotation file and refuses overwrites. `check` regenerates reports/overlays in its output directory. Review cases use repository-relative paths when initialized with relative arguments; the single HTML file is portable without those paths. Do not treat the browser export-control test artifact as a real art annotation.

## Preserve visual quality independently

The user's latest three supplied images are the direct quality reference. The v9 fixed 128-square proposal is superseded for this quality review by a 512-square detailed master. Retain beautiful face/hair, layered bronze, patterned amber cloth, ivory/teal pieces and textured leather. Display zoom does not restore detail erased during export; generate at sufficient resolution and preserve full-color RGBA masters.

Use `studies/walk-test/pack-quality.py` for a verified square 2×2 output. The tool returned 1254 rather than requested 1024 pixels; inspect actual size. Preserve the raw sheet, use one global scale, and record any shared grid-row correction separately from anatomical correction. The particular -20 row offset in this study is not a factory default.

Only multiply items/views/actions after accepting motion and identity in the final drawn pixels. A beautiful flattened redraw, a successful original rig test, or source-guided points cannot supply complete painted hidden replacement parts.
