# Patch 0.0.1 production checkpoint

In production; not release complete. Six characters: male/female Swordsman, Mage and Archer.

## Direction policy

Physical attacks and casting use four real diagonal views, without mirroring. Casting includes CastChannel, CastRelease and Mage basic attack/SkillAction, per latest owner instruction. Other actions retain eight. See research/action-direction-decision.md.

## Actual coverage

48 source guide jobs captured locally (5,632 source positions after reuse). Generated captures are reproducible and excluded from Git due to size. Run `python tools/character_factory_v3/patch001_factory.py guides` to regenerate from pinned CC0 sources.

Six eight-view identity studies exist. They are not final animation coverage. There are 96 unique paint jobs, zero complete imported cutout jobs. The SE basic-attack study has 16 same-frame cutout assemblies and independent provisional trail layers. Exact pixel recomposition is recorded; semantic mask boundaries and motion fitting remain unapproved.

## Outstanding quality work

- Inspect source joins and terminal keys, especially KayKit bow entry and retargeted hand/foot contact. Source capture success is not motion acceptance.
- Complete coherent action painting with fixed cameras and source landmark review.
- Author same-frame HeadHair, BodyCostume, Weapon cutouts and hand overlap; FX independent.
- Validate trajectory-based trail after actual cutting motion; short recent history and correct foreground occlusion.
- Package six complete character sets and inspect normal/slow GIFs before runtime admission.

Existing accepted-review work under the previous Swordsman prototype remains separate because camera/timeline fitting differs. Do not blindly import it as matching these guide jobs. Mesh2Motion remains preferred; KayKit CC0 supplies actual bow clips absent from the free Quaternius Standard download.

No unit tests added or run. Current counts describe source generation and production bookkeeping, not owner approval.

## Owner-requested variant acceptance

After the complete base set, demonstrate alternate hairstyle and costume for one action per class: Swordsman BasicAttack, Mage CastRelease and Archer BasicAttack, across each action's four real directions. Use matching pose IDs/camera/timing and existing weapon/effect layers. Not authored yet.

## Current source corrections and audit

All 48 current guide jobs were audited: zero missing/stale jobs, zero world-pose disagreements between cameras, and no projected landmarks outside the capture. This does not establish natural motion or painted-pixel quality.

Canonical captures are 1536 square with uniform overscan; authoring is 768 square with root [384, 550.4], runtime proposal 240 square with root [120, 172]. Camera world positions and pixels per meter are preserved. Overscan is not per-frame body scaling. Runtime admission remains blocked until complete reviewed packages exist.

Bow guides preserve a closed anatomical left grip and calibrate bow orientation to that wrist. The right release hand no longer drives the bow. The held arrow disappears at the first sampled release pose. Mage partial clips trim reset terminal keys; staff follows the right hand while the native left hand casts. Swordsman skill adds joint-space entry and exit transitions. Floor sitting uses an explicit lower-body 3D adapter, still requiring contact review.

## Archer floating-bow defect

Male NW frame index 11 omitted the far anatomical left bow arm. The visible open near hand is the right release hand. Moving the bow to that hand is anatomically wrong; the adjacent-glove experiment is rejected and must never be imported.

A source-guided single-frame repaint restores the left gripping arm and right open release hand. It remains a single-frame candidate: sequence registration, unchanged scale/root, neighboring pose continuity, and four-view male/female grip/quiver review are outstanding. No corrected full-action GIF is claimed.
