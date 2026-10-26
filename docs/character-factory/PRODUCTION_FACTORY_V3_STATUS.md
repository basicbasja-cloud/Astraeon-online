# Production Factory V3 status and handoff

## Reusable rig and motion preference — 26 October 2026

The owner reaffirmed Mesh2Motion as the preferred motion source. Retain it as the default; record any retained archery fallback separately. Scope remains all three classes, both sexes, reusable sprite parts and rig, smooth source-aligned actions.

A portable shared authoring rig now opens in Blender and GLB with 60 bones, 8 fixed cameras, 10 live sockets and embedded textures. Two overlapping source faces are preserved by splitting six indices; no faces, UV/material surfaces or weights are removed. The saved native Mesh2Motion walk example matches 16 × 51 bone matrices after reopening. This is a reference rig and one editable motion, not six finished meshes or all action sets. See `docs/character-factory/review/patch001-reusable-rig-20261026/`. Current admitted coverage remains 2/96 jobs and zero newly complete characters.


## Storage cleanup update — 26 October 2026

The owner authorized deletion of unnecessary files. Removed 8,704 untracked obsolete generated guide PNGs from 74 superseded jobs, reclaiming 6.37 GB (5.93 GiB). All 48 active guide jobs / 5,568 expected images remain present. Current art, part sprites, motion sources, canonical rig and tracked files were retained. About 6.1 GiB is now free: **the immediate storage blocker below is resolved**. Production can resume. Six-character completeness is still 2/96 imported jobs and zero complete newly admitted characters. Details: `docs/character-factory/review/cleanup-20261026/`.

## Latest actual state — 26 October 2026

Still 2/96 actual imported jobs, both Swordsman BasicAttack, and zero complete newly admitted characters. Mage native walking and casting pilots remain studies; 10 lossless male/female walking role sheets now contain 160 verified native cells. Archer weapon/hand ownership and recovery-arrow defects remain open. The latest eight-view Mage costume drawing is rejected for incorrect camera views and background.

Production of the complete six-character factory is blocked by workspace capacity: approximately 160 MiB free on the 32 GB filesystem. The measured current native-pose output projects to roughly 5.4 GiB for remaining pose positions before reuse, excluding source drawings, sheets, atlases, replay scratch and Git. This is an estimate, not a minimum. A small pilot still fits, but full scope does not. Expand to 64 GB or provide a persistent volume with at least 20 GiB free. No original art or source guide is removed.

See `docs/character-factory/review/patch001-three-class-readiness-20261026/` for the per-character/action/direction matrix, receipts policy, measured capacity and resume sequence. Historical status sections below do not supersede this state.


## Active patch checkpoint — 23 October 2026

Owner clarification: earlier male Swordsman artwork was already visually okay.
Preserve its BasicAttack and SkillOverhead as the baseline. The separate
[preserved-art review](review/patch001-preserved-swordsman-cutouts-20261023/README.md)
keeps 896 source files unchanged and checks 128 actual poses through the browser
compositor, with 256 zero-difference base/trail comparisons. The remaining
semantic/motion limits are recorded; this does not increment current patch imports.

The latest owner scope supersedes the original single-character pilot: male/female Swordsman, Mage and Archer, all patch 0.0.1 actions, general actions in eight real directions and physical attacks/casting in four real diagonals. Mesh2Motion remains preferred; retained CC0 KayKit supplies bow clips. The previous milestones below are historical evidence, not current patch completion.

Native composition now preserves full-resolution cutouts and overlapping hidden surfaces before a single final resize. Eight actual Chromium pixel checks pass with zero changed pixels. A 16-frame source-first Archer study and current temporal masks remain art proposals, with weapon/glove edges and head continuity still pending. Detail PNG/GIF held-pose mismatch is corrected. See `review/patch001-native-composition-20261023/`.

Three actual Archer NW part sheets now cover16 canonical poses. Seven local hand/neck/sleeve ownership probes pass; hidden body coverage remains limited. All16 browser comparisons match the same native-canvas resize path, with direct PNG filter differences reported separately. These remain unapproved single-view studies.

Current ledger: six characters, 114 action instances, 49/49 guide jobs captured, 5,696 source positions after reuse, 98 unique paint jobs, **zero complete imported cutout jobs**. No current six-character runtime admission or owner visual approval. See [the active state](../../authoring/characters/factory-v3/patch-0.0.1/CURRENT_STATE.md).

Actual bow source correction: old retarget added 0.1019 m of rear-toe lift. Authored cheek-anchor arm IK, lifted elbow hints, per-foot donor contact IK and draw/release finger states correct that defect. The actual Blender regression covers 18 poses; all68 factory tests pass. A 64-pose four-view audit reports maximum toe-height discrepancy below 4e-7 m, zero arm reach clamp, matching ready/recovery body landmarks, correct held-arrow release at frame10, and no viewport clipping. These checks do not certify painted anatomy or weight-bearing quality.

Paint progression: a correct-handed single-frame repair and coherent-sheet repair exist, but old recovery timing differs from the current guide. Independent detailed four-frame paint batches fail coherence. A full-action attempt using a generic front portrait turns the rear view toward the chest and is rejected. Matching-direction head/hood references produce a stronger NW rear-view candidate; it remains under source-fit, animation and modular-layer review. Normal/slow, game-scale and guide-versus-paint previews use one shared viewport transform, never per-frame bounding-box fitting.

### Runtime bridge and sprite-quality continuation

Six class/sex package routes, class-specific motion validation, explicit event packing and semantic skill routing are implemented. No complete new packages exist yet. Actual legacy-game browser regression passes movement/attack for class IDs0,3,12; this does not count as six new playable characters. Technical coverage:58 Python tests,143 individual Node checks. Actual16-frame head/body reduction defects are fixed (3,880 changed pixels before,0 after); source-aligned anatomy and complete semantic cutouts remain outstanding. See [the concrete acceptance report](PATCH001_PLAYABLE_ACCEPTANCE.md).

### Current handoff

