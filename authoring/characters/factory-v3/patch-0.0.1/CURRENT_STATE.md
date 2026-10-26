# Patch 0.0.1 production checkpoint

## Latest actual state — 26 October 2026

Still 2/96 actual imported jobs, both Swordsman BasicAttack, and zero complete newly admitted characters. Mage native walking and casting pilots remain studies; 10 lossless male/female walking role sheets now contain 160 verified native cells. Archer weapon/hand ownership and recovery-arrow defects remain open. The latest eight-view Mage costume drawing is rejected for incorrect camera views and background.

Production of the complete six-character factory is blocked by workspace capacity: approximately 160 MiB free on the 32 GB filesystem. The measured current native-pose output projects to roughly 5.4 GiB for remaining pose positions before reuse, excluding source drawings, sheets, atlases, replay scratch and Git. This is an estimate, not a minimum. A small pilot still fits, but full scope does not. Expand to 64 GB or provide a persistent volume with at least 20 GiB free. No original art or source guide is removed.

See `docs/character-factory/review/patch001-three-class-readiness-20261026/` for the per-character/action/direction matrix, receipts policy, measured capacity and resume sequence. Historical status sections below do not supersede this state.


In production; not release complete. Six characters: male/female Swordsman, Mage and Archer.

## Closed native casting cycle and bounded atlas pages — 25 October 2026

Coverage remains **2/96 imported jobs; 94 missing; zero complete newly verified
characters**. This checkpoint adds no completed character or accepted new art.

- Mage casting now has a captured 32-pose native cycle across four real diagonal
  cameras: original 24 Enter/Shoot/Exit samples plus four entry and four recovery
  poses. All 128 captures pass geometry/hash checks; every view has zero endpoint
  matrix, projected-joint and visible-pixel differences.
- Supplementary class-color NE guide preserves all 32 pose controls and every
  alpha pixel. New unpublished guide PNG packaging preserves visible RGBA and
  metadata; original capture receipts and stable identities are retained.
- Whole-cycle paint failed the original grid extraction. Component analysis
  recovers 32 complete figures with one measured shared lattice and no per-frame
  fitting; bilateral foot correspondence passes 32/32 (maximum disagreement
  7.713 native pixels). Hand/staff alignment and semantic cutouts remain open.
  The padded regeneration invented effects and stays rejected. Earlier batch
  painting changed leg stance. No study is imported as a complete character.
- Raw-sheet extraction now has a separate tested padding/empty-cell gate.
  Multi-page part export supports 32+ poses in bounded 4×4 atlas pages; loop
  endpoints must match for both master and each independent part. The historical
  16-pose Mage pilot retains all 120 PNG/GIF files byte-for-byte after upgrading.
- Recovered Mage draft now exports 32 poses as 12 separated proposal sheets plus
  two master pages. Real Chromium: 64 comparisons, zero pixel differences/page
  errors. Right-arm/staff motion audit fails 22/32 poses, maximum 91.556 native
  pixels even with one fixed reference offset. This is an explicit blocker;
  exact recomposition and boot correspondence do not override it.
- 207 factory tests pass. Evidence, native four-view and painted draft GIFs:
  `docs/character-factory/review/patch001-closed-casting-20261025/`.

Next production gate remains clean, source-aligned continuous illustrated art,
then semantic cutouts/swaps and actual runtime admission, across all required
actions and six characters. Native guide loop closure does not approve painting.

## Canonical motion and visible Mage sheets — 25 October 2026

Mechanical coverage remains **2/96 imported jobs, 94 missing, zero complete newly verified characters**. The new Mage artifacts are isolated pilots, not admitted characters.

- Read the original Astraeon rig with verified Blender 5.2.2. Native Mesh2Motion/KayKit poses exported with all 66 donor bones and checked against retained source world landmarks; 51 canonical body/finger bones receive explicit world-rest rotations. No old actions restored.
- Actual new canonical captures: Mage CastRelease 64 poses, Archer BasicAttack 64 poses and Mage full BasicAttack 96 poses. All four real cameras. Rotation error <=1.75e-7 rad, floor error <=1.20e-7 m, identical world prop poses across cameras. These are 3D painting guides, not final artwork.
- Mage NE CastRelease: sixteen illustrated poses, one fixed pair of boot cutouts follows captured ankle/toe controls. No whole-character fitting. Bilinear premultiplied slot sampling avoids the bright cubic edge discovered by tests.
- Four visible ownership layers (body, head, staff, hand occluder), plus two explicitly empty FX layers; six separate 3072px sheets and a master sheet. The refined head labels return 1037 thin cuff/shaft fragments to the body; master pixels do not change.
- Fixed 768px export recomposes exactly. Empty-directory replay reproduces all 122 files byte-for-byte. Actual Chromium: 32 comparisons over 16 poses, zero changed pixels and page errors. 190 Python tests pass.
- Hidden anatomy, hand/staff semantic review, swaps and the other directions remain open. Exact recomposition is not art approval. CastRelease is a one-shot excerpt; its GIF deliberately does not loop from lowered hand back to raised hand. A full native casting cycle is the next production step.

