# Patch 0.0.1 character goal — active

**Source of truth:** [PATCH001_MASTER_PLAN.md](PATCH001_MASTER_PLAN.md). The owner resumed implementation after reviewing the plan. Older checkpoint statements below are historical; current coverage requires fresh evidence.

Owner instruction: 2026-10-27. Continue until the agreed plan is fulfilled.
This goal is active by owner instruction and is not complete. Current imported coverage is 2/96 jobs;
zero newly complete characters. Source motion, tests, imports and exact pixel
reconstruction alone do not constitute acceptance.

## Deliverables

Swordsman male/female (19 actions each), Mage male/female (18 each), Archer
male/female (20 each): 114 logical action instances, currently 96 paint jobs.
Recompute work counts only from verified source/reuse contracts, never count
missing artwork or substitute idle for an absent action.

All six must have complete real direction coverage, usable separate sprite
sheets, clean cutouts, correct grip/FX, smooth transitions, actual gameplay
captures and reproducible production recipes. Demonstrate new HeadHair,
BodyCostume and weapon for both sexes of each class: Swordsman BasicAttack,
Mage CastRelease, Archer BasicAttack, all four authored views.

## Non-negotiable production workflow

Actual rig motion -> locked camera/scale -> coherent COMPLETE clothed master
for each actual pose/view -> anatomy and temporal approval -> same-frame
BodyCostume / HeadHair / Weapon cutouts -> exact recomposition and semantic
boundary review -> occlusion/FX -> variants -> real runtime -> evidence.
BodyCostume includes all limbs. Never construct final characters from separately
generated limb assemblies, freeze legs to hide drift, independently fit frame
alpha bounds, or approve segmentation solely from exact recomposition.

Tall original Swordsman is the protected visual authority. Mesh2Motion is the
preferred source; use appropriate retained ActionForge/Rokoko/Mixamo alternatives
when necessary. Do not overwrite original artwork. Optional cape may be removed
if it harms quality. No unapproved paid services or replacement of the illustrated
pipeline with finished 3D art.

## Scale and motion contract

Source 1536 square; authoring 768 square; runtime 240 square. Runtime root
[120,172], reference height 88. Shared orthographic camera/pixels-per-meter and
character-fit scale across frames/actions; overscan preserves scale. Existing
512 drafts require explicit size qualification, not upscaling claimed as detail.

General actions: 8 real directions. Attacks/casting: SW,NW,NE,SE, using existing
input direction mapping without mirroring handedness. Inspect anticipation,
weight transfer, strike/release, recovery, wrist orientation, grip, root motion,
loops and one-shots in Blender before painting. Densify actual motion samples
where needed; do not duplicate frames to pretend smoothness.

Measure guide-relative contacts on both identifiable feet and the rest of the
anatomy. Contact error <=1 runtime pixel; hidden/ambiguous landmarks require
review. Preserve intentional source movement. True loops need continuity;
one-shots need actual ready/idle transitions, not forced cyclic playback.

Sword trail follows actual blade sweep after movement starts, retains the
approved long impactful style, correct front/back occlusion, speed-dependent
width and fade. Bow/projectile and spell events follow explicit timing.

## Ordered stages and exit gates

0. Audit full coverage/reuse/timing and lock camera/size references for six fits.
   Mage 24-frame BasicAttack/SkillAction must not alias 16-frame CastRelease.
1. Pass Swordsman baseline, Mage casting and Archer basic pilots, both sexes,
   end-to-end from source through actual gameplay. Do not expand failing art.
2. Finish Idle/CombatIdle/Walk/Run/Sprint on all six fits.
3. Finish attacks, skills, casting and all class combat extras.
4. Finish Hit/Death/Sit/Respawn/Interact/Pickup/ItemUse and remaining actions.
5. Pass genuine hair/costume/weapon swaps, separately and together. Newly exposed
   surfaces must be authored; recolor is not a new costume.
6. Verify all six complete packages, every action binding and transition in the
   actual game, at supported zoom/subpixel positions; reproduce into fresh output.

