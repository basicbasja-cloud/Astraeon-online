# Painted Swordsman body authoring source

Status: **REQUIRES_OWNER_VISUAL_REVIEW**. These are new painted proof assets,
not automatically approved because their identity reference was approved.

Visual identity reference: `../../../gait-rig-v50/approved-warrior-seed.png`
(repository-designated owner-supplied/approved seed). Historical production
masters provided orientation context; procedural SVG/pose_for art supplied no
production pixels or motion authority.

The Body includes bald head, body, core class clothing, bronze shoulders,
waist details and boots. Hair, sword, shield, circlet and cape are independent
painted appearance sources. The collar/scarf belongs to the core outfit.

`generated/idle-raw.png` is a coherent eight-direction standing canvas.
`walk-D-raw.png` and `attack-D-raw.png` are coherent 16-pose canvases for each
authored direction. No runtime mirroring. `recovery-D-raw.png` is a coherent
overlapping action chunk: its first two poses overlap original frames8/9;
the compiler preserves those boundary frames and replaces frames10–15.
The original attack tail returned to an incorrect overhead pose and is
superseded. Source frame4 supplies the loaded RO key4; source frame5 supplies
its acceleration in-between. No animation frame was generated independently.

`neutral-*`, `walk-S-key-source.png`, and `attack-*-recovery-boundary.png` are
earlier authoring guides, not final runtime sources. The neutral guide's NW
view was superseded by the actual directional Idle turnaround.

Compile with `python tools/build_painted_swordsman.py`. One shared scale per
strip; overlapping chunks convert source pixel units once from shared head
landmarks. Translation locks the support baseline and measured scalp center.
The full scalp is measured even in off-center leaning poses. Source annotations
and normalization receipts live in `authoring/characters/builds/swordsman-male/`.

Idle breathing is a restrained offline warp of the painted standing raster,
explicitly classified ASTRAEON_INBETWEEN, with feet untouched. Walk/attack
body movement comes from painted coherent pose strips, not pose_for or a
runtime skeleton. Raw RO reference imagery is private research only and is
never read by this asset compiler.