## Selected long trail and real female cosmetic import — 24 October 2026

Current mechanical coverage:48/48 captured guide families,2/96 imported cutout
jobs,94 missing, zero complete newly verified playable characters. Both imports
are Swordsman BasicAttack: male original art plus a female shared-armor head
variant. This is not two complete characters and does not complete0.0.1.

The requested long dragging trail now follows33 actual Blender subframes from
native11..13, bounded at2.4blade lengths, with a55% then15% fade. It is in the
actual current male/female imports. Male's256 non-FX bindings are unchanged;
old bindings are archived in imports/swordsman-long-dense-basicattack-20261024.
Fresh-capture empty-store replay matches all384 current male bindings and269
objects. Runtime proof:128 comparisons per sex, zero changes and page errors.
Both current actions share132 exact pixel objects; the store retains414 objects
including historical effects. Source/master art is preserved.

The female cosmetic action has64 poses and24 real separated sheets. An observed
silver-hair/face label proposal returns old collar/arm pixels to BodyCostume.
A fixed-scale illustrated head kit uses local rigid attachment to the refined
painted head centers, native roll and hemisphere gating. This avoids the failed
alpha-moment slots and several visible gaps. It is not an exact joint/anatomy
certificate; native guide markers alone were not sufficient to fit older art.
New assembled masters are partitioned into exact visible cuts before import.
Semantic neck/arm/edge review remains open; no owner approval is claimed.

New full16-frame Mage NE and Archer NW studies use one complete action sheet
rather than four generation batches. They improve some staff/bow placement but
still show foot/framing/proportion drift. Local Mage staff-only repair created
neck/torso seams and is rejected. No Mage/Archer job was falsely imported.
Detached-neighbor cleanup removes2995 unrelated Mage pixels while retaining
all selected RGBA unchanged; it does not fix anatomy. An optional Archer
material-guide render has9 alpha-edge differences and is not a canonical guide
replacement. Original48 source captures remain intact.

177 Python tests pass, including actual Blender checks. Continuous GIFs/APNGs,
real runtime reports, source/assembly proofs and reproduction recipes are in:
`docs/character-factory/review/patch001-long-dense-sword-trail-20261024/` and
`docs/character-factory/review/patch001-imported-swordswoman-basicattack-20261024/`.
Continue every required action for all three classes and both sexes; reusable
hair/costume changes per class and actual complete-character playtests remain.

## Longer sword trail variant — 24 October 2026

User requested a longer impact trail. The new source-path variant raises the
history bound from .55 to .80 blade lengths, adds the real source11→12 interval,
and tapers the old tail. First emission/source13, fade25%, timing1070ms and all256
non-FX asset bindings are unchanged. All64poses were imported into an isolated
variant store and atlas-packed; actual Chromium passes128 comparisons with zero
differences and page errors. Separate front/back sheets and before/after GIFs:
`docs/character-factory/review/patch001-longer-sword-trail-tapered-20261024/`.
Baseline factory/art remain preserved. This variant does not complete0.0.1 or
change the1/96 baseline imported-paint count. Five focused tests pass.

## Fresh Blender capture → real factory → runtime replay — 24 October 2026

The retained male Swordsman BasicAttack has now been rebuilt against a newly
rendered64-pose Blender capture, using a separate empty content store. All384
part bindings,265 pixel objects, asset IDs, fitting metadata and64 pose bindings
match the existing factory output. Both rebuilt atlas pages match exactly.
Actual Chromium runtime drawing passes128 base/trail pixel comparisons with
zero changed pixels and no page errors. Existing artwork/store were untouched.
Native768px runtime captures, four-view GIF and full-color APNG use the original
1070ms timing table and one shared review viewport. Evidence:
`docs/character-factory/review/patch001-fresh-factory-20261024/`.