- **COMPLETE:** current source captures, actual contact regression, view-specific design-reference preparation, fixed-camera review tooling.
- **PARTIAL:** coherent painted actions and same-frame cutouts; detailed rejected studies retained with provenance.
- **BLOCKED:** release admission by incomplete art/quality work; no owner credential or external provider action is needed for the active path.
- **OWNER REVIEW REQUIRED:** finished candidate animations and the final six-character runtime proof, after internal quality gates.
- **NEXT EXACT ACTION:** finish the current four-view Archer action review, derive and inspect same-frame HeadHair/BodyCostume/Weapon/occluder cutouts, then continue the remaining patch actions and requested hairstyle/costume demonstrations. Do not count sources or paint-job manifests as finished sprites.


**Branch:** `character/production-factory-v3`
**Target:** patch 0.0.1, male/female Swordsman, Mage and Archer
**Updated:** 22 October 2026
**Overall:** `SOURCE_CONTACT_FIXES / PAINT_AND_CUTOUT_QUALITY_WORK / NOT_RELEASE_COMPLETE`
**Runtime admission:** `DEV_ONLY / NOT_APPROVED`

The existing painted-v2 package is still a fused composite. The owner rejected its Wayfarer Capital screenshots because that is not the requested map; they are retained only as historical development evidence and do not count as a successful current-map visual review. The owner supplied clearer art references and directed that hair, outfit, weapon, cape, and effects be drawn as independent layers. V3 remains development-only and is not production-complete.

## Current owner direction

### Mesh2Motion selected (21 October 2026)

The owner chose Mesh2Motion and authorized continued implementation. [The fresh motion/art study](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/README.md) compares A, B, C and Combo on the original source mannequin. B is the working overhead cut; its matching recovery is required. New reproducible Blender scripts sample the source at 60 fps, build a compact 60-pose one-shot, fit one fixed orthographic camera to the entire action, and record hand, foot, blade and root positions. The existing research silhouette audit is reused as a diagnostic rather than an art-quality grade.

Inspection of the raw GLB confirmed that all 198 animation channels in A/B and their recoveries repeat the starting value at the terminal export key. Those resets and the reset-influenced recovery tail are excluded from the review. A trial that artificially returned the final pose to the initial image was rejected because it slid the feet across source root displacement. Current B guides preserve native root motion and finish on the source recovery instead.

The compact B capture now covers all eight real directions: 60 poses each, 480 local 1024px renders, one shared orthographic scale, and initial root `(512,844.8)`. Its structural audit reports zero empty/edge-touching frames and less than 0.001 px initial-root error. [Eight-direction GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/eight-direction-guides/eight-directions-one-shot.gif). This is source-mannequin capture, not a finished illustrated sprite package.

The [prepared Blender scene](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/eight-direction-guides/source-rig-eight-view-ready.blend) reopens at 60 fps with exactly eight fixed cameras, no camera animation, and `CAM_SE` active. These eight-view captures are authoritative; the earlier single-camera paint probes use a different SE angle/framing. Independent WeaponLight source guides now follow each canonical blade path, with identical world-space timing in all directions (emit 11, fastest movement 15, stop 18, fade out 22). [Source/trail eight-direction GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/source-trail-guide/eight-directions-with-trail.gif). They must not be overlaid onto the mismatched painted drafts as if approved.

Four new high-detail painted key poses have been generated from full-body Blender guides. Their pose reading improves on the stick-guide studies, but cell registration, blade foreshortening and matte fringes still fail review. No continuous painted action, semantic cutout set, WeaponLight, game preview or production approval has been completed from this reset. The user's Mesh2Motion choice supersedes the older Rokoko/OGA search direction documented below.

An opaque-white single-frame probe produces clean edges and closer weapon placement. Subsequent adjacent-pose batches still move boots and body proportions relative to the fixed guide anchors, so they remain unapproved paint studies. Source and painted GIFs are compared directly without per-pose figure resizing or warping. Do not use the planned 32-frame batch count as a completed-art count; the cutout review audit records how many actually exist.

### Visual regression recovery (21 October 2026)

The fixed SE Blender camera and its 1024px guide captures remain intact in `basicattack-se-iteration-23/source/rokoko-blender-guide/`. The quality regression came after guide capture: the frame-499 painted composite was warped across unrelated poses in `experiments/rig-highres-master-001/`. The warp failed the pose-strain gate on all four sampled frames and visibly distorted the body and sword. It was never admitted as runtime art.

Use the [pre-warp 32-frame painted GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-23/review/basicattack-se-one-shot.gif) as the visual-quality recovery reference. Its high-resolution source paintings are preserved under `source/keyframes/final-master-v1/raw/`. The [shared-root normalization GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-23/experiments/continuity-normalization-002/review/basicattack-se-one-shot.gif) is the registration diagnostic. Neither is production-ready: costume/cape continuity, sword-to-guide alignment, and frame stability still fail review. Do not replace either with the rejected warp. Correct the remaining jumps on the source-pose matched art while preserving its pixels and the locked-camera guide contract.

Owner correction after recovery: discard iteration 23 as the BasicAttack production direction and redraw the action from a newly selected motion. The Rokoko 480–511 guide is now rejected as an attack because it reads as lifting and lowering the sword. OpenGameArt CC0 Sword Attack I and II are the owner-identified attack alternatives. [Iteration 24](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-24/README.md) records their Blender comparison and a 32-pose one-shot motion GIF for Sword Attack II. This is still motion study only. Its high-detail single-frame paint probe fails pose and clean-edge checks; no art or runtime replacement has passed.

Latest motion direction: the owner wants a top-down cut with obvious weight transfer. Sword Attack II is a lateral cut, so it is only a comparison. A CC0 Sword Charge Attack was downloaded from the same OpenGameArt source. Full 85-frame inspection corrected the initial read: after a long overhead wind-up, source frames about 45–55 contain one spinning slash, followed by an extended pose and recovery. A 34-pose [trimmed one-shot GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-24/review/oga-sword-charge-trimmed-spin-one-shot.gif) keeps the strike dense and shortens the redundant holds without changing source motion curves. It is a promising spinning heavy attack study; its aerial support and rotation still need review for ordinary BasicAttack. The available Quaternius jump attack has body movement without a registered sword. The [iteration-24 motion search](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-24/README.md) lists these findings and free MoCap Online and Mixamo sources awaiting clip-level inspection. No overhead motion is approved for painting.

