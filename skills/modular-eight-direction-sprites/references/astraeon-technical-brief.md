# Astraeon technical brief — permitted newest-branch snapshot

Reviewed 2026-10-11. [User constraints](user-constraints.md) override prior inferences. No character artwork, sprite atlas, animation asset, or asset-authoring output from any game branch was used for this iteration.

## Branch selection and access

GitHub branch commit timestamps were compared, excluding obsolete main. The newest observed branch was `backbone/dev-tool-gap-closure-0.0.1`, commit [`562dfe0e163e96c26189db165e6b2be28a10c5dc`](https://github.com/basicbasja-cloud/Astraeon-online/commit/562dfe0e163e96c26189db165e6b2be28a10c5dc), committed 2026-10-10T18:04:58Z. Recheck recency before future game modifications.

Technical files were read through the GitHub connector at this exact commit. The local checkout was not switched or changed: a combined fetch including an older character branch was rejected by automatic approval review; a subsequent newest-only fetch stalled and was terminated. Connector reads provided the required newest snapshot without loading the excluded assets. No claim is made that a new branch was checked out.

Permitted references include [README](https://github.com/basicbasja-cloud/Astraeon-online/blob/562dfe0e163e96c26189db165e6b2be28a10c5dc/README.md), [equipment-slots.js](https://github.com/basicbasja-cloud/Astraeon-online/blob/562dfe0e163e96c26189db165e6b2be28a10c5dc/equipment-slots.js), [world-view.js](https://github.com/basicbasja-cloud/Astraeon-online/blob/562dfe0e163e96c26189db165e6b2be28a10c5dc/world-view.js), and [locomotion/cosmetic requirements](https://github.com/basicbasja-cloud/Astraeon-online/blob/562dfe0e163e96c26189db165e6b2be28a10c5dc/research/character-locomotion-and-cosmetics.md). These establish technical requirements, not approved art.

## Current contracts

The browser game uses a 2.5D scene: authored 3D scenery and directional illustrated actors. Its town camera defaults to vertical FOV 15°, downward pitch 46°, yaw 0, zoom 125. The README explicitly labels 46° as an Astraeon choice rather than independently verified Gravity behavior. Runtime pitch can range from 10° to 89°; camera yaw also changes.

An eight-direction sheet describes azimuth samples at a chosen capture elevation. Camera yaw requires world-to-view facing conversion. Camera pitch cannot create missing elevated artwork from those eight images. Verify the actual billboard policy and camera extremes before finalizing the export convention. The motion lab projects fresh geometry at adjustable elevations; that capability does not transfer automatically to flattened sprites. It uses orthographic projection for diagnosis, not the game's full perspective renderer.

| Authoritative stored combat slot | Semantic ID |
| --- | --- |
| `weapon` | `mainHand` |
| `offHand` | `offHand` |
| `armor` | `body` |
| `shoes` | `shoes` |
| `relic` | `accessory` |

Appearance selection and owned cosmetic items must be separate from stat modifiers and combat equipment transitions. Hats, hair, costume variants, and wings may be cosmetic selections without becoming extra combat slots. The study's four cosmetic controls are diagnostic examples, not proposed changes to this contract.

## Motion requirements carried forward

- Simple, grounded Ragnarok-inspired movement with complete body coordination.
- Earlier higher-FPS preference is superseded for the current attack: lower RO-like pose cadence with explicit holds. Keep renderer update rate independent; see binding user constraints.
- Fresh idle and locomotion poses; no animated legs pasted under an unchanged torso.
- All eight facings retain consistent scale, anatomical handedness, root registration, and action phase.
- Body motion controls the timing and attachment transforms for hats, weapons, shields, and eventual back cosmetics.
- Review normal and quarter speed, native display scale, loop boundaries, contacts, starts/stops, turns, and reactions under the actual camera.
- Existing runtime transitions or shared GPU textures do not prove that the underlying animation is visually acceptable.

Unresolved production choices include a new approved identity/turnaround, native sprite size, body families, final part coverage, action/grip scope, exporter format, and the engine's exact billboard/facing mapping. Continue independent studies while those remain open; do not revive rejected character assets as shortcuts.

## Dedicated review branch, 2026-10-11

The branch heads were rechecked before publication. `character/production-factory-v2`, commit `e130b217da3ba9e56cce7d1e33bf29f20daedd7a`, was the newest observed head, superseding the earlier creation-base snapshot above. The dedicated working branch `research/modular-sprites-full-body-2026-10-11` was created from it. Its existing character artwork was neither inspected nor used; this update checks branch metadata rather than revising the earlier technical-contract study. Future research edits stay on the dedicated branch as explicitly instructed by the user.
