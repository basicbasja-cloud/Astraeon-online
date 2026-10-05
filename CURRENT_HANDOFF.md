# ASTRAEON source70 hierarchy checkpoint / cache75

Branch `codex/world-pipeline-v3-proof`. Native source70 now separates public cobbles from rectangular building walks, raises 629 curbs to .20 (618 widen to .40), and adds darker native curb fascias. Warm fill/sun and eight-ray down-left casts replace cool blue shade. Native avenue/plaza trial and 432 ground/joint contacts pass. 95 Node checks and four schemas pass. Continue the prepared town composition migration for layered conifers, larger owned green margins and facade relief, then perform the complete native/browser review. Town Golden accepted=false; physical GPU performance remains unverified. Keep server8011 alive.

Details/evidence: `docs/review/wayfarer-v70/hierarchy-review.json`, `hierarchy-check.json`, `hierarchy-trial/`. Original solids, house envelopes, services and routes remain; curb floors were deliberately changed. Commit and push each completed step.

Previous complete checkpoint:

# ASTRAEON continuation checkpoint — 2026-10-05 / source69, cache74

Workspace `/workspace/Astraeon-online`, branch `codex/world-pipeline-v3-proof`.
Origin `https://github.com/basicbasja-cloud/Astraeon-online.git`.
Source checkpoint `159403e` is committed and pushed. Earlier completed steps:
`079f8f9` (house lots/curb/grass), `4aefbd7` (tree crowns), `9bc6773` (rectangular
road paving), `e20dd3d` (city material/planting detail). `159403e` removes the
stamped stone-image pads and roots native tufts in existing paving joints. User explicitly requires a git push after each completed step.
Keep development server8011 alive. No deploy, merge, PR or shutdown requested.
Previous complete source68 handoff is in `docs/review/wayfarer-v69/previous-handoff.md`.

User direction: hard-reference supplied RO3 exteriors, scale, density, fountain,
texture and lighting. Curbs belong at the outer edge of building zones. Grass
should follow and creep into building/path edges; paving should have some wear,
offset/chipped stones and imperfect joints. The tiny hexagon-like road repeat
clashed with brick walks and is removed. Flowers and props need meaningful owned
spaces rather than isolated placements in public paving. Material detail should
be consistent across the city. Original artwork implements the observed structure.

**Town Golden accepted=false; locomotion accepted=false; cosmetics implemented=false.**
The scoped agent review does not establish user Golden acceptance, painted gait/
anatomy acceptance or physical-device FPS. Exact final evidence and limitations:
`docs/review/wayfarer-v69/README.md`, `summary.json`, `visual-test.json`,
`comparison.html` and `native/`. All six native screenshots pass the scoped agent review with zero runtime errors.
Ordinary Merchant/Artisan/Housing Keeper interactions, field exit and saved-character
reload pass. Cache74 migration/offline saved-character reload passes (106 requests, current
1536² floor atlas). Isolated sound-on SwiftShader timing fails:1.3433FPS,
p95/max866.6ms,9 samples/8 moving player pairs and0 observed frozen pairs.
Unchanged gates are>55FPS/<25ms p95/<80ms max/>100 moving pairs. Physical GPU
performance and gait continuity remain unverified. Final reports are complete.

## Saved source

Authority: `authoring/wayfarer-spatial.blend`; export `world/v3/wayfarer-spatial.json`.
Layout `wayfarer-concept-terraced-town-v49`, 120 collections, bounds112×128.
Native authoring markers remain69; boot/page/static cache is74. The source68
37 ordinary house envelopes, density increase13.1%, one infill, five tree-group
relocations and planted tiered fountain remain. Original solid vertices, actors,
services, portals, lights, walkers and navigation are preserved. Actor art,
registration and scale remain; moving human height70*(92/76)/35≈2.42105.
Held character strips remain excluded; previous handoff records gait restrictions.

All37 houses have staggered bevelled plinths/caps,490 apron sections and420 stone
rims. Seventy entry gaps and20 step/slope omissions preserve approaches.910 new
house surfaces are walkable (.055 apron/.105 rim).629 native walkable street curb
blocks (.12rise/.30width) outline building-zone boundaries outside the through-road
union, preserving crossings, services, portals and steps. These1539 surfaces change
7595 quarter-unit elevations.27 new goods colliders explain416 occupancy changes.
Do not claim all source69 floor/collision unchanged.

Roads, stairs, private paving and aprons share original1254² aged rectangular
flagstones and world UV scale8; road tone stays subtly darker. Tiny cobbles have
been removed from current town materials/cache.The separate stone-image pads were rejected for looking stamped onto the road.
All20 are removed;160 short native three-blade tufts now root in actual mortar
and crack joints in20 selected building-side regions. Independent UV sampling
checks every root against the shared stone artwork. Existing walkable floors
and solids remain unchanged. No stone-image overlays remain in the current town.

308 foundation grass strips/2464 rooted three-blade clumps follow private margins;
244 strips moved outward and199 widened toward.58–.82.68 roadside strips creep onto
building-side paving beyond curbs. Their final shared painted1254² grass has soft
organic edges and detailed blades. Grass is nonsolid/noncasting.

