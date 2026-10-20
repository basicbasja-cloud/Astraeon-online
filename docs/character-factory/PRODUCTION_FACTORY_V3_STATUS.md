# Production Factory V3 status and handoff

**Branch:** `character/production-factory-v3`
**Target:** Male Swordsman
**Updated:** 20 October 2026
**Overall:** `EIGHT_FRAME_PILOT_BELOW_SMOOTHNESS_BAR / THREE_16_FRAME_POSE_GUIDES_READY / SE_SWEEP_TRAIL_REVIEW_ONLY / PAINTED_MASTERS_AND_WEAPONLIGHT_PENDING`
**Runtime admission:** `DEV_ONLY / NOT_APPROVED`

The existing painted-v2 package is still a fused composite. The owner rejected its Wayfarer Capital screenshots because that is not the requested map; they are retained only as historical development evidence and do not count as a successful current-map visual review. The owner supplied clearer art references and directed that hair, outfit, weapon, cape, and effects be drawn as independent layers. V3 remains development-only and is not production-complete.

## Current owner direction

- Use open Ragnarok client source as an architecture reference for composable body/equipment/effect layers, directional sprite actions, and palette handling. Keep Astraeon's art original; Ragnarok code being open-source does not make official game assets open assets.
- Preserve the existing motion and first paint one whole-character master frame for each action, camera angle, and source frame. Cut head/hair, body/outfit, sword, cape, and effects from those same exact frames; do not generate each layer independently.
- Use the supplied high-detail swordsman images as the current illustration-quality and costume reference. The golden scarf/cloak is on a removable BackAccessory layer and appears in the default reference render.
- Follow Ragnarok's playback rules: Idle and Walk loop without a terminal duplicate; BasicAttack plays once and transitions from a stable recovery pose. Keep `WeaponLight` separate from the sword and synchronized to action, direction, frame, and blade position, as in the Goro client renderer.
- Build the next art pass from one 16-frame full master per action, then cut separate transparent layers from those exact frames. Do not flatten a character composite and call its empty slots modular.
- Increase target art occupancy from the existing 88px reference height to 112px in the same 160px runtime cell while holding the `(80,132)` root and foot baseline. This adds source pixels for crisp detail without changing the world-space character size.
- Current map acceptance is pending. The prior Wayfarer Capital evidence cannot be used as proof for that gate.

## Progress

### Completed