## Evidence and progress

Every checkpoint: commit, actual coverage, passed/failed gates, frame-specific
open defects, source/tool/model hashes, reproducible commands, native PNG,
normal/slow GIF and gameplay captures where applicable. Publish to GitHub issue
#2 with media. Keep baseline/accepted/draft/rejected assets distinct; remove only
unreferenced reproducible temporary outputs.

Current factual checkpoints: Mage drift is in PNG source. 192 Mage browser
compositor draws and 320 Mage/Archer GIF crops introduce no extra translation
in the recorded diagnostic. These checks do not approve anatomy or gameplay.
Mage reuse metadata was corrected in c8188e4b; stage 0 remains incomplete.

Current inventory resolves114 logical actions /96 paint jobs. All48 original
source-guide jobs validate locally; this does not establish six fitted or
painted characters. The new source-reference preflight rejects clipped
body/weapon crops;346 factory tests pass. The guide-only torso/head fit study
is isolated and not adopted in production.

Next: qualify the six-character anatomy/size references, repair the Mage/Archer
pilot masters with protected same-frame pixels, and close the complete pilot
workflow before expanding those paintings across the remaining actions.

## Historical painting failure — goal continues

Source-constrained painting has not met the geometry gate after full-sheet,
coordinate-guided single-pose and marked-floor local corrections. Latest local
patches remain rejected and unmerged. See review/patch001-mage-local-paint-blocker-20261027
for images and measurements. Unblock with precise complete-master correction or
corrected pilot artwork; do not fake acceptance by warping limbs or weakening gates.

## Owner resumed goal

Continue working after unsuccessful paint studies. Raster sole-component errors
are provisional diagnostics, not verified anatomical contacts and not grounds
to stop the whole goal. Correct master anatomy, improve source controls, and
continue independent engineering work. Do not lower acceptance standards or
claim a failed image as approved. Previous blocker report is historical.

## Active continuation — target gaze and ownership checkpoint (27 October 2026)

347 tests pass. A new isolated Mage gaze study captures 24 poses × 4 real cameras at1536px, protects all64 non-head bones and verifies all66 bone matrices during rendering. It records candidate reusable head pose families; production adoption and painted neck/head seam review are pending. Eighteen Archer head ownership keys are reviewed (566 pixels returned to body/rest), not all96 remaining-view frames. Four coherent single-frame Mage painting studies share one fit and pass the narrow visible-sole diagnostic, but head/costume continuity remains open. Goal ACTIVE, coverage unchanged at2/96 technical imports and0/6 newly complete characters. See `review/patch001-target-gaze-and-semantic-cutouts-20261027/README.md`.

## Active continuation — complete pilot ownership replay (27 October 2026)

All24 Mage SW raw paintings are saved; own-frame anatomy, robe and shoe continuity still fail acceptance. Source fit/gaze replay exports66 bones per pose and checks seven recorded joints against capture metadata. A camera projection diagnostic checks six joints to within0.000071 authoring pixel. Head ownership proposals now cover96 remaining-view Archer frames and24 Mage frames. Editable labels reproduce240 RGBA parts exactly without generation. The existing JavaScript compositor renders120 native-canvas comparisons with zero mismatches in Chromium. BodyRest still contains weapons: this is not a completed modular character. A shared-head preview exposes neck/collar gaps and is rejected for intake. Goal remains ACTIVE at2/96 technical imports,0/6 newly complete characters. See `review/patch001-full-pilot-head-replay-20261027/README.md` for normal/slow GIFs and open defects. Continue correcting own-frame masters and complete weapon/hand ownership before pilot gameplay acceptance or further art expansion.

## Active continuation — filtered cutout support (28 October 2026)

368 factory tests pass. Matching source-part mask coverage to the bicubic master filters reduces old hair edge residue in the Mage 24-frame study; mixed boundaries, neck/collar, staff occlusion and body continuity still need repair. Archer bow proposal has64/96 provisional curves and32 unresolved, with string, arrow and hand ownership unfinished. No new runtime admission; coverage remains2/96 technical imports and0/6 newly complete characters. See `review/patch001-filtered-head-and-bow-study-20261028/README.md`.

