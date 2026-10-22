# Patch 0.0.1 production checkpoint

In production; not release complete. Six characters: male/female Swordsman, Mage and Archer.

## Direction policy

Physical attacks and casting use four real diagonal views, without mirroring. Casting includes CastChannel, CastRelease and Mage basic attack/SkillAction, per latest owner instruction. Other actions retain eight. See research/action-direction-decision.md.

## Actual coverage

49 source guide jobs captured locally (5,696 source positions after reuse). Generated captures are reproducible and excluded from Git due to size. Run `python tools/character_factory_v3/patch001_factory.py guides` to regenerate from pinned CC0 sources.

Six eight-view identity studies exist. They are not final animation coverage. There are 98 unique paint jobs, zero complete imported cutout jobs. The SE basic-attack study has 16 same-frame cutout assemblies and independent provisional trail layers. Exact pixel recomposition is recorded; semantic mask boundaries and motion fitting remain unapproved.

## Outstanding quality work

- Inspect source joins and terminal keys, especially KayKit bow entry and retargeted hand/foot contact. Source capture success is not motion acceptance.
- Complete coherent action painting with fixed cameras and source landmark review.
- Author same-frame HeadHair, BodyCostume, Weapon cutouts and hand overlap; FX independent.
- Validate trajectory-based trail after actual cutting motion; short recent history and correct foreground occlusion.
- Package six complete character sets and inspect normal/slow GIFs before runtime admission.

Existing accepted-review work under the previous Swordsman prototype remains separate because camera/timeline fitting differs. Do not blindly import it as matching these guide jobs. Mesh2Motion remains preferred; KayKit CC0 supplies actual bow clips absent from the free Quaternius Standard download.

41 factory tests pass, including actual Blender retarget/contact checks. These technical results do not establish owner visual approval.

## Owner-requested variant acceptance

After the complete base set, demonstrate alternate hairstyle and costume for one action per class: Swordsman BasicAttack, Mage CastRelease and Archer BasicAttack, across each action's four real directions. Use matching pose IDs/camera/timing and existing weapon/effect layers. Not authored yet.

## Current source corrections and audit

All 49 current guide jobs were audited: zero missing/stale jobs, zero world-pose disagreements between cameras, and no projected landmarks outside the capture. This does not establish natural motion or painted-pixel quality.

Canonical captures are 1536 square with uniform overscan; authoring is 768 square with root [384, 550.4], runtime proposal 240 square with root [120, 172]. Camera world positions and pixels per meter are preserved. Overscan is not per-frame body scaling. Runtime admission remains blocked until complete reviewed packages exist.

Bow guides preserve a closed anatomical left grip and calibrate bow orientation to that wrist. The right release hand no longer drives the bow. The held arrow disappears at the first sampled release pose. Mage partial clips trim reset terminal keys; staff follows the right hand while the native left hand casts. Swordsman skill adds joint-space entry and exit transitions. Floor sitting uses an explicit lower-body 3D adapter, still requiring contact review.

## Archer floating-bow defect

Male NW frame index 11 omitted the far anatomical left bow arm. The visible open near hand is the right release hand. Moving the bow to that hand is anatomically wrong; the adjacent-glove experiment is rejected and must never be imported.

A source-guided single-frame repaint restores the left gripping arm and right open release hand. It remains a single-frame candidate: sequence registration, unchanged scale/root, neighboring pose continuity, and four-view male/female grip/quiver review are outstanding. No corrected full-action GIF is claimed.

## Archer contact correction, 2026-10-22

The old retarget added approximately 0.102 m of rear toe lift at full draw relative to the donor. The explicit `cheek-anchor-arm-IK-floor-elbow-v3` adaptation preserves per-foot donor toe heights, lifts the draw anchor toward the cheek, and follows lifted donor elbow hints. It is authored adapted motion, not unchanged mocap.