- Use open Ragnarok client source as an architecture reference for composable body/equipment/effect layers, directional sprite actions, and palette handling. Keep Astraeon's art original; Ragnarok code being open-source does not make official game assets open assets.
- Preserve an approved motion and first paint one whole-character master frame for each action, camera angle, and source frame. The thrust-like `Sword_Attack` and Rokoko 480–511 lift/lower segment are rejected. OpenGameArt Sword Attack I and II are under fixed-camera review, with II as the first slash study. Cut head/hair, body/outfit, sword, cape, and effects from those same exact frames; do not generate each layer independently.
- Use the supplied high-detail swordsman images as the current illustration-quality and costume reference. The golden scarf/cloak is on a removable BackAccessory layer and appears in the default reference render.
- Follow Ragnarok's playback rules: Idle and Walk loop without a terminal duplicate; BasicAttack plays once and transitions from a stable recovery pose. Keep `WeaponLight` separate from the sword and synchronized to action, direction, frame, and blade position, as in the Goro client renderer.
- Build the next art pass from one high-detail full master per source pose, then cut separate transparent layers from those exact frames. Use up to 64 temporal poses for a short fast move when the actual source cadence needs them. Do not flatten a character composite and call its empty slots modular.
- Increase target art occupancy from the existing 88px reference height to 112px in the same 160px runtime cell while holding the `(80,132)` root and foot baseline. This adds source pixels for crisp detail without changing the world-space character size.
- Current map acceptance is pending. The prior Wayfarer Capital evidence cannot be used as proof for that gate.

## Progress

### Completed

