# Wayfarer research applied — 3 October 2026

This is an implementation record for the existing branch, not Golden acceptance.
The supplied Wayfarer concept remains the visual authority. No Ragnarok client
assets, map files, costumes, names or proprietary animation data were imported.

## Reference coverage

The [RO Laboratory project catalogue](https://github.com/RagnarokResearchLab/CommunityProjects)
currently indexes 58 repositories. Their upstream links are captured in
[ragnarok-community-repositories.txt](ragnarok-community-repositories.txt).
This is a broad discovery inventory; it is not a claim that every repository or
every Ragnarok implementation has been audited. Additional relevant clients
include [NostalRO](https://github.com/nmeylan/nostalro-client) and the original
[roBrowser](https://github.com/Orkin/roBrowser).

| Source | Useful subject | Application here |
| --- | --- | --- |
| [roBrowserLegacy](https://github.com/MrAntares/roBrowserLegacy), particularly [SpriteRenderer](https://github.com/MrAntares/roBrowserLegacy/blob/master/src/Renderer/SpriteRenderer.js) | WebGL sprite offsets, texture reuse and depth correction | Registered full-body atlases in the existing shared depth buffer; remove unused locomotion atlas loads |
| [NostalRO rendering architecture](https://github.com/nmeylan/nostalro-client/blob/master/docs/internal/rendering.md), [Korangar](https://github.com/vE5li/korangar) | Explicit renderer/resource boundaries | Keep simulation and navigation independent of camera/render changes |
| [Ragnarok Research Lab ACT](https://ragnarokresearchlab.github.io/file-formats/act/) | Directional frame registration, offsets, timing | Explicit direction/phase/rectangle/anchor manifest; separate artwork from movement simulation |
| [GND](https://ragnarokresearchlab.github.io/file-formats/gnd/), [GAT](https://ragnarokresearchlab.github.io/file-formats/gat/), [RSW](https://ragnarokresearchlab.github.io/file-formats/rsw/) | Terrain, walkability and scene instances | Keep meshes, contacts, services and exported scene in agreement; these community specifications are reverse engineered |
| [RagLite](https://github.com/RagnarokResearchLab/RagLite), [BrowEdit3](https://github.com/Borf/BrowEdit3) | Tooling and map inspection | Source-scene parity checks and authored scene review, rather than importing RO maps |
| [rAthena](https://github.com/rathena/rathena), [Hercules](https://github.com/HerculesWS/Hercules), [rust-ro](https://github.com/nmeylan/rust-ro) | Server content, NPCs and transitions | Reference for hub/service organization; no new server scope or copied scripts |
| [RagnarokRebuild](https://github.com/Doddler/RagnarokRebuild) | Another client/server architecture | Comparison reference; retain the working browser stack |

Gravity's own [February 2026 presentation](https://img.gravity.co.kr/GravityUpload/0000/2026/02/13/Gravity%20IR%20Presentation_2025_4Q_EN.pdf)
distinguishes Ragnarok Online 3 from The New World and Abyss. It describes RO3
as a modern MMORPG evolution, with PC/mobile plans and GVG. Those announcements
do not provide a public RO3 engine or reusable production assets. A similarly
named promotional website is not sufficient evidence of Gravity affiliation;
its action-combat claims were not used as authoritative RO3 implementation facts.

Gravity's newer [August 7, 2026 issuer update](https://www.globenewswire.com/news-release/2026/08/07/3340984/0/en/6-k_gravity_second-quarter-2026-result-and-business-update.html)
describes RO3 as a mobile/PC MMORPG being prepared for China and global release
within 2027. This updates older launch targets; it is an announced plan, not
evidence of a shipped public client. The classic camera implementation reference
used here is RO1 community tooling, not a claimed RO3 camera specification.

## Similar-game lessons

[Tree of Savior's art director interview](https://treeofsavior.com/page/news/view.php?n=337)
explains its fixed quarter-view and illustrated textures in terms of visibility
and a moving storybook appearance. The application is our elevated view,
stronger architectural silhouettes and whole illustrated characters, not a copy
of its art. The earlier concept camera studies remain selectable for comparison.

[Albion's world guide](https://albiononline.com/news/guide-world-albion) and
[visual overhaul notes](https://albiononline.com/news/visual-overhaul-shorts)
support studying distinct destinations and environmental identity. Our design
inference is that each service district needs its own facade, canopy and street
composition: business awnings, residential bays, market goods, public paving,
and a different roof/wing/porch combination for each added lot.

[CrossCode's developer materials](https://www.radicalfishgames.com/presskit/sheet.php?p=crosscode)
provide a useful browser action-RPG comparison for animation readability and
responsive input. They do not justify replacing our current simulation stack.

## Implemented evidence

- Reauthored Hall: nave, aisles, unequal towers, lantern, pointed windows, rose
  compass, deep portal, blue slate and gold roof details. Existing services stay
  on their authored public terrace.
- Connected public paving, calmer lawns, garden/canal borders, balconies, bays,
  commercial awnings and a larger winged fountain sculpture.
- Eight individually composed district buildings, three additional stalls,
  curtain walls, watchtowers, banners and faceted river banks.
- Camera framing exposes more of the civic composition; picking uses the actual
  perspective projection. Material-compatible static meshes batch together.
- New eight-direction/eight-frame full-body walk, run and sprint strips. Two
  overlapping sprint source bodies initially used complete run poses; the final
  NW and W replacements supersede both temporary repairs. The separate SW
  strip and complete NW/W replacements are recorded in character provenance. No procedural legs are
  added to the painted bodies. Artwork quality still requires visual judgement.
- A service playtest caught a new lodge obscuring the Artisan; that lot was moved.
  Historical tests now use the current authored gate, terrace and projection.

Saved Blender geometry remains authoritative. Review screenshots and normal-input
playtests supplement schemas and unit tests; none automatically certify beauty,
anatomy, loop quality, physical-device performance or final Golden acceptance.

## Classic Ragnarok camera application

[roBrowserLegacy camera](https://github.com/MrAntares/roBrowserLegacy/blob/master/src/Renderer/Camera.js),
[camera preferences](https://github.com/MrAntares/roBrowserLegacy/blob/master/src/Preferences/Camera.js)
and [renderer](https://github.com/MrAntares/roBrowserLegacy/blob/master/src/Renderer/Renderer.js)
provide the public community implementation reference. Outdoor defaults use
angle 230 degrees (interpreted as 50 degrees downward in our Z-up convention),
yaw zero, zoom 125, a 15-degree vertical perspective lens, and smooth follow.
This is not independent verification of Gravity's proprietary client defaults.

The default town now uses those lens/orientation values, centered follow and
zoom/2 camera distance in our map units. It supports 15-step wheel zoom (65–325),
right-drag yaw, Shift-right-drag tilt, Ctrl-right-drag zoom and the corresponding
double-right-click resets. The vertical limit is 89 rather than 90 degrees to
avoid a singular upright sprite projection. Map-unit scale and smoothing are
adapted to Astraeon's runtime; the earlier oblique concept38 profile remains an
explicit comparison at `?camera=concept38`. Native floor rays, picking, sprite
rows and keyboard input all follow the current orientation. Camera gestures
must not start click navigation. A normal-input test compares the projection
against an independent Three PerspectiveCamera and exercises the gestures and
rotated click navigation.
