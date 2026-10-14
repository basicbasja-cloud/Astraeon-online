# Repair one existing key after establishing the whole animation bank

V38improved contacts and produced a genuine intermediate, but its receiver reversed left10.68pxlate in recovery. Five whole-strip edits either preserved the wrong lean or changed packing/alpha/unrequested keys. V39continues the same user-authorized motion work rather than treating that checkpoint as acceptance.

## Control the edit scope

Freeze all seven non-target key records, textures, body/head transforms, receiver points and actual full/body/head/collar render passes. Repair only index6(display key7). This is local maintenance of an existing whole-strip animation, not independently generating every frame. It retains the consistency rationale of the studied sprite-pipeline workflow while avoiding another redraw of already-reviewed neighbors. No new permission or approved-seed claim is inferred; this remains the existing research candidate under the user's standing instruction.

Use the near-upright diagnostic silhouette derived from the standing pose as the pose reference and the unchanged standing body as the material/footprint reference. The guide has a small internal torso hinge/hip drop and planted boot stencils; its temporary knee overlap is not final artwork. The native image tool paints a new complete connected body. Final pixels never come from the guide transform or copied boot patches.

Place a384×512reference cell at2×scale and translation`[128,0]`inside a1024×1024square. This makes the one-body request unambiguous and keeps floor margins defined. `build-reference-plates.py` reproduces the exact inputs. The native output's actual square resolution is measured, not assumed. Normalize it with the inverse sampling affine `[W/512,0,W/8,0,H/512,0]`to384×512, using one bicubic sample. These constants come only from known plate geometry; no silhouette bounds, collar point or shoe detection influences them. If the provider changes composition, subsequent contact/scale checks must reject the result rather than adjust the fit.

Retain the original native output and normalization receipt. The output is a genuine new still edit, not provider video or a synthetic rig frame. `packed-reference-atlas.png`copies the seven previous body drawings plus the normalized new drawing only for legacy exact-crop verification. Its schema explicitly says it is locally packed; do not call it a native full-strip output or claim eight newly generated poses. Independent normalization/isolation checks prove the derivative chain.

## Attach the same head and recheck actual pixels

Manually inspect the normalized collar in `collar-inspection.png`. Reviewed outer-lip points are`[168,139]`and`[195,123]`, with±3canonicalpixel uncertainty. They are actual painted observations, not detected neck bones. Use the same frozen head source insertion pair and scale`.11`; fit midpoint/direction and retain body-owned collar foreground. The new endpoint residual is0.99995px, actual alpha bridge is255and opaque collar pixels retain the original body RGBA. Other seven head transforms remain exact.

All eight body drawings keep the exact v38body matrix. Source/game clocks, thresholds and rest registration stay unchanged. The repaired receiver moves`(194.38,214.86)→(197.94,197.45)→(204.27,185.98)`through the last three exposures. It rises and moves right without the previous reversal. New penultimate vertical fraction`.116`is near actual source`.110894`. The unchanged earlier key2still sets maximum held-out phase error`.169553`; do not retune the0.25criterion.

Forefoot ranges remain far5.540native-equivalent/6rasterpixels and near4.749/5pixels, under the same6pxbudget. Near-sole raster Y range is1px. This is bounded surface continuity, not zero drift or world contact force. The new drawing's canonical forefoot extrema are far`[121,468]`,near`[198,488]`, obtained after the fixed plate normalization. Empty review patches in the verification atlas have zero alpha without background thresholding.

`coherent-motion-spacing.py --require-motion`fails for the old v38before variant and passes the repaired review. The action-specific up/right policy and2pxrecovery tolerance are unchanged. These are intended for this authored crouch, not a universal monotonicity rule for attacks or counter-swings. Parent neck/contact/source-phase checks, strict sequence checks and explicit visual review have separate authority.

## Reusable isolation validator