Current BasicAttack guide `4f6e96426d00fa15c9a3` has 64 actual captures in four views, reused without pixel changes from a compatible completed diagnostic. Retained audit: maximum toe-height difference 3.90e-7 m, no arm reach clamping, first/last body landmark difference 5.79e-7 m, zero camera disagreements, nocked arrow present only indices 0–9, no viewport clipping. Toe-joint agreement is not a mesh sole, collision or weight-bearing certification. Other changed bow guide jobs are being captured with the same adapter.

A full-sheet old-paint bow repair restores both arms, but remains unregistered to the current guide. Separate four-frame detailed paint studies improve visible detail but fail action coherence: body lean/build and terminal ready stance drift. They are explicitly rejected as a complete sequence. A new whole-action source-guided pass is under review. No source captures, mask proposals or detailed studies are counted as imported final art.

## Latest continuation: contact, release and modular work

All 49 implementation-fingerprinted source jobs are captured and audited: no missing/stale captures, cross-camera world-pose disagreement, or offscreen diagnostic points. Archer CastRelease now contains release only; it continues from the drawn channel state instead of lowering and drawing again. This adds one shared source job and two character paint jobs.

Male Archer has four new complete raw action sheets using direction-specific head/hood design references. NW source-facing is corrected; separate four-frame batch paintings were rejected for body-build and stance drift. All four remain unapproved for anatomical registration and complete cutouts.

NE explicitly holds source pose8 at timeline slot9 because the generated slot9 released early. The source certificate checks all66 bones and7,391 weighted vertices; conservative body motion is0.387 runtime pixels and weapon sweep0.499. This is fifteen distinct poses over sixteen timeline slots, not sixteen newly painted poses. Arrow release timing remains slot10. Source pose0 and15 have identical body matrices but different held-arrow state: only body/head/hand/accessory reuse is eligible there.

NW now has sixteen same-frame HeadHair cutout proposals with exact recomposition (zero changed pixels). BodyCostume proposals still include the weapon; complete Weapon/Hand/BackAccessory boundaries and hidden costume surfaces remain unfinished. No complete import is claimed. Four-view normal/slow GIFs are available under `/workspace/outputs/archer-male-four-view-review/`.

Validation:41 unittest cases pass; Python compilation succeeds. The actual Blender contact regression samples18 poses, reproduces the old0.1019m rear-toe error, and measures corrected discrepancy2.37e-7m, finite bone matrices, correct draw/release fingers and zero ready/recovery body seam. These metrics do not certify the painted frames, sole contact, natural weight transfer, or runtime readiness.

Remaining:98 complete cutout jobs, painted/source anatomical review, final trail checks, six runtime packages, and full-action hairstyle/costume variants for each class. Patch0.0.1 remains incomplete.

## Four-view male/female Archer paint review

Four new female action sheets and all four male sheets are retained with exact prompts, raw provenance and direction references. Interactive frame/guide comparison, male NW head/body toggles, and normal/slow eight-character-view GIFs are packaged at `review/archer-basicattack/index.html`. This is a revision review, not runtime proof or an approved character package.

The new source guide2fed9f286cdd5c5ffbf4 and painting source4f6e96426d00fa15c9a3 have identical decoded RGBA pixels across all64 captures and exactly matching world landmarks/weapon projections. PNG file bytes differ; the pixel comparison is recorded separately.

Female NE uses the same explicit pose8 hold at slot9. Raw female NE also released early; SW/SE recovery samples contain reappearing arrows and require local art correction. Female source fitting, ready/recovery pixel stability, and complete cutouts remain unapproved. These eight direction sheets are not counted as eight finished jobs. Complete import count remains zero.

## Bounded local paint correction

A single female SW recovery15 arrow-removal study uses an explicit3,901-pixel repair mask. Outside-mask changes are exactly zero;3,049 inside pixels change. It is not promoted: the segment between nocking hand and bow grip still needs string-mechanics review. Original master/GIFs remain unchanged. This technical repair guard prevents collateral body/head/foot changes; it does not certify the replacement artwork. All41 factory tests pass, including three local-repair regression cases.
