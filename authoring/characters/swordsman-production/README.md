# Swordsman visual production — articulated walk repair in progress

All resulting artwork is **DEV_ONLY / NOT_APPROVED**. Internal gate decisions do
not represent owner approval. Normal gameplay artwork is not replaced.

The owner rejected earlier painted Walks and their simplified leg guide. Rig
candidate 03 passes internally at 38/40 after candidate 02’s pass was withdrawn
for inadequate rearward thigh extension. Current male Idle03, Walk28, Run01 and
BasicAttack04 separately pass internal clip gates (93, 91, 92 and 91/100).
Their source strips, previews, snapshots and reports are retained. All remain
NOT_APPROVED. Five male clips and the female variant remain unproduced; the
complete character is not ready. See the review milestone report for actual
runtime and gameplay captures.

The starting foundation is `origin/codex/modular-sprite-pipeline-v0.1` at
`38228dd26ac8c5e8676a3a5904ad945742eadc42`. Work is isolated on
`codex/swordsman-visual-production-v0.1`.

The identity authority is the unchanged
`../gait-rig-v50/approved-warrior-seed.png`, copied under `reference/`. Nearby gait
studies were rejected or experimental and are not identity authorities.
`reference/identity-lock.json` records the source measurements and design locks.
The coordinated directional candidate was repaired for camera elevation before
modular production. `masters/` contains male canonical full-canvas poses; these
are review candidates, not owner-approved replacements.

Canvas remains 320 × 320, root (160,264), reference height 176. Direction order
is S, SW, W, NW, N, NE, E, SE; no direction is mirrored. Anatomical right/left
hand sockets remain independent of screen side. Rendering uses six logical
layers; internal pose helpers never become a skeletal runtime.

`male/modular-masters/` holds BaseBody, Hair, Outfit, Weapon, Headgear and
BackAccessory independently. BaseBody contains a neutral underlying painted
body and source-painted exposed identity details; costume belongs to Outfit.
Empty headgear/back slots remain valid. The gold cape is outfit construction,
not a separately equipped gameplay cape. Component reconstruction and all pose
transforms happen in source art; runtime layers receive no registration nudges.

Meaningful image generations are preserved under `candidates/`, with prompts,
exclusions, references, method, timestamps and rejection reasons. Each whole
motion attempt has a composite strip, normal/quarter-speed GIF and provenance
under `male/motion-candidates/`. Key candidates retain lossless motion strips;
superseded/rejected construction trials retain compact comparisons and exact
provenance. Boot surfaces occluded in side-view masters
require complete same-direction component textures, rather than independently
splitting incomplete pixels. The internal fixed-camera pose guide is an aid,
not shipping character artwork.

Runtime packing can share byte-identical full-canvas frames and a single empty
cell. It never trims a layer to alpha bounds. Source PNGs remain lossless.
`tools/build-swordsman-production.py` reconstructs the current authoring outputs;
`tools/pack-modular-sprites.py --deduplicate` derives runtime atlases.
The builder is a diagnostic authoring method, not a visual-quality guarantee.
Historical retained masters/strips remain the source of their respective review
captures; later algorithm repairs do not retroactively approve earlier output.

The presentation contract supports extensible `bodyVariant` values. Both male
and female definitions remain `classId: Swordsman`. Parts resolve logical
`cosmeticId` values to body-specific artwork. Equipment is never an input to
cosmetic resolution. The loader preloads only selected cosmetic parts, then
switches appearance atomically. Existing definitions remain compatible.

Production is sequential: finish male visual and runtime gates before starting
female. Pending animation entries in temporary runtime metadata are explicitly
tagged `PENDING_PRODUCTION`; these entries must not be counted as completed
clips. The final review package and production score will be recorded only after
the applicable gates have been inspected.
