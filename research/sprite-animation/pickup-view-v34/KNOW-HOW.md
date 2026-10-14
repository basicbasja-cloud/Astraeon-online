# Adding a physical view without losing motion or replacement correctness

## Start at the demonstrated step

The user pauses MiniMax because setup is not available yet and asks to continue. v32 has scoped user-positive smoothness feedback; v33 demonstrates complete head/hair replacement in one view. Its documented next step is a second physical view. Keep those bytes untouched and create v34 on the same research branch. Do not restart the rejected slash or install REA merely to analyze available source files.

## Evaluate the same source from another camera

`render-source.py` reopens the pinned KayKit 1.1 `Rig_Medium_General.glb`, selects the actual `PickUp` action, mutes other NLA tracks and evaluates eight times across its 39-frame/30Hz source duration. The new orthographic camera is (-6,-9,5.5), aimed at (0,0,1.15), scale3.5,384x512. The prior camera is (6,-9,5.5). Source world points/action/timestamps must remain identical while camera matrices differ. A reflected bitmap or merely renamed direction cannot establish a second physical camera.

View A/B are evidence labels. Their mapping to the game's eight compass facings is not yet approved. Source owner meshes and named bone hierarchy identify anatomical right/left. In B, right is near. Do not rename the reaching hand because its screen position or visibility changes. Screen-near/far texture markers remain distinct from anatomical image annotations.

## Re-author the asset bank and rest bind

Five actual imagegen edits produce the opposite-facing atlas, complete bald head/cape, packing repair, fitted hair pair, and filled thighs. Prompts/inputs/raw outputs are SHA-bound in `generation-ledger.json`. The detailed v32 neutral character is an appearance reference only; no old own attack/rig is used. No generated video is claimed.

The first atlas has a wrong-way cape and joined thigh/tabard region. Do not cut through the joined asset to claim separation. New generation supplies isolated replacement shapes; retain the raw failure. Per-part inspected panels and largest connected alpha components remove only detached packing fragments. Selected source RGBA stays unchanged. Component boundary checks refuse substantial pieces crossing a panel.

19 bank assets include a combined-head comparison plus complete bald base/rear/front hair. Only18 are active for the styled character. Each item declares view B, owner, source texture/hash, authored pivot/end and positive transform. Fixed rest binds are applied to all eight poses. No frame-by-frame bbox fitting or shifting is allowed.

The actual source projection changes the reaching wrist's curve. Copying prior rest offsets verbatim exceeds the authored arm's reach. B uses its own fixed rest wrist and source-delta scale1.1, source-derived trunk curve, explicit body proportions and fixed-length IK. Both shoes stay planted for this particular crouch/reach action. This policy must not be copied onto a walking swing phase. It is an authored 2D adaptation, not a claim that painted anatomy coincides with source joints.

## Review seams and face coverage from the actual composite

Filled receivers must contain real fabric/leather overlap. Initial generated thighs retain hollow cuff ends despite the prompt. Changing ordering exposes the cloth opening instead of solving it. The fifth generation paints solid rounded olive ends. Draw shin before thigh so the filled fabric covers its receiver; near right arm stays above the torso, anatomical left teal cloth behind it. Preserve both failed rendered examples.

The first hair pair covers the eye and leaves scalp exposed. Rest-bind changes alone do not create an appropriate cap. A new imagegen pair supplies a coherent right-facing scalp shell with a right-side face window. Inspect the bald source head and combined-head appearance, register the new pair once, then inspect all eight final images. Do not conceal the bald scalp by changing skin color.

Known authoring polygons define a visible eye interior and an upper-scalp comparison guide in the base-head texture. Project them using the actual head matrix and erode raster borders by one pixel. Eye RGBA must equal bald RGBA; upper scalp must change under the hair. Final eye regions contain44–63pixels each,0changed; sampled scalp has0%uncovered. These are **authored local region checks**, not blind eye detection, skin segmentation, full-scalp geometry proof or an anatomical accuracy percentage. The retained real failed hair image is a negative test.

Head-only counterfactual passes define the intended edited region. All body RGBA outside the union of old/new head passes must remain identical. Those masks come from the renderer and are not independent semantic segmentation. Head base retains v33's explicit opaque-material rule alpha>=240→255; raw head PNG is unchanged. Changing appearance during playback preserves frame, running state and pose data.