- Built the 60-bone action-free V3 Swordsman rig with stable root, eight unmirrored directions, and the six required structural guide passes.
- Selected free Mesh2Motion `Idle_Sword`, `Walk`, and initial `Sword_Attack` sources from a pinned CC0 bundle. Idle and Walk remain internal candidates. `Sword_Attack` is now rejected after frame-by-frame visual review because its forward extension reads as a thrust. Source hash and license evidence remain recorded; no V2 motion fallback is used.
- Completed the forced Blender 5.2.2 pipeline run while all three motion clips were candidates. Preflight, retargeting, 192 guide records, six structural passes, and the procedural DEV_ONLY runtime package passed. The current BasicAttack gate is blocked because the source was subsequently rejected on visual review.
- The first V3 identity prompt used a no-cape default. The current owner-directed prompt supersedes it: the golden cape is part of the default look on an independent optional layer.
- Generated two painted Idle, Walk, and BasicAttack sheets with eight directions and eight frames each. The first iteration is retained for comparison. The sharper-prompt iteration has exact prompts, raw inputs, pose guides, hashes, normalized sheets, GIFs, and an import report in [paint job `imagegen-swordsman-v2`](../../authoring/characters/factory-v3/paint-jobs/imagegen-swordsman-v2/selection.md).
- For iteration 2, removed alpha haze and disconnected cross-cell fragments, applied one shared scale (`0.724771`) across all 192 frames, aligned cells to the V3 guide contract, and trimmed pixels outside a guide silhouette dilated by 6px. The normalized character is about 79px tall in a 160×160 cell; root remains `(80,132)`.
- Added the separate `swordsman-male-v3-painted-v2` DEV_ONLY package and a development route. Its browser playback used the default streamed `wayfarer-regional-capital-v75` map and showed Idle, Walk, and BasicAttack without page errors. The owner later identified this as the wrong map, so the route and screenshots are historical only, not current acceptance evidence. Its `983ms` attack marker is a provisional maximum extension, not a validated hit.
- Set the procedural runtime default Back part to transparent. The cape remains an optional separate `BackAccessory` part in that package.
- Added [Ragnarok open-source reference notes](RAGNAROK_OPEN_SOURCE_REFERENCE.md) covering Goro/OpenMidgard layer and action-selection patterns, and the separate license boundary for original game data.
- Added an atlas-based research continuity audit. On painted-v2 it flags every Walk and BasicAttack direction below the research 0.88 mean warning threshold; BasicAttack has an alpha-IoU minimum of `0.292`. It also confirms the independent Weapon part and separate effect are empty in that package.
- Updated the [master prompt](../../authoring/characters/factory-v3/identities/swordsman_master_prompt_v3.txt) and [identity lock](../../authoring/characters/factory-v3/identities/swordsman_identity_v1.json) to require 112px character height, crisp high-detail art, a default golden cloak with a removable no-cloak option, true part sheets, and an independent sword-trail effect.
- Drew a six-file transparent concept pilot for BaseBody, Hair, Outfit, BackAccessory, Weapon, and CosmeticFX. Each is a separate source image; the pilot has no full-character composite. These static concepts are not registered together or ready for the runtime.
- Added a layered-sheet importer that accepts eight-direction sheets with variable frame rows per layer/action and applies the same scale and per-pose transform to every layer. It sets the cloak as the default cosmetic, retains a no-cloak part, and builds `WeaponLight` as its own optional runtime layer. A missing attack effect remains transparent; the rejected `WeaponSlash` sheet is ignored.
- Tested independent ImageGen sheets for Idle and Walk, then stopped that method after review. Those mismatched images remain as diagnostics in the superseded paint job; they are not production source art.
- Replaced the rejected thrust study with the Rokoko `SwordFight_mixamo.fbx` SE overhead wind-up, diagonal downstroke, follow-through, and recovery. Blender samples the original FBX at 63 real poses over source frames 480–511 in half-frame increments at 60 fps. The one-shot review lasts 1,330 ms and holds the final recovery pose for 300 ms.
- Stabilized the SE study with one shared left support foot, a shared +10 px registration correction, and zero sole-baseline error in all 63 poses. Two-bone IK follows the previous solution; projected limb lengths stay within 0.78–1.12×. Head/neck/waist maximum steps are 1.05/0.96/0.93 px and the sword hand follows the guide exactly. The right elbow still moves up to 14.52 px in one 60 fps step; the non-sword hand misses by 16.82 px and the other foot by 10.40 px.
- Rebuilt the trail as a separate original-gradient `WeaponLight`. It starts midway through the fast stroke at source frame 498.5, reaches 28 px width at frame 499, and fades after impact. The effect follows the Rokoko sword proxy and stays off the face, but it still obscures too much of the tunic.
- The current iteration 22 is **review-only and not approved**. Its 320 px donor art is softer than the owner's reference, body and cape shapes do not yet match the motion guide, the cape remains baked into `Outfit`, and only SE is available. Review the GIF, guide comparison, trail, and pose audit in [iteration 22](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-22/README.md).
- Added `cutout_master_sheet.py` for pixel-label cutouts from one complete eight-direction master sheet per action, with variable frame rows. It preserves each frame's camera, pose, pixels, alpha, and layer placement, and verifies exact reconstruction before any runtime import.
- Added a small browser label editor with per-frame camera selection, zoomed mask painting, and grayscale labels export. The master and labels stay at the exact same eight-column grid before cutout.
- Added `review_layered_sheets.py` to assemble cutouts, produce GIFs, and measure frame continuity before packaging. The Idle `0.835` and Walk `0.785` results from the abandoned independent-layer experiment are retained only to explain why that method was stopped.
- Updated the motion sampler to produce 16 loop samples over `[0,1)` without duplicating the endpoint and to distribute BasicAttack in-between samples across the largest remaining phase gaps. A previous midpoint-selection bug clustered attack samples near the terminal pose; that is corrected.
- Added review-only 16-frame timing plans for Idle, Walk, and BasicAttack. Walk has 16 equal 104ms holds with footstep markers at frames 0 and 8; BasicAttack remains a one-shot and keeps `983ms` only as a provisional maximum-extension marker.
- Updated the master cutout, normalization, label editor, importer, and review GIF tools to accept variable frame rows. Existing painted masters remain eight frames and are explicitly a discarded smoothness pilot.
- Rendered 16-phase eight-direction Blender pose guides for Idle, Walk, and BasicAttack. Idle guide seam alpha IoU is `0.969`; Walk guide mean seam is `0.852`, with the weakest facing seam at `0.760` and weakest adjacent pair at `0.680`. These are low-detail rig silhouette diagnostics, not painted-art or natural-motion scores. BasicAttack contact is frame 8 and recovery starts at frame 13.
- Added `assemble_motion_guide.py` to assemble 16-frame views, create correctly looped Idle/Walk GIFs, keep BasicAttack one-shot, and record timing, hashes, and silhouette diagnostics.
- Corrected review GIF behavior: Idle/Walk loop; BasicAttack plays once and holds its recovery pose. The BasicAttack GIF no longer jumps from its last frame to anticipation.
- The first `WeaponSlash` vector experiment is rejected after visual review because its strokes cross the character and do not follow the blade. It remains diagnostic only; neither it nor the original broad crescent is admitted. The next pass uses a separate frame-synchronized `WeaponLight` sheet based on Goro's renderer pattern.
- Generated a review-only one-shot BasicAttack GIF and per-layer breakdown using the rejected `WeaponSlash` pilot. These files document the failed effect experiment and should not be treated as approval art.
- Rendered 16-phase, eight-direction Idle, Walk, and BasicAttack pose guides from the selected motion timelines with Blender 5.2.2. The guides and source hashes are in [paint-job v2](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/README.md); they are timing/pose guidance, not character artwork.
- Generated a 16-frame, single-SE painted BasicAttack candidate and an infinite-loop GIF for seam review. The loop GIF is review-only; the production BasicAttack remains one-shot under the RO playback contract. Rejected this candidate because several sword poses touch or cross cell bounds, so the blade is cut at the edges; no `WeaponLight` was painted or imported. Its loop seam alpha IoU is `0.805`, and its lowest adjacent-frame IoU is `0.445`; these measurements do not override the visible clipping failure. See [the rejected SE prototype](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-2/README.md).
- Generated a tighter low-diagonal SE attack variant. Its review GIF locks the final recovery frame to the first guard pose, giving a `1.0` seam by construction; the production clip still plays once. This variant is also rejected because the blade clips the cell edge in frames 9–10 and a detached blade fragment appears in frame 11. Its minimum adjacent-frame alpha IoU is `0.598`; it has no `WeaponLight` or cutout layers. See [the compact SE trial](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-3/README.md).
- Generated and composited an effect-only `WeaponLight` test for frames 5–12. It repeats similar curved strokes and crosses the torso instead of following the sword, so it is rejected and remains diagnostic. No effect art is admitted.
- Added a separate tip-motion `WeaponLight` prototype for the compact SE trial. It follows detected blade-tip motion in frames 6–12 and adds a small contact glint at frame 8; its 2× review GIF is in the prototype README. It remains review-only because the source master clips the blade and covers only SE.
- Retracted an earlier motion audit that described `Sword_Attack` source frames 24–33 as a lateral sweep. Direct SE guide review shows a forward sword extension held across frame indices 4–8; this reads as a thrust and fails the requested slash. The source is rejected pending replacement. Phase `.50` / frame index 8 / 983ms is only a provisional maximum-extension marker, not a validated hit; motion curves and sampled poses remain unchanged.
- Updated an effect-only 4×4 `WeaponLight` trial based on the owner's rough slash sample, with an original plum-gray/lavender-silver/warm-ivory gradient and 1.35× thickness. It starts before contact, remains visible at the provisional frame- 8 extension, tapers in frame 9, and is clear before recovery. The separate SE layer and one-shot GIF remain review-only; the underlying motion and painted sword path are rejected.
- Rejected the first 16×8 full-master generation because it retained red fringes, produced sub-160px cells, and did not show enough pose change. It was not imported or cut into parts.
- Corrected Character Studio's one-shot playback: it no longer restarts BasicAttack 700ms after completion; the preview holds the final pose and provides a Replay button. The existing sprite sampler already held one-shot clips on their final frame.
- Created full 8×8 character masters for Idle, Walk, and BasicAttack using the fantasy swordsman identity and existing guide poses. BasicAttack includes the visible sword and a separate gold-white sweep trail. These eight-frame masters are retained for comparison, not accepted as smooth animation.
- Applied the same `0.949153` scale and root `(80,132)` to all three sheets, targeting a 112px visible character height inside each 160px cell. Source action frame order and duration data stay intact.
- Cut all three masters into registered `BaseBody`, `HeadHair`, `Outfit`, `Weapon`, `BackAccessory`, `CosmeticFX`, and empty `Headgear` sheets. All three reconstruct exactly with `0` mismatches (`363,448` Idle, `287,882` Walk, and `322,106` BasicAttack visible pixels).
- Refined each head label seed to include visible warm face pixels with the hair. The refinement is a geometric/color heuristic and still needs visual inspection; it does not generate hidden face or scalp art.
- Added native-resolution eight-direction review GIFs for all three actions and per-layer breakdowns. The pose/art review remains open; Walk (`0.8289`) and BasicAttack (`0.5529`) are below the research `0.88` silhouette-continuity warning. These figures are diagnostics, not art-quality scores, and large attack poses can intentionally change silhouette.
- The cutouts and detailed reports are in the [master-cutout paint job](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/README.md). The source master is the art source; the mask only supplies labels.

