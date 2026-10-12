# Fresh modular walk and whole-sheet original-style redraw

This is a bounded motion experiment, separate from the older attack adapter and rejected character art. Read the [review and failures](../../../../research/sprite-animation/walk-test-v9/README.md). No approved art seed or production-ready painted part library exists.

The user's later quality correction is handled in [v10 detailed masters and anatomical review](../../../../research/sprite-animation/quality-review-v10/README.md). Use [continuity practice and CLI](../../references/anatomical-continuity.md) for source-bone comparison. `pack-quality.py` preserves four-pose 512-square masters instead of the earlier miniature output; for the retained 1254-square sheet only, run with `--sheet research/sprite-animation/quality-review-v10/evidence/four-pose-raw.png --output /tmp/my-quality-master --row-offset -20`. Do not reuse that offset on another image without measuring its grid. `verify-leg-ui.cjs` checks the standalone annotation UI, not the game runtime.

Run from repository root. Use new output directories; tools reject existing build/package/check targets. Requires Blender 4.3.2, Python/NumPy/Pillow; `pack-walk.py` additionally uses OpenEXR 3.5.2. The CLI `game-dev` is unavailable in this environment; direct local Blender execution is the fallback.

```bash
blender -b --factory-startup --python-exit-code 2 --python skills/modular-eight-direction-sprites/studies/walk-test/build-walk.py -- \
  --capture research/sprite-animation/preset-retarget-v8/source-transforms.json.gz --output /tmp/my-walk-build

blender -b --factory-startup --python-exit-code 2 --python skills/modular-eight-direction-sprites/studies/walk-test/check-walk.py -- \
  --blend /tmp/my-walk-build/original-modular-walk.blend --output /tmp/my-walk-check.json

blender -b -t 4 --factory-startup --python-exit-code 2 --python skills/modular-eight-direction-sprites/studies/walk-test/build-walk.py -- \
  --mode render --blend /tmp/my-walk-build/original-modular-walk.blend --views S,SE,E,NE,N,NW,W,SW --output /tmp/my-walk-views

blender -b -t 4 --factory-startup --python-exit-code 2 --python skills/modular-eight-direction-sprites/studies/walk-test/build-walk.py -- \
  --mode render --blend /tmp/my-walk-build/original-modular-walk.blend --views SE --parts --output /tmp/my-walk-parts

python skills/modular-eight-direction-sprites/studies/walk-test/pack-walk.py \
  --build /tmp/my-walk-build --renders /tmp/my-walk-views --parts /tmp/my-walk-parts --output /tmp/my-walk-package

python skills/modular-eight-direction-sprites/studies/walk-test/pack-paint.py \
  --sheet research/sprite-animation/walk-test-v9/redraw-evidence/attempt-2-raw.png \
  --motion-package /tmp/my-walk-package --output /tmp/my-painted-package --row-pitch 499

python skills/modular-eight-direction-sprites/studies/walk-test/validate-walk.py \
  --package research/sprite-animation/walk-test-v9
```

The redraw tool is a recorded imagegen edit, not part of these Python commands. Retain the raw output and exact prompts. Build a 1536×1024 4×2 conditioning sheet from eight 256-square SE renders, globally enlarged to 384 square and placed at `(column*384, row*512+64)`. Generate all poses together in the original style; inspect returned grid/alpha and every frame. Repeated generation is not a pose lock.

`499` is a measured correction for this **particular returned sheet**, not a reusable industry value or a source rig anchor. Default row pitch is 512. All four cells in the second row receive the same grid correction; the same 0.25 scale and canvas padding apply to every key. Do not derive individual frame transforms from the silhouette or freeze intentional motion to manufacture low drift. This calibration cannot fix changing anatomy or recover exact joint positions.

The depth-layer sample is an approximate bounded preview: straight-alpha sRGB compositing, nearest native depth, Lanczos native color/alpha, complete isolated geometry with other pieces casting shadows. It retains failed exact RGB comparison and is not the production compositing policy. Complete part coverage is SE only. Painted whole frames are flat images, not replacement parts.


Iteration 11 adds `export-leg-owners.py`, `pack-leg-owners.py`, `build-eight-review.py` and `verify-eight-leg-ui.cjs`. See [actual eight-facing candidates and rejection cases](../../../../research/sprite-animation/eight-direction-v11/README.md) and [occlusion practice/commands](../../references/occlusion-image-review.md). Source-owner IDs come from actual weighted geometry; generated-image chain traces remain independent human observations, not recovered source ground truth. New pixels always require fresh checks.
