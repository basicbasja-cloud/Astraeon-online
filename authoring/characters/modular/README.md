# Modular source insertion point

Put each approved canonical design in `<characterId>/approved-reference.png`,
with `<characterId>/definition.json` recording its approval reference, identity
locks, camera, handedness, shared source normalization, poses, sockets and parts.
Directional masters go in `<characterId>/masters/{S,SW,W,NW,N,NE,E,SE}/`.
Render whole normalized strips to
`<characterId>/parts/<partId>/<AnimationId>/strip.png`, with eight canonical
rows and chronological frame columns. Keep raw originals alongside normalized
strips. There is one shared registration; never fit individual parts to alpha.

The existing Warrior identity seed remains in
`../gait-rig-v50/approved-warrior-seed.png`. Adjacent motion studies are not approved.
Do not rename a rejected study into a master or invent a permanent Mage design.

Temporary proof originals are generated into `/tmp/astraeon-modular-sources` by
`python3 tools/build-modular-proof.py`; the checked-in generator is their source.
The committed modular atlases/metadata in `assets/characters/*-proof` are explicitly
`DEV_ONLY / PLACEHOLDER / NOT_FINAL_ART` and are excluded from default player use.
See [the production contract](../../../docs/MODULAR_SPRITES.md).