New `scripts/isolated-key-review.py` verifies shared source/head/scale/clocks/render order/limits, exact non-target records, source/body hashes, the known-canvas affine and actual normalized pixels. It independently compares all four render passes for each of the seven protected keys:28actual pixel comparisons. A non-target head-anchor change, faster clock or relaxed contact budget must fail even if an image appears similar. The target body must actually change visible pixels; a changed filename/marker alone is insufficient. Changed pixels still do not certify a correct pose or anatomy.

Eight focused tests exercise the actual successful isolation, non-target anchor changes, clock changes, relaxed budgets, fabricated normalization offsets, the real before/after lateral failure, deliberate head misattachment and actual zero-alpha patches. Nineteen real browser checks retain playback/pixel/slot/clock behavior and verify that runtime metadata binds the current normalization receipt. The earlier23tests and all frozen v38failed evidence remain untouched; they are not retroactively relabelled as passed motion.

## Actual review and limits

The agent inspects the actual eight-key progression, new collar detail, source/XY/contact plot and browser frame. The return now eases toward standing without the obvious left/right hitch; both shoes maintain bounded support, the body moves coherently and the head joins the collar. Cape/cloth follow-through and a returning hand are visible rather than a frozen torso. The receipt grants **one-view coarse crouch/reach/return agent motion review only**. It does not grant user approval, exact concept proportions, automatic hidden hip/knee/finger/owner accuracy, actual object grasp or every RPG action/view. No provider video was generated.

The source remains the externally sourced CC0KayKitPickUp timeline with eight evaluated sample times. The target is an authored proportion/camera adaptation; matching a collar phase does not recover all source joints from painted pixels. No old own attack, rejected baseline game asset, MiniMax or new external paid-provider API is used. Final game admission and all-view/equipment compatibility remain separate work.

Source clock is0…1.3splus600msterminalhold,total1900ms; game comparison is seven100mstransitions plus600mshold,total1300ms. Actual decoded GIF clocks are recorded. Seven other frames and their placements are exact, not merely approximately aligned. Keep the passed repaired bank immutable before adapting another view/action, and recalibrate any genuinely different body/camera rather than transferring pixel budgets blindly.

## Reproduce without generation

From repository root:

```bash
python research/sprite-animation/recovery-key-v39/build-reference-plates.py
python research/sprite-animation/recovery-key-v39/normalize-one-key.py
python research/sprite-animation/recovery-key-v39/build-case.py
python research/sprite-animation/recovery-key-v39/build-motion-runtime.py
node research/sprite-animation/recovery-key-v39/export-motion.cjs
python skills/modular-eight-direction-sprites/scripts/coherent-neck-motion.py --contract research/sprite-animation/recovery-key-v39/motion-contract.json --render-root research/sprite-animation/recovery-key-v39/renders --report research/sprite-animation/recovery-key-v39/motion-qa.json
python skills/modular-eight-direction-sprites/scripts/coherent-motion-spacing.py --contract research/sprite-animation/recovery-key-v39/motion-contract.json --motion-report research/sprite-animation/recovery-key-v39/motion-qa.json --out research/sprite-animation/recovery-key-v39/spacing-qa.json --require-motion
python skills/modular-eight-direction-sprites/scripts/isolated-key-review.py --before-contract research/sprite-animation/coherent-motion-v38/motion-contract.json --after-contract research/sprite-animation/recovery-key-v39/motion-contract.json --before-renders research/sprite-animation/coherent-motion-v38/renders/review --after-renders research/sprite-animation/recovery-key-v39/renders/review --normalization research/sprite-animation/recovery-key-v39/normalization.json --out research/sprite-animation/recovery-key-v39/isolation-qa.json
python research/sprite-animation/recovery-key-v39/test-isolated-key.py
node research/sprite-animation/recovery-key-v39/browser-check.cjs
python research/sprite-animation/recovery-key-v39/package-review.py
python research/sprite-animation/recovery-key-v39/audit-evidence.py
```

NumPy/Pillow/Matplotlib and local Playwright/Chromium are required. Browser execution needs the environment's Chromium permission. Reproduction never regenerates a visual-approval receipt; changed inspected pixels require fresh explicit review. Preserve every previous manifest and protected W file.
