# Hair replacement without changing an accepted motion

## Preserve the approved comparison before expanding appearance

The user positively evaluates v32 smoothness. Save the exact eight drawing/GIF/pose hashes before making changes; do not overwrite the old generator outputs or silently transfer approval to newly generated heads. No source/game clock preference was stated. In v33 both original clocks remain available and the complete original v32 character can be restored byte-for-byte.

Changing appearance must not restart the action or alter the source skeleton. The renderer uses the same v32 source/pose function and original15non-head rows. A skin change selects replacement assets only. The browser test changes hair during playback and asserts the running flag, current frame and pose data remain unchanged. Both700ms and1300ms active clocks still finish on the eighth key with600ms terminal hold.

## Acquire complete hidden anatomy instead of masking old hair

The old `head_hair` part includes silver hair and incomplete hidden scalp. It cannot support a real replacement by simply recoloring or drawing another cap over it. A genuine imagegen edit removes all hair and paints a complete bald cranium, forehead, ears and neck/collar. This new base head has its own provenance and is not claimed to be pixel-identical to the old face.

Generate hair separately as rear/front pairs, with no embedded face/eyes/skin/neck. Silver preserves the costume palette; auburn has a distinct swept silhouette. Rear → base head → front is actual depth order. The bald selection is essential: it exposes the complete hidden content and proves that removing hair does not reveal leftover silver bangs or empty scalp.

Inspect actual atlas output, not the requested layout. The first1254-square output has a joined top silver component despite a2×2request. Cutting equal cells would cut hair or pull a neighboring piece into the wrong part. The failure is retained, and a real imagegen packing repair supplies four separate components with transparent gutters. Normalize selected components once, preserve their retainedRGBA values, and keep raw provider images intact. The crop adapter refuses a substantial component crossing its panel boundary; it does not trim away a failed silhouette to force acceptance.

## Rest registration belongs to the asset bank

The new parts have different raw resolutions. `registration.json` contains one raw-part→original-head-space matrix per asset. The common head space is366×365, with the same authored mount[202,326] as v32. A base-head rest scale.23 and fixed offsets align collar/face landmarks; hair layers have their own fixed scale/offset for complete receivers and face aperture. These values are visible authoring decisions, not detected anatomy.

The runtime composes `world_from_original_head × original_head_from_part`. Every frame inherits the original head transform; no hairstyle supplies a second motion curve. All determinants remain positive, no mirroring is used, and complete bank membership/depth order are checked from actual exported rows. Tests deliberately offset one front hair matrix in one frame, reverse rear/front rows and mirror a layer: each fails.

Camera/view identity is part of this contract. Reusing this hair pair in a back or opposite-facing view is not approved. New views need appropriate head/hair perspective art and their own attachment/occlusion review. Preserve anatomical ownership; do not derive it from screen order or hair color.

## Opaque skin is a material contract

The new generated head looks opaque but its deep skin alpha is252–253. With rear hair behind it, ordinary alpha blending shifts visible face/eye colors. A successful asset load does not prove a correct paper-doll composition. The actual counterfactual renders show538different protected-eye pixels between silver and auburn, with maximum3channel difference.

The renderer explicitly promotes only decoded base-head alpha≥240 to255 before transformation, retaining decodedRGB and soft outer edge pixels. Raw PNGs stay untouched. This is a head-only opaque surface rule, not a rule to destroy translucency in cloth or effects. Record the rule, affected-pixel count and exact loader code. The original combined v32 head is exempt so its exact comparison pixels remain intact.

After this change the34×16visible eye patch matches exactly in silver/auburn/bald rest previews. The same authoring rectangle is projected through the common head matrix into each full frame, with one-pixel interior erosion excluding raster boundary;91–136 actual eye-interior pixels per pose match across new appearances. This is an actualRGBA comparison guided by known authoring geometry, not a blind eye detector, semantic model accuracy claim or hidden-joint measurement.

## Pixel and mechanical evidence must agree

