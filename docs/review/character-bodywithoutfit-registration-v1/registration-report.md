# Repaired Swordsman owner-review checkpoint

**OWNER VISUAL APPROVAL PENDING.** This is a new animated review candidate, not an owner-approved character. The original rejection is preserved at `docs/review/character-ro1-animated-v1/`, and the subsequent hair/cape and W sword rejections are retained in `rejected-registration-candidate-220d535/` and `rejected-grip-candidate-4c0f0e2/`; the further sword-alignment rejection is preserved in `rejected-sword-candidate-31bb1a8/`; none of its sources, atlases, motion metadata or exports were overwritten.

Branch: `character/ro1-reference-engine-v1`.
Starting HEAD on the requested branch: `db2959b97a77b3f9b54c22d5e732fe2b2345a529`.
The initial desktop checkout was on the separate `character/true-modular-ro1-swordsman-v2` at `d26fbcd74458d57150b2063c74151193690a1f6a`. That branch was left intact. The existing requested remote character branch was fetched and checked out at its actual current HEAD. No useful work was reset, rebased, merged away or force-pushed. Final seal HEAD and normal remote-push verification are reported in the task response; a file cannot include its own containing commit SHA.

## What changed

| Requested field | Implementation/result |
| --- | --- |
| Body model before | Required Body slot, body-swordsman; dressed anatomy, armour, clothes, boots **and bald Head** in one raster. No production Outfit layer. |
| Body model after | Required BodyWithOutfit plus required independent Head, with optional Hair, MainHand, OffHand, Headgear, Garment and FX slots. |
| BodyWithOutfit implementation | New schema1.1 pack; complete dressed-body default and DEV_ONLY royal colour proof bind one shared body contract. Internal generic layer Body is retained. No armour paper doll. |
| Head implementation | Existing painted skull/face pixels, skin-seeded silhouette extraction bounded by measured skull geometry, per-frame96px cells, explicit320px source/trim origin and neck/base pivot. BODY_SYNC preserves all direction/action perspectives. Internal layer HeadBase is retained. |
| Was existing painted Body reused? | Yes. All328 original normalized cells remain immutable.323 target phases retain their own source pose. Five bounded attack phases reuse nearby existing art: SW7←8 and NW7←8 align contact with a lowered strike hand; W10←11 removes an isolated reversal; W14/15←13 retains a closed-fist recovery instead of open palms. No character regeneration. |
| Was Head already independent? | No. |
| How separated? | Complementary alpha masks, never repainting/redesigning the face. Body + Head reassembles **every selected source RGBA pixel exactly** in all328 cells (including the five explicitly recorded existing-pose repairs). Direction-local ear extraction keeps the identity separate; raised glove occlusions remain owned by the dressed body, and metal/ivory filtering removes neighbouring costume samples. The mask excludes raised sleeves; the receipt records source rectangles, head pivots, hashes and lossless verification. |
| Head registration root cause | No independent Head sample, no neck pivot, and a broad warm-skin detector could include nearby ivory cuffs. The old head socket represented a bounds centre with width-derived scale. New Head placement registers its explicit neck/base pivot and retains original painted size. |
| Hair registration root cause | Hair chased the body head-centre socket and added a generic quarter-cycle bob/rotation independent of the painted skull. The first repair still left hair smaller than the painted skull and interpreted directional head perspective as extra roll. The revised authored direction registration increases skull coverage by14–24%, seats the crown higher, and removes the neutral directional roll before following action tilt. Hair inherits the selected Head local socket; no independent body-space bob remains. |
| Sword registration root cause | Fractional-bounds pivot rather than a measured grip, guessed/interpolated hand sockets, an incorrect anticipation blade rotation, and a nearest-glove search that changed arms in rear attack poses. All128 attack grips/angles are authored against the visible sword arm. The owner also rejected the first W strip: its handle was drawn over the glove, some pivots sat at finger edges, and one follow-through pose reversed the hand for one frame. W palm centres are remeasured, both weapon grips are explicit authored source coordinates, and body-owned foreground polygons place the glove over the handle, including when hair/headgear overlap it. The owner rejected that candidate again for sword alignment. The revised SW/W/NW arc now takes the blade out beyond the wrist rather than back across the arm. Six PHASE_SYNC entries select ready/loaded/swing/contact/follow-through/recovery perspectives from the retained blade views; the hand anchor still updates on every body frame. SW/NW contact now samples the existing lowered strike pose, W10 is a short hold of existing frame11, and W14/15 reuse the closed fist from frame13. Runtime masks and sampling remain generic and metadata-driven. |
| Cape registration root cause | Head-derived back position, bounds-derived pivot and generic quarter-cycle source changes ignored the collar/shoulders during lean; a single rear pass could cover the glove. The first repair also trusted wrong source-view labels and retained an estimated bounds pivot, oversized cloth and head-derived roll. Revised cape direction selection matches the actual painted torso (straight rear for N; side profiles for W/E), uses authored neckline pivots, scales the cloth to80%, and measures the collar plane independently of the skull. BODY_SYNC retains attachment at every phase; separate rear/front passes keep exposed arms readable. |
| Idle result | Nine frames × eight directions exported and inspected at baseline registration; new skull-fit, palm foreground and neckline-view candidate exported. The earlier smaller-hair/angled-cape candidate was owner-rejected and preserved; this revision is awaiting approval. |
| Walk result | Sixteen frames × eight directions exported, registered and sampled without an independent hair/cape phase lag. Frame16→frame1 boundary board included. |
| BasicAttack result | Sixteen frames × eight directions exported. Head follows the painted lean; Hair inherits it; blade rotates around the held grip through anticipation/contact/recovery; cape follows the painted collar plane. All sixteen W frames and the remaining direction strips were inspected; the owner-rejected W strip is paired with the revised strip. Actual-browser glove foreground checks cover288 strike/recovery combinations of eight directions, two bodies and two swords. Exact contact debug is included for all eight directions, with an explicit grip→guard→blade axis. The registered weaponTip also follows the selected blade landmark; the old motion-space estimate is corrected only within the shared appearance contract. |
| BodyWithOutfit A/B swap | Default ↔ royal colour proof. Browser async selection and controller checks preserve all non-body references and PNG pixels. |
| Timeline preserved? | Yes: runtime Walk/SW at277ms/frame7 preserves action, direction, frame, motion sample, registered anchors and cosmetic time. The GIF also shows before/after swaps at the same mid-walk timestamp, then continues the clock. |
| Hair A/B | Both retained source atlases, revised authored skull-fit/neutral-angle registration and all328 Head-local phase attachments; equipped variant GIFs for each action/all directions. |
| Weapon A/B | Both retained authored directional blade sources and explicit grips. PHASE_SYNC selects six authored attack phase perspectives from the original directional blade images; Idle/Walk hold one directional perspective. Every phase uses the explicit grip pivot and the current frame’s hand transform. No unrelated newly generated blade frames. |
| OffHand | Independent, optional shield; explicit handle pivot, registered offHand anchor, all actions/directions. |
| Headgear | Independent, optional circlet; inherits Head-local socket rather than the old body-space head centre. |
| Cape | Independent and optional; direction-specific source views, measured upper-back pivot, BODY_SYNC and GarmentBack/GarmentFront where needed. |
| MotionTemplate changed? | **No.** Exact bytes, reference keys, choreography, action/direction/frame IDs, duration budgets, events and motion-engine source remain unchanged. Shared appearance-contract socket calibration refines painted registration beneath those motion anchors. |
| Painted frames repaired/re-authored | Zero newly generated or repainted character/face frames. Five attack target phases reuse existing nearby poses (SW7←8, NW7←8, W10←11, W14/15←13); all original source cells remain immutable.328 complementary Body/Head derivatives from the selected source poses, including ear/raised-glove separation;328 controlled colour-proof body cells; eight cape-front masks and authored glove-foreground polygons. All other repair is authored socket/pivot/registration/order metadata. |
| Owner status | **OWNER VISUAL APPROVAL PENDING**. Automated tests do not certify visual quality. |

