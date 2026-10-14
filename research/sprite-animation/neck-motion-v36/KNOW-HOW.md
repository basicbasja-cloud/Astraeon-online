# Painted receivers before declaring sockets

The actual failure was visible above the scarf: the old head contributed a black collar while the coherent outfit already supplied one. The declared pivot `[202,326]` on the previous head was inherited rig metadata, not a detected neck insertion surface. v35's successful transform/draw-call checks were not neck or proportion acceptance.

Keep the rejected v35 preview byte-identical as a counterexample. Inspect head and body separately on contrasting backgrounds, then in an enlarged composite. In `neck-diagnosis.png` the cut surface and doubled clothing are visible; whole-image bounds cannot locate a neck. Paint the complete head with a short solid skin underlap and no scarf, shoulders or collar. The native image tool performed this repaint; diagnostic crops and packaging do not paint anatomy.

## Define a receiver with two visible points and one owner

For the neutral v35 body, manually reviewed collar insertion points in its 1024×1536 source are `[388,250]` and `[485,220]`. The new 1254×1254 head has corresponding visible skin-insertion points `[609,1119]` and `[846,1061]`. These are observations with uncertainty, not recovered neck bones. Fit the point-pair direction and midpoint, while holding head scale `.11` fixed. The old `.40` and new `.11` scales are not a percentage size comparison: their source resolutions differ.

The body keeps its exact old common transform. The new head gets a constant similarity transform. Compare **both endpoints**, not merely the pair midpoint; matching one pivot can leave the neck width or angle wrong. The neutral endpoint budget is 2 px. Motion has separately declared 3 px, with manually reviewed edge uncertainty ±3 native body pixels. These thresholds predate the measured reports and are different attachment cases, not a widened planted-foot budget.

Draw coherent body first, head second, then the body's original collar lip in front. A source-native polygon selects body pixels for that foreground pass. This does not create a new inventory slot or independently resize clothing. Drawing the entire body over the head instead exposed the body neck stub/cutline, so restrict the final pass to actual collar coverage. In each motion pose the collar polygon follows the observed visible edge; it is not one reused screen-space rectangle.

Use the same declared material policy in neutral and motion: native decoded alpha≥240 is opaque for intended interiors, while RGB, raw files and soft outer edges remain intact. Otherwise a visually solid skin patch can reveal collar texture through alpha252–253. This is renderer material handling, not a claim that arbitrary translucent materials should be forced opaque.

## Verify actual pixels independently of the fit

`coherent-neck-motion.py` separately checks the following:

1. Input/source hashes, exact raw sheet crops, positive uniform head scale and identical body transforms through all frames.
2. Transformed insertion-pair residuals against visible body receiver points.
3. Head-only coverage four display pixels above the receiver, body-only coverage five pixels below it, and continuous composite alpha along the intervening strip.
4. Every fully opaque collar-pass pixel must retain the original body-pass RGBA in the final composite. A fitting endpoint cannot approve a skin patch drawn over the collar.
5. Actual raw and rasterized forefoot extrema in fixed, reviewed image bands. Empty bands are unknown/error. Both representations must meet the same 6 px budget.

The pixel strip is a bounded continuity check, not proof of every contour or anatomical shape. The collar and support observations require review when changing camera, outfit, cape coverage, transparency or character proportions. The far band intentionally observes forefoot/toe surfaces, excludes a released/occluding heel, and is not full-shoe segmentation. Hip/knee identity beneath clothes remains unknown without appropriate independent evidence.

Thirteen tests include deliberately shifted head geometry, absent head pixels despite declared alignment, alpha gaps, absent/wrong collar pixels, reflected/anisotropic head transforms, missing support pixels, real overshoot, real subpixel contact failure, wrong body hashes and per-frame body translations. Negative controls exercise the real rendered images; a successful test suite is independent of candidate acceptance.

## Adapt source motion without hiding redraw errors

Source is CC0 KayKit `PickUp`, GLB SHA256 `5f725c0f745f36078c7238968cd5c04843cbc6260689eb6e7f5e2bbd7ffdd7ad`. [Source records](../pickup-pilot-v31/source/source.json) retain the eight actual source times, evaluated joint positions and original camera. [Creator license](../joint-tracking-ro-v30/preset-source/KayKit-License.txt) covers that preset; it does not turn other game references into unrestricted training data.

`build-motion-guide.py` uses the source pelvis/head/wrist deltas with explicitly authored target proportions and fixed-length leg/arm IK. Blue is anatomical right/far and orange left/near. The boots are fixed visual stencils from the neutral reference. This is a source-driven **authored 2D guide**, not automatic anatomical detection or an unchanged retarget. The guide's reserved head area corrected an earlier model tendency to enlarge the bodies and clip capes.

Attempt1 clips and recovers prematurely. Attempt2 preserves more of the intended action but key6 overshoots above neutral and key3's far toe shifts. A targeted repair generation changed unrelated drawings and row packing, so no repair pixels enter the selected bank. Keep every raw attempt; moving each figure to fit its shoe or neck would conceal the failure.