## Owner correction — detached head (28 October 2026)

The user rejected the shared-head preview because the neck is visibly disconnected. The v7 shared-head preview is rejected and must not be admitted. `review/mage-female-own-frame-head-recovery-20261028` reconstructs each of the24 original masters from that frame's own HeadHair and BodyRest with zero visible RGBA mismatch, so the invented head/body assembly is removed. Those source paintings still have temporal anatomy drift and do not establish a working replaceable-head variant. Author the missing neck/collar surfaces in the affected frame masters, review weapon occlusion and all transitions, and complete all three classes and both sexes before final delivery. Goal remains active; no new runtime coverage is claimed.

## Continued after owner asked why work stopped

Continue the active goal without treating source-frame recovery as a finished deliverable. Native Archer female/NE frame003 has a manually annotated same-frame bow/arrow/string proposal in `review/archer-female-ne003-native-bow-study-v2-20261028`. Visible recomposition has zero mismatches; review still shows residual bow/string/arrow pixels on BodyCostume and the head fringe boundary is unapproved. Hidden bow under the gripping hand is not authored. This frame is not accepted for a swappable weapon or counted toward coverage. Mage own-frame masters still vary in head/torso scale and need bounded painting before any head reuse.

## Active continuation — Mage neck underpainting (28 October 2026)

The visibly disconnected shared head was addressed in a 24-frame study with twelve individually generated, bounded neck/collar underpaintings and a corrected head asset that no longer contains a 14-pixel staff fragment. The clean head is an independent RGBA layer; a provisional staff-front layer preserves the narrow source shaft sample but is REJECTED because it contains hair and costume. Twenty-four PIL recompositions and96 fresh-rebuild RGBA checks pass. This is not a completed weapon, valid asset swap, art acceptance or gameplay test. Start/end costume and staff placement, body/boot drift and full semantic boundaries remain open. See `review/patch001-mage-neck-underpaint-20261028/README.md`; goal remains active at0/6 characters and2/96 technical imports.

## Active continuation — Mage separate staff single-frame pilot (28 October 2026)

An independently painted clean staff and a visually different crescent variant have been composed with a bounded same-frame staff-free underpaint and protected glove for Mage female SW frame000. Four visible role proposals plus hand occluder reproduce their underpaint master exactly; a fresh rebuild matches five RGBA outputs and the single-frame weapon swap changes no pixels outside the weapon union. Head boundary, hidden surfaces, actual guide grip alignment, all other frames/directions, game transitions and swaps remain unapproved. This is not a complete action. See `review/patch001-mage-weapon-swap-single-frame-20261028/README.md`. Goal remains active, coverage0/6 newly complete characters and2/96 technical imports.

## Active continuation — Mage frame000 same-frame head ownership (28 October 2026)

The same-frame staff-underpainted Mage female SW frame000 now has a revised head proposal: upper original hair ownership is retained and detached lower mask components return to the body/collar. Its BodyCostume, HeadHair, Weapon and WeaponHandOccluder reconstruct the underpaint master without the weapon; both staff variants reuse the same non-weapon files. Five RGBA exports reproduce exactly. Head/collar semantics, hidden surfaces, grip, other frames/directions, gameplay, motion continuity and all other characters remain open. See `review/patch001-mage-head-ownership-single-frame-20261028/README.md`; coverage is unchanged at0/6 and2/96.

## Active continuation — Mage foot audit (28 October 2026)

Two own-frame bounded shoe paintings for Mage female SW frame005, including a source-guide contact-marked attempt, did not improve the raster sole alignment diagnostic and are rejected as fixes. Source ankle landmarks are close to the painted ankles; the diagnostic is affected by toe shape and is not a certified contact landmark. Do not move or freeze a leg to satisfy it. See `review/patch001-mage-foot-paint-failed-audit-20261028/README.md`. Continue with reviewed contact landmarks and motion continuity; no coverage change.