## Shared contract and runtime boundary

Canvas320×320, root(160,264), referenceHeight176, directions S/SW/W/NW/N/NE/E/SE, no mirroring. Idle3000ms, Walk600ms, BasicAttack450ms; presentation contact remains170ms. A costume cannot override timing, root, anchors, gameplay state or Equipment Backbone.

The transform is motion anchor × shared BodyWithOutfit contract calibration × appearance default/direction/action-phase registration × local sample correction, with a stable local image pivot. Head-local children begin from selected Head transform × its skull/headgear socket. The runtime stays generic; there are no Swordsman frame-offset conditionals. Both compatible bodies consume the same registered head/mainHand/offHand/back/FX contract. Gameplay body equipment and the presentation costumeBodyId are separate.

Production metadata: `authoring/characters/appearance/swordsman-bodywithoutfit/appearance-pack.json`.
Contract schema: `authoring/characters/schemas/bodywithoutfit-appearance.schema.json`.
Source/hash/normalization receipt: `authoring/characters/builds/swordsman-registration-v1/salvage-receipt.json`.
Measured sockets and authored attack overrides are beside that receipt. No RO raster pixels, raw ACT claims or new paid-provider generation were introduced.

## Validation and browser evidence

- 297 JavaScript tests pass (292 CommonJS assertions, including40 new production tests, plus five world-streaming tests). All prior character tests retained.
- 21 Python tests pass, including six new real-raster salvage checks: all328 lossless body/head reassemblies, source/derivative hashes and real alpha, distinct complete costume bodies, actual opaque attack grip positions, and unchanged entire Head/neck seam across the colour-proof swap, and the five bounded contact/follow-through/closed-fist pose selections using existing art.
- The browser exports328 clean repaired poses and328 equipped variants, checks crop margins and visible autoplay for all three actions, tests all solo controls and default-off debug overlays, and captures desktop/mobile review.
- Costume A/B comparison checks **actual non-body PNG bytes** across all328 poses; all are unchanged. The runtime async loader swap at Walk/SW/frame7 preserves277ms and cosmetic time.
- Actual-browser hair/Head crown regression compares656 rasters (328 poses × both hairstyles): minimum opaque coverage98.2183% of the sampled upper sixteen skull rows. This measures coverage, not projected angle or approval.288 actual composite palm comparisons prove that selected body glove pixels cover either sword handle during strike/recovery; maximum pixel error is recorded in `hair-crown-raster-check.json`.
- Actual world review captures all three actions × eight directions, plus eight exact attack-contact states, mobile, unchanged mechanics/position during swaps, ordinary movement and memory-only saves. No Combat is invoked by frame inspection.
- JavaScript syntax, Python compilation and git diff whitespace checks pass. Protected gameplay/world/boot/Equipment sources remain unchanged against the verified baseline. Ordinary gameplay admission was not added.