An observed reproducibility defect is fixed: Blender PNG Date/RenderTime metadata
changes raw capture-manifest hashes while pixels/poses remain identical. Sidecar
seals are created only against original byte-pinned references, without editing
those recipes. Fresh captures must match every recorded pose, relevant job field,
camera and visible RGBA pixel exactly. Alpha, visible color, pose/control,
renderer, camera or sealed-artifact changes are rejected; unsealed legacy
references remain strict. No source/art compatibility fallback is introduced.

A second new64-pose Mage source capture also matches its sealed source identity.
Reassembly reproduces all16 frozen painted frames plus the master sheet exactly;
frozen labels replay64 visible roles exactly. Those Mage masks remain semantically
rejected and are not production art. Reproducibility does not fix their staff
ownership/source-fit failures. New colored-guide/template studies improve the
staff screen-side but retain figure-size/placement errors and remain unadmitted.

159 Python tests pass, including actual Blender source/wrist regressions,
fresh-capture identity negative tests and sealed-source assembly tests. Both
Node test files pass. Current production count remains1/96 imported paint jobs,
95 missing, zero complete newly verified playable six-character packages.
All six characters and every patch action remain required. These are progress
and factory proofs, not a completed0.0.1 release or blanket art approval.

## Temporal source audit and Mage continuation — 24 October 2026

Current coverage is **48/48 captured source jobs, 96 unique paint jobs,
1 imported paint job, 95 missing and zero complete newly verified playable
six-character packages**. Requested coverage remains 114 action instances and
12,992 pose positions. Counts fell through genuine source reuse, not discarded
actions: Mage Guard now reuses CombatIdle/CastChannel geometry while retaining
its own action timing and future ward FX.

The research-derived continuity diagnostic detected nine suspect source loop
views. Swordsman Guard looped a partial recovery interval; it now holds native
Sword_Block frame10. Mage Guard previously looped Spell_Simple_Enter; it now
uses the already captured stable ward/ready loop. The repeated source audit
flags zero suspect loop seams across all48 current jobs. This is a diagnostic,
not certification of human motion or final sprite continuity. Source geometry
checks find no stale captures, cross-camera pose differences or offscreen
control points. Original accepted Swordsman attacks remain unchanged.

Mage male CastRelease NE now has a full16-pose painted candidate assembled
from four source-pinned fixed-viewport batches. The assembler recomputes every
frame from its raw sheet, rejects missing/duplicate/source-stale or moved
normalized frames, and performs no figure fitting. It is not admitted: body
packing drift and held-staff source alignment still fail. Early frozen visible
cutouts replay exactly but semantic removal tests reveal staff remnants and
incomplete head masks; those mask studies are explicitly rejected.

A supplementary Blender material guide now distinguishes skull/front face,
hands, cuffs, coat, pants and boots. Sixteen poses preserve the original
capture's alpha silhouette exactly (zero changed alpha pixels) and projected
coordinates exactly. These are pose guides only, never final3D artwork. The
first repaint improves the left/right staff path but enlarges the figure:
its lower-foot extent differs by30.5–33.5 author pixels, so it is not admitted.
A same-viewport complete design template is being tried to constrain body size.

143 Python tests pass, including actual Blender source/wrist regressions, six
fixed-batch assembly tests, six temporal tests and six material-guide tests.
Both Node test files pass. Evidence is in `research/temporal-guide-audit-20261024/`
and `research/mage-material-guide-20261024/`. Retained attacks, all three classes,
both sexes, every required action, usable cutouts and actual wardrobe variants
remain required; no final acceptance is claimed.

## Reusable head-slot continuation — 24 October 2026

The shared covered-armor experiment now freezes 64 head-slot variants across
four real directions, with 24 separated sprite sheets and unchanged sword,
glove and trail files. It remains a draft, separate from the female base paint
job. Projected native neck joints do not coincide with some earlier painted
neck placements. A frozen 2D head-slot proposal follows the original head masks
without moving or scaling the body. Existing gold collar fragments are retained
as a separate ownership patch, then merged into the body slot for export.

Source-head basis/neck export checks all 64 native poses within 0.0000251 author
pixels. Frozen replay and exact composition are technical checks only. Visible
neck gaps, approximate head angles, and foreground-arm occlusion still need
art corrections. A later NW full-master head repaint also changes some rear
facings and is explicitly rejected as a complete strip. None of these studies
replaces the retained male artwork or increments female production coverage.

124 Python tests pass, including five new rigid head-slot tests. The accepted
male import is still the only imported paint job; 97 remain missing. See
`review/swordswoman-shared-armor-sheets-20261024/README.md` for replay commands
and precise limits. Source generation must not be mistaken for finished art.

