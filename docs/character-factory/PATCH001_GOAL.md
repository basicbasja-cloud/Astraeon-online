# Active goal: playable patch 0.0.1 characters

Owner instruction: 2026-10-27. Continue until the agreed plan is fulfilled.
This goal is ACTIVE again by owner instruction, not complete. Current imported coverage is 2/96 jobs;
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