### Current review GIFs

The established Idle and Walk GIFs still show the eight-frame paint pilot, so they are diagnostic only. Idle and Walk loop; BasicAttack plays once and holds recovery. Playback metadata is correct, but the Idle/Walk artwork still pops at the loop seam and has too few painted poses. Walk's worst seam is `0.614` silhouette IoU. Iteration 8's one-shot SE-only trail and guide comparison are historical diagnostics; the thrust-like source was rejected and the current Rokoko motion study is in iteration 22. No acceptable full-view painted master has been admitted, and no candidate has been previewed on the requested map.

- [Idle master-cutout GIF, eight directions](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/review/layered-v3-idle-8-directions.gif)
- [Walk master-cutout GIF, eight directions](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/review/layered-v3-walk-8-directions.gif)
- [BasicAttack master-cutout GIF, eight directions](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/review/layered-v3-basicattack-8-directions.gif)
- [BasicAttack layer breakdown](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/review/layered-v3-basicattack-layer-breakdown.png)
- [Rejected WeaponSlash BasicAttack GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/review/weapon-slash-pilot/layered-v3-basicattack-8-directions.gif) — diagnostic only; the effect crosses the character.
- [Rejected WeaponSlash layer breakdown](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/review/weapon-slash-pilot/layered-v3-basicattack-layer-breakdown.png)
- [Idle 16-frame pose guide GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/guides/idle-motion-guide-16-8directions.gif) — rig guide only.
- [Walk 16-frame pose guide GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/guides/walk-motion-guide-16-8directions.gif) — rig guide only.
- [BasicAttack 16-frame pose guide GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/guides/basicattack-motion-guide-16-8directions.gif) — one-shot rig guide only.
- [Iteration 8 SE trail one-shot GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-8/review/basicattack-se-weaponlight-one-shot.gif) — review-only overlay on rejected art and motion.
- [SE guide and painted-trail comparison GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-8/review/motion-guide-vs-painted-trail-one-shot.gif) — 16-frame one-shot with the same timing on both sides.
- [Current Rokoko SE guide comparison and trail GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-22/review/rokoko-vs-swordsman-one-shot.gif) — 63 source-time poses at 60 fps; review-only.
- [Frame-by-frame guide and painted sword comparison](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-8/review/motion-guide-vs-painted-sword-4x4.png) — diagnostic only.
- [Sword alignment review](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-8/review/motion-alignment-review.json) — records the mismatch and replacement gate.
- [Iteration 4 transparent WeaponLight sheet](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-4/layers/WeaponLight/weaponlight-se-4x4.png) — separate effect layer.
- [BasicAttack full master](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/source/BasicAttack/master.png)

These previous fused painted-v2 motion reviews remain available to show the earlier quality gap. They are not the new layered candidate and do not count as owner-approved art.

- [Idle, eight directions](evidence/imagegen-swordsman-v2/v3-ai-painted-idle-8-directions.gif)
- [Walk, eight directions](evidence/imagegen-swordsman-v2/v3-ai-painted-walk-8-directions.gif)
- [BasicAttack, eight directions](evidence/imagegen-swordsman-v2/v3-ai-painted-basicattack-8-directions.gif)
- [BasicAttack with cape on/off, earlier procedural comparison](evidence/v3-basicattack-south-cape-compare.gif)

Iteration 2 removes detached edge artifacts after guide-mask cleanup but remains too small and soft for the owner's requested visual quality. It is retained as a prior candidate, not as a quality pass. The images have not been approved by the owner.

### Superseded independent-layer experiment (not runtime art)

These previews are assembled from independently generated layer sheets. They show mismatched details and fail the research continuity warning. The owner has redirected authoring to cutouts from one complete master frame; these previews are retained only to record why.

- [Idle, eight directions](../../authoring/characters/factory-v3/paint-jobs/imagegen-swordsman-layered-v2/review/layered-v3-idle-8-directions.gif)
- [Walk, eight directions](../../authoring/characters/factory-v3/paint-jobs/imagegen-swordsman-layered-v2/review/layered-v3-walk-8-directions.gif)
- [Idle layer breakdown](../../authoring/characters/factory-v3/paint-jobs/imagegen-swordsman-layered-v2/review/layered-v3-idle-layer-breakdown.png)
- [Walk layer breakdown](../../authoring/characters/factory-v3/paint-jobs/imagegen-swordsman-layered-v2/review/layered-v3-walk-layer-breakdown.png)
- [Continuity and source report](../../authoring/characters/factory-v3/paint-jobs/imagegen-swordsman-layered-v2/review/layered-v3-review-report.json)

## Still partial

- **Visual quality and motion:** the current eight-frame masters remain below the requested smoothness bar. Idle/Walk have 16-phase guides; BasicAttack now has a 63-pose Rokoko SE review guide and a stable one-shot study. Iteration 22 is not a painted eight-direction master; its donor art is soft and does not match the motion closely enough. The Walk guide has a weak west/east silhouette seam; Idle is subtle. Earlier full-master trials were rejected for cell-boundary clipping, red fringes, or insufficient pose change.
- **Layering:** all three actions now have exact registered visible `BaseBody`, `HeadHair`, `Outfit`, `Weapon`, `BackAccessory`, and `CosmeticFX` cutouts. `Headgear` is empty. Semantic boundaries remain heuristic and need review. Hidden surfaces have not been painted, so outfit/hair/cape swaps that expose them are not production-ready.
- **Other actions:** Run, Hit, Death, Dash, Guard, and SkillAction are placeholders and still need free-source review and production art.
- **Production approval:** the painted pixels are provider-generated, so no CC0 claim is made for them. The runtime package remains `DEV_ONLY`, `PLACEHOLDER`, `NOT_FINAL_ART`, and `OWNER_APPROVAL_PENDING`.