## Active continuation — own-frame recovery and real-game package audit (28 October 2026)

Mage female SW own-frame head/body reconstruction avoids the obvious transparent neck gaps introduced by the rejected shared-head preview across its 24 source frames. It is a diagnostic, not a usable head swap or an accepted motion: the staff remains embedded and master body, costume, staff and head proportions drift. A separate four-part and alternate-staff trial exists for frame001 as well as frame000, but the hand occluder retains cuff/costume pixels and hidden neck surfaces are missing; neither frame proves a full action. A third shoe redraw and bounded frame003 head/body redraws are rejected. A single four-pose sheet preserves character details more consistently, but its motion-guide overlay still shows staff, hand and foot disagreement; it is rejected for production. See `review/patch001-mage-own-frame-head-recovery-20261028`, `review/patch001-mage-frame001-parts-20261028`, `review/patch001-mage-master-continuity-20261028`, `review/patch001-mage-bounded-head-edit-20261028`, and `review/patch001-mage-coherent-sheet-study-20261028`.

A real Chromium creation-screen check shows all six configured patch001 sprite-definition paths return404 and are absent from the current Git HEAD tree. Creation is disabled for all three classes; female paths were checked by HTTP/Git, not separately through UI. The development-only Swordsman candidate was captured walking in eight directions in Wayfarer Capital. Its gameplay script was interrupted waiting for the pending Run clip, so attacks and transitions are not verified. See `review/patch001-game-package-availability-20261028`. Goal remains ACTIVE: **0/6 newly complete characters, 2/96 technical imports**. Do not promote diagnostic cutouts, fabricate missing packages, claim runtime completion or reduce the master-quality gate.

## Active continuation — sequence-length gate (28 October 2026)

The runtime packer no longer accepts a longer imported timeline by silently selecting the prefix in a requested direction. Each requested view must have exactly the target action's indices; additional real directions can still be present. The new regression and full factory suite pass (369 tests, including Blender). This is a technical gate, not pose/visual/semantic approval. See `review/patch001-runtime-sequence-preflight-20261028`; goal remains ACTIVE at0/6 newly complete characters and2/96 technical imports.

## Active continuation — explicit V3 gameplay probe (28 October 2026)

The opt-in `v3-painted-v2` browser probe now checks the development player in Wayfarer Capital without waiting for an unavailable Run clip. It recorded eight walking directions and one BasicAttack frame, with no page errors; Run is explicitly recorded as Walk fallback and SkillAction as pending. This is not a seamless-motion, trail or six-character package approval. See `review/patch001-swordsman-development-gameplay-20261028`; goal remains ACTIVE at0/6 newly complete characters and2/96 technical imports.

## Owner correction — retire the wrong V3 previews (28 October 2026)

The owner reaffirmed the original tall four-direction Swordsman as the visual baseline and requested removal of the unrelated small development character. In the current working tree, the three `swordsman-male-v3*` runtime preview packages were moved intact into `authoring/characters/factory-v3/unused` and their old development URL selections were disabled; these moves and code changes were not committed or pushed when the owner paused work. Original Swordsman masters/cutouts and motion guides remain preserved. Prior V3 screenshots and captures are historical evidence, not the character to use. The Mage source-frame bounce and size drift are still unresolved; no visual or runtime acceptance is claimed. Goal is paused for plan review, 0/6 newly complete characters and 2/96 technical imports.


## Owner resumed after plan review (28 October 2026)

The owner instructed continuation through the full plan and requested a push and GitHub report at each completed checkpoint. This workspace retains the previously recorded staged preview renames and unstaged edits, including `render_canonical_part_guides.py`. The separate handoff branch `handoff/character-factory-reviewed-20261028` contains a filtered work-in-progress snapshot; it is not a visual or gameplay approval. The remote production branch advanced with a report from another workspace where those files were unavailable. Preserve both histories and the current working tree. Fresh audit: 896/896 baseline hashes match, eight declared pose reuse bindings pass source checks, and coverage inventory remains 114 logical actions / 96 paint jobs / 2 technical imports / 0 completed characters. Mage source-frame drift and size shift remain open.