## Fix a measurement defect without weakening criteria

Frame0 cuff's fully opaque isolated-texture radius is about9.197px. A40px-wide calibration patch includes neighboring surfaces. A13px internal patch fits its rotation support but the old matcher still abstains at frames1/2. Inspection shows its rotated RGB template interpolates black outside the patch while its nearest-neighbor mask includes partially unsupported border samples.

`rigid-surface-observer-v2.py` transforms an all-ones support image with the same bilinear interpolation. It excludes mask pixels whose support is below.999. This changes which pixels are valid, not NCC .95, ambiguity margin .015, planted6px or phase.25 criteria. Source/current-frame rig coordinates never feed detection. The matcher sees frame0, fixed windows and actual frame pixels; later pose data is loaded only afterward for held-out error reporting.

Final samples are72/72visible across three appearances. Toe ranges are0px. Held-out cuff error is<=0.788px and source-relative normalized Y-phase discrepancy about.00763. These values concern a fixed rigid-texture family; independent redraws, deformed cloth, occluded hands or a new character require new calibration/validation. NCC is not an accuracy probability. Erasing a surface returns unknown, blank calibration fails, changed image hashes fail, and the unmodified v1 still reproduces its two abstentions.

## Evidence and acceptance are separate

`directional-part-review.py` checks actual bound bank membership, camera/source clock, limb endpoints/owners, positive determinants, fixed lengths, shoe mounts, overlap order, unchanged body rows, full RGBA and defined eye/scalp regions. Seventeen focused regressions include wrong views, mirrored matrices, swapped chains, synchronized foot errors, bad overlap, changed clocks/images and a real failed generated hair image. Twelve browser checks exercise live appearance swaps, both clocks, exact frame replay and missing/incompatible parts.

Normal/source clocks remain700/1300ms active plus600ms final hold. GIF timing is decoded and verified independently; an eight-key frame count does not imply a universal Ragnarok rate. The comparison GIF replays two source-time-aligned physical views. No frame interpolation is inserted, no video provider is called, and no turn transition is tested.

An exact-image agent visual receipt records final one-view-part/motion review. Numeric packaging cannot grant that receipt to changed images. User art approval, eight physical views, attack/locomotion schedules, object reach/grip and game admission remain separate future gates.

## Reproduce

From repository root; Python/Pillow/NumPy/OpenCV, Blender and Node/Playwright/Chromium. This executor's optional OpenCV wheels live in `/tmp/astraeon-vision-deps`. Raw art is retained: rebuilds do not call generation providers.

```bash
blender -b -t 4 --python research/sprite-animation/pickup-view-v34/render-source.py -- --out research/sprite-animation/pickup-view-v34/source
PYTHONPATH=/tmp/astraeon-vision-deps python research/sprite-animation/pickup-view-v34/normalize-parts.py
python research/sprite-animation/pickup-view-v34/build-runtime.py
node research/sprite-animation/pickup-view-v34/export-frames.cjs
python research/sprite-animation/pickup-view-v34/package-review.py
python research/sprite-animation/pickup-view-v34/build-case.py
python skills/modular-eight-direction-sprites/scripts/directional-part-review.py --case research/sprite-animation/pickup-view-v34/view-case.json --root . --out research/sprite-animation/pickup-view-v34/view-review.json
PYTHONPATH=/tmp/astraeon-vision-deps python research/sprite-animation/pickup-view-v34/check-pixels.py
node research/sprite-animation/pickup-view-v34/check-browser.cjs
python -m unittest discover -s skills/modular-eight-direction-sprites/scripts/tests -p test_directional_part_review.py -v
PYTHONPATH=/tmp/astraeon-vision-deps python -m unittest discover -s skills/modular-eight-direction-sprites/scripts/tests -p test_rigid_surface_observer_v2.py -v
python research/sprite-animation/pickup-view-v34/audit-evidence.py
```

Chromium needs a launcher permitted by the execution sandbox; its initial socket-blocked launch is not a passing test. Here the actual browser run completed through approved execution. Publishing/freezing must happen only after checks and a separate exact-image visual review. The next bounded step is another perspective/slot stress case, then action-specific direction coverage; this two-view result cannot silently fill the other six facings.
