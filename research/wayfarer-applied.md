# Wayfarer research applied — 3 October 2026

**Active authority, 2026-10-05/source68:** RO3 is the hard reference for exteriors,
scale, texture/shading, building density and the fountain. All36 preceding
ordinary house envelopes plus one new street house use the facade kit. Occupied
house ground grows13.1%; public squares stay open. The fountain gains tiered
pools, a scalloped rim, raised planted corners, green benches and walkable steps.
Original ASTRAEON identity and civic hierarchy remain. Review and checks are in
[the source68 review](../docs/review/wayfarer-v68/README.md). User Golden approval
and locomotion/art acceptance remain open.


This is an implementation record for the existing branch, not Golden acceptance.
The supplied Wayfarer concept owns original identity and civic hierarchy; the active RO3 directive above controls exterior/density/fountain presentation. No Ragnarok client
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

The default town uses the 15-degree lens and controls, with a user-directed shallower 46-degree downward pitch, centered follow and
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

## Movement and town-scale recheck — 2026-10-03

The [current community entity renderer](https://github.com/MrAntares/roBrowserLegacy/blob/master/src/Renderer/Entity/EntityRender.js) derives walking frame cadence from accumulated distance and action delay. Its internal-unit conversion is client-specific; Astraeon uses measured art registration and its own world-unit stride lengths instead of importing that numerical constant. The [GAT specification](https://ragnarokresearchlab.github.io/file-formats/gat/) describes map dimensions in navigation tiles. These are not directly interchangeable with Astraeon world units, so the expanded town is not claimed to reproduce a proprietary town size.

Applied recheck: expand land area fourfold, preserve a civic hierarchy and connected district streets, keep the classic community camera lens/control reference, replace an incomplete running cycle, and verify the actual rendered soles and complete RAF intervals. The supplied concept is an atmosphere/composition reference rather than a strict layout.

## RO3 visual comparison — 2026-10-04

The publisher's [RO3 site](https://ro3global.com/) links its [May 27 developer diary](https://club.joymaker.com/article/170403/?from=web). The diary discusses PC experience and combat improvements. Its embedded video could not play in the review browser (YouTube error 153); no claim is made that this footage was watched. [Gravity's issuer release](https://www.globenewswire.com/news-release/2025/10/27/3174382/0/en/RAGNAROK-3-Chinese-Title-%E4%BB%99%E5%A2%83%E4%BC%A0%E8%AF%B43-Received-an-ISBN-Code-by-Chinese-Government.html) identifies the official RO3 channels.

Actual published town screenshots were inspected in [GameSpark's report of Gravity's first full gameplay trailer](https://www.gamespark.jp/article/2025/07/31/155611.html), credited to the official trailer. This secondary source supplies visual frames only; technical camera/engine specifications still rely on inspected primary community sources above. The Geffen frame shows broad, readable stone masses, restrained cool stone, warm sunlight, recognizable civic arches, clear cast shadows and clustered planting around routes. Those are visual inferences, applied through original ASTRAEON meshes/materials: stronger civic architecture, grouped planting, deeper commercial/residential facades, quieter painterly colors and soft street/water transitions.

The published frame is only 600 by 338 pixels. It cannot establish native game resolution, texture dimensions, texel density or the final shipping renderer. No RO3 pixels or proprietary files are included in ASTRAEON. The supplied concept retains priority for ASTRAEON identity; it is used for atmosphere and placement logic rather than reproduced as a fixed geometric diagram.

## Direct RO3 video inspection and paving pass — 2026-10-04

The official [first full gameplay trailer](https://www.youtube.com/watch?v=n8PqmhQBHzc), published by the RagnarokOnline3Global channel, played successfully in the in-app browser during this continuation. Paused footage at about 0:37 (Payon), 0:45–0:47 (town streets/merchant gathering) and 1:41 (dungeon) was actually inspected. The earlier diary playback failure remains a separate historical observation.

Visual inferences: connected stone street/court surfaces, planting concentrated around their edges, grouped roof silhouettes, readable broad material values and building cast shadows give the town coherence. The supplied ASTRAEON concept similarly places most of the city on stone paving with gardens between streets and along the river. Applied v48: joined stone interior, framed tree pits, projecting windows and shutters, chimney/oriel silhouettes, Hall turrets, and baked overhang/contact depth on original editable meshes. No RO video, pixels or proprietary assets are copied into the project. Video playback still cannot establish native texture sizes or engine settings.

Animation recheck: distinct crop indices, simulated opposite-foot metadata and zero rendered-sole drift did not establish correct anatomical leg alternation. The v47 whole-body foot lock held the pelvis/head between poses and then released it at the next frame. V48 removes that hold and checks rendered-root continuity. The generated same-leg candidate was rejected; no new generated movement artwork is installed. A proper left/right gait remains required for visual acceptance.

## Strict concept, Prontera proportions and depth — 2026-10-04

Later user steering supersedes the earlier loose-reference interpretation: building design, silhouette, tone and relative scale must closely resemble the supplied ASTRAEON concept. Its Consortium Hall is a major monumental building beside much smaller people and timber houses; the walled city stands above water. Preserve ASTRAEON identity while using Prontera as the reference for city proportions, connected avenues and civic hierarchy.

The [official Japanese Prontera guide](https://ragnarokonline.gungho.jp/gameguide/worldmap/prontera.html), its [town overview](https://ragnarokonline.gungho.jp/gameguide/worldmap/rune-midgarts/imgaes/town/town_img_01.jpg) and [marked map](https://ragnarokonline.gungho.jp/gameguide/worldmap/rune-midgarts/imgaes/town/prontera.jpg) were inspected. The map supports a long axial avenue, connected branching streets, a substantial northern civic quarter and housing/shops around public space. These small official images cannot establish exact player-to-building measurements. Astraeon's 112 × 128 world-unit town is not claimed to copy Prontera's proprietary dimensions or navigation tiles.

The [RO3 first-look gameplay recording](https://www.youtube.com/watch?v=648A_LVV9T8), by geocine, was also inspected at selected points: tutorial around 0:48, unmounted forest combat around 6:18–6:28, menus/town around 19:24–22:59, town-street dialogue around 24:08, and mounted travel around 25:22. The town view shows cobbled public routes, paving borders, merchandise against façades, flower curbs, warm stone and cooler contact shade. This is a visual inference from a third-party recording, not a measurement of native resolution, texture dimensions or gait timing. The entire hour was not watched.

Applied source v49: Hall width ×1.45, depth ×1.12 and height ×1.48 relative to the previous source, with a broad ribbed dome/drum, nave and aisle roofs, unequal towers, recessed entrance, pointed windows and flying arches. Adjacent houses move away from its wings. Inn, shrine, forge, market and frontage families gain original attached volumes and functional façade details. A 1.4-unit upper civic precinct has retaining walls, coping and three eight-tread flights. The river and masonry bank extend farther below the city; existing bridge decks remain usable. Roads are routed around actual lots, and all ten closed civilian routes are re-planned against the saved geometry. Ground-height camera follow and ground interaction projection account for the terraces.

These changes remain a review candidate. Architecture is still simpler than the concept and the shipped character gait artwork still has weak opposite-leg/passing poses. Rejected generated gait strips remain outside runtime assets. Schema, route and playback tests do not certify the requested visual quality.
# Supplied Prontera map and RO3 tour — 2026-10-04

The user's three acceptance criteria remain independent: strict concept architecture, depth and placement (including waterfalls); Prontera town size, walking scale and adaptable NPC life; anatomically correct animation, size and frame mapping. A passing runtime check does not approve any of these visually.

- [Prontera Small](https://rathena.org/board/files/file/3563-prontera-small/) is a custom community map by INDYPLUS / Ragnarok Edit Plus, version 1.0.0, released July 9, 2017. The public indexed author page supplies that metadata; the live browser is held at automatic Cloudflare verification. The actual map and author screenshot have **not** been inspected or downloaded. Its title does not establish canonical Prontera dimensions.
- [Ragnarok Online 3 (Beta) Prontera City](https://www.youtube.com/watch?v=RZ06YmcbxkU), NunuSaPunso, is the supplied hard gameplay reference. The browser played it successfully. Selected views were inspected at 0:30, 1:00, 1:35, 2:07, 2:39, 3:11, 3:42, 4:14 and 4:46; this is selected scene review, not a claim of frame-by-frame review of all 5:18.
- At 1:35 and 2:07: narrow paved residential lanes, genuinely deep projecting roofs/dormers, repeated but varied timber buildings, planted edges and strong sun/shade separation. Character-relative street width matters more than raw map units.
- At 1:00: a substantial sculptural monument and benches around planted public-space borders. At 2:39: a purpose-built training yard separated from the street. At 3:11 and 3:42: merchants and small service clusters along wider connected paving, with flowers, carts, crates and trees placed at edges. At 4:14: an elongated planted median and benches organize a larger public street; multiple NPCs have distinct roles. At 4:46: the city gives way to a softly blended grass/path field with warm directional shafts.
- Full-screen paused walking frames around 1:35 were advanced in three successive six-video-frame increments. Body/cape pose and travel change coherently. The robe partly hides the lower limbs, so this small sample cannot establish every leg contact or an exact source animation frame count. Do not invent an RO3 FPS/cadence from these observations.
- `prontera-scale-reference.json` records the measured **312 × 392 navigation cells** from the public rAthena pre-renewal map cache at a pinned revision. The current original town is **112 × 128 world units**. Conversion and person-relative travel still require calibration; these differently defined dimensions are not equal, and the current scene is not claimed to be a scale copy.

Applied source refinements: continuous submerged bank sections, three masonry spillways with falling water and softly blended foam, a larger celestial fountain basin with a volumetric draped statue, pierced Hall clerestory/aisle bays and buttresses on pier axes. Broader unequal flagstones replace tiny uniform paving courses. No RO models, map cells or texture pixels ship.
# Current reference and locomotion authority — 2026-10-04

**Later user-requested pause:** current saved source is64, boot/index63 and service-worker62. Read `../CURRENT_HANDOFF.md` and `../docs/review/pause-2026-10-04/summary.json` before continuing. Subsequent source63 adds a raised irregular merchant court with four stair flights and six cloth canopy assemblies; source64 grounds310 whole flower groups and adds rooted soil/leaves. Corner64 is saved/exported, but ground64 is not baked: stale63 metadata was correctly dropped. Three preserved gameplay views and schemas/tests are63 evidence, not64. No64 visual/parity/performance approval. All town and animation Golden gates remain false. User rejected the gait dashboard for sliding/position drift and the town for flat/lifeless presentation. All raw72 gait captures and transition records are archived. New east painted strip63 is held/uninstalled, with native target annotations explicitly not measured painted contacts. Development paused before further work; push is a preservation checkpoint.

This checkpoint supersedes earlier loose-concept interpretation and older Hall scale values in the history below. Approved Wayfarer art controls original identity, macro layout, districts, landmark hierarchy and architecture. RO3 Prontera screenshots are the primary presentation comparison for camera, materials, light, shadows, street readability and density. Reference-image low resolution is not the output target. Keep original ASTRAEON IP; no copied RO assets or literal Prontera reconstruction.

All ten local `RO3 Ref/` images have been visually inspected. The important recurring qualities are organized cobbled streets and lighter side courts, substantial gables and dormers, deep framed façades, strong warm directional light with cool cast/contact shade, and functional street dressing clustered along active frontages. Current Hall source scale is X1.8/Y1.12/Z2.0 about its entrance, plus the raised civic terrace. Current architecture remains below the requested visual gate.

The supplied [RO3 Prontera tour](https://www.youtube.com/watch?v=RZ06YmcbxkU) was revisited through the browser at quarter speed on this checkpoint. Paused frames at approximately95.765,95.965 and96.165seconds show coherent costume/body scale and modest motion during a street walk; the robe obscures exact foot contacts. A stopped facing pose around99.97seconds was inspected too. These observations establish a presentation comparison, not an inferred proprietary frame count, stride or runtime animation FPS. No video was downloaded.

The user explicitly requires town work first, then a full shipped-locomotion diagnosis **before further generation/replacement**: frame durations/order, shared root/foot anchors, dimensions, body drift, contacts, stride, actual speed/cadence, dropped frames, state transitions, directions and cycle closure. All walk/run/sprint cycles are Golden-blocked until frame-by-frame captures, slow previews and grounded normal-speed playback pass. No static torso/procedural leg combination or interpolation/blur/playback-speed trick may conceal bad frames. Whole-body coherent strips, shared scale/root and transition inspection are required. Prior v50 crouched paintings are rejected; v51/v52 candidates remain uninstalled and unapproved.


### Verified source/runtime62 continuation

12 projecting upper-storey envelopes and roof extensions (58),48 recessed side windows replacing erroneous full-depth timber corner slabs (59),stronger .72sun/.36coolfill with native alpha-tested casts (60),and12 open attic bays/structural gables/roof crowns (62) are saved in the original source. Both62light bakes and source/export parity pass;94Node/publicschemas pass. Five actual62 gameplay views inspected; isolated sound-on60.0015FPS/p9516.8/max17.7ms/root holds0/errors0. Town remains below requested Golden appearance.

All72 shipped gait/direction cases were recorded frame-by-frame with slow previews. There were no observed skipped selected poses or held rendered roots; the actual illustrated full-body sequences fail alternation/posture/weapon/registration gates. The confirmed immediate-mode-switch bug is fixed with a queued exact-contact displacement split,19 targeted30/60/120Hz tests and ordinary-input capture. No new art installed. User now requests simple RO1-like motion and future cosmetic costumes/hats/wings; original body/attachment/ownership direction and primary research links are recorded in `character-locomotion-and-cosmetics.md`.