Five inherited flower beds and22 orphan ground-flower groups are relocated into
27 grounded grass islands on building-side curb edges. Raised flower boxes,
formal fountain beds, owned entrances and near-building flowers remain.3913
plant/grass vertices are refitted to actual native paving slopes; maximum correction
.022995. Original431 plant parts move;39674 preceding parts retain exact vertices.
The final city-detail step adds187 decorative terrain surfaces, without changing
existing walkable floor/collision geometry or navigation metadata.

Trees have264 bark-textured trunk/branch parts,608 curved leaf layers and280 rounded
crown tops with original1254² leaf cutouts. Bounds fit preceding visible canopy
extents. Roots, trunks, branches, placement frames and collision remain unchanged.
The tree-step check preserves39217 preceding nonfoliage parts; later city checks
preserve every tree vertex from the completed tree checkpoint.

147 new main-house side/rear windows and64 windows in11 formerly plain wings join
455 retained windows:666 windows/5994 clear outward pane rays. Hidden original
wall cores retain collision. All37 houses have weathered walls, broken base patina,
lanterns, upper flowers, gutters/drains;14 wing gables have timber relief.27 grounded
goods stations fit native proxies.18 formerly plain city materials gain shared
metal, cloth, petal, rind, paper or appropriate existing stone/glass/water textures.
Only intentional light/fire colors remain plain. Prop surfaces/bark/curb/masonry
are1024²; aged paving, grass and refined foliage are1254². PNG masters,
lossless WebPs and provenance are in `authoring/materials/` and `assets/`.
Per-texture4× anisotropy retains oblique detail. No native resolution reduction.

Renderer supports native `texture.alphaBlend` for grass/patina. House reveal
qualifies hidden tall collision cores and raycasts visible facade triangles,
keeping the player visible behind foreground pierced houses. The native home
fixture should record faded owner `frontage-riverside`.

Lighting: warm sun.68, cool ambient.40, cast(.62,−.40), AO16rays/.42strength/1.6radius.
Final corner bake809842 corners/30191meshes/61.1s. Original-alpha floor bake1536²,
1386159 land/815200 shadowed pixels/50.4s. Current geometry digest:
`42897b830bf164683dab302f6b16ea5e43cc40b8e98c261992d9f72942120302`.
Ground land indexing matches4096 full/indexed comparisons. Precomputed alpha UV
projections match authored triangle corners; at most8 transparent intersections
were encountered (bounded at256). Bake filename remains
`assets/wayfarer-ground-shadow-v54.png`.

Object geometry457394 visible triangles/36594 visible parts/63 object materials;
terrain additionally22012 triangles/1998 visible surfaces (1742 walkable,
256 decorative). Object triangles increase67.07% from source68. Native software
buffers remain1×CSS, hardware1×–1.5×. Geometry/texture costs are separate from FPS.

## Verification and source workflow

95 individual Node checks across six files, four public schemas and saved
Blender/export parity pass. The parity tool moves Hall only in RAM to check
shared transforms/bake invalidation; its stale-bake diagnostic is expected.
Final city-detail checker passes368 contacts (including160 independently sampled mortar-joint roots), exact preservation of all preceding
walkable floors and solids, purposeful flower placement and material coverage.
Earlier source69 contact checks cover229376 points with zero unexpected changes,
64501 low facade/accessory vertices and27 stations/1936 proxy-contained vertices.
17 route/service destinations and10 patrols remain clear without route repair.

Continue from the saved `.blend`; historical migrations are not a rebuild recipe.
New modules are once-only and guarded. Source sequence after the earlier house/
curb/tree work: coherent paving → path wear → prop detail → planting edges →
plant vertex contact refit → aged shared paving → corner/alpha floor bakes →
omit wear islands bridging tiny existing paving steps → remove all remaining
stone-image pads → integrate native tufts into existing joints → floor rebake.
Removing the unused material changes the bake digest; the final bake is current.

Use Blender `--python-exit-code 1`; default Blender may return0 after assertions.
Geometry/light edits require sequential save/export, corner bake, original-alpha
preparation and floor bake. The corner baker excludes vegetation; leaf-only edits
need alpha-aware floor rebake. No source mutations/bakes during browser review or
isolated timing. Captures use ordinary camera controls at160/25°/46°, native
1280×666/1× in1280×800 DOM. Fixtures establish appearance. Ordinary Merchant/Artisan/Housing Keeper service
interactions, field exit, saved-character reload and offline cache all pass
separately, with zero runtime/resource errors. Four responsive arrival sizes
are captured. The first service attempt timed out; its later capture showed
arrival within.4. The harness now reads both live coordinates in one snapshot;
arrival tolerance/travel deadline stay unchanged, and the rerun passes. Startup waiting
may be extended for software shader preparation; FPS/frame assertions stay fixed.

Broader civic carving/tracery, functional street goods, painted full-body gait/
anatomy and physical-device FPS acceptance remain open. Retain Hall hierarchy;
RO3 cropped04_08_30 does not establish full Hall height. Keep town work first.
No npm/build/install step is needed here. Keep server8011 active.