- Built the 60-bone action-free V3 Swordsman rig with stable root, eight unmirrored directions, and the six required structural guide passes.
- Selected free Mesh2Motion `Idle_Sword`, `Walk`, and `Sword_Attack` sources from a pinned CC0 bundle. Recorded file hash, source skeleton, license evidence, retarget details, events, and frame timings. No login or credential was needed; no V2 motion fallback is used.
- Completed the forced Blender 5.2.2 pipeline run. Preflight, retargeting, 192 guide records, six structural passes, and the procedural DEV_ONLY runtime package passed. The motion gate correctly remains blocked because all three clips are owner-review candidates.
- The first V3 identity prompt used a no-cape default. The current owner-directed prompt supersedes it: the golden cape is part of the default look on an independent optional layer.
- Generated two painted Idle, Walk, and BasicAttack sheets with eight directions and eight frames each. The first iteration is retained for comparison. The sharper-prompt iteration has exact prompts, raw inputs, pose guides, hashes, normalized sheets, GIFs, and an import report in [paint job `imagegen-swordsman-v2`](../../authoring/characters/factory-v3/paint-jobs/imagegen-swordsman-v2/selection.md).
- For iteration 2, removed alpha haze and disconnected cross-cell fragments, applied one shared scale (`0.724771`) across all 192 frames, aligned cells to the V3 guide contract, and trimmed pixels outside a guide silhouette dilated by 6px. The normalized character is about 79px tall in a 160×160 cell; root remains `(80,132)`.
- Added the separate `swordsman-male-v3-painted-v2` DEV_ONLY package and a development route. Its browser playback used the default streamed `wayfarer-regional-capital-v75` map and showed Idle, Walk, and BasicAttack without page errors. The owner later identified this as the wrong map, so the route and screenshots are historical only, not current acceptance evidence. Its attack clip contact marker is at `983ms`.
- Set the procedural runtime default Back part to transparent. The cape remains an optional separate `BackAccessory` part in that package.
- Added [Ragnarok open-source reference notes](RAGNAROK_OPEN_SOURCE_REFERENCE.md) covering Goro/OpenMidgard layer and action-selection patterns, and the separate license boundary for original game data.
- Added an atlas-based research continuity audit. On painted-v2 it flags every Walk and BasicAttack direction below the research 0.88 mean warning threshold; BasicAttack has an alpha-IoU minimum of `0.292`. It also confirms the independent Weapon part and separate effect are empty in that package.
- Updated the [master prompt](../../authoring/characters/factory-v3/identities/swordsman_master_prompt_v3.txt) and [identity lock](../../authoring/characters/factory-v3/identities/swordsman_identity_v1.json) to require 112px character height, crisp high-detail art, a default golden cloak with a removable no-cloak option, true part sheets, and an independent sword-trail effect.
- Drew a six-file transparent concept pilot for BaseBody, Hair, Outfit, BackAccessory, Weapon, and CosmeticFX. Each is a separate source image; the pilot has no full-character composite. These static concepts are not registered together or ready for the runtime.
- Added a layered-sheet importer that accepts eight-direction sheets with variable frame rows per layer/action and applies the same scale and per-pose transform to every layer. It sets the cloak as the default cosmetic, retains a no-cloak part, and builds `WeaponLight` as its own optional runtime layer. A missing attack effect remains transparent; the rejected `WeaponSlash` sheet is ignored.
- Tested independent ImageGen sheets for Idle and Walk, then stopped that method after review. Those mismatched images remain as diagnostics in the superseded paint job; they are not production source art.
- Added `cutout_master_sheet.py` for pixel-label cutouts from one complete eight-direction master sheet per action, with variable frame rows. It preserves each frame's camera, pose, pixels, alpha, and layer placement, and verifies exact reconstruction before any runtime import.
- Added a small browser label editor with per-frame camera selection, zoomed mask painting, and grayscale labels export. The master and labels stay at the exact same eight-column grid before cutout.
- Added `review_layered_sheets.py` to assemble cutouts, produce GIFs, and measure frame continuity before packaging. The Idle `0.835` and Walk `0.785` results from the abandoned independent-layer experiment are retained only to explain why that method was stopped.
- Updated the motion sampler to produce 16 loop samples over `[0,1)` without duplicating the endpoint and to distribute BasicAttack in-between samples across the largest remaining phase gaps. A previous midpoint-selection bug clustered attack samples near the terminal pose; that is corrected.
- Added review-only 16-frame timing plans for Idle, Walk, and BasicAttack. Walk has 16 equal 104ms holds with footstep markers at frames 0 and 8; BasicAttack preserves contact at 983ms and remains a one-shot clip.
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
- Re-audited the selected `Sword_Attack` source. The strongest lateral sweep is across source frames 24–33; the prior contact event at phase `0.50` / frame 8 preceded it. Retimed the candidate contact event to phase `0.63` / frame 10 / 1239ms and follow-through to `0.735`; the motion curves and sampled poses did not change.
- Added an effect-only 4×4 `WeaponLight` atlas based on the owner's rough slash sample, then applied an original plum-gray/lavender-silver/warm-ivory gradient. Its separate transparent frames are remapped onto the actual SE strike window and shown in a one-shot GIF with a recovery hold. This is an unapproved, single-facing prototype; the base art still has red fringe and clipped blade pixels.
- Rejected the first 16×8 full-master generation because it retained red fringes, produced sub-160px cells, and did not show enough pose change. It was not imported or cut into parts.
- Corrected Character Studio's one-shot playback: it no longer restarts BasicAttack 700ms after completion; the preview holds the final pose and provides a Replay button. The existing sprite sampler already held one-shot clips on their final frame.
- Created full 8×8 character masters for Idle, Walk, and BasicAttack using the fantasy swordsman identity and existing guide poses. BasicAttack includes the visible sword and a separate gold-white sweep trail. These eight-frame masters are retained for comparison, not accepted as smooth animation.
- Applied the same `0.949153` scale and root `(80,132)` to all three sheets, targeting a 112px visible character height inside each 160px cell. Source action frame order and duration data stay intact.
- Cut all three masters into registered `BaseBody`, `HeadHair`, `Outfit`, `Weapon`, `BackAccessory`, `CosmeticFX`, and empty `Headgear` sheets. All three reconstruct exactly with `0` mismatches (`363,448` Idle, `287,882` Walk, and `322,106` BasicAttack visible pixels).
- Refined each head label seed to include visible warm face pixels with the hair. The refinement is a geometric/color heuristic and still needs visual inspection; it does not generate hidden face or scalp art.
- Added native-resolution eight-direction review GIFs for all three actions and per-layer breakdowns. The pose/art review remains open; Walk (`0.8289`) and BasicAttack (`0.5529`) are below the research `0.88` silhouette-continuity warning. These figures are diagnostics, not art-quality scores, and large attack poses can intentionally change silhouette.
- The cutouts and detailed reports are in the [master-cutout paint job](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/README.md). The source master is the art source; the mask only supplies labels.