The entire selected bank gets exactly one rest transform, `s=300/(485−126.95)=0.8378718056`. It maps the observed rest cap centroid to `[192,180]` and near sole to480. This applies identically to all full body drawings. The head attaches to each drawing's observed collar with fixed scale; this legitimate per-pose attachment is different from translating the whole body to repair contacts.

Raw art indices0..7 remain inspectable. Selected indices are `[7,1,2,3,4,5,7,7]`: source0/7 are the same rest, and key6 becomes an explicit early rest hold. There are six unique paintings across eight exposures. This is a disclosed sparse authoring approximation; it does not establish that the omitted recovery pose follows source performance exactly. The source-relative vertical surface metric calibrates rest/peak indices0/3 and checks the other six times. Maximum difference0.215949 is within0.25, but it is not a complete velocity/acting/smoothness metric. A repeated rest can still feel abrupt; that requires visual review and a better authored intermediate.

Contact analysis catches a quantization trap: the far toe moves8 source pixels, or6.70297 display pixels, while transformed raster extrema span only6 integer pixels. Checking only the final integer coordinates would declare this boundary case acceptable. Retain both measurements and fail the unchanged6 px gate. Near-foot X is5.86510 native-equivalent/6 rendered; Y spans3 rendered pixels. These are surface variations, not proven skeleton motion or contact force. Repair the actual coherent-body drawing next; do not move the root, copy/freeze the shoes or relax the threshold.

## Clocks, inspection and source receipts

Source times0…1.3 seconds use GIF exposures `[190,180,190,180,190,180,190,600]`, total1900ms including terminal hold. The optional game comparison uses seven100ms transitions plus600ms terminal hold, total1300ms. They are different clocks for the same keys. Actual browser playback follows the unrounded source timestamps; GIF exposure boundaries round to10ms. Decoded GIF receipts preserve total time and disclose encoder-merging of identical adjacent keys. No extra generated in-betweens or provider video exist.

Fifteen real Chromium checks exercise all sixteen full-frame exports, actual three-pass drawing, logical slot count, explicit repeated rest, slider/variant/clock selection, both completed playbacks and observed-edge overlays. The self-contained HTML makes no external requests. The manual `visual-review.json` binds inspected images; packaging does not mint acceptance for changed images.

The RO grouping reference remains the pinned community [roBrowser renderer](https://github.com/vthibault/roBrowser/blob/e4b5b53aa1f8b7e429bfa987ab321c96502ba1da/src/Renderer/Entity/EntityRender.js), Git blob `87242ad5a9012f17af784e9792769f1eef74dd5c`; [previous exact receipt](../body-outfit-v35/source/receipt.json) is unchanged. It supports logical body/head/equipment and an ACT body positional reference for the head, not hidden original-client bones or a universal one-bitmap rule. Our foreground collar is an internal rendering piece, not a separately equipped collar item.

Four actual still-image jobs are retained with prompts/outputs. The revised guide and neutral reference for attempt2, and attempt2+guide for repair, are bound exactly. The head job's full input manifest, the overwritten first guide revision and the initial neutral composite before its material re-export are missing exact historical input evidence; current files must not be assigned retroactively as those bytes. The retained384×512neutral reference for attempt2 was not overwritten by the later512×512neutral export. The revised guide reproduces exactly from that retained reference/source. No old own attack assets, baseline game branch art, MiniMax calls or native generated video are involved.

## Reproduce without paid generation

From repository root, with Python NumPy/Pillow and local Playwright/Chromium:

```bash
python research/sprite-animation/neck-motion-v36/build-neck.py
node research/sprite-animation/neck-motion-v36/export-neck.cjs
python research/sprite-animation/neck-motion-v36/build-motion-guide.py
python research/sprite-animation/neck-motion-v36/prepare-motion.py
python research/sprite-animation/neck-motion-v36/build-motion-runtime.py
node research/sprite-animation/neck-motion-v36/export-motion.cjs
node research/sprite-animation/neck-motion-v36/browser-check.cjs
python skills/modular-eight-direction-sprites/scripts/coherent-neck-motion.py --contract research/sprite-animation/neck-motion-v36/motion-contract.json --render-root research/sprite-animation/neck-motion-v36/renders --report research/sprite-animation/neck-motion-v36/motion-qa.json
python research/sprite-animation/neck-motion-v36/test-neck-motion.py
python research/sprite-animation/neck-motion-v36/package-review.py
python research/sprite-animation/neck-motion-v36/audit-evidence.py
```

Browser commands require permission to run Chromium outside this environment's restrictive default sandbox. `--require-motion` on the review command deliberately exits1 for the current failed contact gate. Default diagnostic exit0 only means a report was computed. Production remains false even if future numeric gates pass: inspect the actual action, anatomy, silhouette, receivers and compatible replacement coverage first. Freeze only after reports/receipts are final; preserve all previous published manifests and protected W pixels.