## Retained BasicAttack imported — 24 October 2026

The accepted male Swordsman BasicAttack now has a real factory import: 64 poses,
four views, 384 part bindings and 265 deduplicated pixel objects. Native source
samples are explicitly [0,3,6,8,10,11,12,13,14,15,25,28,31,34,37,39].
Guide c297971fcef09188ff60 matches the retained source geometry within
0.000753 author pixels. No retained character drawings were repainted or warped.
The canonical renderer is unchanged; the explicit-sampling wrapper is hash-pinned.
Actual bone sockets are exported and validated independently.

The importer and atlas packer now preserve an explicit full layer order,
including trail layers behind the head, blade and fingers. Real Chromium runtime
draws from the imported atlas match all 128 base/trail comparisons exactly,
with no page errors. Review: `docs/character-factory/review/patch001-imported-swordsman-basicattack-20261024/`.

Current coverage: 49/49 source guides, 1/98 imported paint jobs, 97 missing;
zero complete newly verified playable six-character packages. Technical pixel
identity does not certify head boundaries, anatomy or all requested animations.
The retained SkillOverhead remains separate from the current 32-pose SkillAction.

Female SE studies include exact reproducible visible cutouts (16 poses, four
roles), a separate short post-cut trail, a navy bob hairstyle, and a newly drawn
crimson/silver costume. Four swap combinations reuse identical weapon/glove/FX
files. These are one-view historical uniform-sampling studies, not current
four-view female BasicAttack completion. Other female views have source-fit and
part-ownership failures; they are not admitted. The newest isolated-head sheets
also fail direct pose placement and are reference studies only. Compatible
shared starter armor is under investigation; no female fit is implicitly approved.

Validation evidence: 119 Python tests pass, including actual Blender source and
wrist render checks; both Node test files pass. Frozen cutout replay needs no
SAM2 or image generation and checks decoded RGBA exactly.

## Earlier Swordsman retained — 23 October 2026

The owner clarified that the earlier Swordsman was already visually okay. Keep
the earlier BasicAttack and SkillOverhead illustrations as the male visual
baseline, referenced in `factory.json`. Current Archer experiments do not
replace that work. This is not blanket acceptance of every action/cutout edge.

896 original source files are hash-pinned and unchanged. Bounded white-edge
cleanup and documented camera/root registration produce a separate 128-pose
review, four views per action. Body/head/weapon/hand ownership reconstructs each
master exactly. Independent trails retain their timing. The real browser draw
API passes all 256 base/trail comparisons with no page errors. Evidence:
`docs/character-factory/review/patch001-preserved-swordsman-cutouts-20261023/`.
Old source sampling is retained explicitly; no current guide identity or patch
import is fabricated. All classes, both sexes and every patch action remain
the goal.

## Runtime and visual-quality continuation — 22 October 2026

The runtime bridge now routes six distinct class/sex packages, validates class-specific actions, and resolves actual skill identities rather than hotbar numbers. The exporter consumes real imported cutouts with explicit timing/events; synthetic fixtures are tests, not playable artwork. Cache106 includes the generated policy.

146 individual Node checks and68 Python tests pass. Actual browser input verifies walking/attacking for three existing legacy saves with no page/resource errors; **zero new six-character packages are verified playable**. Full acceptance criteria and pinned other-branch references: `docs/character-factory/PATCH001_PLAYABLE_ACCEPTANCE.md`.

Reducing each layer separately introduced3,880 pixel differences across the16 male Archer NW frames. The new shared reduction and exclusive ownership reconstructs all16 reduced masters exactly. Bounded head-edge ownership refinement moves4,728 existing pixels between layers without changing the master. These fixes do not certify semantic masks: weapons still need separation, and head/arm painting drift remains. Failed constrained/upper-body repaint studies are retained and not promoted. Certified subpixel held poses now retain their actual source pose identity on import, without moving semantic event times.

## Native layer composition and current paint — 23 October 2026

Source-composite packing now preserves overlapping 768px authoring layers and
hidden body pixels. Trimmed atlas crops restore integer offsets into the full
canonical canvas; the runtime composes all parts before one final display resize.
Legacy full-frame definitions remain compatible. The bounded native cache retains
at most 64 entries / 16 MiB. Cache106 ships the compositor.

Actual Chromium pixel comparisons pass 8 checks, all with zero changed pixels:
overlapping underlays, weapon removal, head swap, opacity, trimmed offsets,
trimmed opacity, actual Archer head/body seam, and atomic missing-atlas behavior.
The old independent-layer baseline changes1,509 pixels in that actual Archer
frame. These are technical rendering checks, not semantic art or gameplay approval.

