# Occluded leg ownership: inspect the drawing, not only its joint coordinates

Iteration 11, 2026-10-12. The user identifies SE pose 2 as swapped, then rejects the current overlapping-leg drawings more broadly. They require improved tools and a fresh check **after** the fix. Keep that rejection bound to the old image bytes; new pixels require independent inspection and annotations.

## Why the older comparison missed the problem

The source rig can be correct while the paintover joins a thigh to the other shin. Close projected knees and covered hips make whole-chain swapped-coordinate tests inconclusive. Subtracting broad annotation uncertainty can make an incorrect connection look numerically acceptable. The original tool did not identify leg semantics in the drawing. Never present a low residual as proof that a generated image has no leg swap.

## Sources read in this iteration

The [fetch audit](../../../research/sprite-animation/eight-direction-v11/evidence/research-source-audit.json) records source URLs, retrieved-byte SHA256 and the portions actually read. These techniques motivate the checks; their learned systems were **not executed** on our sprites.

| Source and reading scope | Finding adopted | Boundary |
| --- | --- | --- |
| [OpenPose, CVPR 2017](https://arxiv.org/html/1611.08050), introduction and association sections | Locating joints and associating connected limbs are distinct problems; occlusion complicates association. | Review visible thigh–knee–shin connections, not independent nearest joint locations. Our pixel traces are manual; no learned PAF network runs here. |
| [DensePose, CVPR 2018](https://arxiv.org/abs/1802.00434), abstract; [official chart documentation](https://github.com/facebookresearch/detectron2/blob/main/projects/DensePose/doc/DENSEPOSE_IUV.md), overview/confidence sections | The official representation distinguishes body surface regions and UV coordinates; segmentation confidence is separate from location confidence. | Render true owner regions from our original weighted geometry. These are source labels, **not** DensePose predictions or labels recovered from generated art. No photo-trained model accuracy is assumed for chibi sprites. |
| [CoTracker](https://arxiv.org/abs/2307.07635), abstract; [official repository README](https://github.com/facebookresearch/co-tracker) | Joint point tracking can use temporal dependencies; example API returns tracks and predicted visibility separately. | Retain ownership over the loop and explicit visibility. Sparse independently redrawn poses are not a continuous recorded video; tracking a similarly colored boot would not establish its anatomical owner. No model/weights are used. |
| [COCO evaluation implementation](https://github.com/cocodataset/cocoapi/blob/master/PythonAPI/pycocotools/cocoeval.py), `computeOks` | The implementation selects labeled keypoints with `vg > 0`; that does not distinguish every labeled point as directly visible. | Keep observed/estimated/unknown separate in our custom annotations. We do not report COCO OKS or treat missing observations as correct. |

## Executed source proof and image gate

1. Reopen the actual baked original v9 `.blend`. Render source times 0, 10, 20, 30 at all eight physical rotations. Classify the fresh mesh's R/L legs by bone weight groups. Never mirror this asymmetric character.
2. For each pose render full-scene visible owners and complete isolated right/left leg geometry: **32 poses, 96 passes**. Non-antialiased IndexOB labels are background 0, R 1, L 2, other occluders 3. Blue means anatomical R, orange L. Stored colored guides derive from integer IDs, not painted masks or screen sorting.
3. Intersect isolated R/L silhouettes, then retain pixels whose visible full scene actually belongs to R or L. Group visible crossing regions of at least 32 source pixels. Current fixture contains **36 required regions**. Tiny overlaps below that budget and garment-covered intersections are not proven by this gate; ordinary chain/hidden anatomy review still applies.
4. Condition the redraw with visible owner colors plus the gray source poses and the permitted quality reference. Preserve raw generation. A prompt or conditioning sheet does not establish success.
5. SHA-bind NEW painted pixels, source blend, actual source motion, view, timestamp and owner maps. Mark painted joints independently. Covered internal joints remain estimated/unknown; never copy source landmarks as detected paint landmarks.
6. For every required crossing, select the actual corresponding point on the painted image, trace the visible foreground leg from thigh through the connection toward the shin with at least three points, and independently confirm the owner and trace. The CLI reads actual RGBA: marked points need opaque support, traces need at least 80% sampled foreground support and must pass within 16 px of the selected crossing at 512 square. These are **provisional evidence budgets**, not calibrated anatomy accuracy. Alpha support proves occupancy only; semantic tracing is human review.
7. An unknown foreground, missing/unsupported trace or unconfirmed review blocks the gate. Confirmed owner mismatch or a confirmed image-specific reviewer error rejects it. Import cannot erase a confirmed error in the same image. Source event counts and expected owners cannot be changed to match a drawing.
8. Recheck same-named chains at true source times, including the loop seam. The coordinate tool now checks all 16 combinations of hip/knee/ankle/toe side exchange with raw residuals. If source R/L separation is covered by declared point uncertainty, identity is ambiguous, even if a whole-chain fit looks good. These counterfactual comparisons diagnose ambiguity; they do not recover image semantics.

The additional teal-palette check reads actual lower-body color pixels and flags a centroid that crosses the pelvis/cell root. It needs visual confirmation: natural movement, perspective, clothing changes or a fixed cell root can cause false positives. It detects an appearance discontinuity, not left/right anatomy. The revised NE attachment mistake is independently confirmed in the images; the W flag is still unresolved.

## Actual result and next correction rule

[Eight-facing v11 review](../../../research/sprite-animation/eight-direction-v11/README.md) preserves all initial and revised images. The original user-rejected SE second pose remains **REJECTED**. The user also supplied the revised E third pose as a new confirmed leg swap: its actual image-bound rejection is retained separately. A further E correction has new unknown annotations and one independently traced near/right leading chain. Three local foreground chains in revised SE also have manually traced source-owner matches, but covered hip connections and full motion remain unapproved. **32 of 36 source crossings remain unresolved** across the eight views. Revised NE is rejected because the asymmetric left-hip cloth changes attachment side. The new E correction still deviates from the source leg angle/placement. All complete-art/continuity/painted modular/release gates stay blocked.

When revising a rejected drawing, retain the old case and create a new image-bound case. Do not transfer old confirmed traces to new bytes. Reinspect visible connection paths and the whole loop; do not reduce uncertainty or delete crossings to manufacture a pass. If a connection cannot be resolved, make the staging/silhouette more readable or author it manually with an artist, then repeat the image check. More frames or an attractive surface finish cannot repair unknown ownership.

Current tool checks are bounded original engineering practice. They do not guarantee error-free generation, verify hidden anatomy, establish foot support/COM balance or provide complete interchangeable painted hair/equipment layers.

## Reproduce

```bash
blender -b -t 4 --factory-startup --python-exit-code 2 \
  --python skills/modular-eight-direction-sprites/studies/walk-test/export-leg-owners.py -- \
  --blend research/sprite-animation/walk-test-v9/original-modular-walk.blend \
  --output /tmp/new-source-owner-renders

PYTHONPATH=/tmp/sprite-render-deps python \
  skills/modular-eight-direction-sprites/studies/walk-test/pack-leg-owners.py \
  --renders /tmp/new-source-owner-renders --output /tmp/new-source-owners

python skills/modular-eight-direction-sprites/scripts/leg-continuity.py init \
  --motion research/sprite-animation/walk-test-v9/motion.json \
  --frames research/sprite-animation/eight-direction-v11/master/SE/frames \
  --facing SE --keys 0,10,20,30 \
  --owners research/sprite-animation/eight-direction-v11/source-owners/owner-index.json \
  --out /tmp/new-revised-image-annotations.json

python skills/modular-eight-direction-sprites/studies/walk-test/build-eight-review.py
python -m unittest discover -s skills/modular-eight-direction-sprites/scripts/tests -q
node skills/modular-eight-direction-sprites/studies/walk-test/verify-eight-leg-ui.cjs
```

The owner pack is 512 square; mismatched artwork canvases are rejected. Export/packing use fresh directories. The build-review command regenerates diagnostics and refuses stale image/source hashes; it does not draw corrections. Edit the standalone HTML, export annotations, and rerun CLI `check`; browser edits invalidate the previous report immediately.


## Iteration 12 supersedes calf-only identity matches

The user rejects the E correction again because its pelvis-side origin is not proven by moving the cloth. Read [profile-pelvis-depth](profile-pelvis-depth.md). The four old local match claims are withdrawn as identity proof: without paired proximal/depth evidence they remain foreground-order observations. Refreshed v11 reports have zero complete identity matches and 36 unresolved identities. A different new W sheet receives exact-image user approval; the later regenerated W-like pose 3 is explicitly rejected. Preserve these separate decisions and do not conflate user acceptance with recovered hidden joint coordinates.
