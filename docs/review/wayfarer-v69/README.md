# RO3 town edges and continuous aged paving — source 69

The curb follows the edge of the building zone. Houses own stone bases and
private paving; street and building-side walks share aged rectangular stones.
Grass follows foundation margins and selected mortar joints. Trees, planting
and small city props use original textured artwork.

The separate stone-image pads looked stamped onto the road because their joints
and local stone scale conflicted with the underlying paving. All 20 pads are
removed. The current town keeps one continuous worn-stone material, with 160
native three-blade grass tufts rooted in actual authored mortar/crack joints.
There are no stone-image overlays in the current scene or precache.

Branch: `codex/world-pipeline-v3-proof`. Parent source 68: `27c65c1`.
Pushed source checkpoints: `079f8f9` (house lots, curb and grass), `4aefbd7`
(tree volume), `9bc6773` (rectangular road paving), `e20dd3d` (city textures and
planting) and `159403e` (pad removal and integrated joint grass).
Native authoring remains pass 69; boot/page/static cache is 74.

The six native views pass the scoped agent review in `visual-test.json`.
`comparison.html` provides matched before/after images and the supplied reference.
`summary.json` records code, source, browser and performance outcomes.
**Town Golden accepted=false; locomotion accepted=false; cosmetics implemented=false.**
Agent screenshot review does not establish user acceptance or device performance.

## Saved source

- All 37 ordinary houses have two staggered bevelled plinth courses and a cap,
  490 apron sections, 420 rims and 70 entrance gaps. Twenty planned sections
  crossing steps/slopes were omitted. These 910 native surfaces are walkable;
  aprons rise .055 and rims .105. Source 68 house envelopes, its 13.1% density
  increase, one infill and tiered planted fountain remain.
- 629 bevelled stone curb blocks (.12 rise, .30 width) bound building-side zones
  outside the through-road union. Crossings, services, doors and steps stay open.
  Streets, stairs and house aprons share rectangular stone art and world UV
  scale 8. The fine hexagon-like repeat is removed; the road tone is slightly darker.
- 308 foundation grass strips and 2,464 three-blade clumps follow private margins.
  Of those strips, 244 fit outside private rims and 199 widen toward .58–.82.
  Another 68 roadside strips creep onto the building-side paving beyond the curb.
  Shared painted grass has transparent, organic edges.
- The 160 new joint tufts occupy 20 selected building-side regions. Independent
  floor and authored-UV sampling verifies every root. They preserve existing
  walkable floors, collision and navigation.
- Five inherited flower beds and 22 orphan ground-flower groups move into 27
  grounded grass islands along building-side curb edges. Raised flower boxes,
  formal fountain beds, owned entrances and adjoining shop displays remain.
  A native refit follows paving slopes at 3,913 plant/grass vertices, correcting
  up to .022995 height. The city-detail check preserves 39,674 preceding parts
  and accounts for the 431 moved plant parts.
- Trees retain original roots, placement and collision. They have 264 textured
  bark parts, 608 bowed leaf layers and 280 rounded crown tops. Crown extents
  fit preceding visible canopy bounds. Original-alpha leaf casts are rebaked.
- 147 new main-house windows and 64 windows in 11 formerly plain wings join
  455 retained windows: 666 windows with 5,994 clear outward pane rays.
  Houses have weathered walls/base patina, lanterns, upper flowers and drains;
  14 wing gables have timber relief. The 27 goods stations fit native proxies.
- Eighteen formerly plain city materials gain shared metal wear, cloth weave,
  petal veins, rind, paper fiber or appropriate stone/glass/water art. Only
  intentional fire/light colors remain plain. Paving, grass and leaf artwork
  is 1254²; prop surfaces, bark, curb and masonry are 1024². Lossless WebPs,
  editable PNG masters and provenance are under `assets/` and `authoring/materials/`.
  No RO3 pixels or models are imported. Native per-texture anisotropy is 4×.
- Native alpha blending preserves grass/patina margins. House reveal qualifies
  tall hidden collision cores and raycasts visible facade triangles. The home
  fixture reveals the player behind `frontage-riverside`.

## Evidence and practical limits

The six final views use native 1280×666 buffers at pixel ratio 1, in a 1280×800
DOM, with camera distance 160, yaw 25° and pitch 46°. Source 68 before views use
the same camera and resolution. `curb-tree-trial/` records the earlier tiny-cobble
trial. Screenshots establish appearance; `services/` checks ordinary input separately.

- `city-detail-check.json`: no stone pads, 160 independently checked joint roots,
  368 ground contacts, 187 new decorative surfaces and exact preceding floor/
  solid preservation. `curb-grass-check.json`: 68 strips and 272 grounded vertices.
- `contact.json`: 229,376 quarter-unit samples, 416 occupancy changes explained
  by 27 goods colliders and 7,595 elevation changes explained by 910 house/629
  curb surfaces; no unexpected changes. It covers 64,501 low exterior vertices.
- `traversal.json`: 17 reachable destinations and 10 clear patrol loops, without
  route repair. Actors, services, lights, portals and navigation remain intact.
  Moving human height stays 70*(92/76)/35≈2.42105 world units.
- `street-geometry.json`, `aperture-clearance.json` and `wing-clearance.json`
  record new, retained and wing-window rays. `house-life-check.json` records
  dressed houses and 1,936 goods-station vertices contained by native proxies.
- `unit-tests.log`: 95 individual passing Node checks across six files.
  `schemas.log`: four public schemas pass. `parity.log`: saved Blender/export
  parity and shared transforms pass; the RAM-only Hall move deliberately
  invalidates its test bake and produces the expected stale-bake diagnostic.
- `geometry-budget.json` separates object triangles from terrain/decorative
  triangles. Source 69 has 457,394 visible object triangles and another 22,012
  terrain triangles. These counts do not establish FPS.
- `native-authoring.json`, `corner-final.log` and `floor.log` record the saved
  lighting and bakes. The floor atlas is 1536² with original-alpha foliage casts.
  `bake-index-check.json` records 4,096 matching full/indexed land comparisons.

Ordinary Merchant, Artisan and Housing Keeper interactions, field exit and saved
character reload pass with zero runtime/resource errors. Cache 74 migration and
offline reload pass with 106 precached requests and the current 1536² floor atlas.
The first service attempt timed out; the successful retry reads one live position
snapshot with unchanged arrival tolerance and travel deadline. Both logs remain.

Isolated sound-on SwiftShader timing **fails**: 1.3433 FPS, p95/max 866.6 ms and
only nine samples/eight moving player pairs. No frozen pairs were observed in
that small sample. The unchanged gates require >55 FPS, p95 <25 ms, max <80 ms
and >100 moving pairs. Physical GPU performance and gait continuity are unverified.
Exact outcomes are in `summary.json` and `performance.json`. User Golden acceptance,
broader civic carving, functional street goods and painted gait/anatomy remain open.

## Continue from the saved source

Authority is `authoring/wayfarer-spatial.blend`; export is
`world/v3/wayfarer-spatial.json`. Historical once-only migrations are not a rebuild
recipe. Preserve their guards and the original art masters. Current parameters
and migration order are also in `CURRENT_HANDOFF.md`.

Use Blender `--python-exit-code 1`. Geometry/light edits require sequential
source save/export, corner bake, original-alpha preparation and floor bake.
The corner baker excludes vegetation; leaf-only edits need the alpha-aware floor
bake. Removing an unused material also changes the shadow digest, so the final
pad-removal step includes a fresh floor bake. Do not mutate or bake during browser
review or isolated timing. Keep the development server on port 8011 running.