### Current review GIFs

The established Idle and Walk GIFs still show the eight-frame paint pilot, so they are diagnostic only. Idle and Walk loop; BasicAttack plays once and holds recovery. Playback metadata is correct, but the Idle/Walk artwork still pops at the loop seam and has too few painted poses. Walk's worst seam is `0.614` silhouette IoU. A new SE-only plum-gray/lavender-silver/ivory sweep effect has a one-shot review GIF, but the combined master remains below acceptance because its character source has red fringe and clipped blade pixels. No acceptable 16-frame painted master has been admitted, and no candidate has been previewed on the requested map.

- [Idle master-cutout GIF, eight directions](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/review/layered-v3-idle-8-directions.gif)
- [Walk master-cutout GIF, eight directions](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/review/layered-v3-walk-8-directions.gif)
- [BasicAttack master-cutout GIF, eight directions](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/review/layered-v3-basicattack-8-directions.gif)
- [BasicAttack layer breakdown](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/review/layered-v3-basicattack-layer-breakdown.png)
- [Rejected WeaponSlash BasicAttack GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/review/weapon-slash-pilot/layered-v3-basicattack-8-directions.gif) — diagnostic only; the effect crosses the character.
- [Rejected WeaponSlash layer breakdown](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v1/review/weapon-slash-pilot/layered-v3-basicattack-layer-breakdown.png)
- [Idle 16-frame pose guide GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/guides/idle-motion-guide-16-8directions.gif) — rig guide only.
- [Walk 16-frame pose guide GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/guides/walk-motion-guide-16-8directions.gif) — rig guide only.
- [BasicAttack 16-frame pose guide GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/guides/basicattack-motion-guide-16-8directions.gif) — one-shot rig guide only.
- [Iteration 4 SE slash and trail GIF](../../authoring/characters/factory-v3/paint-jobs/swordsman-master-cutout-v2/prototypes/basicattack-se-iteration-4/review/basicattack-se-weaponlight-one-shot.gif) — one-shot review prototype; not approved art.
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