`browser-review.json`, `node-checks/report.json`, `world-streaming-tests.log`, `python-tests.log`, `gameplay/browser-review.json` and `gameplay-contact/contact-review.json` contain the concrete receipts. `tests/swordsman_registration_browser.py` reproduces the crown and glove raster comparisons against the native browser renderer. The local game-dev CLI is unavailable, so project-native browser capture and Pillow raster validation provide this evidence; no plugin installation or external provider was required.

## Open the visuals

- [Sword alignment W animation](Sword-alignment-W-review.gif), [latest sword rejection comparison](Sword-alignment-latest-rejection-before-after.png)
- [Hair/cape close-up, all actions and directions](Hair-cape-closeup-eight-directions.gif), [hand/grip close-up, half-speed review](BasicAttack-hand-grip-closeup.gif)
- [Latest hair/cape rejection comparison](Hair-cape-latest-rejection-before-after.png), [latest W sword rejection comparison](Weapon-W-latest-rejection-before-after.png)
- [Large owner preview, all three actions/all eight directions](swordsman-repaired-owner-preview.gif)
- [Idle](Idle-fixed-eight-directions.gif), [Walk](Walk-fixed-eight-directions.gif), [BasicAttack](BasicAttack-fixed-eight-directions.gif)
- [Costume swap at the same phase](costume-swap-proof.gif)
- [Head/neck before-after](Head-neck-before-after.png), [Hair before-after](Hair-before-after.png), [Sword grip before-after](Weapon-grip-before-after.png), [Cape before-after](Cape-before-after.png)
- [Idle anchor diagnostics](Idle-anchor-debug.png), [Walk anchor diagnostics](Walk-anchor-debug.png), [Attack anchor diagnostics](BasicAttack-anchor-debug.png), [Exact contact grips](BasicAttack-grip-contact-debug.png)
- [Gameplay-scale board](gameplay-scale-review.png), [Walk loop boundary](Walk-loop-boundary.png)
- [Hair B/Sword B/shield/circlet Idle](Idle-alternate-equipped-eight-directions.gif), [Walk](Walk-alternate-equipped-eight-directions.gif), [Attack](BasicAttack-alternate-equipped-eight-directions.gif)
- [Actual world, all24 poses](gameplay/all-actions-eight-directions-gameplay.png), [actual world exact contact](gameplay-contact/BasicAttack-contact-eight-directions.png)
- [Interactive clean review and development toggles](../../../character-review.html), [actual game-world review](../../../character-gameplay-review.html)

APNGs beside the action GIFs preserve exact millisecond timing. GIF centisecond rounding is a preview limitation. Source PNG frames and all24 direction strips are in `frames/` and `strips/`. `artifact-receipt.json` seals top-level image hashes and sizes.

## Remaining visual limits

The original painterly strips contain direction/phase variation in proportions and pose projection. This repair preserves that art rather than repainting the character. Subpixel raster seams, cape edge occlusion and blade/hand perspective during the fastest attack phases still require the owner's visual judgment at large and gameplay scales. The royal body is a colour-only proof with an intentionally unchanged neck/collar boundary, not a final costume design. A few original antialiased pixels at ear/collar and raised-hand occlusion boundaries remain candidates for final artist cleanup. The cape uses retained directional artwork with body-phase collar attachment/tilt; no new cloth simulation was added. GIF colour quantization is reduced with a palette sampled from visible painted assets, but PNG/APNG retain the original colours.

No additional actions or classes were started. **OWNER VISUAL APPROVAL PENDING.**
