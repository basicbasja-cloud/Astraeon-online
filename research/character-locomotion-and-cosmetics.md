# Original ASTRAEON locomotion and cosmetic direction

Latest user steering (2026-10-04): finish the town, then use the sprite-pipeline skill to make simple, grounded Ragnarok-like movement. Elaborate animation is unnecessary. Characters should support interchangeable costumes/skins, hats and wings for eventual cosmetic monetization. This adds to the critical full-body quality gates; it does not authorize concealing bad poses or importing proprietary character art.

## What the current diagnosis establishes

`docs/review/locomotion-v61/` preserves 72 ordinary-input gait/direction cases, all nine 0..7..0 gameplay sheets and selected normal/quarter-speed previews. No observed frame selection was dropped and no rendered root held in these captures. The drawings themselves repeatedly lack alternating contacts and contain abrupt weapon/body changes. Mage/Ranger use variable unregistered crops and reuse one movement strip across three speeds. Their smaller visible silhouette also contributes to poor readability. Start/stop and view-switch art is not coherently authored.

The confirmed runtime defect was immediate replacement of the active clip despite an intended contact queue. Requests now wait for a declared half-cycle boundary and the traveled distance is split correctly across the old and new stride. The source's declared contacts are still not anatomical truth for bad drawings. Fresh normal-input transitions and 19 regression tests verify this timing repair separately from art acceptance.

## Reference mechanics, not imported game assets

[Ragnarok Research Lab's ACT documentation](https://ragnarokresearchlab.github.io/file-formats/act/) describes per-clip frame timing, layered sprites and body-relative anchors for heads, weapons, shields and headgear. This supports one body-owned pose clock and explicit attachment registration for ASTRAEON.

[roBrowserLegacy's EntityRender source](https://github.com/MrAntares/roBrowserLegacy/blob/master/src/Renderer/Entity/EntityRender.js) describes distance-driven walk cadence and its own cell-to-client conversion. Its constants are particular to those coordinate systems; they are not ASTRAEON world units.

The user's additional [Animation Systems reference](https://ragnarokresearchlab.github.io/rendering/animation-systems/#sprite-animations) reports experiments supporting **24 ms per ACT interval**, rather than the traditional 25 ms estimate. It compares stretched clip durations while accounting for discrete render-frame quantization. Its explanation of the original internal state-machine clock is explicitly a hypothesis. An interval is not a sprite pose: clip delays contain interval counts. ASTRAEON currently uses its own JSON and distance-driven poses, not imported ACT clips. Blindly giving each pose 24 ms would neither match RO nor correct our painted contacts. Measure authored stance-foot travel, root travel and observed frame durations together.

The user rejected the diagnostic dashboard on 2026-10-04 because the shipped art visibly slides and changes position. The zero skipped selections/root holds in the recorded run only establish renderer/selection continuity. They do not establish body registration, leg alternation or planted soles. The current full-body art remains rejected; replacing it with correctly registered, coherently authored actions is required.

[ActEditor's source/releases](https://github.com/Tokeiburu/ActEditor/releases) show a mature layer/anchor editing workflow and garment tooling. No editor or third-party animation pack has been installed; the existing whole-strip/native authoring and deterministic QA tools already cover this task.

## Asset and appearance contract to implement after town work

1. Use the approved in-game original character as the seed. Author one coherent full-body action with two legs, stable anatomy, costume and weapon, modest natural body movement and a closed loop. The whole body moves; there are no generated legs pasted beneath an unmoving torso.
2. Bake all eight directions with one shared scale and root. Preserve source contact/hip/head/back/hand transforms per displayed pose. Body phase controls every attached cosmetic's phase and direction.
3. Treat a costume/skin as a compatible full-body appearance variant with the same action/root contract. Hats and wings use authored head/back attachment points and direction-aware front/back draw order; they may have synchronized authored frames. Do not independently advance their animation clocks or guess attachment offsets from alpha bounds.
4. Validate every variant and equipment combination at normal speed, quarter speed, frame transitions, turns, starts/stops and gameplay camera. Verify grounding, footprint, visibility, sorting and hit/reaction states before runtime integration.
5. Keep appearance selections separate from combat equipment, stats and class identity. Persist selected cosmetic IDs and check ownership/compatibility. A future paid shop needs authoritative entitlements; client-only local ownership is suitable only for a prototype wardrobe.

The next production animation must pass the full-body gates before integration. The current v50/v52 studies and generated material atlas remain uninstalled and unapproved. Cosmetics and payments are not implemented at this checkpoint.