- **Visual quality and motion:** the current eight-frame masters are below the requested smoothness bar. Sixteen-frame Idle, Walk, and BasicAttack pose guides and timing plans exist. The compact 16-frame SE trial reads as a controlled low diagonal attack, and its review GIF has a locked recovery seam, but it is rejected for blade clipping and missing effect art; it is not a painted eight-direction master. The Walk guide has a weak west/east silhouette seam; Idle is subtle. Earlier full-master trials were rejected for cell-boundary clipping, red fringes, or insufficient pose change.
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
| Free motion sources | **PASS for candidate use** | Mesh2Motion CC0 source and evidence recorded. |
| Idle / Walk / BasicAttack | **REPAINT REQUIRED** | Current eight-frame pilot GIFs show the loop/pose issues. Sixteen-frame sampling plans are ready. The compact SE-only attack GIF is for loop-seam review and is rejected for blade clipping; matching eight-direction masters and cutouts remain. |
| Eight directions and structural passes | **PASS** | 192 records, six passes, unmirrored directions. |
| Painted identity and fantasy readability | **REPAINT REQUIRED** | Iteration 4 tests a broad low SE trail with an original plum-gray/lavender-silver/ivory gradient and aligns its peak with the source sweep. It remains review-only because the underlying SE master has red fringe and clipped blade pixels; all eight facings and a clean 16-frame master remain outstanding. |
| Cloak toggling | **PARTIAL** | Earlier procedural on/off comparison exists. Next candidate targets a default golden cloak and transparent no-cloak variant. |
| Frame-matched cutout layers | **CANDIDATE** | Idle, Walk, and BasicAttack masters and visible cutouts recompose with `0` pixel mismatch. Hidden surfaces and manual semantic-mask review remain. |
| Remaining six actions | **PENDING** | Static placeholders only. |
| Runtime package | **PASS as DEV_ONLY** | Schema/atlas validation passes; no production admission. |
| Actual game preview | **HISTORICAL ONLY / MAP REJECTED** | Prior preview used Wayfarer Capital, which the owner said is the wrong map. New layered candidate and target-map preview are pending. |
| Owner approval | **PENDING** | The eight-frame painted GIFs and iteration 4 trail remain below the requested quality bar. The SE-only 16-frame masters are rejected for clipped blade pixels; the 16-frame eight-direction GIFs remain low-detail rig guides. |

## Validation record

| Check | Result | Detail |
|---|---|---|
| Factory `--stage all --force` | **PASS** | Blender 5.2.2; rig, motion, guide, handoff, and procedural package stages completed. |
| Motion production gate | **PENDING by design** | Returns `passed=false` while clips remain `CANDIDATE`; no retarget/build error. |
| Painted importer | **PASS** | 192 cells, shared 0.752381 scale, cleanup and alignment report written to the paint job. |
| Runtime candidate validator | **PASS** | Iteration 2: 9 clip definitions, 20,763,712 decoded atlas bytes, no schema errors. |
| Procedural runtime validator | **PASS** | 9 clip definitions; no schema errors. |
| Painted-sheet normalization test | **PASS** | Shared scale, alpha cleanup, full frame count, and guide-mask containment. |
| Superseded independent-layer experiment | **REJECTED / HISTORICAL** | Earlier separate-sheet Idle mean silhouette IoU `0.835`; Walk `0.785`; both below the research 0.88 warning. These mismatched sheets are retained as diagnostics, not current masters. |
| Three-action master cutouts | **PASS: EXACT RECONSTRUCTION / PILOT REJECTED FOR SMOOTHNESS** | Idle, Walk, BasicAttack each have an 8×8 master, aligned layer sheets, and `0` reconstruction mismatches. This validates pixel registration only; the replacement target is 8×16. |
| Sixteen-frame timing | **PASS: SAMPLING PLAN** | Idle, Walk, BasicAttack plans each have 16 unique frame phases. The SE-only painted trial is not a direction-complete master and has no runtime layers. |
| Frame continuity | **DIAGNOSTIC ONLY / BELOW WARNING** | Eight-frame pilot: Idle mean/min `0.9073 / 0.7739`; Walk `0.8289 / 0.6138`; BasicAttack `0.5529 / 0.3469`. The rejected compact SE trial has minimum adjacent alpha IoU `0.598`; its `1.0` loop seam is created by locking recovery to the first guard frame. Blade clipping still fails the review. |
| Prior browser preview | **DEVELOPMENT-ONLY / MAP REJECTED** | BasicAttack contact marker was at 983ms, but the owner rejected the Wayfarer Capital location as the wrong map. |

See [the implementation record](PRODUCTION_FACTORY_V3.md), [build evidence](evidence/production-factory-v3-motion.json), [iteration 2 paint job](../../authoring/characters/factory-v3/paint-jobs/imagegen-swordsman-v2/imported/job.json), and [Wayfarer Capital browser report](evidence/imagegen-swordsman-v2/wayfarer-capital-review.json) for the full progression and provenance.