`hair-swap-review.py` checks bound images/poses/clock/source texture hashes, real matrices, persistent body rows, head-depth order, silhouettes and actual pixels. Per-frame head-only render passes define the declared changed region. Outside the union of old/new head passes, everyRGBA pixel is identical to v32. The masks are counterfactual renderer outputs and must not be presented as independent anatomical segmentation.

The complete original option restores all8PNG files byte-for-byte, including antialiasing. `poses.json` is byte-identical. Whole-frame translations or time changes cannot inherit prior smoothness feedback. A color-only alternate with the same silhouette does not satisfy this two-style test; actual selected hairstyles differ by6,673silhouette pixels.

Rerun the existing blinded rigid-texture observer on actual silver, auburn and bald frames. It uses frame0patches/fixed windows, never future pose positions. Toe drift stays0px and source-relative cuff phase error0.005313under the unchanged6px/.25criteria. The generic source checker still refuses to certify hidden anatomy, physical support or full production.

Inspect all hair/hidden-head poses and runtime playback. Save a visual receipt against exact new frame hashes. Packaging may recompute numeric results, but it must not grant a positive visual review to changed pictures automatically. Prior user-positive smoothness is not user approval of new face/hair art.

## Official documents studied for this extension

Three documents were actually downloaded, and selected sections were searched/read; raw page hashes and short excerpts are retained. No Spine or Godot project was executed.

| Source | Applied lesson |
| --- | --- |
| [Spine skins](https://esotericsoftware.com/spine-skins) / [receipt](source-skins.json) | Bind attachments to skin placeholders so changing appearance is separate from timeline keys; skin identity does not prove visual compatibility. |
| [Spine attachments](https://esotericsoftware.com/spine-attachments) / [receipt](source-attachments.json) | Referenced attachments need actual exported assets; an editor preview or an unexported attachment cannot constitute a production replacement package. |
| [Godot CanvasItem](https://docs.godotengine.org/en/stable/classes/class_canvasitem.html) / [receipt](source-canvasitem.json) | Transform/modulation/visibility inheritance and Z-order are explicit; CanvasItem inheritance requires direct compatible children. Our adapter uses explicit affine composition instead of claiming a Godot hierarchy was built. |

These sources support separate appearance slots and hierarchical rendering. Our exact alpha threshold, patches and tolerances are executed engineering choices, not standards asserted by those documents.

## Reproduction

Run from repository root. Dependencies match v32: Python/Pillow,NumPy/OpenCV and Node/Playwright/Chromium. This executor uses `/tmp/astraeon-vision-deps` for optional vision wheels; set `PYTHONPATH` accordingly. Raw art is already retained; rebuilding does not generate new art or invoke a paid provider.

```bash
python research/sprite-animation/hair-swap-v33/normalize-parts.py
python research/sprite-animation/hair-swap-v33/build-runtime.py
node research/sprite-animation/hair-swap-v33/export-frames.cjs
python research/sprite-animation/hair-swap-v33/package-review.py
python skills/modular-eight-direction-sprites/scripts/hair-swap-review.py --case research/sprite-animation/hair-swap-v33/swap-case.json --root . --out research/sprite-animation/hair-swap-v33/swap-review.json
python research/sprite-animation/hair-swap-v33/check-source-motion.py
node research/sprite-animation/hair-swap-v33/check-browser.cjs
python -m unittest discover -s skills/modular-eight-direction-sprites/scripts/tests -p test_hair_swap_review.py -v
python research/sprite-animation/hair-swap-v33/audit-evidence.py
```

The synchronized comparisonGIF can be retained as review evidence; each standalone bank has eight frames and both clocks. Rebuilding may alter metadata paths/runtime screenshots, but changed image hashes require fresh visual review. Retain old failures and acceptance receipts. The next factory step is a second physical view with original perspective-specific parts, followed by view coverage/locomotion contact schedules; the planted-shoe policy must not be copied into walk swing phases. Per-pose weapon perspective rules and old own slash exclusion remain in force.