## Retirement handoff and Mage landmark study (28 October 2026)

The retirement handoff was merged to the remote production branch at `be31a085015155b81bfa6ca8584ebd5779a699c6`; local HEAD and the original staged/unstaged changes remain untouched. Reconcile deliberately before replaying. The shared sprite adapter now selects Sprint instead of silently substituting Run (commit `9e8aab8328dbdf561d0d13aacb9fcfc56f8db522`; 49 Node tests passed). Two adjacent landmark-guided Mage master candidates were visually rejected due to scale/anatomy/hand drift; see `review/patch001-mage-landmark-pair-20261028`. Neither candidate is admitted. Technical coverage remains 2/96 jobs and 0/6 characters complete.


## Preserved Swordsman NW registration study (28 October 2026)

The preserved male BasicAttack is now reviewable as a four-view, 16-frame rig-landmark GIF using its actual imported layers and long sword trail; no art was admitted. A bounded NW frame-15 candidate applies one horizontal −8 authoring-pixel translation to the whole master and every same-frame part. It is unapproved and not imported. Hair-centroid versus source-head residual from frames 14→15 fell from 2.592 to 0.092 runtime px, but the visible lower-component versus source foot-R residual is 1.0102 runtime px and the painted-foot association is not verified. Do not round or treat that result as a contact pass.

Blender replay of the retained source mesh matches frozen guide geometry and camera, and tracks the same 26 low-band skin vertices per side. Source frame 14→15 median screen displacement is left (−0.0468,+0.0169) runtime px and right (−2.1971,+1.0101) px. Source foot-surface points do not by themselves identify painted sole pixels or prove intended planted contact. A whole-frame translation moves both painted feet, so the candidate remains pending painted landmark/geometry review, full action and real transition checks. See `docs/character-factory/review/patch001-swordsman-nw-source-foot-mesh-20261028/` and `patch001-swordsman-nw-registration-proposal-20261028/`. No source master or runtime binding was overwritten.

An Archer male NW frame-11 same-frame far-hand repaint visibly clarifies bow grip but changes size/placement and is rejected; see `review/patch001-archer-nw011-far-hand-study-20261028/`. Mage and Archer masters still require true guide and temporal approval. Coverage remains 2/96 technical imports and 0/6 complete characters.


## NW frame-15 weapon ownership and underpaint proposals (28 October 2026)

A same-frame V3 ownership proposal moves visible guard/hilt pixels to Weapon and returns selected visible cloth/forearm/leg pixels from WeaponHandOccluder to BodyCostume. A generated masked underpaint proposal fills 483 pixels solely underneath opaque original weapon pixels; the sword-on master remains byte-identical. These are one-frame NW drafts, **not semantic or variant approval**. Hidden/antialiased regions, mask edges, alternate weapon, other frames, foot contact, transitions and gameplay remain open. Inputs, hashes, cropped generation prompt, layered candidates, tests and limits are in `docs/character-factory/review/patch001-swordsman-nw15-underpaint-v3-20261028/`. No runtime binding was changed. Coverage remains 2/96 technical imports and 0/6 complete characters.


## NW frame-15 alternative sword study (28 October 2026)

A single-frame NW alternative sword was generated and composed over the unapproved V3 underpaint candidate. The other layers match that candidate exactly, and the annotated grip pixel is covered by both sword and hand. The single-frame equipment-toggle GIF and inputs are in `docs/character-factory/review/patch001-swordsman-nw15-alternate-sword-20261028/`. This is **not** a coherent four-view variant, semantic or visual approval, trail proof, runtime admission or game test. All other frames, views, mask edges, anatomy and hidden surfaces remain open; no production binding was changed. Coverage remains 2/96 technical imports and 0/6 completed characters.