## Historical route; not current map evidence

The prior development browser route used the default streamed Wayfarer Capital map, which the owner identified as the wrong map for the requested review. Do not treat its screenshots as current in-game acceptance evidence:

`?qa=1&swordsman=v3-painted-v2`

The route shows the candidate in the character creator and actual player renderer. Browser screenshots and the QA report are in [the Wayfarer Capital evidence folder](evidence/imagegen-swordsman-v2/). It does not mark the candidate approved or production-admitted.

## Remaining acceptance gates

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Canonical rig | **PASS** | 60 bones, stable root, zero V2 actions. |
| Free motion sources | **PARTIAL** | Mesh2Motion CC0 evidence is recorded. The old thrust-like BasicAttack is rejected; the Rokoko fight clip is now the SE review candidate. |
| Idle / Walk / BasicAttack | **REVIEW CANDIDATE + HIGH-RES REPAINT REQUIRED** | Idle/Walk remain candidates. BasicAttack now has 32 high-resolution SE paintings, but iteration 23 fails character-continuity and sword-guide checks; it lacks complete directions, accepted cutouts, and owner review. |
| Eight directions and structural passes | **PASS** | 192 records, six passes, unmirrored directions. |
| Painted identity and fantasy readability | **REPAINT REQUIRED** | Iteration 22's donor art is too soft and its trail covers too much tunic. Iteration 23 improves resolution but has frame-to-frame body/cape drift, sword-angle errors, an unaligned trail, and no semantic cutouts; only SE is covered. |
| Cloak toggling | **PARTIAL** | Earlier procedural on/off comparison exists. Next candidate targets a default golden cloak and transparent no-cloak variant. |
| Frame-matched cutout layers | **CANDIDATE** | The earlier Idle, Walk, and BasicAttack pilot cutouts recompose with `0` pixel mismatch. Iteration 23 has only a separate `WeaponLight`; body, head/hair, outfit, sword, and back accessory layers are still missing. Hidden surfaces and manual semantic-mask review remain. |
| Remaining six actions | **PENDING** | Static placeholders only. |
| Runtime package | **PASS as DEV_ONLY** | Schema/atlas validation passes; no production admission. |
| Actual game preview | **HISTORICAL ONLY / MAP REJECTED** | Prior preview used Wayfarer Capital, which the owner said is the wrong map. New layered candidate and target-map preview are pending. |
| Owner approval | **PENDING** | The eight-frame painted GIFs and iterations 22–23 remain below the requested quality bar. The earlier thrust and its painted path are rejected; the current Rokoko motion remains review-only. The 16-frame eight-direction GIFs remain low-detail rig guides; stable high-detail layered art and a target-map preview remain outstanding. |

## Validation record

| Check | Result | Detail |
|---|---|---|
| Factory `--stage all --force` | **PASS** | Blender 5.2.2; rig, motion, guide, handoff, and procedural package stages completed. |
| Motion production gate | **BLOCKED** | Iteration 22 is a review-only SE pose study. It is not approved motion/art and lacks complete directions and a game preview. |
| Painted importer | **PASS** | 192 cells, shared 0.752381 scale, cleanup and alignment report written to the paint job. |
| Runtime candidate validator | **PASS** | Iteration 2: 9 clip definitions, 20,763,712 decoded atlas bytes, no schema errors. |
| Procedural runtime validator | **PASS** | 9 clip definitions; no schema errors. |
| Painted-sheet normalization test | **PASS** | Shared scale, alpha cleanup, full frame count, and guide-mask containment. |
| Superseded independent-layer experiment | **REJECTED / HISTORICAL** | Earlier separate-sheet Idle mean silhouette IoU `0.835`; Walk `0.785`; both below the research 0.88 warning. These mismatched sheets are retained as diagnostics, not current masters. |
| Three-action master cutouts | **PASS: EXACT RECONSTRUCTION / PILOT REJECTED FOR SMOOTHNESS** | Idle, Walk, BasicAttack each have an 8×8 master, aligned layer sheets, and `0` reconstruction mismatches. This validates pixel registration only; the replacement target is 8×16. |
| Sixteen-frame timing | **PASS: SAMPLING PLAN** | Idle, Walk, BasicAttack plans each have 16 unique frame phases. The SE-only painted trial is not a direction-complete master and has no runtime layers. |
| Frame continuity | **DIAGNOSTIC ONLY / BELOW WARNING** | Eight-frame pilot: Idle mean/min `0.9073 / 0.7739`; Walk `0.8289 / 0.6138`; BasicAttack `0.5529 / 0.3469`. The rejected compact SE trial has minimum adjacent alpha IoU `0.598`; its `1.0` loop seam is created by locking recovery to the first guard frame. Blade clipping still fails the review. |
| Prior browser preview | **DEVELOPMENT-ONLY / MAP REJECTED** | The attack marker at 983ms is now described as provisional maximum extension; the owner also rejected Wayfarer Capital as the wrong map. |

## Latest review: iteration 23 stability findings (2026-10-20)