A new NW male Archer study retains 16 individual high-detail source-first frames,
repairs6/7/14/15, exact ready/recovery head reuse, and certified whole-pose8→9.
A detail export bug left PNG9 at the original pose while GIF/master held8; exports
now share one pose map and a regression test. Current masks are regenerated after
that correction. Ready frames0/15 have separate head/body/weapon proposals with
zero recomposition changes and limited hidden-body donor pixels. Weapon/glove
edges and head scale continuity remain under review. No complete imported jobs
or new six-character playable packages are claimed.

## Same-frame action sheets and semantic refinement —23 October2026

Male Archer NW has16 HeadHair/BodyCostume/Weapon assemblies and three separate
transparent sheets. These are one-view art proposals, not one complete four-view
paint job. Seven explicit local ownership probes pass after correcting neck/glove
separation, retaining fingers, and rejecting a cleanup that mislabeled a sleeve
island as equipment. Current tracking pins input hashes throughout CPU processing.

Canonical-only near-opaque matte cleanup preserves RGB and soft edges; raw art
is retained. Limited ready/recovery hidden-body donors survive source composition.
The real runtime draw API matches all16 cleaned masters under the same source-
canvas/final-resize path. Direct PNG filtering differs and remains separately
reported, up to28/255 composited channel difference. Neither comparison grants
art quality approval.68 Python and146 Node checks pass.

Source-only foot comparisons reject reusing ready boots across early poses; the
right weighted foot moves3.15 runtime pixels even from0→1. The source toe-height
check was never proof of a stationary foot. No incompatible body/boot copying.
Frame002 head-only repair does not solve its upper-body dip and is not selected;
an adjacent-frame-guided whole-pose study is in progress.

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

68 factory tests pass, including actual Blender retarget/contact checks. These technical results do not establish owner visual approval.

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

A single female SW recovery15 arrow-removal study uses an explicit3,901-pixel repair mask. Outside-mask changes are exactly zero;3,049 inside pixels change. It is not promoted: the segment between nocking hand and bow grip still needs string-mechanics review. Original master/GIFs remain unchanged. This technical repair guard prevents collateral body/head/foot changes; it does not certify the replacement artwork. All68 factory tests pass, including three local-repair regression cases.


## 2026-10-25 — high detail native Mage channel draft

New single high resolution Mage NE template drives a bounded 16-pose native channel cycle. Camera stays fixed; one recorded static art calibration is reused by all frames. Staff motion passes 16/16 (maximum 0.449 native px), loop seam 2.551 px versus maximum ordinary adjacent motion 3.756 px. Browser master/parts comparison passes 32/32; frozen motion implementation reproduces 83 files byte exactly. Six separated sheet slots include two empty effect slots.

Visible partitions are not complete hidden surfaces: the staff remains visibly occluded at the hand, and body needs underpainting before arbitrary head/weapon swaps. No gameplay admission, no additional imported paint jobs. Ledger remains 2/96 imported, 94 missing, zero newly complete playable characters. Review: `docs/character-factory/review/patch001-native-channel-hd-20261025/`.


## 25 October 2026 — overlapping Mage parts, hairstyle swap and game gate

One Mage NE native hold has two separate hairstyle choices over the same 16-pose motion. Hidden neck pixels and a rear staff pass are retained, with independent per-role atlases and fixed native offsets. Hair fragments no longer remain in the outfit, and a cloth fragment is removed from the weapon ownership. The same 64 non-head objects are shared by both variants. Near-opaque source alpha is explicitly repaired by at most five levels; added hidden pixels do not change that reference composite.

Real game source compositor: 32 poses / 64 light-dark comparisons, maximum rounding difference 1/255, no page errors. Frozen motion/initial atlas replay matches 216 files byte-for-byte; separate-role atlas replay is recorded independently. Factory tests: 239 pass; direct Node modular runtime tests: 40 pass. App static cache moves to107; world data and world/asset cache namespaces stay unchanged. Legacy saves for classes0/3/12 move and perform their proper basic action (Mage casts).

Fresh character creation remains blocked: `assets/characters/swordsman-male-patch001/sprite.json` is absent and returns404. This is documented, not bypassed. Large-motion segmented casting still has shoulder/occlusion work; additional drawn costumes and camera templates need registration. No new full imported paint job or playable character: **2/96 imports,94 missing,zero newly complete characters**. Review/report assets: `docs/character-factory/review/patch001-layered-swaps-20261025/`.