[Iteration 23's README](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-23/README.md) links its 32-frame one-shot GIF, guide comparison, trail contact, and audits.

- The 1280px canvas uses root `(640,1056)`, mapping to the 320px guide root `(160,264)`. The one-shot lasts 1,330ms and holds recovery for 300ms. This proves the exported canvas root is constant; it does not prove the character is stable.
- The raw full-character paintings vary from 790px to 1,186.5px in detected head-to-floor height. The exporter compensates with per-frame scales from 0.5284 to 0.8177. The source pose and silhouette still change between frames, so this sequence is **REJECTED FOR CONTINUITY / NOT APPROVED**.
- In the original art, frame 498.0's sword is about −43° and follows the guide; frame 498.5's sword points nearly straight down, about 90° away from its guide axis near +11°. A new full-body 498.5 guide paintover corrects the sword direction but changes the cloak and full silhouette. The guide paintovers at 498.0 and 499.0 still miss their blade axes. None is promoted to the master.
- The 40px `WeaponLight` ribbon uses the iteration-22 research weapon path, while the iteration-23 sword is independently painted. The contact sheet shows the trail floating near the head instead of tracking the drawn blade. Regenerate it only after the painted sword and guide share a frame-matched path.
- Iteration 23 does not yet contain registered `BaseBody`, `HeadHair`, `Outfit`, `Weapon`, and `BackAccessory` cuts. The screen-right support-foot anchoring trial shifts the character left in the cell and is rejected.
- The next candidate must keep one master identity and shared root/scale through the action, paint or deform registered cutouts against the exact Blender guides, preserve the cape as a separate part, and pass the blade-axis and trail alignment review before a game preview.

## Latest owner feedback: character stability (2026-10-20)

- Re-normalized the existing 32 iteration-23 poses to a 1280×1280 canvas at the shared `(640,1056)` root. All frames now match `1.1×` of their corresponding guide head-to-floor height, with zero canvas-limited frames. This removes the size jump that the previous canvas edge introduced; it is a registration result only.
- Manual guide comparison still fails pose continuity at the lead-in and strike. The original raw paintings require source scale factors from `0.505962` to `0.819327`, and the cape/body silhouette changes between independent generations. A stable root and matched head-to-floor measurement do not make those poses or character contours stable.
- A common 2×2 generation pass at frames 480, 493, 499, and 511 holds the costume and palette more consistently, but still misses guide landmarks at the guard and strike, omits the sword, and does not supply the in-between frames. A 480–483 probe collapses its four subtle source poses into a repeated drawing and is rejected.
- A separate `Weapon`-layer proof at frames 498.5, 499, and 499.5 uses a hand-annotated fist pivot and a standalone high-detail sword. The three measured blade angles match their guide axes, but the full pose still misses the guide and no matching `WeaponLight` exists. This is a three-frame transform proof only.
- Current artifacts: [32-frame continuity audit](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-23/experiments/continuity-normalization-002/README.md) and [four-pose probe](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-23/experiments/guide-locked-four-pose-001/README.md). Both are **REVIEW ONLY / NOT APPROVED**. Continue from registered pose-matched layers or a deformation approach that preserves the high-detail identity and passes native-size review.

| Iteration 23 visual audit | Result | Evidence |
|---|---|---|
| Shared export root | **PASS AS REGISTRATION ONLY** | `(640,1056)` at 1280px; maps to `(160,264)` at 320px. |
| Character continuity | **REJECTED** | 32 high-resolution frames need frame-specific scale factors `0.5284–0.8177`; body and cape silhouettes change. |
| Sword-to-guide alignment | **REJECTED** | Source frame 498.5 misses the guide axis by about 90°; full-body guide paintovers at 498.0 and 499.0 also drift. |
| WeaponLight alignment | **REJECTED** | Current trail path comes from iteration 22 and does not follow the iteration-23 sword. |
| Semantic cutouts | **PENDING** | Only `WeaponLight` is separate; character layer cuts have not been made. |

| Latest continuity check | Result | Evidence |
|---|---|---|
| Shared canvas/root and guide-relative height | **PASS AS REGISTRATION ONLY** | 32 poses, 1280px canvas, root `(640,1056)`, zero canvas caps, measured height ratio `0.999999–1.000001` of the requested `1.1×` guide height. |
| Body pose and character continuity | **FAIL** | Lead-in/strike poses still miss the guides; independent source scale factors span `0.505962–0.819327`; cape/body contours drift. |
| Common four-pose identity probe | **PARTIAL / NOT APPROVED** | Costume consistency improves at frames 480, 493, 499, 511; guide landmarks are still missed and there are no layers or sword. |
| Three-frame separate weapon transform | **PASS AS MECHANICS ONLY** | Independent sword and fist pivot; exact axis audit for 498.5/499/499.5. Full pose and trail still fail/pending. |
| Adjacent 480–483 pose probe | **REJECTED** | It collapses four subtle guide changes into one repeated pose. |

See [the implementation record](PRODUCTION_FACTORY_V3.md), [build evidence](evidence/production-factory-v3-motion.json), [iteration 2 paint job](../../authoring/characters/factory-v3/paint-jobs/imagegen-swordsman-v2/imported/job.json), and [Wayfarer Capital browser report](evidence/imagegen-swordsman-v2/wayfarer-capital-review.json) for the full progression and provenance.

## Latest pose-fit finding (2026-10-20)

- Tested one high-resolution frame-499 master against four Rokoko guides using the research fixed-mesh method. The single master is pose-incompatible: all four target poses exceed the `0.78–1.12×` limb-segment strain range, the whole-body warp would stretch the painted torso `1.691–1.737×` to match the mannequin, one forearm must compress to `0.509×`, and the mesh flips 29 triangles across the four frames.
- The warped render is **REJECTED**. This identifies a second source of visible character instability: the source artwork pose and guide pose disagree, so fixed root and normalized height still bend the character's torso, arms, and armor.
- Added a pose-strain preflight to the experimental high-resolution warper and documented the exact rejection in [the iteration-23 pilot report](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-23/experiments/rig-highres-master-001/README.md). Next art must start from a guide-matched full-frame pose, then use same-frame cutouts or only deformation that passes the strain and visual gates.

## Owner update — optional cloak (2026-10-21)

The owner permits removing the long cloak if its animation or separation reduces quality. The working art direction prioritizes the weighted Mesh2Motion cut, wrist and sword fidelity, stable body registration, and sharp artwork. Retain a short gold scarf; a long cloak is optional and must not block delivery. This changes art direction only: no replacement animation has passed visual review as a result of this update.

### No-cloak art and editable-cutout follow-up

Produced three crisp no-cloak pose studies and an editable OpenRaster guard master with HeadHair, visible Weapon, and combined BodyOutfit layers. Disjoint visible pixels recompose with zero mismatches. Full artifact and prompt provenance: `authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-mesh2motion-reset/no-cloak-study/README.md`.

The no-cloak guard correction reduces manually measured grip error from about 55px to 14px at 1024px, but its blade tip is still about 39px off. The follow-through study misses the source grip by about 121px. All three are rejected for production registration. No runtime animation is replaced, no completed GIF or equipment separation is claimed, and the source-rig guide remains authoritative. Independent image generation still changes anatomy and framing; cape removal alone is insufficient.

### Continuous GIF requested for owner inspection

Added `no-cloak-continuous-review/`: sixteen poses generated together, no long cloak, normal-cadence and 3x-slow one-shot GIFs, source-versus-paint comparison, original sheets and prompt provenance. Complete figure extraction avoids the uneven generated grid splitting boots/blades; four shared row packing translations are recorded rather than concealed. All 16 output figures remain in bounds. These are review drafts, not approved source registration, equipment separation or runtime replacement.

### Same-frame cosmetic swaps and trail review

Owner liked the sixteen-pose no-cloak animation and requested practical per-frame cutouts with alternate heads, costumes and weapons. Added `modular-swaps-review/`: two original skins, 96 transparent component frames (HeadHair / BodyCostume / Weapon), independent WeaponLight frames, matching sheets and OpenRaster documents, five isolated-combination GIFs, a 3x-slow comparison and an offline interactive viewer. The original accepted frames remain pixel-identical after recomposition; both skins have zero mismatches over 32 pose/skin combinations. Manual boundaries were revised after visible scarf/sleeve and blade residue was found. Trail follows manually annotated painted blade positions, with early onset, a curved graded sweep and independent fade. This remains a sixteen-pose SE cosmetic prototype; BodyCostume is the whole clothed body, not separate hidden anatomy and clothing. No runtime or eight-direction alternate set is claimed.

Owner trail correction: the first modular preview used the shortest projected angle and drew its ribbon behind the body. The owner rejected that side. Rebuilt the effect with a consistent forward clockwise winding through the strike, reduced its history to 0.9 sampled frames, and composed it above the costume but below the head, gripping glove and blade. Added a separate visible-glove occlusion support layer and `forward-trail-slow.gif`; the interactive viewer and all cosmetic comparisons now use the corrected foreground effect. This is a visual-review candidate, not an owner approval of the corrected effect.

Owner timing/length correction: trail must appear after the cut has started and stay short. Removed all wind-up emission (frames 0–3 are transparent), emit at low follow-through frame 4 only, retain a 25%-opacity afterimage at frame 5, then clear it. Recent painted tip travel is capped at 0.65x the contact blade length; this is a review-length bound, not a physical force estimate. The forward sweep and glove/blade occlusion are retained. Updated every GIF, effect sheet, OpenRaster file and offline viewer.

Owner requested separate sprite sheets after the trail correction. Added an explicit sheet manifest indexing six primary cosmetic sheets, two glove-occlusion support sheets and one independent trail sheet, all transparent 2048px with 4x4 cells of 512px. All 144 cells match their corresponding frame PNGs in alpha and visible RGBA. Curated ZIP delivery includes sheets, metadata and stacking instructions; no individual-part recentering is required.

## Four-direction attack experiment — owner correction (2026-10-21)

Owner corrected the attack scope to four diagonal views (SW/NW/NE/SE), following the requested RO-style presentation. Added `four-direction-attack-review/`: 64 gold-skin painted poses, real camera references without mirroring, same-frame HeadHair/BodyCostume/Weapon cutouts, short after-cut front/back WeaponLight layers, glove overlap support, individual GIFs, combined normal/slow GIFs, offline direction/layer viewer, per-view OpenRaster documents and eight combined transparent 2048x8192 sheets. All 64 reconstructions have zero mismatches; all 512 sheet cells match their individual alpha/visible RGBA, and effect bounds/timing checks pass.

The original source Blender scene was opened for world torso landmarks used in approximate front/back trail occlusion. Research alpha-IoU warnings and manual blade-angle comparisons are recorded in `quality-audit.json`. NE pose 8 retains a blade-foreshortening discrepancy (source projection about 8.6px at 1024px); semantic collar/guard edges also remain for owner inspection. This is a four-view art experiment, with no runtime replacement or final naturalness claim. The main prompt now records the four-direction BasicAttack exception.

## 2026-10-21 — action split, registration repair and layered factory

Owner explicitly prefers Mesh2Motion as the primary motion source; recorded in the identity master prompt, source policy and layered action catalog. The large B overhead attack is now **SkillOverhead**, preserved separately in `basicattack-mesh2motion-reset/skill-overhead-registered`. Manual visible pelvis anchors register all 64 poses to their matching actual camera projection at one fixed 0.5 scale; all same-frame layers and FX receive the identical integer translation. No body warp or per-frame fitting. Residuals describe annotation rounding, not independently measured anatomical error. Existing illustration drift and NE recovery blade foreshortening remain review limits.

**BasicAttack** has a new four-view, 16-pose-per-view original-rig `Sword_Attack` compact review in `basic-attack-simple`: 64 new illustrated poses, separate HeadHair/BodyCostume/Weapon/hand-overlap/FX, late short trail at 7 with fade 8, native 512px masters, separate combined sheets and per-view ORA. Historical rejection of Sword_Attack as thrust-like is preserved: this native-rig/knuckle-sword/cadence variant is a re-evaluation, not automatic acceptance. Exact image prompts, raw sheets, manual annotation inputs, real-camera guides and source/license provenance are retained.

`configs/layered_action_catalog.json` and `tools/character_factory_v3/layered_action_factory.py --action all` rebuild both registered actions, verify the immutable source GLB digest/license-evidence presence and write receipts/viewers/sheets. `package_layered_factory_review.py` exports clear 2×2 GIFs, a two-action offline layer viewer and a separate-sheet ZIP. 128 total poses reconstruct their packed master pixels; 1024 exported sheet cells match; no FX touches a canvas edge. These pixel audits do not approve natural motion, wrist anatomy, semantic mask boundaries or runtime use. Browser interactions were not automated. Existing Idle/Walk source selections are retained; Block/Hit/Death are cataloged source possibilities, not newly completed art.
